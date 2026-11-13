"""Prueba del supervisor en dos ejecutores hospedados, con procesos ficticios."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

from . import supervisor, trabajador
from .infra import Git, digest, encoded, now, read, record, require


def claim(label, run_id, attempt):
    allocation = f'prueba_hospedada_{run_id}_{attempt}_{label}'
    return dict(
        schema=supervisor.WORKER_SCHEMA,
        allocation_id=allocation,
        session_id=digest(f'{allocation}/sesion'.encode())[:32],
        worker_id=digest(f'{allocation}/trabajador'.encode())[:32],
        registry_sha256=digest(f'{allocation}/registro-ficticio'.encode()),
        source_archive_sha256=digest(f'{allocation}/origen-ficticio'.encode()),
    )


def runner_identity():
    return hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes()).hexdigest()


@contextmanager
def process_container(job):
    """El PID 1 ejecuta el supervisor. Al destruirlo, desaparecen sus hijos."""
    image = 'python:3.12-slim'
    tools = Path(__file__).resolve().parents[1]
    subprocess.run(['docker', 'pull', image], check=True, timeout=150)
    name = 'cp12-supervisor-' + job.name
    command = ['docker', 'run', '--rm', '--name', name, '--network', 'none',
               '--mount', f'type=bind,src={job},dst=/intento',
               '--mount', f'type=bind,src={tools},dst=/prueba,readonly',
               '-e', 'PYTHONDONTWRITEBYTECODE=1', '--workdir', '/prueba',
               image, 'python', '-m', 'cp12_reanudacion.prueba_hospedada', 'perder']
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL)
    try:
        yield process
    finally:
        removed = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, text=True, timeout=30)
        process.wait(timeout=30)
        require(removed.returncode == 0 and process.returncode == 137,
                'Docker no confirmó la destrucción del contenedor y la terminación del supervisor')


def observe(git, normal, lost):
    supervisor.check_destination(git)
    with TemporaryDirectory(prefix='cp12-salida-') as directory:
        job = Path(directory)
        result = supervisor.supervise(git, job, normal, [sys.executable, '-c',
                                      'import sys,time;time.sleep(2);sys.exit(17)'])
        require(result == 0, 'El supervisor no confirmó la publicación')
        published = read(job / 'SALIDA_PUBLICADA.json')
    recovered = supervisor.recover(git, normal)
    require(recovered and recovered['receipt']['exit_code'] == 17,
            'El recibo esperado no se recuperó de GitHub')

    with TemporaryDirectory(prefix='cp12-contacto-') as directory:
        job = Path(directory)
        record(job / 'asignacion.json', lost)
        with process_container(job) as process:
            deadline = time.monotonic() + 30
            while not (job / 'vivo').is_file() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(.1)
            require((job / 'vivo').is_file() and process.poll() is None,
                    'El proceso ficticio no llegó a estar activo')
            require(not (job / 'SALIDA_OBSERVADA.json').exists(), 'La salida se observó antes de cortar el entorno')
    lost_state = supervisor.evidence(git, lost)
    require(lost_state['status'] == 'CONTACTO_PERDIDO_SIN_SALIDA' and lost_state['exit_lookup'] == 'SIN_RECIBO',
            'Se esperaba pérdida de contacto con salida sin observar')
    return dict(observed_at_utc=now(), github_runner=runner_identity(),
                confirmed=published, lost_container_exit=process.returncode, lost=lost_state)


def disappear():
    # Se usa el supervisor real dentro de un espacio de procesos descartable.
    # La red está deshabilitada en este escenario de pérdida completa.
    job = Path('/intento')
    child_code = 'from pathlib import Path\nimport time\nPath("/intento/vivo").touch()\nwhile True: time.sleep(1)'
    return supervisor.supervise(Git(Path.cwd()), job, read(job / 'asignacion.json'),
                                [sys.executable, '-c', child_code])


def recover(git, normal, lost, report_path):
    head = git.head(supervisor.EXIT_REF)
    report = git.json(head, report_path)
    require(report['github_runner'] != runner_identity(), 'La consulta debe ejecutarse en otra máquina')
    confirmed = supervisor.evidence(git, normal)
    missing = supervisor.evidence(git, lost)
    require(confirmed['status'] == 'SALIDA_CONFIRMADA' and confirmed['exit']['exit_code'] == 17,
            'El nuevo ejecutor no pudo recuperar la salida observada')
    saved = report['confirmed']
    require(git.get(saved['commit'], saved['path']) == encoded(confirmed['exit']),
            'Los bytes recuperados difieren del recibo publicado por el supervisor')
    require(missing == report['lost'] and missing['exit_lookup'] == 'SIN_RECIBO' and
            not missing['exit_observed'], 'La pérdida del entorno se confundió con una salida observada')
    return dict(verified_at_utc=now(), github_runner=runner_identity(), source_report=report_path,
                confirmed=confirmed, lost=missing)


def main(mode):
    if mode == 'perder':
        return disappear()
    run_id = int(os.environ['GITHUB_RUN_ID'])
    attempt = int(os.environ['GITHUB_RUN_ATTEMPT'])
    git = Git(Path(__file__).resolve().parents[2])
    normal, lost = (claim(label, run_id, attempt) for label in ('salida', 'contacto'))
    report_path = str(Path(supervisor.receipt_path(normal)).parent / 'PRUEBA_HOSPEDADA.json')
    if mode == 'observar':
        report = observe(git, normal, lost)
        git.publish(git.head(supervisor.EXIT_REF), {report_path: encoded(report)},
                    'CP12/P3: registrar comprobación hospedada del supervisor', ref=supervisor.EXIT_REF)
    elif mode == 'recuperar':
        report = recover(git, normal, lost, report_path)
    else:
        raise ValueError('Modo de prueba inválido')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as summary:
        summary.write('~~~json\n' + encoded(report).decode() + '~~~\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
