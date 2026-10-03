"""E02: sensibilidad fundamental independiente y carta capilar muestreada."""
from pathlib import Path
import json, sys
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.special import iv
from modelo_m2 import BENCHMARK as model
from soluciones_m2 import solve_state, measures
from capilaridad_m2 import spectrum, extrapolate
R=Path(__file__).resolve().parents[1];O=R/'validacion/validez';O.mkdir(parents=True,exist_ok=True)

class Tabulated:
    def __init__(self,path):
        a=np.loadtxt(path,delimiter=',',skiprows=1);self.x=a[:,0]
        self.f=CubicHermiteSpline(self.x,a[:,1],a[:,2]);self.z=CubicHermiteSpline(self.x,a[:,3],a[:,4])
    def sol(self,x):return np.array([self.f(x),self.f(x,1),self.z(x),self.z(x,1)])

def retry_mass_path(base,offset):
    """Alternative continuation path; final point varies M ALONE.

    First lower g to g/(1+offset); then vary (M,g) together with fixed g/M.
    Intermediate states are numerical continuation, not device-specific laws.
    """
    bg=base;g0=model.g/(1+offset)
    for gvalue in np.linspace(model.g,g0,25)[1:]:
        candidate=model.with_parameter('g',gvalue)
        bg=solve_state(previous=bg,model=candidate,n=2400,tol=1e-7)
    for part in np.linspace(0,offset,9)[1:]:
        candidate=model.with_parameter('M',model.M*(1+part)).with_parameter('g',g0*(1+part))
        bg=solve_state(previous=bg,model=candidate,n=2400,tol=1e-7)
    candidate=model.with_parameter('M',model.M*(1+offset))
    bg=solve_state(previous=bg,model=candidate,n=2400,tol=2e-9)
    return bg,candidate

def run():
    cfg=json.loads((R/'datos/campana_4_2.json').read_text());sensitivity=[];analytic=[]
    initial=Tabulated(R/'validacion/m2_perfil_convergente.csv')
    base=solve_state(previous=initial,tol=1e-9);baseline=measures(base,.9)
    for name in ('m','M','lambda0','g','h'):
        for offset in cfg['fundamental_sensitivity']['analytic_offsets']:
            candidate=model.with_parameter(name,getattr(model,name)*(1+offset))
            row=dict(parameter=name,relative_offset=offset,derived_lambda=candidate.derived_lambda)
            try:
                co=candidate.coexistence();row.update(co)
                row['classical_admissible_attraction']=bool(co['omega_squared']>0)
                row['necessary_localization_at_omega_09']=bool(0<co['omega_squared']<.81<candidate.mass2)
            except ValueError as exc:
                row.update(classical_admissible_attraction=False,necessary_localization_at_omega_09=False,reason=str(exc))
            analytic.append(row)
        for offset in cfg['fundamental_sensitivity']['relative_offsets']:
            candidate=model.with_parameter(name,getattr(model,name)*(1+offset));bg=base
            attempt=dict(parameter=name,relative_offset=offset)
            try:
                for part in np.linspace(0,offset,17)[1:]:
                    mid=model.with_parameter(name,getattr(model,name)*(1+part))
                    bg=solve_state(previous=bg,model=mid,n=2000,tol=1e-7)
                bg=solve_state(previous=bg,model=candidate,n=2400,tol=2e-9)
                data=measures(bg,.9,model=candidate)
                fine=solve_state(previous=bg,model=candidate,radius=75,n=1800,tol=5e-10)
                check=measures(fine,.9,model=candidate)
                attempt.update(result=data,refined=check,E_relative_error=abs(check['E']/data['E']-1),Q_relative_error=abs(check['Q']/data['Q']-1),
                               susceptibility_logQ=float(np.log(data['Q']/baseline['Q'])/np.log(1+offset)),status='SIMULADO')
            except RuntimeError as exc:
                attempt.update(status='FALLO_NUMERICO_NO_INEXISTENCIA',reason=str(exc))
                if name=='M' and offset>0:
                    try:
                        bg,candidate=retry_mass_path(base,offset);data=measures(bg,.9,model=candidate)
                        fine=solve_state(previous=bg,model=candidate,radius=75,n=1800,tol=5e-10);check=measures(fine,.9,model=candidate)
                        attempt.update(result=data,refined=check,E_relative_error=abs(check['E']/data['E']-1),Q_relative_error=abs(check['Q']/data['Q']-1),
                            susceptibility_logQ=float(np.log(data['Q']/baseline['Q'])/np.log(1+offset)),status='SIMULADO',
                            recovery_method='Two-leg continuation: g reduced, then M and g raised at fixed g/M; final point changes M alone.')
                    except RuntimeError as retry_error:attempt['retry_failure']=str(retry_error)
            sensitivity.append(attempt)
            (O/'partial_sensitivity.json').write_text(json.dumps(sensitivity,ensure_ascii=False,indent=2)+'\n')
            print('PARAMETER',name,offset,attempt['status'],flush=True)
    cap=json.loads((R/'validacion/capilaridad/resultados.json').read_text());tau=cap['tension'];w=cap['coexistence']['enthalpy_density'];cs=np.sqrt(cap['coexistence']['sound_speed_squared'])
    wall=Tabulated(R/'validacion/capilaridad/pared.csv');xx=np.linspace(wall.x[0],wall.x[-1],50001);density=wall.f(xx)**2/cap['coexistence']['s'];width=float(np.interp(.1,density[::-1],xx[::-1])-np.interp(.9,density[::-1],xx[::-1]))
    expanded=json.loads((O/'intento_01_resultados.json').read_text())['capillary_extension'] if '--reuse-capillary' in sys.argv else []
    for d in (() if expanded else (2,3)):
        for rn in cfg['capillary_extension']['norm_radii']:
            state=next(x for x in cap['radial_family'] if x['dimension']==d and x['norm_radius']==rn)
            bg=Tabulated(R/f'validacion/capilaridad/perfil_d{d}_RN{rn}.csv');radius=state['equimolar_radius']
            modes=cfg['capillary_extension']['sphere_ell'] if d==3 else cfg['capillary_extension']['tube_kR']
            for mode in modes:
                ell=mode if d==3 else 0;k=0 if d==3 else mode/radius
                factor=ell*(ell-1)*(ell+2) if d==3 else mode*(1-mode*mode)*iv(1,mode)/iv(0,mode)
                prediction=float(np.sqrt(tau*factor/(w*radius**3)))
                rows=[spectrum(bg,d,dx,state['omega'],k=k,ell=ell) for dx in cfg['capillary_extension']['dx']]
                extra=extrapolate(rows,'rate');error=abs(extra['value']/prediction-1)
                record=dict(dimension=d,norm_radius=rn,ell=ell,kR=None if d==3 else mode,omega=state['omega'],
                            equimolar_radius=radius,wall_width_10_90=width,width_over_radius=width/radius,
                            k_width=k*width,frequency_radius_over_cs=extra['value']*radius/cs,
                            prediction=prediction,samples=rows,extrapolation=extra,relative_capillary_error=error,
                            accepted_error_levels=[level for level in [.01,.05,.1] if error+2*extra['relative_sequence_difference']<level])
                expanded.append(record);print('CAP',d,rn,mode,error,flush=True)
                (O/'partial_capillary.json').write_text(json.dumps(expanded,ensure_ascii=False,indent=2)+'\n')
    # At Phi=0, Tr[(mass matrix)^2]=2(m^2+g chi+h chi^2/2)^2+M^4.
    quantum=dict(one_loop_polynomial_at_Phi_zero={'constant':2*model.m**4+model.M**4,'chi':4*model.m**2*model.g,
                    'chi2':2*model.g**2+2*model.m**2*model.h,'chi3':2*model.g*model.h,'chi4':model.h**2/2},
                 absent_operators_required=['chi','chi^3','chi^4','constant'],
                 conclusion='The five-term classical potential is not closed under quantum renormalization. Finite coefficients and renormalization conditions are missing.',
                 quantum_cutoff_identified=False,new_terms_adopted=False)
    result=dict(schema_version='1.0.0',stage='E02',baseline=baseline,analytic_parameter_map=analytic,independent_sensitivity=sensitivity,
                capillary_extension=expanded,quantum_audit=quantum,region_between_samples_certified=False,
                radial_ell0_capillary_formula_valid=False,environment_and_noise_defined=False,
                passed=bool(all(x['status']=='SIMULADO' and max(x['E_relative_error'],x['Q_relative_error'])<1e-7 for x in sensitivity) and all(x['extrapolation']['relative_sequence_difference']<.002 for x in expanded)))
    (O/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    if not result['passed']:raise SystemExit(1)
if __name__=='__main__':run()
