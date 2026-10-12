"""Passive boundary analyses and final permanent evidence; never launches M2."""
from pathlib import Path
import argparse, datetime, fcntl, hashlib, importlib.util, json, os, subprocess, sys, time, zipfile

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n');tmp.replace(p)
def log(home,event,**values):
    value=dict(at=now(),event=event,**values)
    print(json.dumps(value,ensure_ascii=False),flush=True)
    with (home/'runtime/passive_events.jsonl').open('a') as f:f.write(json.dumps(value,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def run_analysis(home,relative,args):
    command=[sys.executable,str(home/relative),'--home',str(home),*args]
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONPYCACHEPREFIX=str(home/'runtime/passive_pycache'),TMPDIR=str(home/'runtime/tmp'))
    result=subprocess.run(command,text=True,capture_output=True,env=env)
    if result.returncode:raise RuntimeError(relative+' failed: '+result.stderr[-1800:])
    log(home,'PASSIVE_ANALYSIS_COMPLETED',program=relative,args=args,result=result.stdout[-1400:],M2_steps=0)

def bundle(home,label):
    spec=importlib.util.spec_from_file_location('administrative_coordinator',home/'coordinator.py')
    admin=importlib.util.module_from_spec(spec);spec.loader.exec_module(admin)
    meta=read(home/'preregistration/nueva_identidad.json')
    selected=[]
    for directory in ['analysis','proofs','preregistration','ancestry']:
        selected.extend(p for p in (home/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.tmp','.pyc','.so'])
    selected.extend(home/n for n in ['coordinator.py','execute_guarded.py','bootstrap_from_boundary.py','passive_postprocess.py','publish_boundary.py'])
    archive=home/'capsules'/('CP12_RI_'+meta['execution_uuid']+'_'+label+'.zip');assert not archive.exists()
    manifest=dict(schema='CP12_PASSIVE_ANALYSIS_AND_PERMANENT_PROOFS',execution_uuid=meta['execution_uuid'],execution_run_id=meta['execution_run_id'],label=label,M2_steps=0,CP12_closed=False,files={p.relative_to(home).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in selected})
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in selected:z.write(p,p.relative_to(home).as_posix())
        z.writestr('MANIFIESTO_ANALISIS.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    digest=sha(archive)
    output=admin.helper(home,'library_upload.py',[],{'uploads':[{'local_path':str(archive),'purpose':'create_library_file','library_artifact_type':'other'}]})
    items=json.loads(output[output.rfind('\n{"results"'):].strip() if '\n{"results"' in output else output)['results']
    assert len(items)==1 and items[0]['status']=='succeeded';item=items[0]
    sys.path.insert(0,str(home/'runtime/library'))
    from library_hosted_apps import HostedAppsClient
    client=HostedAppsClient()
    response=admin.unpack(client.call_tool('connector_openai_library','prepare_materialize',{'items':[{'file_id':item['file_id'],'library_file_id':item['library_file_id'],'file_name':item['file_name']}],'destination':{'directory':str(home/'recoveries'/(label+'_passive_download'))}}))
    assert len(response.get('transfers',[]))==1 and not response.get('unavailable_items')
    tr=response['transfers'][0]
    if tr.get('workspace_path'):
        download=Path(tr['workspace_path']);admin.helper(home,'library_file_transfer.py',['apply-xattrs',str(download),tr['library_file_id']],tr.get('xattrs',[]))
    else:
        download=home/'recoveries'/(label+'_passive_download')/item['file_name'];admin.helper(home,'library_file_transfer.py',['materialize',str(download)],tr)
    assert sha(download)==digest and download.stat().st_size==archive.stat().st_size
    with zipfile.ZipFile(download) as z:
        assert z.testzip() is None and len(z.namelist())==len(manifest['files'])+1
        remote=read_manifest=json.loads(z.read('MANIFIESTO_ANALISIS.json'))
        assert remote==manifest
        for n,v in manifest['files'].items():
            b=z.read(n);assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256']
    proof=dict(schema='CP12_PASSIVE_ANALYSIS_PERMANENTLY_RETRIEVED',execution_uuid=meta['execution_uuid'],execution_run_id=meta['execution_run_id'],file_name=item['file_name'],library_file_id=item['library_file_id'],file_id=item['file_id'],zip_sha256=digest,zip_bytes=archive.stat().st_size,payload_files_verified=len(manifest['files']),passed=True,M2_steps=0,CP12_closed=False,at=now())
    target=home/'proofs'/(label+'_passive_permanent.json');assert not target.exists();write(target,proof)
    log(home,'PASSIVE_BUNDLE_PERMANENTLY_VERIFIED',file_name=proof['file_name'],sha256=digest,payloads=len(manifest['files']),M2_steps=0,CP12_closed=False)
    return proof

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--home',type=Path,required=True);args=ap.parse_args();home=args.home.resolve()
    meta=read(home/'preregistration/nueva_identidad.json')
    marker=home/'runtime/passive_started.json'
    with marker.open('x') as f:json.dump(dict(at=now(),execution_uuid=meta['execution_uuid'],source_sha256=sha(Path(__file__)),M2_steps=0),f)
    lock=(home/'runtime/passive.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    completed=set();start=int(meta['initial_frontier'])
    try:
        while True:
            for t in range(start,161,8):
                p=home/'proofs'/('tau%04d_permanent.json'%t)
                if t in completed or not p.exists():continue
                proof=read(p);assert proof['time']==t and proof['passed'] and proof['all_payload_hashes_verified'] and proof['independent_extracted_audit']['passed']
                assert proof['execution_uuid']==meta['execution_uuid'] and proof['execution_run_id']==meta['execution_run_id']
                if t<160:
                    jobs=[('analysis/prefix/leer_frontera.py',home/'analysis/prefix'/('tau%04d.json'%t)),('analysis/condicional/diagnostico.py',home/'analysis/condicional'/('tau%04d'%t)/'resultados.json'),('analysis/jacobiano_local/evaluar.py',home/'analysis/jacobiano_local'/('tau%04d.json'%t))]
                    for program,output in jobs:
                        if not output.exists():run_analysis(home,program,['--boundary',str(t)])
                        data=read(output);assert data['time']==t and data['M2_steps']==0
                    completed.add(t);log(home,'PASSIVE_BOUNDARY_READY',time=t,M2_steps=0)
                else:
                    exit_path=home/'proofs/coordinator_exit.json'
                    if not exit_path.exists():continue
                    exit_proof=read(exit_path);assert exit_proof['execution_uuid']==meta['execution_uuid'] and exit_proof['worker_has_exited'] and exit_proof['returncode']==0
                    existing=list((home/'analysis/causal').glob('lectura__*/procedencia_lectura.json'))
                    if not existing:run_analysis(home,'analysis/causal/leer_final_independiente.py',[])
                    receipts=list((home/'analysis/causal').glob('lectura__*/procedencia_lectura.json'));assert len(receipts)==1
                    r=read(receipts[0]);assert r['status']=='COMPLETED' and r['M2_steps']==0 and r['identity']['scientific_run_id']==meta['execution_run_id']
                    log(home,'ORIGINAL_FINAL_CAUSAL_READING_READY',time=160,review_pending=True,CP12_closed=False)
                    bundle(home,'LECTURA_FINAL_TAU160')
                    write(home/'proofs/passive_exit.json',dict(at=now(),passed=True,time=160,M2_steps=0,CP12_closed=False,review_pending=True));return
            exit_path=home/'proofs/coordinator_exit.json'
            if exit_path.exists() and read(exit_path)['returncode']!=0:
                write(home/'proofs/passive_exit.json',dict(at=now(),passed=False,reason='The own physical coordinator exited before completion; no new physical worker launched',physical_exit_proof_sha256=sha(exit_path),passive_boundaries=sorted(completed),M2_steps=0,CP12_closed=False))
                bundle(home,'INCOMPLETO_COMPROBADO');return
            write(home/'runtime/passive_heartbeat.json',dict(at=now(),execution_uuid=meta['execution_uuid'],passive_boundaries=sorted(completed),M2_steps=0))
            time.sleep(30)
    except BaseException as exc:
        target=home/'proofs/passive_exit.json'
        if not target.exists():write(target,dict(at=now(),passed=False,reason=repr(exc),passive_boundaries=sorted(completed),M2_steps=0,CP12_closed=False))
        log(home,'PASSIVE_POSTPROCESS_FAILED',reason=repr(exc),M2_steps=0);raise

if __name__=='__main__':main()
