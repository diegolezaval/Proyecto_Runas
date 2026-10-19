"""Lossless immutable Git storage for whole CP12 archives; no numerical imports."""
from pathlib import Path
import argparse,hashlib,json,os

CHUNK_BYTES=760000

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def oid(data):
    return hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()

def prepare(source,destination,context=None):
    source=Path(source).resolve();destination=Path(destination).resolve()
    assert source.is_file() and not source.is_symlink()
    assert not destination.exists()
    digest=sha(source);size=source.stat().st_size
    (destination/'parts').mkdir(parents=True)
    records=[]
    with source.open('rb') as f:
        i=0
        while data:=f.read(CHUNK_BYTES):
            name=f'parts/part_{i:06d}.bin'
            with (destination/name).open('xb') as g:g.write(data)
            records.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=oid(data)))
            i+=1
    assert sha(source)==digest and source.stat().st_size==size
    manifest=dict(schema='CP12_WHOLE_ARCHIVE_LOSSLESS_GIT_PARTS_V1',
        file_name=source.name,bytes=size,sha256=digest,chunk_bytes=CHUNK_BYTES,parts=records,
        context=context or {},source_unchanged=True,scientific_payload_modified=False,
        whole_archive_required_for_recovery=True,M2_steps_executed=0,CP12_closed=False)
    (destination/'MANIFIESTO.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def restore(folder,output):
    folder=Path(folder).resolve();output=Path(output)
    m=json.loads((folder/'MANIFIESTO.json').read_text())
    assert m['schema']=='CP12_WHOLE_ARCHIVE_LOSSLESS_GIT_PARTS_V1'
    assert m['parts'] and m['chunk_bytes']==CHUNK_BYTES
    assert not output.exists(), 'Never overwrite an archive or a previous attempt'
    assert Path(m['file_name']).name==m['file_name']
    output.parent.mkdir(parents=True,exist_ok=True)
    hasher=hashlib.sha256();count=0
    with output.open('xb') as f:
        for i,r in enumerate(m['parts']):
            expected=f'parts/part_{i:06d}.bin';assert r['path']==expected
            p=folder/expected;assert p.is_file() and not p.is_symlink()
            data=p.read_bytes()
            assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
            assert oid(data)==r['git_blob_sha1']
            assert len(data)==CHUNK_BYTES if i<len(m['parts'])-1 else 0<len(data)<=CHUNK_BYTES
            hasher.update(data);count+=len(data);f.write(data)
        f.flush();os.fsync(f.fileno())
    assert count==m['bytes'] and hasher.hexdigest()==m['sha256']
    return dict(schema='CP12_GIT_ARCHIVE_RECONSTRUCTION_INTEGRITY',passed=True,
        archive=str(output.resolve()),bytes=count,sha256=hasher.hexdigest(),
        parts=len(m['parts']),all_part_sha256_and_Git_object_ids_verified=True,
        M2_steps_executed=0,scientific_frontier=False,CP12_closed=False)

def controls(folder):
    """New transport-administration controls; no F0...F5 or M2."""
    folder=Path(folder);assert not folder.exists();folder.mkdir(parents=True)
    data=bytes(range(256))*6500+b'CP12 immutable archive control'
    source=folder/'source.bin';source.write_bytes(data)
    pack=folder/'pack';m=prepare(source,pack,dict(synthetic=True))
    tests={}
    restore(pack,folder/'recovered.bin');tests['exact_byte_roundtrip']=(folder/'recovered.bin').read_bytes()==data
    def rejects(action):
        try:action()
        except (AssertionError,FileNotFoundError,FileExistsError):return True
        return False
    tests['no_overwrite']=rejects(lambda:restore(pack,folder/'recovered.bin'))
    part=pack/m['parts'][0]['path'];original=part.read_bytes();part.write_bytes(bytes([original[0]^1])+original[1:])
    tests['corruption_rejected']=rejects(lambda:restore(pack,folder/'corrupt.bin'));part.write_bytes(original)
    p=pack/'MANIFIESTO.json';baseline=p.read_text();changed=json.loads(baseline)
    changed['parts'][0],changed['parts'][1]=changed['parts'][1],changed['parts'][0]
    p.write_text(json.dumps(changed));tests['order_or_path_change_rejected']=rejects(lambda:restore(pack,folder/'wrong_order.bin'));p.write_text(baseline)
    part.rename(pack/'retained_part.bin');tests['missing_part_rejected']=rejects(lambda:restore(pack,folder/'missing.bin'));part.symlink_to(pack/'retained_part.bin')
    tests['symlink_rejected']=rejects(lambda:restore(pack,folder/'symlink.bin'));part.unlink();(pack/'retained_part.bin').rename(part)
    changed=json.loads(baseline);changed['sha256']='0'*64;p.write_text(json.dumps(changed))
    tests['whole_archive_hash_rejected']=rejects(lambda:restore(pack,folder/'wrong_archive.bin'));p.write_text(baseline)
    tests['source_bytes_unchanged']=source.read_bytes()==data
    r=dict(schema='CP12_NEW_GIT_PRESERVATION_CONTROL',passed=all(tests.values()),tests=tests,
        source_sha256=sha(Path(__file__)),M2_steps_executed=0,preflight_repeated=False,
        failed_control_outputs_retained=True,CP12_closed=False)
    (folder/'CONTROLES.json').write_text(json.dumps(r,indent=2)+'\n')
    assert r['passed'],r
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('prepare');a.add_argument('source',type=Path);a.add_argument('destination',type=Path)
    a=sub.add_parser('restore');a.add_argument('folder',type=Path);a.add_argument('output',type=Path)
    a=sub.add_parser('controls');a.add_argument('folder',type=Path)
    a=p.parse_args()
    if a.command=='prepare':r=prepare(a.source,a.destination)
    elif a.command=='restore':r=restore(a.folder,a.output)
    else:r=controls(a.folder)
    print(json.dumps({k:v for k,v in r.items() if k!='parts'}))
