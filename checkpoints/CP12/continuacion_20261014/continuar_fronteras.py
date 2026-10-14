"""Independent CP12 recovery. Original scientific sources are never edited."""
from pathlib import Path
import argparse, datetime, fcntl, hashlib, json, os, shutil, subprocess, sys, threading, time, zipfile

def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    with tmp.open('rb') as f: os.fsync(f.fileno())
    tmp.replace(p)
def read(p): return json.loads(p.read_text())
def event(home,name,**kw):
    v=dict(at=now(),event=name,**kw)
    with (home/'runtime/events.jsonl').open('a') as f:
        f.write(json.dumps(v,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(v,ensure_ascii=False),flush=True)
def setup(home):
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    assert not os.environ.get('OPENBLAS_CORETYPE'),'Dispatch forcing forbidden'
    root=home/'science';sys.path.insert(0,str(root/'herramientas'))
    import gestionar_respaldo_CP12 as mgr
    import ejecutar_con_procedencia as prov
    import reproducir_par_CP12 as physical
    from threadpoolctl import threadpool_info
    info=read(home/'preregistration/ubicacion.json')
    ident=read(home/'preregistration/identidad_cientifica.json')
    assert len(ident['code_hashes'])==14
    for n,h in ident['code_hashes'].items(): assert sha(root/n)==h
    assert mgr.original_identity()[2]==ident,'Original inputs/environment changed'
    assert all(p['num_threads']==1 and p['architecture']=='SkylakeX' for p in threadpool_info())
    meta=read(home/'preregistration/nueva_identidad.json')
    assert sha(home/'coordinator.py')==meta['supervision_source_sha256']
    run=root/meta['run_relative'];mgr.RUN=run
    return info,meta,root,run,mgr,prov,physical
def finish_receipt(run,prov):
    r=read(run/'procedencia.json')
    r['output_hashes']={p.relative_to(run).as_posix():sha(p) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='procedencia.json' and '__pycache__' not in p.parts and p.suffix!='.tmp'}
    prov.write(run/'procedencia.json',r)
def audit(home,t):
    info,meta,root,run,mgr,prov,physical=setup(home)
    result=mgr.audit(t)
    result['original_scientific_protocol_identity']=result.pop('run_id')
    result['run_id']=meta['execution_run_id'];result['execution_uuid']=info['execution_uuid']
    result['routing_adaptation']='Only administrative RUN points to the new isolated output; original science/audit source bytes unchanged'
    result['old_executor_termination_assumed']=False
    assert result['passed'],json.dumps(result['tests'])
    return result
def helper(home,name,args,data=None):
    result=subprocess.run([sys.executable,str(home/'runtime/library'/name),*args],input=None if data is None else json.dumps(data),text=True,capture_output=True)
    if result.returncode: raise RuntimeError('Library helper failed: '+result.stderr[-2500:])
    return result.stdout
def unpack(r):
    if r.get('isError'): raise RuntimeError(str(r.get('structuredContent',{})))
    s=r.get('structuredContent')
    if s is None:s=json.loads(next(c['text'] for c in r['content'] if c.get('type')=='text'))
    return s.get('result',s)
def preserve(home,t):
    info,meta,root,run,mgr,prov,physical=setup(home)
    checked=audit(home,t);write(home/'proofs'/('tau%04d_audit.json'%t),checked)
    label='CP12_RI_'+info['execution_uuid']+'_tau%04d'%t
    archive=home/'capsules'/(label+'.zip')
    assert not archive.exists(),'Never overwrite an independent capsule'
    selected=[p for p in sorted(home.rglob('*')) if p.is_file() and not any(x in ('runtime','capsules','recoveries','cache','__pycache__') for x in p.relative_to(home).parts) and p.suffix not in ('.tmp','.pyc','.so')]
    manifest=dict(schema='CP12_INDEPENDENT_RECOVERY_FULL_CAPSULE_NOT_SCIENTIFIC_CLOSURE',execution_uuid=info['execution_uuid'],execution_run_id=meta['execution_run_id'],time=t,branch=info['branch'],run_relative=meta['run_relative'],original_ancestor_state_sha256=info['ancestor_state_sha256'],CP12_closed=False,files={p.relative_to(home).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in selected})
    tmp=archive.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in selected:z.write(p,info['execution_uuid']+'/'+p.relative_to(home).as_posix())
        z.writestr(info['execution_uuid']+'/MANIFIESTO_RECUPERACION_INDEPENDIENTE.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    tmp.replace(archive)
    expected=sha(archive)
    output=helper(home,'library_upload.py',[],{'uploads':[{'local_path':str(archive),'purpose':'create_library_file','library_artifact_type':'other'}]})
    uploaded=json.loads(output[output.rfind('\n{"results"'):].strip() if '\n{"results"' in output else output)['results']
    assert len(uploaded)==1 and uploaded[0]['status']=='succeeded'
    item=uploaded[0]
    sys.path.insert(0,str(home/'runtime/library'))
    from library_hosted_apps import HostedAppsClient
    client=HostedAppsClient()
    transfers=unpack(client.call_tool('connector_openai_library','prepare_materialize',{'items':[{'file_id':item['file_id'],'library_file_id':item['library_file_id'],'file_name':item['file_name']}],'destination':{'directory':str(home/'recoveries'/(label+'_download'))}}))
    assert len(transfers.get('transfers',[]))==1 and not transfers.get('unavailable_items')
    tr=transfers['transfers'][0]
    if tr.get('workspace_path'):
        download=Path(tr['workspace_path'])
        helper(home,'library_file_transfer.py',['apply-xattrs',str(download),tr['library_file_id']],tr.get('xattrs',[]))
    else:
        download=home/'recoveries'/(label+'_download')/item['file_name']
        helper(home,'library_file_transfer.py',['materialize',str(download)],tr)
    assert download.stat().st_size==archive.stat().st_size and sha(download)==expected
    dest=home/'recoveries'/(label+'_checked');assert not dest.exists();dest.mkdir()
    with zipfile.ZipFile(download) as z:
        for name in z.namelist():
            p=Path(name);assert not p.is_absolute() and '..' not in p.parts and p.parts[0]==info['execution_uuid']
        z.extractall(dest)
    restored=dest/info['execution_uuid']
    m=read(restored/'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json')
    actual={p.relative_to(restored).as_posix() for p in restored.rglob('*') if p.is_file() and p.name!='MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'}
    assert actual==set(m['files'])
    for n,v in m['files'].items():assert (restored/n).stat().st_size==v['bytes'] and sha(restored/n)==v['sha256']
    proc=subprocess.run([sys.executable,str(restored/'coordinator.py'),'--home',str(restored),'--audit-only',str(t)],text=True,capture_output=True,env={**os.environ,'PYTHONPYCACHEPREFIX':str(restored/'runtime/pycache'),'TMPDIR':str(home/'runtime/tmp')})
    if proc.returncode:raise RuntimeError('Independent extraction audit failed: '+proc.stderr[-3000:]+' '+proc.stdout[-3000:])
    remote=json.loads(proc.stdout)
    assert remote['passed'] and remote['time']==t and remote['state_sha256']==checked['state_sha256']
    proof=dict(schema='CP12_INDEPENDENT_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED',time=t,execution_uuid=info['execution_uuid'],execution_run_id=meta['execution_run_id'],branch=info['branch'],library_file_id=item['library_file_id'],file_id=item['file_id'],file_name=item['file_name'],zip_sha256=expected,zip_bytes=archive.stat().st_size,state_sha256=checked['state_sha256'],configuration_sha256=checked['configuration_sha256'],receipt_sha256=checked['receipt_sha256'],all_payload_hashes_verified=True,independent_extracted_audit=remote,passed=True,at=now(),CP12_closed=False)
    target=home/'proofs'/('tau%04d_permanent.json'%t);assert not target.exists();write(target,proof)
    event(home,'BOUNDARY_PERMANENTLY_VERIFIED',time=t,state_sha256=proof['state_sha256'],capsule_bytes=proof['zip_bytes'],independent_recovery_passed=True)
    return proof

def preserve_additional(home,label):
    """Preserve a negative or new offline result without certifying a frontier."""
    info,meta,root,run,mgr,prov,physical=setup(home)
    selected=[p for p in sorted(home.rglob('*')) if p.is_file() and not any(x in ('runtime','capsules','recoveries','cache','__pycache__') for x in p.relative_to(home).parts) and p.suffix not in ('.tmp','.pyc','.so')]
    manifest=dict(schema='CP12_ADDITIONAL_EVIDENCE_NOT_NEW_FRONTIER_CERTIFICATE',label=label,
                  original_science_unchanged=True,CP12_closed=False,
                  files={p.relative_to(home).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in selected})
    archive=home/'capsules'/('CP12_RI_'+info['execution_uuid']+'_'+label+'.zip')
    assert not archive.exists()
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in selected:z.write(p,info['execution_uuid']+'/'+p.relative_to(home).as_posix())
        z.writestr(info['execution_uuid']+'/MANIFIESTO_EVIDENCIA_ADICIONAL.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    output=helper(home,'library_upload.py',[],{'uploads':[{'local_path':str(archive),'purpose':'create_library_file','library_artifact_type':'other'}]})
    result=json.loads(output[output.rfind('\n{"results"'):].strip() if '\n{"results"' in output else output)
    assert len(result['results'])==1 and result['results'][0]['status']=='succeeded'
    write(home/'proofs'/(label+'_saved.json'),dict(passed=True,zip_sha256=sha(archive),
          file_id=result['results'][0]['file_id'],library_file_id=result['results'][0]['library_file_id'],
          not_a_new_frontier_certificate=True,CP12_closed=False))
    event(home,'ADDITIONAL_EVIDENCE_PERMANENTLY_SAVED',label=label,CP12_closed=False)

def interpret_final(home):
    """Use the unchanged original interpreter after exact reproduction and recovery."""
    info,meta,root,run,mgr,prov,physical=setup(home)
    proof=read(home/'proofs/tau0160_permanent.json')
    assert proof['passed'] and proof['independent_extracted_audit']['passed']
    certificate=root/'trazabilidad/CP12_reconstruccion/respaldos/tau0160.json'
    assert not certificate.exists()
    write(certificate,dict(passed=True,time=160,state_sha256=proof['state_sha256'],
          receipt_sha256=proof['receipt_sha256'],configuration_sha256=proof['configuration_sha256'],
          download_verification=dict(passed=True,all_payload_hashes_verified=True,
          independent_extracted_audit=proof['independent_extracted_audit']),
          administrative_routing_to_independent_run=True,CP12_closed=False))
    import interpretar_presupuesto_CP12 as reader
    reader.PAIR=run
    protocol=read(root/'datos/interpretacion_CP12.json')
    cases=[v for v in protocol['cases'].values() if v['entrypoint']=='herramientas/interpretar_presupuesto_CP12.py']
    assert len(cases)==1
    out=home/'analysis/causal_tau0160';assert not out.exists();out.mkdir(parents=True)
    result=reader.interpret(dict(case=cases[0]),out)
    result['CP12_closed']=False
    result['administrative_routing_only']=True
    result['physical_2_percent_phase_gate_passed']=result['observed_core_phase_relative_error']<=.02
    write(out/'puerta_y_alcance.json',dict(time=160,exact_CP10_reproduction=True,
          three_original_windows_evaluated=True,physical_gate_threshold=.02,
          physical_2_percent_phase_gate_passed=result['physical_2_percent_phase_gate_passed'],
          observed_core_phase_relative_error=result['observed_core_phase_relative_error'],
          sufficient_coupled_channels=result['sufficient_coupled_channels'],
          correction_tested=False,CP12_closed=False,new_M2_steps=0,
          subsequent_corrections_require_independent_derivation_preregistration_and_validation=True))
    preserve_additional(home,'DIAGNOSTICO_CAUSAL_TAU0160')
    event(home,'THREE_CAUSAL_WINDOWS_EVALUATED_AND_PRESERVED',time=160,
          sufficient_coupled_channels=result['sufficient_coupled_channels'],
          physical_2_percent_phase_gate_passed=result['physical_2_percent_phase_gate_passed'],CP12_closed=False)
def heartbeat(home,physical,done):
    while not done.wait(30):
        frames=sys._current_frames();observed=None
        for frame in frames.values():
            while frame:
                if frame.f_code is physical.run_pair.__code__:
                    streams=frame.f_locals.get('streams')
                    observed={'observer_clock':frame.f_locals.get('t'),'physical_streams':None if streams is None else [{'time':float(s.t),'accepted':int(s.accepted),'nfev_closed':int(s.nfev)} for s in streams]}
                    break
                frame=frame.f_back
            if observed is not None:break
        write(home/'runtime/heartbeat.json',dict(at=now(),execution_uuid=read(home/'preregistration/ubicacion.json')['execution_uuid'],observation=observed,not_a_restart_certificate=True))
def main():
    p=argparse.ArgumentParser();p.add_argument('--home',type=Path,required=True);p.add_argument('--audit-only',type=int);p.add_argument('--preserve-only',type=int);p.add_argument('--continue-to',type=int);a=p.parse_args();home=a.home.resolve()
    if a.audit_only is not None:print(json.dumps(audit(home,a.audit_only),ensure_ascii=False));return
    if a.preserve_only is not None:preserve(home,a.preserve_only);return
    if a.continue_to!=160:raise ValueError('Only registered continuation to 160')
    marker=home/'runtime/worker_started.json'
    with marker.open('x') as f:json.dump(dict(at=now(),scope='Only this independent execution; original executor ignored'),f)
    lock=(home/'runtime/worker.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    info,meta,root,run,mgr,prov,physical=setup(home)
    cfg=read(run/'configuration.json')['case']['configuration']
    start=int(meta['initial_frontier'])
    stop=threading.Event();thread=threading.Thread(target=heartbeat,args=(home,physical,stop),daemon=True);thread.start()
    try:
        for target in range(start+8,161,8):
            previous=read(home/'proofs'/('tau%04d_permanent.json'%(target-8)))
            assert previous['passed'] and previous['execution_run_id']==meta['execution_run_id']
            for filename,key in [('CP12_par_estado.npz','state_sha256'),('configuration.json','configuration_sha256'),('procedencia.json','receipt_sha256')]:
                assert sha(run/filename)==previous[key]
            receipt=read(run/'procedencia.json')
            segment=dict(started_at=now(),from_time=target-8,to_time=target,resumed_from_state_sha256=previous['state_sha256'],status='EN_PROGRESO')
            receipt['segments'].append(segment);receipt['status']='EN_PROGRESO';prov.write(run/'procedencia.json',receipt)
            event(home,'BEGIN_INDEPENDENT_SEGMENT',from_time=target-8,to_time=target)
            try:result=physical.run_pair(cfg,run,stop_at=target)
            except BaseException as exc:
                receipt=read(run/'procedencia.json');receipt['status']='FALLIDA';receipt['segments'][-1].update(status='FALLIDA',ended_at=now(),reason=repr(exc));prov.write(run/'procedencia.json',receipt)
                finish_receipt(run,prov)
                write(home/'proofs'/('segment_%04d_negative.json'%target),dict(passed=False,from_time=target-8,to_time=target,reason=repr(exc),CP12_closed=False,not_a_certified_frontier=True))
                event(home,'INDEPENDENT_SEGMENT_FAILED',from_time=target-8,to_time=target,reason=repr(exc))
                preserve_additional(home,'RESULTADO_NEGATIVO_%04d'%target)
                raise
            receipt=read(run/'procedencia.json');receipt['status']='PAUSADA_REANUDABLE' if target<160 else 'COMPLETADA'
            receipt['segments'][-1].update(status=receipt['status'],ended_at=now(),final_time=result['time'])
            prov.write(run/'procedencia.json',receipt);finish_receipt(run,prov)
            try:
                preserve(home,target)
            except BaseException as exc:
                write(home/'proofs'/('preservation_%04d_negative.json'%target),dict(
                    passed=False,time=target,reason=repr(exc),CP12_closed=False,
                    not_a_certified_frontier=True,scope='Audit or permanent recovery failure; no scientific inference'))
                event(home,'BOUNDARY_AUDIT_OR_RECOVERY_FAILED',time=target,reason=repr(exc))
                preserve_additional(home,'FRONTERA_NO_CERTIFICADA_%04d'%target)
                raise
        event(home,'EVOLUTION_160_REPRODUCTION_AUDITED_CAUSAL_INTERPRETATION_PENDING',time=160,CP12_closed=False)
        interpret_final(home)
    finally:stop.set()
if __name__=='__main__':main()

