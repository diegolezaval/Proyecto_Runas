"""Controles independientes y limites del puente capilar. Salida distinta de cero al fallar."""
from pathlib import Path
import json, hashlib
import numpy as np
from scipy.integrate import simpson
from m2_comun import ROOT, potential, ueff, up, upp
R=ROOT
report=json.loads((R/'validacion/capilaridad/resultados.json').read_text())
limits=report['configuration']['thresholds']; checks=[]
def check(name,ok,details=''):
    checks.append(dict(check=name,passed=bool(ok),detail=details))
def bounded(name,value,limit): check(name,value<limit,f'{value:.9g} < {limit:.9g}')
wall=report['wall_convergence']; tau=report['tension']; co=report['coexistence']
check('Theta comun trazable',report['theta_sha256']==hashlib.sha256((R/'datos/theta_comun.json').read_bytes()).hexdigest())
check('Sin parametros fundamentales o capilares ajustados',not report['new_fundamental_parameters'] and not report['fitted_macroscopic_parameters'])
bounded('Coexistencia: presion nula',abs(ueff(co['s'])-co['omega']**2*co['s']),1e-12)
bounded('Coexistencia: estacionariedad',abs(up(co['s'])-co['omega']**2),1e-12)
check('Rama homogenea compresible estable y subluminal',0<co['sound_speed_squared']<1 and upp(co['s'])>0)
bounded('Factorizacion no negativa del potencial',report['variational_bounds']['factorisation_error'],1e-12)
bounded('Pared: refinamiento a dominio fijo',abs(wall[-3]['tension']/wall[-2]['tension']-1),limits['wall_last_relative_difference'])
bounded('Pared: ampliacion de dominio',abs(wall[-2]['tension']/wall[-1]['tension']-1),limits['wall_last_relative_difference'])
bounded('Pared: frecuencia auxiliar converge a coexistencia',abs(wall[-1]['mu_squared_shift']),1e-10)
bounded('Pared: primera integral',wall[-1]['first_integral_max'],limits['wall_first_integral_absolute'])
bounded('Pared: dos definiciones de tension',abs(wall[-1]['tension_from_stress']/tau-1),1e-8)
check('Pared: compatible con cotas variacionales',report['variational_bounds']['lower']<tau<report['variational_bounds']['adiabatic_trial_upper'])
# Use exported samples independently from the BVP quadrature grid.
p=np.loadtxt(R/'validacion/capilaridad/pared.csv',delimiter=',',skiprows=1)
x,f,fp,z,zp=p.T
bounded('CSV pared: energia superficial independiente',abs(simpson(fp**2+.5*zp**2+potential(f,z)-co['omega']**2*f**2,x=x)/tau-1),1e-8)
bounded('CSV pared: normal menos tangencial',abs(simpson(2*fp**2+zp**2,x=x)/tau-1),1e-8)
states=report['radial_family']
check('Diez estados no triviales en dos geometrías',len(states)==10 and {(r['dimension'],r['norm_radius']) for r in states}=={(d,n) for d in [2,3] for n in [8,16,32,64,128]})
for key,label,threshold in [('virial_relative','Virial',limits['radial_virial_relative']),('norm_relative','Norma',limits['norm_relative']),('stress_balance_relative','Balance exacto de tensiones',limits['stress_balance_relative'])]:
    bounded(label+': todas las escalas',max(r[key] for r in states),threshold)
charge_error=0.;energy_error=0.
for row in states:
    data=np.loadtxt(R/f"validacion/capilaridad/perfil_d{row['dimension']}_RN{row['norm_radius']}.csv",delimiter=',',skiprows=1)
    x,f,fp,z,zp=data.T; d=row['dimension']; sd=2*np.pi if d==2 else 4*np.pi; w=row['omega']
    q=2*w*sd*simpson(x**(d-1)*f**2,x=x)
    e=sd*simpson(x**(d-1)*(w*w*f*f+fp*fp+.5*zp*zp+potential(f,z)),x=x)
    charge_error=max(charge_error,abs(q/row['Q']-1));energy_error=max(energy_error,abs(e/row['E']-1))
bounded('CSV: carga integrada independientemente',charge_error,1e-7)
bounded('CSV: energia integrada independientemente',energy_error,1e-7)
for d in [2,3]:
    rows=[r for r in states if r['dimension']==d]
    check(f'd={d}: mejora de limite de Laplace',all(abs(a['laplace_ratio']-1)>abs(b['laplace_ratio']-1) for a,b in zip(rows,rows[1:])))
    check(f'd={d}: mejora del exceso de energia',all(abs(a['energy_excess_ratio']-1)>abs(b['energy_excess_ratio']-1) for a,b in zip(rows,rows[1:])))
    bounded(f'd={d}: Laplace a RN128',abs(rows[-1]['laplace_ratio']-1),limits['large_radius_laplace_relative'])
    bounded(f'd={d}: energia a RN128',abs(rows[-1]['energy_excess_ratio']-1),limits['large_radius_energy_relative'])
first=report['first_laws']
bounded('Primera ley dE/dQ=omega',max(r['relative_error'] for r in first),1e-7)
check('Susceptibilidad de rama: dQ/domega negativo',all(r['dQ_domega']<0 for r in first))
check('Tubo: cL^2 negativo sin contradiccion con cs^2 positivo',all(r['cL_squared']<0 for r in first if r['dimension']==2))
bounded('Tubo: cL^2 y limite capilar RN64',max(abs(r['cL_squared']/r['capillary_cL_squared']-1) for r in first if r['dimension']==2),.01)
spectra=report['spectra']; samples=[s for r in spectra for s in r['samples']]
check('Cinco pasos para cada geometria y escala modal',len(spectra)==8 and all(len(r['samples'])==5 for r in spectra))
bounded('Generador: residuos algebraicos',max(s['residual'] for s in samples),limits['generator_residual_absolute'])
bounded('Richardson: dos extrapolaciones',max(r['rate_extrapolation']['relative_sequence_difference'] for r in spectra),limits['richardson_sequence_relative'])
for d in [2,3]:
    rows=[r for r in spectra if r['dimension']==d]
    check(f'd={d}: error capilar decreciente con radio',all(abs(a['relative_prediction_error'])>abs(b['relative_prediction_error']) for a,b in zip(rows,rows[1:])))
    bounded(f'd={d}: prediccion modal a RN128',abs(rows[-1]['relative_prediction_error']),limits['large_radius_mode_relative'])
    domain=next(r for r in report['domain_check'] if r['dimension']==d)
    bounded(f'd={d}: dominio energia',domain['E_relative_difference'],1e-8)
    bounded(f'd={d}: dominio espectro sin correccion de h',domain['spectral_relative_difference'],limits['domain_spectrum_relative'])
check('Tubo: crecimiento persiste en todas las mallas',all(s['rate']>0 for r in spectra if r['dimension']==2 for s in r['samples']))
check('Tubo: shift-invert empieza bajo cota puntual del Hessiano',all(s['amplitude_lowest']>=s['amplitude_lower_bound'] for r in spectra if r['dimension']==2 for s in r['samples']))
bounded('Tubo: kcrit R tiende a uno',abs(next(r for r in spectra if r['dimension']==2 and r['norm_radius']==128)['kcrit_R']-1),limits['large_radius_kcrit_relative'])
check('Esfera: modo seleccionado oscilatorio, no crecimiento apreciable',all(abs(s['eigenvalue'][0])<1e-8 and s['eigenvalue'][1]>0 for r in spectra if r['dimension']==3 for s in r['samples']))
check('Malla gruesa conserva contraejemplo a usar solo residuo algebraico',any(abs(r['samples'][0]['rate']/r['rate_extrapolation']['value']-1)>.1 for r in spectra))
# Independent algebraic check of Lorentz-transformed unstable long-wave roots.
guide=json.loads((R/'validacion/guia_m2.json').read_text())
a=np.sqrt(-guide['charge_derivative'][-1]['long_wave_cL_squared']); velocities=np.array([-.9,-.5,0,.5,.9,.99]); k=.001
roots=k*(velocities*(1+a*a)+1j*a*(1-velocities**2))/(1+a*a*velocities**2)
bounded('Corriente: dispersion transformada',float(np.max(abs((roots-velocities*k)**2+a*a*(k-velocities*roots)**2))),1e-15)
check('Corriente: rama creciente para velocidades muestreadas',np.all(roots.imag>0))
check('Sin certificacion, preparacion ni dispositivo indebidamente declarados',not any(report[k] for k in ['continuum_error_certified','full_nonlinear_shape_stability_proved','preparation_demonstrated','complete_device_derived']))
cat=json.loads((R/'datos/aceptacion_m2.json').read_text())
check('P04 conserva resultado negativo',next(r for r in cat['runes'] if r['id']=='P-04')['current_realization_status']=='refutada_por_inestabilidad')
result=dict(schema_version='4.1.0',count=len(checks),passed=all(r['passed'] for r in checks),
            scope='Verificacion numerica interna, bajo hipotesis M2; no validacion experimental ni certificacion por intervalos.',checks=checks)
(R/'validacion/capilaridad/verificacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# Verificación del puente capilar\n',result['scope']+'\n',f"Comprobaciones: {len(checks)}. Resultado: {'correctas' if result['passed'] else 'con fallos'}.\n",'| Comprobación | Resultado | Detalle |\n|---|---|---|']
lines += [f"| {r['check']} | {'Correcta' if r['passed'] else 'FALLO'} | {r['detail']} |" for r in checks]
(R/'validacion/capilaridad/verificacion.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(count=len(checks),passed=result['passed'],failed=[r for r in checks if not r['passed']]),ensure_ascii=False,indent=2))
if not result['passed']: raise SystemExit(1)
