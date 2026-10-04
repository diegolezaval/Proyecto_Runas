"""Fronteras originales CP12: ejecución, respaldo y verificación; sin RHS nuevo."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)

def unpack(result):
    if result.get('isError'): raise RuntimeError(str(result))
    s=result.get('structuredContent')
    if s is None:
        s=json.loads(next(c['text'] for c in result['content'] if c.get('type')=='text'))
    return s.get('result',s)

def run(command, *, cwd, input_=None, output=None):
    if output:
        with output.open('w') as out:
            p=subprocess.run(command,cwd=cwd,input=input_,text=True,stdout=out,stderr=subprocess.PIPE)
        if p.returncode: raise RuntimeError(p.stderr+'\n'+output.read_text()[-6000:])
        return
    subprocess.run(command,cwd=cwd,input=input_,text=True,check=True)

def preserve(root, helpers, time_, client):
    label='tau'+str(int(time_)).zfill(4)
    outside=root.parent/'CP12_fronteras';outside.mkdir(exist_ok=True)
    manager=root/'herramientas/gestionar_respaldo_CP12.py'
    support=root/'trazabilidad/CP12_reconstruccion'
    pair=root/'validacion/P06/no_radial/CP12/par_instrumentado__a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
    print(json.dumps({'event':'AUDIT_BOUNDARY','time':time_}),flush=True)
    run([sys.executable,str(manager),'--auditar','--time',str(time_)],cwd=root,output=outside/(label+'_auditoria.log'))
    archive=outside/('Proyecto_Runas_CP12_REINICIO_'+label+'.zip')
    run([sys.executable,str(manager),'--paquete',str(archive),'--time',str(time_)],cwd=root,output=outside/(label+'_paquete.json'))
    packaged=json.loads((outside/(label+'_paquete.json')).read_text())
    print(json.dumps({'event':'SAVING_BOUNDARY','time':time_,'bytes':packaged['bytes']}),flush=True)
    upload_result=outside/(label+'_guardado.json')
    run([sys.executable,str(helpers/'library_upload.py')],cwd=root.parent,
        input_=json.dumps({'uploads':[{'local_path':str(archive),'purpose':'create_library_file','library_artifact_type':'other'}]}),output=upload_result)
    outcomes=json.loads(upload_result.read_text())['results']
    if len(outcomes)!=1 or outcomes[0].get('status')!='succeeded':raise RuntimeError('Respaldo no guardado: '+str(outcomes))
    owned=outcomes[0]
    destination=outside/(label+'_descarga')
    prepared=unpack(client.call_tool('connector_openai_library','prepare_materialize',{
        'items':[{'file_id':owned['file_id'],'library_file_id':owned['library_file_id'],'file_name':owned['file_name']}],
        'destination':{'directory':str(destination)}}))
    transfers=prepared.get('transfers',[])
    if len(transfers)!=1 or prepared.get('unavailable_items'):raise RuntimeError('Descarga incompleta')
    tr=transfers[0]
    if tr.get('workspace_path'):
        downloaded=Path(tr['workspace_path'])
        run([sys.executable,str(helpers/'library_file_transfer.py'),'apply-xattrs',str(downloaded),tr['library_file_id']],
            cwd=root.parent,input_=json.dumps(tr.get('xattrs',[])),output=outside/(label+'_metadata.log'))
    else:
        downloaded=destination/owned['file_name']
        run([sys.executable,str(helpers/'library_file_transfer.py'),'materialize',str(downloaded)],
            cwd=root.parent,input_=json.dumps(tr),output=outside/(label+'_materializacion.log'))
    verification=outside/(label+'_verificacion.json')
    run([sys.executable,str(manager),'--verificar-descarga',str(downloaded),'--sha256',packaged['sha256'],
         '--destino',str(outside/(label+'_extraido'))],cwd=root,output=verification)
    v=json.loads(verification.read_text());assert v['passed'] and v['all_payload_hashes_verified']
    restored=v['independent_extracted_check']
    assert restored['passed'] and restored['time']==time_
    proof=dict(schema_version='1.0.0',passed=True,time=time_,verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        library_file_id=owned['library_file_id'],file_id=owned['file_id'],file_name=owned['file_name'],
        version_id=owned.get('current_version_number'),zip_sha256=packaged['sha256'],
        state_sha256=digest(pair/'CP12_par_estado.npz'),receipt_sha256=digest(pair/'procedencia.json'),
        configuration_sha256=digest(pair/'configuration.json'),download_verification=v,
        original_protocol_unchanged=True,scientific_checkpoint='CP11_DIAGNOSTICO_RADIAL_CHI',
        orchestrator_sha256=digest(Path(__file__)))
    for key in ['state_sha256','receipt_sha256','configuration_sha256']:
        if proof[key]!=restored[key]:raise RuntimeError('El original cambió durante el respaldo: '+key)
    previous=support/'respaldos'/('tau'+str(int(time_-8)).zfill(4)+'.json')
    proof['previous_verified_backup']=json.loads(previous.read_text())['zip_sha256'] if previous.exists() else None
    target=support/'respaldos'/(label+'.json')
    if target.exists():raise RuntimeError('No sobrescribir comprobante anterior')
    write(target,proof)
    print(json.dumps({'event':'BOUNDARY_PERMANENTLY_VERIFIED','time':time_,'state_sha256':proof['state_sha256'],
          'maximum_errors':restored['maximum_errors'],'metadata':restored['metadata']}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--helpers',type=Path,required=True)
    p.add_argument('--from-time',type=int,required=True);p.add_argument('--to-time',type=int,default=160);a=p.parse_args()
    root=a.root.resolve();helpers=a.helpers.resolve()
    if a.from_time%8 or a.to_time%8 or not 0<=a.from_time<a.to_time<=160:raise ValueError('Fronteras inválidas')
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    sys.path.insert(0,str(helpers));from library_hosted_apps import HostedAppsClient
    client=HostedAppsClient()
    for target in range(a.from_time+8,a.to_time+1,8):
        print(json.dumps({'event':'BEGIN_REGISTERED_SEGMENT','from_time':target-8,'to_time':target}),flush=True)
        run([sys.executable,str(root/'herramientas/gestionar_respaldo_CP12.py'),'--avanzar',str(target)],cwd=root)
        preserve(root,helpers,float(target),client)
    print(json.dumps({'event':'REQUESTED_EVOLUTION_AND_BACKUPS_FINISHED','time':a.to_time,'causal_interpretation_pending':True}),flush=True)
