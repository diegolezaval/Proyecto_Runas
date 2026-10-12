"""Read only a permanently recovered boundary; original metrics, zero evolution."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')

def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--home',type=Path,required=True);parser.add_argument('--boundary',type=int,required=True)
    args=parser.parse_args();home=args.home.resolve();t=args.boundary
    assert t>=32 and t%8==0 and t<160
    meta=read(home/'preregistration/nueva_identidad.json');proof_path=home/'proofs'/('tau%04d_permanent.json'%t);proof=read(proof_path)
    assert proof['passed'] and proof['all_payload_hashes_verified'] and proof['independent_extracted_audit']['passed']
    assert proof['execution_run_id']==meta['execution_run_id'] and proof['execution_uuid']==meta['execution_uuid'] and proof['time']==t
    restored=home/'recoveries'/(Path(proof['file_name']).stem+'_checked')/meta['execution_uuid']
    root=restored/'science';run=root/meta['run_relative']
    for name,key in [('CP12_par_estado.npz','state_sha256'),('procedencia.json','receipt_sha256'),('configuration.json','configuration_sha256')]:assert sha(run/name)==proof[key]
    identity=read(restored/'preregistration/identidad_cientifica.json');assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    sys.path.insert(0,str(root/'herramientas'))
    import numpy as np
    from threadpoolctl import threadpool_limits
    from continuar_no_radial_m2 import Evolution
    from observador_causal_CP12 import chi_inner,interpolate,model
    source=home/'analysis/sources/interpretar_presupuesto_CP12_original.py'
    spec=importlib.util.spec_from_file_location('original_metrics',source);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    with np.load(run/'CP12_par_estado.npz',allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    cfg=json.loads(str(saved['config']));assert float(saved['time'])==t
    n=int(saved['coarse_n']);sc,sf=[Evolution(c['dx'],c['radius'],c['L']) for c in cfg['physical_configurations']]
    dq=interpolate(sc,saved['q'][:,:n],sf)-saved['q'][:,n:];dv=interpolate(sc,saved['v'][:,:n],sf)-saved['v'][:,n:]
    S=saved['coupled_angular_basis']
    rawq,rawv=saved['raw_0_q'][:,0],saved['raw_0_v'][:,0]
    with threadpool_limits(limits=1):cq,cv=saved['coupled_0_q'][:,2]@S.T,saved['coupled_0_v'][:,2]@S.T
    q=np.concatenate([dq[2:3],rawq,cq]);v=np.concatenate([dv[2:3],rawv,cv])
    scale=chi_inner(sf,saved['initial_q'][2,n:],saved['initial_v'][2,n:],saved['initial_q'][2,n:],saved['initial_v'][2,n:])
    core=np.array([[chi_inner(sf,a,b,c,d) for c,d in zip(q,v)] for a,b in zip(q,v)])
    last=json.loads(str(saved['budget_rows']))[-1];criteria=read(root/'datos/ensayo_causal_chi_CP12.json')['observer_criteria']
    assert last['time']==t
    grams={'core_phase':core,'short_core_k4':np.array(last['short_modes']['core']['short_response_gram_matrix']),'short_smooth_k4':np.array(last['short_modes']['smooth']['short_response_gram_matrix'])}
    tables={};sufficiency={};cross={};differences=[]
    for family,names,start in [('raw',reader.BARE,1),('coupled',reader.COUPLED,6)]:
        channels={name:[i] for i,name in enumerate(names)};channels.update(reader.GROUPS[family]);tables[family]={};sufficiency[family]={};cross[family]={}
        for window,gram in grams.items():
            tables[family][window]={name:reader.metrics(gram,[start+i for i in ids],scale) for name,ids in channels.items()}
            cross[family][window]=gram[start:start+5,start:start+5].tolist()
        for name in channels:
            tests={window:reader.sufficient(tables[family][window][name],criteria) for window in grams}
            sufficiency[family][name]={'meets_all_three_windows_at_this_provisional_time':all(tests.values()),'tests_by_window':tests}
        for i,name in enumerate(names):
            rec=last[family][i];actual=tables[family]['core_phase'][name]
            differences.extend(abs(actual[key]-rec[key]) for key in actual)
    assert max(differences)<2e-12,'Saved original metrics do not reproduce'
    full=lambda a,b:float(np.sum(sf.w[:,None]*(a*a+b*b/model.mediator**2)))
    closures={family:float(np.sqrt(full(dq[2]-q[start:start+5].sum(0),dv[2]-v[start:start+5].sum(0))/max(full(dq[2],dv[2]),1e-300))) for family,start in [('raw',1),('coupled',6)]}
    result={'schema':'CP12_INDEPENDENT_PROVISIONAL_SAVED_RESPONSE_READING','time':t,'execution_uuid':meta['execution_uuid'],'execution_run_id':meta['execution_run_id'],
        'proof_sha256':sha(proof_path),'state_sha256':proof['state_sha256'],'zip_sha256':proof['zip_sha256'],'M2_steps':0,'observed_core_phase_relative_error':last['observed_relative_error'],
        'original_metrics_max_difference':max(differences),'tables':tables,'provisional_sufficiency':sufficiency,'cross_terms':cross,'full_box_chi_closure':closures,
        'spectral_fractions':{window:last['short_modes'][window]['observed_error_fraction_above_k'] for window in ['core','smooth']},'original_criteria':criteria,
        'source_sha256':sha(Path(__file__)),'original_metrics_source_sha256':sha(source),'preregistration_sha256':sha(home/'analysis/prefix/PRERREGISTRO.md'),
        'final_budget_reading_completed':False,'final_onsets_evaluated':False,'physical_gate_evaluated':False,'physical_correction_tested':False,'CP12_closed':False}
    out=home/'analysis/prefix'/('tau%04d.json'%t);assert not out.exists();out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'time':t,'M2_steps':0,'saved_metrics_max_difference':max(differences),'full_box_chi_closure':closures,'observed_core_phase_relative_error':last['observed_relative_error'],
        'provisional_coupled_classes_in_all_windows':[name for name,v in sufficiency['coupled'].items() if v['meets_all_three_windows_at_this_provisional_time']],'CP12_closed':False}))

if __name__=='__main__':main()
