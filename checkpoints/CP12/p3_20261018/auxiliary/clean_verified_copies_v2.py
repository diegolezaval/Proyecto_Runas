"""Remove only verified disposable P3 duplicates; retain canonical archives."""
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import json
import re
import shutil
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def receipt(home, key, value):
    folder = home/'preregistration/copy_cleanup_receipts'
    folder.mkdir(exist_ok=True)
    path = folder/(key+'.json')
    assert not path.exists()
    value.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 scope='Disposable local duplicate only; canonical archive and Library untouched',
                 M2_steps_executed=0, scientific_files_changed=False)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.replace(path)


def verified(home, uid):
    choices = {}
    for path in (home/'proofs').glob('*_permanent.json'):
        p = read(path)
        audit = p.get('independent_zero_step_audit', p.get('independent_extracted_audit', {}))
        if not (p.get('passed') and p.get('all_payload_hashes_verified') and p.get('library_file_id')
                and audit.get('passed') and audit.get('M2_steps_executed') == 0
                and audit.get('tests') and all(audit['tests'].values())):
            continue
        if p.get('schema') not in ('CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER',
                                   'CP12_P3_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED'):
            continue
        name = p['file_name']
        assert Path(name).name == name and name.startswith('CP12_CANDIDATO_P3_'+uid+'_')
        archive = home/'capsules'/name
        assert archive.is_file() and not archive.is_symlink()
        assert archive.stat().st_size == p['zip_bytes'] and sha(archive) == p['zip_sha256']
        choices[name] = (path, p)
    return choices


def prefix_evidence(restored, relative, manifest, observed, updated, now):
    assert relative.parent == Path('transport')
    assert re.fullmatch(r'\.current\.npz(?:\.[A-Za-z0-9_-]{5,64}){1,3}',relative.name)
    path=restored/relative;source=restored/'transport/current.npz'
    expected=manifest['files']['transport/current.npz']
    def signature(p):
        st=p.stat();return [st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns]
    before=signature(path);digest=hashlib.sha256();count=0
    assert path.stat().st_size<=source.stat().st_size==expected['bytes']
    with path.open('rb') as a,source.open('rb') as b:
        while chunk:=a.read(1024*1024):
            assert chunk==b.read(len(chunk)), 'Unknown non-prefix content: preserve it'
            digest.update(chunk);count+=len(chunk)
    after=signature(path);assert before==after
    key=str(path);prior=observed.get(key,{})
    first=prior['first_unchanged_at'] if prior.get('signature')==after else now
    updated[key]={'signature':after,'first_unchanged_at':first}
    ready=now-first>=60 and now-max(after[-2:])/1e9>=300
    evidence={'path':relative.as_posix(),'bytes':count,'sha256':digest.hexdigest(),
              'source_payload':'transport/current.npz','source_payload_sha256':expected['sha256'],
              'source_payload_bytes':expected['bytes'],'exact_prefix_comparison':True,
              'reconstruction':'Read the first bytes bytes of source_payload in the retained canonical archive',
              'stable_seconds':now-first}
    return evidence,ready


def clean(home, expected_uid, expected_run, dry_run=False, now=None):
    home = home.resolve()
    assert read(home/'preregistration/ubicacion.json')['execution_uuid'] == expected_uid
    assert read(home/'preregistration/nueva_identidad.json')['execution_run_id'] == expected_run
    now=time.time() if now is None else now
    observation_file=home/'runtime/p3_prefix_copy_observations.json'
    observed=read(observation_file) if observation_file.exists() else {}
    updated=dict(observed)
    proofs = verified(home, expected_uid)
    planned = []
    markers = home/'preregistration/copy_cleanup_receipts'
    for path in (home/'preregistration/upload_staging').glob('*.json'):
        assert re.fullmatch('[a-f0-9]{32}', path.stem)
        if (markers/('STAGING_'+path.stem+'.json')).exists():
            continue
        record = read(path)
        canonical = Path(record['canonical_archive_relative'])
        assert canonical.parent == Path('capsules')
        if canonical.name not in proofs or not record.get('canonical_source_unchanged_after_helper'):
            continue
        relative = Path(record['staging_relative'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert relative.parts[:3] == ('runtime', 'tmp', 'library_upload_staging')
        assert len(relative.parts) == 5 and relative.parts[3] == path.stem
        assert relative.name == canonical.name
        staging = home/relative
        if not staging.exists():
            continue
        assert not staging.is_symlink() and staging.resolve().is_relative_to(home/'runtime/tmp/library_upload_staging')
        _, proof = proofs[canonical.name]
        assert staging.stat().st_size == record['bytes'] == proof['zip_bytes']
        assert sha(staging) == record['sha256'] == proof['zip_sha256']
        item = dict(kind='STAGING', path=str(relative), bytes=record['bytes'],
                    archive_sha256=proof['zip_sha256'], library_file_id=proof['library_file_id'],
                    canonical_archive_kept=True)
        planned.append(item)
        if not dry_run:
            staging.unlink()
            receipt(home, 'STAGING_'+path.stem, item)
    transports = [(p['observer_clock'], path, p) for path, p in proofs.values()
                  if p.get('schema') == 'CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER']
    for clock, path, p in sorted(transports, key=lambda x: x[0])[:-2]:
        label = path.stem.removesuffix('_permanent')
        assert re.fullmatch('TRANSPORTE_TAU_[0-9]{6}', label)
        if (markers/(label+'.json')).exists():
            continue
        folders = [home/'recoveries'/label, home/'recoveries'/(label+'_runtime_checked')]
        for folder in folders:
            assert folder.parent == home/'recoveries' and not folder.is_symlink()
            if folder.exists():
                assert folder.resolve().is_relative_to(home/'recoveries')
                for archive in folder.rglob('*.zip'):
                    assert not archive.is_symlink() and archive.name == p['file_name']
                    assert archive.stat().st_size == p['zip_bytes'] and sha(archive) == p['zip_sha256']
        restored = folders[1];prefixes=[];pending_prefix=False
        if restored.exists():
            manifest = read(restored/'MANIFIESTO_NEGATIVO.json')
            allowed = set(manifest['files']) | {'MANIFIESTO_NEGATIVO.json'}
            for name, expected in manifest['files'].items():
                source = restored/name
                assert not source.is_symlink() and source.is_file()
                assert source.stat().st_size == expected['bytes'] and sha(source) == expected['sha256']
            for source in restored.rglob('*'):
                assert not source.is_symlink()
                if not source.is_file() or source.relative_to(restored).as_posix() in allowed:
                    continue
                relative = source.relative_to(restored)
                if source.suffix in ('.pyc','.so') and any(x in ('cache','__pycache__','runtime') for x in relative.parts):
                    continue
                evidence,ready=prefix_evidence(restored,relative,manifest,observed,updated,now)
                prefixes.append(evidence);pending_prefix=pending_prefix or not ready
        if pending_prefix:
            continue
        item = dict(kind='OLDER_TRANSPORT_DUPLICATES', observer_clock=clock,
                    paths=[str(f.relative_to(home)) for f in folders],
                    archive_sha256=p['zip_sha256'], library_file_id=p['library_file_id'],
                    canonical_archive_kept=True, two_latest_transport_copies_retained=True,
                    all_frontier_copies_retained=True)
        planned.append(item)
        if not dry_run:
            if prefixes:
                key=label+'_LOSSLESS_PREFIX_REPRESENTATIONS'
                if not (markers/(key+'.json')).exists():
                    receipt(home,key,dict(kind='LOSSLESS_PREFIX_REPRESENTATIONS_BEFORE_DUPLICATE_REMOVAL',
                        observer_clock=clock,prefixes=prefixes,canonical_archive_kept=True,
                        archive_sha256=p['zip_sha256'],library_file_id=p['library_file_id']))
            # In the download root, unlink only the known verified ZIP; keep unknown files.
            if folders[0].exists():
                for archive in folders[0].rglob('*.zip'):
                    archive.unlink()
            if restored.exists():
                shutil.rmtree(restored)
            receipt(home, label, item)
    if not dry_run:
        temporary=observation_file.with_suffix('.tmp')
        temporary.write_text(json.dumps(updated)+'\n');temporary.replace(observation_file)
    return dict(selected=planned,dry_run=dry_run,M2_steps_executed=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--uid', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    lock = (args.home/'runtime/p3_verified_copy_cleanup.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    while True:
        print(json.dumps(clean(args.home, args.uid, args.run_id, args.dry_run)), flush=True)
        if args.once or args.dry_run or (args.home/'runtime/observed_guardian_exit.json').exists():
            break
        time.sleep(30)
