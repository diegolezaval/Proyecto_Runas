"""Publica CP10 sólo después de la prueba íntegra del clon remoto en el entorno original."""
from pathlib import Path
import datetime
import json
import os
import tempfile
import ejecutar_migracion_GitHub_CP10 as migration

TAG_OBJECT = 'b361fae70ba0c90a4d7a73e6f9049881bc702982'
TOOLS = Path(__file__).resolve().parent


def assert_refs():
    refs = migration.run(migration.GIT_AUTH + ['ls-remote', migration.REMOTE,
                         'refs/heads/main', 'refs/tags/CP10', 'refs/tags/CP10^{}'], capture=True)
    refs = {line.split('\t')[1]: line.split('\t')[0] for line in refs.splitlines()}
    assert refs['refs/heads/main'] == refs['refs/tags/CP10^{}'] == migration.COMMIT
    assert refs['refs/tags/CP10'] == TAG_OBJECT
    repository = migration.gh_json('api', 'repos/' + migration.REPO)
    assert repository['private'] and repository['default_branch'] == 'main'


def main():
    assert os.environ['GITHUB_REPOSITORY'] == migration.REPO
    assert_refs()
    assert migration.sha(TOOLS / 'verificar_clon_CP10.py') == migration.VERIFIER_SHA
    manifest = json.loads((TOOLS / 'MANIFIESTO_PRUEBA_MIGRACION_CP10.json').read_text())
    attachments = []
    for item in manifest['files']:
        path = TOOLS / item['filename']
        assert path.parent == TOOLS and path.is_file()
        assert path.stat().st_size == item['size_bytes'] and migration.sha(path) == item['sha256']
        attachments.append(path)
    proof = json.loads((TOOLS / 'Comprobacion_clon_GitHub_CP10.json').read_text())
    link = json.loads((TOOLS / 'Vinculo_clon_y_verificacion_CP10.json').read_text())
    receipt = json.loads((TOOLS / 'Recibo_clon_GitHub_CP10.json').read_text())
    assert proof['passed'] and proof['remote_clone_verified'] and proof['origin_kind'] == 'github'
    assert proof['commit'] == migration.COMMIT and proof['branch'] == 'main' and proof['tag'] == 'CP10'
    assert proof['payload_files'] == 938 and proof['all_payload_bytes_preserved']
    assert proof['deterministic_checkpoint_zip_reproduced'] and proof['checkpoint_zip_sha256'] == migration.ZIP_SHA
    assert len(proof['CP10_checks']) >= 13 and all(row['passed'] for row in proof['CP10_checks'])
    assert proof['fresh_C_force']['passed'] and proof['fresh_C_force']['integration_steps'] == 0
    assert all(proof['views_regenerated_identically'].values())
    assert proof['scientific_gate'] == 'REFINAMIENTO_PENDIENTE' and not proof['finite_campaign_passed']
    assert not proof['scientific_campaigns_executed'] and not proof['CP11_started']
    assert receipt['clone_created_by_authenticated_git_clone_from_GitHub'] and not receipt['clone_reused_from_local_bundle']
    assert receipt['commit'] == migration.COMMIT and receipt['tree'] == migration.TREE
    assert receipt['annotated_tag_object'] == TAG_OBJECT and not receipt['inline_credentials_in_git_config']
    assert link['scientific_verification_passed'] and link['all_artifact_and_part_hashes_verified']
    assert link['transport_archive_sha256'] == receipt['archive_sha256']
    assert link['proof_sha256'] == migration.sha(TOOLS / 'Comprobacion_clon_GitHub_CP10.json')
    assert link['verifier_sha256'] == migration.VERIFIER_SHA
    assert link['reference_environment']['exact_initial_fields']
    assert not link['criteria_modified'] and not link['scientific_results_modified'] and not link['CP11_started']
    current = [release for release in migration.releases() if release['tag_name'] == 'CP10']
    assert not current, 'Ya existe una Release CP10: detener antes de sustituir evidencia'
    with tempfile.TemporaryDirectory(prefix='cp10_publicacion_verificada_') as temporary:
        work = Path(temporary)
        source = migration.download(migration.TRANSPORT_TAG, migration.ZIP, work / 'fuente')
        assert source.stat().st_size == 81773782 and migration.sha(source) == migration.ZIP_SHA
        migration.run(['gh', 'release', 'create', 'CP10', str(source),
                       *map(str, attachments), str(TOOLS / 'MANIFIESTO_PRUEBA_MIGRACION_CP10.json'),
                       '--repo', migration.REPO, '--verify-tag', '--draft', '--target', migration.COMMIT,
                       '--title', 'CP10 · Mediador espaciotemporal',
                       '--notes-file', str(TOOLS / 'notas_release_CP10_verificada.md')])
        draft = migration.download('CP10', migration.ZIP, work / 'borrador')
        assert draft.stat().st_size == 81773782 and migration.sha(draft) == migration.ZIP_SHA
        migration.run(['gh', 'release', 'edit', 'CP10', '--repo', migration.REPO, '--draft=false'])
        published = migration.download('CP10', migration.ZIP, work / 'publicada')
        assert published.stat().st_size == 81773782 and migration.sha(published) == migration.ZIP_SHA
        release = migration.gh_json('release', 'view', 'CP10', '--repo', migration.REPO,
                                    '--json', 'url,tagName,isDraft,assets,publishedAt')
        assert release['tagName'] == 'CP10' and not release['isDraft']
        assert_refs()
        report = {
            'schema_version': 1, 'migration_status': 'MIGRACION_CP10_VERIFICADA',
            'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'repository_url': 'https://github.com/' + migration.REPO, 'visibility': 'private',
            'branch': 'main', 'commit': migration.COMMIT, 'tree': migration.TREE,
            'tag': 'CP10', 'annotated_tag_object': TAG_OBJECT, 'tag_commit': migration.COMMIT,
            'remote_clone_verified': True, 'clone_receipt_sha256': migration.sha(TOOLS / 'Recibo_clon_GitHub_CP10.json'),
            'clone_workflow_run_url': receipt['workflow_run_url'],
            'transport_archive_sha256': receipt['archive_sha256'],
            'payload_files': 938, 'all_payload_bytes_preserved': True,
            'scientific_checks_passed': True, 'deterministic_checkpoint_zip_reproduced': True,
            'scientific_gate': proof['scientific_gate'], 'finite_campaign_passed': proof['finite_campaign_passed'],
            'original_zip': {'filename': migration.ZIP, 'size_bytes': 81773782, 'sha256': migration.ZIP_SHA},
            'release_url': release['url'], 'release_published': True,
            'draft_download_sha256_verified': True, 'release_download_sha256_verified': True,
            'release_download_size_bytes': published.stat().st_size,
            'proof_filename': 'Comprobacion_clon_GitHub_CP10.json',
            'proof_sha256': migration.sha(TOOLS / 'Comprobacion_clon_GitHub_CP10.json'),
            'verifier_sha256': migration.VERIFIER_SHA,
            'reference_environment': link['reference_environment'],
            'generic_GitHub_runner_scientific_verification_passed': False,
            'environment_limitation_documented': True,
            'science_modified': False, 'project_reorganized': False, 'CP11_started': False,
            'file_migration_map': [], 'auxiliary_branch': 'migration/cp10',
            'bootstrap_commit_preserved': '436fb01ac4656171da31603a306587d6cba559f9',
            'transport_release': {'tag': migration.TRANSPORT_TAG, 'draft': True},
            'workflow_run_url': 'https://github.com/' + migration.REPO + '/actions/runs/' + os.environ['GITHUB_RUN_ID'],
            'proof_source_commit': os.environ['GITHUB_SHA'],
            'authentication': 'Token nativo efímero de GitHub Actions; contents:write del repositorio privado',
        }
        final = work / 'Acta_migracion_GitHub_CP10.json'
        migration.write_json(final, report)
        migration.run(['gh', 'release', 'upload', 'CP10', str(final), '--repo', migration.REPO])
        # Se recupera también el acta desde la Release para comprobar que la evidencia está publicada.
        copy = migration.download('CP10', final.name, work / 'acta_publicada')
        assert migration.sha(copy) == migration.sha(final)
        assert_refs()
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        summary_path = Path(os.environ['GITHUB_STEP_SUMMARY'])
        with summary_path.open('a', encoding='utf-8') as summary:
            summary.write('CP10 migrado y verificado: 938 archivos idénticos, clon real reproducido en el entorno de referencia.\n\n')
            summary.write('ZIP original recuperado de la Release publicada y comprobado por SHA-256.\n\n')
            summary.write('La dependencia de AVX-512/SkylakeX para las dos pruebas exactas queda documentada; no se suavizan criterios.\n')
        artifacts = Path('acta_final_CP10')
        artifacts.mkdir(exist_ok=False)
        migration.write_json(artifacts / final.name, report)


if __name__ == '__main__':
    main()
