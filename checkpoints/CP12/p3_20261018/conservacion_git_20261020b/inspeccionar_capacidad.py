"""Inspect the authenticated scientific capsule and package it without M2 imports."""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, re, subprocess, zipfile
import numpy as np

ARCHIVE_SHA = 'a71554ff3e213d09cf7365697e4d9c9307e9529478d567ae3f89ccc11e43b959'
ARCHIVE_BYTES = 229821160
SECRET = re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|AKIA[A-Z0-9]{16}|sk-(?:proj-)?[A-Za-z0-9_-]{40,}')

def sha(data): return hashlib.sha256(data).hexdigest()
def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def inspect(archive, repo, report):
    raw = archive.read_bytes()
    assert len(raw) == ARCHIVE_BYTES and sha(raw) == ARCHIVE_SHA
    public = set(line.split()[2] for line in subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=repo,text=True).splitlines())
    inventory=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist(); assert len(names)==len(set(names))
        m=json.loads(z.read('MANIFIESTO_NEGATIVO.json'))
        assert set(names)==set(m['files'])|{'MANIFIESTO_NEGATIVO.json'}
        for name in names:
            p=Path(name); assert not p.is_absolute() and '..' not in p.parts
            assert p.parts[0] in {'CONTROLES_SINTETICOS.json','CONTROL_ADAPTACION_ESTATICA.json','MANIFIESTO_NEGATIVO.json','analysis','ancestor','candidate','configuration.json','controlador_transporte.py','coordinator.py','negative','outputs','preregistration','preservation.py','prior','proofs','science','seleccion_canonica.py','transport','transporte.py'}
            assert not any(x.lower() in {'.env','credentials','cookies','id_rsa','id_ed25519','.aws','.ssh','.config'} for x in p.parts)
            data=z.read(name)
            if name in m['files']:
                assert len(data)==m['files'][name]['bytes'] and sha(data)==m['files'][name]['sha256']
            oid=hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()
            entry=dict(path=name,bytes=len(data),sha256=sha(data),git_blob_sha1=oid,identical_public_git_blob=oid in public)
            if p.suffix=='.npz':
                arrays=[]
                with np.load(io.BytesIO(data),allow_pickle=False) as a:
                    for k in a.files:
                        v=a[k];assert not v.dtype.hasobject
                        if v.dtype.kind in 'US': assert not SECRET.search(v.tobytes()),name
                        else: assert v.dtype.kind in 'biufc', (name,k,v.dtype)
                        arrays.append(dict(name=k,dtype=v.dtype.str,shape=list(v.shape)))
                entry.update(kind='scientific_numpy_archive_without_objects',arrays=arrays)
            elif p.suffix in {'.json','.jsonl','.md','.py','.txt','.c'}:
                data.decode('utf-8'); assert not SECRET.search(data),name
                entry['kind']='scientific_source_or_provenance_utf8'
            else:
                assert name=='ancestor/administrative_capture_tau0/omitted_bytecode_transporte.bin',name
                entry['kind']='historical_scientific_transport_bytecode'
            inventory.append(entry)
    result=dict(schema='CP12_CAPACITY_PAYLOAD_CONTENT_INVENTORY',archive_bytes=len(raw),archive_sha256=sha(raw),payload_hashes_verified=len(m['files']),entries=inventory,all_numpy_members_loaded_without_pickle=True,credential_path_and_high_confidence_secret_checks_passed=True,scope='Only the authenticated user-authorized scientific capsule; no unrelated files, browser state, credentials or account exports',public_repository='diegolezaval/Proyecto_Runas',M2_steps_executed=0,CP12_closed=False)
    write(report,result);return result

def build(archive, report, output):
    assert not output.exists()
    padding=hashlib.shake_256(b'Proyecto_Runas P3 capacity padding, no scientific state').digest(1048576)
    context=dict(schema='CP12_CAPACITY_PROBE_WITH_COMPLETE_AUDITED_TRANSPORT',inner_archive_name=archive.name,inner_archive_bytes=ARCHIVE_BYTES,inner_archive_sha256=ARCHIVE_SHA,padding_bytes=len(padding),padding_sha256=sha(padding),lost_tau11p2_archive_bytes=229848115,capacity_test_is_not_a_scientific_frontier=True,M2_steps_executed=0)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_STORED) as z:
        for name,data in [(archive.name,archive.read_bytes()),('SOURCE_CONTENT_INVENTORY.json',report.read_bytes()),('CAPACITY_CONTEXT.json',json.dumps(context,indent=2).encode()),('DETERMINISTIC_PADDING.bin',padding)]:
            info=zipfile.ZipInfo(name,date_time=(2026,10,20,21,0,0));info.compress_type=zipfile.ZIP_STORED;info.external_attr=0o100644<<16;z.writestr(info,data)
    assert output.stat().st_size>229848115
    with zipfile.ZipFile(output) as z:
        assert sha(z.read(archive.name))==ARCHIVE_SHA
        assert z.read('DETERMINISTIC_PADDING.bin')==padding
    return dict(file_name=output.name,bytes=output.stat().st_size,sha256=sha(output.read_bytes()),inner_archive_bytes=ARCHIVE_BYTES,inner_archive_sha256=ARCHIVE_SHA,complete=True,remote_preservation_proven=False,M2_steps_executed=0)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--archive',type=Path,required=True);a.add_argument('--repo',type=Path,required=True);a.add_argument('--report',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a=a.parse_args()
    inspect(a.archive,a.repo,a.report)
    result=build(a.archive,a.report,a.output)
    write(a.output.with_suffix('.json'),result)
    print(json.dumps(result))
