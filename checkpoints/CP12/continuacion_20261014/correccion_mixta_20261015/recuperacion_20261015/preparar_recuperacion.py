"""Copy an authenticated checkpoint; never integrate or reseed M2."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import uuid


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def prepare(source, home, helpers, registration_commit):
    source, home, helpers = source.resolve(), home.resolve(), helpers.resolve()
    assert not home.exists(), 'Never overwrite an execution'
    manifest = read(source / 'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json')
    assert manifest['schema'] == 'CP12_MIXTO_TRIAL_FULL_CAPSULE_NOT_CORRECTION_VALIDATION'
    assert manifest['time'] == 0
    assert len(manifest['files']) == 81
    expected_state = '753c8400b3fad8a34b8286cfb6ac6ea8a10def61c8abd42ea4336efe5026874b'
    assert digest(source / 'outputs/MIXTO_par_estado.npz') == expected_state
    for name, item in manifest['files'].items():
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        path = source / relative
        assert not path.is_symlink() and path.stat().st_size == item['bytes']
        assert digest(path) == item['sha256'], name
    home.mkdir()
    for name in manifest['files']:
        destination = home / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, destination)
    previous_meta = read(source / 'preregistration/nueva_identidad.json')
    previous_location = read(source / 'preregistration/ubicacion.json')
    previous_receipt = read(source / 'outputs/procedencia.json')
    (home / 'ancestor').mkdir(exist_ok=True)
    for name in ('nueva_identidad.json', 'ubicacion.json'):
        shutil.copyfile(source / 'preregistration' / name, home / 'ancestor' / name)
    shutil.copyfile(source / 'outputs/procedencia.json', home / 'ancestor/procedencia_tau0_original.json')
    shutil.copyfile(source / 'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json', home / 'ancestor/MANIFIESTO_ORIGINAL.json')
    shutil.copyfile(source / 'proofs/tau0000_audit.json', home / 'ancestor/audit_tau0_original.json')
    (home / 'proofs/tau0000_audit.json').unlink()
    attempt = uuid.uuid4().hex
    at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    meta = dict(previous_meta, execution_uuid=attempt, recovery_of_execution_uuid=previous_meta['execution_uuid'],
                scientific_experiment_id_unchanged=True, recovery_registration_commit=registration_commit)
    location = dict(previous_location, execution_uuid=attempt, execution_home=str(home),
                    recovery_of_execution_uuid=previous_location['execution_uuid'],
                    previous_executor_termination_assumed=False)
    receipt = dict(previous_receipt, status='RECUPERADA_TAU0_SIN_NUEVOS_PASOS',
                   execution_attempt_uuid=attempt, source_receipt_sha256=digest(source / 'outputs/procedencia.json'),
                   scientific_experiment_id_unchanged=True, original_private_receipt_recreated=False,
                   recovery_attempts=[dict(at=at, time=0, execution_attempt_uuid=attempt,
                       source_state_sha256=expected_state, registration_commit=registration_commit,
                       previous_executor_activity='UNKNOWN_ACTIVITY', previous_executor_termination_assumed=False)])
    write(home / 'preregistration/nueva_identidad.json', meta)
    write(home / 'preregistration/ubicacion.json', location)
    write(home / 'outputs/procedencia.json', receipt)
    for directory in ('analysis', 'negative', 'capsules', 'recoveries', 'runtime/tmp', 'runtime/force', 'runtime/library'):
        (home / directory).mkdir(parents=True, exist_ok=True)
    for name in ('library_download.py', 'library_upload.py', 'library_file_transfer.py', 'library_hosted_apps.py'):
        shutil.copyfile(helpers / name, home / 'runtime/library' / name)
    for name in ('preparar_recuperacion.py', 'PRERREGISTRO.md'):
        shutil.copyfile(Path(__file__).parent / name, home / 'preregistration' / ('recovery_' + name))
    write(home / 'preregistration/recovery_attempt.json', dict(at=at, execution_attempt_uuid=attempt,
          source_archive_sha256='e147eaaa564e811cf04d5629f8092d8655788180dba7be37f27dbf00a7da14db',
          source_state_sha256=expected_state, previous_executor_termination_assumed=False,
          registration_commit=registration_commit, M2_steps_executed=0))
    write(home / 'runtime/attempt_host_identity.json', dict(at=at, hostname=os.uname().nodename,
          boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
          pid_namespace=os.readlink('/proc/self/ns/pid'), scope='Own restored execution only'))
    for name, expected in meta['captured_sources'].items():
        assert digest(home / name) == expected, name
    assert digest(home / 'outputs/MIXTO_par_estado.npz') == expected_state
    return dict(home=str(home), execution_attempt_uuid=attempt, state_sha256=expected_state,
                captured_sources_unchanged=True, M2_steps_executed=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--helpers', type=Path, required=True)
    parser.add_argument('--registration-commit', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.home, args.helpers, args.registration_commit)))
