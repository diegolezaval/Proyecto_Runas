"""Lossless transport of the original checkpoint ZIP through immutable Git bytes.

No recompression, numerical transformations, physics steps or criteria changes.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT/'trazabilidad/CP12_respaldos_Git'
# Below the GitHub Contents API's 1 MiB content threshold. The preregistered
# upper bound remains 1 MiB; changing transport pieces preserves every ZIP byte.
CHUNK = 524288
SMALL = 65536
PENDING = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def object_record(data):
    sha=digest(data)
    path=STORE/'objetos'/(sha+'.bin')
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('Content address collision or altered object')
    else:
        with path.open('xb') as stream:stream.write(data)
    return dict(object_sha256=sha,object_bytes=len(data),path=path.relative_to(ROOT).as_posix())


def keep(data):
    refs=[]
    for start in range(0,len(data),CHUNK):
        part=data[start:start+CHUNK];sha=digest(part)
        if len(part)<=SMALL:
            if sha not in PENDING:
                PENDING[sha]=(part,dict(sha256=sha,bytes=len(part)))
            refs.append(PENDING[sha][1])
        else:
            refs.append(dict(sha256=sha,bytes=len(part),offset=0,**object_record(part)))
    return refs


def flush_small():
    buffer=bytearray();members=[]
    def flush():
        obj=object_record(bytes(buffer))
        for ref,offset in members:ref.update(offset=offset,**obj)
        buffer.clear();members.clear()
    for sha,(part,ref) in sorted(PENDING.items()):
        if buffer and len(buffer)+len(part)>CHUNK:flush()
        members.append((ref,len(buffer)));buffer.extend(part)
    if buffer:flush()
    PENDING.clear()


def pack(archive, api_recipe=False):
    if PENDING:raise ValueError('Unfinished earlier transport operation')
    raw=archive.read_bytes()
    with zipfile.ZipFile(archive) as z:
        manifest=json.loads(z.read('Proyecto_Runas/MANIFIESTO_REINICIO_CP12.json'))
        suffix='_API' if api_recipe else ''
        path=STORE/('tau'+str(int(manifest['time'])).zfill(4)+suffix+'.json')
        if path.exists():raise ValueError('Do not overwrite an earlier capsule recipe')
        infos=z.infolist()
        if not infos:raise ValueError('Empty checkpoint')
        recipe=dict(schema='CP12_ZIP_BYTES_CAS_1',time=manifest['time'],run_id=manifest['run_id'],
                    original_zip_sha256=digest(raw),original_zip_bytes=len(raw),
                    prefix=keep(raw[:infos[0].header_offset]),members=[])
        for i,info in enumerate(infos):
            offset=info.header_offset
            local=struct.unpack('<4s5H3I2H',raw[offset:offset+30])
            if local[0]!=b'PK\x03\x04':raise ValueError('Invalid local ZIP header')
            begin=offset+30+local[-2]+local[-1]
            end=begin+info.compress_size
            next_start=infos[i+1].header_offset if i+1<len(infos) else z.start_dir
            if not begin<=end<=next_start:raise ValueError('Invalid compressed member coverage')
            recipe['members'].append(dict(name=info.filename,
                header_b64=base64.b64encode(raw[offset:begin]).decode(),
                compressed=keep(raw[begin:end]),
                suffix_b64=base64.b64encode(raw[end:next_start]).decode()))
        recipe['tail']=keep(raw[z.start_dir:])
        flush_small()
    path.write_text(json.dumps(recipe,indent=2)+'\n')
    return path


def restore(recipe_path,destination):
    recipe=json.loads(recipe_path.read_text())
    if recipe['schema']!='CP12_ZIP_BYTES_CAS_1':raise ValueError('Unknown transport schema')
    def append(stream,refs):
        for ref in refs:
            rel=Path(ref['path'])
            if rel.is_absolute() or '..' in rel.parts or not rel.is_relative_to('trazabilidad/CP12_respaldos_Git/objetos'):
                raise ValueError('Unexpected object path')
            data=(ROOT/rel).read_bytes()
            if len(data)!=ref['object_bytes'] or digest(data)!=ref['object_sha256']:raise ValueError('Incomplete or altered capsule object')
            start=ref['offset'];part=data[start:start+ref['bytes']]
            if start<0 or len(part)!=ref['bytes'] or digest(part)!=ref['sha256']:raise ValueError('Altered object slice')
            stream.write(part)
    with destination.open('xb') as stream:
        append(stream,recipe['prefix'])
        for member in recipe['members']:
            stream.write(base64.b64decode(member['header_b64'],validate=True))
            append(stream,member['compressed'])
            stream.write(base64.b64decode(member['suffix_b64'],validate=True))
        append(stream,recipe['tail'])
    if destination.stat().st_size!=recipe['original_zip_bytes'] or digest(destination.read_bytes())!=recipe['original_zip_sha256']:
        raise ValueError('Restored ZIP is not byte-identical to original')
    return recipe


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pack',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--restore',type=Path);a=p.parse_args()
    if a.pack:print(pack(a.pack))
    elif a.recipe and a.restore:print(json.dumps(restore(a.recipe,a.restore)))
    else:p.error('Use --pack or --recipe with --restore')
