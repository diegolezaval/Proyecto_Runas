"""Phase A of registered mixed preflight: no DOP853, no physical steps."""
import argparse,hashlib,json,os,sys
from pathlib import Path
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
assert not os.environ.get('OPENBLAS_CORETYPE')
import numpy as np
from threadpoolctl import threadpool_info

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists();a.output.mkdir(parents=True)
    root=a.inputs.resolve();m=json.loads((root/'MANIFIESTO_NEGATIVO.json').read_text())
    for n,v in m['files'].items():assert (root/n).stat().st_size==v['bytes'] and sha(root/n)==v['sha256'],n
    sys.path[:0]=[str(root/'science/herramientas'),str(root/'candidate')]
    from continuar_no_radial_m2 import Evolution
    from operador import Candidate
    from mixed_backend import Mixed,lap_mixed
    import acelerar_fuerza_m2 as fused
    pools=threadpool_info();assert pools and all(x['num_threads']==1 and x.get('architecture')=='SkylakeX' for x in pools)
    fused.OUT=a.output.resolve()/'runtime';fused.OUT.mkdir()
    rng=np.random.default_rng(20261015001);rows=[];passed=True
    for dx in (.125,.0625):
        sim=Mixed(dx,220.,4)
        matches=list((root/'science/validacion/P06/no_radial/CP10').glob(('temporal_h0125__*' if dx==.125 else 'espacial_h00625__*')+'/*_estado.npz'))
        assert len(matches)==1
        with np.load(matches[0],allow_pickle=False) as z:
            snapshots=[('initial',z['initial_q'].copy(),z['initial_v'].copy()),('final',z['q'].copy(),z['v'].copy())]
        for label,q,v in snapshots:
            fv=Evolution.lap(sim,q);k4=Candidate.lap(sim,q);mixed=sim.lap(q)
            tests={'Phi_lap_array_equal_FV':bool(np.array_equal(mixed[:2],fv[:2])),
                   'chi_lap_array_equal_K4':bool(np.array_equal(mixed[2],k4[2])),
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
            delta_lap=k4[2]-fv[2]
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
    result=dict(schema='CP12_MIXED_PREFLIGHT_PHASE_A_NOT_FULL_APPROVAL',passed=passed,
                M2_steps_executed=0,rows=rows,original_input_manifest_files_verified=len(m['files']),
                remaining_controls=['complete_defect_and_extended_identity','mixed_sparse_matrix_and_symmetry','frozen_Gauss_7_6_reference_phase_and_balance'],
                all_registered_controls_passed=False,physical_evolution_authorized=False,correction_validated=False,CP12_closed=False)
    (a.output/'RESULTADO.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
