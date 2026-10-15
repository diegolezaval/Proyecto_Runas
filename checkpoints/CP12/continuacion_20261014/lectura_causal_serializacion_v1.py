"""Replay the unchanged CP12 reader with NumPy boolean JSON serialization only.

No M2 step is executed. The original failure is saved and independently retrieved
before replay; all scientific inputs and criteria remain immutable.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, sys, zipfile

def read(p): return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def write(p, value):
    assert not p.exists(), 'Never overwrite evidence'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
def load_module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def unpack(result):
    assert not result.get('isError')
    body=result.get('structuredContent')
    if body is None:body=json.loads(next(c['text'] for c in result['content'] if c.get('type')=='text'))
    return body.get('result',body)
def helper(directory, name, args, data):
    r=subprocess.run([sys.executable,str(directory/name),*args],input=json.dumps(data),text=True,capture_output=True)
    if r.returncode:raise RuntimeError('Library helper failed; '+r.stderr[-1800:])
    return r.stdout
def preserve(directory, payload, archive, recovery):
    files={p.relative_to(payload).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(payload.rglob('*')) if p.is_file()}
    write(payload/'MANIFIESTO.json',{'schema':'CP12_OFFLINE_EVIDENCE_NOT_NEW_SCIENTIFIC_FRONTIER','files':files,'M2_steps':0,'CP12_closed':False})
    assert not archive.exists()
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(payload.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(payload).as_posix())
    expected=sha(archive);size=archive.stat().st_size
    output=helper(directory,'library_upload.py',[],{'uploads':[{'local_path':str(archive),'purpose':'create_library_file','library_artifact_type':'other'}]})
    uploaded=json.loads(output[output.rfind('\n{"results"'):].strip() if '\n{"results"' in output else output)['results']
    assert len(uploaded)==1 and uploaded[0]['status']=='succeeded'
    item=uploaded[0]
    sys.path.insert(0,str(directory))
    from library_hosted_apps import HostedAppsClient
    transfers=unpack(HostedAppsClient().call_tool('connector_openai_library','prepare_materialize',{'items':[{'file_id':item['file_id'],'library_file_id':item['library_file_id'],'file_name':item['file_name']}],'destination':{'directory':str(recovery/'download')}}))
    assert len(transfers.get('transfers',[]))==1 and not transfers.get('unavailable_items')
    tr=transfers['transfers'][0]
    if tr.get('workspace_path'):
        downloaded=Path(tr['workspace_path'])
        helper(directory,'library_file_transfer.py',['apply-xattrs',str(downloaded),tr['library_file_id']],tr.get('xattrs',[]))
    else:
        downloaded=recovery/'download'/item['file_name']
        helper(directory,'library_file_transfer.py',['materialize',str(downloaded)],tr)
    assert downloaded.stat().st_size==size and sha(downloaded)==expected
    assert archive.stat().st_size==size and sha(archive)==expected
    restored=recovery/'checked';assert not restored.exists();restored.mkdir(parents=True)
    with zipfile.ZipFile(downloaded) as z:
        for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts
        z.extractall(restored)
    manifest=read(restored/'MANIFIESTO.json')
    actual={p.relative_to(restored).as_posix() for p in restored.rglob('*') if p.is_file() and p.name!='MANIFIESTO.json'}
    assert actual==set(manifest['files'])
    for n,v in manifest['files'].items():
        p=restored/n;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256']
    proof={'passed':True,'archive_sha256':expected,'archive_bytes':size,'all_payload_hashes_verified':True,'file_count':len(files),'file_id':item['file_id'],'library_file_id':item['library_file_id'],'file_name':item['file_name'],'M2_steps':0,'CP12_closed':False}
    write(recovery/'PROOF.json',proof)
    print(json.dumps({'preserved':archive.name,'passed':True,'all_hashes':True,'file_count':len(files)},ensure_ascii=False),flush=True)
    return proof
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home',type=Path,required=True);p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--helper-dir',type=Path,required=True)
    a=p.parse_args();home=a.home.resolve();out=a.evidence_root.resolve();helpers=a.helper_dir.resolve()
    assert not out.exists();out.mkdir()
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONPYCACHEPREFIX=str(out/'runtime/pycache'))
    assert not os.environ.get('OPENBLAS_CORETYPE')
    proof=read(home/'proofs/tau0160_permanent.json');audit=proof['independent_extracted_audit']
    assert proof['time']==160 and proof['passed'] and proof['all_payload_hashes_verified'] and audit['passed']
    assert len(audit['tests'])==44 and all(audit['tests'].values()) and audit['observation_count']==401 and audit['M2_steps_executed']==0
    failed=out/'failure';failed.mkdir()
    for f in ('runtime/worker.log','runtime/worker_observed_exit.json','proofs/tau0160_permanent.json','coordinator.py'):
        target=failed/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(home/f,target)
    shutil.copyfile(Path(__file__),failed/'serialization_adapter.py')
    exit_=read(home/'runtime/worker_observed_exit.json');assert exit_['returncode']==1
    assert 'Object of type bool is not JSON serializable' in (home/'runtime/worker.log').read_text()
    write(failed/'FAILURE.json',{'status':'ORIGINAL_READER_FAILED_DURING_JSON_SERIALIZATION','error':'TypeError: Object of type bool is not JSON serializable','M2_evolution_complete_and_audited':True,'time':160,'state_sha256':proof['state_sha256'],'scope':'Administrative output serialization; no scientific conclusion from this failure','CP12_closed':False})
    preserve(helpers,failed,out/'CP12_FALLO_SERIALIZACION_CAUSAL_TAU0160_20261015.zip',out/'failure_recovery')
    archive=home/'capsules'/proof['file_name'];assert archive.stat().st_size==proof['zip_bytes'] and sha(archive)==proof['zip_sha256']
    source=out/'source';source.mkdir()
    with zipfile.ZipFile(archive) as z:
        for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts and Path(n).parts[0]==proof['execution_uuid']
        z.extractall(source)
    restored=source/proof['execution_uuid'];manifest=read(restored/'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json')
    actual={p.relative_to(restored).as_posix() for p in restored.rglob('*') if p.is_file() and p.name!='MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'}
    assert actual==set(manifest['files'])
    for n,v in manifest['files'].items():
        f=restored/n;assert f.stat().st_size==v['bytes'] and sha(f)==v['sha256']
    co=load_module('cp12_captured_coordinator',restored/'coordinator.py')
    info,meta,root,run,mgr,prov,physical=co.setup(restored)
    evidence=out/'results';evidence.mkdir()
    shutil.copyfile(Path(__file__),evidence/'serialization_adapter.py')
    write(evidence/'PREREGISTRATION.json',{'operation':'Unchanged original reader; NumPy bool to Python bool only at JSON serialization','scientific_source_edits':False,'criteria_edits':False,'M2_steps':0,'failure_preserved_before_replay':True,'input_archive_sha256':proof['zip_sha256'],'state_sha256':proof['state_sha256'],'input_manifest_file_count':len(manifest['files']),'CP12_closed':False})
    certificate=root/'trazabilidad/CP12_reconstruccion/respaldos/tau0160.json'
    write(certificate,dict(passed=True,time=160,state_sha256=proof['state_sha256'],receipt_sha256=proof['receipt_sha256'],configuration_sha256=proof['configuration_sha256'],download_verification={'passed':True,'all_payload_hashes_verified':True},administrative_routing_only=True,CP12_closed=False))
    baseline={n:sha(run/n) for n in ('CP12_par_estado.npz','configuration.json','procedencia.json','respuestas_finales.npz','serie_presupuestos.json','CP12_par.json')}
    before=co.audit(restored,160);assert before['passed'];write(evidence/'audit_before.json',before)
    import numpy as np
    import interpretar_presupuesto_CP12 as reader
    reader.PAIR=run
    original_write=prov.write;conversions=[]
    def plain(value,path='$'):
        if isinstance(value,np.bool_):
            converted=value.item();assert type(converted) is bool and converted==value
            conversions.append({'path':path,'value':converted,'from':'numpy.bool_','to':'builtins.bool'});return converted
        if isinstance(value,dict):return {k:plain(v,path+'/'+str(k)) for k,v in value.items()}
        if isinstance(value,list):return [plain(v,path+'/'+str(i)) for i,v in enumerate(value)]
        return value
    def write_adapter(path,value):
        assert path.parent==evidence and path.name=='resultados.json'
        original_write(path,plain(value))
    prov.write=write_adapter
    protocol=read(root/'datos/interpretacion_CP12.json')
    cases=[v for v in protocol['cases'].values() if v['entrypoint']=='herramientas/interpretar_presupuesto_CP12.py'];assert len(cases)==1
    try:reader.interpret({'case':cases[0]},evidence)
    finally:prov.write=original_write
    result=read(evidence/'resultados.json')
    assert conversions and result['time']==160 and result['reproduces_CP10_exactly'] and result['observer_checks_passed'] and result['new_M2_steps']==0 and not result['correction_tested']
    assert baseline=={n:sha(run/n) for n in baseline}
    after=co.audit(restored,160);assert after['passed'] and before['state_sha256']==after['state_sha256']==proof['state_sha256']
    write(evidence/'audit_after.json',after)
    write(evidence/'SERIALIZATION_CHECK.json',{'passed':True,'only_type_conversions':conversions,'scientific_input_hashes_unchanged':True,'original_fourteen_source_hashes_unchanged':True,'native_algorithm_and_criteria_unchanged':True,'M2_steps':0,'CP12_closed':False})
    write(evidence/'puerta_y_alcance.json',{'time':160,'exact_CP10_reproduction':True,'three_original_windows_evaluated':True,'physical_gate_threshold':.02,'physical_2_percent_phase_gate_passed':result['observed_core_phase_relative_error']<=.02,'observed_core_phase_relative_error':result['observed_core_phase_relative_error'],'sufficient_coupled_channels':result['sufficient_coupled_channels'],'correction_tested':False,'CP12_closed':False,'M2_steps':0,'subsequent_corrections_require_independent_derivation_preregistration_and_validation':True})
    shutil.copyfile(home/'proofs/tau0160_permanent.json',evidence/'original_tau160_permanent.json')
    for name in ('interpretar_presupuesto_CP12.py','ejecutar_con_procedencia.py'):
        target=evidence/'original_sources'/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(root/'herramientas'/name,target)
    shutil.copyfile(out/'failure_recovery/PROOF.json',evidence/'failure_preservation.json')
    final=preserve(helpers,evidence,out/'CP12_DIAGNOSTICO_CAUSAL_TAU0160_SERIALIZACION_V1_20261015.zip',out/'results_recovery')
    write(out/'COMPLETE.json',{'passed':True,'diagnostic':final,'M2_steps':0,'original_state_unchanged':True,'CP12_closed':False})
    print(json.dumps({'complete':True,'physical_gate_passed':result['observed_core_phase_relative_error']<=.02,'observed_relative_error':result['observed_core_phase_relative_error'],'sufficient_coupled_channels':result['sufficient_coupled_channels'],'bool_conversions':len(conversions),'CP12_closed':False},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
