"""Create an isolated, hash-pinned K4 experiment; execute no M2 steps."""
from pathlib import Path
import argparse, hashlib, json, shutil, uuid

def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,value):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-home',type=Path,required=True);p.add_argument('--analysis-root',type=Path,required=True);p.add_argument('--causal-root',type=Path,required=True);p.add_argument('--home',type=Path,required=True);p.add_argument('--library-helpers',type=Path,required=True);a=p.parse_args()
    old=a.source_home.resolve();analysis=a.analysis_root.resolve();causal=a.causal_root.resolve();home=a.home.resolve();sources=Path(__file__).parent
    assert not home.exists()
    parent=read(old/'proofs/tau0160_permanent.json');audit=parent['independent_extracted_audit']
    assert parent['passed'] and parent['time']==160 and parent['all_payload_hashes_verified'] and audit['passed'] and len(audit['tests'])==44 and all(audit['tests'].values())
    cm=read(causal/'MANIFIESTO.json')
    for n,v in cm['files'].items():assert sha(causal/n)==v['sha256'] and (causal/n).stat().st_size==v['bytes']
    original=read(causal/'resultados.json');serial=read(causal/'SERIALIZATION_CHECK.json')
    assert original['time']==160 and original['reproduces_CP10_exactly'] and original['observer_checks_passed'] and serial['passed'] and serial['scientific_input_hashes_unchanged']
    assert read(causal/'original_tau160_permanent.json')['state_sha256']==parent['state_sha256']
    assert original['sufficiency']['coupled']['operador_chi']['meets_all_three_windows'] and original['observed_core_phase_relative_error']>.02
    ident=read(old/'preregistration/identidad_cientifica.json');selected=read(analysis/'SELECTED_ANALYSIS_VERIFIED.json')
    assert selected['all_selected_analysis_hashes_passed'] and selected['original_manifest_files']==486 and selected['selected_files_verified']==76
    static=read(analysis/'analysis/candidato_operador/resultados.json');frozen=read(analysis/'analysis/backend_candidato/resultados_acoplados_v2.json')
    assert static['regular_polynomials_verified'] and static['positive_quadratic_form'] and static['mass_and_potential_unchanged'] and frozen['passed']
    assert sha(analysis/'analysis/candidato_operador/operador.py')==static['operator_sha256']
    assert sha(analysis/'analysis/backend_candidato/backend.py')==frozen['backend_sha256']
    for n,h in {**ident['code_hashes'],**ident['input_hashes']}.items():assert sha(old/'science'/n)==h,n
    for name in ('runtime/library','runtime/tmp','outputs','proofs','preregistration','candidate','capsules','recoveries'):(home/name).mkdir(parents=True,exist_ok=True)
    for n,h in {**ident['code_hashes'],**ident['input_hashes']}.items():
        source=old/'science'/n;target=home/'science'/n;assert not source.is_symlink()
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert sha(target)==h and source.stat().st_ino!=target.stat().st_ino;target.chmod(0o444)
    shutil.copyfile(sources/'candidato_K4_coordinador.py',home/'coordinator.py')
    shutil.copyfile(old/'guardian.py',home/'guardian.py')
    preservation=(old/'coordinator.py').read_text();assert preservation.count("'CP12_RI_'")==2
    preservation=preservation.replace("'CP12_RI_'","'CP12_CANDIDATO_K4_'").replace('CP12_INDEPENDENT_RECOVERY_FULL_CAPSULE_NOT_SCIENTIFIC_CLOSURE','CP12_K4_TRIAL_FULL_CAPSULE_NOT_CORRECTION_VALIDATION').replace('CP12_INDEPENDENT_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED','CP12_K4_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED')
    (home/'preservation.py').write_text(preservation)
    for source,target in [('analysis/candidato_operador/operador.py','candidate/operador.py'),('analysis/backend_candidato/backend.py','candidate/backend.py')]:shutil.copyfile(analysis/source,home/target)
    shutil.copyfile(sources/'PRERREGISTRO_K4_PRIMERA_PRUEBA.md',home/'preregistration/PRERREGISTRO.md')
    reused=['analysis/PRERREGISTRO_CONDICIONAL_CORRECCION.md','analysis/candidato_operador/resultados.json','analysis/candidato_operador/PRERREGISTRO.md','analysis/backend_candidato/resultados.json','analysis/backend_candidato/resultados_acoplados_v2.json','analysis/backend_candidato/ENMIENDA_ACOPLADO_V2.md','analysis/backend_candidato/fallo_acoplado_v1.json','analysis/regularidad/DERIVACION_Y_RESULTADOS.md','analysis/dispersion_candidato/DERIVACION_Y_RESULTADOS.md','analysis/paquete_libre/RESULTADO_NEGATIVO.md']
    for n in reused:
        assert sha(analysis/n)==selected['files'][n]['sha256'];target=home/'prior'/Path(n).relative_to('analysis');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(analysis/n,target)
    for name in ('library_download.py','library_file_transfer.py','library_hosted_apps.py','library_upload.py'):shutil.copyfile(a.library_helpers/name,home/'runtime/library'/name)
    write(home/'preregistration/identidad_cientifica_original.json',ident)
    write(home/'preregistration/antecedente_tau160.json',parent)
    write(home/'preregistration/RESULTADO_CAUSAL_ORIGINAL.json',original)
    cfg=read(old/'science/datos/ensayo_causal_chi_CP12.json')['cases']['par_instrumentado']['configuration']
    write(home/'configuration.json',dict(schema='CP12_K4_PREREGISTERED_FIRST_TRIAL',original_configuration=cfg,action='K2_regular_positive_plus_h2_over_12_K2_Winv_K2_all_three_fields',coefficient_fixed_independently_of_chi=1/12,original_two_grids_unchanged=True,additional_reference_deferred_until_positive_original_pair=True,automatic_other_candidates=False,CP12_closed=False))
    capture=[Path('coordinator.py'),Path('guardian.py'),Path('preservation.py'),Path('configuration.json'),Path('candidate/operador.py'),Path('candidate/backend.py'),Path('preregistration/PRERREGISTRO.md')]
    captured={n.as_posix():sha(home/n) for n in capture}
    new_uuid=uuid.uuid4().hex
    run_id=hashlib.sha256(json.dumps(dict(kind='NEW_K4_TRIAL',uuid=new_uuid,original_identity=ident,captured_sources=captured),sort_keys=True).encode()).hexdigest()
    info=dict(execution_uuid=new_uuid,branch='ciencia/cp12-continuacion-20261014',ancestor_state_sha256=parent['state_sha256'],scientific_evidence_parent_time=160,physical_initial_time=0,physical_initial_data='Six original CP10 Cauchy fields; not the tau160 final state',old_executor_termination_assumed=False)
    meta=dict(execution_uuid=new_uuid,execution_run_id=run_id,branch=info['branch'],run_relative='outputs',run_root_anchor='independent_execution_home',supervision_source_sha256=captured['coordinator.py'],captured_sources=captured,initial_frontier=0)
    write(home/'preregistration/ubicacion.json',info);write(home/'preregistration/nueva_identidad.json',meta)
    write(home/'preregistration/CONTROLES_REUTILIZADOS.json',dict(original_archive_sha256=selected['original_zip_sha256'],candidate_operator_sha256=static['operator_sha256'],candidate_backend_sha256=frozen['backend_sha256'],static_variational_relative_residual=static['variational_force_relative_residual'],frozen_preflight_passed=True,new_static_controls_repeated=False,nonlinear_K4_history_previously_validated=False,original_phase_discrepancy=original['observed_core_phase_relative_error'],files={n:selected['files'][n] for n in reused}))
    write(home/'outputs/procedencia.json',dict(schema='CP12_NEW_K4_NUMERICAL_TRIAL_RECEIPT',execution_run_id=run_id,kind='New physical M2 evolution with preregistered spatial action',physical_initial_time=0,time=0,status='CREADA_SIN_PASOS_M2',segments=[],physical_accepted_steps=[0,0],original_CP10_reproduction=False,original_private_receipt_recreated=False,output_hashes={},scientific_sources_changed=False,correction_validated=False,CP12_closed=False))
    for n in captured:(home/n).chmod(0o444)
    write(home/'preregistration/AISLAMIENTO.json',dict(passed=True,independent_files_no_hardlinks_or_symlinks=True,original_sources_and_inputs_verified=len(set(ident['code_hashes'])|set(ident['input_hashes'])),captured_sources=captured,original_source_home_not_modified=True,physical_initial_time=0,M2_steps_executed=0,CP12_closed=False))
    print(json.dumps(dict(home=str(home),execution_uuid=new_uuid,execution_run_id=run_id,source_hash=captured['coordinator.py'],M2_steps_executed=0,public_registration_required_before_initialization=True),ensure_ascii=False))
if __name__=='__main__':main()
