"""Publish a stopped spatial negative and its registered saved-data diagnosis.

Standard-library reporting only. No model, solver or observer is imported.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

BASE = Path('checkpoints/CP12/continuacion_20261018/negativo_espacial_tau0080')
REPORT = 'informes/NEGATIVO_ESPACIAL_MIXTO_TAU80_CP12_20261018.md'
METRICS = [
    ('norm_relative_sup_error', 'Norma temporal suprema'),
    ('final_complex_nonradial_field_error_over_initial_norm', 'Campo Φ'),
    ('final_phi_phase_space_error_over_initial_norm', 'Fases Φ'),
    ('final_mediator_nonradial_error_over_initial_norm', 'Campo χ'),
    ('final_mediator_phase_space_error_over_initial_norm', 'Fases χ'),
]


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(home, repo, diagnosis):
    full_path = home / 'proofs/tau0080_permanent.json'
    prefix_path = home / 'analysis/lectura_prefijos_continuacion/TAU0080_RESULTADO.json'
    negative_path = home / 'proofs/NEGATIVO_ESPACIAL_TAU0080_20261017_permanent.json'
    exit_path = home / 'runtime/observed_guardian_exit.json'
    full, prefix, negative, own_exit, causal = map(read, [full_path, prefix_path, negative_path, exit_path, diagnosis])
    audit = full['independent_extracted_audit']
    assert full['time'] == prefix['time'] == causal['time'] == 80
    assert full['passed'] and full['all_payload_hashes_verified'] and audit['passed']
    assert len(audit['tests']) == 28 and all(audit['tests'].values()) and audit['M2_steps_executed'] == 0
    assert not prefix['prefix_pair_limits_met'] and prefix['original_spatial_threshold'] == .02
    assert prefix['M2_steps_executed'] == causal['new_M2_steps'] == 0
    assert causal['all_input_bytes_unchanged'] and causal['previously_stored_metrics_read_only']
    assert causal['initial_Cauchy_arrays_equal'] and causal['same_actual_time_and_initial_normalizations']
    assert causal['sufficiency']['mixed']['coupled']['operador_chi']['meets_all_three_windows']
    assert causal['sufficiency']['mixed']['raw']['operador_chi']['meets_all_three_windows']
    assert not causal['sufficiency']['original']['raw']['operador_chi']['meets_all_three_windows']
    assert all(not meta['meets_all_three_windows'] for name, meta in causal['sufficiency']['mixed']['coupled'].items()
               if name != 'operador_chi')
    assert full['state_sha256'] == prefix['source_state_sha256'] == causal['state_sha256']
    assert full['receipt_sha256'] == prefix['source_receipt_sha256']
    assert sha(home / 'outputs/MIXTO_par_estado.npz') == full['state_sha256']
    assert sha(home / 'outputs/procedencia.json') == full['receipt_sha256']
    assert own_exit['returncode'] == 2 and negative['passed'] and negative['scientific_gate_failed']
    assert negative['all_payload_hashes_verified']
    events = [json.loads(line) for line in (home / 'runtime/events.jsonl').read_text().splitlines()]
    boundary = [e for e in events if e['event'] == 'BOUNDARY_PERMANENTLY_VERIFIED' and e['time'] == 80]
    gate = [e for e in events if e['event'] == 'SPATIAL_PREFIX_GATE_BEFORE_NEXT_M2_SEGMENT' and e['time'] == 80]
    saved = [e for e in events if e['event'] == 'MIXTO_ADDITIONAL_EVIDENCE_PERMANENTLY_RECOVERED_AND_HASH_VERIFIED'
             and e['label'] == 'NEGATIVO_ESPACIAL_TAU0080_20261017']
    assert len(boundary) == len(gate) == len(saved) == 1 and not gate[0]['all_five_pair_limits_met']
    assert not any(e['event'] == 'MIXTO_TRANSPORT_BEGIN_OR_RESUME_SEGMENT' and e['to_time'] > 80 for e in events)
    times = [e['at'] for e in (boundary[0], gate[0], saved[0], own_exit, causal)]
    assert times == sorted(times)
    destination = repo / BASE
    destination.mkdir(parents=True, exist_ok=False)
    for source, name in [(diagnosis, 'RESULTADO_DIAGNOSTICO.json'), (negative_path, 'CONSERVACION_NEGATIVO.json'),
                         (exit_path, 'SALIDA_PROPIA_OBSERVADA.json')]:
        shutil.copyfile(source, destination / name)
    stop = dict(schema='CP12_SPATIAL_NEGATIVE_ORDER_AND_OWN_EXIT_OBSERVED', time=80,
        events=[boundary[0], gate[0], saved[0]], own_observed_exit=own_exit, diagnosis_at=causal['at'],
        no_next_M2_segment_executed=True, scientific_gate_failed=True, original_threshold=.02,
        last_all_five_spatial_gates_positive_boundary=72, numerical_full_frontier_recovered_and_audited=80,
        forensic_recovery_only=True, automatic_continuation_authorized=False,
        old_inaccessible_executors_termination_assumed=False, accepted_scientific_checkpoint='CP11', CP12_closed=False)
    write(destination / 'SUSPENSION.json', stop)
    provenance = dict(schema='CP12_SAVED_SPATIAL_NEGATIVE_DIAGNOSIS_PUBLICATION',
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), time=80,
        source_hashes={str(p): sha(p) for p in [full_path, prefix_path, negative_path, exit_path, diagnosis]},
        registered_diagnosis='checkpoints/CP12/continuacion_20261017/diagnosticar_negativo_espacial.py',
        registered_diagnosis_sha256=sha(repo / 'checkpoints/CP12/continuacion_20261017/diagnosticar_negativo_espacial.py'),
        original_state_sha256=causal['original_state_sha256'], mixed_state_sha256=causal['state_sha256'],
        reporting_script_sha256=sha(Path(__file__)), reporting_imports_model_or_solver=False,
        M2_steps_executed=0, inputs_not_modified=True, CP12_closed=False)
    write(destination / 'PROCEDENCIA.json', provenance)
    c = prefix['comparison']
    chi = {window: tables['coupled']['operador_chi'] for window, tables in causal['tables']['mixed'].items()}
    ratios = causal['coupled_response_norm_ratios']
    original, mixed = causal['original_observed_phase_error'], causal['mixed_observed_phase_error']
    phi_original = causal['original_coupled_chi_operator_induced_Phi_norm']
    phi_mixed = causal['mixed_coupled_chi_operator_induced_Phi_norm']
    lines = ['# CP12: negativo espacial mixto en τ80 y diagnóstico pasivo', '',
        f'La versión Φ-FV / χ-K4 queda **suspendida en τ80**: fases χ = **{100*mixed:.15g} % >2 %**. '
        'Las otras cuatro métricas pasan. La cápsula completa fue recuperada y auditada con 28 controles positivos; '
        'el negativo se conservó y recuperó antes de la salida propia observada con código2. No se ejecutó 80→88. '
        'La última frontera con las cinco puertas positivas es τ72. CP12 permanece abierto; CP11 sigue aceptado.', '',
        '## Puertas y conservación', '', '| Métrica original | Error (%) | Límite (%) | Decisión |',
        '|---|---:|---:|---|']
    for key, label in METRICS:
        lines.append(f'| {label} | {100*c[key]:.12g} | 2 | {"Pasa" if prefix["prefix_pair_gates"][key] else "NEGATIVO"} |')
    lines += ['', f'Energía FV máxima {max(m["maxe_original"] for m in audit["metadata"]):.12g}; '
        f'energía mixta máxima {max(m["maxe"] for m in audit["metadata"]):.12g}; ambas ≤2e-4. '
        f'Carga máxima {max(m["maxq"] for m in audit["metadata"]):.12g} ≤1e-9. '
        f'Cierre/orden máximo {max(audit["maximum_errors"].values()):.12g} ≤.001; '
        f'Parseval {audit["maximum_errors"]["modal_parseval"]:.12g} ≤2e-11. '
        'Identidad, simetría, configuración, fuentes, semillas y contadores pasan sus controles originales.', '',
        '| Evidencia recuperada | Bytes | SHA256 |', '|---|---:|---|',
        f'| Frontera completa80 | {full["zip_bytes"]} | `{full["zip_sha256"]}` |',
        f'| Negativo espacial80 | {negative["zip_bytes"]} | `{negative["zip_sha256"]}` |', '',
        f'Estado80: `{full["state_sha256"]}`. Recibo: `{full["receipt_sha256"]}`. '
        f'Configuración: `{full["configuration_sha256"]}`. El recibo conserva el tramo terminado; '
        'la suspensión científica está en el certificado de secuencia, sin reescribir la historia.', '',
        'La auditoría completa terminó a '+boundary[0]['at']+', la lectura negativa a '+gate[0]['at']+
        ', la conservación del negativo a '+saved[0]['at']+' y la salida propia a '+own_exit['at']+
        '. El diagnóstico condicionado se ejecutó después, a '+causal['at']+'. '
        'Las sesiones anteriores inaccesibles conservan actividad desconocida.', '',
        '## Causa condicionada por los observadores guardados', '',
        f'Se aplicó el diagnóstico prerregistrado a la extracción independiente80 y a la fila original del mismo τ80 '
        f'conservada en el NPZ original160. Datos iniciales y configuración coinciden exactamente. '
        f'El error original era {100*original:.12g} % y el mixto {100*mixed:.12g} % '
        f'(reducción de norma {100*(1-mixed/original):.10g} %). Cero pasos M2; los bytes de entrada permanecen idénticos.', '',
        'El **operador χ acoplado sigue siendo suficiente en las tres ventanas** con los criterios originales '
        '(proyección≥.8, coseno≥.8 y reducción cuadrática al retirar≥.5). '
        'El residuo continúa atribuido a ese canal radial dentro de esta descomposición. '
        'Las puertas energéticas y de observadores positivas delimitan un fallo del acuerdo espacial.', '',
        '| Ventana original | Norma original del canal χ (%) | Norma mixta (%) | Mixta/original | Proyección mixta | Coseno mixto | Reducción cuadrática al retirar (%) |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for window, m in chi.items():
        ratio = ratios[window]['operador_chi']
        lines.append(f'| {window} | {100*ratio["original_relative_norm"]:.12g} | {100*m["relative_error"]:.12g} | '
            f'{ratio["mixed_over_original"]:.12g} | {m["signed_projection"]:.12g} | {m["cosine"]:.12g} | {100*m["removal_squared_reduction"]:.12g} |')
    lines += ['', f'La reducción de norma del canal χ acoplado es '
        f'{100*(1-ratios["core_phase"]["operador_chi"]["mixed_over_original"]):.10g} % en core_phase '
        '(aproximadamente48,4 % en las tres ventanas). Este cociente de un prefijo no decide la puerta causal final de τ160. '
        'El canal χ libre también satisface ahora las tres ventanas; en el original del mismo tiempo no las satisfacía. '
        'Los otros cuatro canales acoplados no son suficientes individualmente. '
        f'La norma absoluta guardada de Φ inducida por el canal χ acoplado pasa de {phi_original:.12g} a {phi_mixed:.12g} '
        f'(razón {phi_mixed/phi_original:.12g}), sin identificar una fracción de retorno puro χ→Φ→χ.', '',
        f'El comparador localiza {100*next(b["fraction_of_chi_squared_difference"] for b in c["chi_radial_bands"] if b["r_min"]==10):.12g} % '
        f'de la diferencia cuadrática de χ en 10≤r<20; multipolos ℓ2={100*c["chi_multipole_fractions"]["2"]:.12g} % '
        f'y ℓ4={100*c["chi_multipole_fractions"]["4"]:.12g} %. La rotación descriptiva no intervino en la puerta.', '',
        '## Todos los canales: signos y cancelaciones conservados', '',
        'Las normas aisladas no se suman como potencias independientes. La reducción cuadrática es un contraste '
        'pasivo condicionado a las historias adquiridas; un valor negativo significa que retirar ese canal empeora '
        'el residuo en ese contraste. Las matrices Gram originales de las dos ventanas cortas permanecen en el JSON.', '',
        '| Ventana | Familia | Canal | Norma original (%) | Norma mixta (%) | Proyección mixta | Coseno mixto | Reducción cuadrática (%) |',
        '|---|---|---|---:|---:|---:|---:|---:|']
    for window, tables in causal['tables']['mixed'].items():
        for family, channels in tables.items():
            for name, m in channels.items():
                o = causal['tables']['original'][window][family][name]
                lines.append(f'| {window} | {family} | {name} | {100*o["relative_error"]:.10g} | {100*m["relative_error"]:.10g} | '
                    f'{m["signed_projection"]:.10g} | {m["cosine"]:.10g} | {100*m["removal_squared_reduction"]:.10g} |')
    lines += ['', '## Alcance y siguiente investigación', '',
        'La corrección reduce el error frente al original, pero deja un residuo radial χ suficiente para superar '
        'el 2 % a τ80. Esta versión no autoriza el horizonte160. Se conserva su negativo junto con el K4 de tres campos '
        'fallido y el CP12 original, sin relajar criterios, ajustar fase, repetir tramos o lanzar otra corrección.', '',
        'Una nueva evolución requerirá una pregunta y una derivación/prerregistro nuevos sobre el residuo identificado. '
        'Quedan pendientes la causalidad final de160 y las pruebas justificadas de convergencia adicional, referencia, '
        'estabilidad y robustez. No se reconstruyeron grupos del núcleo completo sin sus historias de campos, '
        'no se estimó una fracción pura del bucle y no se afirmó orden de convergencia a partir de dos mallas. '
        'Toda la evidencia es matemática o numérica del modelo M2, sin validación física experimental.', '',
        f'Entradas y salida verificables: `{BASE}/`. La conservación permanente del diagnóstico se documenta '
        'en `CONSERVACION_DIAGNOSTICO.json` junto a esos archivos. Main sigue en CP11 y PR#2 en borrador.', '']
    (repo / REPORT).write_text('\n'.join(lines))
    state_path = repo / 'estado_progreso.json'
    state = read(state_path)
    stages = json.dumps(state['stages'], sort_keys=True)
    assert state['latest_verified_cp12_mixed_restart']['time'] == 80
    assert not any(x.get('campaign') == 'CP12_PILOTO_MIXTO_PHI_FV_CHI_K4' for x in state['numerical_runs_paused'])
    running = [x for x in state['numerical_runs_in_progress'] if x.get('campaign') == 'CP12_PILOTO_MIXTO_PHI_FV_CHI_K4']
    assert len(running) == 1
    paused = dict(running[0], status='PAUSADA_PUERTA_ESPACIAL_TAU80', latest_certified_time=80,
        last_all_five_spatial_gates_positive_boundary=72, evidence=str(BASE / 'SUSPENSION.json'),
        latest_recoverable_observer_clock=80, automatic_continuation_authorized=False,
        own_exit_observed=own_exit, scientific_gate_failed=True)
    state['numerical_runs_in_progress'] = [x for x in state['numerical_runs_in_progress'] if x not in running]
    state['numerical_runs_paused'].append(paused)
    state['automatic_continuation_paused'] = True
    state['latest_verified_cp12_mixed_restart'].update(spatial_gate_failed=True, forensic_only=True,
        automatic_continuation_authorized=False, last_all_five_spatial_gates_positive_boundary=72)
    state['latest_verified_cp12_mixed_transport'].update(historical_before_spatial_negative80=True,
        automatic_continuation_authorized=False)
    activity = state['execution_activity']
    activity.update(mixed_candidate_status='SUSPENDIDO_PUERTA_ESPACIAL_TAU80_NEGATIVO_CONSERVADO_DIAGNOSTICADO',
        mixed_candidate_exit_code_observed=2, mixed_candidate_last_all_five_spatial_gates_positive_boundary=72,
        mixed_candidate_latest_recoverable_observer_clock=80, mixed_candidate_automatic_continuation_authorized=False)
    activity['session_20261018_0730'].update(status='OWN_EXIT_OBSERVED_CODE2_SPATIAL_NEGATIVE',
        latest_full_trial_frontier=80, next_target=None, own_exit_observed=own_exit,
        negative_evidence=str(BASE / 'SUSPENSION.json'))
    for item in state['research_in_progress']:
        if item.get('campaign') == 'CP12_DERIVACION_VARIACIONAL_MIXTA':
            item.update(status='NEGATIVO_ESPACIAL_TAU80_DIAGNOSTICADO_CAUSA_CONDICIONADA',
                scope='Φ-FV/χ-K4 suspendido en80. Operadorχ acoplado suficiente en tres ventanas; cero pasos en diagnóstico. Sin nueva corrección automática.',
                evidence=str(BASE / 'RESULTADO_DIAGNOSTICO.json'))
    state['latest_cp12_mixed_spatial_negative'] = dict(time=80, threshold=.02, metric='final_mediator_phase_space_error_over_initial_norm',
        observed=mixed, suspension=str(BASE / 'SUSPENSION.json'), negative_preservation=str(BASE / 'CONSERVACION_NEGATIVO.json'),
        diagnosis=str(BASE / 'RESULTADO_DIAGNOSTICO.json'), report=REPORT,
        scientific_gate_failed=True, automatic_continuation_authorized=False, CP12_closed=False)
    action = 'Ensayo mixto suspendido enτ80 por fasesχ>2%, negativo recuperado y causa condicionada diagnosticada con cero pasosM2. Conservar evidencia; ninguna continuación o corrección nueva automática. Toda nueva evolución necesita pregunta, derivación y prerregistro nuevos. CP12 abierto; CP11 aceptado.'
    state['next_actions'][0] = state['next_calculation'] = action
    state['do_not_repeat'].append('Ensayo mixto Φ-FV/χ-K4 0→80: conservar fronteras, transportes y negativo espacial80. No repetir A–D ni reanudar desde72/78,4/79,6 para eludir la puerta negativa.')
    state['history'].append(dict(event='CP12_MIXTO_NEGATIVO_ESPACIAL_TAU80_SUSPENDIDO_Y_DIAGNOSTICADO',
        at=provenance['at'], time=80, report=REPORT, evidence=str(BASE / 'SUSPENSION.json'),
        M2_steps_in_diagnosis=0, own_exit_code_observed=2, closed_stages=[], reopened_stages=[],
        accepted_scientific_checkpoint_unchanged='CP11', correction_validated=False, CP12_closed=False))
    assert json.dumps(state['stages'], sort_keys=True) == stages
    write(state_path, state)
    assert provenance['source_hashes'] == {name: sha(Path(name)) for name in provenance['source_hashes']}
    return dict(time=80, continuation_suspended=True, M2_steps_in_diagnosis=0, report=REPORT,
                original_error=original, mixed_error=mixed, causal_operator_chi_sufficient_all_three=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for key in ('home', 'repo', 'diagnosis'):
        parser.add_argument('--' + key, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.home.resolve(), args.repo.resolve(), args.diagnosis.resolve()), ensure_ascii=False))
