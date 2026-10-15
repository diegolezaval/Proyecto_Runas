"""Observe only this child and persist its real wait result."""
from pathlib import Path
import argparse
import datetime
import json
import os
import subprocess
import sys


def main(home):
    home = home.resolve()
    runtime = home / 'runtime'
    with (runtime / 'guardian_started.json').open('x') as stream:
        json.dump(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       scope='Own transport-enabled worker only', previous_executor_termination_assumed=False), stream)
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       TMPDIR=str(runtime / 'tmp'), PYTHONPYCACHEPREFIX=str(runtime / 'pycache'))
    command = [sys.executable, str(home / 'controlador_transporte.py'), '--home', str(home), '--continue-to', '160']
    with (runtime / 'worker.log').open('xb') as log:
        child = subprocess.Popen(command, cwd=home, env=environment, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        (runtime / 'worker_observed_start.json').write_text(json.dumps(dict(
            at=datetime.datetime.now(datetime.timezone.utc).isoformat(), pid_in_parent_namespace=child.pid,
            scope='Observed own child only', scientific_frontier_inferred=False), indent=2) + '\n')
        returncode = child.wait()
    exit_record = dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(), returncode=returncode,
                       scope='Observed own guardian only', previous_executor_termination_assumed=False)
    (runtime / 'worker_observed_exit.json').write_text(json.dumps(exit_record, indent=2) + '\n')
    (runtime / 'observed_guardian_exit.json').write_text(json.dumps(exit_record, indent=2) + '\n')
    raise SystemExit(returncode if returncode >= 0 else 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    main(parser.parse_args().home)
