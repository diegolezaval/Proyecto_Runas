"""Read already stored causal metrics at the same time after a spatial negative."""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import os
import sys

os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import numpy as np

ORIGINAL_STATE = '22078538ebba2e948b433b0ab946ee034be132b27f7e72ca1ee30540323b2413'
READER = 'c0e09c0383f3b5c3764bba37de2dd30a3311945e62f32f09534d49e241385244'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def by_window(row):
    result = {'core_phase': {family: {m['name']: m for m in row[family]}
                            for family in ('raw', 'coupled')}}
    for label, window in [('short_core_k4', 'core'), ('short_smooth_k4', 'smooth')]:
        metrics = row['short_modes'][window]['metrics']
        result[label] = {family: {m['name']: {k: v for k, v in m.items() if k != 'family'}
                                  for m in metrics if m['family'] == family}
                         for family in ('raw', 'coupled')}
    return result


def run(home, certificate, prefix, original_state, output):
    home, output = home.resolve(), output.resolve()
    assert not output.exists() and not output.is_relative_to(home)
    assert not (home / 'runtime/worker_started.json').exists()
    proof, physical = read(certificate), read(prefix)
    audit = proof['independent_extracted_audit']
    assert proof['passed'] and proof['all_payload_hashes_verified']
    assert audit['passed'] and len(audit['tests']) == 28 and all(audit['tests'].values())
    assert audit['M2_steps_executed'] == 0
    target = proof['time']
    assert physical['time'] == target and not physical['prefix_pair_limits_met']
    assert physical['original_spatial_threshold'] == .02 and physical['M2_steps_executed'] == 0
    state = home / 'outputs/MIXTO_par_estado.npz'
    assert sha(state) == proof['state_sha256'] == physical['source_state_sha256']
    assert sha(home / 'outputs/procedencia.json') == proof['receipt_sha256'] == physical['source_receipt_sha256']
    assert sha(home / 'configuration.json') == proof['configuration_sha256']
    assert sha(original_state) == ORIGINAL_STATE
    before = {str(p): sha(p) for p in (state, original_state, home / 'outputs/procedencia.json')}
    with np.load(state, allow_pickle=False) as data:
        assert float(data['time']) == target
        mixed_rows = json.loads(str(data['budget_rows']))
        initial = (data['initial_q'].copy(), data['initial_v'].copy())
        configuration = json.loads(str(data['config']))
    with np.load(original_state, allow_pickle=False) as data:
        assert float(data['time']) == 160
        original_rows = json.loads(str(data['budget_rows']))
        assert np.array_equal(initial[0], data['initial_q']) and np.array_equal(initial[1], data['initial_v'])
        assert configuration == json.loads(str(data['config']))
    chosen = []
    for rows in (original_rows, mixed_rows):
        matches = [row for row in rows if abs(row['time'] - target) <= 1e-12]
        assert len(matches) == 1
        row = matches[0]
        assert max(row['verification'].values()) <= .001
        assert row['short_modes']['parseval_relative_residual'] <= 2e-11
        chosen.append(row)
    original, mixed = chosen
    tables = {'original': by_window(original), 'mixed': by_window(mixed)}
    source = home / 'science/herramientas/interpretar_presupuesto_CP12.py'
    assert sha(source) == READER
    function = next(node for node in ast.parse(source.read_text()).body
                    if isinstance(node, ast.FunctionDef) and node.name == 'sufficient')
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                 '<authenticated_original_sufficient_only>', 'exec'), namespace)
    criteria = read(home / 'science/datos/ensayo_causal_chi_CP12.json')['observer_criteria']
    sufficiency, ratios = {}, {}
    for kind in ('original', 'mixed'):
        sufficiency[kind] = {family: {} for family in ('raw', 'coupled')}
        for family in ('raw', 'coupled'):
            names = set(tables[kind]['core_phase'][family])
            assert all(set(tables[kind][window][family]) == names for window in tables[kind])
            for name in sorted(names):
                tests = {window: bool(namespace['sufficient'](table[family][name], criteria))
                         for window, table in tables[kind].items()}
                sufficiency[kind][family][name] = dict(meets_all_three_windows=all(tests.values()), tests_by_window=tests)
    for window in tables['mixed']:
        ratios[window] = {}
        for name, metric in tables['mixed'][window]['coupled'].items():
            prior = tables['original'][window]['coupled'][name]['relative_error']
            current = metric['relative_error']
            assert np.isfinite([prior, current]).all()
            ratios[window][name] = dict(original_relative_norm=prior, mixed_relative_norm=current,
                mixed_over_original=current/prior if prior > 0 else None)
    result = dict(schema='CP12_SPATIAL_NEGATIVE_SAVED_CAUSAL_METRICS_SAME_TIME_NO_EVOLUTION',
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), time=target,
        state_sha256=proof['state_sha256'], original_state_sha256=ORIGINAL_STATE,
        original_audit_reused=True, prefix_negative=physical['comparison'],
        original_observed_phase_error=original['observed_relative_error'],
        mixed_observed_phase_error=mixed['observed_relative_error'],
        tables=tables, sufficiency=sufficiency, coupled_response_norm_ratios=ratios,
        original_sufficiency_source_sha256=READER, original_criteria=criteria,
        original_coupled_chi_operator_induced_Phi_norm=original['coupled_Phi_response_from_chi_operator'],
        mixed_coupled_chi_operator_induced_Phi_norm=mixed['coupled_Phi_response_from_chi_operator'],
        recorded_short_window_Gram_matrices={kind: {window: row['short_modes'][window]['short_response_gram_matrix']
            for window in ('core', 'smooth')} for kind, row in [('original', original), ('mixed', mixed)]},
        initial_Cauchy_arrays_equal=True, same_actual_time_and_initial_normalizations=True,
        previously_stored_metrics_read_only=True, new_M2_steps=0,
        limits=['Conditional decomposition on two histories in each trial; no pure return-loop fraction',
                'No full-core group or cross-term reconstruction without saved prefix field histories',
                'A diagnostic prefix ratio is not the final tau160 mechanism-reduction gate',
                'No new correction authorized; continuum stability and experimental validity not established'],
        correction_validated=False, CP12_closed=False)
    assert before == {str(p): sha(p) for p in (state, original_state, home / 'outputs/procedencia.json')}
    result['all_input_bytes_unchanged'] = True
    output.mkdir(parents=True)
    (output / 'RESULTADO.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('home', 'certificate', 'prefix', 'original-state', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    result = run(args.home, args.certificate, args.prefix, args.original_state, args.output)
    print(json.dumps({key: result[key] for key in ('time', 'original_observed_phase_error', 'mixed_observed_phase_error', 'new_M2_steps')}))
