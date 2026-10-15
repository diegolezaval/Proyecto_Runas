"""Build a new isolated mixed trial. This preparation never integrates M2."""
from pathlib import Path
import argparse, hashlib, json, shutil, uuid

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ancestor',type=Path,required=True);ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--helpers',type=Path,required=True);ap.add_argument('--home',type=Path,required=True);a=ap.parse_args()
    ancestor=a.ancestor.resolve();sources=a.sources.resolve();home=a.home.resolve()
    assert not home.exists(),'Never overwrite an instance'
    manifest=read(ancestor/'MANIFIESTO_NEGATIVO.json')
    actual={p.relative_to(ancestor).as_posix() for p in ancestor.rglob('*') if p.is_file() and p.name!='MANIFIESTO_NEGATIVO.json' and not any(x in ('cache','__pycache__') for x in p.parts) and p.suffix not in ('.pyc','.so')}
    assert actual==set(manifest['files'])
    for n,v in manifest['files'].items():assert (ancestor/n).stat().st_size==v['bytes'] and sha(ancestor/n)==v['sha256'],n
    cert=read(sources/'preflight_certificate.json');assert cert['all_registered_preflight_controls_passed'] and cert['M2_steps_executed']==0
    assert sha(sources/'mixed_backend.py')==cert['mixed_backend_sha256']
    expected={'operador.py':'8c4232ddc9366b8331729a0336552bb701039ff3be802abf43c24f4de5c1dca4','backend.py':'9ee945d1eb6d33a1972df773b6b858868e5d0498fb15cd03617951389d96d759'}
    for n,h in expected.items():assert sha(ancestor/'candidate'/n)==h
    home.mkdir();shutil.copytree(ancestor/'science',home/'science',ignore=shutil.ignore_patterns('cache','__pycache__','*.pyc','*.so'))
    shutil.copytree(ancestor/'prior',home/'prior')
    for name in ('candidate','preregistration','outputs','proofs','analysis','negative','capsules','recoveries','runtime/tmp','runtime/force','runtime/library'): (home/name).mkdir(parents=True,exist_ok=True)
    for name in ('coordinator.py','preservation.py','guardian.py'):shutil.copyfile(sources/name,home/name)
    for name in expected:shutil.copyfile(ancestor/'candidate'/name,home/'candidate'/name)
    shutil.copyfile(sources/'mixed_backend.py',home/'candidate/mixed_backend.py')
    for name in ('PRERREGISTRO.md','preflight_certificate.json','REGISTRO.json'):shutil.copyfile(sources/name,home/'preregistration'/name)
    for name in ('identidad_cientifica_original.json','RESULTADO_CAUSAL_ORIGINAL.json','CONTROLES_REUTILIZADOS.json','antecedente_tau160.json'):shutil.copyfile(ancestor/'preregistration'/name,home/'preregistration'/name)
    for name in ('library_download.py','library_hosted_apps.py','library_file_transfer.py','library_upload.py'):shutil.copyfile(a.helpers/name,home/'runtime/library'/name)
    cfg=read(ancestor/'configuration.json');cfg.update(schema='CP12_MIXED_PREREGISTERED_PHYSICAL_PILOT',action='Phi_original_FV_chi_fixed_K2_plus_h2_over_12_K2_Winv_K2')
    write(home/'configuration.json',cfg)
    captured=['coordinator.py','preservation.py','guardian.py','configuration.json','candidate/operador.py','candidate/backend.py','candidate/mixed_backend.py','preregistration/PRERREGISTRO.md','preregistration/REGISTRO.json','preregistration/preflight_certificate.json']
    hashes={n:sha(home/n) for n in captured}
    uid=uuid.uuid4().hex;run_id=hashlib.sha256(json.dumps(dict(uuid=uid,sources=hashes),sort_keys=True).encode()).hexdigest()
    write(home/'preregistration/nueva_identidad.json',dict(execution_uuid=uid,execution_run_id=run_id,branch='ciencia/cp12-continuacion-20261014',run_relative='outputs',initial_frontier=0,supervision_source_sha256=hashes['coordinator.py'],captured_sources=hashes))
    write(home/'preregistration/ubicacion.json',dict(execution_uuid=uid,branch='ciencia/cp12-continuacion-20261014',ancestor_state_sha256='22078538ebba2e948b433b0ab946ee034be132b27f7e72ca1ee30540323b2413',scope='Causal antecedent only, not Cauchy data',execution_home=str(home)))
    write(home/'preregistration/registro_publico.json',dict(registered_before_M2=False,captured_sources=hashes,physical_steps_executed=0))
    write(home/'outputs/procedencia.json',dict(schema='CP12_NEW_MIXED_NUMERICAL_TRIAL_RECEIPT',execution_run_id=run_id,kind='New fully coupled M2 evolution with mixed spatial action',physical_initial_time=0,time=0,status='NO_INICIADA',segments=[],physical_accepted_steps=[0,0],original_CP10_reproduction=False,original_private_receipt_recreated=False,output_hashes={},scientific_sources_changed=False,correction_validated=False,CP12_closed=False))
    for p in (home/'science').rglob('*'):
        if p.is_file():p.chmod(0o444)
    print(json.dumps(dict(home=str(home),execution_uuid=uid,execution_run_id=run_id,captured_sources=hashes,M2_steps_executed=0)))

if __name__=='__main__':main()
