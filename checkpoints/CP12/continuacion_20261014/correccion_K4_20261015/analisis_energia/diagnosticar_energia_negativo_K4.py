"""Passive energy/work identities on the authenticated failed K4 snapshot.

No time integrator is imported or executed. This decomposition does not predict
that a different numerical correction will pass a physical gate.
"""
from pathlib import Path
import argparse, hashlib, io, json, sys, zipfile

def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,x):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--sha256',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    archive=a.archive.resolve();out=a.output.resolve();assert not out.exists();assert sha(archive)==a.sha256;out.mkdir()
    write(out/'PREREGISTRO.json',{'operation':'Passive exact quadratic-form gap and work identities at initial and failed saved states','M2_steps':0,'input_negative_archive_sha256':a.sha256,'identities':['E_FV(t)-E_FV(0)=E_K4(t)-E_K4(0)-(G(t)-G(0))','G=sum_fields canonical_energy_weight*(regular_K2_energy-original_FV_gradient_energy+fixed_h2_over12_composition_energy)','instantaneous_dE_FV_dt=sum_fields canonical_equation_weight*W*v*(L_K4-L_FV)q'],'split_fields':['RePhi','ImPhi','chi'],'split_action':['regularization','fixed_positive_composition'],'radii':[0,.25,1,2,5,10,20,40,220],'algebra_relative_tolerance':2e-12,'acceptance_gate_changed':False,'new_correction_validated':False,'CP12_closed':False})
    with zipfile.ZipFile(archive) as z:
        manifest=json.loads(z.read('MANIFIESTO_NEGATIVO.json'));assert manifest['scientific_gate_failed']
        selected={n:v for n,v in manifest['files'].items() if n.startswith('science/') or n in ('candidate/operador.py','negative/segment_0008/FAILURE.json','negative/segment_0008/failed_physical_and_observer_state.npz','outputs/K4_par_estado.npz','preregistration/identidad_cientifica_original.json')}
        for n,v in selected.items():
            p=Path(n);assert not p.is_absolute() and '..' not in p.parts;data=z.read(n);assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
            target=out/'inputs'/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o444)
    source=out/'inputs';sys.path.insert(0,str(source/'science/herramientas'));sys.path.insert(0,str(source/'candidate'))
    import numpy as np
    from threadpoolctl import threadpool_info
    from continuar_no_radial_m2 import Evolution
    from operador import Candidate
    assert threadpool_info() and all(p['num_threads']==1 and p['architecture']=='SkylakeX' for p in threadpool_info())
    failed=read(source/'negative/segment_0008/FAILURE.json');identity=read(source/'preregistration/identidad_cientifica_original.json')
    assert all(sha(source/'science'/n)==h for n,h in {**identity['code_hashes'],**identity['input_hashes']}.items())
    with np.load(source/'negative/segment_0008/failed_physical_and_observer_state.npz',allow_pickle=False) as z:data={k:z[k].copy() for k in z.files}
    with np.load(source/'outputs/K4_par_estado.npz',allow_pickle=False) as z:initial={k:z[k].copy() for k in z.files}
    assert float(initial['time'])==0
    cfg=json.loads(str(initial['config']));reports=[];field_names=['RePhi','ImPhi','chi'];energy_weights=np.array([1.,1.,.5]);equation_weights=2*energy_weights
    def gradient_parts(sim,q):
        dq=np.diff(q,axis=1);u=q/sim.powers[None];du=np.diff(u,axis=1);second=sim.lap2(q)
        old_faces=sim.c[None,:]*np.sum(dq*dq,axis=2)
        regular_faces=np.sum(sim.conductance_u[None]*du*du,axis=2)
        old_cells=sim.dx*np.sum(sim.angular[None,None,:]*q*q,axis=2)
        regular_cells=np.zeros_like(old_cells)
        for cells,faces in [(old_cells,old_faces),(regular_cells,regular_faces)]:cells[:,:-1]+=.5*faces;cells[:,1:]+=.5*faces
        old_cells[:,-1]+=2*sim.radius**2/sim.dx*np.sum(q[:,-1]**2,axis=1)
        regular_cells[:,-1]+=np.sum(sim.boundary_u[None]*u[:,-1]**2,axis=1)
        composition=sim.dx**2/12*sim.w[None]*np.sum(second*second,axis=2)
        return (regular_cells-old_cells)*energy_weights[:,None],composition*energy_weights[:,None]
    for i,c in enumerate(cfg['physical_configurations']):
        sim=Candidate(c['dx'],c['radius'],c['L']);original=Evolution(c['dx'],c['radius'],c['L'])
        q0,v0=data[f'grid_{i}_initial_q'],data[f'grid_{i}_initial_v'];q,v=data[f'grid_{i}_q'],data[f'grid_{i}_v'];t=failed['metadata'][i]['t']
        n=int(initial['coarse_n']);use=slice(0,n) if i==0 else slice(n,None)
        assert np.array_equal(q0,initial['initial_q'][:,use]) and np.array_equal(v0,initial['initial_v'][:,use])
        eo0=original.measure(0,q0,v0)[1];eo=original.measure(t,q,v)[1];ek0=sim.measure(0,q0,v0)[1];ek=sim.measure(t,q,v)[1]
        r0,c0=gradient_parts(sim,q0);r1,c1=gradient_parts(sim,q)
        reg_delta=np.sum(r1-r0,axis=1);composition_delta=np.sum(c1-c0,axis=1);gap_delta=reg_delta+composition_delta
        energy_identity=(eo-eo0)-((ek-ek0)-float(gap_delta.sum()))
        scale=max(1.,abs(eo0),abs(ek0),abs(eo),abs(ek));residual=abs(energy_identity)/scale
        gap_form_residual=max(abs((ek0-eo0)-float((r0+c0).sum())),abs((ek-eo)-float((r1+c1).sum())))/scale
        times=[]
        for label,qq,vv in [('initial',q0,v0),('failed',q,v)]:
            difference=sim.lap(qq)-original.lap(qq)
            density=equation_weights[:,None]*sim.w[None]*np.sum(vv*difference,axis=2)
            u=qq/sim.powers[None];uv=vv/sim.powers[None]
            independent=2*energy_weights*(np.sum(sim.conductance_u[None]*np.diff(u,axis=1)*np.diff(uv,axis=1),axis=(1,2))+np.sum(sim.boundary_u[None]*u[:,-1]*uv[:,-1],axis=1)+sim.dx**2/12*np.sum(sim.w[None,:,None]*sim.lap2(qq)*sim.lap2(vv),axis=(1,2))-np.sum(sim.c[None,:,None]*np.diff(qq,axis=1)*np.diff(vv,axis=1),axis=(1,2))-sim.dx*np.sum(sim.angular[None,None,:]*qq*vv,axis=(1,2))-2*sim.radius**2/sim.dx*np.sum(qq[:,-1]*vv[:,-1],axis=1))
            power=density.sum(axis=1);variation_residual=float(np.max(abs(independent+power))/max(1.,float(np.sum(abs(independent))+np.sum(abs(power)))))
            bins=[]
            for lo,hi in zip([0,.25,1,2,5,10,20,40],[.25,1,2,5,10,20,40,220]):
                sel=(sim.r>=lo)&(sim.r<hi);bins.append({'r_min':lo,'r_max':hi,'work_by_field_over_initial_FV_energy':(density[:,sel].sum(axis=1)/eo0).tolist()})
            times.append({'snapshot':label,'instantaneous_work_by_field':dict(zip(field_names,power.tolist())),'work_by_field_over_initial_FV_energy':dict(zip(field_names,(power/eo0).tolist())),'independent_quadratic_directional_derivative_residual':variation_residual,'radial_bins':bins})
        field_change=-gap_delta/eo0
        report={'dx':c['dx'],'physical_failed_time':t,'initial_FV_energy':eo0,'initial_K4_energy':ek0,'failed_FV_energy':eo,'failed_K4_energy':ek,'signed_FV_energy_change_over_initial':(eo-eo0)/eo0,'signed_K4_energy_change_over_initial':(ek-ek0)/ek0,'regularization_gap_change_over_initial_FV_energy':dict(zip(field_names,(reg_delta/eo0).tolist())),'composition_gap_change_over_initial_FV_energy':dict(zip(field_names,(composition_delta/eo0).tolist())),'minus_gap_change_by_field_over_initial_FV_energy':dict(zip(field_names,field_change.tolist())),'Phi_minus_gap_change_over_initial_FV_energy':float(field_change[:2].sum()),'chi_minus_gap_change_over_initial_FV_energy':float(field_change[2]),'consistent_energy_change_over_initial_FV_energy':(ek-ek0)/eo0,'energy_change_identity_relative_residual':residual,'independent_gradient_gap_relative_residual':gap_form_residual,'instantaneous_work':times,'all_algebra_checks_passed':bool(residual<=2e-12 and gap_form_residual<=2e-12 and all(x['independent_quadratic_directional_derivative_residual']<=2e-12 for x in times))}
        reports.append(report)
    result={'schema':'CP12_K4_FAILED_TRIAL_PASSIVE_ENERGY_FORM_AND_WORK_DIAGNOSIS','passed':all(r['all_algebra_checks_passed'] for r in reports),'M2_steps_executed':0,'input_negative_archive_sha256':a.sha256,'all_selected_input_hashes_verified':True,'input_files_verified':len(selected),'grids':reports,'field_contributions_describe_energy_form_difference_on_measured_states':True,'counterfactual_new_evolution_tested':False,'new_correction_validated':False,'criteria_changed':False,'CP12_closed':False}
    write(out/'RESULTADO.json',result)
    print(json.dumps({'passed':result['passed'],'grids':[{k:r[k] for k in ('dx','physical_failed_time','signed_FV_energy_change_over_initial','Phi_minus_gap_change_over_initial_FV_energy','chi_minus_gap_change_over_initial_FV_energy','energy_change_identity_relative_residual')} for r in reports],'M2_steps':0,'new_correction_validated':False},ensure_ascii=False))
if __name__=='__main__':main()
