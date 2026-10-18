from controls_common import run, snapshots
"""New P3 F1; contrast methods adapted from historical P2, not a rerun of P2."""
import argparse,hashlib,json,os,sys
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
    from continuar_no_radial_m2 import Evolution
    from operador import Candidate
    import acelerar_fuerza_m2 as fused
    fused.OUT=output/'runtime';fused.OUT.mkdir()
    rng=np.random.default_rng(20261018001);rows=[];passed=True
    for dx in (.125,.0625):
        sim=Mixed(dx,220.,4)
        cases=snapshots(root,dx)
        for label,q,v in cases:
            fv=Evolution.lap(sim,q);p3=Candidate.lap(sim,q)+sim.dx**4/90*sim.lap2(sim.lap2(sim.lap2(q)));mixed=sim.lap(q)
            tests={'Phi_lap_array_equal_FV':bool(np.array_equal(mixed[:2],fv[:2])),
                   'chi_lap_array_equal_P3':bool(np.array_equal(mixed[2],p3[2])),
                   'passive_lap_array_equal_physical':bool(np.array_equal(lap_mixed(sim,q),mixed))}
            force=sim.force(q)
            direction=rng.normal(size=q.shape)
            def energy(q):
                b,f,ang,bd,_=sim.components(q,v)
                return b.sum()+f.sum()+ang.sum()+bd
            deriv=float(energy(q.astype(complex)+1e-30j*direction).imag/1e-30)
            exact=float(-np.sum(np.array([2,2,1])[:,None,None]*sim.w[None,:,None]*force*direction))
            gradient=abs(deriv-exact)/max(1.,abs(deriv),abs(exact))
            tests['mixed_variational_gradient']=gradient<=2e-12
            charge=2*np.sum(sim.w[:,None]*(q[0]*force[1]-q[1]*force[0]))
            charge_scale=max(1.,2*np.sum(sim.w[:,None]*(abs(q[0]*force[1])+abs(q[1]*force[0]))))
            charge_error=float(abs(charge)/charge_scale);tests['U1_acceleration']=charge_error<=2e-12
            bf,ff,af,bdf,_=Evolution.components(sim,q,v)
            efv=bf.sum()+ff.sum()+af.sum()+bdf
            delta_lap=p3[2]-fv[2]
            gap=-.5*np.sum(sim.w[:,None]*q[2]*delta_lap)
            energy_gap_error=float(abs(energy(q)-efv-gap)/max(1.,abs(energy(q)),abs(efv)))
            tests['energy_gap_identity']=energy_gap_error<=2e-12
            # Independent directional derivative in the original FV energy.
            complex_q=q.astype(complex)+1e-30j*v
            b,f,ang,bd,_=Evolution.components(sim,complex_q,v)
            potential_gradient_along_v=float((b.sum()+f.sum()+ang.sum()+bd).imag/1e-30)
            kinetic_derivative=float(np.sum(np.array([2,2,1])[:,None,None]*sim.w[None,:,None]*v*force))
            measured_work=potential_gradient_along_v+kinetic_derivative
            expected_work=float(np.sum(sim.w[:,None]*v[2]*delta_lap))
            work_scale=max(1.,abs(potential_gradient_along_v)+abs(kinetic_derivative),abs(expected_work))
            work_error=abs(measured_work-expected_work)/work_scale
            tests['original_FV_work_identity']=work_error<=2e-12
            standard=sim.force;meta=fused.install(sim)
            errors=[]
            for i in range(5):
                trial=q if i==0 else q+1e-5*rng.normal(size=q.shape)
                x=standard(trial);y=sim.force(trial)
                errors.append(float(np.max(abs(x-y))/max(1.,float(np.max(abs(x))))))
            sim.force=standard
            tests['mixed_fused_C_vs_numpy']=max(errors)<=2e-12
            row=dict(dx=dx,snapshot=label,tests=tests,gradient_relative_error=gradient,
                     charge_relative_error=charge_error,energy_gap_relative_error=energy_gap_error,
                     work_relative_error=work_error,fused_C_relative_errors=errors,passed=all(tests.values()))
            rows.append(row);passed=passed and row['passed']
            print(json.dumps(row),flush=True)
            if not row['passed']:break
        if not passed:break
    result=dict(schema='CP12_P3_PREFLIGHT_PHASE_A_NOT_FULL_APPROVAL',passed=passed,
                M2_steps_executed=0,rows=rows,original_input_manifest_files_verified=472,
                remaining_controls=['complete_defect_and_extended_identity','mixed_sparse_matrix_and_symmetry','frozen_Gauss_7_6_reference_phase_and_balance'],
                all_registered_controls_passed=False,physical_evolution_authorized=False,correction_validated=False,CP12_closed=False)
    return result

if __name__=='__main__':raise SystemExit(run('F1',control))
