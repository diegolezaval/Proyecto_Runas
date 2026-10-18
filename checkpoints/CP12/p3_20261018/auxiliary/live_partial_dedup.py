"""Lossless representation of stable redundant partials; never valid M2 states."""
from contextlib import contextmanager
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import json
import re
import time
import uuid
import zipfile
import clean_verified_copies_v2 as prior


def signature(p):
    s = p.stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def in_scope(home, p):
    relative = p.relative_to(home)
    if p.is_symlink() or not p.is_file():
        return False
    suffix = r'(?:\.[A-Za-z0-9_-]{5,64}){1,20}'
    if relative.parent == Path('transport'):
        return bool(re.fullmatch(r'\.current\.(?:npz|tmp)' + suffix, p.name))
    if relative.parent == Path('capsules'):
        return bool(re.fullmatch(r'\.CP12_CANDIDATO_P3_[a-f0-9]{32}_.+\.zip' + suffix, p.name))
    if relative.parts[:3] == ('runtime', 'tmp', 'library_upload_staging') and len(relative.parts) == 5:
        return bool(re.fullmatch(r'\.CP12_CANDIDATO_P3_[a-f0-9]{32}_.+\.zip' + suffix, p.name))
    return False


@contextmanager
def stream(source):
    if source.get('zip_entry'):
        with zipfile.ZipFile(source['path']) as z, z.open(source['zip_entry']) as f:
            yield f
    else:
        with Path(source['path']).open('rb') as f:
            yield f


def matches(p, source):
    n = p.stat().st_size
    if n > source['bytes']:
        return False
    with p.open('rb') as f, stream(source) as g:
        while chunk := f.read(1024 * 1024):
            if chunk != g.read(len(chunk)):
                return False
    return True


def clean(home, uid, run_id, dry_run=False, now=None):
    home = home.resolve()
    assert prior.read(home/'preregistration/ubicacion.json')['execution_uuid'] == uid
    assert prior.read(home/'preregistration/nueva_identidad.json')['execution_run_id'] == run_id
    now = time.time() if now is None else now
    observation_file = home/'runtime/p3_live_partial_observations.json'
    observations = prior.read(observation_file) if observation_file.exists() else {}
    updated = dict(observations)
    candidates = []
    for root in ('transport', 'capsules', 'runtime/tmp/library_upload_staging'):
        for p in (home/root).rglob('*'):
            if not in_scope(home, p):
                continue
            sig = signature(p)
            old = observations.get(str(p), {})
            first = old['first_unchanged_at'] if old.get('signature') == sig else now
            updated[str(p)] = dict(signature=sig, first_unchanged_at=first)
            if now-first >= 60 and now-max(sig[-2:])/1e9 >= 300:
                candidates.append((p, sig))
    sources = []
    for _, proof in prior.verified(home, uid).values():
        archive = home/'capsules'/proof['file_name']
        identity = dict(path=str(archive), bytes=archive.stat().st_size,
                        source_kind='PERMANENTLY_RECOVERED_CANONICAL_ARCHIVE',
                        archive_sha256=proof['zip_sha256'], library_file_id=proof['library_file_id'])
        sources.append(identity)
        with zipfile.ZipFile(archive) as z:
            for name in ('transport/current.npz', uid+'/transport/current.npz'):
                if name in z.namelist():
                    sources.append(dict(identity, zip_entry=name, bytes=z.getinfo(name).file_size))
    planned, anchors = [], []
    for p, sig in sorted(candidates, key=lambda pair: (-pair[1][2], str(pair[0]))):
        chosen = next((s for s in sources+anchors if matches(p, s)), None)
        assert signature(p) == sig, 'Changing partial: preserve and stop auxiliary'
        if chosen is None:
            anchors.append(dict(path=str(p), bytes=sig[2], source_kind='RETAINED_LOCAL_PARTIAL_NOT_SCIENTIFIC_STATE',
                                sha256=prior.sha(p), signature=sig))
            continue
        if chosen['source_kind'].startswith('RETAINED'):
            assert signature(Path(chosen['path'])) == chosen['signature']
            assert prior.sha(Path(chosen['path'])) == chosen['sha256']
        item = dict(path=str(p.relative_to(home)), bytes=sig[2], sha256=prior.sha(p),
                    signature=sig, source=chosen, exact_prefix_comparison=True,
                    reconstruction='First bytes bytes of source; follow SHA-linked receipts if a retained partial is later represented',
                    M2_steps_executed=0, CP12_closed=False)
        planned.append(item)
        if not dry_run:
            folder = home/'preregistration/live_partial_representations'
            folder.mkdir(exist_ok=True)
            receipt = folder/(uuid.uuid4().hex+'.json')
            item.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        schema='CP12_P3_LOSSLESS_REDUNDANT_PARTIAL_REPRESENTATION_BEFORE_REMOVAL')
            with receipt.open('x') as f:
                json.dump(item, f, indent=2)
            assert signature(p) == sig and prior.sha(p) == item['sha256']
            p.unlink()
    if not dry_run:
        temp = observation_file.with_suffix('.tmp')
        temp.write_text(json.dumps(updated)+'\n');temp.replace(observation_file)
    return dict(selected=planned, retained_anchors=anchors, dry_run=dry_run,
                unique_unknown_content_retained=True, M2_steps_executed=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--uid', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    lock = (args.home/'runtime/p3_live_partial_dedup.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    while True:
        print(json.dumps(clean(args.home, args.uid, args.run_id, args.dry_run)), flush=True)
        if args.once or args.dry_run or (args.home/'runtime/observed_guardian_exit.json').exists():
            break
        time.sleep(30)
