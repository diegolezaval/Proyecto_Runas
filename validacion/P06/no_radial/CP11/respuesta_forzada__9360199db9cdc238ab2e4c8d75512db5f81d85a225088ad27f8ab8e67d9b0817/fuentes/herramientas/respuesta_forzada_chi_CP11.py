"""Momentos exactos de Duhamel desde estados guardados; ninguna evolución."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np
from scipy.linalg import eigh_tridiagonal
from threadpoolctl import threadpool_limits,threadpool_info
from diagnosticar_mediador_CP10 import load
from continuar_no_radial_m2 import Evolution
from modelo_m2 import BENCHMARK as model
from diagnosticar_chi_CP11 import grid,interpolate,tridiagonal,chi_metrics,write

ROOT=Path(__file__).resolve().parents[1]


def norm(q,v,w):
    return float(np.sum(w[:,None]*(q[:,1:]**2+v[:,1:]**2/model.mediator**2)))


def forcing(sim,q):
    a,b,z=q@sim.Y
    return -((model.trilinear+model.mixed*z)*(a*a+b*b))@sim.YW


def lap(sim,q):
    fields=np.zeros((3,sim.n,sim.nm));fields[2]=q
    return sim.lap(fields)[2]


def run(configuration,out):
    cfg=configuration['case']['configuration']
    data=[load(ROOT/cfg['states'][key]) for key in ['coarse','fine']]
    sims=[Evolution(d['configuration']['dx'],cfg['radius'],cfg['L']) for d in data]
    c,f=data;sc,sf=sims;rc,wc=grid(c);rf,wf=grid(f);use=rf<cfg['core_radius']
    for path in cfg['prior_results']:
        prior=json.loads((ROOT/path).read_text())
        if prior.get('new_M2_evolution_steps')!=0:raise ValueError('No es el diagnóstico de origen')
    arrays=[];rows=[]
    for d,s in zip(data,sims):
        freeq=np.zeros_like(d['q'][2]);freev=np.zeros_like(d['v'][2])
        for ell in cfg['ell']:
            diag,off=tridiagonal(s,ell);lam,U=eigh_tridiagonal(diag,off,lapack_driver='stemr')
            omega=np.sqrt(model.mediator**2+lam);sel=s.ell==ell;sw=np.sqrt(s.w[:,None])
            a0=U.T@(sw*d['initial_q'][2][:,sel]);v0=U.T@(sw*d['initial_v'][2][:,sel])
            aT=U.T@(sw*d['q'][2][:,sel]);vT=U.T@(sw*d['v'][2][:,sel])
            co=np.cos(omega*cfg['time'])[:,None];si=np.sin(omega*cfg['time'])[:,None]
            aq=a0*co+v0/omega[:,None]*si;av=-omega[:,None]*a0*si+v0*co
            freeq[:,sel]=(U@aq)/sw;freev[:,sel]=(U@av)/sw
            bq,bv=aT-aq,vT-av
            for i in range(s.n):
                rows.append([s.dx,ell,i+1,float(lam[i]),float(np.sum(bq[i]**2)),
                             float(np.sum((bv[i]/model.mediator)**2)),
                             float(np.sum(bq[i]**2+(bv[i]/model.mediator)**2))])
        arrays.append(dict(freeq=freeq,freev=freev,bq=d['q'][2]-freeq,bv=d['v'][2]-freev))
    cq=interpolate(rc,c['q'][2],rf[use]);cv=interpolate(rc,c['v'][2],rf[use])
    dq=cq-f['q'][2,use];dv=cv-f['v'][2,use]
    freeq=interpolate(rc,arrays[0]['freeq'],rf[use])-arrays[1]['freeq'][use]
    freev=interpolate(rc,arrays[0]['freev'],rf[use])-arrays[1]['freev'][use]
    bq=interpolate(rc,arrays[0]['bq'],rf[use])-arrays[1]['bq'][use]
    bv=interpolate(rc,arrays[0]['bv'],rf[use])-arrays[1]['bv'][use]
    actual=norm(dq,dv,wf[use]);free=norm(freeq,freev,wf[use]);forced=norm(bq,bv,wf[use])
    closure=np.sqrt(norm(dq-freeq-bq,dv-freev-bv,wf[use])/actual)
    initial_scale=norm(f['initial_q'][2,use],f['initial_v'][2,use],wf[use])
    lower=max(0,float(1-np.sqrt(free/actual)))
    upper=float(1+np.sqrt(free/actual))
    instantaneous=[]
    for frame,qkey in [('initial','initial_q'),('final','q')]:
        qc,qf=c[qkey],f[qkey];Iqc=interpolate(rc,qc[2],rf);Ic_lap=interpolate(rc,lap(sc,qc[2]),rf)
        delta=Iqc-qf[2]
        commutator=-lap(sf,Iqc)+Ic_lap
        source_delta=interpolate(rc,forcing(sc,qc),rf)-forcing(sf,qf)
        acceleration_delta=interpolate(rc,sc.force(qc)[2],rf)-sf.force(qf)[2]
        rhs=-(model.mediator**2*delta-lap(sf,delta))+commutator+source_delta
        denominator=max(np.linalg.norm(np.sqrt(wf[use,None])*acceleration_delta[use]),np.linalg.norm(np.sqrt(wf[use,None])*rhs[use]),1e-300)
        error=float(np.linalg.norm(np.sqrt(wf[use,None])*(acceleration_delta-rhs)[use])/denominator)
        instantaneous.append(dict(frame=frame,identity_relative_residual=error,
            operator_commutator_norm_over_M2_initial_chi=float(np.sqrt(norm(commutator[use]/model.mediator**2,np.zeros_like(delta[use]),wf[use])/initial_scale)),
            source_difference_norm_over_M2_initial_chi=float(np.sqrt(norm(source_delta[use]/model.mediator**2,np.zeros_like(delta[use]),wf[use])/initial_scale)),
            values_are_instantaneous_not_integrated_error_budgets=True))
    passed=closure<cfg['parseval_relative_tolerance'] and all(x['identity_relative_residual']<cfg['algebra_relative_tolerance'] for x in instantaneous)
    with (out/'momentos_duhamel.csv').open('w') as stream:
        writer=csv.writer(stream,lineterminator='\n');writer.writerow(['dx','ell','mode_index','lambda','Duhamel_field_power','Duhamel_velocity_over_M_power','Duhamel_phase_space_power']);writer.writerows(rows)
    result=dict(checkpoint='CP11_DIAGNOSTICO_RADIAL_CHI',status='RESPUESTA_FORZADA_DELIMITADA_CAUSA_ABIERTA',
                algebra_passed=bool(passed),observed_threadpools=threadpool_info(),
                original_phase_space_error=float(np.sqrt(actual/initial_scale)),
                free_initial_phase_space_error=float(np.sqrt(free/initial_scale)),
                forced_response_phase_space_difference=float(np.sqrt(forced/initial_scale)),
                forced_difference_amplitude_ratio=float(np.sqrt(forced/actual)),
                forced_difference_lower_bound_amplitude_ratio=lower,
                forced_difference_upper_bound_amplitude_ratio=upper,
                decomposition_closure_relative_residual=float(closure),instantaneous_defect_terms=instantaneous,
                main_free_initial_explanation_rejected=bool(lower>cfg['forced_lower_bound_predominance_min']),
                source_history_reconstructible_from_endpoints=False,
                fundamental_model_Cauchy_uniqueness_questioned=False,cause_certified=False,
                physical_gate='REFINAMIENTO_PENDIENTE',physical_gate_threshold=.02,
                new_M2_evolution_steps=0,old_evolutions_repeated=False,
                decisions=[dict(hypothesis='PROPAGACION_LIBRE_INICIAL_DOMINANTE',decision='DESCARTADA' if lower>cfg['forced_lower_bound_predominance_min'] else 'NO_DESCARTADA',
                    scope='Cota triangular exacta de la diferencia en respuesta forzada. No separa error de operador y fuente.'),
                    dict(hypothesis='CAUSA_ACOPLADA_IDENTIFICADA',decision='ABIERTA_POR_HISTORIA_NO_GUARDADA',
                    scope='Los extremos dan dos momentos por modo; el presupuesto Duhamel de conmutador y fuente necesita su historia.')],
                stop_reason='Diagnóstico finito cerrado. No otra malla, otra fase ajustada o evolución sin evidencia discriminante y prerregistro nuevo.')
    if not result['observed_threadpools'] or any(p['num_threads']!=1 for p in result['observed_threadpools']):raise ValueError('Hilos no controlados')
    write(out/'resultados.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    if not passed:raise ValueError('Identidad o cierre no cumple las tolerancias prerregistradas')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    with threadpool_limits(limits=1):run(json.loads(args.config.read_text()),args.output_dir)
