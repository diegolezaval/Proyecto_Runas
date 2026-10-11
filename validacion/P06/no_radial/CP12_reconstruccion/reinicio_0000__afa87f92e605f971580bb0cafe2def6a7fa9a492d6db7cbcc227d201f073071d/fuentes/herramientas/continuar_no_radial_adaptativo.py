"""Full M2 force with DOP853; durable adaptive-time restarts, no mass split.

This is a numerical refinement of the existing CP04 continuation, not a new
physical term or a restart of a completed campaign. Restart times are explicit.
"""
import argparse,json,time,fcntl,hashlib
import numpy as np
from scipy.integrate import DOP853
from threadpoolctl import threadpool_limits
from continuar_no_radial_m2 import Evolution,seed,save_json,OUT


def destination_tag(dx,rtol,max_step,L,radius,eps,tmax,**unused):
    """Identidad efectiva del archivo; los locks deben compartir este destino."""
    scheme=f'dop853e{int(round(-np.log10(rtol)))}'
    return f'{scheme}_L{L}_h{dx:.3f}_dt{max_step:.4f}_R{radius:.0f}_eps{eps:.3f}_T{tmax:.0f}'


def run(dx=.5,rtol=1e-8,atol=1e-10,max_step=.02,L=4,radius=220.,eps=.02,tmax=160.,stop_at=None,fused=False):
    scheme=f'dop853e{int(round(-np.log10(rtol)))}'
    config=dict(dx=dx,dt=max_step,radius=radius,L=L,eps=eps,tmax=tmax,source_time=1200.,core_radius=40.,
                scheme=scheme,adaptive=True,rtol=rtol,atol=atol,max_step=max_step)
    tag=destination_tag(dx,rtol,max_step,L,radius,eps,tmax)
    sp=OUT/f'{tag}_estado.npz';rp=OUT/f'{tag}.json';pp=OUT/f'{tag}_progreso.json'
    if rp.exists():
        assert json.loads(rp.read_text())['configuration']==config
        print('REUTILIZADO',tag,flush=True);return
    if (OUT/f'{tag}_puerta_fallida.json').exists():raise RuntimeError('Failed gate: do not automatically resume')
    assert radius-40>tmax
    sim=Evolution(dx,radius,L);shape=(2,3,sim.n,sim.nm)
    t=0.;elapsed0=0.;accepted=0;nfev=0;maxe=0.;maxq=0.
    implementations=[dict(time=0.,method='numpy')]
    if sp.exists():
        with np.load(sp,allow_pickle=False) as d:
            assert json.loads(str(d['config']))==config
            q=d['q'];v=d['v'];initial_q=d['initial_q'];initial_v=d['initial_v'];rows=d['rows'].tolist()
            t=float(d['time']);elapsed0=float(d['elapsed']);transfer=json.loads(str(d['transfer']))
            accepted=int(d['accepted_steps']);nfev=int(d['nfev']);maxe=float(d['maxe']);maxq=float(d['maxq'])
            if 'implementations' in d:implementations=json.loads(str(d['implementations']))
        print('REANUDADO',tag,'tau',t,flush=True)
    else:
        q,v,transfer=seed(sim,eps);initial_q=q.copy();initial_v=v.copy();rows=[sim.measure(0,q,v)]
        save_json(OUT/f'{tag}_transferencia.json',transfer)
    if fused:
        from acelerar_fuerza_m2 import install
        audit=json.loads((OUT/'auditoria_fuerza_fusionada.json').read_text());assert audit['passed']
        method=install(sim);assert audit['source_sha256']==method['source_sha256']
        if implementations[-1]['method']!=method['method']:implementations.append(dict(time=t,**method))
    elif implementations[-1]['method']!='numpy':implementations.append(dict(time=t,method='numpy'))
    clock=time.perf_counter();end=min(tmax,stop_at) if stop_at is not None else tmax
    def checkpoint():
        tmp=sp.with_suffix('.tmp')
        with tmp.open('wb') as f:
            np.savez_compressed(f,q=q,v=v,initial_q=initial_q,initial_v=initial_v,rows=np.array(rows),time=t,
                elapsed=elapsed0+time.perf_counter()-clock,accepted_steps=accepted,nfev=nfev,maxe=maxe,maxq=maxq,
                config=json.dumps(config),transfer=json.dumps(transfer),labels=np.array(sim.labels,dtype=str),implementations=json.dumps(implementations))
        tmp.replace(sp)
        save_json(pp,dict(status='EN_PROGRESO' if t<tmax else 'EVOLUCION_TERMINADA_DIAGNOSTICO_PENDIENTE',
            time=t,source_time=1200.,accepted_steps=accepted,nfev=nfev,energy_drift=maxe,charge_drift=maxq,
            restart_file=sp.name,stage_complete=False))
    if t==0:checkpoint()
    def rhs(time_,flat):
        state=flat.reshape(shape);return np.stack([state[1],sim.force(state[0])]).ravel()
    nextobs=round(rows[-1][0]/.4+1)*.4
    while t<end-1e-10:
        bound=min(end,8*(np.floor(t/8+1e-8)+1))
        integrator=DOP853(rhs,t,np.stack([q,v]).ravel(),bound,max_step=max_step,rtol=rtol,atol=atol)
        while integrator.status=='running':
            message=integrator.step()
            if integrator.status=='failed':
                save_json(OUT/f'{tag}_fallo.json',dict(time=integrator.t,reason=message,last_valid_restart=sp.name))
                raise RuntimeError(message)
            accepted+=1;t=float(integrator.t);q,v=integrator.y.reshape(shape)
            # Check every accepted step; a sparse output cadence must not hide
            # rapid mediator oscillations in the conserved quantities.
            m=sim.measure(t,q,v);maxe=max(maxe,abs(m[1]/rows[0][1]-1));maxq=max(maxq,abs(m[2]/rows[0][2]-1))
            if not np.isfinite(m).all() or maxe>2e-4 or maxq>1e-9:
                failed=OUT/f'{tag}_estado_fallido.npz'
                np.savez_compressed(failed,q=q,v=v,time=t,config=json.dumps(config),rows=np.array(rows))
                save_json(OUT/f'{tag}_puerta_fallida.json',dict(time=t,energy_drift=maxe,charge_drift=maxq,
                    last_valid_restart=sp.name,failed_state=failed.name,physical_instability_inferred=False))
                save_json(pp,dict(status='PARCIAL',failed_time=t,restart_file=sp.name,stage_complete=False))
                raise SystemExit(2)
            if t+1e-10>=nextobs:
                dense=integrator.dense_output()
                while nextobs<=t+1e-10:
                    qo,vo=dense(min(nextobs,t)).reshape(shape)
                    rows.append(sim.measure(nextobs,qo,vo));nextobs=round(nextobs/.4+1)*.4
        nfev+=integrator.nfev;checkpoint()
        print('EVOLUCION',tag,'tau',t,'pasos',accepted,'E',maxe,'Q',maxq,'s',round(elapsed0+time.perf_counter()-clock,1),flush=True)
    if t<tmax-1e-10:print('PAUSA_REANUDABLE',tag,t,flush=True);return
    a=np.asarray(rows)
    result=dict(configuration=config,initial_energy=float(a[0,1]),initial_charge=float(a[0,2]),final_core_energy=float(a[-1,3]),
        final_core_charge=float(a[-1,4]),relative_energy_drift=maxe,relative_charge_drift=maxq,
        relative_core_charge_change=float(np.max(abs(a[:,4]/a[0,4]-1))),initial_nonradial_norm=float(a[0,5]),
        max_nonradial_norm=float(a[:,5].max()),max_amplification=float(a[:,5].max()/a[0,5]),
        mode_maxima={str(l):float(a[:,5+l].max()) for l in range(1,L+1)},
        elapsed_seconds=elapsed0+time.perf_counter()-clock,accepted_steps=accepted,nfev=nfev,
        implementations=implementations,
        balance_passed=maxe<2e-4 and maxq<1e-9,bounded_window_passed=bool(a[:,5].max()<=3*a[0,5]),
        stage_complete=False,orbital_stability_proven=False,full_angular_continuum=False,
        interpretation='Adaptive full-force refinement of finite nonradial continuation; no action change')
    save_json(rp,result)
    np.savetxt(OUT/f'{tag}_tiempo.csv',a,delimiter=',',header='tau,E_box,Q_box,E_core40,Q_core40,nonradial_norm'+''.join(f',norm_l{l}' for l in range(1,L+1)),comments='')
    save_json(pp,dict(status='CALCULO_TERMINADO',time=tmax,source_time=1200.,result=rp.name,restart_file=sp.name,stage_complete=False))
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dx',type=float,default=.5);p.add_argument('--rtol',type=float,default=1e-8)
    p.add_argument('--atol',type=float,default=1e-10);p.add_argument('--max-step',type=float,default=.02)
    p.add_argument('--L',type=int,default=4);p.add_argument('--radius',type=float,default=220.);p.add_argument('--eps',type=float,default=.02)
    p.add_argument('--tmax',type=float,default=160.);p.add_argument('--stop-at',type=float)
    p.add_argument('--fused',action='store_true',help='Use audited fused C potential with identical discrete equations')
    args=vars(p.parse_args())
    identity={k:v for k,v in args.items() if k not in ['fused','stop_at']}
    lockname='ejecucion_'+hashlib.sha256(destination_tag(**identity).encode()).hexdigest()[:16]+'.lock'
    OUT.mkdir(exist_ok=True,parents=True)
    # Kernel lock, automatically released when a Work session ends. A stale
    # file cannot block a restart; a second live writer is rejected before it
    # reads or modifies the numerical state.
    with (OUT/lockname).open('a+') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('This adaptive configuration already has a live writer')
        with threadpool_limits(limits=1):run(**args)
