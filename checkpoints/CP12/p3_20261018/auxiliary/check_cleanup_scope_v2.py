"""Synthetic ownership/retention controls; no scientific state or service calls."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import tempfile
import time
import os
import zipfile


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    source = Path(__file__).with_name('clean_verified_copies_v2.py')
    spec = importlib.util.spec_from_file_location('P3_copy_cleanup_scope', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    uid, run_id = '1'*32, '2'*64
    tests = {}
    with tempfile.TemporaryDirectory() as temp:
        home = Path(temp)
        put(home/'preregistration/ubicacion.json', dict(execution_uuid=uid))
        put(home/'preregistration/nueva_identidad.json', dict(execution_run_id=run_id))
        (home/'outputs').mkdir()
        (home/'outputs/scientific_state.npz').write_bytes(b'SCIENTIFIC_UNTOUCHED')
        original = module.sha(home/'outputs/scientific_state.npz')
        archives = []
        for clock in (1.6, 3.2, 4.8):
            label = 'TRANSPORTE_TAU_%06d' % round(clock*10)
            name = 'CP12_CANDIDATO_P3_'+uid+'_'+label+'.zip'
            archive = home/'capsules'/name
            archive.parent.mkdir(exist_ok=True)
            payload = b'known_duplicate_payload'
            manifest = dict(files={'transport/current.npz':dict(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())})
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('transport/current.npz', payload)
                z.writestr('MANIFIESTO_NEGATIVO.json', json.dumps(manifest))
            digest = module.sha(archive)
            proof = dict(schema='CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER',
                observer_clock=clock, passed=True, all_payload_hashes_verified=True, library_file_id='synthetic_no_service',
                independent_zero_step_audit=dict(passed=True, M2_steps_executed=0, tests={'synthetic':True}),
                file_name=name, zip_bytes=archive.stat().st_size, zip_sha256=digest)
            put(home/'proofs'/(label+'_permanent.json'), proof)
            download = home/'recoveries'/label/'download'/name
            download.parent.mkdir(parents=True)
            download.write_bytes(archive.read_bytes())
            restored = home/'recoveries'/(label+'_runtime_checked')
            with zipfile.ZipFile(archive) as z:
                z.extractall(restored)
            archives.append((archive, digest, restored))
        key = 'a'*32
        staging = home/'runtime/tmp/library_upload_staging'/key/archives[-1][0].name
        staging.parent.mkdir(parents=True)
        staging.write_bytes(archives[-1][0].read_bytes())
        record = dict(canonical_archive_relative='capsules/'+staging.name,
            staging_relative=staging.relative_to(home).as_posix(),
            canonical_source_unchanged_after_helper=True, bytes=staging.stat().st_size, sha256=module.sha(staging))
        put(home/'preregistration/upload_staging'/(key+'.json'), record)
        fixed=time.time()+601  # Simulate age of both mtime and ctime; no real sleeping.
        prefix=archives[0][2]/'transport/.current.npz.aaaaaa'
        prefix.write_bytes(b'known_d');os.utime(prefix,(fixed-600,fixed-600))
        planned=module.clean(home,uid,run_id,True,now=fixed)
        tests['dry_run_mutates_no_files'] = staging.exists() and all(d.exists() for _,_,d in archives)
        module.clean(home,uid,run_id,now=fixed)
        tests['unsettled_prefix_retained']=prefix.exists()
        module.clean(home,uid,run_id,now=fixed+61)
        evidence=json.loads((home/'preregistration/copy_cleanup_receipts/TRANSPORTE_TAU_000016_LOSSLESS_PREFIX_REPRESENTATIONS.json').read_text())['prefixes'][0]
        with zipfile.ZipFile(archives[0][0]) as z:
            reconstructed=z.read(evidence['source_payload'])[:evidence['bytes']]
        tests['prefix_reconstruction_hash_exact']=hashlib.sha256(reconstructed).hexdigest()==evidence['sha256']
        tests['only_verified_staging_removed'] = not staging.exists()
        tests['two_latest_transport_duplicates_retained'] = not archives[0][2].exists() and all(d.exists() for _,_,d in archives[1:])
        tests['all_canonical_archives_retained_exact'] = all(p.exists() and module.sha(p)==digest for p,digest,_ in archives)
        badkey = 'b'*32
        bad = dict(record, staging_relative='outputs/scientific_state.npz')
        put(home/'preregistration/upload_staging'/(badkey+'.json'), bad)
        rejected = False
        try:
            module.clean(home, uid, run_id)
        except AssertionError:
            rejected = True
        tests['scientific_path_rejected_before_deletion'] = rejected and module.sha(home/'outputs/scientific_state.npz') == original
        tests['receipts_written_for_real_cleanup_only'] = len(list((home/'preregistration/copy_cleanup_receipts').glob('*.json')))==3
    result = dict(schema='CP12_P3_AUXILIARY_V2_LOSSLESS_PREFIX_CONTROLS', tests=tests, passed=all(tests.values()),
                  M2_steps_executed=0, Library_calls=0, scientific_gates_changed=False,
                  source_sha256=module.sha(source), CP12_closed=False)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
