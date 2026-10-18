from controls_common import run, snapshots
"""New P3 F3; contrast methods adapted from historical P2, not a rerun of P2."""
import argparse,hashlib,json,os,sys
from pathlib import Path
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
assert not os.environ.get('OPENBLAS_CORETYPE')
import numpy as np
from scipy.sparse import coo_matrix,diags
from threadpoolctl import threadpool_info

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def independent_spatial(sim,masses):
    """No calls to the physical laplacian or prototype weighted-band builders."""
    n,nm=sim.n,sim.nm;dimension=3*n*nm;rows=[];cols=[];vals=[]
    for field in range(3):
        for mode,ell in enumerate(sim.ell):
            r=sim.r;w=sim.w;h=sim.dx;faces=sim.edges[1:-1]**2/h
            if field<2:
                d=np.r_[faces,0.]+np.r_[0.,faces]+h*ell*(ell+1)
                d[-1]+=2*sim.radius**2/h;d/=w
                e=-faces/np.sqrt(w[:-1]*w[1:])
                H=diags([e,d,e],[-1,0,1],format='csr')
            else:
                power=r**ell;mass=w*power**2
                conductance=(2*ell+3)*np.cumsum(mass)[:-1]/(sim.edges[1:-1]*h)
                d=np.r_[conductance,0.]+np.r_[0.,conductance]
                d[-1]+=2*(2*ell+3)*mass.sum()/(sim.radius*h)
                d/=mass;e=-conductance/(power[:-1]*power[1:]*np.sqrt(w[:-1]*w[1:]))
                H2=diags([e,d,e],[-1,0,1],format='csr')
                H=H2+(h*h/12)*(H2@H2)+(h**4/90)*(H2@H2@H2)
            H=H+diags(np.full(n,masses[field]),format='csr');c=H.tocoo()
            rows.extend(field*n*nm+c.row*nm+mode);cols.extend(field*n*nm+c.col*nm+mode);vals.extend(c.data)
    return coo_matrix((vals,(rows,cols)),shape=(dimension,dimension)).tocsr()

def independent_jacobian(sim,j):
    n,nm=sim.n,sim.nm;D=3*n*nm;rows=[];cols=[];vals=[]
    component=np.array([[0,2,3],[2,1,4],[3,4,5]]);weight=np.sqrt([2.,2.,1.])
    for a in range(3):
        for b in range(3):
            block=j[component[a,b]]*(2 if a==2 and b<2 else 1)*weight[a]/weight[b]
            for i in range(nm):
                for k in range(nm):
                    index=np.arange(n);rows.extend(a*n*nm+index*nm+i);cols.extend(b*n*nm+index*nm+k);vals.extend(block[:,i,k])
    return coo_matrix((vals,(rows,cols)),shape=(D,D)).tocsr()

def control(root, output):
    sys.path[:0]=[str(root/'science/herramientas'),str(root/'candidate')]
    from p3_backend import MixedP3 as Mixed, MixedP3Gauss as MixedGauss, lap_mixed_p3 as lap_mixed
    import observador_causal_CP12 as obs
    from modelo_m2 import BENCHMARK as model
    rng=np.random.default_rng(20261018001);result=[];passed=True
    masses=np.array([model.mass2,model.mass2,model.mediator**2])
    for dx,pattern in ((.125,'temporal_h0125__*'),(.0625,'espacial_h00625__*')):
        sim=Mixed(dx,220.,4);cases=snapshots(root,dx);q0,q1,q80=[q for _,q,v in cases]
        S,rs=obs.symmetry_basis(sim,q0);scale=np.sqrt(np.array([2.,2.,1.])[:,None,None]*rs.w[None,:,None]);D=3*rs.n*rs.nm
        H0=independent_spatial(rs,masses)
        def canonical(q):return (q*scale).reshape(-1,D).T
        def action(H,q):return ((H@canonical(q)).T.reshape(q.shape))/scale
        products=(rs.Y[:,None,:]*rs.Y[None,:,:]*rs.wa[None,None,:]).reshape(rs.nm*rs.nm,-1).T.copy()
        for label,qa,qb in (('initial',q0,q0),('initial_original160_mean',q0,q1),('mixed80',q80,q80)):
            _,_,jac=obs.terms(sim,sim,qa,qb)
            j=(jac.reshape(-1,len(sim.wa))@products).reshape(6,rs.n,rs.nm,rs.nm)
            H=H0-independent_jacobian(rs,j)
            norm=max(1.,float(np.max(abs(H.data))))
            symmetry=float(np.max(abs((H-H.T).data),initial=0.)/norm)
            trial=rng.normal(size=(5,3,rs.n,rs.nm))/scale
            observer=MixedGauss(rs,3,7,trial[0],np.zeros_like(trial[0]))
            physical=observer.action(trial)-obs.apply_jac(rs,j,trial)
            reference=action(H,trial)
            action_error=float(np.max(abs(canonical(physical-reference)))/max(1.,float(np.max(abs(canonical(reference))))))
            tests={'canonical_matrix_action':action_error<=2e-12,'canonical_matrix_symmetry':symmetry<=2e-12}
            solves=[]
            for stages in (7,6):
                o=MixedGauss(rs,3,stages,trial[0],np.zeros_like(trial[0]));o.q=trial.copy();o.v=rng.normal(size=trial.shape)/scale
                forcing=rng.normal(size=(stages,*trial.shape))/scale;h=.01
                Q=o.stage_solve(h,forcing)
                expected=o.q[None]+h*o.A1[:,None,None,None,None]*o.v[None]+h*h*np.tensordot(o.A2,forcing-action(H0,Q),axes=(1,0))
                error=float(np.max(abs(canonical(Q-expected)))/max(1.,float(np.max(abs(canonical(Q))))))
                tests['mixed_resolvent_order_'+str(stages)]=error<=2e-12
                solves.append(dict(stages=stages,residual=error))
            row=dict(dx=dx,background=label,canonical_dimension=D,canonical_matrix_action_error=action_error,canonical_matrix_symmetry_error=symmetry,resolvents=solves,tests=tests,passed=all(tests.values()))
            result.append(row);print(json.dumps(row),flush=True)
            if not row['passed']:passed=False;break
        if not passed:break
    final=dict(schema='CP12_P3_PHASE_C_MATRIX_AND_RESOLVENT_NOT_FROZEN_APPROVAL',passed=passed,rows=result,M2_steps_executed=0,
               remaining_controls=['frozen_Gauss_7_6_reference_phase_and_balance'],all_registered_controls_passed=False,physical_evolution_authorized=False,correction_validated=False,CP12_closed=False)
    return final

if __name__=='__main__':raise SystemExit(run('F3',control))
