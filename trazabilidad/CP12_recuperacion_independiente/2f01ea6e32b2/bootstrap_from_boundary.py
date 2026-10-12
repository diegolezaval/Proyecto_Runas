"""Administrative recovery from a verified permanent boundary, without M2 steps."""
from pathlib import Path
import copy, datetime, hashlib, json, os, shutil, sys, zipfile

def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def read(p): return json.loads(p.read_text())
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    assert not p.exists(), str(p)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

plan=read(Path(__file__).parent/'new_recovery_plan.json')
home=Path(plan['home']);parent=Path(plan['parent_extracted'])
t=plan['initial_frontier'];assert t==48
assert sha(Path(plan['parent_capsule']))==plan['parent_capsule_sha256']
m=read(parent/'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json')
assert m['time']==t and m['execution_uuid']==plan['parent_uuid']
expected=set(m['files'])
actual={p.relative_to(parent).as_posix() for p in parent.rglob('*') if p.is_file() and p.name!='MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'}
assert expected==actual
for n,v in m['files'].items():
    p=parent/n
    assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'], n
audited=read(Path(plan['parent_audit']))
assert audited['passed'] and all(audited['tests'].values()) and audited['time']==t
assert audited['state_sha256']==m['files']['science/'+m['run_relative']+'/CP12_par_estado.npz']['sha256']
for d in ['runtime/tmp','runtime/library','capsules','recoveries','proofs','preregistration','ancestry']:
    (home/d).mkdir(parents=True,exist_ok=True)
root=home/'science';shutil.copytree(parent/'science',root,copy_function=shutil.copyfile)
for p in root.rglob('*'):
    if p.is_file():
        assert not p.is_symlink() and p.stat().st_nlink==1
        p.chmod(0o444)
for p in sorted(root.glob('validacion/P06/no_radial/CP12/par_*'),reverse=True):
    if p.is_dir():
        for d in sorted(p.rglob('*'),reverse=True):
            if d.is_dir():d.chmod(0o555)
        p.chmod(0o555)
for n in ['library_download.py','library_upload.py','library_hosted_apps.py','library_file_transfer.py']:
    shutil.copyfile(Path(plan['library_helpers'])/n,home/'runtime/library'/n)
shutil.copyfile(parent/'execute_guarded.py',home/'execute_guarded.py')
source=(parent/'coordinator.py').read_text()
assert source.count('    start=24\n')==1
(home/'coordinator.py').write_text(source.replace('    start=24\n','    start=int(meta[\'initial_frontier\'])\n'))
assert 'range(start+8,161,8)' in (home/'coordinator.py').read_text()
shutil.copyfile(Path(__file__),home/'bootstrap_from_boundary.py')
if (parent/'analysis').exists():
    shutil.copytree(parent/'analysis',home/'analysis',copy_function=shutil.copyfile)
sys.path.insert(0,str(root/'herramientas'))
import gestionar_respaldo_CP12 as mgr
import ejecutar_con_procedencia as prov
import numpy,scipy,matplotlib,threadpoolctl
_,_,identity,original_id=mgr.original_identity()
assert original_id=='a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
assert identity==read(parent/'preregistration/identidad_cientifica.json')
write(home/'preregistration/identidad_cientifica.json',identity)
info=dict(execution_uuid=plan['execution_uuid'],branch=plan['branch'],home=str(home),root=str(root),ancestor_time=t,ancestor_state_sha256=audited['state_sha256'],ancestor_zip_sha256=plan['parent_capsule_sha256'],ancestor_pair=m['run_relative'],ancestor_payload_files_verified=len(expected),created_at=now(),old_executor_assumed_potentially_active=True,prior_recoveries_assumed_potentially_active=True,old_executor_access_attempts=0,parent_uuid=plan['parent_uuid'],parent_run_id=m['execution_run_id'],parent_commit=plan['parent_commit'],original_tau24_state_sha256='508f32f167abd6211b330d707172612a47fec1f2701577b1a9939d8390fbc529')
prereg=f'''# CP12: recuperación aislada desde τ48

Identidad de instancia {info['execution_uuid']}; rama {info['branch']}. Se continúa desde la cápsula independiente permanente τ48, SHA256 {info['ancestor_zip_sha256']}, estado {info['ancestor_state_sha256']}, 388 archivos íntegros. Su auditor original pasa, con 121 observaciones CP10 exactas y recarga sin avance. La ascendencia científica τ24 se conserva y los segmentos certificados hasta τ48 no se repiten.

El entorno actual no conserva la copia local ni una sesión consultable de la recuperación ab914d1d0470. Eso no prueba terminación. Todos los ejecutores anteriores se consideran potencialmente activos, no autoritativos y fuera de nuestro control. No se intenta consultar, recuperar, controlar ni cancelar al ejecutor original ni contactar soporte. Cualquier resultado futuro anterior requiere auditoría y atribución separadas.

Se copian sólo bytes verificados, con raíces, UUID, identidad de ejecución, rama, recibo, salida, bloqueos, temporales, cachés y nombres de cápsula propios. Los estados y recibos heredados quedan de sólo lectura; no hay enlaces. Cada operación permanente crea un archivo nuevo. Los programas antiguos tienen destinos fijos ajenos a éstos. La garantía de aislamiento se refiere a esos programas legítimos, no a un actor malicioso con privilegios del sistema. Main, el PR #2 y las ramas y cápsulas anteriores quedan intactos. No se utiliza GitHub Actions.

Las catorce fuentes numéricas y la configuración original conservan exactamente sus hashes. M2, Θ, DOP853, tolerancias, mallas, observadores 7/6 con paso .01 y puerta del 2 % permanecen idénticos. BLAS selecciona SkylakeX con un hilo observado, sin forzar dispatch. Sólo cambian el destino administrativo y la frontera inicial del coordinador (de constante 24 a metadato 48). Se invoca run_pair original; la identidad del protocolo ancestral se rotula separadamente de la identidad nueva. Los contadores y observaciones incluyen la ascendencia, no se atribuyen todos a este trabajador.

Antes del primer paso se crea, descarga, verifica y audita una cápsula nueva τ48. Cada frontera de ocho unidades se conserva y recarga permanentemente antes de pasar al siguiente tramo, hasta τ160. Se comprueban prefijo CP10, controles, balances, identidades, simetrías y observadores; en τ160 se exige reproducción final CP10 exacta. Un fallo conserva evidencia y detiene el avance, sin reintentos automáticos ni duplicación de procesos en esta identidad. El guardián propio registra la salida sólo si la observa directamente. Un latido no es una frontera certificada; la supervisión no promete durabilidad del entorno de Work.

Al llegar a τ160 se aplica la lectura causal original con sus tres ventanas y umbrales, sin cambiar las puertas ni forzar dominancia. La lectura separa operador, fuente no lineal y propagación e informa los límites de la atribución de realimentación. Se conservan los diagnósticos pasivos heredados y sus resultados negativos, incluido el candidato que conserva la masa original pero sigue mostrando orden dos y modos que empeoran. El residuo sobre r²Y₂m no basta para explicar el error global. Ninguna corrección se aplica a estas trayectorias. Una campaña de corrección requiere causa suficiente, derivación independiente y prerregistro de convergencia, conservación, estabilidad y robustez. CP12 permanece abierto.
'''
(home/'preregistration/PRERREGISTRO.md').write_text(prereg)
layer=dict(kind='INDEPENDENT_ISOLATED_RECOVERY_CP12',instance_uuid=info['execution_uuid'],ancestor_time=t,ancestor_state_sha256=info['ancestor_state_sha256'],ancestor_capsule_sha256=info['ancestor_zip_sha256'],ancestor_manifest_sha256=sha(parent/'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'),ancestor_receipt_sha256=audited['receipt_sha256'],parent_execution_run_id=m['execution_run_id'],supervision_source_sha256=sha(home/'coordinator.py'),guard_source_sha256=sha(home/'execute_guarded.py'),preregistration_sha256=sha(home/'preregistration/PRERREGISTRO.md'),previous_future_results_authoritative=False)
new_identity=copy.deepcopy(identity);new_identity['recovery_layer']=layer
run_id=hashlib.sha256(prov.canonical(new_identity)).hexdigest()
relative='validacion/P06/no_radial/CP12/par_recuperacion_independiente__'+run_id
run=root/relative;run.mkdir()
ancestor=root/m['run_relative']
for name in ['configuration.json','CP12_par_estado.npz','CP12_par_progreso.json']:
    shutil.copyfile(ancestor/name,run/name);(run/name).chmod(0o644)
assert sha(run/'CP12_par_estado.npz')==audited['state_sha256']
receipt=dict(schema_version='1.0.0',run_id=run_id,case='recuperacion_independiente_CP12',identity=new_identity,created_at=now(),status='PAUSADA_REANUDABLE',segments=[],configuration_sha256=sha(run/'configuration.json'),source_snapshots={},output_hashes={p.name:sha(p) for p in run.iterdir() if p.is_file()},execution_origin=dict(kind='INDEPENDENT_ISOLATED_RECOVERY_FROM_VERIFIED_TAU48',original_lost_receipt_recreated=False,prior_attempt_receipt_recreated=False,original_protocol_unchanged=True,ancestor_receipt_sha256=audited['receipt_sha256'],ancestor_execution_run_id=m['execution_run_id'],inherited_segments_not_claimed_as_this_execution=True,registration_time_new_segments=0),comparisons_and_decision='Independent recovery from certified tau48; all tau0-to-48 state and counters are inherited scientific ancestry. CP12 remains open.')
prov.write(run/'procedencia.json',receipt)
info.update(execution_run_id=run_id,run_relative=relative)
write(home/'preregistration/ubicacion.json',info)
meta=dict(execution_uuid=info['execution_uuid'],execution_run_id=run_id,branch=info['branch'],run_relative=relative,supervision_source_sha256=layer['supervision_source_sha256'],guard_source_sha256=layer['guard_source_sha256'],preregistration_sha256=layer['preregistration_sha256'],ancestor_receipt_retained_read_only=True,initial_frontier=t)
write(home/'preregistration/nueva_identidad.json',meta)
write(home/'ancestry/tau0048_parent_verification.json',dict(time=t,zip_sha256=info['ancestor_zip_sha256'],zip_bytes=Path(plan['parent_capsule']).stat().st_size,manifest_sha256=layer['ancestor_manifest_sha256'],payloads=len(expected),all_payload_hashes_verified=True,independent_original_audit=audited,passed=True,previous_worker_termination_assumed=False))
threads=threadpoolctl.threadpool_info()
assert threads and all(p['num_threads']==1 and p['architecture']=='SkylakeX' for p in threads)
preflight=dict(original_scientific_identity_exact=True,scientific_source_count=len(identity['code_hashes']),observed_BLAS_threads_one=True,observed_dispatch_SkylakeX=True,dispatch_not_forced=not os.environ.get('OPENBLAS_CORETYPE'),configuration_sha256=sha(run/'configuration.json'),state_sha256=sha(run/'CP12_par_estado.npz'),packages={p.__name__:p.__version__ for p in [numpy,scipy,matplotlib,threadpoolctl]},M2_steps=0,initial_frontier=t)
write(home/'preregistration/preflight.json',preflight)
write(home/'preregistration/aislamiento.json',dict(new_uuid_and_run_id=True,new_branch=info['branch'],filesystem_roots_disjoint_from_prior_attempts=True,no_symlinks_or_hardlinks=all(not p.is_symlink() and p.stat().st_nlink==1 for p in root.rglob('*') if p.is_file()),scientific_and_configuration_bytes_original=True,ancestor_receipts_immutable=True,new_receipt_and_output_path=True,new_cache_and_temporary_paths=True,Library_operation_create_only_with_instance_prefix=True,old_executor_control_or_activity_queries=0,physical_source_changes=0,M2_steps=0,passed=True))
write(home.parent/('CP12_RI_'+info['execution_uuid']+'_LOCATION.json'),info)
print(json.dumps(dict(location=info,preflight=preflight),ensure_ascii=False))
