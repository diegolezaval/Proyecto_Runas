"""Byte-only subdivision of an existing V2 archive; no numerical imports."""
from pathlib import Path
import argparse
import hashlib
import json
import os

SIZE = 750000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def oid(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def prepare(source, destination):
    source, destination = Path(source), Path(destination)
    assert not destination.exists()
    m = json.loads((source / 'MANIFIESTO.json').read_text())
    assert m['schema'] == 'CP12_WHOLE_ARCHIVE_LOSSLESS_GIT_PARTS_V2'
    (destination / 'parts').mkdir(parents=True)
    rows, total, whole = [], 0, hashlib.sha256()
    for i, parent in enumerate(m['parts']):
        assert parent['path'] == f'parts/part_{i:06d}.bin'
        p = source / parent['path']
        assert p.is_file() and not p.is_symlink()
        data = p.read_bytes()
        assert len(data) == parent['bytes'] and digest(data) == parent['sha256']
        assert oid(data) == parent['git_blob_sha1']
        whole.update(data)
        for offset in range(0, len(data), SIZE):
            chunk = data[offset:offset + SIZE]
            path = f'parts/part_{len(rows):06d}.bin'
            with (destination / path).open('xb') as f:
                f.write(chunk)
            rows.append(dict(path=path, bytes=len(chunk), sha256=digest(chunk),
                             git_blob_sha1=oid(chunk), parent_part=i,
                             parent_offset=offset, archive_offset=total))
            total += len(chunk)
    assert total == m['bytes'] and whole.hexdigest() == m['sha256']
    result = dict(schema='CP12_EXACT_ARCHIVE_SMALL_PARTS_V3',
                  file_name=m['file_name'], bytes=total, sha256=m['sha256'],
                  chunk_bytes=SIZE, parts=rows,
                  source_v2_manifest_sha256=digest((source/'MANIFIESTO.json').read_bytes()),
                  scientific_payload_modified=False, M2_steps_executed=0,
                  remote_preservation_proven=False, CP12_closed=False)
    (destination/'MANIFIESTO.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def restore(source, destination):
    source, destination = Path(source), Path(destination)
    assert not destination.exists()
    m = json.loads((source/'MANIFIESTO.json').read_text())
    assert m['schema'] == 'CP12_EXACT_ARCHIVE_SMALL_PARTS_V3'
    assert m['chunk_bytes'] == SIZE and m['parts']
    whole, total = hashlib.sha256(), 0
    with destination.open('xb') as out:
        for i, row in enumerate(m['parts']):
            assert row['path'] == f'parts/part_{i:06d}.bin'
            assert row['archive_offset'] == total
            p = source / row['path']
            assert p.is_file() and not p.is_symlink()
            data = p.read_bytes()
            assert len(data) == row['bytes'] and digest(data) == row['sha256']
            assert oid(data) == row['git_blob_sha1']
            assert 0 < len(data) <= SIZE
            whole.update(data)
            total += len(data)
            out.write(data)
        out.flush()
        os.fsync(out.fileno())
    assert total == m['bytes'] and whole.hexdigest() == m['sha256']
    return dict(passed=True, bytes=total, sha256=whole.hexdigest(),
                part_count=len(m['parts']), M2_steps_executed=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['prepare', 'restore'])
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    result = globals()[args.operation](args.source, args.destination)
    print(json.dumps({k:v for k,v in result.items() if k != 'parts'}))
