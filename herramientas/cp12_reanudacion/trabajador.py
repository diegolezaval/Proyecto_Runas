"""Arrancar y reconocer al ejecutor publicado sin cambiar su bucle físico."""

from contextlib import contextmanager
import os
from pathlib import Path
import runpy
import sys
import traceback

from .infra import Timings, optional, read, record, require


def identity(pid):
    try:
        fields = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()
        if fields[0] in ('Z', 'X'):
            return None
        return dict(pid=pid, boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                    namespace=os.readlink(Path('/proc') / str(pid) / 'ns/pid'),
                    start_ticks=int(fields[19]))
    except (FileNotFoundError, ProcessLookupError):
        return None


def lock_owner(path, pid=None):
    if not path.exists():
        return False
    stat = path.stat()
    key = (os.major(stat.st_dev), os.minor(stat.st_dev), stat.st_ino)
    for row in Path('/proc/locks').read_text().splitlines():
        fields = row.split()
        if fields[1] == 'FLOCK' and fields[3] == 'WRITE':
            major, minor, inode = fields[5].split(':')
            if (int(major, 16), int(minor, 16), int(inode)) == key and (pid is None or int(fields[4]) == pid):
                return True
    return False


def live(job, worker_id, registry_sha, *, locks=False):
    launched = optional(job / 'PROCESO.json')
    if not launched or launched['identity'] != identity(launched['identity']['pid']):
        return False
    require(launched['worker_id'] == worker_id and launched['registry_sha256'] == registry_sha,
            'Proceso de otra asignación')
    if locks:
        pid = launched['identity']['pid']
        observed = optional(job / 'home/runtime/worker_started.json')
        return bool(observed and observed['pid'] == pid and observed['registry_sha256'] == registry_sha and
                    lock_owner(job / 'P3_WORKER.lock', pid) and lock_owner(job / 'home/runtime/worker.lock', pid))
    return True


def main(job):
    config = read(job / 'LANZAMIENTO.json')
    command = config['command']
    record(job / 'PROCESO.json', dict(worker_id=config['worker_id'], registry_sha256=config['registry_sha256'],
                                      identity=identity(os.getpid())), once=True)
    sys.path.insert(0, str(Path(command[0]).parent))
    import preservar
    base = preservar.original
    timings = Timings()

    @contextmanager
    def measured(category, name):
        try:
            with timings.measure(category, name):
                yield
        finally:
            record(job / 'TIEMPOS_TRABAJADOR.json', dict(events=timings.events, totals=timings.totals()))

    original_audit, original_logged = base.audit, base.logged
    original_open = base.urllib.request.urlopen

    def audit(home, kind, boundary, output):
        with measured('auditoria', f'{kind} {boundary} {output.name}'):
            return original_audit(home, kind, boundary, output)

    def logged(command, prefix, payload=None, env=None):
        if prefix.name in ('transfer', 'xattrs', 'upload'):
            with measured('espera' if prefix.name == 'upload' else 'descarga', prefix.name):
                return original_logged(command, prefix, payload, env)
        return original_logged(command, prefix, payload, env)

    @contextmanager
    def download(url, *args, **kwargs):
        with measured('descarga', 'Recuperación independiente de Release'):
            with original_open(url, *args, **kwargs) as stream:
                yield stream

    def urlopen(url, *args, **kwargs):
        if isinstance(url, str) and url.startswith('https://github.com/' + base.REPO + '/releases/download/'):
            return download(url, *args, **kwargs)
        return original_open(url, *args, **kwargs)

    # Sólo se cronometra la administración del ejecutor publicado.
    base.audit = preservar.audit = audit
    base.logged = preservar.logged = logged
    base.urllib.request.urlopen = urlopen
    from library_hosted_apps import HostedAppsClient
    original_call = HostedAppsClient.call_tool

    def call_tool(self, connector, tool, *args, **kwargs):
        if connector == 'connector_openai_library' and tool == 'prepare_materialize':
            with measured('descarga', 'Materialización independiente de Biblioteca'):
                return original_call(self, connector, tool, *args, **kwargs)
        return original_call(self, connector, tool, *args, **kwargs)

    HostedAppsClient.call_tool = call_tool
    sys.argv = command
    code = 1
    try:
        runpy.run_path(command[0], run_name='__main__')
        code = 0
    except SystemExit as error:
        code = error.code or 0
    except BaseException:
        traceback.print_exc()
    finally:
        record(job / 'SALIDA_OBSERVADA.json', dict(exit_code=code, exit_observed=True), once=True)
    return code


if __name__ == '__main__':
    # Los ayudantes ya se comprobaron contra el registro publicado.
    root = Path(sys.argv[1])
    sys.path.insert(0, read(root / 'LANZAMIENTO.json')['helpers'])
    raise SystemExit(main(root))
