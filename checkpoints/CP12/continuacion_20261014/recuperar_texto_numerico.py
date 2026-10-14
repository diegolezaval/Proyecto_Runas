"""Rebuild the exact scientific NPZ from inspectable decimal values and CP10 inputs."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def recover(source, science, output):
    m=json.loads((source / 'MANIFIESTO_TEXTUAL.json').read_text()); arrays={}
    for f in m['fields']:
        dtype=np.dtype(f['dtype']);shape=tuple(f['shape'])
        if f['storage']=='exact_CP10_initial_arrays':
            initial=[]
            for r in f['references']:
                p=science/r['path'];assert sha(p)==r['sha256']
                with np.load(p,allow_pickle=False) as z:initial.append(z[f['name']].copy())
            a=np.concatenate(initial,axis=1)
        elif f['storage']=='readable_numeric_parts':
            count=int(np.prod(shape)) if shape else 1
            a=np.empty(count,dtype=dtype);next_offset=0
            for part in f['parts']:
                p=source/part['path'];assert sha(p)==part['sha256']
                d=json.loads(p.read_text());assert d['field']==f['name'] and d['flat_offset']==next_offset==part['offset']
                values=np.asarray(d['values'],dtype=dtype);assert len(values)==part['count']
                a[next_offset:next_offset+len(values)]=values;next_offset+=len(values)
            assert next_offset==count;a=a.reshape(shape)
        elif f['storage']=='scientific_budget_rows_parts':
            rows=[]
            for part in f['parts']:
                p=source/part['path'];assert sha(p)==part['sha256']
                d=json.loads(p.read_text());assert d['field']==f['name'] and d['row_offset']==len(rows)==part['offset']
                assert len(d['rows'])==part['count'];rows.extend(d['rows'])
            a=np.asarray(json.dumps(rows),dtype=dtype)
        else:
            assert f['storage']=='scientific_string'
            p=source/f['path'];assert sha(p)==f['sha256']
            d=json.loads(p.read_text());assert d['field']==f['name'];a=np.asarray(d['value'],dtype=dtype)
        if f['fortran_order']:a=np.asfortranarray(a)
        assert a.dtype==dtype and a.shape==shape
        assert hashlib.sha256(a.tobytes(order='C')).hexdigest()==f['array_bytes_sha256']
        arrays[f['name']]=a
    assert not output.exists(), 'Never overwrite scientific evidence'
    output.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(output,**arrays)
    assert output.stat().st_size==m['source_npz_bytes'] and sha(output)==m['source_npz_sha256']
    return dict(passed=True,time=m['time'],state_sha256=sha(output),fields=len(arrays),
                exact_original_npz_bytes=True,M2_steps=0,CP12_closed=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--science-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(recover(a.source.resolve(),a.science_root.resolve(),a.output.resolve())))

if __name__=='__main__':main()
