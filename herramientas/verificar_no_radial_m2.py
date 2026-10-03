"""Decisions from saved continuations only; no evolution is repeated."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.interpolate import CubicSpline
from modelo_m2 import BENCHMARK as model
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/no_radial'
cfg=json.loads((R/'datos/ensayo_no_radial_CP06.json').read_text())
cases=cfg['configuration_cases']+[x['configuration'] for x in cfg.get('adaptive_extensions',[])]+cfg.get('mediator_refinement',{}).get('cases',[])

def tag(c):
    prefix=c.get('scheme','')
    return (prefix+'_' if prefix else '')+f"L{c['L']}_h{c['dx']:.3f}_dt{c['dt']:.4f}_R{c['radius']:.0f}_eps{c['eps']:.3f}_T160"

records={};series={};pending=[];issues=[]
sourcehash=hashlib.sha256((R/cfg['source']).read_bytes()).hexdigest()
for c in cases:
    name=tag(c);rp=O/f'{name}.json';sp=O/f'{name}_estado.npz'
    if not rp.exists():pending.append(name);continue
    rec=json.loads(rp.read_text());assert all(rec['configuration'][k]==v for k,v in c.items())
    with np.load(sp,allow_pickle=False) as d:
        actual_time=float(d['time']) if rec['configuration'].get('adaptive') else int(d['step'])*c['dt']
        assert actual_time==160 and json.loads(str(d['config']))==rec['configuration']
        assert np.isfinite(d['q']).all() and np.isfinite(d['v']).all()
        assert json.loads(str(d['transfer']))['source_sha256']==sourcehash
        a=d['rows'];series[name]=a
    assert a[0,0]==0 and a[-1,0]==160 and np.all(np.diff(a[:,0])>0)
    assert json.loads((O/f'{name}_progreso.json').read_text())['status']=='CALCULO_TERMINADO'
    records[name]=rec
    for key in ['balance_passed','bounded_window_passed']:
        if not rec[key]:issues.append(name+':'+key)
    if rec['relative_core_charge_change']>cfg['criteria']['core_charge_change_max']:issues.append(name+':core_charge')

def compare(name,left,right,threshold):
    if left not in series or right not in series:return None
    a,b=series[left],series[right];assert np.allclose(a[:,0],b[:,0],rtol=0,atol=1e-12)
    metric=float(np.max(abs(a[:,5]-b[:,5]))/max(b[:,5]))
    return dict(control=name,left=left,right=right,norm_relative_sup_error=metric,threshold=threshold,passed=metric<threshold,
        core_energy_relative_sup_error=float(max(abs(a[:,3]/b[:,3]-1))),core_charge_relative_sup_error=float(max(abs(a[:,4]/b[:,4]-1))))

def final_field_compare(left,right):
    # Independent diagnostic sensitive to complex modal fields, rather than
    # comparing only their norms. Align only the global U(1) phase.
    ds=[]
    for name in [left,right]:
        with np.load(O/f'{name}_estado.npz') as d:
            ds.append((d['q'],d['v'],d['initial_q'],d['initial_v'],json.loads(str(d['config']))))
    qc,vc,ic,ivc,cc=ds[0];qf,vf,if_,ivf,cf=ds[1]
    rc=(np.arange(qc.shape[1])+.5)*cc['dx'];rf=(np.arange(qf.shape[1])+.5)*cf['dx']
    use=rf<40;rr=rf[use];ef=np.arange(len(rf)+1)*cf['dx'];w=(np.diff(ef**3)/3)[use]
    nm=max(qc.shape[2],qf.shape[2]);out=[]
    for q,r in [(qc,rc),(qf,rf),(vc,rc),(vf,rf)]:
        x=np.zeros((3,len(rr),nm));vals=CubicSpline(r,q,axis=1,extrapolate=True)(rr)
        x[:,:,:q.shape[2]]=vals;out.append(x)
    ac,af,bc,bf=out;pc=ac[0]+1j*ac[1];pf=af[0]+1j*af[1]
    phase=np.angle(np.sum(w*np.conj(pf[:,0])*pc[:,0]));pc*=np.exp(-1j*phase)
    initial=if_[0,use]+1j*if_[1,use]
    scale=float(np.sum(w[:,None]*abs(initial[:,1:])**2))
    pvc=(bc[0]+1j*bc[1])*np.exp(-1j*phase);pvf=bf[0]+1j*bf[1]
    initialv=ivf[0,use]+1j*ivf[1,use]
    pspace=float(np.sqrt(np.sum(w[:,None]*(abs(pc[:,1:]-pf[:,1:])**2+abs(pvc[:,1:]-pvf[:,1:])**2/model.mass2))/
        np.sum(w[:,None]*(abs(initial[:,1:])**2+abs(initialv[:,1:])**2/model.mass2))))
    zspace=float(np.sqrt(np.sum(w[:,None]*((ac[2,:,1:]-af[2,:,1:])**2+(bc[2,:,1:]-bf[2,:,1:])**2/model.mediator**2))/
        np.sum(w[:,None]*(if_[2,use,1:]**2+ivf[2,use,1:]**2/model.mediator**2))))
    return dict(global_phase_removed=float(phase),
        final_complex_nonradial_field_error_over_initial_norm=float(np.sqrt(np.sum(w[:,None]*abs(pc[:,1:]-pf[:,1:])**2)/scale)),
        final_mediator_nonradial_error_over_initial_norm=float(np.sqrt(np.sum(w[:,None]*(ac[2,:,1:]-af[2,:,1:])**2)/np.sum(w[:,None]*if_[2,use,1:]**2))),
        final_phi_phase_space_error_over_initial_norm=pspace,final_mediator_phase_space_error_over_initial_norm=zspace,
        interpretation='Additional final-field diagnostic; not the preregistered temporal norm gate')

names=[tag(c) for c in cases]
comparisons=[]
for args in [('angular_L2_L4',names[0],names[1],.05),('radial_L4',names[1],names[2],.02),
             ('temporal_L4',names[1],names[3],.02),('angular_L4_L6',names[1],names[7],.05)]+(
             [('temporal_mediador',names[8],names[9],.02),('radial_mediador_grueso',names[9],names[10],.02)] if len(names)>8 else [])+(
             [('radial_mediador_refinado',names[10],names[11],.02)] if len(names)>11 else []):
    x=compare(*args)
    if x:
        x.update(final_field_compare(args[1],args[2]))
        x['norm_gate_passed']=x['passed']
        x['phi_field_gate_passed']=max(x['final_complex_nonradial_field_error_over_initial_norm'],x['final_phi_phase_space_error_over_initial_norm'])<x['threshold']
        x['mediator_field_gate_required']='mediador' in x['control'] or 'angular' in x['control']
        x['mediator_field_gate_passed']=max(x['final_mediator_nonradial_error_over_initial_norm'],x['final_mediator_phase_space_error_over_initial_norm'])<x['threshold']
        x['passed']=x['norm_gate_passed'] and x['phi_field_gate_passed'] and (not x['mediator_field_gate_required'] or x['mediator_field_gate_passed'])
        comparisons.append(x)
box=None
if names[0] in series and names[6] in series:
    a,b=series[names[0]],series[names[6]]
    box=dict(core_energy_relative_sup_error=float(max(abs(a[:,3]/b[:,3]-1))),
             core_charge_relative_sup_error=float(max(abs(a[:,4]/b[:,4]-1))),norm_absolute_sup_error=float(max(abs(a[:,5]-b[:,5]))))
    box['passed']=bool(max(box.values())<cfg['criteria']['box_core_relative_change_max'])
amplitude=None
if names[1] in series and names[4] in series:
    a,b=series[names[1]],series[names[4]]
    amplitude=dict(relative_departure_from_linear_amplitude_scaling=float(max(abs(a[:,5]-2*b[:,5]))/max(a[:,5])),
        interpretation='Finite-amplitude comparison, not a proof of an open basin or linear response at all epsilon')
if not pending:
    rejected_controls=['angular_L2_L4']+(['radial_mediador_grueso'] if len(names)>11 else [])
    accepted=[x for x in comparisons if x['control'] not in rejected_controls]
    gate=not issues and all(x['passed'] for x in accepted) and box['passed']
    for x in accepted:
        # A small norm error can hide a modal direction/phase error. Such a
        # discrepancy is kept as a distinct pending verification if it occurs.
        if x['final_complex_nonradial_field_error_over_initial_norm']>x['threshold']:
            issues.append(x['control']+':final_complex_field');gate=False
        if 'mediador' in x['control'] and x['final_mediator_nonradial_error_over_initial_norm']>x['threshold']:
            issues.append(x['control']+':final_mediator_field');gate=False
        if 'mediador' in x['control'] and max(x['final_phi_phase_space_error_over_initial_norm'],x['final_mediator_phase_space_error_over_initial_norm'])>x['threshold']:
            issues.append(x['control']+':final_phase_space');gate=False
    status='SUBENSAYO_FINITO_SUPERADO' if gate else 'REFINAMIENTO_PENDIENTE'
else:gate=False;status='EN_PROGRESO'
result=dict(status=status,configuration=str((R/'datos/ensayo_no_radial_CP06.json').relative_to(R)),records=records,
    pending=pending,issues=issues,comparisons=comparisons,box_control=box,amplitude_comparison=amplitude,
    finite_campaign_passed=gate,original_L2_convergence_failure_preserved=True,
    complete_E03=False,complete_E04=False,complete_RES0=False,complete_RES1=False,
    nonlinear_orbital_stability_proven=False,arbitrary_nonradial_perturbations_tested=False,
    scope='CP04 quadrupole deformation epsilon 0.01 and 0.02, tau<=160, declared grids and full m through finite L; only conditional subexperiment')
dest=O/('resultados_parciales.json' if pending else 'resultados.json');dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False,indent=2))
