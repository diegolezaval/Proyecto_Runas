"""Administrative, lossless readable export; never evolve M2 or change its arrays."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        assert json.loads(p.read_text()) == value, 'Never overwrite different evidence'
        return
    p.write_text(json.dumps(value, separators=(',', ':'), ensure_ascii=False, allow_nan=False) + '\n')

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--state', type=Path, required=True)
    a.add_argument('--destination', type=Path, required=True)
    a.add_argument('--science-root', type=Path, required=True)
    args = a.parse_args()
    state = args.state.resolve(); dest = args.destination.resolve()
    with np.load(state, allow_pickle=False) as z:
        arrays = {k: z[k].copy(order='K') for k in z.files}
    cfg = json.loads(str(arrays['config']))
    manifest = dict(schema='CP12_READABLE_LOSSLESS_NUMERIC_STATE',
                    time=float(arrays['time']), source_npz_sha256=digest(state),
                    source_npz_bytes=state.stat().st_size, fields=[],
                    arrays_and_scientific_strings_unchanged=True,
                    private_executor_metadata_included=False, CP12_closed=False)
    refs = []
    for name in cfg['reference_states']:
        p = args.science_root / name
        with np.load(p, allow_pickle=False) as z:
            refs.append({k: z[k].copy() for k in ['initial_q', 'initial_v']})
    for key, array in arrays.items():
        field = dict(name=key, dtype=array.dtype.str, shape=list(array.shape),
                     fortran_order=bool(array.flags.f_contiguous and not array.flags.c_contiguous),
                     array_bytes_sha256=hashlib.sha256(array.tobytes(order='C')).hexdigest())
        assert not array.dtype.hasobject
        if key in ['initial_q', 'initial_v']:
            initial = np.concatenate([r[key] for r in refs], axis=1)
            assert initial.tobytes() == array.tobytes()
            field.update(storage='exact_CP10_initial_arrays',
                         references=[dict(path=name, sha256=digest(args.science_root / name))
                                     for name in cfg['reference_states']])
        elif array.dtype.kind in 'fiu':
            assert np.isfinite(array).all()
            flat = array.ravel(order='C'); pieces=[]
            # The first q trial was retained. All subsequent pieces are readable
            # decimal values with offsets; float repr roundtrips binary64 exactly.
            starts = [0] + list(range(8000, len(flat), 32000)) if key == 'q' else list(range(0, len(flat), 32000))
            for index, start in enumerate(starts):
                stop = starts[index + 1] if index + 1 < len(starts) else len(flat)
                p = dest / key / f'{index:06d}.json'
                content = dict(schema='CP12_READABLE_SCIENTIFIC_NUMERIC_ARRAY_PART',
                               field=key, dtype=str(array.dtype), shape=list(array.shape),
                               flat_offset=start, time=manifest['time'],
                               source_npz_sha256=manifest['source_npz_sha256'],
                               values=flat[start:stop].tolist(), private_metadata_present=False)
                write(p, content)
                restored=np.asarray(json.loads(p.read_text())['values'], dtype=array.dtype)
                assert restored.tobytes() == flat[start:stop].tobytes()
                pieces.append(dict(path=p.relative_to(dest).as_posix(), offset=start,
                                   count=stop-start, sha256=digest(p), bytes=p.stat().st_size))
            field.update(storage='readable_numeric_parts', parts=pieces)
        else:
            assert array.dtype.kind in 'US' and array.shape == ()
            text=str(array)
            if key == 'budget_rows':
                rows=json.loads(text); assert json.dumps(rows) == text
                pieces=[]
                for start in range(0,len(rows),40):
                    p=dest / key / f'{start//40:06d}.json'
                    write(p,dict(field=key,row_offset=start,rows=rows[start:start+40],
                                 time=manifest['time'],source_npz_sha256=manifest['source_npz_sha256']))
                    pieces.append(dict(path=p.relative_to(dest).as_posix(),offset=start,
                                       count=len(rows[start:start+40]),sha256=digest(p),bytes=p.stat().st_size))
                field.update(storage='scientific_budget_rows_parts',parts=pieces)
            else:
                p=dest / key / 'value.json'; write(p,dict(field=key,value=text))
                field.update(storage='scientific_string',path=p.relative_to(dest).as_posix(),sha256=digest(p))
        manifest['fields'].append(field)
    write(dest / 'MANIFIESTO_TEXTUAL.json',manifest)
    print(json.dumps(dict(time=manifest['time'],fields=len(manifest['fields']),
                         files=sum(1 for p in dest.rglob('*') if p.is_file()),
                         bytes=sum(p.stat().st_size for p in dest.rglob('*') if p.is_file()),
                         source_npz_sha256=manifest['source_npz_sha256'], M2_steps=0)))

if __name__ == '__main__':
    main()
