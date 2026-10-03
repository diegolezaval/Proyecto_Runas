"""Comprobaciones independientes de geometría y casos físicos reducidos; stdlib."""
from pathlib import Path
import json,math,sys,platform,re,xml.etree.ElementTree as ET
from geometria import ends,bounds,topology,straight_overlaps
R=Path(__file__).resolve().parents[1]
def load(n):return json.loads((R/'datos'/n).read_text())
g=load('geometria.json');p=load('parametros.json');models=load('modelos.json')['models'];recipes=load('recetas.json')['recipes'];checks=[];results={}
def val(group,k):return p[group][k]['value']
def check(name,ok,detail=''):checks.append({'name':name,'passed':bool(ok),'detail':detail})
def close(a,b,rel=1e-9):return abs(a-b)<=rel*max(abs(a),abs(b),1)
# Canonical data structure and exact geometry, including free ends and disconnected bridge.
check('24 identidades únicas',len(g['runes'])==24 and len({r['id'] for r in g['runes']})==24)
check('Contrato para cada glifo',[x['id'] for x in models]==[r['id'] for r in g['runes']])
geo=[]
for r in g['runes']:
 ep=ends(g,r);used=[e for j in r['joins'] for e in j];free=set(ep)-set(used)
 check(r['id']+' uniones racionales exactas',all(all(ep[e]==ep[j[0]] for e in j) for j in r['joins']))
 check(r['id']+' extremos declarados',len(used)==len(set(used)) and free==set(r['free_ends']))
 check(r['id']+' puertos válidos',all(q['end'] in ep for q in r['ports']))
 check(r['id']+' sin superposición recta',not straight_overlaps(g,r))
 t=topology(g,r);check(r['id']+' conectividad',t['connected_components']==(2 if r['id']=='P-16' else 1))
 geo.append({'id':r['id'],**t,'bounds':[float(x) for x in bounds(g,r)]})
check('P-20 cinco piezas y dos ciclos',geo[19]['pieces']==5 and geo[19]['independent_cycles']==2)
check('Trazabilidad de 50 hallazgos',len(load('revision.json')['findings'])==50)
for group,values in p.items():
 if isinstance(values,dict) and group!='microscopic_benchmark':
  check('Unidades y evidencia '+group,all(isinstance(x,dict) and all(k in x for k in ['value','unit','meaning','status']) and math.isfinite(x['value']) for x in values.values()))
for m in models:check(m['id']+' referencias de parámetros',all(k in p for k in m['parameter_groups']))
for recipe in recipes:
 states=set(recipe['states']);tr=recipe['transitions'];seen={(t['from'],t['event']) for t in tr}
 check(recipe['id']+' autómata determinista',len(seen)==len(tr) and all(t['from'] in states and t['to'] in states for t in tr))
 check(recipe['id']+' módulos existentes',all(m in {x['id'] for x in models} for m in recipe['modules']))
 current=recipe['initial_state']
 for event in ['prepared','checks_pass','start','stop','resources_settled']:
  current=next(t['to'] for t in tr if t['from']==current and t['event']==event)
 check(recipe['id']+' recorrido normal','apagado'==current)
 current='ejecucion'
 for event in ['fault','local_fallback','resources_settled']:current=next(t['to'] for t in tr if t['from']==current and t['event']==event)
 check(recipe['id']+' recorrido de fallo','apagado'==current)
# Lamp: independently account all external energy exits.
I=val('solar','irradiance');eta=val('solar','efficiency');A=val('lamp_case','collector_area');area_hold=val('solar','maintenance_area');L=val('lamp_case','channel_length');atten=val('power_channel','attenuation')
light=val('lamp_case','optical_power');emitter=light/val('optical','efficiency');channel_input=emitter*math.exp(atten*L);channel_loss=channel_input-emitter;services=val('power_channel','hold_power_length')*L+val('seed','idle_power')+val('lamp_case','aux_power');required=channel_input+services;bus=(eta*I-area_hold)*A;export=bus-required;heat=(1-eta)*I*A+area_hold*A+(emitter-light)+channel_loss+services
check('Lámpara: balance externo energía',close(I*A,light+heat+export) and export>0)
results['lamp']={'incident_W':I*A,'optical_W':light,'heat_W':heat,'export_W':export,'required_bus_W':required,'preparation_J':val('seed','prep_energy')+val('power_channel','structural_energy_length')*L+val('solar','deployment_energy_area')*A+val('lamp_case','aux_preparation_energy')}
# Thermostat: analytical ODE solution and time-integrated leakage.
C=val('thermal','water_cp')*val('control_case','water_mass');P=val('control_case','heater_power');G=val('control_case','thermal_loss_conductance');dT=val('control_case','target_temperature')-val('control_case','initial_temperature');time=-C/G*math.log(1-G*dT/P);stored=C*dT;lost=P*(time-C/G*(1-math.exp(-G*time/C)))
check('Calefacción: energía y pérdidas integradas',close(P*time,stored+lost))
results['heater']={'time_s':time,'input_J':P*time,'stored_J':stored,'loss_to_environment_J':lost}
# Freezing uses the stated terminal idealization, not the 400 K radiator.
Ti=val('control_case','initial_temperature');Tf=273.15;latent=val('thermal','water_latent_fusion')*val('control_case','water_mass');Qc=C*(Ti-Tf)+latent;Wmin=C*(Ti*math.log(Ti/Tf)-(Ti-Tf))+latent*(Ti/Tf-1);W=Wmin/val('thermal','carnot_fraction');Qh=Qc+W;dswater=C*math.log(Tf/Ti)-latent/Tf;entropy=dswater+Qh/Ti
check('Congelación: primer y segundo principios',close(Qh,Qc+W) and entropy>=0)
results['freezing']={'heat_extracted_J':Qc,'minimum_work_J':Wmin,'R1_work_ideal_terminals_J':W,'heat_rejected_J':Qh,'entropy_generated_J_K':entropy}
# Reserve duration and recovery cycle.
E0=val('reserve','volume')*val('reserve','usable_density');kd=val('reserve','leak_rate');idle=val('reserve','idle_power');effd=val('reserve','eta_discharge');Pd=1000;cons=Pd/effd+idle;t=math.log1p(kd*E0/cons)/kd;end=(E0+cons/kd)*math.exp(-kd*t)-cons/kd
check('Reserva: duración a 1 kW y no energía negativa',abs(end)<1e-4)
m=val('control_case','mass');grav=val('constants','g');h=val('control_case','height');work=m*grav*h;act=work/val('mechanical','mechanical_efficiency');debit=act/effd;credit=work*val('mechanical','regen_efficiency');loss=(act-work)+(debit-act)+(work-credit)
check('Ciclo elevación: energía neta igual a pérdidas',close(debit-credit,loss) and loss>0)
results['reserve']={'useful_J':E0,'structural_J':val('reserve','structural_density')*val('reserve','volume'),'max_power_W':val('reserve','power_density')*val('reserve','volume'),'runtime_1kW_s':t}
results['lifting']={'gravity_J':work,'actuator_input_J':act,'reserve_debit_J':debit,'regenerated_J':credit,'net_cycle_loss_J':loss}
Y=val('mechanical','young_modulus');area=val('mechanical','cross_section');length=val('mechanical','length');ust=val('mechanical','structural_density');spring=Y*area/length;force=m*grav;maxforce=Y*area*val('mechanical','max_strain');speed=val('constants','c')*math.sqrt(Y/ust)
check('Soporte: carga y velocidad causal',force<maxforce and speed<val('constants','c'))
results['support']={'stiffness_N_m':spring,'max_force_N':maxforce,'structural_J':ust*area*length,'static_extension_m':force/spring,'elastic_J':force**2/(2*spring),'hold_W':ust*area*length*val('mechanical','hold_fraction'),'terminal_area_m2':force/val('mechanical','surface_pressure_max'),'conditional_wave_speed_m_s':speed}
# RK4 closed-loop step, compare against independent critically-damped analytic response.
wn=val('control_case','natural_frequency');ref=.05;dur=1

def controller(dt):
 x=v=0.;maximum=0
 def f(x,v):
  F=max(-maxforce,min(maxforce,m*grav+m*wn**2*(ref-x)-2*m*wn*v))
  return v,F/m-grav,F
 for k in range(round(dur/dt)):
  a,b,F=f(x,v);a2,b2,_=f(x+dt*a/2,v+dt*b/2);a3,b3,_=f(x+dt*a2/2,v+dt*b2/2);a4,b4,_=f(x+dt*a3,v+dt*b3);x+=dt*(a+2*a2+2*a3+a4)/6;v+=dt*(b+2*b2+2*b3+b4)/6;maximum=max(maximum,abs(F))
 return x,v,maximum
c1=controller(.002);c2=controller(.001);exact=ref*(1-(1+wn*dur)*math.exp(-wn*dur))
check('Control mecánico: convergencia y solución analítica',abs(c2[0]-exact)<1e-8 and abs(c1[0]-c2[0])<1e-8 and abs(ref-c2[0])<.001 and c2[2]<maxforce)
results['controller']={'duration_s':dur,'target_step_m':ref,'final_x_m':c2[0],'analytic_x_m':exact,'refinement_change_m':abs(c1[0]-c2[0]),'max_force_N':c2[2],'scope':'Sin ruido ni retardo de sensor mecánico; no prueba robustez ante todos los fallos.'}
# Solar growth valid while energy-limited.
earea=val('solar','deployment_energy_area');net=eta*I-area_hold;asym=val('seed','idle_power')/net;a0=val('solar','starter_area');target=1.;growth=earea/net*math.log((target-asym)/(a0-asym));ratio=(net*target-val('seed','idle_power'))/earea/(2*val('solar','front_speed')*math.sqrt(math.pi*target))
check('Crecimiento a 1 m²: rama energética admisible',a0>asym and ratio<1)
results['solar_growth']={'initial_area_m2':a0,'target_area_m2':target,'time_ideal_s':growth,'assumption':'Sustrato, soporte, sumidero y control salvo servicio Semilla preexistentes.'}
rad=val('thermal','emissivity')*val('constants','sigmaSB')*(val('thermal','radiator_temperature')**4-val('thermal','ambient_temperature')**4)
results['radiator']={'net_W_m2':rad,'area_per_collector_m2':((1-eta)*I+area_hold)/rad}
results['channel']={'delay_1km_s':1000/val('power_channel','signal_speed'),'transmission_1km':math.exp(-1000*atten),'capacity_bound_bit_s':val('power_channel','signal_bandwidth')*math.log2(1+val('power_channel','snr'))}
results['logic']={'landauer_J':val('constants','kB')*val('logic','temperature')*math.log(2),'single_bit_thermal_lifetime_s':val('logic','attempt_time')*math.exp(val('logic','barrier_kBT'))}
check('Lógica: presupuesto de conmutación sobre Landauer',val('logic','switch_energy')>results['logic']['landauer_J'])
results['photon_support_power_W']=m*grav*val('constants','c')
cc=p['chemistry_case'];n=val('chemistry_case','carbon_mass')/val('chemistry_case','carbon_molar_mass');volume=n*val('constants','Rgas')*val('chemistry_case','temperature')/(val('chemistry_case','pressure')*val('chemistry_case','co2_fraction'))
results['carbon']={'amount_mol':n,'air_m3_complete_capture':volume,'minimum_work_J':n*val('chemistry_case','decomposition_gibbs'),'oxygen_kg':n*val('chemistry_case','oxygen_molar_mass'),'global_reversible_voltage_V':val('chemistry_case','decomposition_gibbs')/(4*val('constants','F'))}
# Data formats and links. XML parses every figure, including later derived ones if present.
jsonfiles=list(R.rglob('*.json'))
for file in jsonfiles:json.loads(file.read_text())
check('Todos los JSON se pueden leer',True,str(len(jsonfiles)))
svgfiles=list((R/'graficos').rglob('*.svg'))
for file in svgfiles:ET.parse(file)
check('SVG XML íntegros',len(svgfiles)>=52,str(len(svgfiles)))
missing=[]
for file in list((R/'fichas').glob('*.md'))+list((R/'tratado').glob('*.md'))+[R/'LEEME.md',R/'GUIA_MICROSCOPICA.md',R/'Runica_Tratado_integrado.md']:
 for url in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',file.read_text()):
  if not url.startswith(('https:','http:','#')) and not (file.parent/url.split('#')[0]).exists():missing.append(str(file.relative_to(R))+': '+url)
check('Enlaces locales existentes',not missing,'; '.join(missing))
micro=json.loads((R/'validacion/microscopia.json').read_text());check('Ensayo microscópico: dominio, residuo y virial',micro['passed'] and micro['fine']['virial_relative']<1e-5 and micro['relative_change_E']<1e-4)
extension=json.loads((R/'validacion/correspondencia_micro.json').read_text())
completion=json.loads((R/'validacion/complecion_escalar.json').read_text())
engine=json.loads((R/'validacion/preparacion_motor.json').read_text())
check('Extensión microscópica: ensayos aprobados',extension['passed'] and completion['passed'] and engine['passed'],'Alcance declarado por cada sector; no certificación conjunta.')
matching=load('correspondencia.json')['runes']
check('Correspondencia explícita de 24 primordiales',[x['id'] for x in matching]==[x['id'] for x in models] and all(x['matching_coefficients'] and x['remaining_requirement'] for x in matching))
report={'edition':'4.1.0','legacy_suite_origin':'3.0.0','environment':{'python':platform.python_version()},'scope':'Validación de archivos, geometría exacta, algunos modelos reducidos y un sector radial. No valida realizaciones físicas, biología, un reactor ni correspondencia microscópica conjunta.','passed':all(x['passed'] for x in checks),'checks':checks,'geometry':geo,'calculations':results}
try:
 import numpy,scipy
 report['environment'].update(numpy=numpy.__version__,scipy=scipy.__version__)
except ImportError:pass
(R/'validacion/informe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
s='# Resultados de verificación\n\n'+report['scope']+'\n\n'+f'**Resultado:** {sum(x["passed"] for x in checks)}/{len(checks)} comprobaciones satisfactorias.\n\n'
s+='## Ensayo microscópico\n\n| Magnitud | Resultado |\n|---|---:|\n'
for key in ['f0','Qhat','Ehat','E_over_Q','virial_relative','solver_max_rms_residual']:s+=f'| {key} | {micro["fine"][key]:.12g} |\n'
s+=f'| Cambio relativo de energía entre dominios | {micro["relative_change_E"]:.12g} |\n\nNo se fija una escala física m_r. No se ha probado estabilidad espectral completa.\n\n'
for section,vals in results.items():
 s+='## '+section+'\n\n'
 if isinstance(vals,dict):
  s+='| Magnitud o supuesto | Resultado |\n|---|---|\n'
  for k,v in vals.items():s+='| '+k+' | '+(f'{v:.12g}' if isinstance(v,(float,int)) else str(v))+' |\n'
 else:s+=str(vals)+'\n'
 s+='\n'
s+='## Comprobaciones\n\n| Prueba | Estado |\n|---|---|\n'
for c in checks:s+='| '+c['name']+' | '+('Correcta' if c['passed'] else 'FALLÓ: '+c['detail'])+' |\n'
(R/'validacion/informe.md').write_text(s);(R/'tratado/07_resultados.md').write_text(s)
print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[x for x in checks if not x['passed']],'calculations':results},ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
