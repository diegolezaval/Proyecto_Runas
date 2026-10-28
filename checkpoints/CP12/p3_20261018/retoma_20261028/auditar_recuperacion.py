"""Recupera una cápsula P3 y ejecuta sus auditores originales sin pasos M2."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import sys
import zipfile


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '\\' in name or ':' in name or any(x in ('', '.', '..') for x in name.split('/')):
        raise ValueError(f'Ruta insegura: {name!r}')


def unpack(archive, home, expected_sha, expected_bytes):
    if home.exists():
        raise FileExistsError('Se exige una extracción nueva')
    if archive.stat().st_size != expected_bytes or sha(archive) != expected_sha:
        raise ValueError('Identidad del ZIP incorrecta')
    with zipfile.ZipFile(archive) as zipped:
        entries = zipped.infolist()
        names = [i.filename for i in entries]
        if len(names) != len(set(names)):
            raise ValueError('Entradas duplicadas')
        for item in entries:
            safe(item.filename)
            if item.is_dir() or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('Entrada ZIP no canónica')
        manifest = json.loads(zipped.read('MANIFIESTO_NEGATIVO.json'))
        if set(names) != set(manifest['files']) | {'MANIFIESTO_NEGATIVO.json'}:
            raise ValueError('Cobertura del manifiesto incorrecta')
        for name, metadata in manifest['files'].items():
            content = zipped.read(name)
            if len(content) != metadata['bytes'] or hashlib.sha256(content).hexdigest() != metadata['sha256']:
                raise ValueError(f'Bytes incorrectos: {name}')
        home.mkdir(parents=True)
        zipped.extractall(home)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archivo', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--bytes', type=int, required=True)
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    args.archivo = args.archivo.resolve()
    args.home = args.home.resolve()
    args.salida = args.salida.resolve()
    args.salida.mkdir(parents=True, exist_ok=False)
    report = dict(schema='CP12_P3_RELEASE_RECOVERY_ZERO_STEP_AUDIT_V1',
                  started_at_utc=datetime.now(timezone.utc).isoformat(),
                  archive_sha256=args.sha256, archive_bytes=args.bytes,
                  passed=False, M2_steps_executed=0, CP12_closed=False,
                  correction_validated=False, original_trajectories_repeated=False,
                  scope='Restauración y comprobaciones originales sin construir ni avanzar DOP853')
    try:
        manifest = unpack(args.archivo, args.home, args.sha256, args.bytes)
        for relative in ['runtime/tmp', 'runtime/pycache', 'analysis/lectura_prefijos_continuacion', 'negative']:
            (args.home / relative).mkdir(parents=True, exist_ok=True)
        environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                           PYTHONPYCACHEPREFIX=str(args.home / 'runtime/pycache'), TMPDIR=str(args.home / 'runtime/tmp'))
        if environment.get('OPENBLAS_CORETYPE'):
            raise ValueError('No se fuerza la arquitectura BLAS')
        results = {}
        report['audits'] = results
        for key, script, flags in [('boundary8', 'coordinator.py', ['--audit-only', '8']),
                                   ('transport', 'controlador_transporte.py', ['--audit-transport'])]:
            command = [sys.executable, str(args.home / script), '--home', str(args.home), *flags]
            process = subprocess.run(command, env=environment, capture_output=True, text=True)
            (args.salida / (key + '_stdout.json')).write_text(process.stdout)
            (args.salida / (key + '_stderr.txt')).write_text(process.stderr)
            results[key] = dict(returncode=process.returncode, stdout_sha256=sha(args.salida / (key + '_stdout.json')),
                                stderr_sha256=sha(args.salida / (key + '_stderr.txt')))
            if process.returncode != 0:
                raise RuntimeError(f'Auditor original {key} terminó con código {process.returncode}')
            value = json.loads(process.stdout)
            if not value['passed'] or value['M2_steps_executed'] != 0 or value['DOP853_construction_or_step_attempts'] != 0:
                raise ValueError(f'Auditor original {key} no superado sin pasos')
            results[key]['audit'] = value
            print(json.dumps(dict(completed=key, passed=True, tests=len(value['tests']), M2_steps_executed=0)), flush=True)
        unchanged = all((args.home / name).stat().st_size == meta['bytes'] and sha(args.home / name) == meta['sha256']
                        for name, meta in manifest['files'].items())
        if not unchanged or sha(args.archivo) != args.sha256:
            raise ValueError('La fuente o las cargas canónicas cambiaron durante la auditoría')
        report.update(passed=True, payload_files=len(manifest['files']),
                      all_payload_hashes_verified_before_and_after=True, source_archive_unchanged=True,
                      audits=results, python=platform.python_version(), platform=platform.system(),
                      architecture=platform.machine(), packages={n:importlib.metadata.version(n) for n in
                      ('numpy', 'scipy', 'matplotlib', 'threadpoolctl')},
                      audit_driver_sha256=sha(Path(__file__)))
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
    report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    (args.salida / 'RESULTADO.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(passed=report['passed'], error=report.get('error'), report=str(args.salida / 'RESULTADO.json'))), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
