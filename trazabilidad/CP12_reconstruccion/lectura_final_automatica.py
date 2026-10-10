"""Administrative continuation: original preregistered offline reading after verified tau160.
Never closes the scientific checkpoint or performs additional M2 steps.
"""
from pathlib import Path
import argparse, datetime, fcntl, hashlib, importlib.util, json, os, sys, time, zipfile

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--helpers',type=Path,required=True)
    p.add_argument('--continuation-log',type=Path,required=True)
    args=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    helpers=args.helpers.resolve()
    support=root/'trazabilidad/CP12_reconstruccion'
    outside=root.parent/'CP12_lectura_final';outside.mkdir(exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    sys.path[:0]=[str(root/'herramientas'),str(helpers)]
    from library_hosted_apps import HostedAppsClient
    import gestionar_respaldo_CP12 as manager
    import ejecutar_con_procedencia as prov
    spec=importlib.util.spec_from_file_location('backup_admin',support/'orquestador_respaldos.py')
    admin=importlib.util.module_from_spec(spec);spec.loader.exec_module(admin)
    def emit(event,**values):
        print(json.dumps(dict(event=event,at=prov.now(),**values)),flush=True)
    with (outside/'lectura.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        emit('WAIT_VERIFIED_FINAL_BOUNDARY')
        while True:
            events=[]
            for line in args.continuation_log.read_text().splitlines():
                try: obj=json.loads(line)
                except json.JSONDecodeError: continue
                if isinstance(obj,dict):events.append(obj.get('event'))
            if 'STOP_AND_DIAGNOSE' in events:
                raise RuntimeError('Evolution coordinator stopped; no offline reading')
            if 'EVOLUTION_AND_BACKUPS_FINISHED' in events:break
            time.sleep(5)
        proof=prov.read(support/'respaldos/tau0160.json') if hasattr(prov,'read') else json.loads((support/'respaldos/tau0160.json').read_text())
        if not (proof['passed'] and proof['time']==160 and proof['download_verification']['passed']):
            raise RuntimeError('No verified final proof')
        for key,name in [('state_sha256','CP12_par_estado.npz'),('receipt_sha256','procedencia.json'),('configuration_sha256','configuration.json')]:
            if proof[key]!=prov.digest(manager.RUN/name):raise RuntimeError('Final state changed: '+name)
        manager.original_identity()
        protocol=root/'datos/interpretacion_CP12.json'
        folder=manager.register_full(protocol,'interpretacion_causal')
        emit('BEGIN_ORIGINAL_OFFLINE_INTERPRETATION',folder=str(folder),M2_steps=0)
        prov.execute(protocol,'interpretacion_causal',resume=True)
        verified=prov.verify_receipt(folder/'procedencia.json')
        if not (verified['passed'] and verified['status']=='COMPLETADA'):raise RuntimeError(str(verified))
        result=json.loads((folder/'resultados.json').read_text())
        if result['new_M2_steps']!=0 or result['correction_tested'] or not result['scientific_closure_requires_review']:
            raise RuntimeError('Unexpected scientific scope')
        files={p.relative_to(root).as_posix():p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        files[Path(__file__).resolve().relative_to(root).as_posix()]=Path(__file__).resolve()
        manifest={name:prov.digest(path) for name,path in files.items()}
        archive=outside/'Proyecto_Runas_CP12_LECTURA_FINAL_tau0160.zip'
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for name,path in files.items():z.write(path,'Proyecto_Runas/'+name)
            z.writestr('MANIFEST_SHA256.json',json.dumps(manifest,indent=2)+'\n')
        archive_hash=prov.digest(archive)
        upload_log=outside/'guardado.json'
        admin.run([sys.executable,str(helpers/'library_upload.py')],cwd=root.parent,
                  input_=json.dumps({'uploads':[{'local_path':str(archive),'purpose':'create_library_file','library_artifact_type':'other'}]}),output=upload_log)
        outcomes=json.loads(upload_log.read_text())['results']
        if len(outcomes)!=1 or outcomes[0].get('status')!='succeeded':raise RuntimeError('Offline results not saved')
        owned=outcomes[0];destination=outside/'descarga'
        prepared=admin.unpack(HostedAppsClient().call_tool('connector_openai_library','prepare_materialize',{
            'items':[{'file_id':owned['file_id'],'library_file_id':owned['library_file_id'],'file_name':owned['file_name']}],
            'destination':{'directory':str(destination)}}))
        if len(prepared.get('transfers',[]))!=1 or prepared.get('unavailable_items'):raise RuntimeError('Incomplete result download')
        tr=prepared['transfers'][0]
        if tr.get('workspace_path'):
            downloaded=Path(tr['workspace_path'])
            admin.run([sys.executable,str(helpers/'library_file_transfer.py'),'apply-xattrs',str(downloaded),tr['library_file_id']],
                      cwd=root.parent,input_=json.dumps(tr.get('xattrs',[])),output=outside/'metadata.log')
        else:
            downloaded=destination/owned['file_name']
            admin.run([sys.executable,str(helpers/'library_file_transfer.py'),'materialize',str(downloaded)],
                      cwd=root.parent,input_=json.dumps(tr),output=outside/'materializacion.log')
        if prov.digest(downloaded)!=archive_hash:raise RuntimeError('Downloaded archive hash mismatch')
        extracted=outside/'extraido';extracted.mkdir()
        with zipfile.ZipFile(downloaded) as z:
            expected={'Proyecto_Runas/'+name for name in manifest}|{'MANIFEST_SHA256.json'}
            if set(z.namelist())!=expected or len(z.namelist())!=len(expected):raise RuntimeError('Coverage mismatch')
            if json.loads(z.read('MANIFEST_SHA256.json'))!=manifest:raise RuntimeError('Manifest mismatch')
            for name,sha in manifest.items():
                if hashlib.sha256(z.read('Proyecto_Runas/'+name)).hexdigest()!=sha:raise RuntimeError('Payload mismatch: '+name)
            z.extractall(extracted)
        extracted_receipt=extracted/'Proyecto_Runas'/folder.relative_to(root)/'procedencia.json'
        check=prov.verify_receipt(extracted_receipt)
        if not check['passed']:raise RuntimeError(str(check))
        final=dict(passed=True,verified_at=prov.now(),library_file_id=owned['library_file_id'],file_id=owned['file_id'],
                   file_name=owned['file_name'],zip_sha256=archive_hash,payload_files=len(manifest),
                   download_receipt_verification=check,scientific_closure_requires_review=True,
                   previous_verified_backup=proof['zip_sha256'],M2_steps=0,correction_tested=False)
        target=support/'respaldos/lectura_final_tau0160.json'
        if target.exists():raise RuntimeError('Do not overwrite proof')
        prov.write(target,final)
        emit('OFFLINE_BUDGET_SAVED_AND_VERIFIED',proof=final,scientific_review_pending=True)

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'event':'STOP_AND_DIAGNOSE_OFFLINE','error':repr(error)}),flush=True)
        raise
