"""Recover saved P3 tau0 exactly and correct only its administrative capture."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import uuid
import zipfile
import stat


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(p):
    return json.loads(p.read_text())


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def main():
    parser = argparse.ArgumentParser()
    for name in ('archive', 'source_home', 'package', 'helpers', 'home'):
        parser.add_argument('--'+name.replace('_', '-'), type=Path, required=True)
    args = parser.parse_args()
    home, package = args.home.resolve(), args.package.resolve()
    assert not home.exists()
    incident = read(package/'INCIDENTE_ADMINISTRATIVO_TAU0.json')
    assert args.archive.stat().st_size == incident['archive_bytes'] and sha(args.archive) == incident['archive_sha256']
    original_uid = 'd43807ae26fe43ed9e965a051b5f7659'
    with zipfile.ZipFile(args.archive) as z:
        names = z.namelist()
        assert len(names) == len(set(names))
        prefix = original_uid+'/'
        manifest = json.loads(z.read(prefix+'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'))
        assert set(names) == {prefix+n for n in manifest['files']} | {prefix+'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'}
        for entry in z.infolist():
            path = Path(entry.filename)
            assert not path.is_absolute() and '..' not in path.parts and not stat.S_ISLNK(entry.external_attr >> 16)
        for name, record in manifest['files'].items():
            data = z.read(prefix+name)
            assert len(data) == record['bytes'] and hashlib.sha256(data).hexdigest() == record['sha256'], name
        home.mkdir()
        for name in manifest['files']:
            target = home/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(prefix+name))
    source_meta = read(home/'preregistration/nueva_identidad.json')
    excluded = '__pycache__/transporte.cpython-312.pyc'
    assert len(source_meta['captured_sources']) == 70 and excluded in source_meta['captured_sources']
    for name, expected in source_meta['captured_sources'].items():
        if name != excluded:
            assert sha(home/name) == expected, name
    bytecode = args.source_home/excluded
    assert sha(bytecode) == source_meta['captured_sources'][excluded] == incident['extra_bytecode_sha256']
    ancestor = home/'ancestor/administrative_capture_tau0'
    ancestor.mkdir(parents=True)
    for name in ('nueva_identidad.json', 'ubicacion.json', 'registro_publico.json'):
        shutil.copyfile(home/'preregistration'/name, ancestor/name)
    shutil.copyfile(home/'outputs/procedencia.json', ancestor/'original_procedencia.json')
    shutil.move(home/'proofs/tau0000_audit.json', ancestor/'original_local_tau0_audit.json')
    shutil.copyfile(bytecode, ancestor/'omitted_bytecode_transporte.bin')
    write(ancestor/'original_full_manifest.json', manifest)
    recovery = home/'preregistration/recovery_tau0'
    recovery.mkdir()
    for name in ('RECUPERACION_TAU0.md', 'recover_tau0.py', 'INCIDENTE_ADMINISTRATIVO_TAU0.json'):
        shutil.copyfile(package/name, recovery/name)
    uid = uuid.uuid4().hex
    captured = {n: h for n, h in source_meta['captured_sources'].items() if n != excluded}
    for p in list(ancestor.iterdir())+list(recovery.iterdir()):
        captured[p.relative_to(home).as_posix()] = sha(p)
    meta = dict(source_meta)
    meta.update(execution_uuid=uid, captured_sources=captured,
        recovery_of_execution_uuid=original_uid, scientific_experiment_id_unchanged=True,
        administrative_revision='exclude_noncanonical_bytecode_from_source_capture_1',
        source_state_sha256=incident['source_state_sha256'], M2_steps_executed_in_recovery=0)
    write(home/'preregistration/nueva_identidad.json', meta)
    info = read(home/'preregistration/ubicacion.json')
    info.update(execution_uuid=uid, execution_home=str(home), recovery_of_execution_uuid=original_uid)
    write(home/'preregistration/ubicacion.json', info)
    write(home/'preregistration/registro_publico.json', dict(registered_before_M2=False,
        captured_sources=captured, physical_steps_executed=0, recovery_identity_publication_pending=True))
    receipt = read(home/'outputs/procedencia.json')
    receipt.update(execution_attempt_uuid=uid, source_receipt_sha256=incident['source_receipt_sha256'],
        scientific_experiment_id_unchanged=True, M2_steps_executed_in_recovery=0,
        administrative_recovery_kind='Canonical capture repair; NPZ and configuration byte identical')
    write(home/'outputs/procedencia.json', receipt)
    for name in ('runtime/tmp', 'runtime/force', 'runtime/library', 'capsules', 'recoveries', 'transport'):
        (home/name).mkdir(parents=True, exist_ok=True)
    for name in ('library_download.py', 'library_hosted_apps.py', 'library_file_transfer.py', 'library_upload.py'):
        shutil.copyfile(args.helpers/name, home/'runtime/library'/name)
    assert sha(home/'outputs/MIXTO_par_estado.npz') == incident['source_state_sha256']
    assert sha(home/'configuration.json') == incident['source_configuration_sha256']
    assert meta['execution_run_id'] == source_meta['execution_run_id']
    result = dict(home=str(home), execution_uuid=uid, execution_run_id=meta['execution_run_id'],
        source_execution_uuid=original_uid, captured_sources=captured,
        state_sha256=sha(home/'outputs/MIXTO_par_estado.npz'),
        configuration_sha256=sha(home/'configuration.json'),
        receipt_sha256=sha(home/'outputs/procedencia.json'),
        old69_source_hashes_unchanged=True, bytecode_preserved_as_evidence=True,
        M2_steps_executed=0, seed_calls=0, preflight_repeated=False, CP12_closed=False)
    write(home/'preregistration/RECUPERACION_INSTANCIA.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
