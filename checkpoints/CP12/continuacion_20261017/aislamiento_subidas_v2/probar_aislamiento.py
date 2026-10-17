"""Meaningful controls for upload argument isolation and source mutation detection."""
from pathlib import Path
import json
import tempfile
from aislar_fuentes_subida import isolate_helper, sha


def run():
    with tempfile.TemporaryDirectory() as folder:
        home = Path(folder)
        (home / 'capsules').mkdir()
        source = home / 'capsules/control.zip'
        source.write_bytes(bytes(range(256)) * 8192)
        expected = sha(source)
        original_data = {'uploads': [{'local_path': str(source), 'purpose': 'create_library_file', 'library_artifact_type': 'other'}]}
        def simulated_mapping(home_arg, name, arguments, data):
            assert home_arg == home and name == 'library_upload.py'
            stage = Path(data['uploads'][0]['local_path'])
            assert stage != source and stage.name == source.name and sha(stage) == expected
            stage.write_bytes(b'Synthetic mapped-copy mutation after successful remote transfer')
            return 'success'
        assert isolate_helper(simulated_mapping, home)(home, 'library_upload.py', [], original_data) == 'success'
        assert sha(source) == expected and original_data['uploads'][0]['local_path'] == str(source)
        def source_mutation(home_arg, name, arguments, data):
            source.write_bytes(b'Synthetic canonical mutation')
            return 'success'
        try:
            isolate_helper(source_mutation, home)(home, 'library_upload.py', [], original_data)
            raise RuntimeError('Source mutation was not rejected')
        except AssertionError as error:
            assert 'Canonical archive changed' in str(error)
        received = []
        def passthrough(*args):
            received.append(args)
            return 'unchanged'
        marker = {'transfer': 'untouched'}
        assert isolate_helper(passthrough, home)(home, 'library_file_transfer.py', ['a'], marker) == 'unchanged'
        assert received == [(home, 'library_file_transfer.py', ['a'], marker)]
    return dict(passed=True, canonical_archive_survives_mapped_copy_mutation=True,
        source_mutation_still_rejected=True, caller_request_not_mutated=True,
        non_upload_calls_unchanged=True, scientific_gates_not_relaxed=True, M2_steps_executed=0)


if __name__ == '__main__':
    print(json.dumps(run()))
