"""Publica y verifica una cápsula sin otra acción del chat; no ejecuta M2.

Usa una instalación autenticada de GitHub CLI. No obtiene, imprime ni incorpora
tokens al ZIP. La autorización y una excepción científica nueva son requisitos
independientes; este programa no habilita una repetición del cálculo.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPOSITORY = 'diegolezaval/Proyecto_Runas'
TAG = 'respaldo-cp12-p3-20261027'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def gh(command, binary):
    environment = dict(os.environ)
    environment.pop('GH_DEBUG', None)
    environment['GH_PROMPT_DISABLED'] = '1'
    result = subprocess.run([binary, *command], capture_output=True, text=True, env=environment)
    if result.returncode:
        # El stderr de autenticación no se vuelca al registro científico.
        raise RuntimeError('GitHub CLI no completó la operación; no se autoriza física')
    return result.stdout


def preflight(binary):
    if not binary or not Path(binary).is_file():
        raise RuntimeError('GitHub CLI no está instalado en la ruta indicada')
    gh(['auth', 'status', '--hostname', 'github.com'], binary)
    repository = json.loads(gh(['api', 'repos/' + REPOSITORY], binary))
    if repository.get('full_name') != REPOSITORY or not repository.get('permissions', {}).get('push'):
        raise ValueError('No se acreditó acceso de escritura al repositorio exacto')
    release = json.loads(gh(['api', 'repos/' + REPOSITORY + '/releases/tags/' + TAG], binary))
    if release.get('tag_name') != TAG or release.get('draft') or not release.get('prerelease'):
        raise ValueError('La Release debe existir, estar publicada y ser experimental')
    return release


def upload(request, release, binary):
    if request.get('schema') != 'CP12_GITHUB_RELEASE_ATTACHMENT_REQUEST_V1' or request.get('repository') != REPOSITORY or request.get('release_tag') != TAG:
        raise ValueError('Solicitud fuera del protocolo')
    archive = Path(request['archive_path'])
    if archive.name != request['file_name'] or archive.stat().st_size != request['bytes'] or sha(archive) != request['sha256']:
        raise ValueError('La fuente no coincide con su solicitud')
    matches = [a for a in release['assets'] if a['name'] == request['file_name']]
    if len(matches) > 1:
        raise ValueError('Nombre de adjunto ambiguo')
    if matches:
        asset = matches[0]
        if asset['size'] != request['bytes'] or asset.get('digest') != 'sha256:' + request['sha256']:
            raise ValueError('El nombre existe con otros bytes; se conserva sin sobrescribir')
    else:
        # Se prohíbe --clobber: nunca borrar un respaldo para sustituirlo.
        gh(['release', 'upload', TAG, str(archive), '--repo', REPOSITORY], binary)
        current = json.loads(gh(['api', 'repos/' + REPOSITORY + '/releases/tags/' + TAG], binary))
        matches = [a for a in current['assets'] if a['name'] == request['file_name']]
        if len(matches) != 1:
            raise ValueError('No hay un único adjunto publicado')
        asset = matches[0]
    if asset['size'] != request['bytes'] or asset.get('digest') != 'sha256:' + request['sha256']:
        raise ValueError('El adjunto remoto no coincide con la fuente')
    if sha(archive) != request['sha256']:
        raise ValueError('La fuente local cambió durante la publicación')
    return asset


def publish_and_verify(request_path, output, binary):
    request = json.loads(request_path.read_text())
    release = preflight(binary)
    asset = upload(request, release, binary)
    metadata = request_path.with_name('ASSET_PUBLICADO_DIRECTO.json')
    with metadata.open('x') as stream:
        stream.write(json.dumps(asset, ensure_ascii=False, indent=2) + '\n')
    adapter = Path(__file__).with_name('conservar_release.py')
    if sha(adapter) != request['conservation_driver_sha256']:
        raise ValueError('El adaptador no coincide con el que formó la cápsula')
    process = subprocess.run([sys.executable, str(adapter), 'aceptar', '--solicitud', str(request_path),
                              '--asset-metadata', str(metadata), '--salida', str(output)],
                             capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError('Descarga o auditoría independiente falló; la publicación no habilita física')
    receipt = json.loads((output / 'ACEPTACION.json').read_text())
    if not receipt['passed'] or receipt['sha256'] != request['sha256'] or receipt['request_sha256'] != sha(request_path):
        raise ValueError('Aceptación de conservación inconsistente')
    receipt['publication_performed_from_process_without_chat_action'] = True
    receipt['publication_driver_sha256'] = sha(Path(__file__))
    receipt['scientific_replay_authorized'] = False
    with (output / 'ACEPTACION_DIRECTA.json').open('x') as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gh-bin', default=shutil.which('gh'))
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--solicitud', type=Path)
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    try:
        if args.preflight:
            preflight(args.gh_bin)
            result = dict(passed=True, scope='Autenticación y metadatos; no prueba de conservación completa',
                          full_upload_recovery_test_passed=False, scientific_replay_authorized=False)
        else:
            if args.solicitud is None or args.salida is None:
                parser.error('--solicitud y --salida son obligatorios para publicar y auditar')
            result = publish_and_verify(args.solicitud.resolve(), args.salida.resolve(), args.gh_bin)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(json.dumps(dict(passed=False, error=str(error), scientific_replay_authorized=False,
                             M2_steps_executed=0), ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
