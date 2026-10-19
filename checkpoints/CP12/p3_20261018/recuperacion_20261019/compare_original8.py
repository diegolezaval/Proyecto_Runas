"""Passive comparison of the saved original, P2 and P3 prefix at real tau8."""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import importlib.util
import io
import json
import sys
import zipfile

KEYS=('norm_relative_sup_error','final_complex_nonradial_field_error_over_initial_norm',
      'final_phi_phase_space_error_over_initial_norm','final_mediator_nonradial_error_over_initial_norm',
      'final_mediator_phase_space_error_over_initial_norm')


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(p):return json.loads(p.read_text())


def run(a):
    import numpy as np
    assert not a.output.exists()
    a.output.mkdir(parents=True)
    assert sha(a.archive)=='045b06d6ebd25e9c63b6794d480c0c9570ceb03025fda075f567c3c2f1ff1789'
    assert a.archive.stat().st_size==74606820
    p3=read(a.p3_root/'analysis/lectura_prefijos_continuacion/TAU0008_RESULTADO.json')
    proof=read(a.p3_root/'proofs/tau0008_permanent.json')
    assert p3['time']==proof['time']==8 and proof['passed']
    assert p3['source_state_sha256']==proof['state_sha256']
    with zipfile.ZipFile(a.archive) as z:
        m=json.loads(z.read('Proyecto_Runas/MANIFIESTO_REINICIO_CP12.json'))
        assert m['time']==8
        names={n[len('Proyecto_Runas/'):] for n in z.namelist()}
        assert names==set(m['files'])|{'MANIFIESTO_REINICIO_CP12.json'}
        for n,v in m['files'].items():
            data=z.read('Proyecto_Runas/'+n)
            assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
        run='Proyecto_Runas/'+m['original_pair']+'/'
        receipt_bytes=z.read(run+'procedencia.json')
        receipt=json.loads(receipt_bytes)
        data=z.read(run+'CP12_par_estado.npz')
        state_hash=hashlib.sha256(data).hexdigest()
        assert state_hash==receipt['output_hashes']['CP12_par_estado.npz']
        identity=read(a.p3_root/'preregistration/identidad_cientifica_original.json')
        assert receipt['identity']['code_hashes']==identity['code_hashes']
        assert receipt['identity']['input_hashes']==identity['input_hashes']
        with np.load(io.BytesIO(data),allow_pickle=False) as s:saved={k:s[k].copy() for k in s.files}
        original_config=json.loads(str(saved['config']))
        assert original_config==read(a.p3_root/'configuration.json')['original_configuration']
        assert float(saved['time'])==8
    with np.load(a.p3_root/'outputs/MIXTO_par_estado.npz',allow_pickle=False) as s:
        assert float(s['time'])==8
        assert np.array_equal(s['initial_q'],saved['initial_q'])
        assert np.array_equal(s['initial_v'],saved['initial_v'])
    source=a.p3_root/'science/herramientas/diagnosticar_mediador_CP10.py'
    assert sha(source)==p3['original_metric_source_sha256']
    sys.path.insert(0,str(source.parent))
    spec=importlib.util.spec_from_file_location('unchanged_metric_reader_original8',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    function=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='compare')
    changed=copy.deepcopy(function)
    expected=ast.parse("if c['time'] != 160 or f['time'] != 160:\n    raise ValueError('Tiempo final incorrecto')").body[0]
    assert ast.dump(changed.body[1])==ast.dump(expected)
    constants=[n for n in ast.walk(changed.body[1].test) if isinstance(n,ast.Constant) and n.value==160]
    assert len(constants)==2
    for n in constants:n.value=8
    assert all(ast.dump(x)==ast.dump(y) for i,(x,y) in enumerate(zip(function.body,changed.body)) if i!=1)
    namespace=dict(vars(module))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[changed],type_ignores=[])),'<real_original_prefix8>','exec'),namespace)
    n=int(saved['coarse_n'])
    labels=np.asarray(read(a.p3_root/'science/datos/ensayo_no_radial_CP06.json').get('labels',[]))
    # The label order is the original Evolution harmonic order, also saved in CP10.
    reference=original_config['reference_states'][1]
    with np.load(a.p3_root/'science'/reference,allow_pickle=False) as s:labels=s['labels'].copy()
    for i,name in enumerate(('coarse','fine')):
        use=slice(0,n) if i==0 else slice(n,None)
        rows=saved['rows'][:,:10] if i==0 else np.column_stack([saved['rows'][:,0],saved['rows'][:,10:]])
        np.savez_compressed(a.output/(name+'.npz'),q=saved['q'][:,use],v=saved['v'][:,use],
            initial_q=saved['initial_q'][:,use],initial_v=saved['initial_v'][:,use],rows=rows,
            time=8.,config=json.dumps(original_config['physical_configurations'][i]),labels=labels)
    original=namespace['compare'](a.output/'coarse.npz',a.output/'fine.npz')
    p2=read(a.p2_metrics)
    assert p2['time']==8 and p2['original_metric_source_sha256']==sha(source)
    result=dict(schema='CP12_THREE_SAVED_TRIALS_COMPARISON_REAL_TAU8',time=8,
        original=original,P2=p2['comparison'],P3=p3['comparison'],
        ratios_P3_over_original={k:p3['comparison'][k]/original[k] for k in KEYS},
        ratios_P3_over_P2={k:p3['comparison'][k]/p2['comparison'][k] for k in KEYS},
        original_five_gates={k:original[k]<=.02 for k in KEYS},
        original_archive_sha256=sha(a.archive),original_archive_all_payload_hashes_verified=True,
        original_state_sha256=state_hash,original_receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
        P2_source_state_sha256=p2['source_state_sha256'],P3_source_state_sha256=p3['source_state_sha256'],
        P2_metric_artifact_sha256=sha(a.p2_metrics),P3_metric_artifact_sha256=sha(a.p3_root/'analysis/lectura_prefijos_continuacion/TAU0008_RESULTADO.json'),
        original_fourteen_sources_inputs_and_Cauchy_identical=True,original_metric_source_sha256=sha(source),
        only_time_guard_parameterized=True,chi_phase_rotation_used_for_acceptance=False,
        original_closed_campaign_repeated=False,M2_steps_executed=0,preflight_repeated=False,
        early_prefix_only_no_final_causal_inference=True,correction_validated=False,CP12_closed=False)
    (a.output/'RESULTADO.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({name:result[name]['final_mediator_phase_space_error_over_initial_norm'] for name in ('original','P2','P3')}))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path,required=True);p.add_argument('--p3-root',type=Path,required=True)
    p.add_argument('--p2-metrics',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args())
