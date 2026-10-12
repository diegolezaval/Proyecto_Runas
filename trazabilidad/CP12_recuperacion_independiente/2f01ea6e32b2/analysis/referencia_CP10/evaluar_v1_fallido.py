"""Read immutable CP10 endpoint states; not a CP12 completion certificate."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')

def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--home',type=Path,required=True);ap.add_argument('--prereg-commit',required=True);args=ap.parse_args()
    assert len(args.prereg_commit)==40
    home=args.home.resolve();root=home/'science';folder=Path(__file__).parent;out=folder/'resultados.json';assert not out.exists()
    identity=read(home/'preregistration/identidad_cientifica.json');cfg=identity['case']['configuration']
    assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    paths=[root/n for n in cfg['reference_states']]
    assert all(sha(p)==identity['input_hashes'][p.relative_to(root).as_posix()] for p in paths)
    sys.path.insert(0,str(root/'herramientas'))
    import numpy as np
    from threadpoolctl import threadpool_limits
    from continuar_no_radial_m2 import Evolution
    from observador_causal_CP12 import chi_inner,interpolate,terms,model
    from diagnosticar_chi_CP11 import frozen_equilibrium
    source=home/'analysis/sources/interpretar_presupuesto_CP12_original.py';spec=importlib.util.spec_from_file_location('original_endpoint_metrics',source);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    saved=[]
    for p in paths:
        with np.load(p,allow_pickle=False) as z:saved.append({k:z[k].copy() for k in z.files})
    sc,sf=[Evolution(c['dx'],c['radius'],c['L']) for c in cfg['physical_configurations']]
    cp11=list((root/'validacion/P06/no_radial/CP11').glob('respuesta_forzada_precisa__*/procedencia.json'));assert len(cp11)==1
    dc=read(cp11[0])['identity']['case']['configuration'];assert dc['elliptic_relative_tolerance']==2e-10 and dc['algebra_relative_tolerance']==2e-12
    scale=chi_inner(sf,saved[1]['initial_q'][2],saved[1]['initial_v'][2],saved[1]['initial_q'][2],saved[1]['initial_v'][2])
    records=[]
    for t,qn,vn in [(0,'initial_q','initial_v'),(160,'q','v')]:
        fields=[(z[qn],z[vn]) for z in saved];refs=[];audits=[]
        with threadpool_limits(limits=1):
            for sim,(q,v) in zip([sc,sf],fields):
                eq,veq,unused,audit=frozen_equilibrium({},sim,q,v,dc);refs.append((eq,veq));audits.append(audit)
        dq=interpolate(sc,fields[0][0],sf)-fields[1][0];dv=interpolate(sc,fields[0][1],sf)-fields[1][1]
        dr=interpolate(sc,refs[0][0],sf)-refs[1][0];vr=interpolate(sc,refs[0][1],sf)-refs[1][1]
        q=np.array([dq[2],dr,dq[2]-dr]);v=np.array([dv[2],vr,dv[2]-vr])
        gram=np.array([[chi_inner(sf,a,b,c,d) for c,d in zip(q,v)] for a,b in zip(q,v)])
        fine=[]
        for name,a,b in [('physical',fields[1][0][2],fields[1][1][2]),('instantaneous_reference',*refs[1]),('nonstationary_residue',fields[1][0][2]-refs[1][0],fields[1][1][2]-refs[1][1])]:
            power=sf.w*np.sum((a[:,sf.ell>0]**2+b[:,sf.ell>0]**2/model.mediator**2),axis=1)
            use=sf.r<40;total=float(power[use].sum())
            fine.append(dict(component=name,relative_phase_norm=float(np.sqrt(total/scale)),core_weighted_mean_radius=float(np.dot(sf.r[use],power[use])/max(total,1e-300))))
        with threadpool_limits(limits=1):bare,coupled,J,algebra=terms(sc,sf,fields[0][0],fields[1][0])
        comm=bare[1,0];power=sf.w*np.sum(comm[:,sf.ell>0]**2,axis=1);use=sf.r<40;total=float(power[use].sum())
        records.append(dict(time=t,CP10_inputs=True,elliptic_audits=audits,observed_chi_core_phase_relative_error=float(np.sqrt(max(0,gram[0,0])/scale)),reference_difference_metrics=reader.metrics(gram,[1],scale),nonstationary_difference_metrics=reader.metrics(gram,[2],scale),cross_gram=gram.tolist(),fine_field_decomposition=fine,instantaneous_operator_chi_core_squared_norm=total,instantaneous_operator_chi_fraction_r_lt_half=float(power[sf.r<.5].sum()/max(total,1e-300)),force_identity_audit=algebra))
    assert all(sha(p)==identity['input_hashes'][p.relative_to(root).as_posix()] for p in paths)
    assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    meta=read(home/'preregistration/nueva_identidad.json')
    result=dict(schema='CP12_PASSIVE_ORIGINAL_CP10_ENDPOINT_REFERENCE',execution_uuid=meta['execution_uuid'],execution_run_id=meta['execution_run_id'],preregistration_git_commit=args.prereg_commit,preregistration_sha256=sha(folder/'PRERREGISTRO.md'),source_sha256=sha(Path(__file__)),CP10_input_hashes={p.relative_to(root).as_posix():sha(p) for p in paths},original_CP11_configuration=dc,original_phase_scale=scale,records=records,M2_steps=0,CP12_evolution_to_160_certified_by_this_diagnostic=False,final_causal_budget_evaluated=False,physical_gate_evaluated=False,physical_state_changed=False,nonstationary_residue_proved_free_wave=False,CP12_closed=False)
    temp=out.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');temp.replace(out)
    print(json.dumps({'M2_steps':0,'CP10_endpoints':[{'time':r['time'],'observed_error':r['observed_chi_core_phase_relative_error'],'stationary_projection':r['reference_difference_metrics']['signed_projection'],'nonstationary_removal':r['nonstationary_difference_metrics']['removal_squared_reduction'],'fine_components':r['fine_field_decomposition'],'instantaneous_source_center_fraction':r['instantaneous_operator_chi_fraction_r_lt_half']} for r in records],'CP12_closed':False}))

if __name__=='__main__':main()
