"""Static action and exact linear response controls; no original M2 steps."""
from pathlib import Path
import argparse,hashlib,json,os,sys
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--home',type=Path,required=True);ap.add_argument('--prereg-commit',required=True);a=ap.parse_args()
    home=a.home.resolve();root=home/'science';folder=Path(__file__).parent;out=folder/'resultados.json';assert not out.exists()
    identity=json.loads((home/'preregistration/identidad_cientifica.json').read_text());assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    sys.path.insert(0,str(root/'herramientas'));sys.path.insert(0,str(folder.parent/'candidato_operador'))
    import numpy as np
    from threadpoolctl import threadpool_limits
    from operador import Candidate
    from backend import CandidateGauss,weighted_bands,lap_general
    rng=np.random.default_rng(20261012008);algebra=[];responses=[]
    with threadpool_limits(limits=1):
        for h in [.125,.0625,.03125]:
            sim=Candidate(h,2.,4);eig={}
            for ell in range(5):
                d,e,f=weighted_bands(sim,ell);H=np.diag(d)+np.diag(e,1)+np.diag(e,-1)+np.diag(f,2)+np.diag(f,-2)
                lam,U=np.linalg.eigh(H);assert lam[0]>0;sel=sim.ell==ell
                trial=rng.normal(size=(3,sim.n,sim.nm));expected=np.einsum('ij,fjm->fim',H,np.sqrt(sim.w)[None,:,None]*trial[:,:,sel])
                actual=-np.sqrt(sim.w)[None,:,None]*lap_general(sim,trial)[:,:,sel]
                residual=float(np.max(abs(actual-expected))/max(1.,float(np.max(abs(expected)))))
                assert residual<=2e-12
                compare=float(np.max(abs(lap_general(sim,trial)-sim.lap(trial)))/max(1.,float(np.max(abs(sim.lap(trial))))));assert compare<=2e-12
                algebra.append(dict(h=h,ell=ell,min_eigenvalue=float(lam[0]),max_eigenvalue=float(lam[-1]),weighted_action_relative_residual=residual,original_candidate_prototype_relative_difference=compare,symmetric=bool(np.array_equal(H,H.T))))
                eig[ell]=(lam,U)
            for fields in [1,3]:
                iq=rng.normal(size=(fields,sim.n,sim.nm));iv=rng.normal(size=iq.shape);masses=np.array([10000.] if fields==1 else [1.,1.,10000.]);weights=np.array([1.] if fields==1 else [2.,2.,1.])
                def energy(obs):return float(np.sum(sim.w[None,None,:,None]*weights[None,:,None,None]*(obs.v**2+obs.q*obs.action(obs.q)))/2)
                def charge(obs):return 0. if fields==1 else float(np.sum(sim.w[None,:,None]*(obs.q[:,0]*obs.v[:,1]-obs.q[:,1]*obs.v[:,0])))
                for stages in [7,6]:
                    for step in [.005,.01]:
                        for force_label in ['zero','constant']:
                            obs=CandidateGauss(sim,fields,stages,iq,iv);q0=obs.q.copy();v0=obs.v.copy();forcing=np.zeros_like(q0) if force_label=='zero' else rng.normal(size=q0.shape)
                            e0=energy(obs);c0=charge(obs);obs.advance(step,np.repeat(forcing[None],stages,axis=0))
                            eq=np.empty_like(q0);ev=np.empty_like(v0);sw=np.sqrt(sim.w)
                            for ell,(lam,U) in eig.items():
                                sel=np.flatnonzero(sim.ell==ell)
                                for field in range(fields):
                                    w=np.sqrt(masses[field]+lam);C=np.cos(w*step);S=np.sin(w*step)
                                    def transform(x):return np.einsum('ij,cjm->cim',U.T,x[:,:,sel]*sw[None,:,None])
                                    x,y,F=transform(q0[:,field]),transform(v0[:,field]),transform(forcing[:,field])
                                    x1=C[None,:,None]*x+(S/w)[None,:,None]*y+((1-C)/(w*w))[None,:,None]*F
                                    y1=(-w*S)[None,:,None]*x+C[None,:,None]*y+(S/w)[None,:,None]*F
                                    eq[:,field,:,sel]=np.einsum('ij,cjm->cim',U,x1).transpose(2,0,1)/sw[None,None,:]
                                    ev[:,field,:,sel]=np.einsum('ij,cjm->cim',U,y1).transpose(2,0,1)/sw[None,None,:]
                            phase=lambda q,v:float(np.sum(sim.w[None,None,:,None]*(q*q+v*v/masses[None,:,None,None])))
                            error=float(np.sqrt(phase(obs.q-eq,obs.v-ev)/phase(q0,v0)));assert error<=1e-3
                            de=abs(energy(obs)/e0-1);dc=abs(charge(obs)-c0)/max(1.,abs(c0))
                            if force_label=='zero':assert de<=2e-4 and dc<=1e-9
                            responses.append(dict(h=h,fields=fields,stages=stages,step=step,force=force_label,exact_linear_phase_relative_error=error,homogeneous_energy_relative_change=de if force_label=='zero' else None,homogeneous_charge_scaled_change=dc if force_label=='zero' else None))
    assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    result=dict(schema='CP12_CANDIDATE_FIVE_BAND_PASSIVE_BACKEND_PREFLIGHT',preregistration_git_commit=a.prereg_commit,preregistration_sha256=sha(folder/'PRERREGISTRO.md'),backend_sha256=sha(folder/'backend.py'),verification_source_sha256=sha(Path(__file__)),algebra=algebra,responses=responses,M2_steps=0,original_scientific_sources_unchanged=True,original_trajectories_untouched=True,nonlinear_feedback_backend_validated=False,corrected_DOP853_trajectory_validated=False,physical_gate_evaluated=False,CP12_closed=False,passed=True)
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');tmp.replace(out)
    print(json.dumps(dict(passed=True,M2_steps=0,maximum_action_residual=max(x['weighted_action_relative_residual'] for x in algebra),maximum_exact_linear_phase_error=max(x['exact_linear_phase_relative_error'] for x in responses),CP12_closed=False)))

if __name__=='__main__':main()
