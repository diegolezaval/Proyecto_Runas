"""Read registered residuals after an observed own-worker exit; no M2 steps."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import time
import traceback
import zipfile

READER_HASH = 'b29659e0fd03731ec2aa11f2175a604f9ce64eed9562dee8de01249cea9fb314'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def verify_tree(root, manifest):
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*')
              if p.is_file() and p.name != 'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'
              and not any(x in ('runtime', 'cache', '__pycache__') for x in p.relative_to(root).parts)
              and p.suffix not in ('.pyc', '.so', '.tmp')}
    assert actual == set(manifest['files']), 'Independent capsule coverage differs'
    for name, item in manifest['files'].items():
        path = root / name
        assert not path.is_symlink() and path.stat().st_size == item['bytes'], name
        assert digest(path) == item['sha256'], name


def run(home, output, registration_commit):
    home, output = home.resolve(), output.resolve()
    assert not output.exists() and not output.is_relative_to(home)
    output.mkdir()
    write(output / 'status.json', dict(status='WAITING_FOR_OBSERVED_OWN_GUARDIAN_EXIT',
          at=datetime.datetime.now(datetime.timezone.utc).isoformat(), M2_steps_executed=0,
          CP12_closed=False, registration_commit=registration_commit))
    reader = Path(__file__).with_name('leer_residuo_mixto.py')
    assert digest(reader) == READER_HASH
    while not (home / 'runtime/observed_guardian_exit.json').exists():
        time.sleep(30)
    ended = read(home / 'runtime/observed_guardian_exit.json')
    shutil.copyfile(home / 'runtime/observed_guardian_exit.json', output / 'observed_own_exit.json')
    assert ended['scope'] == 'Observed own guardian only' and ended['previous_executor_termination_assumed'] is False
    if ended['returncode'] != 0:
        write(output / 'status.json', dict(status='WORKER_STOPPED_NO_AUTOMATIC_RETRY',
              returncode=ended['returncode'], M2_steps_executed=0, CP12_closed=False,
              administrative_or_scientific_cause_requires_reading_preserved_failure=True))
        return
    proof = read(home / 'proofs/tau0160_permanent.json')
    assert proof['passed'] and proof['time'] == 160 and proof['all_payload_hashes_verified']
    assert proof['independent_extracted_audit']['passed']
    uid = read(home / 'preregistration/ubicacion.json')['execution_uuid']
    restored = home / 'recoveries' / ('CP12_CANDIDATO_MIXTO_' + uid + '_tau0160_checked') / uid
    assert not (restored / 'runtime/worker_started.json').exists()
    verify_tree(restored, read(restored / 'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json'))
    assert digest(restored / 'outputs/MIXTO_par_estado.npz') == proof['state_sha256']
    choices = [label for label in ('RESULTADO_FINAL_TAU0160', 'PUERTA_FISICA_NEGATIVA_TAU0160')
               if (home / 'proofs' / (label + '_permanent.json')).exists()]
    assert len(choices) == 1
    label = choices[0]
    final_proof = read(home / 'proofs' / (label + '_permanent.json'))
    assert final_proof['passed'] and final_proof['all_payload_hashes_verified']
    # This is the independently retrieved archive, not the worker's source ZIP.
    archive = home / 'recoveries' / label / 'download' / final_proof['file_name']
    if not archive.exists():
        candidates = [p for p in (home / 'recoveries' / label).rglob('*.zip')
                      if p.stat().st_size == final_proof['zip_bytes'] and digest(p) == final_proof['zip_sha256']]
        assert len(candidates) <= 1
        if candidates:
            archive = candidates[0]
        else:
            sys.path.insert(0, str(home / 'runtime/library'))
            from library_hosted_apps import HostedAppsClient
            response = HostedAppsClient().call_tool('connector_openai_library', 'prepare_materialize',
                {'items': [{'file_id': final_proof['file_id'],
                            'library_file_id': final_proof['library_file_id'],
                            'file_name': final_proof['file_name']}],
                 'destination': {'directory': str(output / 'physical_download')}})
            assert not response.get('isError')
            transfer_result = response.get('structuredContent')
            if transfer_result is None:
                transfer_result = json.loads(next(c['text'] for c in response['content'] if c.get('type') == 'text'))
            transfer_result = transfer_result.get('result', transfer_result)
            assert not transfer_result.get('unavailable_items') and len(transfer_result['transfers']) == 1
            transfer = transfer_result['transfers'][0]
            if transfer.get('workspace_path'):
                archive = Path(transfer['workspace_path'])
                arguments = ['apply-xattrs', str(archive), transfer['library_file_id']]
                payload = transfer.get('xattrs', [])
            else:
                archive = output / 'physical_download' / final_proof['file_name']
                arguments, payload = ['materialize', str(archive)], transfer
            applied = subprocess.run([sys.executable, str(home / 'runtime/library/library_file_transfer.py'),
                                      *arguments], input=json.dumps(payload), text=True, capture_output=True)
            assert applied.returncode == 0, 'Final supplement recovery failed'
    assert archive.stat().st_size == final_proof['zip_bytes'] and digest(archive) == final_proof['zip_sha256']
    physical_home = output / 'recovered_physical_supplement'
    physical_home.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        assert len(names) == len(set(names))
        for item in zipped.infolist():
            path = Path(item.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert not stat.S_ISLNK(item.external_attr >> 16)
        manifest = json.loads(zipped.read('MANIFIESTO_NEGATIVO.json'))
        assert set(names) == set(manifest['files']) | {'MANIFIESTO_NEGATIVO.json'}
        for name, item in manifest['files'].items():
            data = zipped.read(name)
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], name
        zipped.extractall(physical_home)
    physical = physical_home / 'analysis/RESULTADO.json'
    command = [sys.executable, str(reader), '--home', str(restored),
               '--certificate', str(home / 'proofs/tau0160_permanent.json'),
               '--state-sha256', proof['state_sha256'],
               '--original-result', str(restored / 'preregistration/RESULTADO_CAUSAL_ORIGINAL.json'),
               '--physical-result', str(physical), '--physical-result-sha256', digest(physical),
               '--output', str(output / 'residual')]
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    process = subprocess.run(command, env=environment, text=True, capture_output=True)
    (output / 'reader_stdout.txt').write_text(process.stdout)
    (output / 'reader_stderr.txt').write_text(process.stderr)
    assert process.returncode == 0, 'Registered residual reader failed; retain administrative negative'
    result = read(output / 'residual/RESULTADO_RESIDUAL.json')
    assert result['M2_steps_executed'] == 0 and not result['CP12_closed']
    destination = home / 'analysis/residual_offline_registered'
    assert not destination.exists()
    destination.mkdir()
    for name in ('leer_residuo_mixto.py', 'despues_del_guardian.py', 'CONTINUACION_AUTOMATICA.md'):
        shutil.copyfile(Path(__file__).with_name(name), destination / name)
    shutil.copyfile(output / 'residual/RESULTADO_RESIDUAL.json', destination / 'RESULTADO_RESIDUAL.json')
    write(destination / 'PROCEDENCIA.json', dict(registration_commit=registration_commit,
          reader_sha256=READER_HASH, recovered_state_sha256=proof['state_sha256'],
          recovered_physical_result_sha256=digest(physical), all_recovered_payload_hashes_verified=True,
          M2_steps_executed=0, correction_validated=False, CP12_closed=False))
    spec = importlib.util.spec_from_file_location('captured_mixed_preserver_after_exit', home / 'coordinator.py')
    coordinator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(coordinator)
    coordinator.preserve_negative(home, 'LECTURA_RESIDUAL_TAU0160',
            'Registered offline residual reading after observed own guardian exit; no M2 steps',
            negative=not result['necessary_pair_and_mechanism_gates_passed'])
    write(output / 'status.json', dict(status='RESIDUAL_SAVED_RECOVERED_AND_VERIFIED',
          necessary_pair_and_mechanism_gates_passed=result['necessary_pair_and_mechanism_gates_passed'],
          additional_resolution_stability_robustness_pending=True, M2_steps_executed=0,
          correction_validated=False, CP12_closed=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--registration-commit', required=True)
    args = parser.parse_args()
    try:
        from seleccion_canonica import canonical_selection
        with canonical_selection(args.home.resolve()):
            run(args.home, args.output, args.registration_commit)
    except BaseException:
        if args.output.is_dir():
            write(args.output / 'administrative_failure.json', dict(
                  status='ADMINISTRATIVE_POSTPROCESS_FAILURE_NO_M2_RETRY', traceback=traceback.format_exc(),
                  M2_steps_executed=0, CP12_closed=False))
        raise
