"""Local canonical mean-Jacobian spectrum; no propagation or physical acceptance."""
from pathlib import Path
import argparse, hashlib, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--home',type=Path,required=True);p.add_argument('--boundary',type=int,required=True);a=p.parse_args();home=a.home.resolve();t=a.boundary
    assert t>=32 and t%8==0 and t<=160
    meta=read(home/'preregistration/nueva_identidad.json');proof_path=home/'proofs'/('tau%04d_permanent.json'%t);proof=read(proof_path)
    assert proof['passed'] and proof['time']==t and proof['execution_run_id']==meta['execution_run_id'] and proof['independent_extracted_audit']['passed']
    restored=home/'recoveries'/(Path(proof['file_name']).stem+'_checked')/meta['execution_uuid'];root=restored/'science';run=root/meta['run_relative'];state=run/'CP12_par_estado.npz'
    assert sha(state)==proof['state_sha256']
    identity=read(restored/'preregistration/identidad_cientifica.json');assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    sys.path.insert(0,str(root/'herramientas'))
    import numpy as np
    from threadpoolctl import threadpool_limits
    from continuar_no_radial_m2 import Evolution
    from observador_causal_CP12 import chi_inner,interpolate,terms,model
    with np.load(state,allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    assert float(saved['time'])==t;cfg=json.loads(str(saved['config']));n=int(saved['coarse_n']);sc,sf=[Evolution(c['dx'],c['radius'],c['L']) for c in cfg['physical_configurations']]
    with threadpool_limits(limits=1):unused0,unused1,jac=terms(sc,sf,saved['q'][:,:n],saved['q'][:,n:])
    use=sf.r<40;J=jac[:,use];H=np.zeros((use.sum(),sf.Y.shape[1],3,3))
    H[:,:,0,0]=model.mass2-J[0];H[:,:,1,1]=model.mass2-J[1];H[:,:,2,2]=model.mediator**2-J[5]
    H[:,:,0,1]=H[:,:,1,0]=-J[2];H[:,:,0,2]=H[:,:,2,0]=-np.sqrt(2)*J[3];H[:,:,1,2]=H[:,:,2,1]=-np.sqrt(2)*J[4]
    with threadpool_limits(limits=1):values,vectors=np.linalg.eigh(H)
    highest=values[:,:,-1];diagonal=H[:,:,2,2];assert np.all(highest>0) and np.all(highest>=diagonal-2e-10)
    frequency=np.sqrt(highest);diag_frequency=np.sqrt(diagonal);participation=vectors[:,:,2,-1]**2
    dq=interpolate(sc,saved['q'][:,:n],sf)-saved['q'][:,n:];dv=interpolate(sc,saved['v'][:,:n],sf)-saved['v'][:,n:]
    nrq=dq[2,use].copy();nrv=dv[2,use].copy();nrq[:,0]=0;nrv[:,0]=0
    with threadpool_limits(limits=1):xq=nrq@sf.Y;xv=nrv@sf.Y/model.mediator
    weights=sf.w[use,None]*sf.wa[None,:]*(xq*xq+xv*xv);total=float(weights.sum())
    exact=chi_inner(sf,dq[2],dv[2],dq[2],dv[2]);parseval=abs(total-exact)/max(exact,1e-300);assert parseval<=2e-11
    flat=weights.ravel();assert total>0
    def summary(x):
        z=x.ravel();order=np.argsort(z);cumulative=np.cumsum(flat[order])/total
        percentiles={str(q):float(z[order[min(np.searchsorted(cumulative,q/100),len(order)-1)]]) for q in [5,50,95]}
        return {'weighted_mean':float(np.dot(flat,z)/total),'weighted_percentiles':percentiles,'minimum_all_core_points':float(z.min()),'maximum_all_core_points':float(z.max())}
    ratios={str(k):summary(-(highest-diagonal)/(diagonal+4*np.sin(k*sf.dx/2)**2/sf.dx**2)) for k in cfg['wave_number_cuts']}
    result={'schema':'CP12_PASSIVE_CANONICAL_LOCAL_MEAN_JACOBIAN_HIGH_BRANCH','time':t,'execution_run_id':meta['execution_run_id'],'proof_sha256':sha(proof_path),'state_sha256':proof['state_sha256'],
        'original_model_parameters':{'mass2_Phi':model.mass2,'mediator':model.mediator,'quartic':model.quartic,'trilinear':model.trilinear,'mixed':model.mixed},
        'highest_local_frequency':summary(frequency),'chi_diagonal_frequency_shift':summary(diag_frequency-model.mediator),'highest_branch_extra_shift':summary(frequency-diag_frequency),'chi_participation_highest_branch':summary(participation),
        'local_stationary_chi_to_high_mode_ratios_fine_grid':ratios,'all_eigenvalue_ranges':[{'minimum':float(values[:,:,i].min()),'maximum':float(values[:,:,i].max())} for i in range(3)],
        'original_phase_weight_parseval_relative_residual':parseval,'M2_steps':0,'original_scientific_sources_unchanged':True,'full_radial_generator_stability_claimed':False,'actual_time_dependent_phase_history_predicted':False,
        'pure_global_feedback_return_isolated':False,'physical_gate_evaluated':False,'physical_correction_tested':False,'CP12_closed':False,'source_sha256':sha(Path(__file__)),'preregistration_sha256':sha(home/'analysis/jacobiano_local/PRERREGISTRO.md')}
    assert sha(state)==proof['state_sha256'] and all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    out=home/'analysis/jacobiano_local'/('tau%04d.json'%t);assert not out.exists();out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'time':t,'original_model_parameters':result['original_model_parameters'],'weighted_highest_frequency':result['highest_local_frequency']['weighted_mean'],'weighted_chi_participation':result['chi_participation_highest_branch']['weighted_mean'],
        'weighted_diagonal_shift':result['chi_diagonal_frequency_shift']['weighted_mean'],'weighted_extra_shift':result['highest_branch_extra_shift']['weighted_mean'],'stationary_ratio_k8':ratios['8']['weighted_mean'],'M2_steps':0,'CP12_closed':False}))

if __name__=='__main__':main()
