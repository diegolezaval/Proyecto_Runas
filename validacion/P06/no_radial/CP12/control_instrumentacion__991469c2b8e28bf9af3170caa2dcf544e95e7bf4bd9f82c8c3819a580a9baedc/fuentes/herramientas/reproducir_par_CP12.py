"""Dos DOP853 CP10 intactos, intercalados con observadores que no los modifican."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
from scipy.integrate import DOP853
from scipy.linalg import expm
from threadpoolctl import threadpool_limits, threadpool_info
import continuar_no_radial_m2 as base
import acelerar_fuerza_m2 as accelerated
from observador_causal_CP12 import Budget, GaussResponse, terms, apply_jac, apply_jac_numpy, reference_library, gauss_table, symmetry_basis, symmetry_residual, passive_dense, interpolate, lap, model
from respuesta_forzada_chi_CP11_precisa import extended_identity
from ejecutar_con_procedencia import verify_receipt

ROOT = Path(__file__).resolve().parents[1]


def write(path, obj):
    base.save_json(path, obj)


def source_state(path):
    with np.load(path, allow_pickle=False) as z:
        return {k:z[k].copy() for k in z.files}


def reference(sim, fields):
    # Referencia extendida de la identidad cúbica, sin restar primero fuerzas en float64.
    coarse, fine, qc, qf = fields
    qi = interpolate(coarse, qc, fine)
    Y=np.asarray(fine.Y,dtype=np.longdouble);YW=np.asarray(fine.YW,dtype=np.longdouble)
    xi=np.asarray(qi,dtype=np.longdouble)@Y;xf=np.asarray(qf,dtype=np.longdouble)@Y
    mu=(xi+xf)/2;delta=xi-xf;a,b,z=mu;da,db,dz=delta
    l,g,h=map(np.longdouble,[model.quartic,model.trilinear,model.mixed])
    a2=a*a+da*da/12;b2=b*b+db*db/12;z2=z*z+dz*dz/12
    fac=2*l*(a2+b2)+g*z+h*z2/2
    aa=-fac-4*l*a2;bb=-fac-4*l*b2;ab=-4*l*(a*b+da*db/12)
    az=-g*a-h*(z*a+dz*da/12);bz=-g*b-h*(z*b+dz*db/12);zz=-h*(a2+b2)
    applied=np.array([aa*da+ab*db+az*dz,ab*da+bb*db+bz*dz,2*az*da+2*bz*db+zz*dz])@YW
    def nl(x):
        a,b,z=x;s=a*a+b*b;fac=2*l*s+g*z+h*z*z/2
        return np.array([-fac*a,-fac*b,-(g+h*z)*s])@YW
    exact=nl(xi)-nl(xf)
    weights=np.asarray(fine.w[None,:,None],dtype=np.longdouble)*np.array([2,2,1],dtype=np.longdouble)[:,None,None]
    norm=lambda x:np.sqrt(np.sum(weights*x*x))
    error=float(norm(applied-exact)/max(norm(exact),np.longdouble(1e-300)))
    lib=reference_library();quad_difference=np.empty_like(xi);quad_residual=np.empty_like(xi)
    lib.cp12_identity(fine.n*fine.Y.shape[1],np.ascontiguousarray(xi),np.ascontiguousarray(xf),quad_difference,quad_residual,model.quartic,model.trilinear,model.mixed)
    quad_error=float(norm(quad_residual@YW)/max(norm(quad_difference@YW),np.longdouble(1e-300)))
    raw,coup,jac=terms(coarse,fine,qc,qf)
    def forcing(s,q):
        a,b,z=q@s.Y
        return -((model.trilinear+model.mixed*z)*(a*a+b*b))@s.YW
    mapped=interpolate(coarse,forcing(coarse,qc),fine);fine_source=forcing(fine,qf);source=mapped-fine_source
    partition=raw[2:,0].sum(0)
    # La escala absoluta de fuerza distingue redondeo del error relativo en una diferencia pequeña.
    residual=float(np.max(abs(source-partition)))
    subtraction_scale=max(1,float(np.max(abs(source))))
    force_scale=max(1,float(np.max(abs(mapped))+np.max(abs(fine_source))))
    production_error=residual/force_scale
    trial=np.random.default_rng(20261004).normal(size=(2,3,fine.n,fine.nm))*1e-5
    jt=apply_jac(fine,jac,trial)
    jn=apply_jac_numpy(fine,jac,trial)
    equivalence=float(np.max(abs(jt-jn))/max(float(np.max(abs(jn))),1e-300))
    weight=fine.w[None,:,None]*np.array([2,2,1])[:,None,None]
    ab=float(np.sum(weight*trial[0]*jt[1]));ba=float(np.sum(weight*trial[1]*jt[0]))
    symmetry=abs(ab-ba)/max(abs(ab)+abs(ba),1e-300)
    return dict(mean_jacobian_identity_extended_relative_residual=quad_error,
                prior_longdouble_subtraction_relative_residual=error,
                weighted_jacobian_symmetry_residual=symmetry,
                fused_passive_jacobian_relative_error=equivalence,
                production_force_absolute_scaled_residual=production_error,
                production_source_residual_absolute=residual,
                production_source_difference_scaled_residual=residual/subtraction_scale,
                production_source_absolute_force_scale=force_scale,
                quad_reference_epsilon=lib.cp12_quad_epsilon(),
                extended_epsilon=float(np.finfo(np.longdouble).eps),reference_is_not_evolution=True)


class PhysicalStream:
    """Mismas operaciones y fronteras del run adaptativo CP10; ningún término nuevo."""
    def __init__(self, config, reference_data, restored=None):
        self.config=config;self.saved=reference_data;self.sim=base.Evolution(config['dx'],config['radius'],config['L'])
        standard=self.sim.force
        q,v,transfer=base.seed(self.sim,config['eps'])
        self.initial_q=q.copy();self.initial_v=v.copy();self.transfer=transfer
        if not np.array_equal(q,self.saved['initial_q']) or not np.array_equal(v,self.saved['initial_v']):
            raise ValueError('Los datos iniciales no reproducen CP10; detener antes de evolucionar')
        self.audit=accelerated.install(self.sim)
        rng=np.random.default_rng(20261002);errors=[]
        for k in range(5):
            trial=q if k==0 else q+rng.normal(size=q.shape)*1e-5
            a,b=standard(trial),self.sim.force(trial)
            errors.append(float(np.max(abs(a-b))/max(1,float(np.max(abs(a))))))
        if max(errors)>=2e-12:raise ValueError('Fuerza C/NumPy incompatible; no evolución')
        self.audit.update(errors=errors,passed=True)
        self.q,self.v=q,v;self.t=0.;self.accepted=0;self.nfev=0;self.maxe=0.;self.maxq=0.
        self.rows=[self.sim.measure(0,q,v)];self.solver=None;self.dense=None
        if restored:
            for key in ['q','v','t','accepted','nfev','maxe','maxq','rows']:setattr(self,key,restored[key])
        self.shape=(2,3,self.sim.n,self.sim.nm)
        self.nextobs=round(self.rows[-1][0]/.4+1)*.4
        if not np.array_equal(np.asarray(self.rows),self.saved['rows'][:len(self.rows)]):
            raise ValueError('Observaciones anteriores no reproducen CP10')

    def rhs(self,t,flat):
        state=flat.reshape(self.shape)
        return np.stack([state[1],self.sim.force(state[0])]).ravel()

    def advance(self,bound):
        if self.solver is None:
            c=self.config
            self.solver=DOP853(self.rhs,self.t,np.stack([self.q,self.v]).ravel(),bound,
                              max_step=c['max_step'],rtol=c['rtol'],atol=c['atol'])
        solver=self.solver;message=solver.step()
        if solver.status=='failed':raise RuntimeError(message)
        self.accepted+=1;self.t=float(solver.t);self.q,self.v=solver.y.reshape(self.shape)
        m=self.sim.measure(self.t,self.q,self.v)
        self.maxe=max(self.maxe,abs(m[1]/self.rows[0][1]-1));self.maxq=max(self.maxq,abs(m[2]/self.rows[0][2]-1))
        if not np.isfinite(m).all() or self.maxe>2e-4 or self.maxq>1e-9:raise ValueError('Balance original CP10 falló; no inferir inestabilidad física')
        if self.t+1e-10>=self.nextobs:
            dense=solver.dense_output()
            while self.nextobs<=self.t+1e-10:
                qo,vo=dense(min(self.nextobs,self.t)).reshape(self.shape)
                self.rows.append(self.sim.measure(self.nextobs,qo,vo));self.nextobs=round(self.nextobs/.4+1)*.4
        self.dense=passive_dense(solver)
        return self.dense

    def close_segment(self):
        if self.solver.status!='finished':raise ValueError('Segmento físico incompleto')
        self.nfev+=self.solver.nfev;self.solver=None;self.dense=None
        if not np.array_equal(np.asarray(self.rows),self.saved['rows'][:len(self.rows)]):
            raise ValueError('Las observaciones instrumentadas difieren de CP10; detener y diagnosticar')

    def metadata(self):
        return dict(t=self.t,accepted=self.accepted,nfev=self.nfev,maxe=self.maxe,maxq=self.maxq)


def controls(cfg,out):
    tests={};reports=[]
    data=[source_state(ROOT/p) for p in cfg['reference_states']]
    configs=cfg['physical_configurations']
    streams=[PhysicalStream(c,d) for c,d in zip(configs,data)]
    S,reduced=symmetry_basis(streams[1].sim,data[1]['initial_q'])
    tests['D2_basis_orthonormal']=np.max(abs(S.T@S-np.eye(S.shape[1])))<2e-12
    symmetry=[]
    for i,d in enumerate(data):
        for key in ['initial_q','initial_v','q','v']:
            r=symmetry_residual(streams[i].sim,S,d[key]);symmetry.append(dict(grid=configs[i]['dx'],frame=key,residual=r))
            tests[f'D2_saved_{i}_{key}']=r<2e-12
    reports.append(dict(control='simetria_semilla_antes_de_evolucion',retained_angular_dimensions=S.shape[1],measured_residuals=symmetry,derived_from_initial_state_only=True))
    tests['initial_fields_exact_CP10_both_grids']=True
    tests['C_source_and_variational_force_unchanged']=all(s.audit['passed'] for s in streams)
    for qkey in ['initial_q','q']:
        qc,qf=[d[qkey] for d in data];sc,sf=[s.sim for s in streams]
        r=reference(sf,(sc,sf,qc,qf));reports.append(dict(frame=qkey,**r))
        tests[qkey+':mean_jacobian_extended_identity']=r['mean_jacobian_identity_extended_relative_residual']<2e-12
        tests[qkey+':weighted_Jacobian_symmetry']=r['weighted_jacobian_symmetry_residual']<2e-12
        tests[qkey+':passive_C_Jacobian_equivalence']=r['fused_passive_jacobian_relative_error']<2e-12
        tests[qkey+':source_partition']=r['production_force_absolute_scaled_residual']<2e-12
        _,_,jac=terms(sc,sf,qc,qf);trial=np.random.default_rng(20261004).normal(size=(2,3,sf.n,6))*1e-5
        full=apply_jac(sf,jac,trial@S.T);small=apply_jac(reduced,jac,trial)@S.T
        tests[qkey+':D2_Jacobian_invariance']=symmetry_residual(sf,S,full)<2e-12
        tests[qkey+':D2_Jacobian_equivalence']=np.max(abs(full-small))/max(np.max(abs(full)),1e-300)<2e-12
        c=dict(configuration=configs[0],q=data[0]['q'],initial_q=data[0]['initial_q'])
        f=dict(configuration=configs[1],q=data[1]['q'],initial_q=data[1]['initial_q'],initial_v=data[1]['initial_v'])
        ci=extended_identity(c,f,sc,sf,sc.r,sf.r,sf.w,sf.r<40,qkey)
        tests[qkey+':CP11_exact_radial_defect_identity']=ci['identity_relative_residual']<2e-12
    # Un oscillator de prueba verifica que la lectura pasiva no cambia ninguna operación física.
    def rhs(t,y):return np.array([y[1],-10000*y[0]])
    a=DOP853(rhs,0,np.array([1.,0.]),.4,max_step=.02,rtol=1e-10,atol=1e-12)
    b=DOP853(rhs,0,np.array([1.,0.]),.4,max_step=.02,rtol=1e-10,atol=1e-12)
    identical=True
    while a.status=='running':
        a.step();b.step()
        before={k:getattr(b,k).copy() if isinstance(getattr(b,k),np.ndarray) else getattr(b,k) for k in ['y','f','K','K_extended','t','h_abs','nfev']}
        dense=passive_dense(b);dense((b.t_old+b.t)/2)
        identical &= all(np.asarray(getattr(b,k)).tobytes()==np.asarray(v).tobytes() for k,v in before.items())
        identical &= all(np.array_equal(getattr(a,k),getattr(b,k)) for k in ['y','f','K','t','h_abs','nfev'])
    tests['passive_dense_preserves_every_step_and_counter']=bool(identical)
    # Solución exacta matricial de un problema radial fabricado, sin evolución M2.
    sim=base.Evolution(.0625,2.,4);rng=np.random.default_rng(20261004)
    for fields in [1,3]:
        q=rng.normal(size=(fields,sim.n,sim.nm))*1e-5;v=rng.normal(size=q.shape)*1e-4
        errors=[]
        for stages in cfg['observer_stages']:
            obs=GaussResponse(sim,fields,stages,q,v)
            force=np.zeros((stages,5,fields,sim.n,sim.nm));forcing=rng.normal(size=q.shape)*1e-4
            force[:,1]=forcing
            original=np.array([q,v]);h=.003;obs.advance(h,force)
            for ell in range(5):
                selector=sim.ell==ell
                for f in range(fields):
                    matrix=np.column_stack([obs.action(np.eye(sim.n)[:,j,None]*np.ones((fields,1,sim.nm)))[f,:,np.flatnonzero(selector)[0]] for j in range(sim.n)])
                    G=np.zeros((2*sim.n+1,2*sim.n+1));G[:sim.n,sim.n:2*sim.n]=np.eye(sim.n);G[sim.n:2*sim.n,:sim.n]=-matrix
                    for channel,source in [(0,np.zeros_like(forcing)),(1,forcing)]:
                        for mode in np.flatnonzero(selector):
                            G[sim.n:2*sim.n,-1]=source[f,:,mode]
                            init=np.r_[q[f,:,mode] if channel==0 else np.zeros(sim.n),v[f,:,mode] if channel==0 else np.zeros(sim.n),1.]
                            exact=expm(h*G)@init
                            errors.append(float(np.max(abs(np.r_[obs.q[channel,f,:,mode],obs.v[channel,f,:,mode]]-exact[:-1]))))
        tests['Gauss_manufactured_fields_'+str(fields)]=max(errors)<2e-12
        reports.append(dict(control='radial_fabricado',fields=fields,maximum_absolute_error=max(errors),dx=sim.dx,radius=sim.radius,L=4,step=.003))
    # Ensayo pasivo de una sola lectura/intervalo sobre los datos iniciales ya guardados.
    sc,sf=[s.sim for s in streams];bench=dict(cfg,modal_diagnostics=False)
    budget=Budget(sc,sf,data[0]['initial_q'],data[0]['initial_v'],data[1]['initial_q'],data[1]['initial_v'],bench)
    phase_bounds=[]
    for stages in cfg['observer_stages']:
        c,b,A,_,_,_=gauss_table(stages);bounds=[];h=cfg['observer_max_step'];N=160/h
        for omega in np.linspace(0,budget.max_frequency,1001):
            z=1j*h*omega;R=1+z*(b@np.linalg.solve(np.eye(stages)-z*A,np.ones(stages)))
            bounds.append(float(abs(np.angle(R)-h*omega)*N+abs(abs(R)-1)*N))
        phase_bounds.append(dict(stages=stages,maximum_free_global_phase_modulus_bound=max(bounds),maximum_frequency=budget.max_frequency,step=h,time=160))
    tests['passive_free_propagation_global_bound']=max(p['maximum_free_global_phase_modulus_bound'] for p in phase_bounds)<=1e-4
    reports.extend(phase_bounds)
    dense=[lambda t,d=d:np.stack([d['initial_q'],d['initial_v']]).ravel() for d in data]
    clock=time.perf_counter();budget.advance(0,.003,dense[0],dense[1],streams[0].shape,streams[1].shape)
    reports.append(dict(control='coste_observacion_pasiva_estado_fijo',wall_seconds=time.perf_counter()-clock,interval=.003,
                        measured_only=True,M2_integration_steps=0,maximum_iterations=max(o.max_iterations for o in budget.coupled),
                        observer_timings=[dict(fields=o.fields,stages=o.stages,timings=o.timings) for o in budget.raw+budget.coupled]))
    tests['longdouble_exceeds_float64']=np.finfo(np.longdouble).eps<np.finfo(float).eps
    pools=threadpool_info();tests['observed_threads_one']=bool(pools) and all(p['num_threads']==1 for p in pools)
    tests={key:bool(value) for key,value in tests.items()}
    result=dict(passed=all(tests.values()),tests=tests,algebra=reports,force_audits=[s.audit for s in streams],
                observed_threadpools=pools,new_M2_evolution_steps=0,physical_gate_threshold=.02,
                scope='Pruebas de implementación sobre datos existentes y soluciones fabricadas; no evolución ni aceptación M2.')
    write(out/'resultados.json',result)
    if not result['passed']:raise ValueError('Control de instrumentación falló; no iniciar M2')
    return result


def restart_write(out,streams,budget,cfg,time_):
    rows=np.column_stack([np.asarray(streams[0].rows),np.asarray(streams[1].rows)[:,1:]])
    data=dict(q=np.concatenate([s.q for s in streams],axis=1),v=np.concatenate([s.v for s in streams],axis=1),
              initial_q=np.concatenate([s.initial_q for s in streams],axis=1),initial_v=np.concatenate([s.initial_v for s in streams],axis=1),
              rows=rows,time=time_,config=json.dumps(cfg),metadata=json.dumps([s.metadata() for s in streams]),
              coarse_n=streams[0].sim.n,schema='CP12_DOS_MALLAS_Y_OBSERVADORES_PASIVOS',
              budget_rows=json.dumps(budget.rows),budget_algebra=json.dumps(budget.algebra),
              maximum_errors=json.dumps(budget.maximum_errors),max_step_phase=budget.max_step_phase,
              coupled_angular_basis=budget.S,maximum_symmetry_residual=budget.maximum_symmetry_residual)
    for name,family in [('raw',budget.raw),('coupled',budget.coupled)]:
        for index,obs in enumerate(family):
            data[f'{name}_{index}_q']=obs.q;data[f'{name}_{index}_v']=obs.v
            data[f'{name}_{index}_iterations']=obs.max_iterations
    destination=out/'CP12_par_estado.npz';temporary=destination.with_suffix('.tmp')
    with temporary.open('wb') as stream:np.savez_compressed(stream,**data)
    temporary.replace(destination)
    write(out/'CP12_par_progreso.json',dict(status='EN_PROGRESO' if time_<160 else 'EVOLUCION_TERMINADA_DIAGNOSTICO_PENDIENTE',time=time_,restart_file=destination.name,stage_complete=False,configuration=cfg))


def run_pair(cfg,out,stop_at=None):
    control=[p for p in (ROOT/cfg['control_directory']).glob('control_instrumentacion__*/resultados.json') if json.loads(p.read_text())['passed']]
    if not control:raise ValueError('Control previo ausente o negativo')
    matching=[]
    for candidate in control:
        receipt=json.loads((candidate.parent/'procedencia.json').read_text())
        if all((ROOT/p).is_file() and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==expected for p,expected in receipt['identity']['code_hashes'].items()):matching.append(candidate)
    if len(matching)!=1:raise ValueError('Control positivo no corresponde al código actual o es ambiguo')
    control=matching
    if not verify_receipt(control[0].parent/'procedencia.json')['passed']:raise ValueError('Control previo sin integridad')
    states=[source_state(ROOT/p) for p in cfg['reference_states']]
    restored=None;start=0.;history=None
    path=out/'CP12_par_estado.npz'
    if path.is_file():
        history=source_state(path);start=float(history['time']);meta=json.loads(str(history['metadata']));n=int(history['coarse_n'])
        if json.loads(str(history['config']))!=cfg:raise ValueError('Configuración de reinicio cambiada')
        if str(history['schema'])!='CP12_DOS_MALLAS_Y_OBSERVADORES_PASIVOS' or start%8 or any(m['t']!=start for m in meta):raise ValueError('Frontera o esquema de reinicio incompatibles')
        for name in ['raw','coupled']:
            for i in [0,1]:
                for field in ['q','v']:
                    if not np.isfinite(history[f'{name}_{i}_{field}']).all():raise ValueError('Observador no finito; no reanudar')
        restored=[]
        for index,use in enumerate([slice(0,n),slice(n,None)]):
            item=dict(meta[index],q=history['q'][:,use],v=history['v'][:,use],rows=history['rows'][:,:10].tolist() if index==0 else np.column_stack([history['rows'][:,0],history['rows'][:,10:]]).tolist())
            restored.append(item)
    streams=[PhysicalStream(c,d,None if restored is None else restored[i]) for i,(c,d) in enumerate(zip(cfg['physical_configurations'],states))]
    sc,sf=[s.sim for s in streams]
    budget=Budget(sc,sf,streams[0].initial_q,streams[0].initial_v,streams[1].initial_q,streams[1].initial_v,cfg)
    if history:
        budget.rows=json.loads(str(history['budget_rows']));budget.algebra=json.loads(str(history['budget_algebra']));budget.maximum_errors=json.loads(str(history['maximum_errors']));budget.max_step_phase=float(history['max_step_phase'])
        if not np.array_equal(budget.S,history['coupled_angular_basis']):raise ValueError('Base pasiva de reinicio distinta')
        budget.maximum_symmetry_residual=float(history['maximum_symmetry_residual'])
        if budget.rows[-1]['time']!=start or max(budget.maximum_errors.values())>cfg['observer_relative_tolerance']:raise ValueError('Presupuesto de reinicio inválido')
        for name,family in [('raw',budget.raw),('coupled',budget.coupled)]:
            for i,obs in enumerate(family):obs.q=history[f'{name}_{i}_q'];obs.v=history[f'{name}_{i}_v'];obs.max_iterations=int(history[f'{name}_{i}_iterations'])
    else:
        budget.record(0.,streams[0].q,streams[0].v,streams[1].q,streams[1].v)
        restart_write(out,streams,budget,cfg,0.)
    clock=time.perf_counter();end=min(160.,stop_at) if stop_at is not None else 160.
    if end%8:raise ValueError('Pausa sólo en fronteras originales de ocho unidades')
    t=start;next_record=round(t/.4+1)*.4;observer_step=cfg['observer_max_step']
    while t<end-1e-10:
        bound=min(end,8*(np.floor(t/8+1e-8)+1));dense=[s.advance(bound) for s in streams]
        while t<bound-1e-12:
            right=min(round((round(t/observer_step)+1)*observer_step,12),next_record,bound)
            histories=[]
            for i,s in enumerate(streams):
                pieces=[dense[i]]
                while pieces[-1].t_max<right-1e-12:pieces.append(s.advance(bound))
                dense[i]=pieces[-1]
                ends=np.array([d.t_max for d in pieces])
                def history(time,pieces=pieces,ends=ends):return pieces[min(int(np.searchsorted(ends,time)),len(pieces)-1)](time)
                histories.append(history)
            if right>t+1e-14:budget.advance(t,right,histories[0],histories[1],streams[0].shape,streams[1].shape)
            t=float(right)
            if t>=next_record-1e-12:
                c=histories[0](t).reshape(streams[0].shape);f=histories[1](t).reshape(streams[1].shape)
                budget.record(t,c[0],c[1],f[0],f[1]);next_record=round(next_record/.4+1)*.4
        for s in streams:s.close_segment()
        check=reference(sf,(sc,sf,streams[0].q,streams[1].q));budget.algebra.append(dict(time=t,**check))
        restart_write(out,streams,budget,cfg,t)
        write(out/'presupuesto_parcial.json',dict(time=t,latest=budget.rows[-1],maximum_errors=budget.maximum_errors,
              extended_identity=check,original_observations_reproduced=True,physical_steps=[s.accepted for s in streams],
              original_nfev=[s.nfev for s in streams],wall_seconds=time.perf_counter()-clock,physical_gate_threshold=.02))
        print(json.dumps(dict(time=t,physical_steps=[s.accepted for s in streams],maximum_errors=budget.maximum_errors,wall_seconds=round(time.perf_counter()-clock,1)),ensure_ascii=False),flush=True)
        if check['mean_jacobian_identity_extended_relative_residual']>=2e-12:raise ValueError('Identidad extendida no cerrada; detener atribución')
        if check['weighted_jacobian_symmetry_residual']>=2e-12 or check['production_force_absolute_scaled_residual']>=2e-12:raise ValueError('Simetría o partición de fuente no cerrada')
        if budget.maximum_errors.get('modal_parseval',0)>2e-11:raise ValueError('Parseval modal no cerrado; no atribuir')
        if max(budget.maximum_errors.values())>cfg['observer_relative_tolerance']:raise ValueError('Observadores o control temporal no cierran; preservar y detener')
    if t<160-1e-10:return dict(status='PAUSADA_REANUDABLE',time=t)
    reproductions=[]
    for s,label in zip(streams,['coarse','fine']):
        tests={k:bool(np.array_equal(getattr(s,k),s.saved[k])) for k in ['q','v','initial_q','initial_v']}
        tests['rows']=bool(np.array_equal(np.asarray(s.rows),s.saved['rows']))
        tests['accepted_steps']=s.accepted==int(s.saved['accepted_steps']);tests['nfev']=s.nfev==int(s.saved['nfev'])
        tests['maxe']=s.maxe==float(s.saved['maxe']);tests['maxq']=s.maxq==float(s.saved['maxq'])
        reproductions.append(dict(grid=s.config['dx'],passed=all(tests.values()),tests=tests,metadata=s.metadata()))
        np.savez_compressed(out/(label+'_final.npz'),q=s.q,v=s.v,initial_q=s.initial_q,initial_v=s.initial_v,rows=np.asarray(s.rows),time=160.,config=json.dumps(s.config))
    result=dict(configuration=cfg,status='PRESUPUESTO_CAUSAL_PENDIENTE_DE_INTERPRETACION',time=160.,
                reproductions=reproductions,reproduces_CP10_exactly=all(r['passed'] for r in reproductions),
                observer_checks_passed=max(budget.maximum_errors.values())<=cfg['observer_relative_tolerance'],
                maximum_errors=budget.maximum_errors,maximum_step_frequency_product=budget.max_step_phase,
                maximum_symmetry_residual=budget.maximum_symmetry_residual,
                final=budget.rows[-1],new_M2_evolutions=2,physical_gate_threshold=.02,
                physical_gate='REFINAMIENTO_PENDIENTE',correction_tested=False,cause_certified=False,
                only_authorized_CP10_trajectories_reproduced=True,observed_threadpools=threadpool_info())
    write(out/'CP12_par.json',result);write(out/'serie_presupuestos.json',budget.rows)
    write(out/'identidades_algebraicas.json',budget.algebra)
    cq,cv=budget.family_arrays('coupled',0);bq,bv=budget.family_arrays('coupled',1)
    np.savez_compressed(out/'respuestas_finales.npz',raw_q=budget.raw[0].q,raw_v=budget.raw[0].v,
                        coupled_q=cq,coupled_v=cv,coupled_angular_basis=budget.S,
                        raw_control_q=budget.raw[1].q,raw_control_v=budget.raw[1].v,
                        coupled_control_q=bq,coupled_control_v=bv)
    if not result['reproduces_CP10_exactly']:raise ValueError('CP10 no reproducido exactamente: diagnóstico causal detenido')
    write(out/'CP12_par_progreso.json',dict(status='CALCULO_TERMINADO',time=160.,restart_file='CP12_par_estado.npz',result='CP12_par.json',stage_complete=False))
    np.savetxt(out/'CP12_par_tiempo.csv',np.column_stack([np.asarray(streams[0].rows),np.asarray(streams[1].rows)[:,1:]]),delimiter=',',header='tau,coarse_observables_1_9,fine_observables_1_9')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--stop-at',type=float)
    a=p.parse_args();case=json.loads(a.config.read_text())['case'];a.output_dir.mkdir(parents=True,exist_ok=True)
    with threadpool_limits(limits=1):
        if case['operation']=='control_pasivo_sin_evolucion_M2':result=controls(case['configuration'],a.output_dir)
        else:result=run_pair(case['configuration'],a.output_dir,a.stop_at)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
