"""Administrative guard for one isolated CP12 worker; no numerical modifications."""
from pathlib import Path
import argparse, datetime, fcntl, hashlib, json, os, subprocess, sys

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    with tmp.open('rb') as stream: os.fsync(stream.fileno())
    tmp.replace(path)

def main():
    p = argparse.ArgumentParser(); p.add_argument('--home', type=Path, required=True)
    home = p.parse_args().home.resolve()
    runtime = home / 'runtime'
    meta = json.loads((home / 'preregistration/nueva_identidad.json').read_text())
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == meta['guard_source_sha256']
    with (runtime / 'guard_started.json').open('x') as stream:
        json.dump({'at': now(), 'execution_uuid': meta['execution_uuid'], 'single_launch': True}, stream)
    lock = (runtime / 'guard.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    private = {'at': now(), 'guard_pid': os.getpid(), 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(), 'private_runtime_only': True}
    write(runtime / 'private_host.json', private)
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONPYCACHEPREFIX=str(runtime / 'pycache'), TMPDIR=str(runtime / 'tmp'))
    assert not env.get('OPENBLAS_CORETYPE')
    with (runtime / 'coordinator_stdout.log').open('x') as log:
        child = subprocess.Popen([sys.executable, '-u', str(home / 'coordinator.py'), '--home', str(home), '--continue-to', '160'], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=home)
        private['worker_pid'] = child.pid
        private['worker_start_stat'] = Path('/proc' + '/' + str(child.pid) + '/stat').read_text()
        write(runtime / 'private_host.json', private)
        code = child.wait()
    proof = {'schema': 'CP12_INDEPENDENT_COORDINATOR_EXIT_OBSERVED_BY_PARENT', 'execution_uuid': meta['execution_uuid'], 'execution_run_id': meta['execution_run_id'], 'observed_at': now(), 'returncode': code, 'signal': -code if code < 0 else None, 'worker_has_exited': True, 'scope': 'Only this identified recovery worker; no claim about previous executors', 'CP12_closed': False}
    target = home / 'proofs/coordinator_exit.json'
    assert not target.exists()
    write(target, proof)
    print(json.dumps(proof), flush=True)
    if code: sys.exit(code if code > 0 else 128 - code)

if __name__ == '__main__': main()
