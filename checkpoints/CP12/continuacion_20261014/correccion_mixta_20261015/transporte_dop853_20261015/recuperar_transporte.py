"""Verify a permanent transport capsule and rehydrate it without M2 steps."""
from pathlib import Path
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import uuid
import transporte as tr


def recover(args):
    destination = args.destination.resolve()
    manifest = tr.unpack_verified(args.capsule.resolve(), destination, args.sha256, args.bytes)
    registration = tr.read(args.public_sources / 'REGISTRO.json')
    captured = tr.read(destination / 'preregistration/registro_transporte.json')
    assert registration['files'] == captured['files']
    for name, expected in registration['files'].items():
        assert tr.sha(destination / name) == expected and tr.sha(args.public_sources / name) == expected, name
    for name in ('tmp', 'force', 'library'):
        (destination / 'runtime' / name).mkdir(parents=True, exist_ok=True)
    for name in ('capsules', 'recoveries'):
        (destination / name).mkdir(exist_ok=True)
    for name in ('library_download.py', 'library_upload.py', 'library_hosted_apps.py', 'library_file_transfer.py'):
        shutil.copyfile(args.helpers / name, destination / 'runtime/library' / name)
    session = dict(schema='CP12_TRANSPORT_RECOVERY_SESSION_NO_RECEIPT_REWRITING',
                   session_uuid=uuid.uuid4().hex,
                   at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   source_capsule_sha256=args.sha256, source_capsule_bytes=args.bytes,
                   source_payload_files=len(manifest['files']),
                   authenticated_source_receipt_sha256=tr.sha(destination / 'outputs/procedencia.json'),
                   actual_home=str(destination), historical_location_metadata_retained=True,
                   previous_executor_termination_assumed=False, M2_steps_executed=0, CP12_closed=False)
    # The scientific receipt and solver image stay byte-identical. This new session
    # gets a distinct record rather than impersonating an old executor.
    (destination / 'preregistration/recovery_sessions').mkdir(exist_ok=True)
    tr.write(destination / 'preregistration/recovery_sessions' / (session['session_uuid'] + '.json'), session)
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       PYTHONPYCACHEPREFIX=str(destination / 'runtime/pycache'), TMPDIR=str(destination / 'runtime/tmp'))
    process = subprocess.run([sys.executable, str(destination / 'controlador_transporte.py'),
                              '--home', str(destination), '--audit-transport'],
                              env=environment, text=True, capture_output=True)
    (destination / 'runtime/recovery_audit_stdout.json').write_text(process.stdout)
    (destination / 'runtime/recovery_audit_stderr.txt').write_text(process.stderr)
    assert process.returncode == 0, 'Recovered transport audit failed; inspect retained stderr'
    checked = json.loads(process.stdout)
    assert checked['passed'] and checked['M2_steps_executed'] == 0
    assert tr.sha(destination / 'outputs/procedencia.json') == session['authenticated_source_receipt_sha256']
    proof = dict(schema='CP12_TRANSPORT_RECOVERED_IN_NEW_SESSION_ZERO_STEP', passed=True,
                 capsule_sha256=args.sha256, capsule_bytes=args.bytes, payload_files=len(manifest['files']),
                 observer_clock=checked['observer_clock'], independent_zero_step_audit=checked,
                 source_receipt_unchanged=True, solver_not_restarted=True,
                 M2_steps_executed=0, scientific_frontier=False, CP12_closed=False)
    tr.write(destination / 'proofs' / ('RECOVERY_SESSION_' + session['session_uuid'] + '.json'), proof)
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--capsule', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--bytes', type=int, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--public-sources', type=Path, required=True)
    parser.add_argument('--helpers', type=Path, required=True)
    print(json.dumps(recover(parser.parse_args())))
