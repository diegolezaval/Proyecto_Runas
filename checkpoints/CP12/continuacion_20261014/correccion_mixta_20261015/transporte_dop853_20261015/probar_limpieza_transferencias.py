"""Synthetic filesystem checks only; no M2, Library calls or actual certificates."""
from pathlib import Path
import hashlib
import json
import os
import tempfile
import time
import zipfile
import limpiar_transferencias as cleaner


def run():
    checks = {}
    with tempfile.TemporaryDirectory() as temporary:
        home = Path(temporary)
        for name in ('transport', 'runtime', 'capsules', 'proofs', 'preregistration', 'negative'):
            (home / name).mkdir()
        base = time.time()
        invalid = b'PK\x03\x04INCOMPLETE_SYNTHETIC'
        canonical = home / 'transport/current.npz'
        canonical.write_bytes(invalid)
        negative = home / 'negative/failed.npz'
        negative.write_bytes(invalid)
        unknown = home / 'transport/user_notes.txt'
        unknown.write_bytes(b'KEEP')
        valid = home / 'transport/.current.npz.validxx'
        with zipfile.ZipFile(valid, 'w') as zipped:
            zipped.writestr('synthetic.npy', b'NO_M2_DATA')
        checks['no_cleanup_without_permanent_certificate'] = cleaner.tick(home, base + 600)['quarantined'] == 0
        old = []
        for index in range(6):
            path = home / 'transport' / ('.current.npz.old%05d' % index)
            path.write_bytes(invalid)
            old.append(path)
        wrong_header = home / 'transport/.current.npz.otherxx'
        wrong_header.write_bytes(b'KEEP_UNRECOGNIZED_CONTENT')
        symlink = home / 'transport/.current.npz.symlinkx'
        symlink.symlink_to(negative)
        fresh = []
        for index in range(3):
            path = home / 'transport' / ('.current.npz.fresh%05d' % index)
            path.write_bytes(invalid)
            os.utime(path, (base + 500 + index * 100, base + 500 + index * 100))
            fresh.append(path)
        archive = home / 'capsules/synthetic.zip'
        with zipfile.ZipFile(archive, 'w') as zipped:
            zipped.writestr('fixture.txt', b'SYNTHETIC_NOT_A_SCIENTIFIC_BACKUP')
        archive_bytes = archive.read_bytes()
        os.utime(archive, (base + 100, base + 100))
        proof = dict(schema='CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER',
            passed=True, all_payload_hashes_verified=True,
            library_file_id='SYNTHETIC_TEST_FIXTURE_NOT_A_LIBRARY_OBJECT',
            file_name=archive.name, zip_bytes=archive.stat().st_size,
            zip_sha256=hashlib.sha256(archive_bytes).hexdigest(), observer_clock=1.6,
            independent_zero_step_audit=dict(passed=True, M2_steps_executed=0, tests={'synthetic_fixture_only': True}))
        proof_path = home / 'proofs/synthetic_permanent.json'
        proof_path.write_text(json.dumps(proof))
        checks['first_observation_does_not_move_files'] = cleaner.tick(home, base + 600)['quarantined'] == 0
        result = cleaner.tick(home, base + 661)
        checks['only_six_old_malformed_copies_quarantined'] = result['quarantined'] == 6 * len(invalid) and all(not p.exists() for p in old)
        checks['valid_zip_is_preserved'] = valid.exists() and zipfile.is_zipfile(valid)
        checks['recent_copies_are_preserved'] = all(p.read_bytes() == invalid for p in fresh)
        checks['canonical_state_is_untouched'] = canonical.read_bytes() == invalid
        checks['negative_is_untouched'] = negative.read_bytes() == invalid
        checks['unrelated_and_unrecognized_files_are_untouched'] = unknown.read_bytes() == b'KEEP' and wrong_header.exists()
        checks['symlink_and_target_are_untouched'] = symlink.is_symlink() and negative.read_bytes() == invalid
        checks['same_checkpoint_does_not_authorize_release'] = cleaner.tick(home, base + 750)['released'] == 0
        proof['observer_clock'] = 3.2
        proof_path.write_text(json.dumps(proof))
        checks['later_verified_checkpoint_authorizes_release'] = cleaner.tick(home, base + 800)['released'] == 6 * len(invalid)
        records = [json.loads(p.read_text()) for p in (home / 'preregistration/limpieza_transferencias').glob('*.json')]
        entries = [entry for record in records for entry in record['entries']]
        checks['all_removed_hashes_and_authorizations_retained'] = len(entries) == 6 and all(
            e['sha256'] == hashlib.sha256(invalid).hexdigest()
            and e['release_authorization']['clock'] == 3.2
            and e['status'] == 'RELEASED_AFTER_LATER_RECOVERED_CHECKPOINT' for e in entries)
        archive.write_bytes(b'CORRUPTED_SYNTHETIC_ARCHIVE')
        try:
            cleaner.tick(home, base + 900)
        except AssertionError:
            checks['corrupt_archive_blocks_cleanup'] = True
        else:
            checks['corrupt_archive_blocks_cleanup'] = False
    assert all(checks.values()), checks
    return dict(schema='CP12_SYNTHETIC_TRANSFER_CLEANUP_CONTROLS', passed=True, tests=checks,
                synthetic_files_only=True, M2_steps_executed=0, Library_calls=0,
                scientific_gates_changed=False, CP12_closed=False)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
