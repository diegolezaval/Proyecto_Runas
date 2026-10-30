"""Inventario completo de un commit y contraste del manifiesto histórico; sin M2."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def audit(root, commit):
    records = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-rz', '--full-tree', commit])
    files = {}
    for record in records.split(b'\0'):
        if not record:
            continue
        meta, path = record.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        path = path.decode()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('Entrada no regular: ' + path)
        content = subprocess.check_output(['git', '-C', str(root), 'cat-file', 'blob', oid])
        actual = root / path
        files[path] = dict(git_blob=oid, bytes=len(content), sha256=hashlib.sha256(content).hexdigest(),
                           working_copy_matches=actual.is_file() and not actual.is_symlink() and actual.read_bytes()==content)
    manifest = json.loads(subprocess.check_output(['git', '-C', str(root), 'show', commit+':MANIFIESTO_SHA256.json']))
    expected = manifest['files']
    return dict(schema='RUNICA_EXACT_GIT_TREE_INVENTORY_V1', commit=commit, files=files,
                file_count=len(files), logical_bytes=sum(x['bytes'] for x in files.values()),
                all_working_bytes_match=all(x['working_copy_matches'] for x in files.values()),
                historical_manifest_entries=len(expected),
                historical_missing=sorted(set(expected)-set(files)),
                historical_changed=[p for p,h in expected.items() if p in files and files[p]['sha256']!=h],
                historical_uncovered=sorted(set(files)-set(expected)-{'MANIFIESTO_SHA256.json'}),
                M2_steps_executed=0, scope='Identidad e integridad del árbol; no aceptación científica.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--commit',required=True);parser.add_argument('--salida',type=Path,required=True)
    args=parser.parse_args();result=audit(args.root.resolve(),args.commit)
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    with args.salida.open('x') as out:out.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','historical_uncovered')},ensure_ascii=False))
    print('uncovered',len(result['historical_uncovered']))
    return 0 if result['all_working_bytes_match'] else 1


if __name__=='__main__':raise SystemExit(main())
