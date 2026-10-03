"""Ensaya las guardas con repositorios temporales locales; no contacta ni escribe GitHub."""
from pathlib import Path
import datetime
import importlib.util
import json
import os
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('guardas', BASE / 'instalar_guardas_main.py')
guardas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardas)


def run(root, *arguments, expected=0):
    result = subprocess.run(['git', '-C', str(root), *arguments], text=True,
                            capture_output=True, env=os.environ.copy())
    if expected == 0:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode != 0, 'Una operación prohibida fue aceptada: ' + repr(arguments)
    return result


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix='cp10_guardas_main_') as temporary:
        work = Path(temporary)
        repository = work / 'clon'
        remote = work / 'remoto.git'
        repository.mkdir()
        run(repository, 'init', '--initial-branch=main')
        run(repository, 'config', 'user.name', 'Ensayo local de guardas')
        run(repository, 'config', 'user.email', 'ensayo@example.invalid')
        run(repository, 'remote', 'add', 'origin', 'https://github.com/diegolezaval/Proyecto_Runas.git')
        source = repository / 'evidencia.txt'
        source.write_text('Evidencia inalterada.\n')
        run(repository, 'add', 'evidencia.txt')
        run(repository, 'commit', '-m', 'Base temporal del ensayo')
        baseline = run(repository, 'rev-parse', 'HEAD').stdout.strip()
        run(repository, 'tag', 'CP10')
        remote.mkdir()
        run(remote, 'init', '--bare', '--initial-branch=main')
        run(repository, 'remote', 'add', 'ensayo', str(remote))
        # Se prepara el remoto local antes de instalar, sin emplear GitHub ni sus credenciales.
        run(repository, 'push', 'ensayo', 'main', 'CP10')
        guardas.install(repository)
        installed = {name: (repository / '.git/hooks' / name).read_bytes()
                     for name in ['pre-commit', 'pre-push']}
        guardas.install(repository)
        assert installed == {name: (repository / '.git/hooks' / name).read_bytes() for name in installed}
        checks.append('instalación idempotente y sin cambios de archivos registrados')
        run(repository, 'commit', '--allow-empty', '-m', 'Commit prohibido en main', expected=1)
        assert run(repository, 'rev-parse', 'HEAD').stdout.strip() == baseline
        checks.append('commit real en main rechazado')
        run(repository, 'switch', '--create', 'ciencia/ensayo-local')
        source.write_text('Evidencia nueva del ensayo local.\n')
        run(repository, 'add', 'evidencia.txt')
        run(repository, 'commit', '-m', 'Trabajo permitido en una rama separada')
        head = run(repository, 'rev-parse', 'HEAD').stdout.strip()
        checks.append('commit real en rama de trabajo permitido')
        run(repository, 'push', 'ensayo', 'HEAD:refs/heads/main', expected=1)
        assert run(remote, 'rev-parse', 'main').stdout.strip() == baseline
        checks.append('push a main desde otra rama rechazado sin alterar el remoto')
        run(repository, 'push', '--force', 'ensayo', 'HEAD:refs/heads/main', expected=1)
        assert run(remote, 'rev-parse', 'main').stdout.strip() == baseline
        checks.append('force push a main rechazado')
        run(repository, 'push', 'ensayo', ':refs/heads/main', expected=1)
        assert run(remote, 'rev-parse', 'main').stdout.strip() == baseline
        checks.append('borrado remoto de main rechazado')
        run(repository, 'push', '--force', 'ensayo', 'HEAD:refs/tags/CP10', expected=1)
        assert run(remote, 'rev-parse', 'CP10').stdout.strip() == baseline
        checks.append('sustitución del tag CP10 rechazada')
        run(repository, 'push', 'ensayo', ':refs/tags/CP10', expected=1)
        assert run(remote, 'rev-parse', 'CP10').stdout.strip() == baseline
        checks.append('borrado del tag CP10 rechazado')
        run(repository, 'push', 'ensayo', 'HEAD:refs/heads/ciencia/ensayo-local')
        assert run(remote, 'rev-parse', 'ciencia/ensayo-local').stdout.strip() == head
        checks.append('push de rama de trabajo permitido')
        run(repository, 'switch', '--detach', baseline)
        run(repository, 'commit', '--allow-empty', '-m', 'Commit prohibido fuera de una rama', expected=1)
        assert run(repository, 'rev-parse', 'HEAD').stdout.strip() == baseline
        checks.append('commit en HEAD separado rechazado')
        # Un hook ajeno debe conservarse íntegro y bloquear una reinstalación automática.
        custom = repository / '.git/hooks/pre-commit'
        custom.write_text('#!/bin/sh\n# Hook previo del usuario.\nexit 0\n')
        custom_bytes = custom.read_bytes()
        try:
            guardas.install(repository)
        except ValueError:
            pass
        else:
            raise AssertionError('El instalador sobrescribió un hook ajeno')
        assert custom.read_bytes() == custom_bytes
        checks.append('hook ajeno conservado; conflicto detectado')
    record = {'schema_version': 1, 'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'passed': True, 'checks': checks, 'check_count': len(checks),
              'actual_local_git_operations_tested': True, 'GitHub_writes_executed': False,
              'scientific_campaigns_executed': False, 'CP11_started': False}
    (BASE / 'Comprobacion_guardas_main.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
