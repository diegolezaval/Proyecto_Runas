"""Actual M2 forces and frozen-Jacobian linear controls; no physical M2 steps."""
from pathlib import Path
import argparse,hashlib,json,os,sys
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--home',type=Path,required=True);ap.add_argument('--prereg-commit',required=True);a=ap.parse_args()
    home=a.home.resolve();folder=Path(__file__).parent;out=folder/'diagnostico_fallo_acoplado.json';assert not out.exists()
    meta=read(home/'preregistration/nueva_identidad.json');proof=read(home/'proofs/tau0048_permanent.json')
    assert proof['passed'] and proof['execution_run_id']==meta['execution_run_id'] and proof['independent_extracted_audit']['passed']
    restored=home/'recoveries'/(Path(proof['file_name']).stem+'_checked')/meta['execution_uuid'];root=restored/'science';run=root/meta['run_relative']
    assert sha(run/'CP12_par_estado.npz')==proof['state_sha256'];identity=read(restored/'preregistration/identidad_cientifica.json')
    assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    sys.path.insert(0,str(root/'herramientas'));sys.path.insert(0,str(folder.parent/'candidato_operador'))
    import numpy as np
    from scipy import sparse
    from scipy.sparse.linalg import expm_multiply
    from threadpoolctl import threadpool_limits
    import acelerar_fuerza_m2 as accelerated
    import observador_causal_CP12 as obs
    from operador import Candidate
    from backend import CandidateGauss,weighted_bands,lap_general
    cache=home/'runtime/candidate_force_cache';cache.mkdir(exist_ok=True);accelerated.OUT=cache;obs.OUT=cache
    with np.load(run/'CP12_par_estado.npz',allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    cfg=json.loads(str(saved['config']));n=int(saved['coarse_n']);sc,sf=[Candidate(c['dx'],c['radius'],c['L']) for c in cfg['physical_configurations']]
    rng=np.random.default_rng(20261012009);force_controls=[];identities=[];frozen=[]
    with threadpool_limits(limits=1):
        standard=[sim.force for sim in [sc,sf]]
        for sim in [sc,sf]:assert accelerated.install(sim)['source_sha256']==identity['code_hashes']['herramientas/fuerza_potencial_m2.c']
        for t,qn,vn in [(0,'initial_q','initial_v'),(48,'q','v')]:
            qc,qf=saved[qn][:,:n],saved[qn][:,n:];vc,vf=saved[vn][:,:n],saved[vn][:,n:]
            for i,(sim,q) in enumerate(zip([sc,sf],[qc,qf])):
                errors=[]
                for j in range(5):
                    trial=q if j==0 else q+rng.normal(size=q.shape)*1e-5
                    reference=standard[i](trial);tested=sim.force(trial)
                    errors.append(float(np.max(abs(reference-tested))/max(1.,float(np.max(abs(reference))))))
                assert max(errors)<=2e-12
                force_controls.append(dict(time=t,dx=sim.dx,errors=errors,passed=True,potential_M2_changed=False,radial_action='candidate_K4'))
            qi=obs.interpolate(sc,qc,sf);d=qi-qf
            bare,coupled,jac=obs.terms(sc,sf,qc,qf)
            comm=obs.interpolate(sc,lap_general(sc,qc),sf)-lap_general(sf,qi)
            transfer=coupled[3:].sum(0)
            lhs=obs.interpolate(sc,sc.force(qc),sf)-sf.force(qf)
            rhs=lap_general(sf,d)-np.array([1.,1.,10000.])[:,None,None]*d+comm+transfer+obs.apply_jac(sf,jac,d[None])[0]
            residual=float(np.max(abs(lhs-rhs))/max(1.,float(np.max(abs(lhs)))));print(json.dumps({'time':t,'lhs_max':float(np.max(abs(lhs))),'absolute_residual':float(np.max(abs(lhs-rhs))),'scaled_residual':residual,'force_controls':force_controls,'by_field_absolute':[float(np.max(abs((lhs-rhs)[i]))) for i in range(3)],'original_nonlinear_mean_J_identity_abs':float(np.max(abs(obs.nonlinear(sf,qi@sf.Y)-obs.nonlinear(sf,qf@sf.Y)-obs.apply_jac(sf,jac,d[None])[0]))),'lap_linearity_abs':float(np.max(abs(lap_general(sf,qi)-lap_general(sf,qf)-lap_general(sf,d))))},allow_nan=False),flush=True);return
            identities.append(dict(time=t,full_instantaneous_defect_scaled_residual=residual,passed=True))
            S,reduced=obs.symmetry_basis(sf,saved['initial_q'][:,n:]);nm=reduced.nm;N=reduced.n;D=3*N*nm
            products=(reduced.Y[:,None,:]*reduced.Y[None,:,:]*sf.wa[None,None,:]).reshape(nm*nm,-1).T.copy()
            blocks=(jac.reshape(-1,len(sf.wa))@products).reshape(6,N,nm,nm)
            ids=np.arange(D).reshape(3,N,nm);rows=[];cols=[];values=[];masses=np.array([1.,1.,10000.]);canon=np.array([np.sqrt(2),np.sqrt(2),1.])
            for f in range(3):
                for m,ell in enumerate(reduced.ell):
                    diag,e,e2=weighted_bands(reduced,int(ell));idx=ids[f,:,m]
                    rows.append(idx);cols.append(idx);values.append(diag+masses[f])
                    for offset,band in [(1,e),(2,e2)]:
                        rows.extend([idx[:-offset],idx[offset:]]);cols.extend([idx[offset:],idx[:-offset]]);values.extend([band,band])
            map_blocks=[[blocks[0],blocks[2],np.sqrt(2)*blocks[3]],[blocks[2],blocks[1],np.sqrt(2)*blocks[4]],[np.sqrt(2)*blocks[3],np.sqrt(2)*blocks[4],blocks[5]]]
            for f in range(3):
                for g in range(3):
                    rows.append(np.broadcast_to(ids[f,:, :,None],(N,nm,nm)).ravel());cols.append(np.broadcast_to(ids[g,:,None,:],(N,nm,nm)).ravel());values.append(-map_blocks[f][g].ravel())
            H=sparse.coo_matrix((np.concatenate(values),(np.concatenate(rows),np.concatenate(cols))),shape=(D,D)).tocsr()
            antisymmetric=H-H.T;symmetry=float(np.max(abs(antisymmetric.data),initial=0)/max(1.,float(np.max(abs(H.data)))));assert symmetry<=2e-12
            mf=np.repeat(np.sqrt(masses),N*nm);M=sparse.diags(mf);Mi=sparse.diags(1/mf)
            G=sparse.bmat([[None,M],[-Mi@H,None]],format='csr')
            q0=rng.normal(size=(5,3,N,nm));v0=rng.normal(size=q0.shape);factor=canon[:,None,None]*np.sqrt(sf.w)[None,:,None]
            Q=(q0*factor[None]).reshape(5,-1).T;P=(v0*factor[None]/np.sqrt(masses)[None,:,None,None]).reshape(5,-1).T;Z0=np.vstack([Q,P])
            action=CandidateGauss(reduced,3,7,q0[0],v0[0]).action(q0)-obs.apply_jac(reduced,blocks,q0)
            expected=np.vstack([(v0*factor[None]).reshape(5,-1).T,(-action*factor[None]/np.sqrt(masses)[None,:,None,None]).reshape(5,-1).T])
            action_residual=float(np.max(abs(G@Z0-expected))/max(1.,float(np.max(abs(expected)))));assert action_residual<=2e-12
            exact=expm_multiply(G*.01,Z0,traceA=0.)
            eq=exact[:D].T.reshape(q0.shape)/factor[None];ev=exact[D:].T.reshape(v0.shape)*np.sqrt(masses)[None,:,None,None]/factor[None]
            norm=lambda q,v:float(np.sum(sf.w[None,None,:,None]*canon[None,:,None,None]**2*(q*q+v*v/masses[None,:,None,None])))
            energy=lambda q,v:float((np.sum((v*factor[None])**2)+np.sum(((q*factor[None]).reshape(5,-1).T)*(H@((q*factor[None]).reshape(5,-1).T))))/2)
            E0=energy(q0,v0)
            for stages in [7,6]:
                solver=CandidateGauss(reduced,3,stages,q0[0],v0[0]);solver.q=q0.copy();solver.v=v0.copy()
                solver.advance(.01,np.zeros((stages,*q0.shape)),np.repeat(blocks[None],stages,axis=0))
                error=float(np.sqrt(norm(solver.q-eq,solver.v-ev)/norm(q0,v0)));balance=abs(energy(solver.q,solver.v)/E0-1)
                assert error<=1e-3 and balance<=2e-4
                frozen.append(dict(time=t,stages=stages,step=.01,canonical_symmetry_residual=symmetry,canonical_action_residual=action_residual,sparse_exponential_phase_relative_error=error,quadratic_energy_relative_change=balance,iterations=solver.last_iterations,iteration_residual=solver.max_iteration_residual,passed=True))
            print(json.dumps(dict(snapshot=t,force_controls_passed=True,instantaneous_identity=residual,frozen_controls=frozen[-2:],M2_steps=0)),flush=True)
    assert sha(run/'CP12_par_estado.npz')==proof['state_sha256'] and all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    result=dict(schema='CP12_CANDIDATE_M2_FORCE_AND_FROZEN_INTERACTION_PREFLIGHT',execution_uuid=meta['execution_uuid'],execution_run_id=meta['execution_run_id'],input_proof_sha256=sha(home/'proofs/tau0048_permanent.json'),input_state_sha256=proof['state_sha256'],preregistration_git_commit=a.prereg_commit,preregistration_sha256=sha(folder/'PRERREGISTRO_ACOPLADO.md'),source_sha256=sha(Path(__file__)),backend_sha256=sha(folder/'backend.py'),force_controls=force_controls,instantaneous_identities=identities,frozen_jacobian_controls=frozen,M2_steps=0,original_trajectories_untouched=True,nonlinear_history_validated=False,corrected_DOP853_trajectory_validated=False,physical_gate_evaluated=False,CP12_closed=False,passed=True)
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');tmp.replace(out)
    print(json.dumps(dict(passed=True,M2_steps=0,CP12_closed=False)))

if __name__=='__main__':main()
