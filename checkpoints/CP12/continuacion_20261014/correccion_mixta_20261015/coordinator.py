"""Independent MIXTO trial: unchanged M2, original Cauchy data and CP12 observers.

MIXTO denotes the fixed positive polynomial composition, not a global-order claim.
Every certified boundary is preserved, independently retrieved and audited.
"""
from pathlib import Path
import argparse, datetime, fcntl, hashlib, importlib.util, json, os, shutil
import subprocess, sys, threading, traceback, zipfile

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    def scalar(v):
        import numpy as np
        if isinstance(v,np.generic):return v.item()
        raise TypeError(type(v).__name__)
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False,default=scalar)+'\n')
    with temp.open('rb') as f:os.fsync(f.fileno())
    temp.replace(p)
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def event(home,name,**data):
    value=dict(at=now(),event=name,**data)
    with (home/'runtime/events.jsonl').open('a') as f:
        f.write(json.dumps(value,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value,ensure_ascii=False),flush=True)

def setup(home):
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    assert not os.environ.get('OPENBLAS_CORETYPE')
    info=read(home/'preregistration/ubicacion.json');meta=read(home/'preregistration/nueva_identidad.json')
    root=home/'science';ident=read(home/'preregistration/identidad_cientifica_original.json')
    for n,h in {**ident['code_hashes'],**ident['input_hashes']}.items():assert sha(root/n)==h,n
    assert len(ident['code_hashes'])==14
    for n,h in meta['captured_sources'].items():assert sha(home/n)==h,n
    assert sha(home/'coordinator.py')==meta['supervision_source_sha256']
    registration=read(home/'preregistration/registro_publico.json')
    assert registration['registered_before_M2'] and registration['captured_sources']==meta['captured_sources']
    sys.path.insert(0,str(root/'herramientas'));sys.path.insert(0,str(home/'candidate'))
    import numpy as np
    from threadpoolctl import threadpool_info
    import continuar_no_radial_m2 as base
    import acelerar_fuerza_m2 as accelerated
    import observador_causal_CP12 as obs
    import reproducir_par_CP12 as native
    from ejecutar_con_procedencia import environment
    from mixed_backend import Mixed as Candidate, MixedGauss, lap_mixed
    assert all(x['architecture']=='SkylakeX' and x['num_threads']==1 for x in threadpool_info())
    assert environment()==ident['environment'],'Original recorded numerical environment changed'
    cache=home/'runtime/force';cache.mkdir(parents=True,exist_ok=True);accelerated.OUT=cache
    obs.lap=lap_mixed;obs.GaussResponse=MixedGauss
    cfg=read(home/'configuration.json')['original_configuration']
    expected=read(root/'datos/ensayo_causal_chi_CP12.json')['cases']['par_instrumentado']['configuration']
    assert cfg==expected
    return info,meta,root,home/'outputs',None,None,dict(np=np,base=base,accelerated=accelerated,obs=obs,native=native,Candidate=Candidate,cfg=cfg)

def streams_and_budget(home,restore=True):
    info,meta,root,out,_,_,modules=setup(home)
    np=modules['np'];base=modules['base'];native=modules['native'];obs=modules['obs'];Candidate=modules['Candidate'];cfg=modules['cfg']
    references=[native.source_state(root/p) for p in cfg['reference_states']]
    path=out/'MIXTO_par_estado.npz';saved=None
    if restore and path.exists():
        with np.load(path,allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    class Stream(native.PhysicalStream):
        def __init__(self,c,reference,index):
            self.config=c;self.sim=Candidate(c['dx'],c['radius'],c['L']);self.original_sim=base.Evolution(c['dx'],c['radius'],c['L'])
            q,v,self.transfer=base.seed(self.sim,c['eps'])
            assert np.array_equal(q,reference['initial_q']) and np.array_equal(v,reference['initial_v'])
            self.initial_q=q.copy();self.initial_v=v.copy()
            method=modules['accelerated'].install(self.sim)
            assert method['source_sha256']==read(home/'preregistration/identidad_cientifica_original.json')['code_hashes']['herramientas/fuerza_potencial_m2.c']
            self.q,self.v=q,v;self.t=0.;self.accepted=0;self.nfev=0;self.maxe=0.;self.maxq=0.;self.maxe_original=0.
            self.rows=[self.sim.measure(0,q,v)];self.original_rows=[self.original_sim.measure(0,q,v)]
            assert np.array_equal(np.asarray(self.original_rows[0]),reference['rows'][0])
            self.shape=(2,3,self.sim.n,self.sim.nm);self.solver=None;self.dense=None
            if saved:
                n=int(saved['coarse_n']);use=slice(0,n) if index==0 else slice(n,None)
                self.q=saved['q'][:,use].copy();self.v=saved['v'][:,use].copy()
                old=json.loads(str(saved['metadata']))[index]
                for k in ('t','accepted','nfev','maxe','maxq','maxe_original'):setattr(self,k,old[k])
                def rows(key):return saved[key][:,:10].tolist() if index==0 else np.column_stack([saved[key][:,0],saved[key][:,10:]]).tolist()
                self.rows=rows('consistent_rows');self.original_rows=rows('rows')
                assert np.array_equal(saved['initial_q'][:,use],self.initial_q) and np.array_equal(saved['initial_v'][:,use],self.initial_v)
            self.nextobs=round(self.rows[-1][0]/.4+1)*.4
        def advance(self,bound):
            previous=len(self.rows);dense=super().advance(bound)
            m=self.original_sim.measure(self.t,self.q,self.v)
            self.maxe_original=max(self.maxe_original,abs(m[1]/self.original_rows[0][1]-1))
            if not np.isfinite(m).all() or self.maxe_original>2e-4:raise ValueError('Original FV energy gate failed for MIXTO; preserve without promoting the consistent-energy result')
            for row in self.rows[previous:]:
                q,v=dense(min(row[0],self.t)).reshape(self.shape)
                self.original_rows.append(self.original_sim.measure(row[0],q,v))
            return dense
        def close_segment(self):
            assert self.solver.status=='finished';self.nfev+=self.solver.nfev;self.solver=None;self.dense=None
        def metadata(self):return dict(t=self.t,accepted=self.accepted,nfev=self.nfev,nfev_live=0 if self.solver is None else self.solver.nfev,maxe=self.maxe,maxq=self.maxq,maxe_original=self.maxe_original)
    streams=[Stream(c,r,i) for i,(c,r) in enumerate(zip(cfg['physical_configurations'],references))]
    budget=obs.Budget(streams[0].sim,streams[1].sim,streams[0].initial_q,streams[0].initial_v,streams[1].initial_q,streams[1].initial_v,cfg)
    if saved:
        assert str(saved['schema'])=='CP12_MIXTO_NEW_EXPERIMENT_ORIGINAL_OBSERVER_EQUATIONS'
        assert json.loads(str(saved['config']))==cfg and str(saved['experiment_id'])==meta['execution_run_id']
        budget.rows=json.loads(str(saved['budget_rows']));budget.algebra=json.loads(str(saved['budget_algebra']));budget.maximum_errors=json.loads(str(saved['maximum_errors']));budget.max_step_phase=float(saved['max_step_phase'])
        budget.maximum_symmetry_residual=float(saved['maximum_symmetry_residual'])
        assert np.array_equal(budget.S,saved['coupled_angular_basis'])
        for name,family in [('raw',budget.raw),('coupled',budget.coupled)]:
            for i,o in enumerate(family):o.q=saved[f'{name}_{i}_q'].copy();o.v=saved[f'{name}_{i}_v'].copy();o.max_iterations=int(saved[f'{name}_{i}_iterations'])
    else:budget.record(0.,streams[0].q,streams[0].v,streams[1].q,streams[1].v)
    return modules,streams,budget

def save_state(home,streams,budget):
    np=__import__('numpy');meta=read(home/'preregistration/nueva_identidad.json');cfg=read(home/'configuration.json')['original_configuration'];out=home/'outputs';t=streams[0].t
    assert all(s.t==t for s in streams)
    data=dict(q=np.concatenate([s.q for s in streams],axis=1),v=np.concatenate([s.v for s in streams],axis=1),initial_q=np.concatenate([s.initial_q for s in streams],axis=1),initial_v=np.concatenate([s.initial_v for s in streams],axis=1),rows=np.column_stack([np.asarray(streams[0].original_rows),np.asarray(streams[1].original_rows)[:,1:]]),consistent_rows=np.column_stack([np.asarray(streams[0].rows),np.asarray(streams[1].rows)[:,1:]]),time=t,config=json.dumps(cfg),metadata=json.dumps([s.metadata() for s in streams]),coarse_n=streams[0].sim.n,schema='CP12_MIXTO_NEW_EXPERIMENT_ORIGINAL_OBSERVER_EQUATIONS',experiment_id=meta['execution_run_id'],candidate_action='Phi_original_FV_chi_fixed_K2_plus_h2_over_12_K2_Winv_K2',budget_rows=json.dumps(budget.rows),budget_algebra=json.dumps(budget.algebra),maximum_errors=json.dumps(budget.maximum_errors),max_step_phase=budget.max_step_phase,coupled_angular_basis=budget.S,maximum_symmetry_residual=budget.maximum_symmetry_residual)
    for name,family in [('raw',budget.raw),('coupled',budget.coupled)]:
        for i,o in enumerate(family):data[f'{name}_{i}_q']=o.q;data[f'{name}_{i}_v']=o.v;data[f'{name}_{i}_iterations']=o.max_iterations
    path=out/'MIXTO_par_estado.npz';temp=path.with_suffix('.tmp')
    with temp.open('wb') as f:np.savez_compressed(f,**data)
    temp.replace(path)
    write(out/'progreso.json',dict(time=t,status='FRONTERA_PENDIENTE_DE_AUDITORIA',candidate='MIXTO',CP12_closed=False,correction_validated=False))
    receipt=read(out/'procedencia.json')
    if receipt['segments']:
        receipt['segments'][-1].update(ended_at=now(),status='FRONTERA_ESCRITA_PENDIENTE_DE_AUDITORIA',time=t,state_sha256=sha(path),accepted_steps=[s.accepted for s in streams],nfev=[s.nfev for s in streams])
    receipt.update(time=t,status='PAUSADA_REANUDABLE' if t<160 else 'EVOLUCION_COMPLETA_PENDIENTE_DE_VALIDACION',physical_accepted_steps=[s.accepted for s in streams],original_CP10_reproduction=False,output_hashes={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='procedencia.json' and p.suffix!='.tmp'});write(out/'procedencia.json',receipt)

def audit(home,t):
    info,meta,root,out,_,_,modules=setup(home);np=modules['np'];state=out/'MIXTO_par_estado.npz';before=sha(state)
    receipt=read(out/'procedencia.json');tests={}
    tests['own_receipt_and_all_output_hashes']=receipt['execution_run_id']==meta['execution_run_id'] and receipt['time']==t and all(sha(out/n)==h for n,h in receipt['output_hashes'].items())
    tests['original_fourteen_sources_and_all_inputs_unchanged']=True;tests['captured_candidate_and_administrative_sources_unchanged']=True
    tests['original_M2_Theta_two_grids_solver_tolerances_and_observer_configuration']=True
    modules,streams,budget=streams_and_budget(home)
    with np.load(state,allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    tests['new_experiment_schema_and_identity']=str(saved['schema'])=='CP12_MIXTO_NEW_EXPERIMENT_ORIGINAL_OBSERVER_EQUATIONS' and str(saved['experiment_id'])==meta['execution_run_id']
    tests['time_original_eight_unit_boundary']=float(saved['time'])==t and t%8==0 and all(s.t==t for s in streams)
    tests['original_CP10_Cauchy_data_exact']=True
    from continuar_no_radial_m2 import Evolution
    from operador import Candidate as AllK4
    from mixed_backend import lap_mixed, MixedGauss
    tests['Phi_FV_chi_K4_physical_routing_exact']=all(np.array_equal(s.sim.lap(s.q)[:2],Evolution.lap(s.sim,s.q)[:2]) and np.array_equal(s.sim.lap(s.q)[2:3],AllK4.lap(s.sim,s.q[2:3])) for s in streams)
    tests['mixed_passive_routing_exact']=all(np.array_equal(lap_mixed(s.sim,s.q),s.sim.lap(s.q)) for s in streams)
    tests['mixed_observer_class_selected']=all(isinstance(o,MixedGauss) for family in (budget.raw,budget.coupled) for o in family)
    tests['initial_or_closed_segment_evaluation_accounting']=all(s.solver is None and s.nfev>=s.accepted for s in streams)
    tests['current_original_and_mixed_energy_rows_reproduced']=all(np.allclose(np.asarray(s.original_rows[-1]),np.asarray(s.original_sim.measure(t,s.q,s.v)),rtol=2e-12,atol=2e-12) and np.allclose(np.asarray(s.rows[-1]),np.asarray(s.sim.measure(t,s.q,s.v)),rtol=2e-12,atol=2e-12) for s in streams)
    tests['finite_physical_and_observer_arrays']=all(np.isfinite(saved[k]).all() for k in ('q','v','initial_q','initial_v','rows','consistent_rows',*[f'{n}_{i}_{f}' for n in ('raw','coupled') for i in (0,1) for f in ('q','v')]))
    tests['observation_count_and_original_time_labels']=len(saved['rows'])==int(t*2.5+1) and np.array_equal(saved['rows'][:,0],np.arange(int(t*2.5+1))*.4) and np.array_equal(saved['consistent_rows'][:,0],saved['rows'][:,0])
    tests['budget_count_and_time_labels']=len(budget.rows)==len(saved['rows']) and np.allclose(np.asarray([r['time'] for r in budget.rows]),saved['rows'][:,0],rtol=0,atol=1e-12)
    tests['original_FV_energy_gate']=all(s.maxe_original<=2e-4 for s in streams)
    tests['consistent_MIXTO_energy_gate']=all(s.maxe<=2e-4 for s in streams)
    tests['original_charge_gate']=all(s.maxq<=1e-9 for s in streams)
    tests['original_observer_closure_and_order_gates']=max(budget.maximum_errors.values(),default=0)<=.001
    tests['original_Parseval_gate']=budget.maximum_errors.get('modal_parseval',0)<=2e-11
    tests['original_symmetry_gate']=budget.maximum_symmetry_residual<=2e-12
    tests['original_angular_basis_exact_on_restart']=np.array_equal(budget.S,saved['coupled_angular_basis'])
    old_rows=len(budget.rows);budget.record(t,streams[0].q,streams[0].v,streams[1].q,streams[1].v)
    tests['independent_reloaded_observer_closure_and_order']=max(budget.rows[-1]['verification'].values())<=.001
    tests['independent_reloaded_Parseval']=budget.rows[-1]['short_modes']['parseval_relative_residual']<=2e-11
    obs=modules['obs'];sc,sf=[s.sim for s in streams];qc,qf=[s.q for s in streams]
    extended=modules['native'].reference(sf,(sc,sf,qc,qf))
    tests['original_extended_force_identity_and_symmetry']=all(extended[k]<=2e-12 for k in ('mean_jacobian_identity_extended_relative_residual','weighted_jacobian_symmetry_residual','fused_passive_jacobian_relative_error','production_force_absolute_scaled_residual'))
    qi=obs.interpolate(sc,qc,sf);delta=qi-qf;raw,coupled,jac=obs.terms(sc,sf,qc,qf)
    lhs=obs.interpolate(sc,sc.force(qc),sf)-sf.force(qf)
    masses=np.array([obs.model.mass2,obs.model.mass2,obs.model.mediator**2])[:,None,None]
    comm=obs.interpolate(sc,obs.lap(sc,qc),sf)-obs.lap(sf,qi)
    rhs=obs.lap(sf,delta)-masses*delta+comm+coupled[3:].sum(0)+obs.apply_jac(sf,jac,delta[None])[0]
    scale=max(1.,float(np.max(abs(obs.interpolate(sc,sc.force(qc),sf)))+np.max(abs(sf.force(qf)))))
    full_identity=float(np.max(abs(lhs-rhs))/scale)
    tests['MIXTO_full_instantaneous_defect_identity_original_force_scale']=full_identity<=2e-12
    dq=obs.interpolate(sc,streams[0].q,sf)-streams[1].q;dv=obs.interpolate(sc,streams[0].v,sf)-streams[1].v
    full=lambda q,v:float(np.sum(sf.w[:,None]*(q*q+v*v/obs.model.mediator**2)))
    closures={}
    for name in ('raw','coupled'):
        q,v=budget.family_arrays(name,0);f=0 if name=='raw' else 2
        closures[name]=float(np.sqrt(full(dq[2]-q[:,f].sum(0),dv[2]-v[:,f].sum(0))/max(full(dq[2],dv[2]),1e-300)))
    tests['original_full_box_chi_closure_gate']=max(closures.values())<=.001
    tests['zero_M2_restart_no_state_mutation']=sha(state)==before
    report=dict(schema='CP12_MIXTO_CORRECTION_TRIAL_ZERO_STEP_AUDIT',time=t,passed=all(tests.values()),tests=tests,state_sha256=before,configuration_sha256=sha(home/'configuration.json'),receipt_sha256=sha(out/'procedencia.json'),observation_count=len(saved['rows']),metadata=[s.metadata() for s in streams],maximum_errors=json.loads(str(saved['maximum_errors'])),extended_identity=extended,full_instantaneous_identity=full_identity,full_box_chi_closure=closures,observed_core_phase_relative_error=budget.rows[-1]['observed_relative_error'],M2_steps_executed=0,experiment_kind='NEW_MIXTO_DISCRETIZATION_TRIAL',correction_tested=t>0,correction_validated=False,CP12_closed=False,run_id=meta['execution_run_id'],execution_uuid=info['execution_uuid'],original_trajectories_repeated=False)
    if not report['passed']:raise ValueError(json.dumps(report,default=lambda x:x.item()))
    return report

def preservation_module(home):
    module=load_module('captured_MIXTO_preservation',home/'preservation.py');module.setup=setup;module.audit=audit;return module

def advance_segment(home,target,progress):
    modules,streams,budget=streams_and_budget(home);np=modules['np'];cfg=modules['cfg'];native=modules['native'];start=streams[0].t
    progress.update(observer_clock=start,streams=streams)
    try:
        t=start;next_record=round(t/.4+1)*.4;observer_step=cfg['observer_max_step'];dense=[s.advance(target) for s in streams]
        while t<target-1e-12:
            right=min(round((round(t/observer_step)+1)*observer_step,12),next_record,target);histories=[]
            for i,s in enumerate(streams):
                pieces=[dense[i]]
                while pieces[-1].t_max<right-1e-12:pieces.append(s.advance(target))
                dense[i]=pieces[-1];ends=np.array([d.t_max for d in pieces])
                def history(time,pieces=pieces,ends=ends):return pieces[min(int(np.searchsorted(ends,time)),len(pieces)-1)](time)
                histories.append(history)
            if right>t+1e-14:budget.advance(t,right,histories[0],histories[1],streams[0].shape,streams[1].shape)
            t=float(right);progress['observer_clock']=t
            if t>=next_record-1e-12:
                c=histories[0](t).reshape(streams[0].shape);f=histories[1](t).reshape(streams[1].shape)
                budget.record(t,c[0],c[1],f[0],f[1]);next_record=round(next_record/.4+1)*.4
                if budget.maximum_errors.get('modal_parseval',0)>2e-11 or max(budget.maximum_errors.values(),default=0)>.001:raise ValueError('Original observer gate failed for MIXTO')
        for s in streams:s.close_segment()
        check=native.reference(streams[1].sim,(streams[0].sim,streams[1].sim,streams[0].q,streams[1].q));budget.algebra.append(dict(time=t,**check))
        save_state(home,streams,budget)
        return dict(time=t,metadata=[s.metadata() for s in streams],maximum_errors=budget.maximum_errors)
    except BaseException:
        failed=home/'negative'/('segment_%04d'%target);failed.mkdir(parents=True,exist_ok=False)
        data={f'grid_{i}_{k}':getattr(s,k) for i,s in enumerate(streams) for k in ('q','v','initial_q','initial_v')}
        data.update(physical_metadata=json.dumps([s.metadata() for s in streams]),budget_rows=json.dumps(budget.rows),budget_maximum_errors=json.dumps(budget.maximum_errors),coupled_angular_basis=budget.S)
        for name,family in [('raw',budget.raw),('coupled',budget.coupled)]:
            for i,o in enumerate(family):data[f'{name}_{i}_q']=o.q;data[f'{name}_{i}_v']=o.v
        np.savez_compressed(failed/'failed_physical_and_observer_state.npz',**data)
        write(failed/'FAILURE.json',dict(status='SCIENTIFIC_TRIAL_STOPPED',target=target,observer_clock=progress.get('observer_clock'),metadata=[s.metadata() for s in streams],traceback=traceback.format_exc(),maximum_errors=budget.maximum_errors,failed_state_is_certified_frontier=False,correction_validated=False,CP12_closed=False))
        raise

def preserve_negative(home,label,reason,negative=True):
    """Retrieve complete additional evidence; never certify it as a frontier."""
    module=preservation_module(home);info=read(home/'preregistration/ubicacion.json')
    payload=home/'negative'/label;payload.mkdir(parents=True,exist_ok=True)
    write(payload/'reason.json',dict(reason=reason,scope='Additional trial evidence; no new certified scientific frontier',scientific_gate_failed=negative,CP12_closed=False))
    files=[p for p in sorted(home.rglob('*')) if p.is_file() and not any(x in ('runtime','capsules','recoveries','__pycache__','cache') for x in p.relative_to(home).parts) and p.suffix not in ('.tmp','.pyc','.so')]
    manifest={'schema':'CP12_MIXTO_ADDITIONAL_EVIDENCE_NOT_VALIDATED_FRONTIER','scientific_gate_failed':negative,'files':{p.relative_to(home).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in files},'CP12_closed':False}
    archive=home/'capsules'/('CP12_CANDIDATO_MIXTO_'+info['execution_uuid']+'_'+label+'.zip');assert not archive.exists()
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,p.relative_to(home).as_posix())
        z.writestr('MANIFIESTO_NEGATIVO.json',json.dumps(manifest,indent=2)+'\n')
    expected=sha(archive);size=archive.stat().st_size
    raw=module.helper(home,'library_upload.py',[],{'uploads':[{'local_path':str(archive),'purpose':'create_library_file','library_artifact_type':'other'}]})
    uploaded=json.loads(raw[raw.rfind('\n{"results"'):].strip() if '\n{"results"' in raw else raw)['results'];assert len(uploaded)==1 and uploaded[0]['status']=='succeeded';item=uploaded[0]
    sys.path.insert(0,str(home/'runtime/library'));from library_hosted_apps import HostedAppsClient
    transfers=module.unpack(HostedAppsClient().call_tool('connector_openai_library','prepare_materialize',{'items':[{'file_id':item['file_id'],'library_file_id':item['library_file_id'],'file_name':item['file_name']}],'destination':{'directory':str(home/'recoveries'/label/'download')}}))
    assert len(transfers.get('transfers',[]))==1 and not transfers.get('unavailable_items');tr=transfers['transfers'][0]
    if tr.get('workspace_path'):
        downloaded=Path(tr['workspace_path']);module.helper(home,'library_file_transfer.py',['apply-xattrs',str(downloaded),tr['library_file_id']],tr.get('xattrs',[]))
    else:
        downloaded=home/'recoveries'/label/'download'/item['file_name'];module.helper(home,'library_file_transfer.py',['materialize',str(downloaded)],tr)
    assert downloaded.stat().st_size==size and sha(downloaded)==expected and archive.stat().st_size==size and sha(archive)==expected
    with zipfile.ZipFile(downloaded) as z:
        assert set(z.namelist())==set(manifest['files'])|{'MANIFIESTO_NEGATIVO.json'}
        for n,v in manifest['files'].items():
            data=z.read(n);assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
    write(home/'proofs'/(label+'_permanent.json'),dict(passed=True,scope='Additional evidence integrity only; no certified frontier',scientific_gate_failed=negative,zip_sha256=expected,zip_bytes=size,all_payload_hashes_verified=True,library_file_id=item['library_file_id'],file_id=item['file_id'],file_name=item['file_name'],correction_validated=False,CP12_closed=False))
    event(home,'MIXTO_ADDITIONAL_EVIDENCE_PERMANENTLY_RECOVERED_AND_HASH_VERIFIED',label=label,scientific_gate_failed=negative,CP12_closed=False)

def final_review(home):
    modules,streams,budget=streams_and_budget(home);np=modules['np'];out=home/'analysis';out.mkdir(exist_ok=True)
    for label,s in zip(('coarse','fine'),streams):
        np.savez_compressed(out/(label+'_final.npz'),q=s.q,v=s.v,initial_q=s.initial_q,initial_v=s.initial_v,rows=np.asarray(s.original_rows),time=s.t,config=json.dumps(s.config),labels=np.asarray(s.sim.labels,dtype=str))
    from diagnosticar_mediador_CP10 import compare
    comparison=compare(out/'coarse_final.npz',out/'fine_final.npz')
    criteria=read(home/'science/datos/ensayo_causal_chi_CP12.json')['criteria']
    keys=('norm_relative_sup_error','final_complex_nonradial_field_error_over_initial_norm','final_phi_phase_space_error_over_initial_norm','final_mediator_nonradial_error_over_initial_norm','final_mediator_phase_space_error_over_initial_norm')
    gates={k:comparison[k]<=.02 for k in keys}
    for i,s in enumerate(streams):
        rows=np.asarray(s.original_rows);gates[f'{i}_original_energy']=s.maxe_original<=2e-4;gates[f'{i}_MIXTO_energy']=s.maxe<=2e-4;gates[f'{i}_charge']=s.maxq<=1e-9
        gates[f'{i}_core_charge']=np.max(abs(rows[:,4]/rows[0,4]-1))<=criteria['core_charge_change_max'];gates[f'{i}_bounded_window']=rows[:,5].max()<=3*rows[0,5]
    result=dict(time=160,candidate='MIXTO',comparison=comparison,original_physical_gates={k:bool(v) for k,v in gates.items()},two_original_grid_gates_passed=all(gates.values()),maximum_errors=budget.maximum_errors,final_causal_budget=budget.rows[-1],correction_tested=True,correction_validated=False,CP12_closed=False,full_acceptance_requires_additional_reference_and_robustness=True,automatic_K6_K8_launch_authorized_by_this_protocol=False)
    write(out/'RESULTADO.json',result)
    label='RESULTADO_FINAL_TAU0160' if all(gates.values()) else 'PUERTA_FISICA_NEGATIVA_TAU0160'
    preserve_negative(home,label,'Final MIXTO trial review; provisional result, not CP12 closure',negative=not all(gates.values()))
    event(home,'MIXTO_FINAL_REVIEW_SAVED',two_original_grid_gates_passed=all(gates.values()),correction_validated=False,CP12_closed=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--home',type=Path,required=True);p.add_argument('--prepare-only',action='store_true');p.add_argument('--audit-only',type=int);p.add_argument('--preserve-only',type=int);p.add_argument('--continue-to',type=int);a=p.parse_args();home=a.home.resolve()
    if a.audit_only is not None:print(json.dumps(audit(home,a.audit_only),default=lambda x:x.item()));return
    module=preservation_module(home)
    if a.preserve_only is not None:module.preserve(home,a.preserve_only);return
    if a.prepare_only:
        assert not (home/'outputs/MIXTO_par_estado.npz').exists()
        modules,streams,budget=streams_and_budget(home,False);save_state(home,streams,budget);print(json.dumps(audit(home,0),default=lambda x:x.item()));return
    assert a.continue_to in (8,160)
    with (home/'runtime/worker_started.json').open('x') as f:json.dump(dict(at=now(),kind='NEW_MIXTO_TRIAL_NOT_ORIGINAL_CP10_REPRODUCTION'),f)
    lock=(home/'runtime/worker.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    progress={};stop=threading.Event()
    def heartbeat():
        while not stop.wait(30):
            write(home/'runtime/heartbeat.json',dict(at=now(),observer_clock=progress.get('observer_clock'),physical_streams=[dict(time=s.t,accepted=s.accepted,nfev_closed=s.nfev) for s in progress.get('streams',[])],not_a_restart_certificate=True))
    thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
    try:
        np=__import__('numpy')
        with np.load(home/'outputs/MIXTO_par_estado.npz',allow_pickle=False) as z:start=int(z['time'])
        for target in range(start+8,a.continue_to+1,8):
            previous=read(home/'proofs'/('tau%04d_permanent.json'%(target-8)))
            assert previous['passed'] and previous['execution_run_id']==read(home/'preregistration/nueva_identidad.json')['execution_run_id']
            assert previous['state_sha256']==sha(home/'outputs/MIXTO_par_estado.npz') and previous['receipt_sha256']==sha(home/'outputs/procedencia.json')
            receipt=read(home/'outputs/procedencia.json');receipt['status']='EN_PROGRESO';receipt['segments'].append(dict(started_at=now(),from_time=target-8,to_time=target,initial_state_sha256=previous['state_sha256'],status='EN_PROGRESO'));write(home/'outputs/procedencia.json',receipt)
            event(home,'MIXTO_BEGIN_INDEPENDENT_SEGMENT',from_time=target-8,to_time=target)
            try:
                advance_segment(home,target,progress)
                module.preserve(home,target)
            except BaseException:
                failure=traceback.format_exc()
                receipt=read(home/'outputs/procedencia.json');receipt['status']='FALLIDA_SIN_NUEVA_FRONTERA_CERTIFICADA';receipt['segments'][-1].update(status='FALLIDA',ended_at=now(),reason=failure.splitlines()[-1]);write(home/'outputs/procedencia.json',receipt)
                event(home,'MIXTO_TRIAL_STOPPED',target=target,reason=failure.splitlines()[-1],CP12_closed=False)
                preserve_negative(home,'NEGATIVO_%04d'%target,failure)
                raise
        if a.continue_to==160:final_review(home)
    finally:stop.set()
if __name__=='__main__':main()
