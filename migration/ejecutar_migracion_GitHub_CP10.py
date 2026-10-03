"""Transferencia y prueba remota de CP10; se ejecuta sólo en la rama auxiliar."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import zipfile
import zlib

REPO = 'diegolezaval/Proyecto_Runas'
REMOTE = 'https://github.com/' + REPO + '.git'
COMMIT = '47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81'
TREE = '15e40bba81afaf7c6b4a5be14dcf4bad4e2134bd'
ZIP = 'Proyecto_Runas_M2_4_2_CP10_MEDIADOR_ESPACIOTEMPORAL.zip'
BUNDLE = 'Proyecto_Runas_CP10_Git.bundle'
ZIP_SHA = 'c1b8b472f8d1f89c466fd5cb89470f63993ec73dedc9dac3896a88ffc2add4c1'
BUNDLE_SHA = 'fee9336fb2e314b0fe82b0b47935fa95d7c548cfa74ba4157592e961c1277278'
VERIFIER_SHA = 'd23ab572533fbe73e118ed30f200661307f46cd40cff29b92dba2a0cbe591f69'
TRANSPORT_TAG = 'cp10-transferencia'
TOOLS = Path(__file__).resolve().parent
GIT_AUTH = ['git', '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential']


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def run(command, cwd=None, capture=False, timeout=600):
    # El token nativo permanece en el entorno del runner; nunca en argumentos o recibos.
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=capture,
                            timeout=timeout, check=True)
    return result.stdout.strip() if capture else None


def git(root, *args):
    return run(['git', '-C', str(root), *args], capture=True, timeout=90)


def gh_json(*args):
    return json.loads(run(['gh', *args], capture=True, timeout=120))


def releases():
    return gh_json('api', 'repos/' + REPO + '/releases?per_page=100')


def download(tag, filename, destination):
    destination.mkdir(parents=True, exist_ok=True)
    run(['gh', 'release', 'download', tag, '--repo', REPO,
         '--pattern', filename, '--dir', str(destination)])
    return destination / filename


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    assert os.environ['GITHUB_REPOSITORY'] == REPO
    bootstrap = os.environ['CP10_BOOTSTRAP_COMMIT']
    assert len(bootstrap) == 40
    assert sha(TOOLS / 'verificar_clon_CP10.py') == VERIFIER_SHA
    repo = gh_json('api', 'repos/' + REPO)
    assert repo['private'] and repo['default_branch'] == 'main'
    # El commit de arranque se conserva en la rama auxiliar, incluso al sustituir main.
    run(['git', 'merge-base', '--is-ancestor', bootstrap, 'HEAD'], cwd=TOOLS.parent)
    transport = [r for r in releases() if r['tag_name'] == TRANSPORT_TAG]
    assert len(transport) == 1 and transport[0]['draft']

    with tempfile.TemporaryDirectory(prefix='cp10_migracion_remota_') as directory:
        work = Path(directory)
        archive = download(TRANSPORT_TAG, ZIP, work / 'entrada')
        bundle = download(TRANSPORT_TAG, BUNDLE, work / 'entrada')
        assert sha(archive) == ZIP_SHA and archive.stat().st_size == 81773782
        assert sha(bundle) == BUNDLE_SHA
        imported = work / 'importacion'
        run(['git', 'clone', '--branch', 'main', str(bundle), str(imported)])
        assert git(imported, 'rev-parse', 'HEAD') == COMMIT
        assert git(imported, 'rev-parse', 'HEAD^{tree}') == TREE
        assert git(imported, 'rev-parse', 'CP10^{commit}') == COMMIT
        tag_object = git(imported, 'rev-parse', 'CP10')
        run(['git', '-C', str(imported), 'bundle', 'verify', str(bundle)])
        with zipfile.ZipFile(archive) as source:
            assert source.testzip() is None
            expected = {name.removeprefix('Proyecto_Runas/'): hashlib.sha256(source.read(name)).hexdigest()
                        for name in source.namelist()}
        assert len(expected) == 938
        assert set(git(imported, 'ls-files', '-z').split('\0')) - {''} == set(expected)
        assert all(sha(imported / name) == digest for name, digest in expected.items())
        assert not git(imported, 'status', '--porcelain')
        run([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check',
             '-r', str(imported / 'requirements.txt')])
        git(imported, 'remote', 'set-url', 'origin', REMOTE)
        refs = run(GIT_AUTH + ['ls-remote', REMOTE, 'refs/heads/main', 'refs/tags/CP10',
                              'refs/tags/CP10^{}'], capture=True)
        refs = {line.split('\t')[1]: line.split('\t')[0] for line in refs.splitlines()}
        if refs.get('refs/heads/main') == bootstrap:
            assert 'refs/tags/CP10' not in refs, 'No sustituir un tag CP10 preexistente'
            run(GIT_AUTH + ['-C', str(imported), 'push', '--atomic',
                           '--force-with-lease=refs/heads/main:' + bootstrap,
                           'origin', 'refs/heads/main:refs/heads/main', 'refs/tags/CP10:refs/tags/CP10'])
        else:
            assert refs.get('refs/heads/main') == COMMIT, 'main ha cambiado: detener sin sobrescribirlo'
            assert refs.get('refs/tags/CP10') == tag_object
            assert refs.get('refs/tags/CP10^{}') == COMMIT

        # Clon real de GitHub, en una carpeta nueva; jamás se reutiliza la importación del bundle.
        clone = work / 'clon_GitHub'
        run(GIT_AUTH + ['clone', '--branch', 'main', REMOTE, str(clone)])
        assert git(clone, 'rev-parse', 'HEAD') == COMMIT
        assert git(clone, 'rev-parse', 'CP10') == tag_object
        proof = work / 'Comprobacion_clon_GitHub_CP10.json'
        run([sys.executable, str(TOOLS / 'verificar_clon_CP10.py'), '--clon', str(clone),
             '--zip', str(archive), '--salida', str(proof), '--origen', 'github'], timeout=600)
        verified = json.loads(proof.read_text())
        assert verified['passed'] and verified['remote_clone_verified']
        assert verified['commit'] == COMMIT and verified['payload_files'] == 938

        current = [r for r in releases() if r['tag_name'] == 'CP10']
        assert not current, 'Una Release CP10 ya existe: revisar su estado antes de modificarla'
        run(['gh', 'release', 'create', 'CP10', str(archive), str(proof),
             str(TOOLS / 'verificar_clon_CP10.py'), '--repo', REPO, '--verify-tag', '--draft',
             '--target', COMMIT, '--title', 'CP10 · Mediador espaciotemporal',
             '--notes-file', str(TOOLS / 'notas_release_CP10.md')])
        uploaded = download('CP10', ZIP, work / 'prueba_borrador')
        assert sha(uploaded) == ZIP_SHA
        run(['gh', 'release', 'edit', 'CP10', '--repo', REPO, '--draft=false'])
        published = download('CP10', ZIP, work / 'prueba_publicada')
        assert sha(published) == ZIP_SHA and published.stat().st_size == 81773782
        release = gh_json('release', 'view', 'CP10', '--repo', REPO,
                          '--json', 'url,tagName,isDraft,assets,publishedAt')
        assert release['tagName'] == 'CP10' and not release['isDraft']
        final_refs = run(GIT_AUTH + ['ls-remote', REMOTE, 'refs/heads/main',
                                    'refs/tags/CP10', 'refs/tags/CP10^{}'], capture=True)
        final_refs = {line.split('\t')[1]: line.split('\t')[0] for line in final_refs.splitlines()}
        assert final_refs['refs/heads/main'] == final_refs['refs/tags/CP10^{}'] == COMMIT
        assert final_refs['refs/tags/CP10'] == tag_object
        assert gh_json('api', 'repos/' + REPO)['private']
        record = {
            'schema_version': 1, 'migration_status': 'MIGRACION_CP10_VERIFICADA',
            'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'repository_url': 'https://github.com/' + REPO, 'visibility': 'private',
            'branch': 'main', 'commit': COMMIT, 'tree': TREE, 'tag': 'CP10',
            'annotated_tag_object': tag_object, 'tag_commit': COMMIT,
            'github_clone_command': 'git clone --branch main ' + REMOTE + ' <carpeta_nueva>',
            'remote_clone_verified': True, 'payload_files': 938,
            'all_payload_bytes_preserved': True, 'scientific_checks_passed': True,
            'deterministic_checkpoint_zip_reproduced': True,
            'original_zip': {'filename': ZIP, 'size_bytes': 81773782, 'sha256': ZIP_SHA},
            'release_url': release['url'], 'release_published': True,
            'release_download_sha256_verified': True,
            'release_download_size_bytes': published.stat().st_size,
            'proof_filename': proof.name, 'proof_sha256': sha(proof),
            'verifier_sha256': VERIFIER_SHA, 'transport_bundle_sha256': BUNDLE_SHA,
            'science_modified': False, 'project_reorganized': False, 'CP11_started': False,
            'file_migration_map': [],
            'auxiliary_branch': 'migration/cp10', 'bootstrap_commit_preserved': bootstrap,
            'transport_release': {'tag': TRANSPORT_TAG, 'draft': True},
            'workflow_run_url': 'https://github.com/' + REPO + '/actions/runs/' + os.environ['GITHUB_RUN_ID'],
            'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                            'zlib': zlib.ZLIB_RUNTIME_VERSION},
            'authentication': 'Token nativo efímero de GitHub Actions; limitado a contents:write del repositorio',
        }
        act = work / 'Acta_migracion_GitHub_CP10.json'
        write_json(act, record)
        run(['gh', 'release', 'upload', 'CP10', str(act), '--repo', REPO])
        downloaded_act = download('CP10', act.name, work / 'prueba_acta')
        assert sha(downloaded_act) == sha(act)
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as summary:
            summary.write('CP10 migrado y verificado.\n\n')
            summary.write('- Repositorio privado; main y tag CP10: `' + COMMIT + '`.\n')
            summary.write('- Clon limpio de GitHub: 938 archivos y comprobaciones científicas correctos.\n')
            summary.write('- ZIP regenerado y ZIP descargado de la Release: SHA-256 original idéntico.\n')
            summary.write('- Sin cambios científicos, movimientos de archivos ni CP11.\n')
        print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
