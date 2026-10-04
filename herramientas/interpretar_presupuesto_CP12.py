"""Lectura offline del presupuesto CP12; cero pasos M2 y ninguna corrección."""
from pathlib import Path
import argparse, json
import numpy as np
from threadpoolctl import threadpool_limits
import ejecutar_con_procedencia as prov
from continuar_no_radial_m2 import Evolution
from observador_causal_CP12 import BARE, COUPLED, interpolate, chi_inner, model

ROOT=Path(__file__).resolve().parents[1]
PAIR=ROOT/'validacion/P06/no_radial/CP12/par_instrumentado__a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
GROUPS={'raw':{'inicial':[0],'operador':[1],'fuente_total':[2,3,4]},
        'coupled':{'inicial':[0],'operador_total':[1,2],'transferencia_total':[3,4]}}

def read(p):return json.loads(p.read_text())

def metrics(gram,indices,scale):
    norm=float(gram[0,0]);den=max(norm,scale*1e-10)
    power=float(gram[np.ix_(indices,indices)].sum());dot=float(gram[indices,0].sum())
    return dict(relative_error=float(np.sqrt(max(0,power)/scale)),signed_projection=dot/den,
        cosine=dot/np.sqrt(max(1e-300,power*norm)),removal_squared_reduction=(2*dot-power)/den)

def sufficient(m,c):
    return m['signed_projection']>=c['majority_signed_projection_min'] and m['cosine']>=c['majority_cosine_min'] and m['removal_squared_reduction']>=c['removal_squared_reduction_min']

def onset(values,times,threshold,count):
    for i in range(len(values)-count+1):
        if all(x>=threshold for x in values[i:i+count]):return times[i]
    return None

def interpret(configuration,out):
    original=read(ROOT/'datos/ensayo_causal_chi_CP12.json');criteria=original['observer_criteria']
    expected=dict(time=160,M2_steps=0,physical_gate_threshold=.02,groups=GROUPS)
    if configuration['case']['configuration']!=expected:
        raise ValueError('Configuración de lectura distinta del prerregistro')
    receipt=prov.verify_receipt(PAIR/'procedencia.json')
    if not receipt['passed'] or receipt['status']!='COMPLETADA':
        raise ValueError('Recibo final no completado y verificado; no interpretar')
    run=read(PAIR/'CP12_par.json')
    if not run['reproduces_CP10_exactly'] or not run['observer_checks_passed'] or run['time']!=160:
        raise ValueError('Reproducción y observadores no cerrados; no interpretar')
    certificate=read(ROOT/'trazabilidad/CP12_reconstruccion/respaldos/tau0160.json')
    if not certificate['passed'] or certificate['time']!=160 or not certificate['download_verification']['passed']:
        raise ValueError('Respaldo final no comprobado; no interpretar')
    for key,name in [('state_sha256','CP12_par_estado.npz'),('receipt_sha256','procedencia.json'),('configuration_sha256','configuration.json')]:
        if certificate[key]!=prov.digest(PAIR/name):
            raise ValueError('Estado final difiere del respaldo comprobado: '+name)
    with np.load(PAIR/'CP12_par_estado.npz',allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    with np.load(PAIR/'respuestas_finales.npz',allow_pickle=False) as z:responses={k:z[k].copy() for k in z.files}
    cfg=json.loads(str(saved['config']));n=int(saved['coarse_n'])
    sc,sf=[Evolution(x['dx'],x['radius'],x['L']) for x in cfg['physical_configurations']]
    dq=interpolate(sc,saved['q'][:,:n],sf)-saved['q'][:,n:]
    dv=interpolate(sc,saved['v'][:,:n],sf)-saved['v'][:,n:]
    scale=chi_inner(sf,saved['initial_q'][2,n:],saved['initial_v'][2,n:],saved['initial_q'][2,n:],saved['initial_v'][2,n:])
    q=np.concatenate([dq[2:3],responses['raw_q'][:,0],responses['coupled_q'][:,2]])
    v=np.concatenate([dv[2:3],responses['raw_v'][:,0],responses['coupled_v'][:,2]])
    core=np.array([[chi_inner(sf,a,b,c,d) for c,d in zip(q,v)] for a,b in zip(q,v)])
    series=read(PAIR/'serie_presupuestos.json');final=series[-1];assert len(series)==401 and final['time']==160
    windows={'core_phase':core,'short_core_k4':np.array(final['short_modes']['core']['short_response_gram_matrix']),
             'short_smooth_k4':np.array(final['short_modes']['smooth']['short_response_gram_matrix'])}
    tables={};dominance={};cross_terms={}
    for family,names,start in [('raw',BARE,1),('coupled',COUPLED,6)]:
        tables[family]={};dominance[family]={};cross_terms[family]={}
        channels={name:[i] for i,name in enumerate(names)}
        channels.update(GROUPS[family])
        for label,gram in windows.items():
            table={name:metrics(gram,[start+i for i in ids],scale) for name,ids in channels.items()}
            tables[family][label]=table
            cross_terms[family][label]={'response_gram_matrix':gram[start:start+5,start:start+5].tolist(),
                'normalized_by_observed_squared_norm':(gram[start:start+5,start:start+5]/max(float(gram[0,0]),scale*1e-10)).tolist()}
        for name in channels:
            dominance[family][name]={'meets_all_three_windows':all(sufficient(tables[family][label][name],criteria) for label in windows),
                'tests_by_window':{label:sufficient(tables[family][label][name],criteria) for label in windows}}
    full=lambda a,b:float(np.sum(sf.w[:,None]*(a*a+b*b/model.mediator**2)))
    closures={}
    for family,start in [('raw',1),('coupled',6)]:
        rq=dq[2]-q[start:start+5].sum(0);rv=dv[2]-v[start:start+5].sum(0)
        closures[family]=float(np.sqrt(full(rq,rv)/max(full(dq[2],dv[2]),1e-300)))
    if max(closures.values())>criteria['closure_relative_tolerance']:raise ValueError('Identidad de defecto no cierra en toda la caja')
    times=[r['time'] for r in series];onsets={}
    for label in ['core_phase','short_core_k4','short_smooth_k4']:
        if label=='core_phase':observed=final['observed_relative_error']
        else:observed=final['short_modes']['core' if label=='short_core_k4' else 'smooth']['short_relative_error']
        threshold=criteria['onset_final_observed_norm_fraction']*observed
        entries={}
        for family,names in [('raw',BARE),('coupled',COUPLED)]:
            for i,name in enumerate(names):
                if label=='core_phase':values=[r[family][i]['relative_error'] for r in series]
                else:
                    window='core' if label=='short_core_k4' else 'smooth'
                    values=[next(m['relative_error'] for m in r['short_modes'][window]['metrics'] if m['family']==family and m['name']==name) for r in series]
                entries[family+':'+name]=onset(values,times,threshold,criteria['onset_consecutive_samples'])
        onsets[label]={'relative_error_threshold':threshold,'consecutive_samples':criteria['onset_consecutive_samples'],'first_sustained_crossing':entries}
    candidates=[k for k,m in dominance['coupled'].items() if m['meets_all_three_windows']]
    result=dict(status='PRESUPUESTO_CAUSAL_CERRADO',time=160,scientific_scope='Dos historias CP10, spline fijo y descomposición prerregistrada; atribución condicionada.',
        reproduces_CP10_exactly=True,observer_checks_passed=True,full_box_chi_closure=closures,maximum_errors=run['maximum_errors'],
        observed_core_phase_relative_error=final['observed_relative_error'],physical_gate_threshold=.02,
        physical_gate='REFINAMIENTO_PENDIENTE',correction_tested=False,new_M2_steps=0,
        tables=tables,sufficiency=dominance,sufficient_coupled_channels=candidates,cross_terms=cross_terms,onsets=onsets,
        criteria=criteria,chi_operator_induced_Phi_response=[{'time':r['time'],'response_norm':r['coupled_Phi_response_from_chi_operator']} for r in series],
        feedback_scope='La respuesta acoplada incluye el Jacobiano completo medido. Un canal χ→Φ puede detectarse; no se inventa una separación adicional de retornos sin observadores.',
        scientific_closure_requires_review=True,
        limitations=original['limitations'])
    prov.write(out/'resultados.json',result)
    print(json.dumps({'status':result['status'],'sufficient_coupled_channels':candidates,'full_box_chi_closure':closures},ensure_ascii=False))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    with threadpool_limits(limits=1):interpret(read(a.config),a.output_dir)
