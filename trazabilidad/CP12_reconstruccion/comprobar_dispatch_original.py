"""Reject incompatible observed BLAS dispatch before any CP12 execution."""
from pathlib import Path
import datetime
import json
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import numpy as np
from threadpoolctl import threadpool_info

ROOT=Path(__file__).resolve().parents[2]
observed=threadpool_info()
passed=bool(observed) and all(p['architecture']=='SkylakeX' and p['num_threads']==1 for p in observed)
result=dict(passed=passed,checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    expected_observed_architecture='SkylakeX',observed_threadpools=observed,
    M2_steps=0,physical_execution_started=False,coretype_override_used=False,
    GitHub_run_id=os.environ.get('GITHUB_RUN_ID'),GitHub_run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),
    purpose='Actual dispatch eligibility only; original full identity and exact zero-step restart remain mandatory.')
folder=ROOT/'trazabilidad/CP12_reconstruccion/entorno_durable';folder.mkdir(exist_ok=True)
name='dispatch_GitHub_'+os.environ.get('GITHUB_RUN_ID','local')+'_'+os.environ.get('GITHUB_RUN_ATTEMPT','1')+'.json'
(folder/name).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if not passed:raise ValueError('Original BLAS dispatch unavailable on this runner; zero M2 steps; do not migrate.')
