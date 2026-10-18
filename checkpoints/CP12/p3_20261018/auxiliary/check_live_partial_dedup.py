"""Synthetic protection and exact reconstruction; no Library or M2."""
from pathlib import Path
import argparse
import hashlib
import json
import tempfile
import time
import zipfile
import live_partial_dedup as m


def put(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    tests = {}
    uid, run = '1'*32, '2'*64
    with tempfile.TemporaryDirectory() as temp:
        h = Path(temp)
        put(h/'preregistration/ubicacion.json', dict(execution_uuid=uid))
        put(h/'preregistration/nueva_identidad.json', dict(execution_run_id=run))
        (h/'runtime').mkdir();(h/'transport').mkdir();(h/'capsules').mkdir()
        name = 'CP12_CANDIDATO_P3_'+uid+'_TRANSPORTE_TAU_000016.zip'
        archive = h/'capsules'/name
        payload = b'CANONICAL_PAYLOAD_1234567'
        with zipfile.ZipFile(archive, 'w') as z:
            z.writestr('transport/current.npz', payload)
        original_archive = m.prior.sha(archive)
        put(h/'proofs/TRANSPORTE_TAU_000016_permanent.json',
            dict(schema='CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER',
                 passed=True, all_payload_hashes_verified=True, library_file_id='synthetic_no_service',
                 independent_zero_step_audit=dict(passed=True, M2_steps_executed=0, tests={'synthetic':True}),
                 file_name=name, zip_bytes=archive.stat().st_size, zip_sha256=original_archive))
        canonical = h/'transport/.current.npz.aaaaaa';canonical.write_bytes(payload[:10])
        anchor = h/'transport/.current.npz.bbbbbb';anchor.write_bytes(b'UNIQUE_UNKNOWN_LOCAL_PARTIAL')
        short = h/'transport/.current.npz.bbbbbb.cccccc';short.write_bytes(b'UNIQUE_UNKNOWN')
        protected = [h/'transport/current.npz', h/'transport/current.tmp',
                     h/'transport/other.npz', h/'negative/.current.npz.dddddd']
        for p in protected:
            p.parent.mkdir(exist_ok=True);p.write_bytes(b'PROTECTED')
        symlink = h/'transport/.current.npz.eeeeee';symlink.symlink_to(protected[0])
        fixed = time.time()+601
        before = {p.relative_to(h).as_posix():m.prior.sha(p) for p in h.rglob('*') if p.is_file()}
        m.clean(h, uid, run, True, now=fixed)
        after = {p.relative_to(h).as_posix():m.prior.sha(p) for p in h.rglob('*') if p.is_file()}
        tests['dry_run_has_no_mutation'] = before == after
        m.clean(h, uid, run, now=fixed)
        tests['new_observation_retains_partials'] = canonical.exists() and short.exists()
        m.clean(h, uid, run, now=fixed+61)
        tests['only_redundant_partials_removed'] = not canonical.exists() and not short.exists()
        tests['unique_unknown_anchor_retained'] = anchor.read_bytes() == b'UNIQUE_UNKNOWN_LOCAL_PARTIAL'
        tests['all_canonical_and_protected_paths_retained'] = all(p.read_bytes()==b'PROTECTED' for p in protected) and m.prior.sha(archive)==original_archive
        tests['symlink_preserved'] = symlink.is_symlink()
        receipts = [json.loads(p.read_text()) for p in (h/'preregistration/live_partial_representations').glob('*.json')]
        for receipt in receipts:
            with m.stream(receipt['source']) as f:
                reconstructed = f.read(receipt['bytes'])
            assert hashlib.sha256(reconstructed).hexdigest() == receipt['sha256']
        tests['all_removed_bytes_reconstruct_exactly'] = len(receipts)==2
        tests['both_canonical_and_local_reference_cases'] = {r['source']['source_kind'] for r in receipts}=={'PERMANENTLY_RECOVERED_CANONICAL_ARCHIVE','RETAINED_LOCAL_PARTIAL_NOT_SCIENTIFIC_STATE'}
    result = dict(schema='CP12_P3_LIVE_PARTIAL_DEDUP_SCOPE_AND_RECOVERY_CONTROLS',
                  tests=tests, passed=all(tests.values()), source_sha256=m.prior.sha(Path(m.__file__)),
                  M2_steps_executed=0, Library_calls=0, scientific_kernels_changed=False, CP12_closed=False)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
