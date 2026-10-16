"""Publish an existing registered offline reading; never integrate M2."""
from pathlib import Path
import argparse
import datetime
import json
import math

PREFIX = Path('checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015')
KEYS = ('norm_relative_sup_error', 'final_complex_nonradial_field_error_over_initial_norm',
        'final_phi_phase_space_error_over_initial_norm', 'final_mediator_nonradial_error_over_initial_norm',
        'final_mediator_phase_space_error_over_initial_norm')
READER_SHA = '3043d3f58bb0a28cac20a528d3680408191a75c18a0c36505884e0cd9eac330b'
SOURCE_SHA = '41f0b56b797f9caca7601577d8db7f846d1d452e77a80940de6092be6a8fea64'
REGISTRATION = 'b805708d3faedc37118164f574325d3a6ebb3d2b'


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def export(home, repo, result_path):
    result = read(result_path)
    time = result['time']
    registration = read(repo / PREFIX / 'REGISTRO_LECTURA_PREFIJOS_CONTINUACION_20261016.json')
    assert time in registration['prefix_times'] and 24 <= time < 160 and time % 8 == 0
    proof = read(home / 'proofs' / ('tau%04d_permanent.json' % time))
    assert proof['schema'] == 'CP12_MIXTO_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED'
    audit = proof['independent_extracted_audit']
    assert proof['passed'] and proof['all_payload_hashes_verified'] and audit['passed']
    assert audit['M2_steps_executed'] == 0 and len(audit['tests']) == 28 and all(audit['tests'].values())
    assert result['schema'] == 'CP12_SUPPLEMENTARY_SAVED_PREFIX_SPATIAL_AGREEMENT'
    assert result['source_state_sha256'] == proof['state_sha256']
    assert result['source_receipt_sha256'] == proof['receipt_sha256']
    assert result['reader_sha256'] == registration['reader_sha256'] == READER_SHA
    assert result['original_metric_source_sha256'] == registration['original_source_sha256'] == SOURCE_SHA
    assert result['M2_steps_executed'] == 0 and result['physical_state_and_receipt_unchanged']
    assert result['only_time_guard_parameterized'] and result['real_time_labels_preserved']
    assert not result['chi_rotation_used_for_acceptance'] and not result['correction_validated'] and not result['CP12_closed']
    assert result['original_spatial_threshold'] == registration['metrics_threshold'] == .02
    gates = {k: math.isfinite(result['comparison'][k]) and result['comparison'][k] <= .02 for k in KEYS}
    assert gates == result['prefix_pair_gates'] and all(gates.values()) == result['prefix_pair_limits_met']
    state_path = repo / 'estado_progreso.json'
    state = read(state_path)
    stages = json.dumps(state['stages'], sort_keys=True)
    initial = read(home / 'proofs/tau0000_permanent.json')
    assert state['mixed_transport_initial_capsule_sha256'] == initial['zip_sha256']
    relative = PREFIX / ('METRICAS_ESPACIALES_PREFIJO_TAU%04d.json' % time)
    captured = home / 'analysis/lectura_prefijos_continuacion' / ('TAU%04d_RESULTADO.json' % time)
    for path in (repo / relative, captured):
        if path.exists():
            assert read(path) == result, 'Do not overwrite a different certified reading'
        else:
            write(path, result)
    existing = state.get('mixed_saved_prefix_spatial_agreement', {}).get(str(time))
    if existing:
        assert existing['result'] == str(relative)
        assert existing['all_five_pair_limits_met'] == result['prefix_pair_limits_met']
        return dict(written=False, time=time, already_published=True, limits_met=all(gates.values()))
    report = 'informes/ACUERDO_ESPACIAL_PREFIJOS_MIXTOS_CP12_20261016.md'
    state.setdefault('mixed_saved_prefix_spatial_agreement', {})[str(time)] = dict(
        time=time, result=str(relative), all_five_pair_limits_met=all(gates.values()), threshold=.02,
        final_tau160_acceptance=False, M2_steps_executed=0, registration_commit=REGISTRATION)
    state['history'].append(dict(
        event='CP12_ACUERDO_ESPACIAL_PREFIJO_GUARDADO' if all(gates.values()) else 'CP12_LECTURA_ESPACIAL_PREFIJO_NEGATIVA',
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), time=time, evidence=str(relative), report=report,
        all_five_pair_limits_met=all(gates.values()), closed_stages=[], reopened_stages=[],
        M2_steps_executed=0, correction_validated=False, CP12_closed=False))
    lines = ['# CP12 · Acuerdo espacial de prefijos mixtos guardados', '',
             'Las cinco métricas originales se leen en extracciones independientes de fronteras completas, '
             'sin pasos M2 ni mutación del estado o recibo. Los porcentajes conservan normalizaciones '
             'iniciales, spline y tratamiento de fase originales. El límite es 2 % por métrica.', '',
             '| Tiempo real | Norma suprema (%) | Campo Φ (%) | Fase Φ (%) | Campo χ (%) | Fase χ (%) |',
             '|---|---:|---:|---:|---:|---:|']
    results = []
    for key, meta in sorted(state['mixed_saved_prefix_spatial_agreement'].items(), key=lambda pair: float(pair[0])):
        item = read(repo / meta['result'])
        assert item['time'] == int(key) and item['reader_sha256'] == READER_SHA
        results.append(item)
        lines.append('| ' + str(item['time']) + ' | ' + ' | '.join(format(100 * item['comparison'][k], '.10g') for k in KEYS) + ' |')
    latest = max(results, key=lambda item: item['time'])
    worst = max(latest['comparison'][k] for k in KEYS)
    lines += ['', f'En el prefijo más reciente, τ{latest["time"]}, el mayor error es {100 * worst:.12g} %. '
              f'Las cinco comparaciones {"pasan" if latest["prefix_pair_limits_met"] else "no pasan todas"} el límite original.', '',
              'τ8/16 reutilizan sus certificados sin repetir la lectura. Las nuevas fronteras siguen la extensión '
              f'registrada en `{REGISTRATION}` antes de su análisis; τ24 ya estaba adquirido al registrar '
              'esa extensión. Sólo se parametriza la comprobación temporal, con identidad AST del resto. '
              'La rotación descriptiva de χ no interviene en aceptación. Los JSON conservan todos los diagnósticos.', '',
              'El acuerdo de dos mallas en prefijos no demuestra orden de convergencia ni acepta el horizonte '
              'original τ160. Siguen pendientes reducción del mecanismo en las tres ventanas y pruebas '
              'adicionales justificadas de referencia, conservación, estabilidad y robustez. Una lectura '
              'negativa se conserva y exige suspender la continuación para investigar sin relajar las puertas.', '',
              'CP12 permanece abierto; CP11 sigue aceptado. Main, PR #2 y las 33 etapas permanecen intactos.', '']
    (repo / report).write_text('\n'.join(lines))
    if not all(gates.values()):
        action = f'Suspender el ensayo mixto por la lectura espacial negativa de τ{time}; conservar y diagnosticar su causa sin relajar criterios ni lanzar variantes automáticas. CP12 abierto.'
        state['next_actions'][0] = state['next_calculation'] = action
    assert json.dumps(state['stages'], sort_keys=True) == stages
    write(state_path, state)
    return dict(written=True, time=time, limits_met=all(gates.values()), requires_suspension=not all(gates.values()),
                M2_steps_executed=0, result=str(relative), report=report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.home.resolve(), args.repo.resolve(), args.result.resolve())))
