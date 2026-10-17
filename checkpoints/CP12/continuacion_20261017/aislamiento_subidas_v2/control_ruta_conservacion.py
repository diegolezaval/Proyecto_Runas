"""Exercise the full current Library path on preserved administrative evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from aislar_fuentes_subida import isolate_helper, sha


def run(home, evidence, helpers):
    home, evidence, helpers = home.resolve(), evidence.resolve(), helpers.resolve()
    assert not home.exists()
    (home / 'capsules').mkdir(parents=True)
    (home / 'runtime/tmp').mkdir(parents=True)
    selected = sorted(p for p in evidence.iterdir() if p.is_file())
    manifest = dict(schema='CP12_ADMINISTRATIVE_INTEGRITY_INCIDENT_NO_NEW_M2',
        files={p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in selected})
    canonical = home / 'capsules/CP12_INCIDENTE_INTEGRIDAD_TAU49p6_20261017.zip'
    with zipfile.ZipFile(canonical, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
        for path in selected:
            zipped.write(path, path.name)
        zipped.writestr('MANIFIESTO.json', json.dumps(manifest, indent=2) + '\n')
    size, expected = canonical.stat().st_size, sha(canonical)
    def helper(home_arg, name, arguments, data=None):
        process = subprocess.run([sys.executable, str(helpers / name), *arguments],
            input=json.dumps(data) if data is not None else None, text=True, capture_output=True)
        assert process.returncode == 0, process.stderr
        return process.stdout
    raw = isolate_helper(helper, home)(home, 'library_upload.py', [], {'uploads': [dict(
        local_path=str(canonical), purpose='create_library_file', library_artifact_type='other')]})
    (home / 'runtime/upload_result.txt').write_text(raw)
    marker = raw.rfind('\n{"results"')
    result = json.loads(raw[marker:].strip() if marker >= 0 else raw)['results']
    assert len(result) == 1 and result[0]['status'] == 'succeeded'
    item = result[0]
    sys.path.insert(0, str(helpers))
    from library_hosted_apps import HostedAppsClient
    response = HostedAppsClient().call_tool('connector_openai_library', 'prepare_materialize', dict(
        items=[dict(file_id=item['file_id'], library_file_id=item['library_file_id'], file_name=item['file_name'])],
        destination=dict(directory=str(home / 'recovery'))))
    assert not response.get('isError')
    transfer = response.get('structuredContent')
    if transfer is None:
        transfer = json.loads(next(x['text'] for x in response['content'] if x.get('type') == 'text'))
    transfer = transfer.get('result', transfer)
    assert len(transfer['transfers']) == 1 and not transfer.get('unavailable_items')
    transfer = transfer['transfers'][0]
    if transfer.get('workspace_path'):
        retrieved = Path(transfer['workspace_path'])
        helper(home, 'library_file_transfer.py', ['apply-xattrs', str(retrieved), transfer['library_file_id']],
               transfer.get('xattrs', []))
    else:
        retrieved = home / 'recovery' / item['file_name']
        helper(home, 'library_file_transfer.py', ['materialize', str(retrieved)], transfer)
    assert canonical.stat().st_size == retrieved.stat().st_size == size
    assert sha(canonical) == sha(retrieved) == expected
    with zipfile.ZipFile(retrieved) as zipped:
        assert zipped.testzip() is None
        assert set(zipped.namelist()) == set(manifest['files']) | {'MANIFIESTO.json'}
        assert json.loads(zipped.read('MANIFIESTO.json')) == manifest
        for name, entry in manifest['files'].items():
            data = zipped.read(name)
            assert len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256']
    proof = dict(schema='CP12_FULL_ADMINISTRATIVE_UPLOAD_COPY_ROUTE_RECOVERED_ZERO_M2',
        passed=True, zip_bytes=size, zip_sha256=expected, payload_files=len(manifest['files']),
        all_payload_hashes_verified=True, canonical_source_unchanged_after_upload_and_recovery=True,
        local_source_not_mapped_to_library=True, expected_retrieved_corrupt_source_sha256=
        manifest['files']['archivo_local_alterado_tau49p6.bin']['sha256'],
        library_file_id=item['library_file_id'], file_id=item['file_id'], file_name=item['file_name'],
        M2_steps_executed=0, scientific_gates_changed=False, CP12_closed=False)
    (home / 'PROOF.json').write_text(json.dumps(proof, indent=2) + '\n')
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('home', 'evidence', 'helpers'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.home, args.evidence, args.helpers)))
