"""Registro, comprobación y cápsulas CP12; integración y observadores intactos."""
from pathlib import Path
import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import numpy as np
from threadpoolctl import threadpool_limits, threadpool_info
import ejecutar_con_procedencia as prov
import ejecutar_protocolo as adapter
import reproducir_par_CP12 as physical

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT/'datos/ensayo_causal_chi_CP12.json'
RECOVERY = ROOT/'datos/reconstruccion_CP12.json'
RUN_ID = 'a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
RUN = ROOT/'validacion/P06/no_radial/CP12'/('par_instrumentado__'+RUN_ID)
SUPPORT = ROOT/'trazabilidad/CP12_reconstruccion'
DOCUMENT = 'informes/PRERREGISTRO_RECONSTRUCCION_CP12.md'


def read(path):
    return json.loads(path.read_text())


def original_identity():
    data, case, identity, run_id = prov.prepare(ORIGINAL, 'par_instrumentado')
    if run_id != RUN_ID or len(identity['code_hashes']) != 14:
        raise ValueError('Identidad original CP12 cambiada; no avanzar')
    return data, case, identity, run_id


def register_full(protocol, case_name):
    """Recibo NUEVO previo, capturando también entradas mutables de auditoría."""
    adapter.configure(protocol, case_name)
    data, case, identity, run_id = prov.prepare(protocol, case_name)
    folder = prov.CAMPAIGN/(case_name+'__'+run_id)
    receipt_path = folder/'procedencia.json'
    lock_path = ROOT/('validacion/P06/no_radial/ejecucion_prov_'+run_id+'.lock')
    with lock_path.open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if receipt_path.is_file():
            old = read(receipt_path)
            if old['identity'] != identity or not prov.verify_receipt(receipt_path)['passed']:
                raise ValueError('Recibo existente incompatible')
            return folder
        folder.mkdir(parents=True, exist_ok=True)
        snapshots = {}
        for name in sorted(set(identity['code_hashes']) | set(identity['input_hashes'])):
            target = folder/'fuentes'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)
            snapshots[name] = target.relative_to(folder).as_posix()
        prov.write(folder/'configuration.json', dict(case=case, protocol=identity['protocol'], initial_state=data['initial_state']))
        receipt = dict(schema_version='1.0.0', run_id=run_id, case=case_name, identity=identity,
                       created_at=prov.now(), status='REGISTRADA', segments=[],
                       configuration_sha256=prov.digest(folder/'configuration.json'),
                       source_snapshots=snapshots, output_hashes={},
                       execution_origin=dict(kind='RECONSTRUCCION_EXPLICITA_CP12',
                           preregistration=DOCUMENT, preregistration_sha256=prov.digest(ROOT/DOCUMENT),
                           original_lost_receipt_recreated=False, original_protocol_unchanged=True),
                       comparisons_and_decision='Reconstrucción autorizada; evidencia y puertas CP12 originales. No cierre de etapa por finalizar una ejecución.')
        receipt['output_hashes'] = {p.relative_to(folder).as_posix():prov.digest(p) for p in sorted(folder.rglob('*')) if p.is_file()}
        prov.write(receipt_path, receipt)
    return folder


def audit(time_):
    _, case, identity, _ = original_identity()
    cfg = case['configuration']
    receipt = prov.verify_receipt(RUN/'procedencia.json')
    controls = [prov.verify_receipt(p) for p in sorted((RUN.parent).glob('control_instrumentacion__*/procedencia.json'))]
    matching = [p for p in RUN.parent.glob('control_instrumentacion__*/procedencia.json') if
                read(p)['status']=='COMPLETADA' and all(prov.digest(ROOT/n)==h for n,h in read(p)['identity']['code_hashes'].items())]
    previous = read(ROOT/'trazabilidad/CP11_entrada/estado_progreso.json')
    tests = dict(original_identity_and_fourteen_files=True, receipt_integrity=receipt['passed'],
                 six_controls_intact=len(controls)==6 and all(x['passed'] for x in controls),
                 one_current_positive_control=len(matching)==1,
                 original_stage_records_unchanged=read(ROOT/'estado_progreso.json')['stages']==previous['stages'],
                 physical_gate_unchanged=cfg['physical_gate_threshold']==.02,
                 observed_BLAS_threads_one=bool(threadpool_info()) and all(p['num_threads']==1 for p in threadpool_info()),
                 new_receipt_explicitly_declares_reconstruction=read(RUN/'procedencia.json')['execution_origin']['original_lost_receipt_recreated'] is False)
    if time_ is None:
        tests['no_physical_segment_started']=read(RUN/'procedencia.json')['segments']==[]
        tests['all_inputs_captured_before_execution']=set(identity['input_hashes'])<=set(read(RUN/'procedencia.json')['source_snapshots'])
        return dict(passed=all(tests.values()), tests=tests, time=None, run_id=RUN_ID,
                    M2_steps_executed=0, observer_changes=False, correction_tested=False,
                    causal_inference_allowed=False, receipt=receipt)
    time_=float(time_)
    saved=physical.source_state(RUN/'CP12_par_estado.npz')
    progress=read(RUN/'CP12_par_progreso.json')
    metadata=json.loads(str(saved['metadata']));n=int(saved['coarse_n'])
    rows=saved['rows'];budget_rows=json.loads(str(saved['budget_rows']))
    maximum=json.loads(str(saved['maximum_errors']));algebra=json.loads(str(saved['budget_algebra']))
    tests.update(time_and_original_boundary=float(saved['time'])==time_ and time_%8==0,
                 original_configuration_exact=json.loads(str(saved['config']))==cfg,
                 expected_schema=str(saved['schema'])=='CP12_DOS_MALLAS_Y_OBSERVADORES_PASIVOS',
                 companion_progress_time=progress['time']==time_,
                 finite_physical_arrays=all(np.isfinite(saved[k]).all() for k in ['q','v','initial_q','initial_v','rows']),
                 finite_observer_arrays=all(np.isfinite(saved[f'{f}_{i}_{k}']).all() for f in ['raw','coupled'] for i in [0,1] for k in ['q','v']),
                 observation_count=len(rows)==round(time_/.4)+1,
                 budget_count=len(budget_rows)==len(rows),
                 budget_time_labels=max(abs(b['time']-r[0]) for b,r in zip(budget_rows,rows))<=1e-12,
                 metadata_times=all(m['t']==time_ for m in metadata),
                 original_observer_error_gate=max(maximum.values())<=cfg['observer_relative_tolerance'],
                 original_parseval_gate=maximum.get('modal_parseval',0)<=2e-11,
                 original_symmetry_gate=float(saved['maximum_symmetry_residual'])<=2e-12,
                 extended_identity_gate=all(a['mean_jacobian_identity_extended_relative_residual']<2e-12 for a in algebra),
                 original_force_partition_and_symmetry=all(a['production_force_absolute_scaled_residual']<2e-12 and a['weighted_jacobian_symmetry_residual']<2e-12 for a in algebra))
    for i,use in enumerate([slice(0,n),slice(n,None)]):
        reference=physical.source_state(ROOT/cfg['reference_states'][i])
        actual=rows[:,:10] if i==0 else np.column_stack([rows[:,0],rows[:,10:]])
        for name in ['initial_q','initial_v']:
            tests[f'{i}_{name}_array_equal_CP10']=np.array_equal(saved[name][:,use],reference[name])
        tests[f'{i}_prefix_observations_array_equal_CP10']=np.array_equal(actual,reference['rows'][:len(actual)])
        tests[f'{i}_original_balances']=metadata[i]['maxe']<=2e-4 and metadata[i]['maxq']<=1e-9
        if time_==160:
            for name in ['q','v']:
                tests[f'{i}_{name}_array_equal_CP10']=np.array_equal(saved[name][:,use],reference[name])
            for name,ref in [('accepted','accepted_steps'),('nfev','nfev'),('maxe','maxe'),('maxq','maxq')]:
                tests[f'{i}_{name}_exact_CP10']=metadata[i][name]==float(reference[ref])
    antecedent=read(RECOVERY)['prior_observations'].get(str(int(time_)))
    comparisons=None
    if antecedent:
        tests['prior_accepted_steps_exact']=all(m['accepted']==antecedent['accepted_steps_per_grid'] for m in metadata)
        tests['prior_original_nfev_exact']=all(m['nfev']==antecedent['original_nfev_per_grid'] for m in metadata)
        tests['prior_npz_size_exact']=(RUN/'CP12_par_estado.npz').stat().st_size==antecedent['state_bytes']
        tests['prior_npz_hash_exact']=prov.digest(RUN/'CP12_par_estado.npz')==antecedent['state_sha256']
        comparisons=dict(prior_status='ANTECEDENTE_DE_SALIDA_DE_HERRAMIENTA_NO_ARCHIVO_RECUPERADO',
                         expected=antecedent, observed_state_sha256=prov.digest(RUN/'CP12_par_estado.npz'),
                         observed_state_bytes=(RUN/'CP12_par_estado.npz').stat().st_size,
                         observed_metadata=metadata)
    before=prov.digest(RUN/'CP12_par_estado.npz')
    if all(tests.values()) and time_<160:
        with tempfile.TemporaryDirectory(prefix='cp12_sin_avance_') as directory:
            temporary=Path(directory)
            shutil.copyfile(RUN/'CP12_par_estado.npz',temporary/'CP12_par_estado.npz')
            with threadpool_limits(limits=1):
                result=physical.run_pair(cfg,temporary,stop_at=time_)
            tests['original_worker_zero_step_restart']=result['time']==time_ and prov.digest(temporary/'CP12_par_estado.npz')==before
    tests['audited_state_not_modified']=prov.digest(RUN/'CP12_par_estado.npz')==before
    return dict(passed=all(tests.values()), tests={k:bool(v) for k,v in tests.items()}, time=time_, run_id=RUN_ID,
                M2_steps_executed=0, state_sha256=before, configuration_sha256=prov.digest(RUN/'configuration.json'),
                receipt_sha256=prov.digest(RUN/'procedencia.json'), observation_count=len(rows),
                metadata=metadata, maximum_errors=maximum, prior_comparisons=comparisons,
                observer_changes=False, correction_tested=False, causal_inference_allowed=False, receipt=receipt)


def audit_case(time_):
    case_name='preejecucion' if time_ is None else 'reinicio_'+str(int(time_)).zfill(4)
    folder=register_full(RECOVERY,case_name)
    prov.execute(RECOVERY,case_name,resume=True)
    report=read(folder/'resultados.json')
    if not report['passed'] or not prov.verify_receipt(folder/'procedencia.json')['passed']:
        raise ValueError('Comprobación negativa; no avanzar')
    return folder


def package(time_,destination):
    case_name='preejecucion' if time_ is None else 'reinicio_'+str(int(time_)).zfill(4)
    adapter.configure(RECOVERY,case_name)
    _,_,_,audit_id=prov.prepare(RECOVERY,case_name)
    audit_folder=prov.CAMPAIGN/(case_name+'__'+audit_id)
    if not read(audit_folder/'resultados.json')['passed'] or not prov.verify_receipt(RUN/'procedencia.json')['passed'] or not prov.verify_receipt(audit_folder/'procedencia.json')['passed']:
        raise ValueError('Cápsula requiere recibos y comprobación válidos')
    _,_,identity,_=original_identity()
    selected=set(p for folder in [RUN,audit_folder] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.tmp','.pyc'])
    selected.update(ROOT/n for n in set(identity['code_hashes'])|set(identity['input_hashes']))
    for folder in RUN.parent.glob('control_instrumentacion__*'):
        selected.update(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.tmp','.pyc'])
    selected.update([RECOVERY,ROOT/DOCUMENT,Path(__file__).resolve(),ROOT/'requirements.txt',ROOT/'estado_progreso.json'])
    # La cápsula siguiente conserva comprobantes anteriores; el propio se
    # escribe después de descargarla, evitando una dependencia circular.
    selected.update(p for p in SUPPORT.rglob('*') if p.is_file())
    manifest=dict(schema='CP12_CAPSULA_DE_TRABAJO_NO_CHECKPOINT_CERRADO',created_at=prov.now(),
                  run_id=RUN_ID,time=time_,scientific_checkpoint='CP11_DIAGNOSTICO_RADIAL_CHI',
                  original_pair=RUN.relative_to(ROOT).as_posix(),audit=audit_folder.relative_to(ROOT).as_posix(),
                  files={p.relative_to(ROOT).as_posix():dict(sha256=prov.digest(p),bytes=p.stat().st_size) for p in sorted(selected)})
    destination=destination.resolve();destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.is_relative_to(ROOT) or destination.exists():
        raise ValueError('Cápsula nueva fuera del corpus; no sobreescribir historia')
    temporary=destination.with_suffix('.zip.tmp')
    if temporary.exists():raise ValueError('Escritura previa pendiente; conservar y diagnosticar')
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(selected):archive.write(path,'Proyecto_Runas/'+path.relative_to(ROOT).as_posix())
        archive.writestr('Proyecto_Runas/MANIFIESTO_REINICIO_CP12.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with temporary.open('rb') as held:os.fsync(held.fileno())
    temporary.replace(destination)
    result=dict(path=str(destination),sha256=prov.digest(destination),bytes=destination.stat().st_size,
                time=time_,audit=audit_folder.relative_to(ROOT).as_posix(),payload_files=len(selected))
    print(json.dumps(result,ensure_ascii=False));return result


def verify_download(archive_path,expected_sha,destination):
    if prov.digest(archive_path)!=expected_sha:raise ValueError('ZIP descargado no coincide')
    destination=destination.resolve()
    if destination.exists():raise ValueError('Destino de comprobación debe ser nuevo')
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or path.parts[0]!='Proyecto_Runas':raise ValueError('Ruta insegura en cápsula')
        archive.extractall(destination)
    project=destination/'Proyecto_Runas'
    manifest=read(project/'MANIFIESTO_REINICIO_CP12.json')
    actual={p.relative_to(project).as_posix() for p in project.rglob('*') if p.is_file() and p.name!='MANIFIESTO_REINICIO_CP12.json'}
    if actual!=set(manifest['files']):raise ValueError('Cobertura de cápsula incorrecta')
    for name,record in manifest['files'].items():
        path=project/name
        if path.stat().st_size!=record['bytes'] or prov.digest(path)!=record['sha256']:raise ValueError('Payload alterado: '+name)
    command=[sys.executable,str(project/'herramientas/gestionar_respaldo_CP12.py'),'--auditar-extraido']
    if manifest['time'] is not None:command+=['--time',str(manifest['time'])]
    outcome=subprocess.run(command,cwd=project,capture_output=True,text=True)
    result=dict(passed=outcome.returncode==0,zip_sha256=expected_sha,time=manifest['time'],
                payload_files=len(actual),all_payload_hashes_verified=True,
                independent_extracted_check=json.loads(outcome.stdout) if outcome.returncode==0 else outcome.stdout,
                stderr=outcome.stderr,downloaded_path=str(archive_path),extracted_path=str(project))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result['passed']:raise ValueError('Copia extraída no reanuda correctamente')
    return result


def advance(target):
    target=float(target)
    _,_,_,_=original_identity()
    previous=None if target==0 else target-8
    certificate=SUPPORT/'respaldos'/('preejecucion.json' if previous is None else 'tau'+str(int(previous)).zfill(4)+'.json')
    proof=read(certificate)
    if not proof['passed'] or not proof['download_verification']['passed'] or not proof['library_file_id']:
        raise ValueError('Sin respaldo permanente comprobado; no avanzar')
    if prov.digest(RUN/'procedencia.json')!=proof['receipt_sha256'] or prov.digest(RUN/'configuration.json')!=proof['configuration_sha256']:
        raise ValueError('Recibo/configuración cambiaron después del respaldo')
    if previous is not None and (float(physical.source_state(RUN/'CP12_par_estado.npz')['time'])!=previous or prov.digest(RUN/'CP12_par_estado.npz')!=proof['state_sha256']):
        raise ValueError('Estado difiere del respaldo verificado')
    adapter.configure(ORIGINAL,'par_instrumentado')
    adapter.recover_if_needed(ORIGINAL,'par_instrumentado')
    prov.execute(ORIGINAL,'par_instrumentado',stop_at=target,resume=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path);parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--registrar',action='store_true');parser.add_argument('--auditar',action='store_true')
    parser.add_argument('--auditar-extraido',action='store_true');parser.add_argument('--avanzar',type=float)
    parser.add_argument('--time',type=float);parser.add_argument('--paquete',type=Path)
    parser.add_argument('--verificar-descarga',type=Path);parser.add_argument('--sha256');parser.add_argument('--destino',type=Path)
    args=parser.parse_args()
    if args.config:
        result=audit(read(args.config)['case']['configuration']['time'])
        prov.write(args.output_dir/'resultados.json',result)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        raise SystemExit(0 if result['passed'] else 1)
    if args.registrar:
        original_identity();print(register_full(ORIGINAL,'par_instrumentado'))
    elif args.auditar:print(audit_case(args.time))
    elif args.auditar_extraido:
        result=audit(args.time);print(json.dumps(result,ensure_ascii=False));raise SystemExit(0 if result['passed'] else 1)
    elif args.avanzar is not None:advance(args.avanzar)
    elif args.paquete:package(args.time,args.paquete)
    elif args.verificar_descarga:verify_download(args.verificar_descarga,args.sha256,args.destino)
    else:parser.error('Indicar una operación')
