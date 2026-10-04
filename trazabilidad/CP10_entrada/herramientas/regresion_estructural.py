"""Regresión aislada sobre resultados guardados; nunca repite campañas.

Los verificadores históricos escriben sus salidas sólo en una copia temporal.
El corpus de entrada conserva todos sus bytes. --salida es una escritura
explícita del recibo administrativo, fuera de los resultados científicos.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from checkpoint import files, digest

ROOT = Path(__file__).resolve().parents[1]


def hashes(root):
    return {str(p.relative_to(root)): digest(p) for p in files(root)}


def run_suite():
    original = hashes(ROOT)
    state = json.loads((ROOT / 'estado_progreso.json').read_text())
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg')
    runs, tests = [], {}
    with tempfile.TemporaryDirectory(prefix='runica_regresion_') as temporary:
        work = Path(temporary)
        clone = work / 'Proyecto_Runas'
        for relative in original:
            target = clone / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        def execute(arguments, expected=0):
            before = hashes(clone)
            result = subprocess.run([sys.executable, str(clone / 'herramientas' / arguments[0]), *arguments[1:]],
                                    cwd=work, env=env, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=60)
            after = hashes(clone)
            output = result.stdout.replace(str(clone), '<Proyecto_Runas>').replace(str(work), '<copia_temporal>')
            record = dict(command=arguments, returncode=result.returncode, expected_returncode=expected,
                          passed=result.returncode == expected,
                          changed_files=sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)),
                          output=output)
            runs.append(record)
            return record
        if state.get('scientific_checkpoint', '').startswith('CP10'):
            for args in [['verificar_CP10.py'], ['generar_resumen_CP10.py', '--comprobar'], ['probar_procedencia_futura.py']]:
                execute(args)
        for args in [
            ['verificar_entorno.py', '--cp10' if state.get('scientific_checkpoint', '').startswith('CP10') else '--adaptativo'],
            ['generar_continuidad.py', '--comprobar'],
            (['auditar_arquitectura.py', '--conservacion-cp08'] if state['checkpoint'] == 'CP09_AUDITORIA_ARQUITECTURA' else ['auditar_arquitectura.py']),
            ['verificar_continuidad.py', '--solo-lectura'],
            ['verificar.py'], ['verificar_m2.py'], ['verificar_capilaridad.py'],
            ['verificar_campana_4_2.py'], ['verificar_preparacion_m2.py'],
            ['verificar_no_radial_m2.py'], ['puerta_acceso_lineal_m2.py'], ['generar.py']]:
            execute(args)
        first = hashes(clone)
        execute(['generar.py'])
        tests['geometry_views_idempotent'] = first == hashes(clone)
        # Detect current broken links while preserving declared historical contexts.
        readme = clone / 'LEEME.md'
        content = readme.read_bytes()
        readme.write_bytes(content + b'\n[enlace de prueba](archivo_ausente_de_prueba.md)\n')
        broken = execute(['verificar_continuidad.py', '--solo-lectura'], expected=1)
        tests['broken_current_link_detected'] = broken['passed'] and 'archivo_ausente_de_prueba' in broken['output']
        readme.write_bytes(content)
        # Check exclusions and refusal of unfinished state writes without packaging physics.
        for relative in ['.git/objects/prueba', '.venv/cache/prueba',
                         'validacion/P06/no_radial/cache/sub/force.so',
                         'validacion/P06/no_radial/ejecucion_prueba.lock']:
            target = clone / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'artefacto de ejecucion')
        (clone / 'uv.lock').write_text('# dependency lock fixture\n')
        code = "import sys,json;sys.path.insert(0,sys.argv[1]);from checkpoint import files;from pathlib import Path;r=Path(sys.argv[2]);print(json.dumps([str(p.relative_to(r)) for p in files(r)]))"
        call = subprocess.run([sys.executable, '-c', code, str(clone / 'herramientas'), str(clone)], cwd=work, env=env, text=True, capture_output=True, timeout=20)
        paths = json.loads(call.stdout) if call.returncode == 0 else []
        tests['recursive_execution_exclusions'] = bool(paths) and not any('/cache/' in p or p.startswith(('.git/', '.venv/')) or (p.startswith('validacion/P06/no_radial/ejecucion_') and p.endswith('.lock')) for p in paths)
        tests['dependency_lockfiles_not_ignored'] = 'uv.lock' in paths
        tests['scientific_states_not_ignored'] = len([p for p in paths if p.endswith('.npz')]) == len([p for p in original if p.endswith('.npz')])
        unfinished = clone / 'validacion/P06/no_radial/prueba_estado.tmp'
        unfinished.write_bytes(b'escritura incompleta')
        rejected = subprocess.run([sys.executable, '-c', code, str(clone / 'herramientas'), str(clone)], cwd=work, env=env, text=True, capture_output=True, timeout=20)
        tests['unfinished_scientific_write_rejected'] = rejected.returncode != 0 and 'Temporal científico pendiente' in rejected.stderr
        unfinished.unlink()
        external = work / 'external_payload'
        external.mkdir()
        (external / 'unlisted.dat').write_bytes(b'undeclared data')
        symlink = clone / 'validacion/externo_de_prueba'
        symlink.symlink_to(external, target_is_directory=True)
        symlink_result = subprocess.run([sys.executable, '-c', code, str(clone / 'herramientas'), str(clone)], cwd=work, env=env, text=True, capture_output=True, timeout=20)
        tests['undeclared_directory_symlink_rejected'] = symlink_result.returncode != 0 and 'Directorio científico enlazado' in symlink_result.stderr
        symlink.unlink()
        # Reuse a finished adaptive state: no force evaluation/evolution occurs.
        command = ['continuar_no_radial_adaptativo.py', '--dx', '.125', '--rtol', '1e-9', '--atol', '1e-11', '--max-step', '.02', '--L', '4', '--radius', '220', '--eps', '.02', '--tmax', '160']
        reused = execute(command)
        tests['finished_adaptive_run_reused'] = reused['passed'] and 'REUTILIZADO' in reused['output'] and not reused['changed_files']
        changed = list(command)
        changed[changed.index('--atol') + 1] = '1e-10'
        refused = execute(changed, expected=1)
        tests['same_destination_different_configuration_rejected'] = refused['passed'] and not refused['changed_files']
        lock_code = "import sys,tempfile,fcntl,json;sys.path.insert(0,sys.argv[1]);from continuar_no_radial_adaptativo import destination_tag;c=dict(dx=.125,rtol=1e-9,atol=1e-11,max_step=.02,L=4,radius=220.,eps=.02,tmax=160.);d=dict(c,atol=1e-10);print(json.dumps({'same_destination':destination_tag(**c)==destination_tag(**d),'destination_tag':destination_tag(**c)}))"
        lock_result = subprocess.run([sys.executable, '-c', lock_code, str(clone / 'herramientas')], cwd=work, env=env, text=True, capture_output=True, timeout=20)
        tests['colliding_tags_share_lock_identity'] = lock_result.returncode == 0 and json.loads(lock_result.stdout)['same_destination']
        import fcntl
        effective_tag = json.loads(lock_result.stdout)['destination_tag']
        lockfile = clone / 'validacion/P06/no_radial' / ('ejecucion_' + hashlib.sha256(effective_tag.encode()).hexdigest()[:16] + '.lock')
        with lockfile.open('a+') as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            blocked = execute(command, expected=1)
            tests['second_live_writer_rejected'] = blocked['passed'] and 'already has a live writer' in blocked['output'] and not blocked['changed_files']
        # A declared failed artifact never masks a changed/corrupt payload.
        known_bad = clone / 'validacion/P06/acceso_lineal/colocacion_Om5.0000_estado.npz'
        old_bad = known_bad.read_bytes()
        known_bad.write_bytes(b'corruption introduced by structural test')
        state_code = "import sys,json;sys.path.insert(0,sys.argv[1]);from auditar_arquitectura import inspect_states;rows,issues=inspect_states();print(json.dumps(issues))"
        state_result = subprocess.run([sys.executable, '-c', state_code, str(clone / 'herramientas')], cwd=work, env=env, text=True, capture_output=True, timeout=20)
        tests['historical_bad_state_exception_bound_to_hash'] = state_result.returncode == 0 and any('unexpected_unreadable_state' in x for x in json.loads(state_result.stdout))
        known_bad.write_bytes(old_bad)
        # AST comparison excludes only the destination-tag expression, never equations.
        archived = ROOT / 'trazabilidad/CP08_arquitectura_entrada/herramientas/continuar_no_radial_adaptativo.py'
        def numerical_body(path):
            tree = ast.parse(path.read_text())
            function = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'run')
            for node in ast.walk(function):
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'tag' for t in node.targets):
                    node.value = ast.Constant(value='DESTINATION_IDENTITY_ONLY')
            return ast.dump(function, include_attributes=False)
        if state['checkpoint'] == 'CP09_AUDITORIA_ARQUITECTURA':
            tests['adaptive_numerical_body_unchanged'] = numerical_body(archived) == numerical_body(ROOT / 'herramientas/continuar_no_radial_adaptativo.py')
        # Reconstruct all original files of CP08 from current bytes plus snapshots.
        baseline = json.loads((ROOT / 'trazabilidad/arquitectura/archivos_CP08.json').read_text())
        recovered = work / 'CP08' / 'Proyecto_Runas'
        okay = True
        for relative, expected in baseline.items():
            source = ROOT / relative
            if digest(source) != expected:
                candidates = [x for x in (ROOT / 'trazabilidad').rglob(relative) if x.is_file() and digest(x) == expected]
                if not candidates:
                    raise ValueError('Original CP08 no recuperable: ' + relative)
                source = candidates[0]
            target = recovered / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            okay = okay and digest(target) == expected
        old = subprocess.run([sys.executable, str(recovered / 'herramientas/checkpoint.py'), '--verificar'], cwd=work, env=env, text=True, capture_output=True, timeout=30)
        tests['original_CP08_reconstructed_786_files'] = okay and len(baseline) == 786 and old.returncode == 0
        final = hashes(clone)
        tests['saved_CSV_NPZ_unchanged'] = all(final.get(k) == v for k, v in original.items() if k.endswith(('.csv', '.npz')))
    tests['input_corpus_unmodified'] = hashes(ROOT) == original
    return dict(checkpoint=state['checkpoint'], passed=all(r['passed'] for r in runs) and all(tests.values()),
                numerical_campaigns_executed=False, tests=tests, runs=runs,
                scope='Verificaciones de datos guardados, generación y controles estructurales en copia temporal. Una puerta científica negativa sigue siendo negativa.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, help='Guardar recibo administrativo sin modificar resultados de campañas')
    args = parser.parse_args()
    result = run_suite()
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'runs'}, ensure_ascii=False, indent=2))
    if not result['passed']:
        print(json.dumps([dict(command=x['command'], output=x['output']) for x in result['runs'] if not x['passed']], ensure_ascii=False, indent=2))
        raise SystemExit(1)
