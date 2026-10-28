"""Controles de conservación sin datos científicos, red ni autenticación real."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('publisher',ROOT/'publicar_desde_proceso.py')
pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)


def run():
    tests={}
    with tempfile.TemporaryDirectory() as temp:
        folder=Path(temp);archive=folder/'capsula.zip';archive.write_bytes(b'abc')
        request=dict(schema='CP12_GITHUB_RELEASE_ATTACHMENT_REQUEST_V1',repository=pub.REPOSITORY,
                     release_tag=pub.TAG,archive_path=str(archive),file_name=archive.name,bytes=3,
                     sha256=hashlib.sha256(b'abc').hexdigest())
        asset=dict(id=1,name=archive.name,size=3,digest='sha256:'+request['sha256'])
        calls=[]
        with patch.object(pub,'gh',side_effect=lambda *args:calls.append(args)):
            assert pub.upload(request,{'assets':[asset]},'dummy')==asset
        tests['identical_existing_asset_reused_without_upload']=not calls
        conflict=dict(asset,digest='sha256:'+'0'*64)
        with patch.object(pub,'gh') as command:
            try:pub.upload(request,{'assets':[conflict]},'dummy')
            except ValueError:tests['conflicting_existing_asset_preserved']=not command.called
            else:tests['conflicting_existing_asset_preserved']=False
        calls=[]
        def fake_gh(command,binary):
            calls.append(command)
            return '' if command[0]=='release' else json.dumps({'assets':[asset]})
        with patch.object(pub,'gh',side_effect=fake_gh):
            assert pub.upload(request,{'assets':[]},'dummy')==asset
        tests['new_upload_has_no_clobber_or_delete']=calls[0]==['release','upload',pub.TAG,str(archive),'--repo',pub.REPOSITORY] and all('--clobber' not in c and 'delete' not in c for c in calls)
        archive.write_bytes(b'def')
        with patch.object(pub,'gh') as command:
            try:pub.upload(request,{'assets':[]},'dummy')
            except ValueError:tests['changed_source_rejected_before_upload']=not command.called
            else:tests['changed_source_rejected_before_upload']=False
        archive.write_bytes(b'abc')
        binary=folder/'gh';binary.write_text('placeholder')
        with patch.object(pub,'gh',side_effect=['',json.dumps({'full_name':pub.REPOSITORY,'permissions':{'push':True}}),json.dumps({'tag_name':pub.TAG,'draft':False,'prerelease':False})]):
            try:pub.preflight(str(binary))
            except ValueError:tests['stable_scientific_release_rejected']=True
            else:tests['stable_scientific_release_rejected']=False
        request['conservation_driver_sha256']=pub.sha(ROOT/'conservar_release.py')
        request_file=folder/'SOLICITUD.json';request_file.write_text(json.dumps(request))
        with patch.object(pub,'preflight',return_value={'assets':[]}),patch.object(pub,'upload',return_value=asset),patch.object(pub.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','PRIVATE_DIAGNOSTIC_NOT_FOR_LOG')):
            try:pub.publish_and_verify(request_file,folder/'recovered','dummy')
            except RuntimeError as error:
                tests['failed_independent_audit_emits_no_acceptance']=not (folder/'recovered/ACEPTACION_DIRECTA.json').exists() and 'PRIVATE_DIAGNOSTIC_NOT_FOR_LOG' not in str(error)
            else:tests['failed_independent_audit_emits_no_acceptance']=False
        output=io.StringIO()
        with patch.object(sys,'argv',['publisher','--preflight','--gh-bin',str(folder/'ABSENT')]),redirect_stdout(output):
            code=pub.main()
        report=json.loads(output.getvalue())
        tests['missing_cli_cannot_authorize_scientific_replay']=code!=0 and report['scientific_replay_authorized'] is False
        result=subprocess.run([sys.executable,str(ROOT/'retomar_hasta11p2.py'),'--home',str(folder/'EMPTY_RESTORED_WORKSPACE')],capture_output=True,text=True)
        report=json.loads(result.stdout)
        tests['consumed_replay_blocked_even_in_fresh_workspace']=result.returncode==3 and report['blocked'] and report['M2_steps_executed']==0 and not (folder/'EMPTY_RESTORED_WORKSPACE').exists()
    if not all(tests.values()):raise AssertionError(tests)
    report=dict(schema='CP12_DIRECT_PUBLICATION_GUARDS_TEST_V1',checked_at_utc=datetime.now(timezone.utc).isoformat(),
                passed=True,tests=tests,M2_steps_executed=0,scientific_data_used=False,
                real_network_or_authentication_used=False,full_live_direct_publication_test_passed=False)
    (ROOT/'CONTROLES_PUBLICACION_DIRECTA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':run()
