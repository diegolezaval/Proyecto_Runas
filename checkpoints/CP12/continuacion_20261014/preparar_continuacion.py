"""Create independent CP12 outputs from a verified frontier; zero M2 steps."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, os, shutil, sys, uuid

os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:
        json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--source-science',type=Path,required=True)
    a.add_argument('--ancestor-state',type=Path,required=True)
    a.add_argument('--ancestor-certificate',type=Path,required=True)
    a.add_argument('--home',type=Path,required=True)
    a.add_argument('--library-helpers',type=Path,required=True)
    args=a.parse_args()
    source=args.source_science.resolve();ancestor=args.ancestor_state.resolve()
    home=args.home.resolve();root=home/'science'
    assert not home.exists(),'Use a new independent destination'
    certificate=json.loads(args.ancestor_certificate.read_text())
    assert certificate['passed'] and all(certificate['tests'].values())
    initial=int(certificate['time']);assert 0<=initial<160 and initial%8==0
    assert sha(ancestor/'CP12_par_estado.npz')==certificate['state_sha256']
    assert sha(ancestor/'configuration.json')==certificate['configuration_sha256']
    identity=json.loads((source/'checkpoints/CP12/continuacion_20261014/IDENTIDAD_CIENTIFICA_ORIGINAL.json').read_text())
    assert len(identity['code_hashes'])==14
    root.mkdir(parents=True)
    def put(name,expected=None):
        src=source/name;dst=root/name
        assert src.is_file() and not src.is_symlink(),name
        if expected is not None:assert sha(src)==expected,name
        dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert sha(dst)==sha(src)
        else:shutil.copyfile(src,dst)
        assert not dst.is_symlink() and dst.stat().st_nlink==1
        dst.chmod(0o444)
    for name,h in {**identity['input_hashes'],**identity['code_hashes']}.items():put(name,h)
    for src in (source/'herramientas').iterdir():
        if src.is_file() and src.suffix in ('.py','.c'):put(src.relative_to(source).as_posix())
    for name in ['requirements.txt','estado_progreso.json','datos/reconstruccion_CP12.json','datos/interpretacion_CP12.json']:
        put(name)
    put('checkpoints/CP12/continuacion_20261014/IDENTIDAD_CIENTIFICA_ORIGINAL.json')
    controls=sorted((source/identity['case']['configuration']['control_directory']).glob('control_instrumentacion__*'))
    assert len(controls)==6
    for control in controls:
        for src in control.rglob('*'):
            if src.is_file() and '__pycache__' not in src.parts and src.suffix not in ('.pyc','.so','.tmp'):
                put(src.relative_to(source).as_posix())
        receipt=json.loads((control/'procedencia.json').read_text())
        for name,h in {**receipt['identity']['input_hashes'],**receipt['identity']['code_hashes']}.items():
            if name in receipt['source_snapshots']:continue
            src=source/name
            if src.is_file() and sha(src)==h:put(name,h)
            else:
                historical='trazabilidad/CP11_entrada/'+name
                if (source/historical).is_file() and sha(source/historical)==h:put(historical,h)
    for folder in ['runtime/tmp','runtime/pycache','capsules','recoveries','proofs','preregistration']:
        (home/folder).mkdir(parents=True,exist_ok=True)
    library=home/'runtime/library';library.mkdir()
    for name in ['library_upload.py','library_download.py','library_file_transfer.py','library_hosted_apps.py']:
        src=args.library_helpers/name;assert src.is_file()
        shutil.copyfile(src,library/name);assert sha(src)==sha(library/name)
    controller=Path(__file__).with_name('continuar_fronteras.py')
    shutil.copyfile(controller,home/'coordinator.py')
    shutil.copyfile(Path(__file__).with_name('ejecutar_guardian.py'),home/'guardian.py')
    execution_uuid=uuid.uuid4().hex
    info=dict(execution_uuid=execution_uuid,branch='ciencia/cp12-continuacion-20261014',
              ancestor_state_sha256=certificate['state_sha256'],ancestor_time=initial,
              ancestor_public_recovery_certified=bool(certificate.get('public_recovery_receipt_is_new')),
              old_executor_termination_assumed=False)
    prereg='''# Continuación aislada CP12

Se retoma la frontera certificada más avanzada sin repetir tramos certificados.
La ciencia, Θ, ambas mallas, DOP853, tolerancias, observadores, spline y la puerta del 2 % quedan originales.
Se copian archivos, sin enlaces simbólicos ni duros. Todas las fuentes y entradas heredadas son de sólo lectura.
La instancia tiene raíz, salida, recibo, caché, temporales, bloqueo y cápsulas propios.
No se presupone terminación ni se controlan trabajadores anteriores. Main y PR #2 permanecen intactos.
Antes de cada avance se exige respaldo creado, recuperado por separado y auditado de la frontera anterior.
Cada nueva frontera de ocho unidades se audita y conserva antes de continuar. Un fallo se conserva y detiene el trabajador.
El guardián desacopla el lanzamiento de la terminal, pero no garantiza que la plataforma conserve indefinidamente el entorno.
En τ160 la reproducción CP10 debe ser exacta. Sólo entonces se leen las tres ventanas causales y se aplican las puertas originales.
Finalizar la evolución o cerrar un presupuesto de Duhamel no acredita una corrección ni cierra CP12.
'''
    (home/'preregistration/PRERREGISTRO.md').write_text(prereg)
    os.environ.update(PYTHONPYCACHEPREFIX=str(home/'runtime/pycache'),TMPDIR=str(home/'runtime/tmp'))
    sys.path.insert(0,str(root/'herramientas'))
    import gestionar_respaldo_CP12 as mgr
    import ejecutar_con_procedencia as prov
    import reproducir_par_CP12 as physical
    from threadpoolctl import threadpool_info
    _,_,actual,scientific_id=mgr.original_identity();assert actual==identity
    threads=threadpool_info()
    assert threads and not os.environ.get('OPENBLAS_CORETYPE')
    assert all(x['num_threads']==1 and x['architecture']=='SkylakeX' for x in threads)
    saved=physical.source_state(ancestor/'CP12_par_estado.npz')
    assert float(saved['time'])==initial
    assert json.loads(str(saved['config']))==identity['case']['configuration']
    layer=dict(kind='NEW_ISOLATED_CP12_CONTINUATION',execution_uuid=execution_uuid,
               ancestor_time=initial,ancestor_state_sha256=certificate['state_sha256'],
               supervision_source_sha256=sha(home/'coordinator.py'),
               guardian_source_sha256=sha(home/'guardian.py'),
               preregistration_sha256=sha(home/'preregistration/PRERREGISTRO.md'),
               original_future_results_authoritative=False)
    independent=copy.deepcopy(identity);independent['recovery_layer']=layer
    run_id=hashlib.sha256(prov.canonical(independent)).hexdigest()
    relative='validacion/P06/no_radial/CP12/par_continuacion_aislada__'+run_id
    run=root/relative;run.mkdir()
    for name in ['CP12_par_estado.npz','CP12_par_progreso.json','configuration.json']:
        shutil.copyfile(ancestor/name,run/name)
        assert sha(ancestor/name)==sha(run/name) and (run/name).stat().st_nlink==1
    receipt=dict(schema_version='1.0.0',run_id=run_id,case='continuacion_aislada_CP12',identity=independent,
                 created_at=prov.now(),status='PAUSADA_REANUDABLE',segments=[],source_snapshots={},
                 configuration_sha256=sha(run/'configuration.json'),
                 output_hashes={p.name:sha(p) for p in run.iterdir() if p.is_file()},
                 execution_origin=dict(kind='NEW_INDEPENDENT_CONTINUATION_FROM_CERTIFIED_FRONTIER',
                     original_lost_receipt_recreated=False,historical_private_receipt_not_recreated=True,
                     original_protocol_unchanged=True,new_physical_segments_executed=0,
                     inherited_segments_not_claimed_as_this_execution=True))
    prov.write(run/'procedencia.json',receipt)
    meta=dict(execution_uuid=execution_uuid,execution_run_id=run_id,branch=info['branch'],
              run_relative=relative,supervision_source_sha256=sha(home/'coordinator.py'),initial_frontier=initial)
    write(home/'preregistration/ubicacion.json',info)
    write(home/'preregistration/nueva_identidad.json',meta)
    write(home/'preregistration/identidad_cientifica.json',identity)
    write(home/'preregistration/ancestor_certificate.json',certificate)
    mgr.RUN=run;checked=mgr.audit(initial)
    assert checked['passed'] and all(checked['tests'].values()),checked['tests']
    write(home/'proofs/bootstrap_audit.json',checked)
    write(home/'preregistration/aislamiento.json',dict(passed=True,original_scientific_identity=scientific_id,
          no_symlinks_or_hardlinks=True,sources_and_inputs_original=True,new_output_receipt_cache_tmp_lock_and_capsules=True,
          all_sources_read_only=True,old_executor_termination_assumed=False,M2_steps=0,CP12_closed=False))
    print(json.dumps(dict(passed=True,initial_frontier=initial,scientific_identity_exact=True,
                         original_source_count=14,M2_steps=0,CP12_closed=False)))

if __name__=='__main__':main()
