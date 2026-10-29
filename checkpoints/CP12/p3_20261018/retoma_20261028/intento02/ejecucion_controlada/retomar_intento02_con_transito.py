"""Intento02 acotado9,6→11,2; conservación temporal nativa antes de más física."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import traceback

SOURCE_TRANSPORT = '1bf0a52cf3cfd357e07d54fc519591558181508fdbb718242d369411a082e4e2'
CLOSED_STATE = '1984303f49cac1c424952af632b6b5fa552c2a119d233a613c869cf0055b2db0'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def now():
    return datetime.now(timezone.utc).isoformat()


def capacity_gates(value):
    if value.get('schema') != 'CP12_P3_TEMPORARY_TRANSIT_AND_GITHUB_CAPACITY_ACCEPTANCE_V1':
        raise ValueError('No es una aceptación combinada del control completo')
    fields = ['passed', 'capacity_probe', 'native_full_cycle_performed_in_this_invocation',
              'github_final_publication_verified', 'independently_extracted_zero_step_audits_passed',
              'source_archive_and_payload_unchanged']
    if any(value.get(key) is not True for key in fields):
        raise ValueError('Falta una puerta de conservación completa')
    if value.get('observer_clock') != 9.6 or value.get('bytes', 0) <= 229848115:
        raise ValueError('Capacidad o reloj no acreditados')
    if value.get('transport_state_sha256') != SOURCE_TRANSPORT or value.get('M2_steps_executed') != 0:
        raise ValueError('La prueba no corresponde al transporte sin pasos')


def consume_ticket(ticket, allocation):
    if ticket.is_symlink():
        raise ValueError('El permiso exclusivo no puede ser un enlace')
    ticket = ticket.resolve()
    name = allocation['ticket_basename']
    if ticket.name != name or ticket.is_symlink() or not ticket.is_file():
        raise ValueError('No existe el permiso privado de ejecución de un solo uso')
    if sha(ticket) != allocation['one_use_ticket_sha256']:
        raise ValueError('Permiso de ejecución distinto de la asignación')
    used = ticket.parent / (name + '.consumido')
    os.link(ticket, used)
    ticket.unlink()


def run_logged(command, prefix):
    process = subprocess.run(command, capture_output=True, text=True)
    prefix.with_suffix('.stdout.txt').write_text(process.stdout)
    prefix.with_suffix('.stderr.txt').write_text(process.stderr)
    if process.returncode:
        raise RuntimeError('Conservación detenida; revisar el recibo sin reiniciar física')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--registro', type=Path, required=True)
    parser.add_argument('--aceptacion', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--helpers', type=Path, required=True)
    parser.add_argument('--solo-auditar-puertas', action='store_true')
    parser.add_argument('--asignacion', type=Path)
    parser.add_argument('--ticket', type=Path)
    parser.add_argument('--auditoria-previa', type=Path)
    args = parser.parse_args()
    if sys.flags.optimize:
        raise ValueError('Las comprobaciones no pueden deshabilitarse')
    home, output = args.home.resolve(), args.salida.resolve()
    registration, acceptance = read(args.registro), read(args.aceptacion)
    if registration.get('schema') != 'CP12_P3_ADDITIONAL_BOUNDED_REPLAY_TRANSIT_REGISTRATION_V1':
        raise ValueError('Registro de otra ejecución')
    if registration.get('registered_before_M2') is not True or registration.get('additional_replay_authorized') is not True:
        raise ValueError('Falta el registro o la autorización adicional existente')
    if not args.solo_auditar_puertas and registration.get('one_time_replay_reserved') is not True:
        raise ValueError('La evolución requiere una reserva exclusiva registrada')
    if sha(Path(__file__)) != registration['bounded_runner_sha256']:
        raise ValueError('El lanzador no coincide con su registro')
    if sha(args.aceptacion) != registration['capacity_acceptance_sha256']:
        raise ValueError('La aceptación de capacidad no es la registrada')
    capacity_gates(acceptance)
    for key, filename in [('native_transit_driver_sha256','conservar_transito.py'),
                          ('conservation_driver_sha256','conservar_release.py'),
                          ('audit_driver_sha256','auditar_recuperacion.py')]:
        if sha(Path(__file__).with_name(filename)) != registration[key]:
            raise ValueError('Adaptador distinto de los bytes registrados')
    for name, expected in registration['current_helper_sha256'].items():
        if sha(args.helpers / name) != expected:
            raise ValueError('Ayudante distinto del utilizado por el control completo')
    if sha(home/'transport/current.npz') != SOURCE_TRANSPORT or sha(home/'outputs/MIXTO_par_estado.npz') != CLOSED_STATE:
        raise ValueError('No es el origen original9,6 con frontera8')
    if os.environ.get('OPENBLAS_CORETYPE'):
        raise ValueError('No se fuerza la arquitectura BLAS')
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                      PYTHONPYCACHEPREFIX=str(home/'runtime/pycache'), TMPDIR=str(home/'runtime/tmp'))
    sys.pycache_prefix = str(home/'runtime/pycache')
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(home))
    import controlador_transporte as controller
    tr = controller.tr
    legacy = controller.legacy_module(home)
    with legacy.zero_m2_audit() as attempts:
        modules, streams, budget, dense, payload = tr.restore(home, legacy, home/'transport/current.npz')
        repeated = tr.capture(home, streams, budget, dense, payload['observer_clock'], payload['next_record'], payload['target'])
        tr.assert_equal(payload, repeated)
        assert len(attempts) == 0 and payload['observer_clock'] == 9.6 and payload['target'] == 16
    gate_receipt = dict(schema='CP12_P3_ADDITIONAL_REPLAY_ZERO_STEP_GATES_V1', passed=True,
                        at=now(), runner_sha256=sha(Path(__file__)),
                        capacity_acceptance_sha256=sha(args.aceptacion), source_transport_sha256=SOURCE_TRANSPORT,
                        closed_state_sha256=CLOSED_STATE, exact_restore_without_construction_or_steps=True,
                        M2_steps_executed=0, DOP853_construction_or_step_attempts=0,
                        allocation_consumed=False, scientific_frontier=False, CP12_closed=False)
    if args.solo_auditar_puertas:
        tr.write(output/'PUERTAS_SIN_PASOS.json', gate_receipt)
        print(json.dumps(gate_receipt), flush=True)
        return 0
    if not args.asignacion or not args.ticket or not args.auditoria_previa:
        raise ValueError('Faltan asignación, permiso exclusivo o auditoría previa')
    prior = read(args.auditoria_previa)
    if sha(args.auditoria_previa) != registration['dry_run_receipt_sha256'] or prior.get('passed') is not True:
        raise ValueError('No se acreditó la auditoría de puertas previa')
    for key in ['runner_sha256','capacity_acceptance_sha256','source_transport_sha256','closed_state_sha256']:
        if prior[key] != gate_receipt[key]:
            raise ValueError('La auditoría previa tiene otras identidades')
    allocation = read(args.asignacion)
    if sha(args.asignacion) != registration['allocation_record_sha256']:
        raise ValueError('La asignación no coincide con el registro')
    if allocation.get('schema') != 'CP12_P3_ADDITIONAL_REPLAY_EXCLUSIVE_ALLOCATION_V1' or allocation.get('reserved_before_M2') is not True:
        raise ValueError('Falta una asignación exclusiva registrada')
    if allocation['attempt_id'] != registration['attempt_id'] or allocation['runner_sha256'] != gate_receipt['runner_sha256'] or allocation['capacity_acceptance_sha256'] != gate_receipt['capacity_acceptance_sha256']:
        raise ValueError('La asignación corresponde a otro intento')
    global_lock = (args.registro.resolve().parent/'P3_WORKER.lock').open('a+')
    fcntl.flock(global_lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    instance_lock = (home/'runtime/worker.lock').open('a+')
    fcntl.flock(instance_lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    marker = args.registro.resolve().parent/'REPETICION_INTENTO02_ASIGNADA.json'
    if marker.exists():
        raise FileExistsError('La asignación local ya fue utilizada; no reiniciar')
    consume_ticket(args.ticket, allocation)
    with marker.open('x') as stream:
        json.dump(dict(at=now(), pid=os.getpid(), source_time=9.6, stop_time=11.2,
                       allocation_record_sha256=sha(args.asignacion), source_state_sha256=SOURCE_TRANSPORT,
                       scope='Exclusive allocation; physical consumption requires observed steps'), stream)
        stream.flush(); os.fsync(stream.fileno())
    clock, next_record = payload['observer_clock'], payload['next_record']
    before_steps = [int(s.accepted) for s in streams]
    before_evaluations = [int(s.solver.nfev) for s in streams]
    report = dict(schema='CP12_P3_ADDITIONAL_BOUNDED_REPLAY_TRANSIT_V1',started_at_utc=now(),
                  from_observer_clock=9.6,to_observer_clock=11.2,internal_solver_bound=16,
                  source_transport_sha256=sha(home/'transport/current.npz'),
                  capacity_acceptance_sha256=sha(args.aceptacion),
                  exact_restore_without_construction_or_steps=True,passed=False,
                  correction_validated=False,CP12_closed=False,scientific_frontier=False)
    stop = threading.Event()
    def heartbeat():
        while not stop.wait(30):
            tr.write(output/'HEARTBEAT.json',dict(at=now(),observer_clock=clock,
                     physical_streams=[s.metadata() for s in streams],not_a_restart_certificate=True))
    threading.Thread(target=heartbeat,daemon=True).start()
    try:
        while clock < 11.2 - 1e-12:
            clock,next_record,dense,recorded = controller.interval(modules,streams,budget,dense,clock,next_record,16)
            assert clock <= 11.2 + 1e-12
            if not report.get('physical_start_observed') and any(int(s.accepted) > n for s,n in zip(streams,before_steps)):
                report['physical_start_observed'] = True
                tr.write(output/'INICIO_FISICO_OBSERVADO.json',dict(at=now(),observer_clock=clock,
                         accepted_steps_since_restore=[int(s.accepted)-n for s,n in zip(streams,before_steps)],
                         additional_replay_exception_consumed=True,CP12_closed=False))
                print(json.dumps(dict(stage='physical_start_observed',observer_clock=clock)),flush=True)
            if recorded:
                tr.save(home/'transport/current.npz',tr.capture(home,streams,budget,dense,clock,next_record,16))
                checked = controller.audit_transport(home,legacy)
                tr.write(output/('AUDITORIA_TAU_%06d.json'%round(clock*10)),checked)
                record = dict(at=now(),observer_clock=clock,physical_streams=[s.metadata() for s in streams],
                              accepted_steps_since_restore=[int(s.accepted)-v for s,v in zip(streams,before_steps)],
                              source_transport_sha256=tr.sha(home/'transport/current.npz'),
                              audited_without_steps=True,permanent_preservation_pending=True)
                tr.write(output/'PROGRESO.json',record)
                print(json.dumps(record),flush=True)
        assert abs(clock-11.2) < 1e-12
        report.update(passed=True,observer_clock=clock,transport_state_sha256=sha(home/'transport/current.npz'),
                      physical_streams=[s.metadata() for s in streams],
                      physical_accepted_steps_executed=[int(s.accepted)-v for s,v in zip(streams,before_steps)],
                      physical_RHS_evaluations_executed=[int(s.solver.nfev)-v for s,v in zip(streams,before_evaluations)],
                      closed_frontier_unchanged=sha(home/'outputs/MIXTO_par_estado.npz')=='1984303f49cac1c424952af632b6b5fa552c2a119d233a613c869cf0055b2db0',
                      permanent_preservation_pending=True,next_physical_interval_executed=False)

        report.update(physical_interval_completed=True, passed=False, github_publication_pending=True,
                      further_physics_authorized=False, additional_replay_exception_consumed=True)
        assert report['closed_frontier_unchanged']
        stop.set()
        snapshot = home/'administracion_github_20261028/intento02'
        snapshot.mkdir(parents=True, exist_ok=True)
        tr.write(snapshot/'CALCULO_TERMINADO_CONSERVACION_PENDIENTE.json',report)
        preparation = output/'capsula'
        run_logged([sys.executable,str(Path(__file__).with_name('conservar_release.py')),'preparar',
                    '--home',str(home),'--label','TRANSPORTE_TAU_000112_TRANSITO_INTENTO02_20261028',
                    '--salida',str(preparation)],output/'preparacion')
        transit = output/'transito'
        run_logged([sys.executable,str(Path(__file__).with_name('conservar_transito.py')),
                    '--solicitud',str(preparation/'SOLICITUD.json'),'--salida',str(transit),
                    '--helpers',str(args.helpers.resolve())],output/'conservacion_transito')
        receipt=read(transit/'RESULTADO_TRANSITO.json')
        assert receipt['passed'] and receipt['independent_recovery_verified']
        assert receipt['native_full_cycle_performed_in_this_invocation']
        assert receipt['observer_clock']==11.2 and receipt['transport_state_sha256']==sha(home/'transport/current.npz')
        assert receipt['transit_driver_sha256']==registration['native_transit_driver_sha256']
        assert receipt['current_helper_sha256']==registration['current_helper_sha256']
        report.update(passed=True, temporary_transit_permanently_recovered=True,
                      permanent_preservation_pending=False, github_publication_pending=True,
                      further_physics_authorized=False,transit_receipt_sha256=sha(transit/'RESULTADO_TRANSITO.json'),
                      library_file_id=receipt['library_file_id'],file_id=receipt['file_id'],
                      file_name=receipt['file_name'],archive_bytes=receipt['bytes'],archive_sha256=receipt['sha256'])

    except BaseException as error:
        report['additional_replay_exception_consumed'] = any(
            int(s.accepted) > n or int(s.solver.nfev) > f
            for s,n,f in zip(streams,before_steps,before_evaluations))
        report.update(error=f'{type(error).__name__}: {error}',traceback=traceback.format_exc(),
                      last_completed_observer_clock=clock,physical_streams=[s.metadata() for s in streams],
                      stop_classification='STOP_REQUIRES_REVIEW_NO_AUTOMATIC_REPLAY')
        negative=home/'negative/intento02_20261028';negative.mkdir(parents=True,exist_ok=False)
        np=modules['np']
        arrays={f'grid_{i}_{k}':getattr(s,k) for i,s in enumerate(streams) for k in ('q','v','initial_q','initial_v')}
        arrays.update(physical_metadata=json.dumps([s.metadata() for s in streams]),budget_rows=json.dumps(budget.rows),
                      budget_maximum_errors=json.dumps(budget.maximum_errors),coupled_angular_basis=budget.S)
        for name,family in [('raw',budget.raw),('coupled',budget.coupled)]:
            for i,observer in enumerate(family):
                arrays[f'{name}_{i}_q'],arrays[f'{name}_{i}_v']=observer.q,observer.v
        np.savez_compressed(negative/'ESTADO_NO_CERTIFICADO.npz',**arrays)
        tr.write(negative/'FALLO.json',report)
        raise
    finally:
        stop.set()
        report['finished_at_utc']=now()
        tr.write(output/'RESULTADO.json',report)
        print(json.dumps(dict(passed=report['passed'],observer_clock=clock,
                             permanent_preservation_pending=report.get('permanent_preservation_pending',True),
                             github_publication_pending=True,CP12_closed=False)),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())

