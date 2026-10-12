"""Prepare a new, independently named recovery using only the certified scientific ZIP."""
from pathlib import Path
import copy, datetime, hashlib, json, os, shutil, sys, zipfile

def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
home=Path(__file__).parent.resolve(); workspace=home.parent
info=json.loads((home/'preregistration/ubicacion.json').read_text())
archive=workspace/'respaldos_actuales/Proyecto_Runas_CP12_REINICIO_tau0024.zip'
assert sha(archive)==info['ancestor_zip_sha256']
root=home/'science';root.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    manifest_bytes=z.read('Proyecto_Runas/MANIFIESTO_REINICIO_CP12.json')
    manifest=json.loads(manifest_bytes)
    assert manifest['time']==24 and len(manifest['files'])==329
    expected={'Proyecto_Runas/'+n for n in manifest['files']}|{'Proyecto_Runas/MANIFIESTO_REINICIO_CP12.json'}
    assert {n for n in z.namelist() if not n.endswith('/')}==expected
    for n,item in manifest['files'].items():
        p=Path(n);assert not p.is_absolute() and '..' not in p.parts
        data=z.read('Proyecto_Runas/'+n)
        assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
        destination=root/p;destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists(): assert destination.read_bytes()==data
        else: destination.write_bytes(data)
        destination.chmod(0o444)
    if (root/'MANIFIESTO_REINICIO_CP12.json').exists(): assert (root/'MANIFIESTO_REINICIO_CP12.json').read_bytes()==manifest_bytes
    else: (root/'MANIFIESTO_REINICIO_CP12.json').write_bytes(manifest_bytes)
    (root/'MANIFIESTO_REINICIO_CP12.json').chmod(0o444)
ancestor_pair=manifest['original_pair']
for p in sorted((root/ancestor_pair).rglob('*'),reverse=True):
    if p.is_dir(): p.chmod(0o555)
(root/ancestor_pair).chmod(0o555)
prior=workspace/'CP12_RI_ab8034463e964548a4af5e5e2f572c13'
source=prior/'coordinator.py'
assert sha(source)=='9e9a377cc06493d3cf08b62e4854654a99feedee2b227e45fbc5da71b8351a2f'
shutil.copyfile(source,home/'coordinator.py')
assert all(not p.is_symlink() and p.stat().st_nlink==1 for p in root.rglob('*') if p.is_file())
sys.path.insert(0,str(root/'herramientas'))
import gestionar_respaldo_CP12 as mgr
import ejecutar_con_procedencia as prov
import numpy,scipy,matplotlib,threadpoolctl
_,_,identity,_=mgr.original_identity()
assert hashlib.sha256(prov.canonical(identity)).hexdigest()==manifest['run_id']
write(home/'preregistration/identidad_cientifica.json',identity)
prereg=f'''# Recuperación independiente CP12, intento ab914d1d0470

Instancia {info['execution_uuid']}; rama {info['branch']}. CP12 permanece abierto.
Se usa exclusivamente el reinicio científico íntegro τ24: ZIP {sha(archive)}, 329 archivos, estado {info['ancestor_state_sha256']}. No se integra 0→24.

La ejecución original y el intento independiente anterior ab8034463e96 se consideran potencialmente activos, no autoritativos y fuera de esta ejecución. La sesión disponible del intento anterior dejó de ser consultable; el latido de τ26,06 no es un reinicio ni prueba de terminación. No hay τ32 certificado accesible. Se conserva todo su espacio sin cambios y no se le consulta de nuevo. Cualquier resultado futuro suyo permanece ajeno hasta una auditoría separada. Repetir 24→32 en este espacio es indispensable para recuperar un segmento que nunca fue certificado; no se repiten segmentos certificados.

Los destinos nuevos tienen UUID, identidad y rama propios; carpeta científica, salidas, recibos, bloqueos, cachés, temporales y nombres de cápsulas distintos de ambos espacios previos. Se copian bytes del ZIP verificado, nunca enlaces; todas sus evidencias heredadas son sólo lectura. Las operaciones permanentes crean archivos nuevos, no reemplazan ninguno anterior. Main y PR2 permanecen intactos; no se usa Actions. Los trabajadores anteriores tienen destinos fijos y no escriben en esta instancia. La garantía se refiere a esos trabajadores legítimos, no a un actor malicioso con privilegios del sistema.

Se invoca exactamente run_pair original; configuración, catorce fuentes, M2, Θ, DOP853, tolerancias, mallas, observadores 7/6 y puerta física del 2 % quedan intactos. BLAS debe seleccionar SkylakeX de un hilo sin forzar su tipo. Sólo el destino administrativo RUN del auditor se dirige a la salida nueva, con su identidad científica ancestral rotulada como tal.

Antes del cálculo se crea, recupera y audita permanentemente una cápsula independiente τ24. Cada frontera original de ocho unidades sigue el mismo procedimiento antes del avance siguiente, hasta τ160. Se conserva el prefijo CP10, controles, balances, identidades de defecto, simetrías, observadores y recarga original sin avance. Toda comparación final CP10 deberá ser exacta. Un fallo detiene el trabajador, conserva la evidencia y no genera un reintento automático.

Un guardián administrativo con lanzamiento único espera al proceso propio y registra su código de salida o señal cuando puede observarlos directamente. Sus datos privados del entorno quedan excluidos de cápsulas y Git. El lanzamiento se desacopla de la sesión del comando interactivo; ello no afirma durabilidad del entorno si la plataforma lo destruye. Los latidos cada 30 segundos observan sólo reloj y contadores, nunca alteran el estado. La supervisión actual acompaña el cálculo hasta fronteras verificadas y no atribuye latidos a resultados certificados.

En τ160 se aplican las ventanas y puertas causales originales para separar operador radial, fuente, propagación y realimentación. El armónico regular r²Y₂m se estudia con análisis y diagnósticos pasivos; no basta por sí solo para atribuir el error. Una corrección física exige identificación suficiente, derivación y pruebas independientes prerregistradas de convergencia, conservación, estabilidad y robustez. Ninguna declaración de cierre se deriva del mero final del cálculo.
'''
(home/'preregistration/PRERREGISTRO.md').write_text(prereg)
recovery=dict(kind='INDEPENDENT_ISOLATED_RECOVERY_CP12',instance_uuid=info['execution_uuid'],ancestor_time=24,ancestor_state_sha256=info['ancestor_state_sha256'],ancestor_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),supervision_source_sha256=sha(home/'coordinator.py'),guard_source_sha256=sha(home/'execute_guarded.py'),preregistration_sha256=sha(home/'preregistration/PRERREGISTRO.md'),original_future_results_authoritative=False,prior_recovery_attempt_future_results_authoritative=False)
new_identity=copy.deepcopy(identity);new_identity['recovery_layer']=recovery
run_id=hashlib.sha256(prov.canonical(new_identity)).hexdigest()
relative='validacion/P06/no_radial/CP12/par_recuperacion_independiente__'+run_id
run=root/relative;run.mkdir()
for name in ['configuration.json','CP12_par_estado.npz','CP12_par_progreso.json']:
    shutil.copyfile(root/ancestor_pair/name,run/name);(run/name).chmod(0o644)
assert sha(run/'CP12_par_estado.npz')==info['ancestor_state_sha256']
receipt=dict(schema_version='1.0.0',run_id=run_id,case='recuperacion_independiente_CP12',identity=new_identity,created_at=now(),status='PAUSADA_REANUDABLE',segments=[],configuration_sha256=sha(run/'configuration.json'),source_snapshots={},output_hashes={p.name:sha(p) for p in run.iterdir() if p.is_file()},execution_origin=dict(kind='INDEPENDENT_ISOLATED_RECOVERY_FROM_VERIFIED_TAU24',original_lost_receipt_recreated=False,prior_attempt_receipt_recreated=False,original_protocol_unchanged=True,ancestor_receipt_sha256=sha(root/ancestor_pair/'procedencia.json'),inherited_segments_not_claimed_as_this_execution=True,new_physical_segments_executed=0),comparisons_and_decision='Independent recovery with new provenance; inherited tau24 is verified scientific ancestry. CP12 remains open.')
prov.write(run/'procedencia.json',receipt)
meta=dict(execution_uuid=info['execution_uuid'],execution_run_id=run_id,branch=info['branch'],run_relative=relative,supervision_source_sha256=recovery['supervision_source_sha256'],guard_source_sha256=recovery['guard_source_sha256'],preregistration_sha256=recovery['preregistration_sha256'],ancestor_receipt_retained_read_only=True,initial_frontier=24)
write(home/'preregistration/nueva_identidad.json',meta)
info.update(ancestor_pair=ancestor_pair,ancestor_payload_files_verified=329,execution_run_id=run_id,run_relative=relative)
write(home/'preregistration/ubicacion.json',info);write(workspace/'CP12_RI_INTENTO2.json',info)
threads=threadpoolctl.threadpool_info()
assert threads and all(p['num_threads']==1 and p['architecture']=='SkylakeX' for p in threads)
preflight=dict(original_scientific_identity_exact=True,scientific_source_count=len(identity['code_hashes']),observed_BLAS_threads_one=True,observed_dispatch_SkylakeX=True,dispatch_not_forced=not os.environ.get('OPENBLAS_CORETYPE'),configuration_sha256=sha(run/'configuration.json'),state_sha256=sha(run/'CP12_par_estado.npz'),packages={p.__name__:p.__version__ for p in [numpy,scipy,matplotlib,threadpoolctl]},M2_steps=0)
write(home/'preregistration/preflight.json',preflight)
isolation=dict(new_uuid_and_run_id=True,new_branch=info['branch'],filesystem_roots_disjoint_from_prior_attempt=True,no_symlinks_or_hardlinks=True,scientific_and_configuration_bytes_original=True,ancestor_receipts_immutable=True,new_receipt_and_output_path=True,new_cache_and_temporary_paths=True,Library_operation_create_only_with_instance_prefix=True,old_executor_control_or_activity_queries=0,physical_source_changes=0,M2_steps=0,passed=True)
write(home/'preregistration/aislamiento.json',isolation)
print(json.dumps(dict(location=info,preflight=preflight,isolation=isolation)))
