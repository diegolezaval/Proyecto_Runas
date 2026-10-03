"""Diagnóstico conservativo y de asentamiento de los estados ya calculados.

El ajuste estacionario iguala la carga medida; no modifica ni reinicia la PDE.
Se conserva el diagnóstico PCHIP original, aunque su carga no coincidiera.
"""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicHermiteSpline, PchipInterpolator
from scipy.optimize import brentq
from modelo_m2 import BENCHMARK as model
from soluciones_m2 import solve_state,measures
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/preparacion'

def diagnose(path):
    raw=json.loads(path.read_text());c=raw['configuration'];tag=path.stem
    out=O/f'{tag}_diagnostico.json'
    if out.exists():return json.loads(out.read_text())
    a=np.loadtxt(O/f'{tag}_tiempo.csv',delimiter=',',skiprows=1);sel=a[:,0]>=.8*c['tmax'];Q=float(np.mean(a[sel,4]));Ec=float(np.mean(a[sel,3]))
    branch=json.loads((R/'validacion/P06/rama/resultados.json').read_text())['rows'];stable=sorted([b for b in branch if b['omega']<=.98],key=lambda b:b['Q'])
    ws=float(PchipInterpolator([b['Q'] for b in stable],[b['omega'] for b in stable],extrapolate=False)(Q))
    nearest=min(stable,key=lambda b:abs(b['omega']-ws))
    profile=np.loadtxt(R/f"validacion/P06/rama/perfil_w{nearest['omega']:.5f}.csv",delimiter=',',skiprows=1)
    f=CubicHermiteSpline(profile[:,0],profile[:,1],profile[:,2]);z=CubicHermiteSpline(profile[:,0],profile[:,3],profile[:,4])
    bg=solve_state(omega=nearest['omega'],previous=lambda x:np.array([f(x),f(x,1),z(x),z(x,1)]),n=1800)
    for w in np.linspace(nearest['omega'],ws,int(np.ceil(abs(ws-nearest['omega'])/.0002))+1)[1:]:bg=solve_state(omega=float(w),previous=bg,n=1800)
    cache={}
    def residual(w):
        s=solve_state(omega=w,previous=bg,n=2000,tol=5e-10);m=measures(s,w);cache[w]=(s,m)
        return m['Q']-Q
    root=float(brentq(residual,ws-.0003,ws+.0003,xtol=2e-12));residual(root);eq,mm=cache[root]
    with np.load(O/f'{tag}_estado.npz',allow_pickle=False) as state:
        dx=c['dx'];near=int(round(30/dx));edges=np.arange(near+1)*dx;r=(edges[1:]+edges[:-1])/2;weight=np.diff(edges**3)/3
        ref=eq.sol(r)[0];den=np.dot(weight,ref*ref)
        errs=[float(np.sqrt(np.dot(weight,(q-ref)**2)/den)) for q in state['late']]
        n=c['n'];edgesall=np.arange(n+1)*dx;vol=np.diff(edgesall**3)/3;conduct=edgesall[1:-1]**2/dx
        phi=state['phi'];vel=state['vel'];chi=state['chi'];vchi=state['vchi']
        Eb=4*np.pi*np.dot(vol,abs(vel)**2+.5*vchi*vchi+model.potential(abs(phi),chi))
        Eg=4*np.pi*(np.dot(conduct,abs(np.diff(phi))**2+.5*np.diff(chi)**2)+2*c['radius']**2/dx*(abs(phi[-1])**2+.5*chi[-1]**2))
        Qend=8*np.pi*np.dot(vol,np.imag(np.conj(phi)*vel))
        np.savetxt(O/f'{tag}_perfil_referencia.csv',np.c_[r,ref,eq.sol(r)[2]],delimiter=',',header='r,f_equilibrio_Q_media,chi_equilibrio_Q_media',comments='')
    criteria=json.loads((R/'datos/ensayo_preparacion_4_2.json').read_text())['acceptance']
    settled=bool(max(errs)<criteria['max_late_profile_deviation_for_settling'] and raw['mean_late_charge_fraction']>=criteria['min_late_retained_charge_fraction'])
    result=dict(schema_version='1.0.0',run=tag,configuration=c,mean_late_core_charge=Q,mean_late_core_energy=Ec,
        equilibrium_omega=root,equilibrium_Q=mm['Q'],equilibrium_E=mm['E'],charge_matching_relative=abs(mm['Q']/Q-1),
        min_late_profile_deviation=min(errs),max_late_profile_deviation=max(errs),mean_late_charge_fraction=raw['mean_late_charge_fraction'],
        mean_core_energy_excess_over_matched_stationary=Ec-mm['E'],excess_is_not_demonstrated_extractable_energy=True,
        final_energy_recomputed=Eb+Eg,final_charge_recomputed=float(Qend),energy_accounting_relative=abs((Eb+Eg)/a[-1,1]-1),charge_accounting_relative=abs(Qend/a[-1,2]-1),
        relative_energy_drift=raw['relative_energy_drift'],relative_charge_drift=raw['relative_charge_drift'],balance_passed=raw['balance_passed'],
        radial_settling_criteria_passed=settled,complete_preparation=False,
        scope='Paquete cargado preexistente; datos radiales finitos. Sin fuente primaria, prueba 3D, apagado, receptor ni ciclo.')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(tag,'perfil',max(errs),'Q/Q0',raw['mean_late_charge_fraction'],'asentamiento',settled,flush=True)
    return result

def run():
    records=[]
    for p in sorted(O.glob('w*.json')):
        if any(p.stem.endswith(x) for x in ['_diagnostico','_progreso','_transferencia']):continue
        records.append(diagnose(p))
    def get(w,h,dt,T):return next(r for r in records if r['configuration']['width']==w and r['configuration']['dx']==h and r['configuration']['dt']==dt and r['configuration']['tmax']==T)
    comparisons=[]
    for label,left,right in [('tiempo',(8,.2,.004,240),(8,.2,.002,240)),('espacio',(8,.2,.002,240),(8,.1,.002,240)),('larga',(7.2,.2,.004,1200),(7.2,.1,.002,1200))]:
        try:a,b=get(*left),get(*right)
        except StopIteration:continue
        keys=['mean_late_core_charge','mean_late_core_energy']
        diffs={k:abs(a[k]/b[k]-1) for k in keys}
        comparisons.append(dict(type=label,left=a['run'],right=b['run'],relative_differences=diffs,
            energy_drift_reduction=a['relative_energy_drift']/b['relative_energy_drift'],
            passed=max(diffs.values())<.02))
    ok=all(x['balance_passed'] and max(x['energy_accounting_relative'],x['charge_accounting_relative'],x['charge_matching_relative'])<1e-7 for x in records) and all(x['passed'] for x in comparisons)
    report=dict(schema_version='1.0.0',records=records,convergence=comparisons,numerical_verification_passed=ok,
        complete_E04=False,complete_RES1=False,primary_source_derived=False,full_3D_stability=False,
        settling_pass_does_not_close_stage=True)
    (O/'resultados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('Numerical verification:',ok,flush=True)
    if not ok:raise SystemExit(1)

if __name__=='__main__':run()
