"""Controles sintéticos de parada: no usa ciencia, credenciales ni red."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
from unittest.mock import patch
import conservar_transito as subject


def run():
    tests = {}
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / 'fixture.zip'; archive.write_bytes(b'synthetic-fixture')
        request = dict(schema='CP12_GITHUB_RELEASE_ATTACHMENT_REQUEST_V1',
                       repository=subject.REPOSITORY, release_tag='respaldo-cp12-p3-20261027',
                       observer_clock=9.6, archive_path=str(archive), file_name=archive.name,
                       bytes=archive.stat().st_size, sha256=subject.sha(archive),
                       conservation_driver_sha256=subject.REGISTERED_ADAPTER)
        request_path = root / 'request.json'
        def rejected(change):
            altered = dict(request, **change)
            request_path.write_text(json.dumps(altered))
            try:
                subject.validate_request(request_path)
            except ValueError:
                return True
            return False
        tests['changed_source_rejected_before_upload'] = rejected({'sha256':'0'*64})
        tests['other_repository_rejected_before_upload'] = rejected({'repository':'other/repo'})
        tests['other_release_rejected_before_upload'] = rejected({'release_tag':'CP11'})
        tests['unregistered_clock_rejected_before_upload'] = rejected({'observer_clock':12.8})
        tests['unregistered_adapter_rejected_before_upload'] = rejected({'conservation_driver_sha256':'0'*64})
        request_path.write_text(json.dumps(request))
        helpers = root / 'helpers'; helpers.mkdir()
        for name in ['library_upload.py','library_hosted_apps.py','library_file_transfer.py']:
            (helpers/name).write_bytes(b'fixture only')
        private = root/'private';private.mkdir()
        with patch.object(subject.subprocess,'run',return_value=types.SimpleNamespace(returncode=0,stdout='Archivo materializado\n',stderr='')):
            transfer_result=subject.helper(helpers,'library_file_transfer.py',['materialize','unused'],{},private)
        tests['documented_text_transfer_response_not_mistaken_for_json'] = transfer_result is None
        validation = (request, archive, root/'unused-auditor.py')
        first = root/'failed-upload'
        with patch.object(subject,'validate_request',return_value=validation), patch.object(subject,'helper',side_effect=RuntimeError('fixture')):
            try:subject.preserve(request_path,first,helpers)
            except RuntimeError:pass
        result = subject.read(first/'RESULTADO_TRANSITO.json')
        tests['uncertain_write_stops_without_retry_or_success'] = (not result['passed'] and
            result['upload_outcome']=='unknown_requires_reconciliation' and not result['automatic_retry_permitted'] and
            not result['further_physics_authorized'])
        module = types.SimpleNamespace(HostedAppsClient=lambda:types.SimpleNamespace(call_tool=lambda *a,**k:{'transfers':[],'unavailable_items':[{}]}))
        second = root/'failed-download'
        uploaded = {'results':[{'status':'succeeded','file_name':archive.name,'library_file_id':'libfile_fixture','file_id':'file_fixture'}]}
        with patch.object(subject,'validate_request',return_value=validation), patch.object(subject,'helper',return_value=uploaded), patch.dict(sys.modules,{'library_hosted_apps':module}):
            try:subject.preserve(request_path,second,helpers)
            except ValueError:pass
        result = subject.read(second/'RESULTADO_TRANSITO.json')
        pending = subject.read(second/'GUARDADO_DURABLE_PENDIENTE_AUDITORIA.json')
        tests['failed_recovery_keeps_saved_identity_and_blocks_physics'] = (result['uploaded'] and
            result['library_file_id']=='libfile_fixture' and not result['passed'] and
            not result['independent_recovery_verified'] and not result['further_physics_authorized'] and
            pending['library_file_id']=='libfile_fixture')
    report = dict(schema='CP12_P3_TEMPORARY_TRANSIT_GUARDS_V1',passed=all(tests.values()),tests=tests,
                  M2_steps_executed=0,scientific_data_used=False,real_network_or_credentials_used=False,
                  real_capacity_test_passed=False)
    print(json.dumps(report),flush=True)
    if not report['passed']:raise AssertionError('Transit guard failure')


if __name__=='__main__':run()
