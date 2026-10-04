"""Recibo previo, identidad completa y reanudación de campañas nuevas."""
from pathlib import Path
import argparse
import ast
import datetime
import fcntl
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / 'validacion/P06/no_radial/CP10'


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def closure(entrypoints):
    found = set()
    pending = list(entrypoints)
    while pending:
        path = pending.pop()
        if path in found:
            continue
        found.add(path)
        if path.suffix != '.py':
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            names = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            for name in names:
                candidate = ROOT / 'herramientas' / (name.split('.')[0] + '.py')
                if candidate.is_file() and candidate not in found:
                    pending.append(candidate)
    return sorted(found)


def environment():
    compiler = subprocess.run(['cc', '--version'], text=True, capture_output=True) if shutil.which('cc') else None
    return dict(python=platform.python_version(), system=platform.system(), architecture=platform.machine(),
                packages={n: importlib.metadata.version(n) for n in ['numpy', 'scipy', 'matplotlib', 'threadpoolctl']},
                compiler=compiler.stdout.splitlines()[0] if compiler and compiler.returncode == 0 else None,
                BLAS_threads=1, compiler_flags=['-O3', '-fPIC', '-shared', '-fno-fast-math'])


def prepare(protocol, case_name):
    data = json.loads(protocol.read_text())
    case = data['cases'][case_name]
    entry = ROOT / case['entrypoint']
    if entry.parent != ROOT / 'herramientas' or not entry.is_file():
        raise ValueError('Entrypoint fuera de herramientas')
    code = closure([entry, Path(__file__).resolve()] + [ROOT / p for p in case.get('extra_code', [])])
    inputs = {protocol, ROOT / 'datos/theta_comun.json', ROOT / data['initial_state']}
    for pattern in case['inputs']:
        matched = [p for p in ROOT.glob(pattern) if p.is_file()]
        if not matched:
            raise ValueError('Entrada ausente: ' + pattern)
        inputs.update(matched)
    source_hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(inputs)}
    code_hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in code}
    identity = dict(case=case, protocol=protocol.relative_to(ROOT).as_posix(), model=data['model'],
                    input_hashes=source_hashes, code_hashes=code_hashes, environment=environment())
    run_id = hashlib.sha256(canonical(identity)).hexdigest()
    return data, case, identity, run_id


def verify_receipt(path):
    receipt = json.loads(path.read_text())
    run = path.parent
    errors = []
    if hashlib.sha256(canonical(receipt['identity'])).hexdigest() != receipt['run_id']:
        errors.append('run_identity')
    for original, expected in {**receipt['identity']['input_hashes'], **receipt['identity']['code_hashes']}.items():
        actual_path = run / receipt['source_snapshots'][original] if original in receipt['source_snapshots'] else ROOT / original
        if not actual_path.is_file() or digest(actual_path) != expected:
            errors.append('source:' + original)
    for name, expected in receipt.get('output_hashes', {}).items():
        if not (run / name).is_file() or digest(run / name) != expected:
            errors.append('output:' + name)
    if receipt['status'] in ['COMPLETADA', 'PAUSADA_REANUDABLE']:
        present = {p.relative_to(run).as_posix() for p in run.rglob('*')
                   if p.is_file() and p != path and '__pycache__' not in p.parts and p.suffix != '.tmp'}
        if present != set(receipt['output_hashes']):
            errors.append('output_coverage')
    if receipt.get('configuration_sha256') != digest(run / 'configuration.json'):
        errors.append('configuration')
    return dict(passed=not errors, run_id=receipt['run_id'], status=receipt['status'], issues=errors,
                scope='Fuentes de ejecución capturadas y salidas; no aceptación científica.')


def execute(protocol, case_name, stop_at=None, resume=False):
    data, case, identity, run_id = prepare(protocol, case_name)
    run = CAMPAIGN / (case_name + '__' + run_id)
    lock_path = ROOT / ('validacion/P06/no_radial/ejecucion_prov_' + run_id + '.lock')
    with lock_path.open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run.mkdir(parents=True, exist_ok=True)
        receipt_path = run / 'procedencia.json'
        configuration = run / 'configuration.json'
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt['identity'] != identity:
                raise ValueError('Fuentes/configuración/entorno cambiaron')
            if receipt['status'] in ['COMPLETADA', 'PAUSADA_REANUDABLE']:
                if not verify_receipt(receipt_path)['passed']:
                    raise ValueError('Recibo o salida alterados')
            if receipt['status'] == 'COMPLETADA':
                print(json.dumps(dict(status='REUTILIZADO', run_id=run_id, receipt=receipt_path.relative_to(ROOT).as_posix())))
                return
            if receipt['status'] == 'FALLIDA':
                raise ValueError('Intento fallido conservado; no reanudar automáticamente')
            if not resume:
                raise ValueError('Reanudación requiere --reanudar y estado/configuración válidos')
        else:
            snapshots = {}
            for name in sorted(set(identity['code_hashes']) | set(identity['input_hashes'])):
                if name in identity['code_hashes'] or name in [identity['protocol'], 'datos/theta_comun.json']:
                    target = run / 'fuentes' / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / name, target)
                    snapshots[name] = target.relative_to(run).as_posix()
            write(configuration, dict(case=case, protocol=identity['protocol'], initial_state=data['initial_state']))
            receipt = dict(schema_version='1.0.0', run_id=run_id, case=case_name, identity=identity,
                           created_at=now(), status='REGISTRADA', configuration_sha256=digest(configuration),
                           source_snapshots=snapshots, segments=[], output_hashes={},
                           comparisons_and_decision='La puerta se registra en el resultado y el informe CP10; completar una ejecución no cierra una etapa.')
            write(receipt_path, receipt)
        command = [sys.executable, str(ROOT / case['entrypoint']), '--config', str(configuration), '--output-dir', str(run)]
        if stop_at is not None:
            command += ['--stop-at', str(stop_at)]
        restarts = {p.name: digest(p) for p in run.glob('*_estado.npz')}
        segment = dict(started_at=now(), command=[Path(sys.executable).name, case['entrypoint'], '--config', 'configuration.json', '--output-dir', '.'] + ([] if stop_at is None else ['--stop-at', str(stop_at)]),
                       resumed_from_hashes=restarts, status='EN_PROGRESO')
        receipt['segments'].append(segment)
        receipt['status'] = 'EN_PROGRESO'
        write(receipt_path, receipt)  # durable before the child starts
        try:
            with (run / 'ejecucion.log').open('a', buffering=1) as log:
                child = subprocess.Popen(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in child.stdout:
                    log.write(line)
                    print(line, end='', flush=True)
                returncode = child.wait()
            state_files = list(run.glob('*_progreso.json'))
            state = json.loads(state_files[0].read_text()) if state_files else {}
            receipt['status'] = 'FALLIDA' if returncode else 'PAUSADA_REANUDABLE' if state.get('status') == 'EN_PROGRESO' else 'COMPLETADA'
            segment.update(ended_at=now(), returncode=returncode, status=receipt['status'], final_time=state.get('time'))
            receipt['output_hashes'] = {p.relative_to(run).as_posix(): digest(p) for p in sorted(run.rglob('*'))
                                        if p.is_file() and p != receipt_path and '__pycache__' not in p.parts and p.suffix != '.tmp'}
            write(receipt_path, receipt)
            print(json.dumps(dict(run_id=run_id, status=receipt['status'], receipt=receipt_path.relative_to(ROOT).as_posix())), flush=True)
            if returncode:
                raise SystemExit(returncode)
        except (KeyboardInterrupt, OSError) as error:
            segment.update(interrupted_at=now(), status='INTERRUMPIDA', reason=str(error))
            receipt['status'] = 'INTERRUMPIDA'
            write(receipt_path, receipt)
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocolo', type=Path, default=Path('datos/ensayo_mediador_CP10.json'))
    parser.add_argument('--caso')
    parser.add_argument('--stop-at', type=float)
    parser.add_argument('--reanudar', action='store_true')
    parser.add_argument('--verificar', action='store_true')
    args = parser.parse_args()
    if args.verificar:
        results = [verify_receipt(p) for p in sorted(CAMPAIGN.glob('*/procedencia.json'))]
        print(json.dumps(dict(passed=bool(results) and all(r['passed'] for r in results), receipts=results), ensure_ascii=False, indent=2))
        raise SystemExit(0 if results and all(r['passed'] for r in results) else 1)
    if not args.caso:
        parser.error('--caso requerido')
    protocol = args.protocolo if args.protocolo.is_absolute() else ROOT / args.protocolo
    execute(protocol, args.caso, args.stop_at, args.reanudar)
