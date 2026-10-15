"""Keep bounded scratch duplicates only after complete permanent recovery audits.

No Library deletion, no scientific-source or output mutation, no solver access.
The complete permanent archives and all local proof/history files are retained.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def clean(home):
    uid = json.loads((home / 'preregistration/ubicacion.json').read_text())['execution_uuid']
    groups = {'transport': [], 'frontier': []}
    for path in (home / 'proofs').glob('*_permanent.json'):
        proof = json.loads(path.read_text())
        if not proof.get('passed') or not proof.get('all_payload_hashes_verified') or not proof.get('library_file_id'):
            continue
        if proof.get('schema') == 'CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER':
            if not proof.get('independent_zero_step_audit', {}).get('passed'):
                continue
            groups['transport'].append((proof['observer_clock'], path, proof))
        elif proof.get('schema') == 'CP12_MIXTO_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED' and proof.get('time', 0) > 0:
            if not proof.get('independent_extracted_audit', {}).get('passed'):
                continue
            groups['frontier'].append((proof['time'], path, proof))
    for group, values in groups.items():
        for clock, proof_path, proof in sorted(values, key=lambda item: item[0])[:-2]:
            marker = home / 'runtime' / ('temporary_copies_removed_' + proof_path.name)
            if marker.exists():
                continue
            name = proof['file_name']
            assert Path(name).name == name
            if not name.startswith('CP12_CANDIDATO_MIXTO_' + uid + '_'):
                continue
            capsule = home / 'capsules' / name
            label = proof_path.stem.removesuffix('_permanent')
            if group == 'transport':
                assert label.startswith('TRANSPORTE_TAU_')
                folders = [home / 'recoveries' / label, home / 'recoveries' / (label + '_runtime_checked')]
            else:
                base = 'CP12_CANDIDATO_MIXTO_' + uid + '_tau%04d' % int(clock)
                folders = [home / 'recoveries' / (base + '_download'), home / 'recoveries' / (base + '_checked')]
            # Only task-created duplicate roots. Unknown files and negatives are never selected.
            if capsule.exists():
                assert capsule.stat().st_size == proof['zip_bytes'] and sha(capsule) == proof['zip_sha256']
            for folder in folders:
                assert folder.parent == home / 'recoveries' and not folder.is_symlink()
                if folder.exists():
                    for archive in folder.rglob('*.zip'):
                        assert archive.name == name and archive.stat().st_size == proof['zip_bytes']
                        assert sha(archive) == proof['zip_sha256']
            for folder in folders:
                if folder.exists():
                    shutil.rmtree(folder)
            if capsule.exists():
                capsule.unlink()
            marker.write_text(json.dumps(dict(scope='Verified redundant scratch copies only',
                permanent_library_file_id=proof['library_file_id'], archive_sha256=proof['zip_sha256'],
                permanent_archive_and_proof_retained=True, clock=clock)) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    args = parser.parse_args()
    home = args.home.resolve()
    while True:
        clean(home)
        if (home / 'runtime/observed_guardian_exit.json').exists():
            break
        time.sleep(30)
