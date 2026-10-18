"""Create a separate P3 instance from authenticated inputs; never integrate M2."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import shutil
import uuid


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(p):
    return json.loads(p.read_text())


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ancestor', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--helpers', type=Path, required=True)
    parser.add_argument('--home', type=Path, required=True)
    args = parser.parse_args()
    ancestor, package, home = args.ancestor.resolve(), args.package.resolve(), args.home.resolve()
    assert not home.exists(), 'Never overwrite any experiment instance'
    assert sha(args.manifest) == '1591cf07d208d3363de4f10676cb3bfb69f3b2500c7848c405825291d12fc5b2'
    manifest = read(args.manifest)
    assert len(manifest['files']) == 472
    for name, record in manifest['files'].items():
        assert (ancestor/name).stat().st_size == record['bytes'] and sha(ancestor/name) == record['sha256'], name
    preflight = read(package/'CERTIFICADO_F0_F5.json')
    proof = read(package/'CONSERVACION_F0_F5.json')
    assert preflight['all_registered_preflight_controls_passed'] and preflight['controls_preserved_and_independently_retrieved']
    assert proof['passed'] and proof['all_payload_hashes_verified']
    registered = read(package/'REGISTRO_CODIGO.json')
    for name, expected in registered['source_hashes'].items():
        assert sha(package/name) == expected, name
    for name, expected in read(package/'pilot/REGISTRO_FUENTES.json')['source_hashes'].items():
        assert sha(package/'pilot'/name) == expected, name
    home.mkdir()
    ignore = shutil.ignore_patterns('cache', '__pycache__', '*.pyc', '*.so')
    shutil.copytree(ancestor/'science', home/'science', ignore=ignore)
    shutil.copytree(ancestor/'prior', home/'prior', ignore=ignore)
    for name in ('candidate', 'preregistration', 'outputs', 'proofs', 'analysis', 'negative', 'capsules',
                 'recoveries', 'transport', 'runtime/tmp', 'runtime/force', 'runtime/library'):
        (home/name).mkdir(parents=True, exist_ok=True)
    for name in ('operador.py', 'backend.py', 'mixed_backend.py'):
        shutil.copyfile(ancestor/'candidate'/name, home/'candidate'/name)
    shutil.copyfile(package/'p3_backend.py', home/'candidate/p3_backend.py')
    for name in ('coordinator.py', 'preservation.py', 'controlador_transporte.py', 'transporte.py',
                 'seleccion_canonica.py', 'CONTROLES_SINTETICOS.json', 'CONTROL_ADAPTACION_ESTATICA.json'):
        shutil.copyfile(package/'pilot'/name, home/name)
    shutil.copytree(package/'pilot/administration', home/'preregistration/administration')
    for name in ('identidad_cientifica_original.json', 'RESULTADO_CAUSAL_ORIGINAL.json',
                 'CONTROLES_REUTILIZADOS.json', 'antecedente_tau160.json'):
        shutil.copyfile(ancestor/'preregistration'/name, home/'preregistration'/name)
    shutil.copyfile(package/'PRERREGISTRO_PILOTO.md', home/'preregistration/PRERREGISTRO.md')
    shutil.copyfile(package/'CERTIFICADO_F0_F5.json', home/'preregistration/preflight_certificate.json')
    shutil.copyfile(package/'CONSERVACION_F0_F5.json', home/'preregistration/preflight_preservation.json')
    shutil.copytree(package, home/'preregistration/registered_proposal', ignore=ignore)
    for name in ('library_download.py', 'library_hosted_apps.py', 'library_file_transfer.py', 'library_upload.py'):
        shutil.copyfile(args.helpers/name, home/'runtime/library'/name)
    spec = importlib.util.spec_from_file_location('P3_transport_identity_only', home/'transporte.py')
    transport = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transport)
    cfg = read(ancestor/'configuration.json')
    cfg.update(schema='CP12_P3_PREREGISTERED_PHYSICAL_PILOT',
               action='Phi_original_FV_chi_fixed_A2_plus_h2_A2_squared_over_12_plus_h4_A2_cubed_over_90',
               fixed_dimensionless_polynomial_coefficients=[1., 1/12, 1/90],
               global_sixth_order_claim=False, formal_radial_order=2,
               dop853_implementation_identity=transport.scipy_identity())
    cfg.pop('coefficient_fixed_independently_of_chi', None)
    write(home/'configuration.json', cfg)
    admin = home/'preregistration/administration'
    write(admin/'REGISTRO_LECTURA_PREFIJOS_CONTINUACION_20261016.json', dict(
        schema='CP12_P3_PREFIX_METRICS_REGISTERED_BEFORE_NEW_DATA',
        reader_sha256=sha(admin/'leer_metricas_prefijo.py'),
        original_source_relative='herramientas/diagnosticar_mediador_CP10.py',
        original_source_sha256=sha(home/'science/herramientas/diagnosticar_mediador_CP10.py'),
        metrics_threshold=.02, prefix_times=list(range(8, 160, 8)),
        only_original_time_guard_parameterized=True, extra_physical_checks_also_required=True,
        new_M2_steps_authorized=False, CP12_closed=False))
    write(admin/'REGISTRO.json', dict(schema='CP12_P3_ADMINISTRATION_REGISTERED_BEFORE_M2',
        administrative_files={p.name: sha(p) for p in admin.iterdir() if p.is_file()},
        prefix_reader_sha256=sha(admin/'leer_metricas_prefijo.py'),
        prefix_registration_sha256=sha(admin/'REGISTRO_LECTURA_PREFIJOS_CONTINUACION_20261016.json'),
        scientific_kernels_changed=False, scope='Administration only, P3 action registered separately',
        historical_generic_controls_reused_not_rerun=True, scientific_gates_changed=False,
        no_solver_restart=True, CP12_closed=False))
    write(home/'preregistration/registro_transporte.json', dict(
        schema='CP12_P3_EXACT_TRANSPORT_BINDING_BEFORE_M2',
        files={n: sha(home/n) for n in ('transporte.py', 'controlador_transporte.py',
                                        'seleccion_canonica.py', 'CONTROLES_SINTETICOS.json')},
        generic_transport_source_bytes_identical_to_historical_certificate=True,
        synthetic_controls_passed=True, registered_before_new_M2=True,
        new_P3_one_interval_control_required=True, CP12_closed=False))
    captured = [p for p in home.rglob('*') if p.is_file()
                and p.relative_to(home).parts[0] not in ('science', 'prior', 'runtime')]
    hashes = {p.relative_to(home).as_posix(): sha(p) for p in captured}
    uid = uuid.uuid4().hex
    run_id = hashlib.sha256(json.dumps(dict(uuid=uid, sources=hashes), sort_keys=True).encode()).hexdigest()
    branch = 'ciencia/cp12-residuo-p3-20261018'
    write(home/'preregistration/nueva_identidad.json', dict(execution_uuid=uid,
        execution_run_id=run_id, branch=branch, run_relative='outputs', initial_frontier=0,
        supervision_source_sha256=hashes['coordinator.py'], captured_sources=hashes,
        kind='NEW_P3_EXPERIMENT_NOT_A_RECOVERY_OF_FAILED_P2'))
    write(home/'preregistration/ubicacion.json', dict(execution_uuid=uid, branch=branch,
        ancestor_state_sha256='abfae6d6b88a1f5b6a58df1657ea3f860a81b02835fe6598b97315da3c1f3ba4',
        scope='Forensic causal antecedent only; never used as Cauchy state', execution_home=str(home)))
    write(home/'preregistration/registro_publico.json', dict(registered_before_M2=False,
        captured_sources=hashes, physical_steps_executed=0, concrete_identity_publication_pending=True))
    write(home/'outputs/procedencia.json', dict(schema='CP12_NEW_P3_NUMERICAL_TRIAL_RECEIPT',
        execution_run_id=run_id, execution_uuid=uid, kind='New fully coupled M2 P3 chi composition',
        physical_initial_time=0, time=0, status='NO_INICIADA', segments=[],
        physical_accepted_steps=[0, 0], original_CP10_reproduction=False,
        original_private_receipt_recreated=False, output_hashes={}, original14_scientific_sources_changed=False,
        old_P2_resumed=False, correction_validated=False, CP12_closed=False))
    identity = read(home/'preregistration/identidad_cientifica_original.json')
    for name, expected in {**identity['code_hashes'], **identity['input_hashes']}.items():
        assert sha(home/'science'/name) == expected, name
    for p in (home/'science').rglob('*'):
        if p.is_file():
            p.chmod(0o444)
    result = dict(home=str(home), execution_uuid=uid, execution_run_id=run_id,
                  at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  captured_sources=hashes, M2_steps_executed=0, CP12_closed=False)
    write(home/'preregistration/INSTANCIA.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
