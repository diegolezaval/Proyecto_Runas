"""Upload private copies; retain an unmapped canonical archive for byte checks."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import shutil
import uuid


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def isolate_helper(original, expected_home):
    def helper(home, name, arguments, data=None):
        assert home.resolve() == expected_home.resolve()
        if name != 'library_upload.py' or data is None:
            return original(home, name, arguments, data)
        request = copy.deepcopy(data)
        records = []
        for item in request['uploads']:
            assert item['purpose'] == 'create_library_file'
            source = Path(item['local_path']).resolve()
            assert source.parent == home.resolve() / 'capsules' and source.is_file() and not source.is_symlink()
            key = uuid.uuid4().hex
            stage = home / 'runtime/tmp/library_upload_staging' / key / source.name
            stage.parent.mkdir(parents=True, exist_ok=False)
            expected_bytes, expected_sha = source.stat().st_size, sha(source)
            shutil.copyfile(source, stage)
            assert source.stat().st_size == stage.stat().st_size == expected_bytes
            assert sha(source) == sha(stage) == expected_sha
            record = dict(schema='CP12_CANONICAL_ARCHIVE_SEPARATE_FROM_LIBRARY_MAPPED_UPLOAD_COPY',
                at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                canonical_archive_relative=str(source.relative_to(home)),
                staging_relative=str(stage.relative_to(home)),
                bytes=expected_bytes, sha256=expected_sha, canonical_source_unchanged=True,
                upload_copy_hash_verified_before_transfer=True,
                scientific_kernels_changed=False, scientific_gates_changed=False, M2_steps_executed=0)
            path = home / 'preregistration/upload_staging' / (key + '.json')
            write(path, record)
            records.append((source, path, record))
            item['local_path'] = str(stage.resolve())
        result = original(home, name, arguments, request)
        for source, path, record in records:
            record['canonical_source_unchanged_after_helper'] = (
                source.stat().st_size == record['bytes'] and sha(source) == record['sha256'])
            write(path, record)
            assert record['canonical_source_unchanged_after_helper'], 'Canonical archive changed despite upload isolation'
        return result
    return helper


def install(controller, home):
    original_loader = controller.legacy_module
    def loader(actual_home):
        assert actual_home.resolve() == home.resolve()
        legacy = original_loader(actual_home)
        original_factory = legacy.preservation_module
        def factory(actual_home):
            module = original_factory(actual_home)
            module.helper = isolate_helper(module.helper, actual_home)
            return module
        legacy.preservation_module = factory
        return legacy
    controller.legacy_module = loader
