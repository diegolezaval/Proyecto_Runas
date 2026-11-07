"""Comprueba el alcance del cambio y sus rechazos sin transferir ni evolucionar."""
import argparse
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import capacidad_separada as capacity
import continuar as original
import continuar_desde_transporte as runner
import preservar as p
from probar import item, receipt, refused


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    baseline = Path(original.__file__).read_text()
    adapter = Path(runner.__file__).read_text()
    after_capacity = "        capacity_sha="
    checks = {
        'shared_original_restore_activate_metrics_validation': all(
            getattr(original, name) is getattr(runner, name)
            for name in ('restore', 'activate', 'metrics', 'validate')),
        'identical_activation_evolution_saves_scientific_gates_and_suspension': (
            baseline.split(after_capacity, 1)[1] == adapter.split(after_capacity, 1)[1]),
    }
    native = receipt(28.8)
    native['recovery']['original_audits']['transport']['state_sha256'] = 'TRANSPORT'
    public_request = dict(observer_clock=24, archive_path='PUBLIC_REFERENCE.zip', bytes=231000000, sha256='PUBLIC')
    public = dict(github_asset_id=2, recovery={'original_audits': {
        'boundary': native['recovery']['original_audits']['boundary']}})
    reg = dict(capacity_mode=capacity.MODE, kind='transport', allocation_id='test',
               closed_boundary=24, clock=28.8, transport_sha256='TRANSPORT',
               public_capacity_reference={'github_asset_id': 1})
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / 'REGISTRO.json').write_text(json.dumps(reg))
        home = root / 'home'
        (home / 'runtime').mkdir(parents=True)
        ring = home / 'runtime/HIBRIDO_ROTACION.json'
        ring.write_text('previous backups')

        def prepare_public(archive, output, label, registration, auditor):
            assert archive == root / 'public-reference.zip'
            p.write(output / 'publico/ASSET_GITHUB.json', {'id': 2})
            return public_request

        def run(name):
            return capacity.preserve_capacity(home, root / name, reg, root / 'REGISTRO.json',
                root / 'public-reference.zip', root, root)

        with patch.object(capacity, 'prepare_public_reference', side_effect=prepare_public), \
                patch.object(p, 'prepare', return_value={'kind': 'transport'}) as prepare, \
                patch.object(p, 'native', return_value=native) as save_native, \
                patch.object(p, 'public', return_value=public) as save_public, \
                patch.object(p, 'unchanged'), patch.object(p, 'record_transport') as rotate:
            combined = run('accepted')
            checks['separate_destinations_keep_exact_native_origin_and_public_reference'] = (
                prepare.call_args.args[3:6] == ('transport', 28.8, 24) and
                save_native.call_args.args[0] == {'kind': 'transport'} and
                save_public.call_args.args[0] is public_request and
                combined['registry_sha256'] == p.sha(root / 'REGISTRO.json') and not rotate.called)
            checks['complete_native_capacity_is_recognized_by_original_incident_scan'] = (
                p.read(root / 'accepted/nativo/ACEPTACION_COMBINADA.json') == combined)
            save_public.reset_mock()
            save_native.side_effect = RuntimeError('fallo sintético nativo')
            checks['native_failure_keeps_prior_backups_and_blocks_publication_and_activation'] = (
                refused(lambda: run('native_failed')) and ring.read_text() == 'previous backups' and
                not save_public.called and not (root / 'native_failed/ACEPTACION_COMBINADA.json').exists())
            save_native.side_effect = None
            save_public.side_effect = ValueError('recuperación pública distinta')
            checks['public_failure_keeps_prior_backups_and_blocks_activation'] = (
                refused(lambda: run('public_failed')) and ring.read_text() == 'previous backups' and
                not (root / 'public_failed/ACEPTACION_COMBINADA.json').exists())
            save_public.side_effect = None
            save_public.return_value = dict(public, github_asset_id=1)
            checks['historical_public_asset_cannot_satisfy_new_capacity'] = refused(lambda: run('historical'))
            with patch.object(capacity, 'prepare_public_reference', side_effect=ValueError('referencia distinta')):
                save_native.reset_mock()
                checks['wrong_reference_rejected_before_native_write'] = (
                    refused(lambda: run('wrong_reference')) and not save_native.called)
        incident_home = root / 'incident_home'
        (incident_home / 'runtime').mkdir(parents=True)
        proof = 'administracion_continuacion_20261030/INCIDENTE_SESION_1.json'
        p.write(incident_home / proof, dict(recovery_kind='protected_administrative_transport',
            latest_exact_local_observer_clock=30, exact_state_sha256='RECOVERED'))
        prior = [item(27.2), item(28.8)]
        rescue = dict(kind='transport', clock=30, inherited_verified_transports=prior,
            source_library_file_id='INCIDENT', source_archive_sha256='ZIP', transport_sha256='RECOVERED',
            protected_incident_recovery=dict(protected=True, observer_clock=30, library_file_id='INCIDENT',
                sha256='ZIP', embedded_record=proof, embedded_record_sha256=p.sha(incident_home / proof)))
        p.initialize_rotation(incident_home, rescue)
        checks['protected_exact_rescue_preserves_both_prior_periodic_transports'] = (
            p.read(incident_home / 'runtime/HIBRIDO_ROTACION.json')['retained'] == prior)
        checks['protected_rescue_rejects_different_exact_state'] = refused(
            lambda: p.initialize_rotation(incident_home, dict(rescue, transport_sha256='WRONG')))
    result = dict(schema='CP12_P3_SPLIT_CAPACITY_BOUNDED_TESTS_V1', passed=all(checks.values()),
                  checks=checks, test_count=len(checks), M2_steps_executed=0, remote_mutations_executed=0)
    p.write(args.salida, result)
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
