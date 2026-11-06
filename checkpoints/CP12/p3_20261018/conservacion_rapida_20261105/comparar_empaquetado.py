"""Compare ZIP packing only, without loading arrays or scientific modules."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import statistics
import time
import zipfile


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def administrative_change(original, candidate):
    old=ast.parse(original.read_text()); new=ast.parse(candidate.read_text())
    before=ast.parse('z.writestr(n,b)').body[0].value
    after=ast.parse("z.writestr(n,b,compress_type=zipfile.ZIP_STORED if n.endswith('.npz') else zipfile.ZIP_DEFLATED,compresslevel=6)").body[0].value
    class Normalize(ast.NodeTransformer):
        count=0
        def visit_Call(self,node):
            if ast.dump(node)==ast.dump(after):
                self.count+=1
                return before
            return self.generic_visit(node)
    normalize=Normalize(); normalized=normalize.visit(new)
    if normalize.count!=1 or ast.dump(old)!=ast.dump(normalized):
        raise ValueError('Change exceeds the single registered serialization call')


def run(args):
    if args.output.exists():
        raise FileExistsError('Keep each measurement and refuse replacement')
    source=args.archive.resolve()
    if sha(source)!=args.sha256 or source.stat().st_size!=args.bytes:
        raise ValueError('Source identity mismatch')
    original=args.original.resolve(); candidate=args.candidate.resolve()
    administrative_change(original,candidate)
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(source) as z:
        entries=[(i.filename,z.read(i.filename)) for i in z.infolist()]
    inventory={name:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in entries}
    if len(inventory)!=len(entries):
        raise ValueError('Duplicate source entry')
    spec=importlib.util.spec_from_file_location('original_unpack_only',args.auditor)
    unpacker=importlib.util.module_from_spec(spec); spec.loader.exec_module(unpacker)
    observations=[]
    # Reverse the order on the second pair to reduce the cache/order bias.
    for repeat, modes in enumerate((('deflate_all','store_npz'),('store_npz','deflate_all')),1):
        for mode in modes:
            target=args.output/f'{mode}_{repeat}.zip'
            started=time.perf_counter()
            with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                for name,data in entries:
                    info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
                    method=zipfile.ZIP_STORED if mode=='store_npz' and name.endswith('.npz') else zipfile.ZIP_DEFLATED
                    z.writestr(info,data,compress_type=method,compresslevel=6)
            elapsed=time.perf_counter()-started
            with zipfile.ZipFile(target) as z:
                if z.namelist()!=[name for name,_ in entries]:
                    raise ValueError('Entry order/coverage changed')
                recovered={name:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
                           for name,data in ((n,z.read(n)) for n in z.namelist())}
            if recovered!=inventory:
                raise ValueError('Payload bytes changed')
            manifest=unpacker.unpack(target,args.output/f'{mode}_{repeat}_extraido',sha(target),target.stat().st_size)
            observations.append(dict(mode=mode,repeat=repeat,packing_seconds=elapsed,
                bytes=target.stat().st_size,sha256=sha(target),exact_entries_and_all_payload_bytes=True,
                original_unpacker_passed=True,payload_files=len(manifest['files'])))
            print(json.dumps(observations[-1]),flush=True)
    medians={mode:statistics.median(o['packing_seconds'] for o in observations if o['mode']==mode)
             for mode in ('deflate_all','store_npz')}
    sizes={mode:next(o['bytes'] for o in observations if o['mode']==mode) for mode in medians}
    if sha(source)!=args.sha256:
        raise ValueError('Source changed')
    result=dict(schema='CP12_P3_LOSSLESS_PACKING_BENCHMARK_V1',passed=True,
        source_archive_sha256=args.sha256,source_archive_bytes=args.bytes,
        original_preserver_sha256=sha(original),candidate_preserver_sha256=sha(candidate),
        only_registered_serialization_call_changed=True,source_archive_unchanged=True,
        archive_entries=len(entries),observations=observations,median_packing_seconds=medians,
        packing_speedup=medians['deflate_all']/medians['store_npz'],
        archive_bytes=sizes,extra_bytes=sizes['store_npz']-sizes['deflate_all'],
        extra_fraction=sizes['store_npz']/sizes['deflate_all']-1,
        scientific_modules_imported=False,M2_steps_executed=0,CP12_closed=False,
        scope='Packing only in this environment; not evolution or end-to-end conservation speed.',
        actual_process_capacity_and_original_audits_still_required=True)
    (args.output/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('archive','original','candidate','auditor','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--bytes',type=int,required=True)
    print(json.dumps(run(parser.parse_args()),ensure_ascii=False))
