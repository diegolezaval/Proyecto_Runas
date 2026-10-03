"""Verificación científica y de procedencia CP10 sin avanzar integraciones."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from threadpoolctl import threadpool_limits
from ejecutar_con_procedencia import verify_receipt
from diagnosticar_mediador_CP10 import load, compare
from comparar_mediador_CP10 import completed_case, assert_unchanged_criteria
from continuar_no_radial_m2 import Evolution, seed

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'validacion/P06/no_radial/CP10'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify():
    tests = {}
    criteria = json.loads((ROOT/'datos/ensayo_mediador_CP10.json').read_text())['criteria']
    original_criteria = json.loads((ROOT/'datos/ensayo_no_radial_CP06.json').read_text())['criteria']
    assert_unchanged_criteria(criteria, original_criteria)
    tests['all_protocol_thresholds_match_original'] = True
    receipts = [verify_receipt(p) for p in sorted(BASE.glob('*/procedencia.json'))]
    tests['four_closed_receipts_valid'] = len(receipts) == 4 and all(x['passed'] and x['status'] == 'COMPLETADA' for x in receipts)
    comparisons = list(BASE.glob('comparacion_final__*/resultados.json'))
    if len(comparisons) != 1:
        raise ValueError('Comparación final no disponible o ambigua')
    result = json.loads(comparisons[0].read_text())
    tests['final_comparison_observed_single_thread_pools'] = bool(result['observed_threadpools']) and all(p['num_threads'] == 1 for p in result['observed_threadpools'])
    diagnostic_receipt = next(BASE.glob('diagnostico_guardado__*/procedencia.json'))
    diagnostic = json.loads(diagnostic_receipt.read_text())
    clarification = diagnostic['provenance_clarifications'][0]
    original_diagnostic = json.loads((diagnostic_receipt.parent/clarification['original_receipt']).read_text())
    tests['diagnostic_thread_observation_unknown_and_original_preserved'] = clarification['observed_threads_at_execution'] is None and clarification['scientific_output_changed'] is False and diagnostic['identity'] == original_diagnostic['identity'] and all(diagnostic['output_hashes'].get(k) == v for k,v in original_diagnostic['output_hashes'].items())
    prior = json.loads((ROOT/'trazabilidad/CP09_entrada/archivos_sha256.json').read_text())
    original_data = [p for p in prior if p.startswith(('validacion/','graficos/','fichas/','hoja_ruta_original/'))]
    tests['all_original_numerical_results_failures_figures_and_roadmap_unchanged'] = all((ROOT/p).is_file() and sha(ROOT/p) == prior[p] for p in original_data)
    recovered = []
    for name, expected in prior.items():
        current, old = ROOT/name, ROOT/'trazabilidad/CP09_entrada'/name
        recovered.append(current.is_file() and sha(current) == expected or old.is_file() and sha(old) == expected)
    tests['all_833_CP09_files_recoverable'] = all(recovered)
    for name in ['herramientas/modelo_m2.py','herramientas/continuar_no_radial_m2.py','herramientas/continuar_no_radial_adaptativo.py','herramientas/fuerza_potencial_m2.c','herramientas/acelerar_fuerza_m2.py','datos/theta_comun.json','datos/ensayo_no_radial_CP06.json']:
        tests['unchanged:'+name] = sha(ROOT/name) == prior[name]
    original_state = json.loads((ROOT/'trazabilidad/CP09_entrada/estado_progreso.json').read_text())
    state = json.loads((ROOT/'estado_progreso.json').read_text())
    original_stages = {s['id']: s for s in original_state['stages']}
    stages = {s['id']: s for s in state['stages']}
    tests['all_33_stage_identities_preserved'] = len(state['stages']) == len(stages) == 33 and stages.keys() == original_stages.keys()
    tests['other_29_stage_records_identical'] = all(s == original_stages[name] for name,s in stages.items() if name not in ['E03','E04','RES0','RES1'])
    tests['E00_E01_C0_closed_records_identical'] = all(next(s for s in state['stages'] if s['id'] == name) == next(s for s in original_state['stages'] if s['id'] == name) for name in ['E00','E01','C0'])
    tests['all_original_stage_gates_and_dependencies_identical'] = all(s['gate_original'] == o['gate_original'] and s['dependencies'] == o['dependencies'] for s, o in zip(state['stages'], original_state['stages']))
    tests['general_research_stages_remain_partial'] = all(next(s for s in state['stages'] if s['id'] == name)['status'] == 'PARCIAL' for name in ['E03','E04','RES0','RES1'])
    tests['no_active_runs_in_delivery'] = not state['numerical_runs_in_progress'] and not state['research_in_progress']
    tests['no_complete_primordials_declared'] = state['complete_primordials'] == 0
    full_source = ROOT/'validacion/P06/preparacion/w7.20_h0.100_dt0.0020_R1300_T1200_estado.npz'
    for case in ['temporal_h0125','espacial_h00625']:
        folder, saved = completed_case(case)
        data = load(saved)
        cfg = data['configuration']
        sim = Evolution(cfg['dx'],cfg['radius'],cfg['L'])
        q0, v0, transfer = seed(sim,cfg['eps'])
        tests[case+':initial_Cauchy_fields_exactly_from_saved_CP04'] = np.array_equal(data['initial_q'],q0) and np.array_equal(data['initial_v'],v0)
        tests[case+':source_hash'] = transfer['source_sha256'] == sha(full_source)
        tests[case+':all_arrays_finite'] = all(np.isfinite(data[k]).all() for k in ['q','v','initial_q','initial_v','rows'])
        tests[case+':completed_window'] = data['time'] == 160 and data['rows'][0,0] == 0 and data['rows'][-1,0] == 160 and np.all(np.diff(data['rows'][:,0])>0)
        receipt = json.loads((folder/'procedencia.json').read_text())
        segments = receipt['segments']
        tests[case+':real_restart_from_valid_pilot'] = len(segments) >= 2 and segments[0]['final_time'] == 8 and bool(segments[1]['resumed_from_hashes']) and segments[-1]['final_time'] == 160
        interruptions = [(i, s) for i, s in enumerate(segments) if s['status'] == 'INTERRUMPIDA']
        tests[case+':interrupted_segments_preserved_and_recovered'] = bool(interruptions) and all(
            i + 1 < len(segments) and s['recovered_state_sha256'] == segments[i+1]['resumed_from_hashes'].get(s['recovered_state'])
            and 8 < s['recovered_time'] < 160 and s.get('interruption_detected_at')
            for i, s in interruptions)
        tests[case+':no_unclosed_receipt_segment'] = all(s['status'] != 'EN_PROGRESO' for s in segments)
        audit = json.loads((folder/'auditoria_fuerza_fusionada.json').read_text())
        tests[case+':C_Numpy_force_equivalence'] = audit['passed'] and max(audit['errors']) < 2e-12
    temporal = completed_case('temporal_h0125')[1]
    old = load(ROOT/'validacion/P06/no_radial/dop853e9_L4_h0.125_dt0.0200_R220_eps0.020_T160_estado.npz')
    newer = load(temporal)
    tests['temporal_control_keeps_initial_data_exact'] = np.array_equal(old['initial_q'],newer['initial_q']) and np.array_equal(old['initial_v'],newer['initial_v'])
    keys = ['norm_relative_sup_error','final_complex_nonradial_field_error_over_initial_norm','final_phi_phase_space_error_over_initial_norm','final_mediator_nonradial_error_over_initial_norm','final_mediator_phase_space_error_over_initial_norm']
    for row in result['comparisons']:
        recalculated = compare(ROOT/row['left'],ROOT/row['right'])
        tests[row['control']+':saved_metrics_recovered'] = all(np.isclose(row[k],recalculated[k],rtol=1e-12,atol=1e-14) for k in keys)
        tests[row['control']+':unchanged_gate_correctly_applied'] = row['threshold'] == .02 and row['passed'] == all(recalculated[k] < .02 for k in keys)
    gate = all(x['passed'] for x in result['comparisons']+result['run_gates']+result['inherited_controls']) and result['inherited_box_control']['passed'] and not result['unaddressed_historical_issues']
    tests['negative_or_positive_decision_matches_data'] = result['finite_campaign_passed'] == gate and result['status'] == ('SUBENSAYO_FINITO_SUPERADO' if gate else 'REFINAMIENTO_PENDIENTE')
    tests['no_chi_phase_fitting_or_continuum_claim'] = not result['chi_phase_fitted_for_acceptance'] and not result['continuum_error_certified'] and not result['angular_spatial_temporal_joint_convergence_certified']
    # NumPy comparisons may return np.bool_; the administrative JSON uses native bools.
    tests = {name: bool(value) for name, value in tests.items()}
    return dict(passed=all(tests.values()),tests=tests,decision=result['status'],receipt_count=len(receipts),
                scientific_campaigns_repeated=False,new_integration_steps_executed=False,
                scope='Recibos, estados, construcción inicial, conservación histórica y recuperación de comparaciones. No certificado del continuo ni dispositivo.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path)
    args = parser.parse_args()
    try:
        with threadpool_limits(limits=1):
            report = verify()
    except Exception as error:
        report = dict(passed=False,error=str(error))
    if args.salida:
        args.salida.parent.mkdir(parents=True,exist_ok=True)
        args.salida.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['passed'] else 1)
