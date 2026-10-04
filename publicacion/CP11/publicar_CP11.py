"""Publicación limitada a CP11 ya verificado e integrado mediante PR; sin ciencia."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zlib

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / 'configuracion.json').read_text())
REPO = 'diegolezaval/Proyecto_Runas'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1048576), b''): h.update(part)
    return h.hexdigest()


def run(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=180)
    if result.returncode: raise RuntimeError('Comando fallido: ' + str(args[:3]) + '\n' + result.stderr[-3000:])
    return result.stdout


def api(endpoint, body=None):
    args = ['gh', 'api', 'repos/' + REPO + '/' + endpoint]
    if body is not None:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as data:
            json.dump(body, data); data.flush()
            return json.loads(run(args + ['--method', 'POST', '--input', data.name]))
    return json.loads(run(args))


def refs():
    repository = json.loads(run(['gh', 'api', 'repos/' + REPO]))
    assert repository['private'] is False and repository['default_branch'] == 'main'
    main = api('branches/main')
    assert main['protected'] and main['commit']['sha'] == CFG['merge_commit']
    assert main['commit']['commit']['tree']['sha'] == CFG['tree']
    cp10 = api('git/ref/tags/CP10')
    assert cp10['object']['sha'] == CFG['CP10_tag_object'] and cp10['object']['type'] == 'tag'
    assert api('git/tags/' + CFG['CP10_tag_object'])['object']['sha'] == CFG['CP10_commit']
    pr = api('pulls/' + str(CFG['pull_request']))
    assert pr['merged'] and pr['merge_commit_sha'] == CFG['merge_commit']
    assert pr['head']['sha'] == CFG['scientific_head'] and pr['base']['ref'] == 'main'
    return main


def download(name, destination):
    destination.mkdir(parents=True, exist_ok=True)
    run(['gh', 'release', 'download', 'CP11', '--repo', REPO, '--pattern', name, '--dir', str(destination)])
    return destination / name


def main():
    assert os.environ['GITHUB_REPOSITORY'] == REPO
    assert os.environ['GITHUB_REF'] == 'refs/heads/publicacion/cp11'
    assert sys.version_info[:3] == (3, 12, 14) and zlib.ZLIB_RUNTIME_VERSION == '1.3.2'
    refs()
    attachments = []
    for item in CFG['attachments']:
        path = HERE / item['filename']
        assert path.parent == HERE and path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
        attachments.append(path)
    proof = json.loads((HERE / 'Comprobacion_clon_CP11.json').read_text())
    assert proof['passed'] and proof['remote_clone_verified'] and proof['clean_before'] and proof['clean_after']
    assert proof['commit'] == CFG['scientific_head'] and proof['tree'] == CFG['tree']
    assert proof['payload_files'] == 1047 and proof['checkpoint_zip_sha256'] == CFG['zip_sha256']
    assert proof['regression_checks_passed'] == 23 and proof['structural_tests_passed'] == 15
    assert proof['three_diagnostics_reproduced_byte_identically'] and proof['publication_command_returncode'] == 0
    assert proof['external_receipt_integrity_verified'] and proof['original_CP10_files_recoverable'] == 938
    assert proof['new_M2_evolution_steps'] == 0 and proof['physical_gate_threshold'] == .02
    assert proof['physical_gate'] == 'REFINAMIENTO_PENDIENTE' and not proof['cause_certified']
    with tempfile.TemporaryDirectory(prefix='publicar_CP11_') as temporary:
        work = Path(temporary); source = work / 'Proyecto_Runas'
        run(['git', '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential', 'clone', '--depth', '1', '--single-branch', '--branch', 'main', 'https://github.com/' + REPO + '.git', str(source)])
        run(['git', 'checkout', '-b', 'verificacion-publicacion-cp11', CFG['merge_commit']], cwd=source)
        assert run(['git', 'rev-parse', 'HEAD'], cwd=source).strip() == CFG['merge_commit']
        assert run(['git', 'rev-parse', 'HEAD^{tree}'], cwd=source).strip() == CFG['tree']
        assert not run(['git', 'status', '--porcelain'], cwd=source).strip()
        verified = json.loads(run([sys.executable, 'herramientas/checkpoint.py', '--verificar'], cwd=source))
        assert verified['passed'] and verified['files'] == 1046
        archive = work / CFG['zip_filename']
        packed = json.loads(run([sys.executable, 'herramientas/checkpoint.py', '--salida', str(archive)], cwd=source))
        assert packed['combined_integrity_passed'] and packed['combined_files'] == 1047
        assert archive.stat().st_size == CFG['zip_bytes'] and sha(archive) == CFG['zip_sha256']
        assert not run(['git', 'status', '--porcelain'], cwd=source).strip()
        refs()
        message = 'CP11 verificado; commit=' + CFG['merge_commit'] + '; tree=' + CFG['tree'] + '; ZIP SHA256=' + CFG['zip_sha256']
        existing = api('git/matching-refs/tags/CP11')
        exact = [item for item in existing if item['ref'] == 'refs/tags/CP11']
        assert len(exact) <= 1
        if exact:
            tag_object = exact[0]['object']['sha']; assert exact[0]['object']['type'] == 'tag'
            tag = api('git/tags/' + tag_object)
            assert tag['object']['sha'] == CFG['merge_commit'] and tag['message'].strip() == message
        else:
            tag_object = api('git/tags', dict(tag='CP11', message=message, object=CFG['merge_commit'], type='commit'))['sha']
            api('git/refs', dict(ref='refs/tags/CP11', sha=tag_object))
        notes = (HERE / 'notas_release_CP11.md').read_text()
        releases = api('releases?per_page=100')
        releases = [item for item in releases if item['tag_name'] == 'CP11']; assert len(releases) <= 1
        if releases:
            assert releases[0]['body'].strip() == notes.strip(), 'No sustituir una Release de otra procedencia'
        else:
            run(['gh', 'release', 'create', 'CP11', '--repo', REPO, '--verify-tag', '--target', CFG['merge_commit'], '--draft', '--title', 'CP11 · Diagnóstico radial de χ', '--notes-file', str(HERE / 'notas_release_CP11.md')])
        assets = [archive, *attachments, HERE / 'configuracion.json', HERE / 'publicar_CP11.py', HERE / 'notas_release_CP11.md']
        present = {item['name'] for item in api('releases/tags/CP11')['assets']}
        for path in assets:
            if path.name not in present: run(['gh', 'release', 'upload', 'CP11', str(path), '--repo', REPO])
            received = download(path.name, work / ('comprobar_' + path.name))
            assert received.stat().st_size == path.stat().st_size and sha(received) == sha(path)
        release = api('releases/tags/CP11')
        if release['draft']: run(['gh', 'release', 'edit', 'CP11', '--repo', REPO, '--draft=false'])
        published = download(archive.name, work / 'publicada')
        assert sha(published) == CFG['zip_sha256'] and published.stat().st_size == CFG['zip_bytes']
        refs(); release = api('releases/tags/CP11'); assert not release['draft']
        report = dict(schema_version=1, passed=True, checkpoint='CP11_DIAGNOSTICO_RADIAL_CHI',
            recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), repository_url='https://github.com/' + REPO,
            main_commit=CFG['merge_commit'], scientific_head=CFG['scientific_head'], tree=CFG['tree'], pull_request=CFG['pull_request'],
            integration_via_PR=True, main_protection_preserved=True, CP10_tag_preserved=True,
            tag='CP11', annotated_tag_object=tag_object, release_url=release['html_url'], release_published=True,
            zip_filename=archive.name, zip_sha256=CFG['zip_sha256'], zip_bytes=CFG['zip_bytes'], payload_files=1047,
            remote_main_clone_verified=True, deterministic_checkpoint_zip_reproduced=True,
            draft_or_existing_asset_download_hashes_verified=True, published_zip_download_hash_verified=True,
            scientific_reference_clone_proof_sha256=sha(HERE / 'Comprobacion_clon_CP11.json'),
            scientific_reference_verification_passed=True, generic_runner_exact_scientific_tests_executed=False,
            physical_gate='REFINAMIENTO_PENDIENTE', physical_gate_threshold=.02, cause_certified=False,
            new_M2_evolution_steps=0, CP12_started=False, project_reorganized=False, file_migration_map=[],
            workflow_run_url='https://github.com/' + REPO + '/actions/runs/' + os.environ['GITHUB_RUN_ID'],
            publication_source_commit=os.environ['GITHUB_SHA'], authentication='Token nativo efímero de GitHub Actions, contents:write; no credenciales exportadas')
        out = Path('acta_final_CP11'); out.mkdir(exist_ok=True)
        final = out / 'Acta_publicacion_CP11.json'; final.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        current = {item['name'] for item in release['assets']}
        if final.name not in current:
            run(['gh', 'release', 'upload', 'CP11', str(final), '--repo', REPO])
            received = download(final.name, work / 'acta'); assert sha(received) == sha(final)
        else:
            previous = json.loads(download(final.name, work / 'acta').read_text())
            assert previous['passed'] and previous['main_commit'] == CFG['merge_commit'] and previous['zip_sha256'] == CFG['zip_sha256']
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as summary:
            summary.write('CP11 publicado tras PR y clon verificado: 1047 archivos, ZIP idéntico por SHA-256.\n\nPuerta científica 2 % pendiente; ningún paso nuevo M2.\n')


if __name__ == '__main__':
    main()
