"""Duhamel y referencia extendida de una identidad mal condicionada; cero evolución."""
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


def extended_identity(c,f,sc,sf,rc,rf,wf,use,qkey):
    """Same stored coefficients and fixed spline; precision is the sole change."""
    extended=np.longdouble
    if np.finfo(extended).eps>=np.finfo(float).eps:
        raise ValueError('Este entorno no ofrece longdouble con mayor precisión')
    count=int(use.sum());local=count+1
    I=np.asarray(interpolate(rc,np.eye(sc.n),rf[:local]),dtype=extended)
    def apply_lap(sim,q,local_count=None):
        w=np.asarray(sim.w[:len(q),None],dtype=extended)
        cent=np.asarray(sim.cent[:len(q)],dtype=extended)
        flux=np.asarray(sim.c[:len(q)-1,None],dtype=extended)*np.diff(q,axis=0)
        value=np.zeros_like(q);value[:-1]+=flux;value[1:]-=flux
        if len(q)==sim.n:
            value[-1]-=extended(2*sim.radius**2/sim.dx)*q[-1]
        return (value/w-cent*q)[:local_count] if local_count is not None else value/w-cent*q
    def source(sim,q):
        Y=np.asarray(sim.Y,dtype=extended);YW=np.asarray(sim.YW,dtype=extended)
        a,b,z=q@Y
        return -((extended(model.trilinear)+extended(model.mixed)*z)*(a*a+b*b))@YW
    qc=np.asarray(c[qkey],dtype=extended)
    qf=np.asarray(f[qkey][:,:local],dtype=extended)
    Iq=I@qc[2];lc=apply_lap(sc,qc[2]);lf=apply_lap(sf,qf[2],count)
    fc=source(sc,qc);ff=source(sf,qf)[:count]
    M2=extended(model.mediator**2)
    d=Iq-qf[2]
    comm=-apply_lap(sf,Iq,count)+(I@lc)[:count]
    fd=(I@fc)[:count]-ff
    lhs=(I@(lc-M2*qc[2]+fc))[:count]-(lf-M2*qf[2,:count]+ff)
    rhs=-M2*d[:count]+apply_lap(sf,d,count)+comm+fd
    sw=np.sqrt(np.asarray(wf[use,None],dtype=extended))
    def size(x):return np.sqrt(np.sum((sw*x)**2))
    denominator=max(size(lhs),size(rhs),extended(1e-300))
    error=float(size(lhs-rhs)/denominator)
    reference=interpolate(rc,c[qkey][2],rf[use])
    map_error=float(size(Iq[:count]-reference)/max(size(Iq[:count]),extended(1e-300)))
    scale=extended(norm(f['initial_q'][2,use],f['initial_v'][2,use],wf[use]))
    def scaled(q):return float(np.sqrt(np.sum(np.asarray(wf[use,None],dtype=extended)*(q[:,1:]/M2)**2)/scale))
    return dict(identity_relative_residual=error,spline_matrix_equivalence_relative_error=map_error,
                operator_commutator_norm_over_M2_initial_chi=scaled(comm),
                source_difference_norm_over_M2_initial_chi=scaled(fd),
                float64_epsilon=float(np.finfo(float).eps),reference_epsilon=float(np.finfo(extended).eps),
                values_are_instantaneous_not_integrated_error_budgets=True,
                same_equations_parameters_states_and_interpolation=True)


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
        instantaneous.append(dict(frame=frame,**extended_identity(c,f,sc,sf,rc,rf,wf,use,qkey)))
    passed=closure<cfg['parseval_relative_tolerance'] and all(x['identity_relative_residual']<cfg['algebra_relative_tolerance'] and x['spline_matrix_equivalence_relative_error']<cfg['algebra_relative_tolerance'] for x in instantaneous)
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
                arithmetic_reference='longdouble; misma acción y estados, spline fijo; intento doble fallido preservado',
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
