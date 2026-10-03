"""Ensayo Git aislado: índice y checkout exactos; nunca migra el proyecto."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from checkpoint import files, digest

ROOT = Path(__file__).resolve().parents[1]


def verify():
    baseline = {p.relative_to(ROOT).as_posix(): digest(p) for p in files()}
    env = os.environ.copy()
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    # A caller's repository variables must not redirect the temporary test.
    for key in ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES']:
        env.pop(key, None)
    with tempfile.TemporaryDirectory(prefix='runica_git_preparacion_') as t:
        work, checkout = Path(t)/'indice', Path(t)/'checkout'
        work.mkdir(); checkout.mkdir()
        for name in baseline:
            target = work/name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)
        def git(*arguments):
            r = subprocess.run(['git', *arguments], cwd=work, env=env, text=True,
                               capture_output=True, timeout=60)
            if r.returncode:
                raise ValueError('Git fixture: '+r.stderr)
            return r.stdout
        git('init', '-q')
        git('config', 'core.autocrlf', 'true')
        transient = ['__pycache__/prueba.pyc', '.venv/prueba',
                     'validacion/P06/no_radial/cache/prueba.so',
                     'validacion/P06/no_radial/ejecucion_prueba.lock',
                     'validacion/prueba_CP10.tmp', 'validacion/prueba_CP10.part']
        for name in transient:
            target = work/name; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'fixture transitoria')
        ignored = {name: bool(git('check-ignore', name).strip()) for name in transient}
        git('add', '-A')
        tracked = set(git('ls-files', '-z').split('\0')) - {''}
        git('checkout-index', '--all', '--prefix='+str(checkout)+'/')
        exact = {name: (checkout/name).is_file() and digest(checkout/name)==expected
                 for name, expected in baseline.items()}
        tests = dict(payload_exactly_tracked=tracked==set(baseline),
                     all_checkout_bytes_exact_even_autocrlf_true=all(exact.values()),
                     transient_fixtures_ignored=all(ignored.values()),
                     all_NPZ_CSV_JSON_SVG_logs_and_history_ZIP_tracked=all(
                         name in tracked for name in baseline
                         if name.endswith(('.npz','.csv','.json','.svg','.log','.zip'))),
                     no_remote=not git('remote').strip(),
                     input_project_has_no_git_repository=not (ROOT/'.git').exists(),
                     input_corpus_unmodified=baseline=={p.relative_to(ROOT).as_posix():digest(p) for p in files()})
        return dict(passed=all(tests.values()), tests=tests, git_version=git('--version').strip(),
                    files_checked=len(baseline), ignored_fixtures=ignored,
                    migrations_performed=0, LFS_installed=False, published=False,
                    scope='Repositorio temporal: índice y checkout; no commit o remoto del proyecto, no campaña científica.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path)
    args=parser.parse_args()
    report=verify()
    if args.salida:
        args.salida.parent.mkdir(parents=True,exist_ok=True)
        args.salida.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['passed'] else 1)
