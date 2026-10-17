"""Administrative sequencing of captured science, with synchronous prefix gates."""
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


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def sequence(targets, evolve_preserve, check_prefix):
    """No following evolution is called until the previous prefix passes."""
    for target in targets:
        evolve_preserve(target)
        if target < 160 and not check_prefix(target):
            return target
    return None


def run(home, registered):
    home, registered = home.resolve(), registered.resolve()
    sys.path.insert(0, str(home))
    import transporte as tr
    import numpy as np
    spec = importlib.util.spec_from_file_location('immutable_transport_controller', home / 'controlador_transporte.py')
    controller = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controller)
    from aislar_fuentes_subida import install
    install(controller, home)
    legacy = controller.legacy_module(home)
    registration = read(registered / 'REGISTRO.json')
    for name, expected in registration['administrative_files'].items():
        assert sha(registered / name) == expected
    assert registration['scientific_kernels_changed'] is False
    assert read(registered / 'CONTROL_SECUENCIA.json')['passed']
    assert read(registered / 'CONTROL_AISLAMIENTO.json')['passed']
    route = read(registered / 'CONTROL_RUTA_COMPLETA.json')
    assert route['passed'] and route['M2_steps_executed'] == 0
    assert route['canonical_source_unchanged_after_upload_and_recovery']
    assert route['all_payload_hashes_verified']
    assert not (home / 'runtime/observed_guardian_exit.json').exists()
    with (home / 'runtime/worker_started.json').open('x') as stream:
        json.dump(dict(at=legacy.now(), administrative_supervisor_sha256=sha(Path(__file__)),
                       original_science_unchanged=True, exact_internal_transport=True), stream)
    lock = (home / 'runtime/worker.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    progress, stop = {}, threading.Event()
    def heartbeat():
        while not stop.wait(30):
            tr.write(home / 'runtime/heartbeat.json', dict(at=legacy.now(),
                observer_clock=progress.get('observer_clock'),
                physical_streams=[s.metadata() for s in progress.get('streams', [])],
                administrative_transport_phase=progress.get('administrative_transport_phase', False),
                not_a_restart_certificate=True))
    threading.Thread(target=heartbeat, daemon=True).start()
    with np.load(home / 'outputs/MIXTO_par_estado.npz', allow_pickle=False) as data:
        start = int(data['time'])
    def evolve_preserve(target):
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
            controller.advance_segment(home, legacy, target, progress)
            progress['administrative_transport_phase'] = True
            with controller.canonical_selection(home):
                legacy.preservation_module(home).preserve(home, target)
            progress['administrative_transport_phase'] = False
        except BaseException:
            failure = traceback.format_exc()
            receipt = tr.read(home / 'outputs/procedencia.json')
            receipt['status'] = 'FALLIDA_SIN_NUEVA_FRONTERA_CERTIFICADA'
            receipt['segments'][-1].update(status='FALLIDA', ended_at=legacy.now(), reason=failure.splitlines()[-1])
            tr.write(home / 'outputs/procedencia.json', receipt)
            administrative = progress.get('administrative_transport_phase', False)
            legacy.event(home, 'MIXTO_TRANSPORT_STOPPED', target=target,
                         reason=failure.splitlines()[-1], administrative_transport_phase=administrative, CP12_closed=False)
            with controller.canonical_selection(home):
                legacy.preserve_negative(home, 'NEGATIVO_SESION_20261017_%04d' % target, failure, negative=not administrative)
            raise
    def check_prefix(target):
        proof = tr.read(home / 'proofs' / ('tau%04d_permanent.json' % target))
        uid = proof['execution_uuid']
        restored = home / 'recoveries' / ('CP12_CANDIDATO_MIXTO_' + uid + '_tau%04d_checked' % target) / uid
        output = home / 'runtime/prefix_readings' / ('tau%04d' % target)
        reader = registered / 'leer_metricas_prefijo.py'
        assert sha(reader) == registration['prefix_reader_sha256']
        assert sha(registered / 'REGISTRO_LECTURA_PREFIJOS_CONTINUACION_20261016.json') == registration['prefix_registration_sha256']
        command = [sys.executable, str(reader), '--home', str(restored),
            '--certificate', str(home / 'proofs' / ('tau%04d_permanent.json' % target)),
            '--registration', str(registered / 'REGISTRO_LECTURA_PREFIJOS_CONTINUACION_20261016.json'),
            '--output', str(output)]
        process = subprocess.run(command, text=True, capture_output=True)
        (home / 'runtime' / ('prefix_%04d_stdout.json' % target)).write_text(process.stdout)
        (home / 'runtime' / ('prefix_%04d_stderr.txt' % target)).write_text(process.stderr)
        if process.returncode:
            raise RuntimeError('Administrative prefix reading failure; no next M2 segment authorized')
        result = read(output / 'RESULTADO.json')
        assert result['time'] == target and result['M2_steps_executed'] == 0
        assert result['source_state_sha256'] == proof['state_sha256']
        assert result['source_receipt_sha256'] == proof['receipt_sha256']
        destination = home / 'analysis/lectura_prefijos_continuacion' / ('TAU%04d_RESULTADO.json' % target)
        assert not destination.exists()
        shutil.copyfile(output / 'RESULTADO.json', destination)
        legacy.event(home, 'SPATIAL_PREFIX_GATE_BEFORE_NEXT_M2_SEGMENT', time=target,
                     all_five_pair_limits_met=result['prefix_pair_limits_met'], CP12_closed=False)
        return result['prefix_pair_limits_met']
    try:
        failed_at = sequence(range(start + 8, 161, 8), evolve_preserve, check_prefix)
        if failed_at is not None:
            tr.write(home / 'analysis/PUERTA_ESPACIAL_NEGATIVA_20261017.json', dict(
                time=failed_at, threshold=.02, next_segment_executed=False,
                certified_boundary_retained=True, scientific_gate_failed=True,
                correction_validated=False, CP12_closed=False))
            with controller.canonical_selection(home):
                legacy.preserve_negative(home, 'NEGATIVO_ESPACIAL_TAU%04d_20261017' % failed_at,
                    'One or more original spatial prefix metrics exceeded .02; continuation suspended', negative=True)
            return 2
        with controller.canonical_selection(home):
            legacy.final_review(home)
        return 0
    finally:
        stop.set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--registered', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.home, args.registered))
