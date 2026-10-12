"""Run the original final interpretation through an explicit independent-proof mapping."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')

def read(path): return json.loads(path.read_text())
def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--home',type=Path,required=True)
    home=parser.parse_args().home.resolve();root=home/'science'
    meta=read(home/'preregistration/nueva_identidad.json');run=root/meta['run_relative']
    proof_path=home/'proofs/tau0160_permanent.json';proof=read(proof_path)
    assert proof['passed'] and proof['time']==160 and proof['execution_uuid']==meta['execution_uuid'] and proof['execution_run_id']==meta['execution_run_id']
    assert proof['all_payload_hashes_verified'] and proof['independent_extracted_audit']['passed']
    assert proof['independent_extracted_audit']['time']==160
    for filename,key in [('CP12_par_estado.npz','state_sha256'),('procedencia.json','receipt_sha256'),('configuration.json','configuration_sha256')]:
        assert sha(run/filename)==proof[key]
    capsule=home/'capsules'/proof['file_name'];assert sha(capsule)==proof['zip_sha256'] and capsule.stat().st_size==proof['zip_bytes']
    source=home/'analysis/sources/interpretar_presupuesto_CP12_original.py'
    protocol_path=home/'analysis/sources/interpretacion_CP12_original.json'
    sys.path.insert(0,str(root/'herramientas'))
    import ejecutar_con_procedencia as prov
    import numpy as np
    from threadpoolctl import threadpool_limits
    worker_receipt=prov.verify_receipt(run/'procedencia.json')
    assert worker_receipt['passed'] and worker_receipt['status']=='COMPLETADA'
    scientific_result=read(run/'CP12_par.json')
    assert scientific_result['time']==160 and scientific_result['reproduces_CP10_exactly'] and scientific_result['observer_checks_passed']
    identity={'kind':'INDEPENDENT_ORIGINAL_CP12_OFFLINE_INTERPRETATION','execution_uuid':meta['execution_uuid'],'scientific_run_id':meta['execution_run_id'],
        'proof_sha256':sha(proof_path),'proof_zip_sha256':proof['zip_sha256'],'original_reader_source_sha256':sha(source),
        'original_reading_protocol_sha256':sha(protocol_path),'adapter_source_sha256':sha(Path(__file__)),
        'preregistration_sha256':sha(home/'analysis/causal/PRERREGISTRO.md'),
        'inputs':{name:sha(run/name) for name in ['CP12_par_estado.npz','CP12_par.json','respuestas_finales.npz','serie_presupuestos.json','identidades_algebraicas.json','procedencia.json','configuration.json']}}
    analysis_id=hashlib.sha256(prov.canonical(identity)).hexdigest()
    out=home/'analysis/causal'/('lectura__'+analysis_id);out.mkdir()
    receipt={'schema':'CP12_INDEPENDENT_OFFLINE_ANALYSIS_RECEIPT','analysis_id':analysis_id,'identity':identity,'status':'REGISTERED','registered_at':now(),'M2_steps':0,'CP12_closed':False}
    write(out/'procedencia_lectura.json',receipt)
    mapped={'passed':True,'time':160,'download_verification':{'passed':proof['all_payload_hashes_verified'] and proof['independent_extracted_audit']['passed'],
        'independent_extracted_audit':proof['independent_extracted_audit'],'zip_sha256':proof['zip_sha256']},
        **{k:proof[k] for k in ['state_sha256','receipt_sha256','configuration_sha256']}}
    write(out/'traduccion_comprobante.json',{'source_proof_path':'proofs/tau0160_permanent.json','source_proof_sha256':sha(proof_path),'execution_run_id':meta['execution_run_id'],'original_certificate_route_not_written':True,'mapped_certificate':mapped})
    spec=importlib.util.spec_from_file_location('original_offline_reader',source)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    reader.ROOT=root;reader.PAIR=run
    original_read=reader.read; old_certificate=root/'trazabilidad/CP12_reconstruccion/respaldos/tau0160.json'
    reader.read=lambda path: mapped if path==old_certificate else original_read(path)
    config={'case':read(protocol_path)['cases']['interpretacion_causal']}
    try:
        with threadpool_limits(limits=1): result=reader.interpret(config,out)
        assert result['time']==160 and result['new_M2_steps']==0 and result['reproduces_CP10_exactly'] and result['scientific_closure_requires_review']
        from observador_causal_CP12 import chi_inner, interpolate
        from continuar_no_radial_m2 import Evolution
        with np.load(run/'CP12_par_estado.npz',allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
        with np.load(run/'respuestas_finales.npz',allow_pickle=False) as z:responses={k:z[k].copy() for k in z.files}
        cfg=json.loads(str(saved['config']));n=int(saved['coarse_n']);sc,sf=[Evolution(c['dx'],c['radius'],c['L']) for c in cfg['physical_configurations']]
        dq=interpolate(sc,saved['q'][:,:n],sf)-saved['q'][:,n:];dv=interpolate(sc,saved['v'][:,:n],sf)-saved['v'][:,n:]
        scale=chi_inner(sf,saved['initial_q'][2,n:],saved['initial_v'][2,n:],saved['initial_q'][2,n:],saved['initial_v'][2,n:])
        q=np.concatenate([dq[2:3],responses['raw_q'][:,0],responses['coupled_q'][:,2]])
        v=np.concatenate([dv[2:3],responses['raw_v'][:,0],responses['coupled_v'][:,2]])
        core=np.array([[chi_inner(sf,a,b,c,d) for c,d in zip(q,v)] for a,b in zip(q,v)])
        final=read(run/'serie_presupuestos.json')[-1]
        grams={'core_phase':core,'short_core_k4':np.array(final['short_modes']['core']['short_response_gram_matrix']),'short_smooth_k4':np.array(final['short_modes']['smooth']['short_response_gram_matrix'])}
        channels={'bare_chi_operator_propagation':{2:1},'coupled_chi_operator_response':{8:1},'interaction_added_to_chi_operator_response':{8:1,2:-1},'raw_density_plus_reaction':{4:1,5:1}}
        supplement={}
        for window,gram in grams.items():
            supplement[window]={}
            for name,terms in channels.items():
                coeff=np.zeros(11)
                for index,value in terms.items():coeff[index]=value
                power=float(coeff@gram@coeff);dot=float(coeff@gram[:,0]);den=max(float(gram[0,0]),scale*1e-10)
                m={'relative_error':float(np.sqrt(max(0,power)/scale)),'signed_projection':dot/den,'cosine':dot/np.sqrt(max(1e-300,power*float(gram[0,0]))),'removal_squared_reduction':(2*dot-power)/den}
                supplement[window][name]=dict(metrics=m,passes_original_majority_criteria=reader.sufficient(m,result['criteria']),coefficients=terms)
        write(out/'propagacion_interaccion_derivadas.json',{'time':160,'M2_steps':0,'windows':supplement,'pure_chi_Phi_chi_return_separately_identifiable':False,
            'limitation':'The coupled-minus-bare response includes diagonal mean-Jacobian interaction and cross-field paths. Original observers do not isolate a pure chi-to-Phi-to-chi return. No new observer or physical evolution was integrated.','CP12_closed':False})
        receipt.update(status='COMPLETED',completed_at=now(),outputs={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='procedencia_lectura.json'})
        write(out/'procedencia_lectura.json',receipt)
        print(json.dumps({'analysis_id':analysis_id,'status':receipt['status'],'sufficient_coupled_channels':result['sufficient_coupled_channels'],'CP12_closed':False}))
    except BaseException as exc:
        receipt.update(status='FAILED',ended_at=now(),reason=repr(exc));write(out/'procedencia_lectura.json',receipt);raise

if __name__=='__main__':main()
