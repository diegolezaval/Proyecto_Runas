"""Original CP11 elliptic reference on new certified snapshots; no M2 evolution."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--home',type=Path,required=True);p.add_argument('--boundary',type=int,required=True);a=p.parse_args()
    home=a.home.resolve();t=a.boundary;assert t>=32 and t%8==0 and t<=160
    out=home/'analysis/condicional'/('tau%04d'%t);out.mkdir()
    try:
        meta=read(home/'preregistration/nueva_identidad.json');proof_path=home/'proofs'/('tau%04d_permanent.json'%t);proof=read(proof_path)
        assert proof['passed'] and proof['time']==t and proof['execution_run_id']==meta['execution_run_id'] and proof['independent_extracted_audit']['passed']
        restored=home/'recoveries'/(Path(proof['file_name']).stem+'_checked')/meta['execution_uuid'];root=restored/'science';run=root/meta['run_relative']
        assert sha(run/'CP12_par_estado.npz')==proof['state_sha256'] and sha(run/'procedencia.json')==proof['receipt_sha256']
        identity=read(restored/'preregistration/identidad_cientifica.json');assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
        sys.path.insert(0,str(root/'herramientas'))
        import numpy as np
        from scipy.linalg import eigh_tridiagonal
        from threadpoolctl import threadpool_limits
        from continuar_no_radial_m2 import Evolution
        from observador_causal_CP12 import chi_inner,interpolate,model
        from diagnosticar_chi_CP11 import frozen_equilibrium,tridiagonal
        source=home/'analysis/sources/interpretar_presupuesto_CP12_original.py';spec=importlib.util.spec_from_file_location('original_metrics',source);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        with np.load(run/'CP12_par_estado.npz',allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
        assert float(saved['time'])==t;cfg=json.loads(str(saved['config']));n=int(saved['coarse_n'])
        sc,sf=[Evolution(c['dx'],c['radius'],c['L']) for c in cfg['physical_configurations']]
        cp11_receipts=list((root/'validacion/P06/no_radial/CP11').glob('respuesta_forzada_precisa__*/procedencia.json'));assert len(cp11_receipts)==1
        diagnostic_cfg=read(cp11_receipts[0])['identity']['case']['configuration'];assert diagnostic_cfg['elliptic_relative_tolerance']==2e-10 and diagnostic_cfg['algebra_relative_tolerance']==2e-12
        references=[];audits=[]
        with threadpool_limits(limits=1):
            for sim,use in [(sc,slice(0,n)),(sf,slice(n,None))]:
                eq,veq,unused,report=frozen_equilibrium({},sim,saved['q'][:,use],saved['v'][:,use],diagnostic_cfg)
                references.append((eq,veq));audits.append(report)
        dq=interpolate(sc,saved['q'][:,:n],sf)-saved['q'][:,n:];dv=interpolate(sc,saved['v'][:,:n],sf)-saved['v'][:,n:]
        eqc,vec=references[0];eqf,vef=references[1]
        dref=interpolate(sc,eqc,sf)-eqf;vref=interpolate(sc,vec,sf)-vef
        q=np.array([dq[2],dref,dq[2]-dref]);v=np.array([dv[2],vref,dv[2]-vref])
        scale=chi_inner(sf,saved['initial_q'][2,n:],saved['initial_v'][2,n:],saved['initial_q'][2,n:],saved['initial_v'][2,n:])
        core=np.array([[chi_inner(sf,x,y,z,w) for z,w in zip(q,v)] for x,y in zip(q,v)])
        criteria=read(root/'datos/ensayo_causal_chi_CP12.json')['observer_criteria'];last=json.loads(str(saved['budget_rows']))[-1]
        use=sf.r<40;window=np.ones(use.sum());transition=(sf.r[use]>=32);window[transition]=.5*(1+np.cos(np.pi*(sf.r[use][transition]-32)/8))
        grams={'core_phase':core};spectral_checks={}
        lower={}
        with threadpool_limits(limits=1):
            for ell in [1,2,3,4]:
                d,e=tridiagonal(sf,ell);lam,U=eigh_tridiagonal(d,e,select='v',select_range=(0.,16.),lapack_driver='stebz');lower[ell]=U[use]
            for label,win in [('core',np.ones(use.sum())),('smooth',window)]:
                gram=np.zeros((3,3))
                for ell in [1,2,3,4]:
                    sel=sf.ell==ell;nm=int(sel.sum());sw=np.sqrt(sf.w[use])*win
                    xq=(q[:,use][:,:,sel]*sw[None,:,None]).transpose(1,0,2).reshape(use.sum(),-1)
                    xv=(v[:,use][:,:,sel]*sw[None,:,None]/model.mediator).transpose(1,0,2).reshape(use.sum(),-1)
                    total=xq.T@xq+xv.T@xv;belowq=lower[ell].T@xq;belowv=lower[ell].T@xv
                    remainder=total-belowq.T@belowq-belowv.T@belowv
                    gram+=np.einsum('imjm->ij',remainder.reshape(3,nm,3,nm))
                expected=last['short_modes'][label]['short_response_gram_matrix'][0][0]
                difference=abs(float(gram[0,0])-expected)/max(expected,scale*1e-20)
                assert difference<=2e-11,'Original spectral window does not reproduce'
                spectral_checks[label]={'observed_norm_relative_difference':difference,'original_parseval_tolerance':2e-11,'passed':True}
                grams['short_'+label+'_k4']=gram
        tables={};cross={}
        for label,gram in grams.items():
            tables[label]={name:reader.metrics(gram,[i],scale) for name,i in [('instantaneous_reference_difference',1),('nonstationary_residue_difference',2)]}
            cross[label]=gram.tolist()
        S=saved['coupled_angular_basis']
        with threadpool_limits(limits=1):pq,pv=saved['coupled_0_q'][2,:2]@S.T,saved['coupled_0_v'][2,:2]@S.T
        phi_inner=lambda aq,av,bq,bv:float(np.sum(sf.w[None,:,None]*(aq*bq+av*bv/model.mass2)))
        phi_scale=phi_inner(saved['initial_q'][:2,n:],saved['initial_v'][:2,n:],saved['initial_q'][:2,n:],saved['initial_v'][:2,n:])
        phi_gram=np.array([[phi_inner(x,y,z,w) for z,w in [(dq[:2],dv[:2]),(pq,pv)]] for x,y in [(dq[:2],dv[:2]),(pq,pv)]])
        phi_metrics=reader.metrics(phi_gram,[1],phi_scale)
        assert all(sha(root/n)==h for n,h in identity['code_hashes'].items()) and sha(run/'CP12_par_estado.npz')==proof['state_sha256']
        np.savez_compressed(out/'componentes.npz',reference_coarse_q=eqc,reference_coarse_v=vec,reference_fine_q=eqf,reference_fine_v=vef,reference_difference_q=dref,reference_difference_v=vref,nonstationary_difference_q=q[2],nonstationary_difference_v=v[2])
        result={'schema':'CP12_PASSIVE_INSTANTANEOUS_PHI_CONDITIONED_REFERENCE','time':t,'execution_run_id':meta['execution_run_id'],'proof_sha256':sha(proof_path),'state_sha256':proof['state_sha256'],
            'diagnostic_CP11_configuration':diagnostic_cfg,'elliptic_audits':audits,'spectral_window_verification':spectral_checks,'tables':tables,'cross_grams':cross,
            'Phi_response_to_chi_operator_alignment_full_box':phi_metrics,'Phi_alignment_new_gate_applied':False,'M2_steps':0,'original_scientific_sources_unchanged':True,'physical_state_not_substituted':True,
            'stationary_or_adiabatic_physical_evolution_assumed':False,'nonstationary_residue_proved_free_wave':False,'independent_causal_identification_proved':False,'physical_gate_evaluated':False,'CP12_closed':False,
            'source_sha256':sha(Path(__file__)),'preregistration_sha256':sha(home/'analysis/condicional/PRERREGISTRO.md'),'CP11_function_source_sha256':sha(root/'herramientas/diagnosticar_chi_CP11.py'),'components_sha256':sha(out/'componentes.npz')}
        (out/'resultados.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps({'time':t,'M2_steps':0,'elliptic_residuals':[[r['field']['relative_residual'],r['velocity']['relative_residual']] for r in audits],'core_tables':tables['core_phase'],'Phi_response_alignment':phi_metrics,'CP12_closed':False}))
    except BaseException as exc:
        (out/'fallo.json').write_text(json.dumps({'time':t,'M2_steps':0,'diagnostic_only':True,'reason':repr(exc),'original_trajectories_unchanged':True,'CP12_closed':False},indent=2)+'\n');raise

if __name__=='__main__':main()
