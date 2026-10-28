"""Cápsula P3 completa, solicitud de adjunto y aceptación tras descarga/auditoría.

La subida se efectúa por el canal autorizado de GitHub. Este programa no contiene
credenciales y no acepta una publicación sin verificar sus bytes recuperados.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile

REPOSITORY = 'diegolezaval/Proyecto_Runas'
UID = '128492e27d6d44798f2ef9336fc1b2e7'
MIN_CAPACITY_BYTES = 229848115
CAPACITY_SEED = b'CP12_P3_RELEASE_CAPACITY_PROBE_V1'


def sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def original_audits(home, output):
    output.mkdir()
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       PYTHONPYCACHEPREFIX=str(home / 'runtime/pycache'), TMPDIR=str(home / 'runtime/tmp'))
    if environment.get('OPENBLAS_CORETYPE'):
        raise ValueError('No se fuerza la arquitectura BLAS')
    results = {}
    for name, script, flags in [('boundary8', 'coordinator.py', ['--audit-only', '8']),
                               ('transport', 'controlador_transporte.py', ['--audit-transport'])]:
        process = subprocess.run([sys.executable, str(home / script), '--home', str(home), *flags],
                                 env=environment, capture_output=True, text=True)
        (output / (name + '_stdout.json')).write_text(process.stdout)
        (output / (name + '_stderr.txt')).write_text(process.stderr)
        if process.returncode:
            raise RuntimeError(f'Auditor original {name} falló con código {process.returncode}')
        result = json.loads(process.stdout)
        if not result['passed'] or result['M2_steps_executed'] != 0 or result['DOP853_construction_or_step_attempts'] != 0:
            raise ValueError('La auditoría original no pasó sin pasos')
        results[name] = result
    return results


def selected(home):
    ignored = {'runtime', 'capsules', 'recoveries', 'cache', '__pycache__'}
    allowed_roots = {'science', 'candidate', 'outputs', 'prior', 'preregistration', 'ancestor',
                     'proofs', 'analysis', 'negative', 'transport', 'administracion_github_20261028'}
    original_names = set(read(home / 'MANIFIESTO_NEGATIVO.json')['files'])
    files = {}
    for path in sorted(home.rglob('*')):
        relative = path.relative_to(home)
        if any(p in ignored or p.startswith('.') for p in relative.parts) or path.suffix in ('.tmp', '.pyc', '.so'):
            continue
        if path.is_symlink():
            raise ValueError('No se conservan enlaces simbólicos')
        if not path.is_file() or relative.as_posix() == 'MANIFIESTO_NEGATIVO.json':
            continue
        name = relative.as_posix()
        if len(relative.parts) == 1 and name not in original_names:
            raise ValueError(f'Archivo de raíz fuera del inventario: {name}')
        if len(relative.parts) > 1 and relative.parts[0] not in allowed_roots:
            raise ValueError(f'Carpeta fuera del inventario: {name}')
        files[name] = path
    missing = set(original_names) - set(files)
    if missing:
        raise ValueError(f'Faltan cargas originales: {sorted(missing)}')
    return files


def prepare(args):
    home, output = args.home.resolve(), args.salida.resolve()
    if not re.fullmatch(r'[A-Z0-9_]+', args.label):
        raise ValueError('Etiqueta inválida')
    output.mkdir(parents=True, exist_ok=False)
    results = original_audits(home, output / 'auditoria_local')
    clock = results['transport']['observer_clock']
    if args.capacity_probe:
        probe = home / 'administracion_github_20261028/capacity_probe.bin'
        probe.parent.mkdir(parents=True, exist_ok=True)
        if probe.exists():
            raise FileExistsError('No se sobrescribe la prueba de capacidad')
        with probe.open('xb') as stream:
            for i in range(32768):
                stream.write(hashlib.sha256(CAPACITY_SEED + i.to_bytes(8, 'big')).digest())
        write_new(probe.with_suffix('.json'), dict(schema='CP12_DETERMINISTIC_ADMINISTRATIVE_CAPACITY_PROBE_V1',
                  bytes=probe.stat().st_size, sha256=sha(probe), seed=CAPACITY_SEED.decode(),
                  algorithm='Concatenate SHA256(seed + uint64_big_endian(i)) for i in range(32768)',
                  scientific_data=False, M2_steps_executed=0))
    files = selected(home)
    inventory = {n:dict(bytes=p.stat().st_size, sha256=sha(p)) for n,p in files.items()}
    archive = output / ('CP12_CANDIDATO_P3_' + UID + '_' + args.label + '.zip')
    ancestor_name = 'ancestor/retoma_20261028/MANIFIESTO_FUENTE_TAU9p6.json'
    if ancestor_name in inventory:
        raise ValueError('Colisión del manifiesto histórico')
    ancestor = (home / 'MANIFIESTO_NEGATIVO.json').read_bytes()
    inventory[ancestor_name] = dict(bytes=len(ancestor), sha256=hashlib.sha256(ancestor).hexdigest())
    manifest = dict(schema='CP12_P3_RELEASE_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER_V1',
                    observer_clock=clock, execution_uuid=UID, label=args.label, CP12_closed=False,
                    correction_validated=False, scientific_frontier=False, files=inventory)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
        for name, path in files.items():
            content = path.read_bytes()
            if len(content) != inventory[name]['bytes'] or hashlib.sha256(content).hexdigest() != inventory[name]['sha256']:
                raise ValueError(f'Archivo cambió al empaquetar: {name}')
            zipped.writestr(name, content)
        zipped.writestr(ancestor_name, ancestor)
        zipped.writestr('MANIFIESTO_NEGATIVO.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    source_unchanged = all(p.stat().st_size == inventory[n]['bytes'] and sha(p) == inventory[n]['sha256'] for n,p in files.items())
    if not source_unchanged or (args.capacity_probe and archive.stat().st_size <= MIN_CAPACITY_BYTES):
        raise ValueError('Fuente alterada o prueba de tamaño insuficiente')
    request = dict(schema='CP12_GITHUB_RELEASE_ATTACHMENT_REQUEST_V1', created_at_utc=now(),
                   repository=REPOSITORY, release_tag='respaldo-cp12-p3-20261027', label=args.label,
                   file_name=archive.name, bytes=archive.stat().st_size, sha256=sha(archive),
                   observer_clock=clock, transport_state_sha256=results['transport']['state_sha256'],
                   closed_state_sha256=results['boundary8']['state_sha256'],
                   source_home=str(home), archive_path=str(archive), source_inventory=inventory,
                   synthetic_ancestor_member=ancestor_name, source_unchanged_after_packaging=True,
                   capacity_probe=args.capacity_probe, minimum_capacity_bytes=MIN_CAPACITY_BYTES,
                   conservation_driver_sha256=sha(Path(__file__)),
                   scientific_frontier=False, CP12_closed=False, M2_steps_executed=0)
    write_new(output / 'SOLICITUD.json', request)
    print(json.dumps({k:request[k] for k in ['label','file_name','bytes','sha256','observer_clock','capacity_probe']},ensure_ascii=False), flush=True)


def accept(args):
    request = read(args.solicitud)
    metadata = read(args.asset_metadata)
    if request['schema'] != 'CP12_GITHUB_RELEASE_ATTACHMENT_REQUEST_V1' or request['repository'] != REPOSITORY:
        raise ValueError('Solicitud ajena al protocolo')
    if metadata['name'] != request['file_name'] or metadata['size'] != request['bytes'] or metadata['digest'] != 'sha256:' + request['sha256']:
        raise ValueError('Metadatos del adjunto no coinciden')
    url = metadata['browser_download_url']
    prefix = 'https://github.com/' + REPOSITORY + '/releases/download/' + request['release_tag'] + '/'
    if url != prefix + request['file_name']:
        raise ValueError('URL fuera de la Release registrada')
    output = args.salida.resolve()
    output.mkdir(parents=True, exist_ok=False)
    archive = output / request['file_name']
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Proyecto-Runas-recovery/1.0'}),timeout=60) as response, archive.open('xb') as dest:
        shutil.copyfileobj(response, dest, 1024 * 1024)
    if archive.stat().st_size != request['bytes'] or sha(archive) != request['sha256']:
        raise ValueError('Descarga pública distinta de la fuente')
    driver = Path(__file__).with_name('auditar_recuperacion.py')
    process = subprocess.run([sys.executable, str(driver), '--archivo', str(archive), '--sha256', request['sha256'],
                              '--bytes', str(request['bytes']), '--home', str(output / 'extraido'),
                              '--salida', str(output / 'auditoria')], capture_output=True, text=True)
    (output / 'audit_driver_stdout.txt').write_text(process.stdout)
    (output / 'audit_driver_stderr.txt').write_text(process.stderr)
    if process.returncode:
        raise RuntimeError('Auditoría de la descarga fallida; no se emite aceptación')
    audit = read(output / 'auditoria/RESULTADO.json')
    transport = audit['audits']['transport']['audit']
    if not audit['passed'] or transport['state_sha256'] != request['transport_state_sha256'] or transport['observer_clock'] != request['observer_clock']:
        raise ValueError('La descarga no restaura el transporte solicitado')
    source = Path(request['source_home'])
    for name, item in request['source_inventory'].items():
        if name == request['synthetic_ancestor_member']:
            continue
        path = source / name
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError(f'Fuente cambió después de subir: {name}')
    if sha(Path(request['archive_path'])) != request['sha256']:
        raise ValueError('El ZIP local cambió después de subir')
    receipt = dict(schema='CP12_GITHUB_RELEASE_TRANSPORT_ACCEPTANCE_V1', accepted_at_utc=now(), passed=True,
                   label=request['label'], observer_clock=request['observer_clock'], file_name=request['file_name'],
                   bytes=request['bytes'], sha256=request['sha256'], download_url=url, github_asset_id=metadata['id'],
                   request_sha256=sha(args.solicitud), transport_state_sha256=transport['state_sha256'],
                   source_archive_and_payload_unchanged=True, exact_manifest_coverage=True,
                   independently_extracted_zero_step_audits_passed=True, audit_receipt_sha256=sha(output / 'auditoria/RESULTADO.json'),
                   capacity_probe=request['capacity_probe'], M2_steps_executed_during_preservation=0,
                   scientific_frontier=False, correction_validated=False, CP12_closed=False)
    write_new(output / 'ACEPTACION.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('preparar');p.add_argument('--home',type=Path,required=True);p.add_argument('--label',required=True)
    p.add_argument('--salida',type=Path,required=True);p.add_argument('--capacity-probe',action='store_true')
    p = sub.add_parser('aceptar');p.add_argument('--solicitud',type=Path,required=True);p.add_argument('--asset-metadata',type=Path,required=True)
    p.add_argument('--salida',type=Path,required=True)
    args = parser.parse_args()
    if args.mode == 'preparar':
        prepare(args)
    else:
        accept(args)


if __name__ == '__main__':
    main()
