"""Registered offline reading of audited mixed trajectories; zero M2 steps.

Import the original reader's metrics, sufficient and onset functions unchanged.
Its CP10-exact-history entrypoint is deliberately never called or spoofed.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import sys

ORIGINAL_READER_SHA256 = 'c0e09c0383f3b5c3764bba37de2dd30a3311945e62f32f09534d49e241385244'
ORIGINAL_RESULT_SHA256 = '644a82f7fce38fbdb76e5d807a45e7ed9644e54fb58d709496b0e6ce257cf6b1'
PHYSICAL_KEYS = (
    'norm_relative_sup_error',
    'final_complex_nonradial_field_error_over_initial_norm',
    'final_phi_phase_space_error_over_initial_norm',
    'final_mediator_nonradial_error_over_initial_norm',
    'final_mediator_phase_space_error_over_initial_norm',
)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(args):
    home = args.home.resolve()
    assert not args.output.resolve().is_relative_to(home) and not args.output.exists()
    assert not (home / 'runtime/worker_started.json').exists(), 'Use an independent recovered capsule'
    state = home / 'outputs/MIXTO_par_estado.npz'
    before = digest(state)
    assert before == args.state_sha256
    certificate = read(args.certificate)
    assert certificate['passed'] and certificate['time'] == 160
    assert certificate['state_sha256'] == before
    if certificate['schema'] == 'CP12_MIXED_ADDITIONAL_INDEPENDENT_RECOVERY':
        assert certificate['exact_manifest_coverage'] and certificate['payload_hashes_verified'] > 0
        audit = certificate['independent_zero_step_audit']
    else:
        assert certificate['schema'] == 'CP12_MIXTO_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED'
        assert certificate['all_payload_hashes_verified']
        audit = certificate['independent_extracted_audit']
    assert audit['passed'] and audit['time'] == 160 and audit['M2_steps_executed'] == 0
    assert all(audit['tests'].values()) and audit['state_sha256'] == before
    assert digest(args.original_result) == ORIGINAL_RESULT_SHA256
    baseline = read(args.original_result)
    assert baseline['time'] == 160 and baseline['reproduces_CP10_exactly']
    assert digest(args.physical_result) == args.physical_result_sha256
    physical = read(args.physical_result)
    assert physical['time'] == 160 and physical['candidate'] == 'MIXTO'
    assert all(key in physical['comparison'] for key in PHYSICAL_KEYS)
    assert set(physical['original_physical_gates']) == set(PHYSICAL_KEYS) | {
        f'{i}_{key}' for i in (0, 1) for key in
        ('original_energy', 'MIXTO_energy', 'charge', 'core_charge', 'bounded_window')}
    assert physical['two_original_grid_gates_passed'] == all(physical['original_physical_gates'].values())
    assert not os.environ.get('OPENBLAS_CORETYPE')
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    runtime = home / 'runtime'
    (runtime / 'tmp').mkdir(parents=True, exist_ok=True)
    os.environ['TMPDIR'] = str(runtime / 'tmp')
    sys.pycache_prefix = str(runtime / 'pycache')
    coordinator = load_module('captured_mixed_offline_coordinator', home / 'coordinator.py')
    modules, streams, budget = coordinator.streams_and_budget(home)
    np = modules['np']
    assert all(s.t == 160 for s in streams)
    assert all(s.solver is None for s in streams)
    reader_path = home / 'science/herramientas/interpretar_presupuesto_CP12.py'
    assert digest(reader_path) == ORIGINAL_READER_SHA256
    reader = load_module('original_cp12_metrics_for_mixed_reading', reader_path)
    obs = modules['obs']
    sc, sf = [s.sim for s in streams]
    dq = obs.interpolate(sc, streams[0].q, sf) - streams[1].q
    dv = obs.interpolate(sc, streams[0].v, sf) - streams[1].v
    fine = streams[1]
    scale = obs.chi_inner(sf, fine.initial_q[2], fine.initial_v[2], fine.initial_q[2], fine.initial_v[2])
    raw_q, raw_v = budget.family_arrays('raw', 0)
    coupled_q, coupled_v = budget.family_arrays('coupled', 0)
    q = np.concatenate([dq[2:3], raw_q[:, 0], coupled_q[:, 2]])
    v = np.concatenate([dv[2:3], raw_v[:, 0], coupled_v[:, 2]])
    core = np.array([[obs.chi_inner(sf, a, b, c, d) for c, d in zip(q, v)] for a, b in zip(q, v)])
    series = budget.rows
    final = series[-1]
    assert len(series) == 401 and final['time'] == 160
    windows = {
        'core_phase': core,
        'short_core_k4': np.array(final['short_modes']['core']['short_response_gram_matrix']),
        'short_smooth_k4': np.array(final['short_modes']['smooth']['short_response_gram_matrix']),
    }
    assert all(gram.shape == (11, 11) and np.isfinite(gram).all() for gram in windows.values())
    original = read(home / 'science/datos/ensayo_causal_chi_CP12.json')
    criteria = original['observer_criteria']
    assert criteria == baseline['criteria']
    tables, dominance, cross_terms = {}, {}, {}
    for family, names, start in [('raw', obs.BARE, 1), ('coupled', obs.COUPLED, 6)]:
        tables[family], dominance[family], cross_terms[family] = {}, {}, {}
        channels = {name: [i] for i, name in enumerate(names)}
        channels.update(reader.GROUPS[family])
        for label, gram in windows.items():
            tables[family][label] = {
                name: reader.metrics(gram, [start + i for i in ids], scale)
                for name, ids in channels.items()}
            cross_terms[family][label] = {
                'response_gram_matrix': gram[start:start+5, start:start+5].tolist(),
                'normalized_by_observed_squared_norm':
                    (gram[start:start+5, start:start+5] / max(float(gram[0, 0]), scale * 1e-10)).tolist()}
        for name in channels:
            by_window = {label: reader.sufficient(tables[family][label][name], criteria) for label in windows}
            dominance[family][name] = {'meets_all_three_windows': all(by_window.values()), 'tests_by_window': by_window}
    full = lambda a, b: float(np.sum(sf.w[:, None] * (a*a + b*b / obs.model.mediator**2)))
    closures = {}
    for family, start in [('raw', 1), ('coupled', 6)]:
        rq, rv = dq[2] - q[start:start+5].sum(0), dv[2] - v[start:start+5].sum(0)
        closures[family] = float(np.sqrt(full(rq, rv) / max(full(dq[2], dv[2]), 1e-300)))
    times, onsets = [r['time'] for r in series], {}
    for label in windows:
        window = 'core' if label == 'short_core_k4' else 'smooth'
        observed = final['observed_relative_error'] if label == 'core_phase' else final['short_modes'][window]['short_relative_error']
        threshold = criteria['onset_final_observed_norm_fraction'] * observed
        entries = {}
        for family, names in [('raw', obs.BARE), ('coupled', obs.COUPLED)]:
            for i, name in enumerate(names):
                if label == 'core_phase':
                    values = [r[family][i]['relative_error'] for r in series]
                else:
                    values = [next(m['relative_error'] for m in r['short_modes'][window]['metrics']
                                   if m['family'] == family and m['name'] == name) for r in series]
                entries[family + ':' + name] = reader.onset(values, times, threshold, criteria['onset_consecutive_samples'])
        onsets[label] = {'relative_error_threshold': threshold,
                         'consecutive_samples': criteria['onset_consecutive_samples'],
                         'first_sustained_crossing': entries}
    reduction = {}
    for label in windows:
        prior = baseline['tables']['coupled'][label]['operador_chi']['relative_error']
        current = tables['coupled'][label]['operador_chi']['relative_error']
        assert prior > 0
        reduction[label] = dict(original_relative_response_norm=prior,
                                mixed_relative_response_norm=current, mixed_over_original=current/prior,
                                norm_reduction_fraction=1-current/prior, at_least_half_reduced=current <= .5*prior)
    closure_passed = max(closures.values()) <= criteria['closure_relative_tolerance']
    mechanism_passed = all(row['at_least_half_reduced'] for row in reduction.values())
    assert digest(state) == before
    result = dict(schema='CP12_MIXED_RESIDUAL_ORIGINAL_METRICS_ZERO_STEP_READING',
                  time=160, state_sha256=before, original_result_sha256=ORIGINAL_RESULT_SHA256,
                  original_reader_sha256=ORIGINAL_READER_SHA256,
                  physical_result_sha256=args.physical_result_sha256,
                  scientific_scope='Two autoconsistent mixed histories; fixed original spline, norms, windows and criteria',
                  reproduces_CP10_exactly=False, original_initial_Cauchy_data_exact_CP10=True,
                  tables=tables, sufficiency=dominance, cross_terms=cross_terms,
                  full_window_Gram_matrices={key: value.tolist() for key, value in windows.items()},
                  onsets=onsets, full_box_chi_closure=closures, criteria=criteria,
                  maximum_errors=budget.maximum_errors,
                  chi_operator_induced_Phi_response=[{'time':r['time'], 'response_norm':r['coupled_Phi_response_from_chi_operator']} for r in series],
                  coupled_chi_operator_norm_reduction=reduction,
                  physical_comparison=physical['comparison'], original_physical_gates=physical['original_physical_gates'],
                  original_two_grid_physical_gates_passed=physical['two_original_grid_gates_passed'],
                  full_box_closure_gate_passed=closure_passed,
                  registered_mechanism_reduction_gate_passed=mechanism_passed,
                  necessary_pair_and_mechanism_gates_passed=bool(physical['two_original_grid_gates_passed'] and closure_passed and mechanism_passed),
                  additional_resolution_stability_robustness_pending=True,
                  feedback_scope=baseline['feedback_scope'],
                  additional_limitations=['Coupled minus free is not a pure return loop',
                                          'Response removal alone is not proof of correction efficacy',
                                          'No global fourth-order or continuum stability claim'],
                  M2_steps_executed=0, correction_tested=True, correction_validated=False, CP12_closed=False)
    args.output.mkdir(parents=True, exist_ok=False)
    def scalar(value):
        if isinstance(value, np.generic):
            return value.item()
        raise TypeError(type(value).__name__)
    (args.output / 'RESULTADO_RESIDUAL.json').write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False, default=scalar) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True, help='Independent recovered mixed capsule, never a live worker')
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--state-sha256', required=True)
    parser.add_argument('--original-result', type=Path, required=True)
    parser.add_argument('--physical-result', type=Path, required=True, help='Authenticated final-review result from its saved capsule')
    parser.add_argument('--physical-result-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    result = run(parser.parse_args())
    print(json.dumps({key: result[key] for key in ('time', 'necessary_pair_and_mechanism_gates_passed', 'correction_validated', 'CP12_closed')}))


if __name__ == '__main__':
    main()
