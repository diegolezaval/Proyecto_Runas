"""Durable administrative CP12 coordinator. Original physics and gates only."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[2]
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.path.insert(0,str(ROOT/'herramientas'))
import gestionar_respaldo_CP12 as manager
import capsula_git_CP12 as transport

BRANCH='ciencia/cp12-causal-chi'
REMOTE='https://github.com/diegolezaval/Proyecto_Runas.git'
SUPPORT=ROOT/'trazabilidad/CP12_reconstruccion'
STORE=ROOT/'trazabilidad/CP12_respaldos_Git'
ADMIN=ROOT/'trazabilidad/CP12_ejecucion_durable'


def read(path):return json.loads(path.read_text())


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def label(time_):return 'tau'+str(int(time_)).zfill(4)


def command(args,cwd=ROOT,input_=None):
    result=subprocess.run(args,cwd=cwd,input=input_,text=True,capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr+'\n'+result.stdout[-6000:])
    return result.stdout.strip()


def git(*args,cwd=ROOT,input_=None):return command(['git',*args],cwd,input_)


def commit_paths(paths,message):
    if git('branch','--show-current')!=BRANCH:raise ValueError('Working branch only')
    remote=git('ls-remote','--heads','origin',BRANCH).split()[0]
    if git('rev-parse','HEAD')!=remote:raise ValueError('Unexpected concurrent branch update; no overwrite')
    git('add','-f','--',*[str(p.relative_to(ROOT)) for p in paths])
    allowed=('trazabilidad/CP12_reconstruccion/','trazabilidad/CP12_respaldos_Git/',
             'trazabilidad/CP12_ejecucion_durable/','validacion/P06/no_radial/CP12_interpretacion/')
    staged=git('diff','--cached','--name-only').splitlines()
    if not staged or any(not p.startswith(allowed) for p in staged):raise ValueError('Invalid administrative commit scope')
    git('-c','user.name=CP12 scientific checkpoint worker','-c','user.email=cp12-worker@users.noreply.github.com',
        'commit','-m',message)
    git('push','origin','HEAD:refs/heads/'+BRANCH)
    return git('rev-parse','HEAD')


def recipe_refs(recipe):
    refs=list(recipe['prefix'])+list(recipe['tail'])
    for member in recipe['members']:refs.extend(member['compressed'])
    return refs


def recover_commit(commit,time_,expected_sha,workspace):
    workspace.mkdir(parents=True,exist_ok=True)
    if not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError('Actual immutable Git commit required')
    recipe_path=Path('trazabilidad/CP12_respaldos_Git')/(label(time_)+'.json')
    download=workspace/'remote_checkout'
    # Fresh object database: no local Git objects can satisfy this retrieval.
    command(['git','clone','--filter=blob:none','--no-checkout','--depth=1','--branch',BRANCH,REMOTE,str(download)])
    git('fetch','--depth=1','origin',commit,cwd=download)
    recipe=json.loads(git('show',commit+':'+recipe_path.as_posix(),cwd=download))
    if recipe['time']!=time_ or recipe['run_id']!=manager.RUN_ID or recipe['original_zip_sha256']!=expected_sha:
        raise ValueError('Permanent capsule does not match certificate')
    paths={recipe_path.as_posix()}
    for ref in recipe_refs(recipe):
        path=Path(ref['path'])
        if path.is_absolute() or '..' in path.parts or not path.is_relative_to('trazabilidad/CP12_respaldos_Git/objetos'):
            raise ValueError('Invalid capsule object path')
        paths.add(path.as_posix())
    git('sparse-checkout','init','--no-cone',cwd=download)
    git('sparse-checkout','set','--no-cone','--stdin',cwd=download,input_='\n'.join('/'+p for p in sorted(paths))+'\n')
    git('checkout','--detach',commit,cwd=download)
    if git('rev-parse','HEAD',cwd=download)!=commit:raise ValueError('Wrong recovered commit')
    original_root=transport.ROOT
    try:
        transport.ROOT=download
        archive=workspace/('Proyecto_Runas_CP12_REINICIO_'+label(time_)+'.zip')
        transport.restore(download/recipe_path,archive)
    finally:transport.ROOT=original_root
    verification=manager.verify_download(archive,expected_sha,workspace/'independent_extraction')
    if not verification['passed'] or not verification['all_payload_hashes_verified']:
        raise ValueError('Permanent capsule failed original verification')
    actual=verification['independent_extracted_check']
    if not actual['passed'] or actual['time']!=time_:raise ValueError('Invalid independent restart')
    verification['permanent_Git_commit']=commit
    return verification


def validate_proof(proof,time_):
    if proof.get('passed') is not True or proof['time']!=time_ or proof['download_verification'].get('passed') is not True:
        raise ValueError('No verified complete previous backup')
    if not proof['download_verification'].get('all_payload_hashes_verified'):
        raise ValueError('Payload coverage not verified')
    if not proof['download_verification']['independent_extracted_check'].get('passed'):
        raise ValueError('No independent original restart audit')
    if proof.get('storage_backend')=='GIT':
        if not re.fullmatch('[0-9a-f]{40}',proof.get('permanent_Git_commit','')):
            raise ValueError('Permanent Git identity missing')
    elif not proof.get('library_file_id'):raise ValueError('Permanent identity missing')


def install_restart(verification,proof,time_):
    actual=verification['independent_extracted_check']
    for key in ['state_sha256','receipt_sha256','configuration_sha256']:
        if actual[key]!=proof[key]:raise ValueError('Recovered state differs from certificate: '+key)
    project=Path(verification['extracted_path']);manifest=read(project/'MANIFIESTO_REINICIO_CP12.json')
    if manifest['time']!=time_ or manifest['original_pair']!=manager.RUN.relative_to(ROOT).as_posix():
        raise ValueError('Incorrect pair or boundary in recovered manifest')
    for rel in [manifest['original_pair'],manifest['audit']]:
        destination=ROOT/rel
        if destination.exists():shutil.rmtree(destination)
        shutil.copytree(project/rel,destination)
    for name,key in [('CP12_par_estado.npz','state_sha256'),('procedencia.json','receipt_sha256'),('configuration.json','configuration_sha256')]:
        if sha(manager.RUN/name)!=proof[key]:raise ValueError('Installed restart differs from verified bytes')


def descriptor(time_,proof):
    if proof.get('storage_backend')=='GIT':return proof['permanent_Git_commit']
    handoff=read(ADMIN/'activacion.json')
    if handoff['start_time']!=time_ or handoff['zip_sha256']!=proof['zip_sha256']:
        raise ValueError('No explicit Git handoff for legacy certificate')
    return handoff['permanent_Git_commit']


def certify_recovered_gap(target):
    """A published capsule survives even if its verification job disconnected."""
    recipe_path=STORE/(label(target)+'.json')
    if not recipe_path.exists():return False
    recipe=read(recipe_path);previous=read(SUPPORT/'respaldos'/(label(target-8)+'.json'))
    validate_proof(previous,target-8)
    commit=git('rev-parse','HEAD')
    with tempfile.TemporaryDirectory(prefix='cp12_complete_uncertified_') as directory:
        result=recover_commit(commit,float(target),recipe['original_zip_sha256'],Path(directory))
        project=Path(result['extracted_path']);actual=result['independent_extracted_check']
        saved_previous=read(project/'trazabilidad/CP12_reconstruccion/respaldos'/(label(target-8)+'.json'))
        if saved_previous['zip_sha256']!=previous['zip_sha256']:raise ValueError('Published capsule has a different predecessor')
        counters=read(project/'trazabilidad/CP12_reconstruccion/controles_contadores'/label(target)/'resultados.json')
        key=(manager.RUN/'CP12_par_estado.npz').relative_to(ROOT).as_posix()
        if not counters['passed'] or counters['input_sha256'][key]!=actual['state_sha256']:
            raise ValueError('Published capsule has no matching passed counter audit')
        target_proof=SUPPORT/'respaldos'/(label(target)+'.json')
        write_new(target_proof,dict(schema_version='1.0.0',passed=True,time=float(target),
            verified_at=manager.prov.now(),storage_backend='GIT',permanent_Git_commit=commit,
            recipe=recipe_path.relative_to(ROOT).as_posix(),zip_sha256=recipe['original_zip_sha256'],
            zip_bytes=recipe['original_zip_bytes'],download_verification=result,
            **{k:actual[k] for k in ['state_sha256','receipt_sha256','configuration_sha256']},
            previous_verified_backup=previous['zip_sha256'],original_protocol_unchanged=True,
            scientific_checkpoint='CP11_DIAGNOSTICO_RADIAL_CHI',
            recovery='Complete immutable capsule recovered; no repeated physical segment',
            administrative_code_sha256=sha(Path(__file__))))
    commit_paths([target_proof],'Verificar cápsula CP12 ya publicada sin repetir evolución '+label(target))
    return True


def segment(target):
    if target%8 or not 32<=target<=160:raise ValueError('Original boundaries only, after explicit local handoff')
    manager.original_identity()
    target_proof=SUPPORT/'respaldos'/(label(target)+'.json')
    if not target_proof.exists() and certify_recovered_gap(target):return
    if target_proof.exists():
        proof=read(target_proof);validate_proof(proof,target)
        with tempfile.TemporaryDirectory(prefix='cp12_existing_verified_') as directory:
            recovered=recover_commit(descriptor(target,proof),target,proof['zip_sha256'],Path(directory))
            actual=recovered['independent_extracted_check']
            if any(actual[k]!=proof[k] for k in ['state_sha256','receipt_sha256','configuration_sha256']):
                raise ValueError('Previously certified boundary no longer reproduces')
        print(json.dumps(dict(event='SKIP_ALREADY_PERMANENTLY_VERIFIED',time=target)),flush=True)
        return
    previous=target-8;proof=read(SUPPORT/'respaldos'/(label(previous)+'.json'));validate_proof(proof,previous)
    with tempfile.TemporaryDirectory(prefix='cp12_previous_remote_') as directory:
        recovered=recover_commit(descriptor(previous,proof),previous,proof['zip_sha256'],Path(directory))
        install_restart(recovered,proof,previous)
        before=SUPPORT/'segmentos_Git'/(label(target)+'_antes.json')
        write_new(before,dict(target=target,previous=previous,recorded_before_execution=manager.prov.now(),
            original_run_id=manager.RUN_ID,original_full_identity=manager.original_identity()[2],
            previous_certificate=proof,fresh_remote_recovery=recovered,
            administrative_code_sha256=sha(Path(__file__)),
            preregistration_sha256=sha(ROOT/'informes/PRERREGISTRO_EJECUCION_DURABLE_CP12.md'),
            physical_protocol_changes=False,observer_changes=False,correction_tested=False))
    # Same original adapter and executor; Git certificate replaces only the
    # legacy storage-ID check, after the stricter fresh remote retrieval above.
    for name,key in [('CP12_par_estado.npz','state_sha256'),('procedencia.json','receipt_sha256'),('configuration.json','configuration_sha256')]:
        if sha(manager.RUN/name)!=proof[key]:raise ValueError('Restart changed before original execution')
    if float(manager.physical.source_state(manager.RUN/'CP12_par_estado.npz')['time'])!=previous:
        raise ValueError('Wrong previous physical time')
    manager.adapter.configure(manager.ORIGINAL,'par_instrumentado')
    manager.adapter.recover_if_needed(manager.ORIGINAL,'par_instrumentado')
    manager.prov.execute(manager.ORIGINAL,'par_instrumentado',stop_at=float(target),resume=True)
    manager.audit_case(float(target))
    command([sys.executable,str(SUPPORT/'auditar_contadores_CP12.py'),'--time',str(target)])
    with tempfile.TemporaryDirectory(prefix='cp12_new_boundary_') as directory:
        workspace=Path(directory);archive=workspace/('Proyecto_Runas_CP12_REINICIO_'+label(target)+'.zip')
        packaged=manager.package(float(target),archive)
        recipe=transport.pack(archive)
        frozen_hashes=dict(state_sha256=sha(manager.RUN/'CP12_par_estado.npz'),
                           receipt_sha256=sha(manager.RUN/'procedencia.json'),
                           configuration_sha256=sha(manager.RUN/'configuration.json'))
        commit=commit_paths([STORE,before,SUPPORT/'controles_contadores'/label(target)],
                            'Conservar cápsula completa CP12 '+label(target)+' antes de avanzar')
        verified=recover_commit(commit,float(target),packaged['sha256'],workspace/'retrieved')
        actual=verified['independent_extracted_check']
        for key,value in frozen_hashes.items():
            if actual[key]!=value:raise ValueError('Permanent backup differs from completed boundary')
        if any(sha(manager.RUN/name)!=frozen_hashes[key] for name,key in [('CP12_par_estado.npz','state_sha256'),('procedencia.json','receipt_sha256'),('configuration.json','configuration_sha256')]):
            raise ValueError('Live state changed during permanent backup')
        write_new(target_proof,dict(schema_version='1.0.0',passed=True,time=float(target),
            verified_at=manager.prov.now(),storage_backend='GIT',permanent_Git_commit=commit,
            recipe=recipe.relative_to(ROOT).as_posix(),zip_sha256=packaged['sha256'],
            zip_bytes=packaged['bytes'],download_verification=verified,**frozen_hashes,
            previous_verified_backup=proof['zip_sha256'],original_protocol_unchanged=True,
            scientific_checkpoint='CP11_DIAGNOSTICO_RADIAL_CHI',
            administrative_code_sha256=sha(Path(__file__))))
    final_commit=commit_paths([target_proof],'Verificar recuperación permanente CP12 '+label(target))
    print(json.dumps(dict(event='BOUNDARY_PERMANENTLY_VERIFIED',time=target,
                         backup_commit=commit,verification_commit=final_commit)),flush=True)


def interpret():
    proof=read(SUPPORT/'respaldos/tau0160.json');validate_proof(proof,160)
    with tempfile.TemporaryDirectory(prefix='cp12_final_remote_') as directory:
        recovered=recover_commit(descriptor(160,proof),160,proof['zip_sha256'],Path(directory))
        install_restart(recovered,proof,160)
    protocol=ROOT/'datos/interpretacion_CP12.json'
    folder=manager.register_full(protocol,'interpretacion_causal')
    manager.prov.execute(protocol,'interpretacion_causal',resume=True)
    if not manager.prov.verify_receipt(folder/'procedencia.json')['passed']:
        raise ValueError('Offline interpretation receipt failed')
    commit=commit_paths([folder],'Publicar presupuesto causal CP12 y puertas prerregistradas para revisión científica')
    print(json.dumps(dict(event='PREREGISTERED_BUDGET_REVIEW_AVAILABLE',commit=commit,
                         scientific_closure_requires_review=True,correction_tested=False)),flush=True)


def check_handoff():
    manager.original_identity()
    handoff=read(ADMIN/'activacion.json');time_=handoff['start_time']
    proof=read(SUPPORT/'respaldos'/(label(time_)+'.json'));validate_proof(proof,time_)
    if handoff['zip_sha256']!=proof['zip_sha256']:raise ValueError('Handoff capsule mismatch')
    with tempfile.TemporaryDirectory(prefix='cp12_Git_zero_step_') as directory:
        result=recover_commit(handoff['permanent_Git_commit'],time_,proof['zip_sha256'],Path(directory))
        actual=result['independent_extracted_check']
        for key in ['state_sha256','receipt_sha256','configuration_sha256']:
            if actual[key]!=proof[key]:raise ValueError('Original zero-step handoff differs: '+key)
    record=ADMIN/('verificacion_traslado_'+os.environ['GITHUB_RUN_ID']+'_'+os.environ.get('GITHUB_RUN_ATTEMPT','1')+'.json')
    write_new(record,dict(passed=True,M2_steps=0,time=time_,checked_at=manager.prov.now(),
        original_full_identity=manager.original_identity()[2],fresh_remote_recovery=result,
        scientific_closure=False,correction_tested=False))
    commit=commit_paths([record],'Verificar traslado CP12 sin pasos M2 ni cambios científicos')
    print(json.dumps(dict(event='ORIGINAL_ZERO_STEP_HANDOFF_VERIFIED',commit=commit,time=time_)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--target',type=int);parser.add_argument('--interpret',action='store_true')
    parser.add_argument('--check-handoff',action='store_true')
    parser.add_argument('--recover-only-commit');parser.add_argument('--time',type=float);parser.add_argument('--zip-sha256')
    parser.add_argument('--workspace',type=Path);args=parser.parse_args()
    try:
        if args.recover_only_commit:
            print(json.dumps(recover_commit(args.recover_only_commit,args.time,args.zip_sha256,args.workspace)))
        elif args.check_handoff:check_handoff()
        elif args.interpret:interpret()
        elif args.target is not None:segment(args.target)
        else:parser.error('Specify an administrative operation')
    except Exception:
        details=dict(failed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),target=args.target,
            error=traceback.format_exc(),scientific_closure=False,main_modified=False)
        incident=SUPPORT/'incidentes'/('GitHub_'+os.environ.get('GITHUB_RUN_ID','local')+'_'+os.environ.get('GITHUB_RUN_ATTEMPT','1')+'_'+str(args.target))
        try:
            write_new(incident/'fallo.json',details)
            for name in ['procedencia.json','ejecucion.log','CP12_par_progreso.json']:
                source=manager.RUN/name
                if source.exists():shutil.copyfile(source,incident/name)
            if os.environ.get('GITHUB_ACTIONS')=='true':commit_paths([incident],'Conservar parada técnica CP12 sin cerrar la etapa')
        except Exception:print(traceback.format_exc(),file=sys.stderr)
        raise
