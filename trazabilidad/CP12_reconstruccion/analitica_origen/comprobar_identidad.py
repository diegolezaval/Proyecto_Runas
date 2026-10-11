"""Zero-M2 algebraic check of the existing radial operator, not a correction."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.path.insert(0,str(ROOT/'herramientas'))
import numpy as np
from continuar_no_radial_m2 import Evolution

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

sources=['herramientas/continuar_no_radial_m2.py','datos/ensayo_causal_chi_CP12.json']
before={s:sha(ROOT/s) for s in sources}
records=[]
for h in [.125,.0625]:
    sim=Evolution(h,220.,4)
    index=int(np.flatnonzero(sim.ell==2)[0])
    q=np.zeros((3,sim.n,sim.nm));q[2,:,index]=sim.r**2
    measured=sim.lap(q)[2,:,index]
    expected=h*h/(2*(sim.r*sim.r+h*h/12))
    error=float(np.max(np.abs(measured[:-1]-expected[:-1])))
    use=sim.r<40
    norm=float(np.sqrt(np.sum(sim.w[use]*measured[use]**2)))
    records.append(dict(h=h,first_cell=float(measured[0]),first_cell_expected=1.5,
        maximum_absolute_interior_error=error,weighted_residual_norm_core=norm,
        outer_Dirichlet_row_excluded=True))
after={s:sha(ROOT/s) for s in sources}
passed=before==after and all(r['maximum_absolute_interior_error']<2e-12 and abs(r['first_cell']-1.5)<2e-12 for r in records)
result=dict(passed=passed,checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    M2_steps=0,original_sources_before=before,original_sources_after=after,
    code_sha256=sha(Path(__file__)),preregistration_sha256=sha(HERE/'PRERREGISTRO.md'),
    records=records,norm_ratio_fine_over_coarse=records[1]['weighted_residual_norm_core']/records[0]['weighted_residual_norm_core'],
    asymptotic_ratio=2**(-1.5),causal_sufficiency_not_established=True,
    physical_gate_unchanged=.02,correction_tested=False)
with (HERE/'resultados.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(result))
if not passed:raise ValueError('Original operator identity differs from independent algebra')
