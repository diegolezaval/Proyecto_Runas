#!/usr/bin/env python3
"""Comprueba bytes y manifiestos de los ZIP CP12; no importa ni ejecuta su código."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import zipfile


def digest_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    if (not name or '\\' in name or ':' in name or '\x00' in name
            or path.is_absolute() or any(p in ('', '.', '..') for p in name.rstrip('/').split('/'))):
        raise ValueError(f'Ruta ZIP insegura: {name!r}')
    return name


def verify_archive(directory, archive):
    name = safe_name(archive['file_name'])
    if '/' in name:
        raise ValueError('El nombre del ZIP debe ser un nombre simple')
    path = directory / name
    result = {'id': archive['id'], 'file_name': name, 'passed': False}
    try:
        if path.stat().st_size != archive['bytes']:
            raise ValueError('Tamaño global distinto del índice')
        if digest_file(path) != archive['sha256']:
            raise ValueError('SHA-256 global distinto del índice')
        manifest_path = safe_name(archive['manifest_path'])
        prefix = archive['payload_prefix']
        if prefix:
            safe_name(prefix)
            if not prefix.endswith('/'):
                raise ValueError('Prefijo de manifiesto inválido')
        with zipfile.ZipFile(path) as source:
            infos = source.infolist()
            names = [entry.filename for entry in infos]
            if len(set(names)) != len(names):
                raise ValueError('Entradas ZIP duplicadas')
            for entry in infos:
                safe_name(entry.filename)
                if stat.S_ISLNK(entry.external_attr >> 16):
                    raise ValueError('Enlace simbólico ZIP rechazado')
                if entry.is_dir():
                    raise ValueError('Entrada de directorio no declarada')
            manifest = json.loads(source.read(manifest_path))
            files = manifest['files']
            if len(files) != archive['payload_files']:
                raise ValueError('Número de archivos del manifiesto incorrecto')
            expected = {manifest_path}
            for relative in files:
                safe_name(relative)
                expected.add(prefix + relative)
            if len(expected) != len(files) + 1 or set(names) != expected:
                raise ValueError('La cobertura del manifiesto no es exacta')
            checked = {}
            uncompressed = 0
            for relative, metadata in files.items():
                target = prefix + relative
                digest = hashlib.sha256()
                size = 0
                with source.open(target) as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(block)
                        size += len(block)
                if size != metadata['bytes'] or digest.hexdigest() != metadata['sha256']:
                    raise ValueError(f'Bytes o SHA-256 distintos: {target}')
                checked[relative] = digest.hexdigest()
                uncompressed += size
            for relative, sha256 in archive['required_member_sha256'].items():
                if checked.get(relative) != sha256:
                    raise ValueError(f'Identidad requerida distinta: {relative}')
        result.update(passed=True, bytes=path.stat().st_size, sha256=archive['sha256'],
                      manifest_files_verified=len(files), zip_entries_verified=len(names),
                      uncompressed_payload_bytes=uncompressed, exact_manifest_coverage=True,
                      safe_paths=True, all_member_sha256_and_crc_verified=True,
                      required_members_verified=archive['required_member_sha256'])
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as error:
        result['error'] = f'{type(error).__name__}: {error}'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--indice', type=Path, default=Path(__file__).with_name('indice.json'))
    parser.add_argument('--archivos', type=Path, required=True)
    parser.add_argument('--salida', type=Path)
    parser.add_argument('--extraer', type=Path, help='Carpeta nueva; sólo se extrae tras verificar todos los ZIP')
    args = parser.parse_args()
    if args.salida and args.salida.exists():
        parser.error('La salida ya existe; elige otro nombre para conservar el recibo anterior')
    if args.extraer and args.extraer.exists():
        parser.error('La carpeta de extracción ya existe; elige una carpeta nueva')
    index = json.loads(args.indice.read_text(encoding='utf-8'))
    archives = index['archives']
    ids = [a['id'] for a in archives]
    if not archives or len(set(ids)) != len(ids) or not all(re.fullmatch(r'[A-Za-z0-9_-]+', i) for i in ids):
        parser.error('Identificadores de archivo inválidos en el índice')
    results = [verify_archive(args.archivos, archive) for archive in archives]
    receipt = {'schema': 'CP12_RELEASE_ARCHIVE_INTEGRITY_V1',
               'checked_at_utc': datetime.now(timezone.utc).isoformat(),
               'index_sha256': digest_file(args.indice), 'release_url': index['release']['url'],
               'passed': all(r['passed'] for r in results), 'archives': results,
               'scope': 'Integridad y extracción de datos; no certifica rehidratación DOP853 ni puertas científicas',
               'M2_evolution_steps_executed': 0, 'CP12_closed': False}
    if receipt['passed'] and args.extraer:
        args.extraer.mkdir(parents=True, exist_ok=False)
        for archive in archives:
            target = args.extraer / archive['id']
            target.mkdir()
            with zipfile.ZipFile(args.archivos / archive['file_name']) as source:
                for entry in source.infolist():
                    output = target.joinpath(*PurePosixPath(entry.filename).parts)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    with source.open(entry) as stream, output.open('xb') as dest:
                        shutil.copyfileobj(stream, dest, 1024 * 1024)
        receipt['verified_extraction'] = True
    content = json.dumps(receipt, ensure_ascii=False, indent=2) + '\n'
    if args.salida:
        with args.salida.open('x', encoding='utf-8') as output:
            output.write(content)
    print(content, end='')
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
