"""Instala guardas locales de main fuera del corpus científico; no modifica archivos registrados."""
from pathlib import Path
import argparse
import datetime
import json
import os
import subprocess

REPOSITORY = 'diegolezaval/Proyecto_Runas'
POLICY_URL = 'https://github.com/diegolezaval/Proyecto_Runas/blob/migration/cp10/gobernanza/POLITICA_MAIN.md'
ALLOWED_ORIGINS = {
    'https://github.com/diegolezaval/Proyecto_Runas.git',
    'git@github.com:diegolezaval/Proyecto_Runas.git',
}
PRE_COMMIT = '''#!/bin/sh
# Proyecto_Runas: guarda local de main; política publicada en la rama administrativa.
branch_ref=$(git symbolic-ref --quiet --short HEAD) || {
    printf '%s\\n' 'Commit bloqueado: crea una rama de trabajo; no registres ciencia en HEAD separado.' >&2
    exit 1
}
if [ "$branch_ref" = main ]; then
    printf '%s\\n' 'Commit bloqueado: main es estable. Crea una rama, verifica el trabajo y usa un Pull Request.' >&2
    exit 1
fi
exit 0
'''
PRE_PUSH = '''#!/bin/sh
# Rechaza actualizaciones, borrados y pushes forzados de main y del tag autoritativo CP10.
while read -r local_ref local_sha remote_ref remote_sha
do
    case "$remote_ref" in
        refs/heads/main)
            printf '%s\\n' 'Push bloqueado: main se actualiza únicamente mediante Pull Request en GitHub.' >&2
            exit 1
            ;;
        refs/tags/CP10)
            printf '%s\\n' 'Push bloqueado: el tag CP10 identifica el checkpoint autoritativo y debe conservarse.' >&2
            exit 1
            ;;
    esac
done
exit 0
'''


def git(root, *arguments, check=True):
    result = subprocess.run(['git', '-C', str(root), *arguments], text=True,
                            capture_output=True, check=check)
    return result


def install(repository):
    root = Path(git(repository, 'rev-parse', '--show-toplevel').stdout.strip()).resolve()
    origin = git(root, 'remote', 'get-url', 'origin').stdout.strip()
    if origin not in ALLOWED_ORIGINS:
        raise ValueError('El origen no corresponde a Proyecto_Runas; no se escriben hooks.')
    if git(root, 'config', '--get', 'core.hooksPath', check=False).returncode == 0:
        raise ValueError('Existe core.hooksPath personalizado. Revisar su integración antes de instalar.')
    before = git(root, 'status', '--porcelain').stdout
    hook_path = Path(git(root, 'rev-parse', '--git-path', 'hooks').stdout.strip())
    if not hook_path.is_absolute():
        hook_path = root / hook_path
    hook_path = hook_path.resolve()
    scripts = {'pre-commit': PRE_COMMIT, 'pre-push': PRE_PUSH}
    # Primero se comprueban ambos destinos; jamás se sustituyen hooks ajenos.
    for name, content in scripts.items():
        destination = hook_path / name
        if destination.is_symlink():
            raise ValueError('Hook enlazado existente: ' + name)
        if destination.exists() and destination.read_bytes() != content.encode('utf-8'):
            raise ValueError('Hook existente distinto: ' + name + '. Integrar explícitamente sin sobrescribirlo.')
    hook_path.mkdir(parents=True, exist_ok=True)
    for name, content in scripts.items():
        destination = hook_path / name
        if not destination.exists():
            with destination.open('xb') as stream:
                stream.write(content.encode('utf-8'))
        destination.chmod(0o755)
    assert git(root, 'status', '--porcelain').stdout == before
    record = {
        'schema_version': 1,
        'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'repository': REPOSITORY, 'policy_url': POLICY_URL,
        'installed_hooks': list(scripts), 'main_commits_blocked_locally': True,
        'main_pushes_blocked_locally': True, 'CP10_tag_pushes_blocked_locally': True,
        'scientific_worktree_unchanged': True,
        'server_enforcement': False,
        'scope': 'Sólo este clon; GitHub web/API y clientes sin estos hooks no quedan bloqueados.',
    }
    metadata_path = Path(git(root, 'rev-parse', '--git-path', 'proteccion-main.json').stdout.strip())
    if not metadata_path.is_absolute():
        metadata_path = root / metadata_path
    metadata_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repositorio', type=Path, default=Path('.'))
    args = parser.parse_args()
    try:
        install(args.repositorio.resolve())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')
