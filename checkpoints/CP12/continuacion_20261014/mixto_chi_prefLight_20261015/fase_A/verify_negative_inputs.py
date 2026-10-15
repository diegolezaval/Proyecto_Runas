"""Authenticate the complete failed K4 capsule without evolving the model."""
import argparse,hashlib,json,zipfile
from pathlib import Path
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
    assert a.archive.stat().st_size==39126835
    assert sha(a.archive.read_bytes())=='f4176ec466647faa5a48a427403db3a865f3eef8fda21ea0f837520adfc5bf0b'
    assert not a.destination.exists()
    with zipfile.ZipFile(a.archive) as z:
        names=z.namelist();assert len(names)==len(set(names))
        for n in names:
            r=Path(n);assert not r.is_absolute() and '..' not in r.parts
        m=json.loads(z.read('MANIFIESTO_NEGATIVO.json'))
        assert set(names)==set(m['files'])|{'MANIFIESTO_NEGATIVO.json'}
        for n,r in m['files'].items():
            b=z.read(n);assert len(b)==r['bytes'] and sha(b)==r['sha256'],n
        a.destination.mkdir(parents=True);z.extractall(a.destination)
    print(json.dumps({'passed':True,'payload_files':len(m['files']),'coverage_exact':True,'all_hashes_verified':True,'M2_steps':0}))
if __name__=='__main__':main()
