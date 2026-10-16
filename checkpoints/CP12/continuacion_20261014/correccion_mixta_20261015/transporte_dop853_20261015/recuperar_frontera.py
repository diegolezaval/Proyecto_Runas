"""Recover an authenticated full MIXTO boundary without evolving M2."""
from pathlib import Path
import argparse
import datetime
import json
import os
import shutil
import stat
import subprocess
import sys
import uuid
import zipfile
import hashlib
import transporte as tr


def recover(args):
    capsule, certificate = args.capsule.resolve(), args.certificate.resolve()
    proof = tr.read(certificate)
    assert proof['schema'] == 'CP12_MIXTO_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED'
    assert proof['passed'] and proof['all_payload_hashes_verified']
    audit = proof['independent_extracted_audit']
    assert audit['passed'] and audit['M2_steps_executed'] == 0 and all(audit['tests'].values())
    time = proof['time']
    assert time == audit['time'] and time > 0 and time % 8 == 0
    assert capsule.stat().st_size == proof['zip_bytes'] and tr.sha(capsule) == proof['zip_sha256']
    home = args.destination.resolve()
    assert not home.exists()
    with zipfile.ZipFile(capsule) as zipped:
        names = zipped.namelist()
        assert len(names) == len(set(names)) and names
        first = Path(names[0]).parts[0]
        for item in zipped.infolist():
            path = Path(item.filename)
            assert not path.is_absolute() and '..' not in path.parts and path.parts[0] == first
            assert path.as_posix() == item.filename
            assert not stat.S_ISLNK(item.external_attr >> 16)
        manifest_name = first + '/MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'
        manifest = json.loads(zipped.read(manifest_name))
        assert manifest['execution_uuid'] == first and manifest['time'] == time
        assert manifest['execution_run_id'] == proof['execution_run_id']
        assert set(names) == {first + '/' + name for name in manifest['files']} | {manifest_name}
        for name, expected in manifest['files'].items():
            data = zipped.read(first + '/' + name)
            assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256'], name
        home.mkdir(parents=True)
        for name in names:
            relative = Path(name).relative_to(first)
            target = home / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zipped.read(name))
    registration = tr.read(args.public_sources / 'REGISTRO.json')
    assert registration['files'] == tr.read(home / 'preregistration/registro_transporte.json')['files']
    for name, expected in registration['files'].items():
        assert tr.sha(home / name) == expected and tr.sha(args.public_sources / name) == expected, name
    for name, key in [('outputs/MIXTO_par_estado.npz', 'state_sha256'),
                      ('outputs/procedencia.json', 'receipt_sha256'),
                      ('configuration.json', 'configuration_sha256')]:
        assert tr.sha(home / name) == proof[key] == audit[key], name
    old_transport = home / 'transport/current.json'
    if old_transport.exists():
        assert tr.read(old_transport)['observer_clock'] <= time
    for name in ('tmp', 'force', 'library'):
        (home / 'runtime' / name).mkdir(parents=True, exist_ok=True)
    for name in ('capsules', 'recoveries'):
        (home / name).mkdir(exist_ok=True)
    for name in ('library_download.py', 'library_upload.py', 'library_hosted_apps.py', 'library_file_transfer.py'):
        shutil.copyfile(args.helpers / name, home / 'runtime/library' / name)
    # This external certificate was issued after the capsule was uploaded.
    # Install its authenticated content, never reconstruct a historical receipt.
    previous = home / 'proofs' / ('tau%04d_permanent.json' % time)
    assert not previous.exists()
    shutil.copyfile(certificate, previous)
    session = dict(schema='CP12_FULL_MIXTO_BOUNDARY_RECOVERY_SESSION', session_uuid=uuid.uuid4().hex,
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), time=time,
        source_capsule_sha256=proof['zip_sha256'], source_capsule_bytes=proof['zip_bytes'],
        source_external_certificate_sha256=tr.sha(certificate), actual_home=str(home),
        previous_executor_termination_assumed=False, source_receipt_unchanged=True,
        physical_prefix_repeated=False, M2_steps_executed=0, CP12_closed=False)
    tr.write(home / 'preregistration/recovery_sessions' / (session['session_uuid'] + '.json'), session)
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
        PYTHONPYCACHEPREFIX=str(home / 'runtime/pycache'), TMPDIR=str(home / 'runtime/tmp'))
    process = subprocess.run([sys.executable, str(home / 'coordinator.py'), '--home', str(home),
        '--audit-only', str(time)], env=environment, text=True, capture_output=True)
    (home / 'runtime/recovery_audit_stdout.json').write_text(process.stdout)
    (home / 'runtime/recovery_audit_stderr.txt').write_text(process.stderr)
    assert process.returncode == 0, 'Recovered boundary audit failed; inspect retained stderr'
    checked = json.loads(process.stdout)
    assert checked['passed'] and checked['M2_steps_executed'] == 0 and checked['time'] == time
    assert checked['state_sha256'] == proof['state_sha256'] and checked['receipt_sha256'] == proof['receipt_sha256']
    result = dict(schema='CP12_FULL_MIXTO_BOUNDARY_RECOVERED_IN_NEW_SESSION', passed=True, time=time,
        capsule_sha256=proof['zip_sha256'], capsule_bytes=proof['zip_bytes'], payload_files=len(manifest['files']),
        independent_zero_step_audit=checked, source_receipt_unchanged=True, M2_steps_executed=0,
        correction_validated=False, CP12_closed=False)
    tr.write(home / 'proofs' / ('RECOVERY_SESSION_' + session['session_uuid'] + '.json'), result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--capsule', type=Path, required=True)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--public-sources', type=Path, required=True)
    parser.add_argument('--helpers', type=Path, required=True)
    print(json.dumps(recover(parser.parse_args())))
