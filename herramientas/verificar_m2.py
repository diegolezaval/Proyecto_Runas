"""Verificaciones de resultados y de su clasificación; no una prueba automática de física."""
from pathlib import Path
import json,math,ast,re
import xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parents[1]
def load(path):return json.loads((R/path).read_text())
theta=load('datos/theta_comun.json');q=load('validacion/cierre_m2.json');g=load('validacion/guia_m2.json')
d=load('validacion/dinamica_m2.json');c=load('validacion/contrastes_r1.json');cat=load('datos/aceptacion_m2.json')
checks=[]
def check(name,ok,detail=''):checks.append({'check':name,'passed':bool(ok),'detail':detail})
legacy=load('datos/microscopia.json')['M2'];common=theta['scalar_benchmark']['dimensionless']
check('Una fuente comun: el espejo historico coincide',all(legacy[k]==v for k,v in common.items()))
check('Sin nuevos parametros fundamentales de dispositivo',not q['new_device_specific_fundamental_parameters'] and g['same_fundamental_parameters_as_Qball'])
check('El conjunto interactuante R1 no se declara identificado',not theta['total_interacting_theory']['identified_jointly'])
fine=q['field_convergence'][-1];prev=q['field_convergence'][-2]
check('Convergencia energia Q-ball',abs(fine['Ehat']/prev['Ehat']-1)<1e-8)
check('Virial Q-ball',fine['virial_relative']<1e-8)
check('Pendiente de rama y primera ley',all(r['dQ_dw']<0 and abs(r['dE_dQ']-.9)<1e-5 for r in q['branch_derivatives']))
check('Carga fija radial positiva en mallas calculadas',all(r['H_fixed_charge'][0]>0.18 for r in q['spectra'] if r['ell']==0))
phase=[r for r in q['spectra'] if r['ell']==1 and r['radius']==40]
check('Traslacion: error de autovalor decrece como h^2',3.9<abs(phase[-2]['H_amplitude'][0]/phase[-1]['H_amplitude'][0])<4.1)
check('Q-ball: el modo cuadrupolar esta bajo el continuo',all(0.04<min(abs(v['imag']) for v in r['selected_generator_eigenvalues'])<.1 for r in q['spectra'] if r['ell']==2))
check('Generadores Q-ball: residuos numericos',max(r.get('dynamic_residual_max',0) for r in q['spectra'])<1e-7)
check('No se declara certificacion espectral del continuo',not q['certified_continuum_spectral_proof'])
check('Energia no lineal: mejora al refinar',3<d['runs'][0]['max_relative_energy_drift']/d['runs'][1]['max_relative_energy_drift']<5)
check('Noether numerico conservado',max(r['max_relative_charge_drift'] for r in d['runs'])<1e-10)
check('Transitorio no se vende como preparacion',not d['preparation_demonstrated'])
gf=g['background_convergence'][-1];gp=g['background_convergence'][-2]
check('Guia: convergencia de energia por longitud',abs(gf['energy_per_length']/gp['energy_per_length']-1)<1e-8)
check('Guia: virial transversal',gf['transverse_virial_relative']<1e-8)
gs=g['spectral_convergence'];fineg=gs[-1]
check('Guia: autovalor negativo robusto',all(r['H_low'][0]<-.05 for r in gs))
check('Guia: crecimiento robusto al refinar dominio',abs(gs[-2]['growth_samples'][2]['growth']/gs[-1]['growth_samples'][2]['growth']-1)<1e-5)
check('Guia: exterior de banda sin crecimiento en muestra k=0.3',max(r['growth_samples'][-1]['growth'] for r in gs)<1e-8)
check('Guia: raiz creciente resuelta',max(r['residual'] for r in g['growth_band'])<1e-7)
check('Guia: signo hidrodinamico concordante',all(r['long_wave_cL_squared']<0 for r in g['charge_derivative']))
check('Guia: no se marca estabilidad ni terminal demostrados',not g['stable_free_guide_demonstrated'] and not g['exact_Neumann_terminal_demonstrated'])
terminal=next(r for r in g['exterior_vacuum'] if r['Omega']==.05)
check('Vacío: las tres constantes de decaimiento son no nulas',min(terminal['kappa_squared_phi_plus_minus_chi'])>0)
terminal=next(r for r in g['exterior_vacuum'] if r['Omega']==.125)
check('Vacío: apertura de radiacion en la primera banda',terminal['kappa_squared_phi_plus_minus_chi'][0]<0)
x=np.linspace(-3,3,503);rho=np.exp(2j*x);r=(rho-1)/(rho+3);t=2*(1+rho)/(3+rho)
check('Grafo terminado: conservacion independiente de potencia',np.max(abs(abs(r)**2+abs(t)**2-1))<1e-12)
check('Canal: presupuesto de reflexion condicionado',c['P04']['matched_neumann_stub']['reflection_at_plus_minus_500kHz']<c['P04']['R1_bulk_loss_fraction'])
check('Canal: velocidad R1 requiere presion negativa en ese fondo',q['homogeneous']['state_matching_R1_speed_only']['pressure']<0)
check('Memoria: barrera de fase y meta no se confunden',c['P11']['phase_encoding_barrier_J_exact_U1']==0 and c['P11']['R1_requested_barrier_J']>0)
check('Termica: canal con brecha suprimido',0<c['P18']['one_gapped_ballistic_channel_W_K']<c['P18']['gapless_conductance_quantum_W_K'])
check('Semilla: restricciones de cero y carga registradas',c['P01']['exact_zero_classical_field_remains_zero'] and c['P01']['net_charge_created_by_U1_invariant_closed_drive']==0)
check('Catalogo: 24 identidades unicas',len(cat['runes'])==len({r['id'] for r in cat['runes']})==24)
check('Catalogo: aceptacion es una conjuncion',all(r['complete_device_derived']==all(r['complete_chain'].values()) for r in cat['runes']))
check('Las 24 primordiales evaluadas, sin la antigua exclusion',cat['evaluated_catalog_count']==24 and cat['explicitly_deferred_count']==0 and all(r['decision']=='no_aceptada_como_derivada' for r in cat['runes']))
check('Ningun dispositivo condicional declarado completo',not any(r['complete_device_derived'] for r in cat['runes']))
for f in R.rglob('*.json'):
    json.loads(f.read_text())
check('JSON: todos parsean',True)
for f in (R/'herramientas').glob('*.py'):ast.parse(f.read_text(),filename=str(f))
check('Python: sintaxis de todos los scripts',True)
for f in (R/'graficos').rglob('*.svg'):ET.parse(f)
check('SVG: todos parsean como XML',True)
from rutas_documentales import missing_links
missing=missing_links(R)
check('Enlaces locales Markdown',not missing,'; '.join(missing[:20]))
report={'schema_version':'4.1.0','count':len(checks),'passed':all(x['passed'] for x in checks),
        'scope':'Comprobaciones numericas y editoriales; no certificacion por intervalos ni demostracion de R1.',
        'complete_device_derived':False,'checks':checks}
(R/'validacion/verificacion_m2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# Verificación de la edición M2 4.1\n',f'Comprobaciones: {len(checks)}. Resultado: '+('correctas' if report['passed'] else 'con fallos')+'.\n',report['scope']+'\n','| Comprobación | Resultado |\n|---|---|']
lines += [f'| {v["check"]} | '+('Correcta' if v['passed'] else 'FALLO')+' |' for v in checks]
(R/'validacion/verificacion_m2.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'count':report['count'],'passed':report['passed'],'failed':[x for x in checks if not x['passed']]},ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
