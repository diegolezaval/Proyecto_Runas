"""Conservación P3 con auditores originales; ninguna evolución numérica aquí."""
from datetime import datetime, timezone
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile

REPO='diegolezaval/Proyecto_Runas'
TAG='respaldo-cp12-p3-20261027'
UID='128492e27d6d44798f2ef9336fc1b2e7'


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text())


def now():return datetime.now(timezone.utc).isoformat()


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())


def logged(command,prefix,payload=None,env=None):
    p=subprocess.run(command,input=None if payload is None else json.dumps(payload),env=env,capture_output=True,text=True)
    prefix.with_suffix('.stdout.txt').write_text(p.stdout);prefix.with_suffix('.stderr.txt').write_text(p.stderr)
    if p.returncode:raise RuntimeError('Operación no completada; conservar recibos y no repetir una escritura incierta')
    return p.stdout


def audit(home,kind,boundary,output):
    output.mkdir(parents=True,exist_ok=False)
    for n in ['runtime/tmp','runtime/pycache']:(home/n).mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
             PYTHONPYCACHEPREFIX=str(home/'runtime/pycache'),TMPDIR=str(home/'runtime/tmp'))
    if env.get('OPENBLAS_CORETYPE'):raise ValueError('Arquitectura forzada')
    commands=[('boundary','coordinator.py',['--audit-only',str(boundary)])]
    if kind=='transport':commands.append(('transport','controlador_transporte.py',['--audit-transport']))
    result={}
    for key,script,flags in commands:
        value=json.loads(logged([sys.executable,str(home/script),'--home',str(home),*flags],output/key,env=env))
        if not value['passed'] or value['M2_steps_executed']!=0 or value['DOP853_construction_or_step_attempts']!=0:
            raise ValueError('Auditor original no superado sin construcciones/pasos')
        result[key]=value
    return result


def prepare(home,output,label,kind,clock,boundary,capacity=False):
    if kind not in ('transport','boundary','negative') or not re.fullmatch('[A-Z0-9_]+',label):raise ValueError('Solicitud inválida')
    output.mkdir(parents=True,exist_ok=False)
    checked={} if kind=='negative' else audit(home,kind,boundary,output/'auditoria_local')
    if kind=='transport' and checked['transport']['observer_clock']!=clock:raise ValueError('Reloj distinto')
    if kind=='boundary' and checked['boundary']['time']!=clock:raise ValueError('Frontera distinta')
    original=read(home/'MANIFIESTO_NEGATIVO.json')['files'];selected={}
    ignored={'runtime','capsules','recoveries','cache','__pycache__'}
    roots={'science','candidate','outputs','prior','preregistration','ancestor','proofs','analysis','negative','transport',
           'administracion_github_20261028','administracion_continuacion_20261030'}
    for p in sorted(home.rglob('*')):
        rel=p.relative_to(home);name=rel.as_posix()
        if any(x in ignored or x.startswith('.') for x in rel.parts) or p.suffix in ('.tmp','.pyc','.so'):continue
        if p.is_symlink():raise ValueError('Enlace fuera de cargas canónicas')
        if not p.is_file() or name=='MANIFIESTO_NEGATIVO.json':continue
        if len(rel.parts)==1 and name not in original:raise ValueError('Raíz no registrada: '+name)
        if len(rel.parts)>1 and rel.parts[0] not in roots:raise ValueError('Carpeta no registrada: '+name)
        selected[name]=p
    if set(original)-set(selected):raise ValueError('Cargas originales ausentes')
    inventory={n:dict(bytes=p.stat().st_size,sha256=sha(p)) for n,p in selected.items()}
    extra={'ancestor/continuidad_20261030/'+label+'_MANIFIESTO_ORIGEN.json':(home/'MANIFIESTO_NEGATIVO.json').read_bytes()}
    if capacity:
        seed=b'RUNICA_P3_FORWARD_CAPACITY_20261030'
        extra['administracion_continuacion_20261030/CAPACIDAD.bin']=b''.join(hashlib.sha256(seed+i.to_bytes(8,'big')).digest() for i in range(32768))
        extra['administracion_continuacion_20261030/CAPACIDAD.json']=json.dumps(dict(scientific_data=False,bytes=1048576,
            seed=seed.decode(),algorithm='Concatenate SHA256(seed + uint64_be(i)), i=0..32767',M2_steps_executed=0)).encode()
    for n,b in extra.items():
        if n in inventory:raise ValueError('Colisión de historia')
        inventory[n]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    manifest=dict(schema='CP12_P3_FORWARD_CAPSULE_V2',kind=kind,observer_clock=clock,closed_boundary=boundary,
                  capacity_probe=capacity,CP12_closed=False,correction_validated=False,files=inventory,
                  stale_internal_transport_forensic_only=kind=='boundary')
    archive=output/('CP12_CANDIDATO_P3_'+UID+'_'+label+'.zip')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n,p in selected.items():
            b=p.read_bytes()
            if len(b)!=inventory[n]['bytes'] or hashlib.sha256(b).hexdigest()!=inventory[n]['sha256']:raise ValueError('Fuente cambió')
            z.writestr(n,b,compress_type=zipfile.ZIP_STORED if n.endswith('.npz') else zipfile.ZIP_DEFLATED,compresslevel=6)
        for n,b in extra.items():z.writestr(n,b)
        z.writestr('MANIFIESTO_NEGATIVO.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    request=dict(schema='CP12_P3_FORWARD_REQUEST_V2',repository=REPO,release_tag=TAG,kind=kind,
        observer_clock=clock,closed_boundary=boundary,capacity_probe=capacity,source_home=str(home),
        archive_path=str(archive),file_name=archive.name,bytes=archive.stat().st_size,sha256=sha(archive),
        source_inventory={n:inventory[n] for n in selected},archive_inventory=inventory,local_audits=checked,
        conservation_code_sha256=sha(__file__),M2_steps_executed_during_preservation=0,CP12_closed=False)
    if capacity and request['bytes']<=229880902:raise ValueError('Capacidad de prueba insuficiente')
    write(output/'SOLICITUD.json',request);return request


def unchanged(request):
    if sha(request['archive_path'])!=request['sha256']:raise ValueError('ZIP fuente cambiado')
    for n,v in request['source_inventory'].items():
        p=Path(request['source_home'])/n
        if p.stat().st_size!=v['bytes'] or sha(p)!=v['sha256']:raise ValueError('Fuente cambiada: '+n)


def recover(archive,request,output,auditor):
    spec=importlib.util.spec_from_file_location('original_P3_unpack',auditor);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    home=output/'extraido';manifest=m.unpack(archive,home,request['sha256'],request['bytes'])
    if manifest['files']!=request['archive_inventory']:raise ValueError('Inventario recuperado distinto')
    result={} if request['kind']=='negative' else audit(home,request['kind'],request['closed_boundary'],output/'auditoria')
    for key in result:
        if result[key]['state_sha256']!=request['local_audits'][key]['state_sha256']:raise ValueError('Estado recuperado distinto')
    for n,v in manifest['files'].items():
        p=home/n
        if p.stat().st_size!=v['bytes'] or sha(p)!=v['sha256']:raise ValueError('Carga cambió durante auditoría')
    unchanged(request)
    return dict(passed=True,scope='Integridad y auditores declarados; negativo implica sólo integridad.',
        payload_files=len(manifest['files']),exact_manifest_coverage=True,all_payload_hashes_verified_before_and_after=True,
        kind=request['kind'],original_audits=result,recovered_home=str(home),M2_steps_executed=0,CP12_closed=False)


def unwrap(value):
    for _ in range(12):
        if isinstance(value,dict) and 'transfers' in value:return value
        if isinstance(value,dict) and isinstance(value.get('structuredContent'),dict):value=value['structuredContent'];continue
        if isinstance(value,dict) and isinstance(value.get('result'),dict):value=value['result'];continue
        if isinstance(value,dict) and 'content' in value:
            value=json.loads(''.join(x['text'] for x in value['content'] if x.get('type')=='text'));continue
        raise ValueError('Respuesta no reconocida')
    raise ValueError('Respuesta demasiado anidada')


def native(request,output,helpers,auditor):
    output.mkdir();private=output/'privado';private.mkdir(mode=0o700)
    receipt=dict(schema='CP12_P3_FORWARD_NATIVE_RECEIPT_V2',passed=False,upload_outcome='not_started',
                 bytes=request['bytes'],sha256=request['sha256'],observer_clock=request['observer_clock'],CP12_closed=False,M2_steps_executed=0)
    try:
        receipt['upload_outcome']='unknown_requires_reconciliation'
        raw=logged([sys.executable,str(helpers/'library_upload.py')],private/'upload',payload={
            'uploads':[dict(local_path=request['archive_path'],purpose='create_library_file',library_artifact_type='other')]})
        value=json.loads(raw[raw.rfind('\n{"results"'):].strip() if '\n{"results"' in raw else raw)
        items=value.get('results',[])
        if len(items)!=1 or items[0].get('status')!='succeeded':raise RuntimeError('Escritura no acreditada; no repetir automáticamente')
        item=items[0];receipt.update(upload_outcome='confirmed',library_file_id=item['library_file_id'],file_id=item['file_id'],file_name=item['file_name'])
        write(output/'GUARDADO_DURABLE.json',receipt)
        if not item['library_file_id'] or not item['file_id'] or Path(item['file_name']).name!=item['file_name']:raise ValueError('Identidad guardada no canónica')
        sys.path.insert(0,str(helpers));from library_hosted_apps import HostedAppsClient
        dest=output/'descarga';dest.mkdir()
        with (private/'materialize.log').open('w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            response=HostedAppsClient().call_tool('connector_openai_library','prepare_materialize',dict(items=[dict(
                library_file_id=item['library_file_id'],file_id=item['file_id'],file_name=item['file_name'])],destination=dict(directory=str(dest))))
        value=unwrap(response)
        if len(value.get('transfers',[]))!=1 or value.get('unavailable_items'):raise ValueError('Recuperación no acreditada')
        transfer=value['transfers'][0]
        if transfer.get('workspace_path'):
            downloaded=Path(transfer['workspace_path']).resolve()
            if not downloaded.is_relative_to(dest):raise ValueError('Recuperación no independiente')
            logged([sys.executable,str(helpers/'library_file_transfer.py'),'apply-xattrs',str(downloaded)],private/'xattrs',payload=transfer)
        else:
            downloaded=dest/item['file_name'];logged([sys.executable,str(helpers/'library_file_transfer.py'),'materialize',str(downloaded)],private/'transfer',payload=transfer)
        checked=recover(downloaded,request,output,auditor)
        receipt.update(passed=True,recovery=checked,native_full_cycle_performed_in_this_invocation=True);return receipt
    except BaseException as error:
        receipt.update(error_type=type(error).__name__,automatic_retry_permitted=False);raise
    finally:write(output/'RESULTADO_TRANSITO.json',receipt)


def public(request,metadata,output,auditor):
    url='https://github.com/'+REPO+'/releases/download/'+TAG+'/'+request['file_name']
    if any([metadata['name']!=request['file_name'],metadata['size']!=request['bytes'],metadata.get('digest')!='sha256:'+request['sha256'],metadata['browser_download_url']!=url]):raise ValueError('Adjunto distinto')
    output.mkdir();archive=output/request['file_name']
    with urllib.request.urlopen(url,timeout=60) as source,archive.open('xb') as dest:shutil.copyfileobj(source,dest,1024*1024)
    receipt=dict(schema='CP12_P3_FORWARD_PUBLIC_RECOVERY_V2',passed=True,github_asset_id=metadata['id'],
        bytes=request['bytes'],sha256=request['sha256'],observer_clock=request['observer_clock'],kind=request['kind'],
        recovery=recover(archive,request,output,auditor),M2_steps_executed=0,CP12_closed=False)
    write(output/'ACEPTACION.json',receipt);return receipt


def preserve(home,output,label,kind,clock,boundary,helpers,auditor,capacity=False):
    request=prepare(home,output,label,kind,clock,boundary,capacity)
    temporary=native(request,output/'transito',helpers,auditor)
    print(json.dumps(dict(stage='PUBLICACION_GITHUB_REQUERIDA',request=str(output/'SOLICITUD.json'),
        archive=request['archive_path'],bytes=request['bytes'],sha256=request['sha256'],observer_clock=clock,
        library_file_id=temporary['library_file_id'])),flush=True)
    path=output/'ASSET_GITHUB.json';deadline=time.monotonic()+3600
    while not path.exists():
        if time.monotonic()>deadline:raise TimeoutError('Publicación pendiente; no repetir escritura ni física')
        time.sleep(.5)
    final=public(request,read(path),output/'github',auditor)
    result=dict(schema='CP12_P3_FORWARD_COMBINED_PRESERVATION_V2',passed=True,observer_clock=clock,
        closed_boundary=boundary,kind=kind,capacity_probe=capacity,native=temporary,github=final,
        source_archive_and_payload_unchanged=True,M2_steps_executed_during_preservation=0,CP12_closed=False)
    write(output/'ACEPTACION_COMBINADA.json',result);return result
