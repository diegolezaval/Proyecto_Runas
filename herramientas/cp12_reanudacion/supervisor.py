"""Observar la salida del hijo y publicar su recibo fuera del intento local."""

from datetime import datetime
import fcntl
import os
from pathlib import Path
import re
import subprocess
import sys

from . import trabajador
from .infra import CLAIM, ROOT, Git, Stop, digest, encoded, now, optional, read, record, require, sha


EXIT_BRANCH = 'administracion/cp12-recibos-salida'
EXIT_REF = 'refs/heads/' + EXIT_BRANCH
WORKER_SCHEMA = 'CP12_REANUDADOR_WORKER_V2'
EXIT_SCHEMA = 'CP12_REANUDADOR_SALIDA_V1'


def supervised(claim):
    return claim is not None and claim.get('schema') == WORKER_SCHEMA


def binding(claim):
    require(supervised(claim), 'La asignación no identifica una sesión supervisada')
    identity = {key: claim[key] for key in ('allocation_id', 'worker_id', 'session_id',
                                           'registry_sha256', 'source_archive_sha256')}
    require(re.fullmatch('[a-z0-9_]+', identity['allocation_id']), 'Identidad de asignación inválida')
    for key, size in (('worker_id', 32), ('session_id', 32), ('registry_sha256', 64), ('source_archive_sha256', 64)):
        require(re.fullmatch('[0-9a-f]{%d}' % size, identity[key]), f'Identidad inválida en {key}')
    return identity


def receipt_path(claim):
    ids = binding(claim)
    return f'{ROOT}/recibos_salida/{ids["allocation_id"]}/{ids["session_id"]}.json'


def active(job, claim):
    started = optional(job / 'SUPERVISION_INICIADA.json')
    if not started:
        return False
    require(all(started.get(key) == value for key, value in binding(claim).items()),
            'El supervisor pertenece a otra sesión')
    identity = started.get('identity')
    return bool(identity and identity == trabajador.identity(identity['pid']))


def validate(receipt, claim):
    require(receipt['schema'] == EXIT_SCHEMA and receipt['method'] == 'waitpid_hijo_directo' and
            receipt['exit_observed'] is True and
            all(receipt.get(key) == value for key, value in binding(claim).items()),
            'Recibo de salida de otra sesión, asignación o registro')
    code = receipt['returncode']
    require(type(code) is int and -64 <= code <= 255, 'Estado terminal inválido')
    exit_code, exit_signal = receipt['exit_code'], receipt['signal']
    if code >= 0:
        require(type(exit_code) is int and exit_code == code and exit_signal is None,
                'Código de salida incompatible con el estado terminal')
    else:
        require(type(exit_signal) is int and exit_signal == -code and exit_code is None,
                'Señal incompatible con el estado terminal')
    identity_sha = receipt['process_identity_sha256']
    require(type(receipt['pid']) is int and receipt['pid'] > 0 and
            (identity_sha is None or re.fullmatch('[0-9a-f]{64}', identity_sha)) and
            datetime.fromisoformat(receipt['observed_at_utc']).utcoffset() is not None,
            'Recibo sin identidad de proceso o fecha de observación')
    return receipt


def recover(git, claim):
    path = receipt_path(claim)
    head = git.head(EXIT_REF)
    value = git.json(head, path, missing=True)
    if value is None:
        return None
    return dict(commit=head, path=path, receipt=validate(value, claim))


def check_destination(git):
    try:
        head = git.head(EXIT_REF)
        result = git.run('push', '--dry-run', 'origin', f'{head}:{EXIT_REF}',
                         env=dict(os.environ, GIT_TERMINAL_PROMPT='0'), check=False)
        if result.returncode:
            raise RuntimeError('El destino no aceptó el acceso de escritura')
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        raise Stop('SUPERVISOR_DESTINO', 'No se acreditó acceso al destino persistente de salidas',
                   'Habilitar acceso Git de escritura a la rama de recibos y repetir retomar',
                   destination=EXIT_BRANCH) from error


def publish(git, claim, receipt):
    path = receipt_path(claim)
    data = encoded(validate(receipt, claim))
    for _ in range(4):
        head = git.head(EXIT_REF)
        present = git.get(head, path, missing=True)
        if present is not None:
            require(present == data, 'La sesión ya tiene un recibo de salida distinto')
            return dict(commit=head, path=path)
        try:
            commit = git.publish(head, {path: data}, 'CP12/P3: acreditar salida de trabajador', ref=EXIT_REF)
            return dict(commit=commit, path=path)
        except (Stop, ValueError):
            # Una publicación simultánea puede añadir este mismo recibo u otro.
            updated = git.head(EXIT_REF)
            if updated == head:
                raise
    raise Stop('SUPERVISOR_DESTINO', 'La rama de recibos siguió cambiando',
               'Reintentar la publicación del recibo local', file=path, destination=EXIT_BRANCH)


def evidence(git, claim, local=None, *, retry=False):
    if local is not None:
        validate(local, claim)
    try:
        remote = recover(git, claim)
        if remote is None and local is not None and retry:
            publish(git, claim, local)
            remote = recover(git, claim)
    except (Stop, RuntimeError, OSError, subprocess.SubprocessError):
        return dict(status='SALIDA_LOCAL_PENDIENTE' if local else 'CONTACTO_PERDIDO_SIN_SALIDA',
                    exit_observed=local is not None, exit=local, exit_lookup='DESTINO_INDISPONIBLE')
    if remote is None:
        return dict(status='SALIDA_LOCAL_PENDIENTE' if local else 'CONTACTO_PERDIDO_SIN_SALIDA',
                    exit_observed=local is not None, exit=local, exit_lookup='SIN_RECIBO')
    require(local is None or local == remote['receipt'], 'La salida local y el recibo remoto difieren')
    return dict(status='SALIDA_CONFIRMADA', exit_observed=True, exit=remote['receipt'],
                exit_commit=remote['commit'], exit_path=remote['path'], exit_lookup='RECUPERADO')


def supervise(git, job, claim, command):
    ids = binding(claim)
    child = subprocess.Popen(command)
    try:
        identity = trabajador.identity(child.pid, include_exited=True)
    except OSError:
        identity = None
    try:
        _, status = os.waitpid(child.pid, 0)
    except ChildProcessError:
        child.poll()  # Cerrar el registro local de Popen sin usar su valor de respaldo.
        print('El supervisor perdió el estado terminal del hijo', file=sys.stderr)
        return 2
    code = child.returncode = os.waitstatus_to_exitcode(status)
    receipt = dict(schema=EXIT_SCHEMA, **ids, method='waitpid_hijo_directo', exit_observed=True,
                   observed_at_utc=now(), pid=child.pid,
                   process_identity_sha256=digest(encoded(identity)) if identity else None,
                   returncode=code, exit_code=code if code >= 0 else None, signal=-code if code < 0 else None)
    try:
        if job.is_dir():
            record(job / 'SALIDA_OBSERVADA.json', receipt, once=True)
    except OSError as error:
        print(f'Copia local de salida indisponible: {type(error).__name__}', file=sys.stderr)
    try:
        published = publish(git, claim, receipt)
    except (Stop, OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(f'Publicación de salida pendiente en {EXIT_BRANCH}: {error}', file=sys.stderr)
        return 2
    try:
        if job.is_dir():
            record(job / 'SALIDA_PUBLICADA.json', published, once=True)
    except OSError as error:
        print(f'Recibo publicado y acuse local indisponible: {type(error).__name__}', file=sys.stderr)
    return 0


def main(job):
    config = read(job / 'LANZAMIENTO.json')
    claim = config['supervision']
    ids = binding(claim)
    registry_path = job / 'REGISTRO.json'
    registry = read(registry_path)
    require(config['worker_id'] == ids['worker_id'] and
            sha(registry_path) == config['registry_sha256'] == ids['registry_sha256'] and
            registry['allocation_id'] == ids['allocation_id'] and
            registry['source_archive_sha256'] == ids['source_archive_sha256'],
            'El lanzamiento no coincide con la asignación supervisada')
    git = Git(Path(__file__).resolve().parents[2])
    with (job / 'SUPERVISION.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not (job / 'SUPERVISION_INICIADA.json').exists(), 'La sesión ya tiene un supervisor')
        require(git.json(git.head(), CLAIM) == claim, 'La sesión supervisada ya no es la registrada')
        record(job / 'SUPERVISION_INICIADA.json',
               dict(**ids, at=now(), identity=trabajador.identity(os.getpid())), once=True)
        return supervise(git, job, claim, [sys.executable, '-m', 'cp12_reanudacion.trabajador', str(job)])


if __name__ == '__main__':
    sys.exit(main(Path(sys.argv[1]).resolve()))
