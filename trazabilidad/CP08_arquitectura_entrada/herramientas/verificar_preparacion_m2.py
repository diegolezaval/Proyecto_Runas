"""Audita el ensayo y su estado sin repetir evoluciones ni campañas cerradas."""
from pathlib import Path
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/preparacion'
def read(p):return json.loads(p.read_text())
d=read(O/'resultados.json');energy=read(O/'exceso_energia.json');state=read(R/'estado_progreso.json')
checks={}
checks['eight_completed_runs']=len(d['records'])==8
checks['numerical_verification']=d['numerical_verification_passed']
checks['three_convergence_controls']=len(d['convergence'])==3 and all(c['passed'] for c in d['convergence'])
checks['two_long_runs_settle_only_conditionally']=sum(r['radial_settling_criteria_passed'] for r in d['records'])==2 and all(not r['complete_preparation'] for r in d['records'])
checks['excitation_same_discrete_action_converges']=energy['excitation_convergence_passed'] and not energy['extractable_energy_demonstrated']
snapshots=[]
for r in d['records']:
    p=O/f"{r['run']}_estado.npz"
    with np.load(p,allow_pickle=False) as z:
        c=json.loads(str(z['config']));ok=abs(int(z['step'])*c['dt']-c['tmax'])<1e-10
        ok=ok and all(np.isfinite(z[k]).all() for k in ['phi','vel','chi','vchi','rows','initial','late'])
        ok=ok and len(z['phi'])==c['n'] and z['rows'][-1,0]==c['tmax']
    progress=read(O/f"{r['run']}_progreso.json")
    snapshots.append(dict(file=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),passed=bool(ok and progress['status']=='CALCULO_TERMINADO')))
checks['all_restart_states_complete_and_finite']=all(x['passed'] for x in snapshots)
transfer=read(O/'w7.20_h0.100_dt0.0020_R1300_T1200_transferencia.json')
checks['fine_run_resumed_from_240']=transfer['continued_from_time']==240 and not transfer['prior_steps_repeated'] and transfer['outer_annulus_energy_fraction']<1e-12
checks['failures_preserved']=(O/'intento_01_extension.json').exists() and (O/'intento_01_diagnostico_parcial.json').exists()
checks['stages_not_falsely_closed']=all(next(s for s in state['stages'] if s['id']==k)['status']=='PARCIAL' for k in ['E02','E03','RES0','E04','RES1'])
checks['C7_remains_in_progress']=next(s for s in state['stages'] if s['id']=='C7')['status']=='EN_PROGRESO'
report=dict(schema_version='1.0.0',checks=checks,passed=all(checks.values()),snapshots=snapshots,simulations_repeated=False,
    scope='Consistencia, conservación publicada, refinamiento y honestidad de puertas; no prueba del continuo ni experimento.')
(R/'validacion/verificacion_CP04.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='snapshots'},ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
