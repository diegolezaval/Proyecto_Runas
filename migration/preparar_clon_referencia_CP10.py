"""Comprueba arquitectura; conserva un clon remoto si necesita el entorno de referencia."""
from pathlib import Path
import json,os,subprocess,sys,tarfile,tempfile,datetime
import ejecutar_migracion_GitHub_CP10 as migration

TOOLS=Path(__file__).resolve().parent


def diagnose(clone, overrides=None):
    env=os.environ.copy();env.update(overrides or {})
    result=subprocess.run([sys.executable,str(TOOLS/'diagnosticar_entorno_CP10.py'),str(clone)],
                          env=env,text=True,capture_output=True,check=True,timeout=90)
    return json.loads(result.stdout)


def main():
    assert os.environ['GITHUB_REPOSITORY']==migration.REPO
    with tempfile.TemporaryDirectory(prefix='cp10_clon_remoto_para_referencia_') as temporary:
        work=Path(temporary);clone=work/'clon_GitHub'
        migration.run(migration.GIT_AUTH+['clone','--branch','main','--single-branch',migration.REMOTE,str(clone)])
        assert migration.git(clone,'rev-parse','HEAD')==migration.COMMIT
        assert migration.git(clone,'rev-parse','CP10')=='b361fae70ba0c90a4d7a73e6f9049881bc702982'
        assert not migration.git(clone,'status','--porcelain')
        migration.git(clone,'fsck','--full')
        migration.run([sys.executable,'-m','pip','install','--disable-pip-version-check','-r',str(clone/'requirements.txt')])
        default=diagnose(clone)
        profile={'default_host':default,'reference_profile':'NumPy 2.3.5 / SciPy 1.17.0 / OpenBLAS 0.3.30 SkylakeX, AVX-512, un hilo',
                 'criteria_modified':False,'initial_arrays_modified':False,'integration_steps':0}
        candidate=None
        # Sólo se selecciona SkylakeX cuando las instrucciones existen físicamente.
        if default['cpu_features'].get('AVX512F') and default['cpu_features'].get('AVX512_SKX'):
            candidate=diagnose(clone,{'OPENBLAS_CORETYPE':'SkylakeX'})
            profile['reference_coretype_candidate']=candidate
        match=(candidate or default)
        profile['reference_profile_available_on_host']=all(row['exact_equal'] for row in match['rows'])
        profile_path=work/'Diagnostico_entorno_GitHub_CP10.json'
        migration.write_json(profile_path,profile)
        print(json.dumps(profile,ensure_ascii=False,indent=2),flush=True)
        if profile['reference_profile_available_on_host']:
            if candidate:os.environ['OPENBLAS_CORETYPE']='SkylakeX'
            # El verificador original sigue exigiendo igualdad exacta y todas sus puertas.
            migration.main()
            migration.run(['gh','release','upload','CP10',str(profile_path),'--repo',migration.REPO])
            return
        # Se conserva el clon real y sin credenciales, no se reconstruye a partir del bundle local.
        config=migration.git(clone,'config','--local','--list')
        assert 'extraheader=' not in config.lower() and 'credential.' not in config.lower()
        assert migration.git(clone,'remote','get-url','origin')==migration.REMOTE
        archive=work/'Clon_limpio_GitHub_CP10.tar.gz'
        with tarfile.open(archive,'w:gz') as tar:tar.add(clone,arcname='clon_GitHub')
        receipt={'schema_version':1,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'repository_url':'https://github.com/'+migration.REPO,'origin':migration.REMOTE,
                 'commit':migration.COMMIT,'tree':migration.TREE,'tag':'CP10',
                 'annotated_tag_object':migration.git(clone,'rev-parse','CP10'),
                 'clone_created_by_authenticated_git_clone_from_GitHub':True,
                 'clone_reused_from_local_bundle':False,'worktree_clean':True,'git_fsck_passed':True,
                 'archive_filename':archive.name,'archive_sha256':migration.sha(archive),
                 'archive_size_bytes':archive.stat().st_size,'archive_includes_git_object_database':True,
                 'inline_credentials_in_git_config':False,'scientific_verification_pending_in_reference_environment':True,
                 'profile_filename':profile_path.name,'profile_sha256':migration.sha(profile_path),
                 'workflow_run_url':'https://github.com/'+migration.REPO+'/actions/runs/'+os.environ['GITHUB_RUN_ID'],
                 'main_modified':False,'scientific_results_modified':False,'CP11_started':False}
        receipt_path=work/'Recibo_clon_GitHub_CP10.json';migration.write_json(receipt_path,receipt)
        migration.run(['gh','release','upload',migration.TRANSPORT_TAG,str(archive),str(receipt_path),str(profile_path),'--repo',migration.REPO])
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as summary:
            summary.write('Clon real de GitHub conservado para verificar con el entorno de referencia.\n\n')
            summary.write('La arquitectura del host difiere; la igualdad exacta de campos iniciales permanece exigida. CP10 aún no se publica.\n')
        print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
