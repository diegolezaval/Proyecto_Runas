from controls_common import run, snapshots
"""New P3 F2; contrast methods adapted from historical P2, not a rerun of P2."""
import argparse,ctypes,hashlib,json,os,subprocess,sys
from pathlib import Path
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
assert not os.environ.get('OPENBLAS_CORETYPE')
import numpy as np
from threadpoolctl import threadpool_info

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def control(root, output):
    sys.path[:0]=[str(root/'science/herramientas'),str(root/'candidate')]
    from p3_backend import MixedP3 as Mixed, MixedP3Gauss as MixedGauss, lap_mixed_p3 as lap_mixed
    import observador_causal_CP12 as obs
    from modelo_m2 import BENCHMARK as model
    runtime=output/'runtime';runtime.mkdir()
    source=root/'science/herramientas/referencia_pasiva_CP12.c';target=runtime/'reference.so'
    subprocess.run(['cc','-O3','-fPIC','-shared','-fno-fast-math',str(source),'-lquadmath','-o',str(target)],check=True,capture_output=True)
    lib=ctypes.CDLL(str(target.resolve()));wide=np.ctypeslib.ndpointer(dtype=np.longdouble,flags='C_CONTIGUOUS')
    lib.cp12_identity.argtypes=[ctypes.c_size_t,wide,wide,wide,wide,ctypes.c_double,ctypes.c_double,ctypes.c_double];lib.cp12_identity.restype=None
    lib.cp12_quad_epsilon.restype=ctypes.c_double
    rng=np.random.default_rng(20261018001);sc=Mixed(.125,220.,4);sf=Mixed(.0625,220.,4)
    cs=[(q,v) for _,q,v in snapshots(root,.125)];fs=[(q,v) for _,q,v in snapshots(root,.0625)]
    S,_=obs.symmetry_basis(sf,fs[0][0]);rows=[];passed=True
    masses=np.array([model.mass2,model.mass2,model.mediator**2])[:,None,None]
    def scaled(error,*forces):return float(np.max(abs(error))/max(1.,sum(float(np.max(abs(x))) for x in forces)))
    for index,label in enumerate(('initial','original160','mixed80')):
        for trial in range(5):
            qc=cs[index][0].copy();qf=fs[index][0].copy()
            if trial:
                qc+=1e-5*rng.normal(size=qc.shape);qf+=1e-5*rng.normal(size=qf.shape)
            qi=obs.interpolate(sc,qc,sf);delta=qi-qf
            bare,coupled,jac=obs.terms(sc,sf,qc,qf)
            # Preserve original transfer/density/reaction/J, replace only the true P3 commutator.
            comm=obs.interpolate(sc,sc.lap(qc),sf)-sf.lap(qi)
            bare[1,0]=comm[2];coupled[1,:2]=comm[:2];coupled[2,2]=comm[2]
            jdelta=obs.apply_jac_numpy(sf,jac,delta[None])[0]
            lhs=obs.interpolate(sc,sc.force(qc),sf)-sf.force(qf)
            rhs=lap_mixed(sf,delta)-masses*delta+jdelta+coupled.sum(axis=0)
            force_scale=(obs.interpolate(sc,sc.force(qc),sf),sf.force(qf))
            defect=scaled(lhs-rhs,*force_scale)
            ni=obs.nonlinear(sf,qi@sf.Y);nf=obs.nonlinear(sf,qf@sf.Y)
            polynomial=scaled(ni-nf-jdelta,ni,nf)
            # Reference cancellation in the same polynomial, original float128 C source.
            xi=np.ascontiguousarray(qi.astype(np.longdouble)@sf.Y.astype(np.longdouble))
            xf=np.ascontiguousarray(qf.astype(np.longdouble)@sf.Y.astype(np.longdouble))
            exact=np.empty_like(xi);residual=np.empty_like(xi)
            lib.cp12_identity(sf.n*sf.Y.shape[1],xi,xf,exact,residual,model.quartic,model.trilinear,model.mixed)
            projected=residual@sf.YW.astype(np.longdouble)
            projected_exact=exact@sf.YW.astype(np.longdouble)
            extended=float(np.max(abs(projected))/max(np.longdouble('1e-30'),np.max(abs(projected_exact))))
            weights=np.array([2.,2.,1.])[:,None,None]*sf.w[None,:,None]
            x=rng.normal(size=qf.shape);y=rng.normal(size=qf.shape)
            jx=obs.apply_jac_numpy(sf,jac,x[None])[0];jy=obs.apply_jac_numpy(sf,jac,y[None])[0]
            l=float(np.sum(weights*x*jy));r=float(np.sum(weights*y*jx))
            symmetry=abs(l-r)/max(1.,abs(l),abs(r))
            # Bare identity must partition the same mixed chi difference independently.
            bare_rhs=lap_mixed(sf,delta)[2]-model.mediator**2*delta[2]+bare[:,0].sum(axis=0)
            bare_error=scaled(lhs[2]-bare_rhs,*force_scale)
            tests={'mixed_complete_defect':defect<=2e-12,'bare_source_partition':bare_error<=2e-12,
                   'polynomial_J_action':polynomial<=2e-12,'extended_polynomial_reference':extended<=2e-12,
                   'kinetic_weighted_J_symmetry':symmetry<=2e-12}
            row=dict(snapshot=label,perturbation=trial,tests=tests,mixed_defect_error=defect,
                     bare_partition_error=bare_error,polynomial_error=polynomial,
                     extended_reference_error=extended,weighted_symmetry_error=symmetry)
            if trial==0:
                leakage=obs.symmetry_residual(sf,S,qf);row['physical_D2_leakage']=leakage;tests['original_physical_D2_invariance']=leakage<=2e-12
            row['passed']=all(tests.values());rows.append(row);print(json.dumps(row),flush=True)
            if not row['passed']:passed=False;break
        if not passed:break
    unchanged=True # common wrapper independently checks all472 after return
    result=dict(schema='CP12_P3_PREFLIGHT_PHASE_B_DEFECT_ONLY',passed=passed and unchanged,rows=rows,
                input_files_unchanged=unchanged,float128_epsilon=lib.cp12_quad_epsilon(),M2_steps_executed=0,
                remaining_controls=['independent_canonical_sparse_matrix_and_symmetry','frozen_Gauss_7_6_reference_phase_and_balance'],
                all_registered_controls_passed=False,physical_evolution_authorized=False,correction_validated=False,CP12_closed=False)
    return result

if __name__=='__main__':raise SystemExit(run('F2',control))
