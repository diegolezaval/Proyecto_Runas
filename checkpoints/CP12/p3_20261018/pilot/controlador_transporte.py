"""Original mixed scientific kernels, with exact intermediate solver transport."""
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import threading
import traceback

os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import numpy as np
import transporte as tr
from seleccion_canonica import canonical_selection


def legacy_module(home):
    registration = tr.read(home / 'preregistration/registro_transporte.json')
    for name, expected in registration['files'].items():
        assert tr.sha(home / name) == expected, name
    assert registration['registered_before_new_M2'] and registration['synthetic_controls_passed']
    spec = importlib.util.spec_from_file_location('immutable_mixed_coordinator_for_transport', home / 'coordinator.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def interval(modules, streams, budget, dense, clock, next_record, target):
    """Same operations, order, rounding and gates as the original mixed loop."""
    observer_step = modules['cfg']['observer_max_step']
    right = min(round((round(clock / observer_step) + 1) * observer_step, 12), next_record, target)
    histories = []
    for i, stream in enumerate(streams):
        pieces = [dense[i]]
        while pieces[-1].t_max < right - 1e-12:
            pieces.append(stream.advance(target))
        dense[i] = pieces[-1]
        ends = np.array([item.t_max for item in pieces])
        def history(time, pieces=pieces, ends=ends):
            return pieces[min(int(np.searchsorted(ends, time)), len(pieces) - 1)](time)
        histories.append(history)
    if right > clock + 1e-14:
        budget.advance(clock, right, histories[0], histories[1], streams[0].shape, streams[1].shape)
    clock = float(right)
    recorded = clock >= next_record - 1e-12
    if recorded:
        coarse = histories[0](clock).reshape(streams[0].shape)
        fine = histories[1](clock).reshape(streams[1].shape)
        budget.record(clock, coarse[0], coarse[1], fine[0], fine[1])
        next_record = round(next_record / .4 + 1) * .4
        if budget.maximum_errors.get('modal_parseval', 0) > 2e-11 or max(budget.maximum_errors.values(), default=0) > .001:
            raise ValueError('Original observer gate failed for MIXTO')
    return clock, next_record, dense, recorded


def _audit_transport(home, legacy):
    path = home / 'transport/current.npz'
    before = tr.sha(path)
    modules, streams, budget, dense, payload = tr.restore(home, legacy, path)
    reproduced = tr.capture(home, streams, budget, dense, payload['observer_clock'], payload['next_record'], payload['target'])
    tr.assert_equal(payload, reproduced)
    clock = payload['observer_clock']
    tests = dict(all_internal_state_bits_and_nfev_restored=True, original_sources_and_configuration=True,
                 scientific_seed_unchanged=True, restore_used_no_solver_step=True,
                 exact_stage_alias=all(np.shares_memory(s.solver.K, s.solver.K_extended) for s in streams),
                 accepted_states_match_solver=all(np.array_equal(np.stack([s.q, s.v]).ravel(), s.solver.y) for s in streams),
                 clocks_bracket_observer=all(d.t_min <= clock <= d.t_max and s.t == s.solver.t for s, d in zip(streams, dense)),
                 both_energy_and_charge_gates=True,
                 original_observer_maximum_gates=max(budget.maximum_errors.values(), default=0) <= .001,
                 original_Parseval=budget.maximum_errors.get('modal_parseval', 0) <= 2e-11,
                 original_symmetry=budget.maximum_symmetry_residual <= 2e-12)
    for stream in streams:
        mixed = stream.sim.measure(stream.t, stream.q, stream.v)
        original = stream.original_sim.measure(stream.t, stream.q, stream.v)
        tests['both_energy_and_charge_gates'] &= bool(
            np.isfinite(mixed).all() and np.isfinite(original).all()
            and stream.maxe <= 2e-4 and stream.maxe_original <= 2e-4 and stream.maxq <= 1e-9
            and abs(mixed[1] / stream.rows[0][1] - 1) <= 2e-4
            and abs(original[1] / stream.original_rows[0][1] - 1) <= 2e-4
            and abs(mixed[2] / stream.rows[0][2] - 1) <= 1e-9)
    coarse = dense[0](clock).reshape(streams[0].shape)
    fine = dense[1](clock).reshape(streams[1].shape)
    budget.record(clock, coarse[0], coarse[1], fine[0], fine[1])
    tests['independently_reloaded_observer_closure'] = max(budget.rows[-1]['verification'].values()) <= .001
    tests['independently_reloaded_Parseval'] = budget.rows[-1]['short_modes']['parseval_relative_residual'] <= 2e-11
    tests['file_unchanged'] = tr.sha(path) == before
    result = dict(schema='CP12_INTERMEDIATE_INTERNAL_TRANSPORT_ZERO_STEP_AUDIT', passed=all(tests.values()),
                  tests=tests, observer_clock=clock, target=payload['target'], state_sha256=before,
                  physical_metadata=[s.metadata() for s in streams], M2_steps_executed=0,
                  scientific_frontier=False, correction_validated=False, CP12_closed=False)
    assert result['passed'], json.dumps(result)
    return result


def audit_transport(home,legacy):
    with legacy.zero_m2_audit() as attempts:
        result=_audit_transport(home,legacy)
        result['DOP853_construction_or_step_attempts']=len(attempts)
        return result


def preserve_transport(home, legacy, clock):
    tick = round(clock * 10)
    label = 'TRANSPORTE_TAU_%06d' % tick
    with canonical_selection(home):
        legacy.preserve_negative(home, label, 'Exact DOP853 and observer transport; not a scientific frontier', negative=False)
    proof = tr.read(home / 'proofs' / (label + '_permanent.json'))
    assert proof['passed'] and proof['all_payload_hashes_verified']
    candidates = [p for p in (home / 'recoveries' / label).rglob('*.zip')
                  if p.stat().st_size == proof['zip_bytes'] and tr.sha(p) == proof['zip_sha256']]
    assert len(candidates) == 1, 'Independent retrieved transport ZIP unavailable; stop administratively'
    restored = home / 'recoveries' / (label + '_runtime_checked')
    manifest = tr.unpack_verified(candidates[0], restored, proof['zip_sha256'], proof['zip_bytes'])
    environment = dict(os.environ, PYTHONPYCACHEPREFIX=str(restored / 'runtime/pycache'),
                       TMPDIR=str(home / 'runtime/tmp'))
    process = subprocess.run([sys.executable, str(restored / 'controlador_transporte.py'),
                              '--home', str(restored), '--audit-transport'],
                              env=environment, text=True, capture_output=True)
    (home / 'runtime' / (label + '_audit_stdout.json')).write_text(process.stdout)
    (home / 'runtime' / (label + '_audit_stderr.txt')).write_text(process.stderr)
    assert process.returncode == 0, 'Independent transport rehydration failed'
    checked = json.loads(process.stdout)
    assert checked['passed'] and checked['observer_clock'] == clock and checked['M2_steps_executed'] == 0
    proof.update(schema='CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER',
                 observer_clock=clock, payload_files=len(manifest['files']), independent_zero_step_audit=checked,
                 scientific_frontier=False, transport_state_sha256=checked['state_sha256'])
    tr.write(home / 'proofs' / (label + '_permanent.json'), proof)
    legacy.event(home, 'INTERNAL_TRANSPORT_PERMANENTLY_RECOVERED_AND_REHYDRATED',
                 observer_clock=clock, scientific_frontier=False, CP12_closed=False)


def control_next_interval(home, legacy, modules, streams, budget, dense, clock, next_record, target):
    before_steps = [s.accepted for s in streams]
    before_evaluations = [s.solver.nfev for s in streams]
    shadow = home / 'runtime/control_shadow.npz'
    process = subprocess.run([sys.executable, str(home / 'controlador_transporte.py'), '--home', str(home),
                              '--shadow-next-interval', str(shadow)], text=True, capture_output=True)
    (home / 'runtime/control_shadow_stdout.txt').write_text(process.stdout)
    (home / 'runtime/control_shadow_stderr.txt').write_text(process.stderr)
    assert process.returncode == 0, 'Independent one-interval transport control failed'
    clock, next_record, dense, _ = interval(modules, streams, budget, dense, clock, next_record, target)
    actual = tr.capture(home, streams, budget, dense, clock, next_record, target)
    expected = tr.load(shadow)
    tr.assert_equal(actual, expected)
    tr.write(home / 'proofs/CONTROL_TRANSPORTE_M2_UN_INTERVALO.json', dict(
        schema='CP12_NEW_TRANSPORT_CONTROL_NOT_PREFLIGHT_REPETITION', passed=True,
        from_observer_clock=round(clock - .01, 12), to_observer_clock=clock,
        physical_and_passive_states_solver_memory_dense_and_counters_bitwise_exact=True,
        source_transport_sha256=tr.sha(home / 'transport/current.npz'), shadow_transport_sha256=tr.sha(shadow),
        shadow_physical_accepted_steps=[s.accepted - b for s, b in zip(streams, before_steps)],
        shadow_solver_RHS_evaluations=[s.solver.nfev - b for s, b in zip(streams, before_evaluations)],
        diagnostic_work_separate_from_production_counters=True, certified_campaign_repeated=False,
        correction_validated=False, CP12_closed=False))
    return clock, next_record, dense


def advance_segment(home, legacy, target, progress):
    current = home / 'transport/current.npz'
    with np.load(home / 'outputs/MIXTO_par_estado.npz', allow_pickle=False) as zipped:
        closed = float(zipped['time'])
    partial = tr.load(current) if current.exists() else None
    if partial and partial['observer_clock'] > closed + 1e-12:
        assert partial['target'] == target
        modules, streams, budget, dense, partial = tr.restore(home, legacy, current)
        clock, next_record = partial['observer_clock'], partial['next_record']
    else:
        modules, streams, budget = legacy.streams_and_budget(home)
        clock = streams[0].t
        next_record = round(clock / .4 + 1) * .4
        dense = None
    progress.update(observer_clock=clock, streams=streams)
    try:
        if dense is None:
            dense = [stream.advance(target) for stream in streams]
        while clock < target - 1e-12:
            clock, next_record, dense, recorded = interval(modules, streams, budget, dense, clock, next_record, target)
            progress['observer_clock'] = clock
            if recorded and clock < target - 1e-12:
                progress['administrative_transport_phase'] = True
                tr.save(current, tr.capture(home, streams, budget, dense, clock, next_record, target))
                audit_transport(home, legacy)
                durable_clock = clock
                if not (home / 'proofs/CONTROL_TRANSPORTE_M2_UN_INTERVALO.json').exists():
                    clock, next_record, dense = control_next_interval(home, legacy, modules, streams, budget, dense,
                                                                    clock, next_record, target)
                    progress['observer_clock'] = clock
                # First .4 proves the full route; thereafter every 1.6, without solver restarts.
                if abs(durable_clock - .4) < 1e-12 or round(durable_clock / .4) % 4 == 0:
                    preserve_transport(home, legacy, durable_clock)
                progress['administrative_transport_phase'] = False
        for stream in streams:
            stream.close_segment()
        check = modules['native'].reference(streams[1].sim, (streams[0].sim, streams[1].sim, streams[0].q, streams[1].q))
        budget.algebra.append(dict(time=clock, **check))
        legacy.save_state(home, streams, budget)
    except BaseException:
        failed = home / 'negative' / ('segment_%04d' % target)
        failed.mkdir(parents=True, exist_ok=False)
        arrays = {f'grid_{i}_{key}': getattr(stream, key) for i, stream in enumerate(streams)
                  for key in ('q', 'v', 'initial_q', 'initial_v')}
        arrays.update(physical_metadata=json.dumps([s.metadata() for s in streams]),
                      budget_rows=json.dumps(budget.rows), budget_maximum_errors=json.dumps(budget.maximum_errors),
                      coupled_angular_basis=budget.S)
        for name, family in [('raw', budget.raw), ('coupled', budget.coupled)]:
            for i, observer in enumerate(family):
                arrays[f'{name}_{i}_q'], arrays[f'{name}_{i}_v'] = observer.q, observer.v
        np.savez_compressed(failed / 'failed_physical_and_observer_state.npz', **arrays)
        shadow = home / 'runtime/control_shadow.npz'
        if shadow.exists():
            shutil.copyfile(shadow, failed / 'control_shadow.npz')
            shutil.copyfile(shadow.with_suffix('.json'), failed / 'control_shadow.json')
        tr.write(failed / 'FAILURE.json', dict(target=target, observer_clock=progress.get('observer_clock'),
                 metadata=[s.metadata() for s in streams], traceback=traceback.format_exc(),
                 administrative_transport_phase=progress.get('administrative_transport_phase', False),
                 maximum_errors=budget.maximum_errors, failed_state_is_certified_frontier=False,
                 correction_validated=False, CP12_closed=False))
        raise


def main(args):
    home = args.home.resolve()
    legacy = legacy_module(home)
    if args.audit_transport:
        print(json.dumps(audit_transport(home, legacy)))
        return
    if args.shadow_next_interval:
        modules, streams, budget, dense, payload = tr.restore(home, legacy, home / 'transport/current.npz')
        clock, next_record, dense, _ = interval(modules, streams, budget, dense, payload['observer_clock'],
                                              payload['next_record'], payload['target'])
        tr.save(args.shadow_next_interval, tr.capture(home, streams, budget, dense, clock, next_record, payload['target']))
        return
    assert args.continue_to == 160
    with (home / 'runtime/worker_started.json').open('x') as stream:
        json.dump(dict(at=legacy.now(), original_science_unchanged=True, exact_internal_transport=True), stream)
    lock = (home / 'runtime/worker.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    progress = {}
    stop = threading.Event()
    def heartbeat():
        while not stop.wait(30):
            tr.write(home / 'runtime/heartbeat.json', dict(at=legacy.now(), observer_clock=progress.get('observer_clock'),
                physical_streams=[dict(time=s.t, accepted=s.accepted, nfev_closed=s.nfev) for s in progress.get('streams', [])],
                administrative_transport_phase=progress.get('administrative_transport_phase', False),
                not_a_restart_certificate=True))
    threading.Thread(target=heartbeat, daemon=True).start()
    try:
        with np.load(home / 'outputs/MIXTO_par_estado.npz', allow_pickle=False) as zipped:
            start = int(zipped['time'])
        for target in range(start + 8, 161, 8):
            previous = tr.read(home / 'proofs' / ('tau%04d_permanent.json' % (target - 8)))
            assert previous['passed'] and previous['state_sha256'] == tr.sha(home / 'outputs/MIXTO_par_estado.npz')
            current = home / 'transport/current.npz'
            partial = tr.load(current) if current.exists() else None
            resuming = bool(partial and partial['observer_clock'] > target - 8 + 1e-12)
            receipt = tr.read(home / 'outputs/procedencia.json')
            if resuming:
                assert partial['target'] == target and partial['source_receipt_sha256'] == tr.sha(home / 'outputs/procedencia.json')
                assert receipt['segments'][-1]['to_time'] == target and receipt['status'] == 'EN_PROGRESO'
            else:
                assert previous['receipt_sha256'] == tr.sha(home / 'outputs/procedencia.json')
                receipt['status'] = 'EN_PROGRESO'
                receipt['segments'].append(dict(started_at=legacy.now(), from_time=target-8, to_time=target,
                      initial_state_sha256=previous['state_sha256'], status='EN_PROGRESO'))
                tr.write(home / 'outputs/procedencia.json', receipt)
            legacy.event(home, 'MIXTO_TRANSPORT_BEGIN_OR_RESUME_SEGMENT', to_time=target,
                         resuming_internal_state=resuming, CP12_closed=False)
            try:
                advance_segment(home, legacy, target, progress)
                with canonical_selection(home):
                    legacy.preservation_module(home).preserve(home, target)
            except BaseException:
                failure = traceback.format_exc()
                receipt = tr.read(home / 'outputs/procedencia.json')
                receipt['status'] = 'FALLIDA_SIN_NUEVA_FRONTERA_CERTIFICADA'
                receipt['segments'][-1].update(status='FALLIDA', ended_at=legacy.now(), reason=failure.splitlines()[-1])
                tr.write(home / 'outputs/procedencia.json', receipt)
                administrative = progress.get('administrative_transport_phase', False)
                legacy.event(home, 'MIXTO_TRANSPORT_STOPPED', target=target, reason=failure.splitlines()[-1],
                             administrative_transport_phase=administrative, CP12_closed=False)
                with canonical_selection(home):
                    legacy.preserve_negative(home, 'NEGATIVO_TRANSPORTE_%04d' % target, failure, negative=not administrative)
                raise
        with canonical_selection(home):
            legacy.final_review(home)
    finally:
        stop.set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--continue-to', type=int)
    parser.add_argument('--audit-transport', action='store_true')
    parser.add_argument('--shadow-next-interval', type=Path)
    main(parser.parse_args())
