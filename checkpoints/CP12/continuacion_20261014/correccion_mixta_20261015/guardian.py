"""Observe only the new independent worker, never previous executor activity."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess, sys

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write(p,v):
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(v,indent=2)+'\n');temp.replace(p)

def main():
    p=argparse.ArgumentParser();p.add_argument('--home',type=Path,required=True);a=p.parse_args()
    home=a.home.resolve();runtime=home/'runtime'
    with (runtime/'guardian_started.json').open('x') as f:
        json.dump(dict(at=now(),scope='Only this new worker',old_executor_termination_assumed=False),f)
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1',
         'TMPDIR':str(runtime/'tmp'),'PYTHONPYCACHEPREFIX':str(runtime/'pycache')}
    command=[sys.executable,str(home/'coordinator.py'),'--home',str(home),'--continue-to','160']
    with (runtime/'worker.log').open('xb') as log:
        child=subprocess.Popen(command,cwd=home,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        write(runtime/'worker_observed_start.json',dict(at=now(),pid=child.pid,scope='Observed own child only',
              controller_sha256=hashlib.sha256((home/'coordinator.py').read_bytes()).hexdigest(),
              completed_frontier_not_inferred_from_activity=True))
        rc=child.wait()
    write(runtime/'worker_observed_exit.json',dict(at=now(),pid=child.pid,returncode=rc,
          signal=-rc if rc<0 else None,scope='Observed own child only',
          original_or_other_executor_termination_asserted=False))
    raise SystemExit(rc if rc>=0 else 1)

if __name__=='__main__':main()

