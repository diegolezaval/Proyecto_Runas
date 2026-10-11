"""Zero-M2-step environment and provenance gate for durable execution."""
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
sys.path.insert(0, str(ROOT/'herramientas'))
import ejecutar_con_procedencia as prov
import numpy as np
from threadpoolctl import threadpool_info


def main():
    expected = json.loads((ROOT/'trazabilidad/CP12_reconstruccion/identidad_original.json').read_text())
    protocol = ROOT/'datos/ensayo_causal_chi_CP12.json'
    _, case, observed, run_id = prov.prepare(protocol, 'par_instrumentado')
    controls = [prov.verify_receipt(p) for p in sorted((ROOT/'validacion/P06/no_radial/CP12').glob('control_instrumentacion__*/procedencia.json'))]
    references = [prov.verify_receipt((ROOT/p).parent/'procedencia.json') for p in case['configuration']['reference_states']]
    tests = dict(original_run_id=run_id==expected['run_id'],
                 original_full_identity=observed==expected['identity'],
                 fourteen_original_sources=len(observed['code_hashes'])==14,
                 six_original_controls_intact=len(controls)==6 and all(x['passed'] for x in controls),
                 CP10_references_intact=all(x['passed'] for x in references),
                 observed_BLAS_one=bool(threadpool_info()) and all(x['num_threads']==1 for x in threadpool_info()))
    result = dict(passed=all(tests.values()), tests=tests, checked_at=prov.now(),
                  expected_environment=expected['identity']['environment'],
                  observed_environment=observed['environment'], observed_run_id=run_id,
                  expected_run_id=expected['run_id'], M2_steps=0, correction_tested=False,
                  physical_protocol_changes=False, observed_threadpools=threadpool_info(),
                  scope='Environment gate only; no new boundary or causal conclusion.')
    out=ROOT/'trazabilidad/CP12_reconstruccion/entorno_durable'
    out.mkdir(exist_ok=True)
    result['execution_origin'] = dict(GitHub_run_id=os.environ.get('GITHUB_RUN_ID'),
                                     GitHub_job=os.environ.get('GITHUB_JOB'),
                                     available_logical_CPUs=os.cpu_count())
    result['execution_origin']['GitHub_run_attempt']=os.environ.get('GITHUB_RUN_ATTEMPT')
    filename='GitHub_'+os.environ['GITHUB_RUN_ID']+'_'+os.environ.get('GITHUB_RUN_ATTEMPT','1')+'.json' if os.environ.get('GITHUB_RUN_ID') else 'resultados.json'
    prov.write(out/filename,result)
    print(json.dumps(result,indent=2))
    if not result['passed']:
        raise ValueError('Original identity not reproduced; no M2 execution allowed.')


if __name__=='__main__':
    main()
