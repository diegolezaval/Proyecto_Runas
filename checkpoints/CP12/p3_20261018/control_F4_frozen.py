from controls_common import run, snapshots
"""New P3 F4; contrast methods adapted from historical P2, not a rerun of P2."""
import argparse,hashlib,json,math,os,sys
from pathlib import Path
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
assert not os.environ.get('OPENBLAS_CORETYPE')
import numpy as np
from scipy.sparse import bmat,eye
from scipy.sparse.linalg import expm_multiply
from threadpoolctl import threadpool_info
from control_F3_matrix import independent_spatial,independent_jacobian

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def taylor(H,Y,omega,T,steps,degree=32):
    Z=Y.copy();dt=T/steps;D=H.shape[0]
    for _ in range(steps):
        total=Z.copy();term=Z.copy()
        for k in range(1,degree+1):
            term=(dt/k)*np.vstack((omega*term[D:],-(H@term[:D])/omega))
            total+=term
        Z=total
    x=dt*omega
    log_bound=math.log(steps)+T*omega+x+(degree+1)*math.log(x)-math.lgamma(degree+2)
    return Z,math.exp(log_bound)

def control(root, output):
    sys.path[:0]=[str(root/'science/herramientas'),str(root/'candidate')]
    from p3_backend import MixedP3 as Mixed, MixedP3Gauss as MixedGauss, lap_mixed_p3 as lap_mixed
    import observador_causal_CP12 as obs
    from modelo_m2 import BENCHMARK as model
    rng=np.random.default_rng(20261018001);rows=[];passed=True;T=.1
    masses=np.array([model.mass2,model.mass2,model.mediator**2])
    for dx,pattern in ((.125,'temporal_h0125__*'),(.0625,'espacial_h00625__*')):
        sim=Mixed(dx,220.,4);cases=snapshots(root,dx);q0,q1,q80=[q for _,q,v in cases]
        S,rs=obs.symmetry_basis(sim,q0);scale=np.sqrt(np.array([2.,2.,1.])[:,None,None]*rs.w[None,:,None]);D=3*rs.n*rs.nm
        H0=independent_spatial(rs,masses)
        products=(rs.Y[:,None,:]*rs.Y[None,:,:]*rs.wa[None,None,:]).reshape(rs.nm*rs.nm,-1).T.copy()
        def canonical(q):return (q*scale).reshape(-1,D).T
        def physical(y):return y.T.reshape(5,3,rs.n,rs.nm)/scale
        def phase(y,omega):
            q=y[:D].T.reshape(5,3,rs.n,rs.nm);v=omega*y[D:].T.reshape(q.shape)
            return np.concatenate((q.reshape(5,-1),(v/np.sqrt(masses)[None,:,None,None]).reshape(5,-1)),axis=1)
        for label,qa,qb in (('initial',q0,q0),('initial_original160_mean',q0,q1),('mixed80',q80,q80)):
            _,_,jac=obs.terms(sim,sim,qa,qb)
            j=(jac.reshape(-1,len(sim.wa))@products).reshape(6,rs.n,rs.nm,rs.nm)
            H=H0-independent_jacobian(rs,j)
            bound=max(float(np.max(np.asarray(abs(H).sum(axis=1)))),float(np.max(np.asarray(abs(H).sum(axis=0)))))
            omega=math.sqrt(bound)
            B=bmat([[None,omega*eye(D,format='csr')],[-H/omega,None]],format='csr')
            qcan=rng.normal(size=(D,5))/math.sqrt(D);vcan=rng.normal(size=(D,5))/math.sqrt(D)
            Y=np.vstack((qcan,vcan/omega))
            # Three fixed independent approximation routes; no parameter search.
            ref=expm_multiply(T*B,Y,traceA=0.)
            ref16,tail16=taylor(H,Y,omega,T,16)
            ref32,tail32=taylor(H,Y,omega,T,32)
            pref=phase(ref,omega);den=max(float(np.linalg.norm(pref)),1e-300)
            difference16=float(np.linalg.norm(phase(ref16-ref,omega))/den)
            difference32=float(np.linalg.norm(phase(ref32-ref,omega))/den)
            split_difference=float(np.linalg.norm(phase(ref32-ref16,omega))/den)
            conversion=max(1.,omega/float(np.min(np.sqrt(masses))))
            truncation=max(tail16,tail32)*conversion*float(np.linalg.norm(Y))/den
            reference_pass=max(difference16,difference32,split_difference,truncation)<=1e-8
            item=dict(dx=dx,background=label,duration=T,windows=10,frequency_bound=omega,
                      reference_expm_vs_Taylor16=difference16,reference_expm_vs_Taylor32=difference32,
                      reference_Taylor_split_contrast=split_difference,reference_truncation_bound=truncation,
                      reference_certification='Fixed three-way controlled contrast plus analytic truncation bound; not interval arithmetic',
                      reference_passed=reference_pass,orders=[])
            if not reference_pass:
                item['passed']=False;rows.append(item);passed=False;print(json.dumps(item),flush=True);break
            e0=.5*np.sum(qcan*(H@qcan)+vcan*vcan,axis=0)
            for stages in (7,6):
                o=MixedGauss(rs,3,stages,physical(qcan)[0],physical(vcan)[0]);o.q=physical(qcan);o.v=physical(vcan)
                forcing=np.zeros((stages,5,3,rs.n,rs.nm));jm=np.broadcast_to(j,(stages,*j.shape))
                for _ in range(10):o.advance(.01,forcing,jm)
                actual=np.vstack((canonical(o.q),canonical(o.v)/omega))
                error=float(np.linalg.norm(phase(actual,omega)-pref)/den)
                qn=canonical(o.q);vn=canonical(o.v);en=.5*np.sum(qn*(H@qn)+vn*vn,axis=0)
                drift=float(np.max(abs(en-e0)/np.maximum(abs(e0),1e-300)))
                checks={'frozen_phase_error':error<=1e-3,'frozen_quadratic_balance':drift<=2e-4,
                        'original_stage_iteration_residual':o.max_iteration_residual<=1e-12,'original_stage_iteration_count':o.max_iterations<=12}
                item['orders'].append(dict(stages=stages,phase_error=error,quadratic_balance=drift,
                                           maximum_iterations=o.max_iterations,maximum_iteration_residual=o.max_iteration_residual,
                                           tests=checks,passed=all(checks.values())))
                if not all(checks.values()):passed=False;break
            item['passed']=reference_pass and all(x['passed'] for x in item['orders']) and len(item['orders'])==2
            rows.append(item);print(json.dumps(item),flush=True)
            if not item['passed']:passed=False;break
        if not passed:break
    result=dict(schema='CP12_P3_FROZEN_LINEAR_PREFLIGHT_NOT_CORRECTION_VALIDATION',passed=passed,rows=rows,
                M2_steps_executed=0,physical_histories_evolved=0,physical_evolution_authorized=False,
                correction_validated=False,CP12_closed=False)
    return result

if __name__=='__main__':raise SystemExit(run('F4',control))
