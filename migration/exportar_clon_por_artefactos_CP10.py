"""Transporta un clon auténtico de GitHub mediante artefactos privados, sin alterar CP10."""
from pathlib import Path
import datetime
import json
import os
import tarfile
import tempfile
import ejecutar_migracion_GitHub_CP10 as migration


def main():
    assert os.environ['GITHUB_REPOSITORY'] == migration.REPO
    repository = migration.gh_json('api', 'repos/' + migration.REPO)
    assert repository['private'] and repository['default_branch'] == 'main'
    output = Path('transporte_clon_CP10').resolve()
    output.mkdir(exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='cp10_clon_autentico_') as temporary:
        clone = Path(temporary) / 'clon_GitHub'
        migration.run(migration.GIT_AUTH + ['clone', '--branch', 'main', '--single-branch',
                                           migration.REMOTE, str(clone)])
        assert migration.git(clone, 'rev-parse', 'HEAD') == migration.COMMIT
        assert migration.git(clone, 'rev-parse', 'HEAD^{tree}') == migration.TREE
        assert migration.git(clone, 'rev-parse', 'CP10') == 'b361fae70ba0c90a4d7a73e6f9049881bc702982'
        assert migration.git(clone, 'rev-parse', 'CP10^{commit}') == migration.COMMIT
        assert not migration.git(clone, 'status', '--porcelain')
        migration.git(clone, 'fsck', '--full')
        assert migration.git(clone, 'remote', 'get-url', 'origin') == migration.REMOTE
        config = migration.git(clone, 'config', '--local', '--list').lower()
        assert 'credential.' not in config and 'extraheader=' not in config
        archive = Path(temporary) / 'Clon_limpio_GitHub_CP10.tar.gz'
        with tarfile.open(archive, 'w:gz') as stream:
            stream.add(clone, arcname='clon_GitHub')
        parts = []
        with archive.open('rb') as stream:
            while block := stream.read(20 * 1024 * 1024):
                number = len(parts)
                assert number < 8, 'El clon excede el transporte previsto; detener sin truncarlo'
                folder = output / f'part{number:02d}'
                folder.mkdir()
                piece = folder / f'Clon_limpio_GitHub_CP10.tar.gz.part{number:02d}.bin'
                piece.write_bytes(block)
                parts.append({'filename': piece.name, 'artifact_name': f'CP10-clon-parte-{number:02d}',
                              'size_bytes': len(block), 'sha256': migration.sha(piece)})
        assert len(parts) == 8
        record = {
            'schema_version': 1,
            'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'repository_url': 'https://github.com/' + migration.REPO,
            'origin': migration.REMOTE,
            'commit': migration.COMMIT, 'tree': migration.TREE, 'tag': 'CP10',
            'annotated_tag_object': migration.git(clone, 'rev-parse', 'CP10'),
            'clone_created_by_authenticated_git_clone_from_GitHub': True,
            'clone_reused_from_local_bundle': False,
            'worktree_clean': True, 'git_fsck_passed': True,
            'archive_filename': archive.name, 'archive_size_bytes': archive.stat().st_size,
            'archive_sha256': migration.sha(archive),
            'archive_includes_git_object_database': True,
            'inline_credentials_in_git_config': False,
            'scientific_verification_pending_in_reference_environment': True,
            'workflow_run_url': 'https://github.com/' + migration.REPO + '/actions/runs/' + os.environ['GITHUB_RUN_ID'],
            'transport': 'GitHub Actions artifacts; eight lossless binary parts',
            'parts': parts, 'main_modified': False, 'scientific_results_modified': False, 'CP11_started': False,
        }
        metadata = output / 'recibo'
        metadata.mkdir()
        migration.write_json(metadata / 'Recibo_clon_GitHub_CP10.json', record)
        print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as summary:
            summary.write('Clon real de main y CP10 conservado sin cambios mediante artefactos privados.\n')
            summary.write('La comprobación científica permanece pendiente hasta ejecutar el verificador original en el entorno de referencia.\n')


if __name__ == '__main__':
    main()
