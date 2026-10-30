"""Verifica o empaqueta el corpus completo, sin ejecutar ciencia."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import zipfile

R = Path(__file__).resolve().parents[1]
TRANSIENT_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
CACHE = 'validacion/P06/no_radial/cache'
EXCLUDED = ['MANIFIESTO_SHA256.json', '**/.git/**', '**/.venv/**', '**/venv/**', '**/__pycache__/**', '**/.pytest_cache/**', '**/.mypy_cache/**', '**/.ruff_cache/**', '**/*.pyc', '**/*.pyo', 'validacion/P06/no_radial/ejecucion_*.lock', CACHE + '/**']


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def files(root=R):
    payload = []
    for parent, dirs, names in os.walk(root):
        folder = Path(parent)
        for d in dirs:
            if d not in TRANSIENT_DIRS and (folder / d).is_symlink():
                raise ValueError('Directorio científico enlazado fuera del payload: ' + str((folder / d).relative_to(root)))
        dirs[:] = sorted(d for d in dirs if d not in TRANSIENT_DIRS and (folder / d).relative_to(root).as_posix() != CACHE)
        for name in sorted(names):
            path = folder / name
            if path.suffix in ['.pyc', '.pyo']:
                continue
            if path.parent == root / 'validacion/P06/no_radial' and path.name.startswith('ejecucion_') and path.suffix == '.lock':
                continue
            if path.is_symlink():
                raise ValueError('No se empaquetan enlaces simbólicos: ' + str(path.relative_to(root)))
            if path.suffix in ['.tmp', '.part'] and path.is_relative_to(root / 'validacion'):
                raise ValueError('Temporal científico pendiente; revisar el último estado válido: ' + str(path.relative_to(root)))
            payload.append(path)
    return sorted(payload)


def validate_context():
    state = json.loads((R / 'estado_progreso.json').read_text(encoding='utf-8'))
    versions = json.loads((R / 'VERSIONES.json').read_text(encoding='utf-8'))
    if versions['project'] != state['project_version'] or versions['fundamental_model'] != state['model_version']:
        raise ValueError('VERSIONES y progreso no coinciden')
    if digest(R / 'trazabilidad/fuente_M2_4_1.zip') != state['baseline_sha256']:
        raise ValueError('Fuente histórica 4.1 alterada')
    original = json.loads((R / 'hoja_ruta_original/MANIFIESTO_SHA256.json').read_text())['files']
    if any(not (R / 'hoja_ruta_original' / k).is_file() or digest(R / 'hoja_ruta_original' / k) != v for k, v in original.items()):
        raise ValueError('Hoja de ruta original alterada o incompleta')
    seen = set()
    for stage in state['stages']:
        if stage['id'] in seen or stage['status'] not in state['allowed_statuses']:
            raise ValueError('Identidad/estado de etapa inválido: ' + stage['id'])
        seen.add(stage['id'])
        if stage['status'] == 'COMPLETADA' and not all(stage.get(k) for k in ['evidence', 'checkpoint', 'reopen_conditions']):
            raise ValueError('Cierre incompleto: ' + stage['id'])
        if any(not (R / e).is_file() for e in stage['evidence']):
            raise ValueError('Falta evidencia de etapa: ' + stage['id'])
    return state


def verify():
    state = validate_context()
    manifest = R / 'MANIFIESTO_SHA256.json'
    data = json.loads(manifest.read_text(encoding='utf-8'))
    expected = data['files']
    actual = {p.relative_to(R).as_posix(): digest(p) for p in files() if p != manifest}
    bad = sorted(k for k in set(expected) | set(actual) if expected.get(k) != actual.get(k))
    if data['edition'] != state['project_version'] or data['checkpoint'] != state['checkpoint']:
        bad.append('identidad_administrativa_del_manifiesto')
    result = dict(passed=not bad, files=len(actual), failures=bad, checkpoint=state['checkpoint'], scope='Identidad de bytes y contexto; no aceptación científica.')
    if bad:
        raise ValueError(json.dumps(result, ensure_ascii=False))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--salida', type=Path)
    group.add_argument('--verificar', action='store_true')
    parser.add_argument('--estados-salida', type=Path, help='ZIP complementario de acceso lineal; extraer ambos en la misma carpeta')
    args = parser.parse_args()
    try:
        if args.verificar:
            if args.estados_salida:
                parser.error('--estados-salida requiere --salida')
            print(json.dumps(verify(), ensure_ascii=False))
            return
        outputs = [args.salida] + ([args.estados_salida] if args.estados_salida else [])
        if any(p.resolve().is_relative_to(R) for p in outputs):
            raise ValueError('Los ZIP deben quedar fuera del proyecto')
        if len(set(p.resolve() for p in outputs)) != len(outputs):
            raise ValueError('Los ZIP deben tener destinos distintos')
        state = validate_context()
        manifest = R / 'MANIFIESTO_SHA256.json'
        hashes = {p.relative_to(R).as_posix(): digest(p) for p in files() if p != manifest}
        data = dict(algorithm='SHA256', edition=state['project_version'], checkpoint=state['checkpoint'], scientific_checkpoint=state.get('scientific_checkpoint', state['checkpoint']), excluded=EXCLUDED, files=hashes)
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        payload = files()
        def separate(p):
            return bool(args.estados_salida and p.parent == R / 'validacion/P06/acceso_lineal' and p.name.endswith('_estado.npz'))
        groups = [(args.salida, [p for p in payload if not separate(p)])]
        if args.estados_salida:
            groups.append((args.estados_salida, [p for p in payload if separate(p)]))
        receipts = []
        names = set()
        for output, entries in groups:
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(output.name + '.tmp')
            try:
                with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                    for p in entries:
                        content = p.read_bytes()
                        relative = p.relative_to(R).as_posix()
                        expected = digest(manifest) if p == manifest else hashes[relative]
                        if hashlib.sha256(content).hexdigest() != expected:
                            raise ValueError('Archivo cambió durante empaquetado: ' + relative)
                        name = 'Proyecto_Runas/' + relative
                        info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                        info.compress_type = zipfile.ZIP_DEFLATED
                        info.external_attr = 0o100644 << 16
                        z.writestr(info, content, compresslevel=9)
                with zipfile.ZipFile(temporary) as z:
                    if z.testzip() is not None:
                        raise ValueError('CRC de ZIP fallido')
                    for name in z.namelist():
                        if name in names:
                            raise ValueError('Colisión entre paquetes: ' + name)
                        names.add(name)
                verify()
                temporary.replace(output)
            finally:
                if temporary.exists():
                    temporary.unlink()
            receipts.append(dict(path=str(output.resolve()), bytes=output.stat().st_size, sha256=digest(output), files=len(entries)))
        if names != {'Proyecto_Runas/' + p.relative_to(R).as_posix() for p in payload}:
            raise ValueError('Cobertura incompleta de los paquetes')
        print(json.dumps(dict(archives=receipts, checkpoint=state['checkpoint'], combined_files=len(names), combined_integrity_passed=True, extraction='Extraer todos los ZIP complementarios en la misma carpeta.'), ensure_ascii=False))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        print(json.dumps(dict(passed=False, error=str(error)), ensure_ascii=False))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
