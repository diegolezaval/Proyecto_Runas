"""Record the actual observed exit of this session's single scientific child."""
from pathlib import Path
import argparse
import datetime
import json
import os
import subprocess
import sys


def run(home, registered):
    home, registered = home.resolve(), registered.resolve()
    runtime = home / 'runtime'
    with (runtime / 'guardian_started.json').open('x') as stream:
        json.dump(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            scope='Own transport-enabled worker only; synchronous registered prefix gates',
            previous_executor_termination_assumed=False), stream)
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
        TMPDIR=str(runtime / 'tmp'), PYTHONPYCACHEPREFIX=str(runtime / 'pycache'))
    command = [sys.executable, str(registered / 'supervisar_fronteras.py'),
               '--home', str(home), '--registered', str(registered)]
    with (runtime / 'worker.log').open('xb') as log:
        child = subprocess.Popen(command, cwd=home, env=environment, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        (runtime / 'worker_observed_start.json').write_text(json.dumps(dict(
            at=datetime.datetime.now(datetime.timezone.utc).isoformat(), pid_in_parent_namespace=child.pid,
            scope='Observed own child only', scientific_frontier_inferred=False), indent=2) + '\n')
        returncode = child.wait()
    record = dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(), returncode=returncode,
                  scope='Observed own guardian only', previous_executor_termination_assumed=False)
    for name in ('worker_observed_exit.json', 'observed_guardian_exit.json'):
        (runtime / name).write_text(json.dumps(record, indent=2) + '\n')
    return returncode if returncode >= 0 else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--registered', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.home, args.registered))
