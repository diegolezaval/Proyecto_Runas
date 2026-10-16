"""Quarantine only old malformed transfer copies; never select scientific files."""
from pathlib import Path
import argparse
import fcntl
import hashlib
import json
import os
import re
import stat
import time
import uuid
import zipfile

PATTERN = re.compile(r'\.current\.npz\.[A-Za-z0-9_-]{5,64}')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def signature(path):
    value = path.lstat()
    assert stat.S_ISREG(value.st_mode) and not path.is_symlink()
    return [value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns]


def certificate(home):
    choices = []
    for path in (home / 'proofs').glob('*_permanent.json'):
        proof = json.loads(path.read_text())
        if proof.get('schema') == 'CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER':
            audit, clock = proof.get('independent_zero_step_audit', {}), proof['observer_clock']
        elif proof.get('schema') == 'CP12_MIXTO_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED':
            audit, clock = proof.get('independent_extracted_audit', {}), proof['time']
        else:
            continue
        if not (proof.get('passed') and proof.get('all_payload_hashes_verified') and proof.get('library_file_id')
                and audit.get('passed') and audit.get('M2_steps_executed') == 0
                and audit.get('tests') and all(audit['tests'].values())):
            continue
        choices.append((clock, path, proof))
    if not choices:
        return None
    clock, path, proof = max(choices, key=lambda item: item[0])
    name = proof['file_name']
    assert Path(name).name == name
    archive = home / 'capsules' / name
    if not archive.is_file():
        return None
    assert archive.stat().st_size == proof['zip_bytes'] and sha(archive) == proof['zip_sha256']
    return dict(clock=clock, archive_sha256=proof['zip_sha256'],
                certificate_sha256=sha(path), archive_mtime=archive.stat().st_mtime)


def malformed(path):
    with path.open('rb') as stream:
        return stream.read(4) == b'PK\x03\x04' and not zipfile.is_zipfile(path)


def tick(home, now=None):
    now = time.time() if now is None else now
    assert home.is_dir() and not (home / 'transport').is_symlink()
    proof = certificate(home)
    if proof is None:
        return dict(quarantined=0, released=0, reason='No complete local permanent certificate')
    records = home / 'preregistration/limpieza_transferencias'
    quarantine = home / 'runtime/transfer_cleanup_quarantine'
    records.mkdir(exist_ok=True)
    quarantine.mkdir(parents=True, exist_ok=True)
    released = 0
    for path in records.glob('*.json'):
        record = json.loads(path.read_text())
        if proof['clock'] <= record['after_recovered_clock'] or now - record['at_seconds'] < 60:
            continue
        for entry in record['entries']:
            if entry['status'] != 'QUARANTINED':
                continue
            parked = quarantine / entry['quarantine_name']
            assert parked.parent == quarantine and parked.is_file()
            assert sha(parked) == entry['sha256'] and malformed(parked)
            entry['release_authorization'] = proof
            write(path, record)
            parked.unlink()
            entry['status'] = 'RELEASED_AFTER_LATER_RECOVERED_CHECKPOINT'
            write(path, record)
            released += entry['bytes']
    observed_path = home / 'runtime/transfer_cleanup_observations.json'
    observed = json.loads(observed_path.read_text()) if observed_path.exists() else {}
    current = {}
    candidates = []
    for path in (home / 'transport').iterdir():
        if not PATTERN.fullmatch(path.name) or path.is_symlink() or not path.is_file():
            continue
        saved = signature(path)
        current[path.name] = dict(signature=saved, first_unchanged_at=now)
        old = observed.get(path.name)
        if old and old['signature'] == saved:
            current[path.name]['first_unchanged_at'] = old['first_unchanged_at']
        candidates.append((max(saved[-2:]) / 1e9, path, saved))
    selected = []
    cutoff = min(now - 300, proof['archive_mtime'] - 60)
    for modified, path, saved in sorted(candidates, key=lambda item: item[0])[:-2]:
        if modified >= cutoff or now - current[path.name]['first_unchanged_at'] < 60 or not malformed(path):
            continue
        digest = sha(path)
        if signature(path) != saved:
            continue
        selected.append(dict(source_name=path.name, quarantine_name=uuid.uuid4().hex,
                             bytes=saved[2], sha256=digest, status='PLANNED'))
    if selected:
        record = dict(schema='CP12_UNUSED_MALFORMED_TRANSFER_COPY_QUARANTINE', at_seconds=now,
            after_recovered_clock=proof['clock'], authorization=proof, entries=selected,
            scope='Only old invalid ZIP transfer copies; no canonical file, negative or valid NPZ selected',
            M2_steps_executed=0, CP12_closed=False)
        manifest = records / (uuid.uuid4().hex + '.json')
        write(manifest, record)
        for entry in selected:
            source, parked = home / 'transport' / entry['source_name'], quarantine / entry['quarantine_name']
            assert PATTERN.fullmatch(source.name) and source.parent == home / 'transport'
            assert not source.is_symlink() and sha(source) == entry['sha256'] and malformed(source)
            source.rename(parked)
            assert sha(parked) == entry['sha256'] and malformed(parked)
            entry['status'] = 'QUARANTINED'
            write(manifest, record)
    write(observed_path, current)
    return dict(quarantined=sum(e['bytes'] for e in selected), released=released, checkpoint=proof['clock'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    args = parser.parse_args()
    lock = (args.home / 'runtime/transfer_cleanup.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    while not (args.home / 'runtime/observed_guardian_exit.json').exists():
        print(json.dumps(tick(args.home.resolve())), flush=True)
        time.sleep(30)
