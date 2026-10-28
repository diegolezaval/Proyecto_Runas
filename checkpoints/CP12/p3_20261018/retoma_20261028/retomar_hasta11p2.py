"""Repetición única y acotada9,6→11,2 usando el intervalo original y t_bound=16."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import traceback


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home',type=Path,required=True)
    parser.add_argument('--registro',type=Path,required=True)
    parser.add_argument('--aceptacion',type=Path,required=True)
    parser.add_argument('--salida',type=Path,required=True)
    args = parser.parse_args()
    home, output = args.home.resolve(), args.salida.resolve()
    registration, acceptance = read(args.registro), read(args.aceptacion)
    assert registration['schema'] == 'CP12_P3_BOUNDED_REPLAY_REGISTRATION_V1'
    assert registration['registered_before_M2'] and registration['one_time_replay_reserved']
    assert sha(Path(__file__)) == registration['bounded_runner_sha256']
    assert sha(args.aceptacion) == registration['capacity_acceptance_sha256']
    assert acceptance['schema'] == 'CP12_GITHUB_RELEASE_TRANSPORT_ACCEPTANCE_V1'
    assert acceptance['passed'] and acceptance['capacity_probe']
    assert acceptance['bytes'] > 229848115 and acceptance['observer_clock'] == 9.6
    assert acceptance['independently_extracted_zero_step_audits_passed']
    assert acceptance['source_archive_and_payload_unchanged']
    assert acceptance['transport_state_sha256'] == sha(home / 'transport/current.npz')
    assert sha(home / 'transport/current.npz') == '1bf0a52cf3cfd357e07d54fc519591558181508fdbb718242d369411a082e4e2'
    assert sha(home / 'outputs/MIXTO_par_estado.npz') == '1984303f49cac1c424952af632b6b5fa552c2a119d233a613c869cf0055b2db0'
    assert not os.environ.get('OPENBLAS_CORETYPE')
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                     PYTHONPYCACHEPREFIX=str(home/'runtime/pycache'),TMPDIR=str(home/'runtime/tmp'))
    sys.pycache_prefix = str(home/'runtime/pycache')
    output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(home))
    import controlador_transporte as controller
    tr = controller.tr
    legacy = controller.legacy_module(home)
    with legacy.zero_m2_audit() as attempts:
        modules, streams, budget, dense, payload = tr.restore(home,legacy,home/'transport/current.npz')
        repeated = tr.capture(home,streams,budget,dense,payload['observer_clock'],payload['next_record'],payload['target'])
        tr.assert_equal(payload,repeated)
        assert len(attempts) == 0 and payload['observer_clock'] == 9.6 and payload['target'] == 16
    global_lock = (args.registro.resolve().parent/'P3_WORKER.lock').open('a+')
    fcntl.flock(global_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    instance_lock = (home/'runtime/worker.lock').open('a+')
    fcntl.flock(instance_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    marker = args.registro.resolve().parent/'REPETICION_ASIGNADA.json'
    with marker.open('x') as stream:
        json.dump(dict(at=now(),pid=os.getpid(),source_time=9.6,stop_time=11.2,
                       source_state_sha256=sha(home/'transport/current.npz'),
                       scope='Exclusive one-time allocation; physical progress is recorded separately',
                       original_inaccessible_executor_termination_assumed=False),stream)
        stream.flush();os.fsync(stream.fileno())
    clock, next_record = payload['observer_clock'], payload['next_record']
    before_steps = [int(s.accepted) for s in streams]
    before_evaluations = [int(s.solver.nfev) for s in streams]
    report = dict(schema='CP12_P3_BOUNDED_REPLAY_96_TO_112_V1',started_at_utc=now(),
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
    except BaseException as error:
        report.update(error=f'{type(error).__name__}: {error}',traceback=traceback.format_exc(),
                      last_completed_observer_clock=clock,physical_streams=[s.metadata() for s in streams],
                      stop_classification='STOP_REQUIRES_REVIEW_NO_AUTOMATIC_REPLAY')
        negative=home/'negative/retoma_20261028';negative.mkdir(parents=True,exist_ok=False)
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
                             permanent_preservation_pending=True,CP12_closed=False)),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
