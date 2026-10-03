"""Diagnóstico de reconstrucción inicial; sólo lectura, sin pasos de evolución."""
from pathlib import Path
import hashlib,json,os,platform,sys
import numpy as np
from threadpoolctl import threadpool_info,threadpool_limits

root=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(root/'herramientas'))
from continuar_no_radial_m2 import Evolution,seed
from diagnosticar_mediador_CP10 import load
rows=[]
with threadpool_limits(limits=1):
 for case in ['temporal_h0125','espacial_h00625']:
  saved=next(root.glob('validacion/P06/no_radial/CP10/'+case+'__*/*_estado.npz'))
  data=load(saved);c=data['configuration']
  sim=Evolution(c['dx'],c['radius'],c['L']);q,v,transfer=seed(sim,c['eps'])
  for key,array in [('initial_q',q),('initial_v',v)]:
   expected=data[key];different=array!=expected;where=np.argwhere(different)
   first=[]
   for idx in where[:3]:
    index=tuple(map(int,idx));first.append({'index':list(index),'expected_hex':float(expected[index]).hex(),'actual_hex':float(array[index]).hex()})
   rows.append({'case':case,'field':key,'exact_equal':bool(np.array_equal(expected,array)),
                'different_values':int(different.sum()),'different_columns':np.flatnonzero(different.any(axis=(0,1))).tolist(),
                'max_abs_error':float(np.max(abs(array-expected))),
                'expected_array_sha256':hashlib.sha256(expected.tobytes()).hexdigest(),
                'actual_array_sha256':hashlib.sha256(array.tobytes()).hexdigest(),'first_differences':first})
 report={'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,
         'cpu_features':np._core._multiarray_umath.__cpu_features__,
         'NPY_DISABLE_CPU_FEATURES':os.environ.get('NPY_DISABLE_CPU_FEATURES'),
         'OPENBLAS_CORETYPE':os.environ.get('OPENBLAS_CORETYPE'),
         'threadpools':[{k:v for k,v in p.items() if k!='filepath'} for p in threadpool_info()],
         'rows':rows,'integration_steps':0,'science_modified':False}
print(json.dumps(report,ensure_ascii=False,indent=2))
