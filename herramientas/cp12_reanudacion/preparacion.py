"""Preparar el entorno original y auditar cápsulas sin evolución."""

import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import uuid
import zipfile

from .evidencia import checked_audits, zero
from .infra import (AUDITOR, COMPARE, HYBRID, Stop, digest, encoded, install, module, optional,
                    record, require, sha)

COMPILER_REGISTRY = 'trazabilidad/continuidad_20261104/RESTAURACION_COMPILADOR.json'
COMPILER_PROOF = 'trazabilidad/cierre_auditorias_20261104/COMPILADOR_PUBLICO.json'
COMPILER_SCRIPT = 'herramientas/restaurar_compilador_p3.py'


def log_command(command, log, env):
    result = subprocess.run(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    install(log.with_suffix('.stdout'), result.stdout)
    install(log.with_suffix('.stderr'), result.stderr)
    require(result.returncode == 0, f'Falló {Path(command[1]).name}. Ver {log.with_suffix(".stderr")}')
    return result.stdout


def snapshots(git, plan, work, helpers, *, historical=False):
    reg = plan.registry
    expected = {AUDITOR: reg['original_auditor_sha256']}
    require({'base_preservar.py', 'preservar.py', 'continuar.py', 'POLITICA.json'}
            <= set(reg['administrative_sources']), 'Registro de fuentes administrativas incompleto')
    for name, checksum in reg['administrative_sources'].items():
        require(re.fullmatch(r'[a-zA-Z0-9_]+\.(py|json)', name), 'Nombre administrativo inválido')
        expected[HYBRID + '/' + name] = checksum
    comparator = git.get(plan.head, COMPARE, missing=historical and reg['kind'] == 'boundary')
    if comparator is not None:
        expected[COMPARE] = (reg['public_capacity_comparator_sha256'] if reg['kind'] == 'transport'
                             else digest(comparator))
    if reg['kind'] == 'transport':
        require(reg['capacity_mode'] == 'CP12_P3_HYBRID_SPLIT_CAPACITY_V1' and
                {'continuar_desde_transporte.py', 'capacidad_separada.py'} <= set(reg['administrative_sources']),
                'Falta el adaptador registrado de capacidad separada')
        ref = reg['public_capacity_reference']
        require(all(ref[key] == plan.frontier[key] for key in
                    ('kind', 'observer_clock', 'file_name', 'bytes', 'sha256', 'github_asset_id')),
                'La asignación fija una referencia pública distinta de la vigente')
        require(digest(git.get(plan.head, reg['capacity_amendment'])) == reg['capacity_amendment_sha256'],
                'Enmienda de capacidad distinta')
    names = ('library_file_transfer.py', 'library_upload.py', 'library_hosted_apps.py')
    require(set(reg['helper_sha256']) == set(names), 'Registro de ayudantes distinto')
    for name in names:
        if not (helpers / name).is_file() or sha(helpers / name) != reg['helper_sha256'][name]:
            raise Stop('ENTORNO_AYUDANTES', 'Falta el ayudante registrado o difiere su SHA256',
                       'Proporcionar el directorio --helpers con las versiones registradas', file=name)
    root = work / 'codigo' / plan.registry_sha
    for relative, checksum in expected.items():
        data = git.get(plan.head, relative)
        require(digest(data) == checksum, f'SHA256 del código publicado distinto: {relative}')
        install(root / relative, data, once=True)
    return root


def environment(git, plan, destinations, assets, work):
    require(not sys.flags.optimize and not os.environ.get('OPENBLAS_CORETYPE'),
            'Entorno incompatible: comprobaciones deshabilitadas o arquitectura BLAS forzada')
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    # Los auditores originales comparan la identidad científica completa y la arquitectura BLAS.
    dependencies = git.get(plan.head, 'requirements.txt').decode().splitlines()
    versions = {name: importlib.metadata.version(name) for name, _ in
                (line.split('==', 1) for line in dependencies if '==' in line)}
    require(all(f'{name}=={version}' in dependencies for name, version in versions.items()),
            'Las versiones de requirements.txt no coinciden')
    scipy = Path(importlib.util.find_spec('scipy').origin).parent
    solver = {name + '_sha256': sha(scipy / 'integrate/_ivp' / (name + '.py')) for name in ('rk', 'base')}
    solver['version'] = versions['scipy']
    registered = plan.frontier_receipt['original_audits']['boundary']['DOP853_implementation_identity']
    require(solver == registered, 'La versión o el código DOP853 difieren del recibo original')

    expected = git.json(plan.head, COMPILER_REGISTRY)
    tool = shutil.which('cc')
    if not tool or sha(tool) != expected['compiler_real_sha256']:
        proof = git.json(plan.head, COMPILER_PROOF)
        prefix = work / 'compilador' / proof['sha256']
        compiler = prefix / 'bin/cc'
        if not compiler.is_file():
            require(proof['passed'] is True and proof['all_packages_verified'] == expected['packages'],
                    'Recibo de compilador distinto')
            matches = [x for x in assets if x['id'] == proof['github_asset_id']]
            require(len(matches) == 1, 'Falta el adjunto registrado del compilador')
            archive = destinations.archive(dict(proof, file_name=matches[0]['name']), public=matches[0])
            recovery = work / 'compilador' / ('preparar-' + uuid.uuid4().hex)
            recovery.mkdir(parents=True)
            checkout = recovery / 'codigo'
            for relative in (COMPILER_SCRIPT, COMPILER_REGISTRY):
                install(checkout / relative, git.get(plan.head, relative))
            debs = recovery / 'paquetes'
            debs.mkdir()
            with destinations.timings.measure('auditoria', 'Restaurar compilador original'):
                with zipfile.ZipFile(archive) as zipped:
                    for entry in expected['packages']:
                        name = entry['name']
                        require(Path(name).name == name, 'Ruta de paquete inválida')
                        with zipped.open(name) as source, (debs / name).open('xb') as target:
                            shutil.copyfileobj(source, target)
                log_command([sys.executable, str(checkout / COMPILER_SCRIPT), '--destino',
                             str(recovery / 'prefijo'), '--paquetes-desde', str(debs)], recovery / 'restauracion', env)
                # El restaurador crea un enlace absoluto dentro de su prefijo.
                restored = recovery / 'prefijo'
                real = (restored / 'bin/cc').resolve().relative_to(restored)
                (restored / 'bin/cc').unlink()
                (restored / 'bin/cc').symlink_to(Path('..') / real)
                (restored / 'RECIBO.json').rename(restored / 'RECIBO_RESTAURACION.json')
                restored.rename(prefix)
        env['PATH'] = str(compiler.parent) + os.pathsep + env['PATH']
        tool = compiler
    require(sha(tool) == expected['compiler_real_sha256'] and
            subprocess.check_output([str(tool), '--version'], env=env, text=True).splitlines()[0] == expected['cc_version'],
            'El ejecutable o la versión del compilador difieren del registro')
    blas = json.loads(subprocess.check_output(
        [sys.executable, '-c', 'import json,numpy,scipy.linalg,threadpoolctl;'
         'print(json.dumps(threadpoolctl.threadpool_info()))'], env=env, timeout=30))
    require(blas and all(x['architecture'] == 'SkylakeX' and x['num_threads'] == 1 for x in blas),
            'La arquitectura BLAS o los hilos no coinciden con el entorno original')
    blas = [dict(architecture=x['architecture'], threads=x['num_threads'], sha256=sha(x['filepath']))
            for x in blas]
    distribution = {}
    for name in versions:
        metadata = importlib.metadata.distribution(name)
        distribution[name] = digest((metadata.read_text('RECORD') or '').encode())
    fingerprint = dict(python=platform.python_version(), executable_sha256=sha(sys.executable),
                       platform=platform.platform(), machine=platform.machine(),
                       packages=versions, distribution=distribution, blas=blas,
                       solver=solver, compiler_sha256=sha(tool))
    return env, fingerprint


def payloads(home, manifest):
    for name, metadata in manifest['files'].items():
        path = home / name
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == metadata['bytes'] and
                sha(path) == metadata['sha256'], f'Carga modificada: {name}')


def audit_archive(spec, archive, code, work, env, fingerprint, timings, *, capacity=False):
    auditor = module(code / AUDITOR, '_cp12_original_unpack')
    with timings.measure('auditoria', ('Capacidad ' if capacity else 'Origen ') + archive.name):
        identity = dict(spec=spec, environment=fingerprint, capacity=capacity, driver=sha(code / AUDITOR),
                        preservation=sha(code / HYBRID / 'base_preservar.py'), coordinator=sha(__file__))
        key = digest(encoded(identity))
        cache = work / 'auditorias' / key
        cached = optional(cache / 'RECIBO.json')
        reused = cached is not None
        if reused:
            require(cached['identity'] == identity, 'Recibo en caché de otra identidad')
        else:
            cache = cache.with_name(key + '-preparar-' + uuid.uuid4().hex)
        home = cache / 'home'
        if reused:
            with zipfile.ZipFile(archive) as zipped:
                inventory = zipped.read('MANIFIESTO_NEGATIVO.json')
            require((home / 'MANIFIESTO_NEGATIVO.json').read_bytes() == inventory,
                    'Inventario local distinto del respaldo')
            manifest = json.loads(inventory)
            payloads(home, manifest)
            audits = cached['original_audits']
        else:
            manifest = auditor.unpack(archive, home, spec['sha256'], spec['bytes'])
            # Se ejecuta el mismo lanzador de auditorías y la misma selección de scripts.
            require(spec['closed_boundary'] == int(spec['closed_boundary']), 'Frontera cerrada fraccionaria')
            runner = [sys.executable, '-c',
                      'import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);'
                      'from base_preservar import audit;print(json.dumps(audit(Path(sys.argv[2]),sys.argv[3],'
                      'int(sys.argv[4]),Path(sys.argv[5]))))',
                      str(code / HYBRID), str(home), spec['kind'], str(spec['closed_boundary']), str(cache / 'originales')]
            audits = json.loads(log_command(runner, cache / 'auditoria', env))
            payloads(home, manifest)
            require(sha(archive) == spec['sha256'], 'El archivo cambió durante la auditoría')
        require(manifest['kind'] == spec['kind'] and manifest['capacity_probe'] is capacity and
                manifest['observer_clock'] == spec['observer_clock'] and
                manifest['closed_boundary'] == spec['closed_boundary'] and
                len(manifest['files']) == spec['payload_files'], 'Manifiesto distinto del respaldo o control')
        checked_audits(audits, spec)
        if not reused:
            record(cache / 'RECIBO.json', dict(identity=identity, original_audits=audits,
                                              exact_manifest_coverage=True,
                                              all_payload_hashes_verified_before_and_after=True))
            stable = cache.with_name(key)
            cache.rename(stable)
            home = stable / 'home'
        return home, dict(path=str(home.parent / 'RECIBO.json'), reused=reused,
                          tests={name: len(value['tests']) for name, value in audits.items()},
                          M2_steps_executed=0, DOP853_construction_or_step_attempts=0)


def runner(code, reg):
    name = 'continuar_desde_transporte.py' if reg['kind'] == 'transport' else 'continuar.py'
    return code / HYBRID / name


def worker_args(home, registry, helpers, code, output, reference, reg):
    flags = ['--home', str(home), '--registro', str(registry), '--helpers', str(helpers),
             '--auditor', str(code / AUDITOR), '--salida', str(output)]
    if reg['kind'] == 'transport':
        flags.extend(['--referencia-publica', str(reference)])
    return flags


def restore_exact(plan, home, reference, code, helpers, work, env, fingerprint, timings):
    identity = dict(registry=plan.registry_sha, source=plan.origin['sha256'], reference=plan.frontier['sha256'],
                    env=fingerprint, archive_audit=str(home.parent))
    root = work / 'restauraciones' / digest(encoded(identity))
    done = root / 'resultado/RESTAURACION_EXACTA.json'
    reused = done.is_file()
    with timings.measure('auditoria', 'Restauración exacta --solo-auditar'):
        if not reused:
            root = root.with_name(root.name + '-preparar-' + uuid.uuid4().hex)
            registry = root / 'REGISTRO.json'
            install(registry, plan.registry_bytes)
            cmd = [sys.executable, str(runner(code, plan.registry)), *worker_args(
                   home, registry, helpers, code, root / 'resultado', reference, plan.registry), '--solo-auditar']
            log_command(cmd, root / 'ejecutor', env)
            done = root / 'resultado/RESTAURACION_EXACTA.json'
        value = json.loads(done.read_bytes())
        zero(value)
        require(value['clock'] == plan.origin['observer_clock'] and value['target'] == plan.registry['target'],
                'Restauración exacta de otro reloj o destino')
        if not reused:
            stable = root.with_name(digest(encoded(identity)))
            root.rename(stable)
            done = stable / 'resultado/RESTAURACION_EXACTA.json'
    return dict(path=str(done), reused=reused, **value)
