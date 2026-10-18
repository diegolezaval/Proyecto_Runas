"""Supplementary saved-prefix agreement; original metrics, real prefix times, no M2."""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
import sys

KEYS = ('norm_relative_sup_error', 'final_complex_nonradial_field_error_over_initial_norm',
        'final_phi_phase_space_error_over_initial_norm', 'final_mediator_nonradial_error_over_initial_norm',
        'final_mediator_phase_space_error_over_initial_norm')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def run(args):
    home, output = args.home.resolve(), args.output.resolve()
    assert not output.exists() and not output.is_relative_to(home)
    assert not (home / 'runtime/worker_started.json').exists(), 'Use an independent recovered snapshot'
    registration = read(args.registration)
    assert registration['reader_sha256'] == sha(Path(__file__))
    source = home / 'science' / registration['original_source_relative']
    assert sha(source) == registration['original_source_sha256']
    proof = read(args.certificate)
    assert proof['schema'] == 'CP12_P3_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED'
    audit = proof['independent_extracted_audit']
    assert proof['passed'] and proof['all_payload_hashes_verified'] and audit['passed']
    assert all(audit['tests'].values()) and audit['M2_steps_executed'] == 0
    target = proof['time']
    assert target > 0 and target < 160 and target % 8 == 0
    state = home / 'outputs/MIXTO_par_estado.npz'
    before = sha(state)
    assert before == proof['state_sha256']
    assert sha(home / 'configuration.json') == proof['configuration_sha256']
    assert sha(home / 'outputs/procedencia.json') == proof['receipt_sha256']
    output.mkdir(parents=True)
    (output / 'runtime/tmp').mkdir(parents=True)
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                      TMPDIR=str(output / 'runtime/tmp'))
    sys.pycache_prefix = str(output / 'runtime/pycache')
    legacy = module('captured_unchanged_mixed_prefix_loader', home / 'coordinator.py')
    with legacy.zero_m2_audit():
        modules, streams, budget = legacy.streams_and_budget(home)
    np = modules['np']
    assert all(s.t == target and s.solver is None for s in streams)
    for label, stream in zip(('coarse', 'fine'), streams):
        np.savez_compressed(output / (label + '.npz'), q=stream.q, v=stream.v,
            initial_q=stream.initial_q, initial_v=stream.initial_v, rows=np.asarray(stream.original_rows),
            time=stream.t, config=json.dumps(stream.config), labels=np.asarray(stream.sim.labels, dtype=str))
    original = module('pinned_original_CP10_metric_reader', source)
    tree = ast.parse(source.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'compare')
    changed = copy.deepcopy(function)
    guard = changed.body[1]
    expected = ast.parse("if c['time'] != 160 or f['time'] != 160:\n    raise ValueError('Tiempo final incorrecto')").body[0]
    assert ast.dump(guard) == ast.dump(expected), 'Original time guard changed'
    count = 0
    for node in ast.walk(guard.test):
        if isinstance(node, ast.Constant) and node.value == 160:
            node.value = target
            count += 1
    assert count == 2
    assert all(ast.dump(a) == ast.dump(b) for index, (a, b) in enumerate(zip(function.body, changed.body)) if index != 1)
    namespace = dict(vars(original))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[changed], type_ignores=[])),
                 '<original_metrics_real_prefix_time>', 'exec'), namespace)
    comparison = namespace['compare'](output / 'coarse.npz', output / 'fine.npz')
    gates = {key: bool(np.isfinite(comparison[key]) and comparison[key] <= .02) for key in KEYS}
    criteria=read(home/'science/datos/ensayo_causal_chi_CP12.json')['criteria']
    physical_gates={}
    for index,stream in enumerate(streams):
        rows=np.asarray(stream.original_rows)
        physical_gates[str(index)+'_core_charge']=bool(np.max(abs(rows[:,4]/rows[0,4]-1))<=criteria['core_charge_change_max'])
        physical_gates[str(index)+'_bounded_window']=bool(rows[:,5].max()<=3*rows[0,5])
        physical_gates[str(index)+'_original_energy']=stream.maxe_original<=2e-4
        physical_gates[str(index)+'_P3_energy']=stream.maxe<=2e-4
        physical_gates[str(index)+'_charge']=stream.maxq<=1e-9
    assert before == sha(state) and proof['receipt_sha256'] == sha(home / 'outputs/procedencia.json')
    result = dict(schema='CP12_SUPPLEMENTARY_SAVED_PREFIX_SPATIAL_AGREEMENT', time=target,
        scope='Agreement of the two original meshes on this prefix; no final-protocol acceptance',
        source_state_sha256=before, source_receipt_sha256=proof['receipt_sha256'],
        original_metric_source_sha256=sha(source), reader_sha256=sha(Path(__file__)),
        only_time_guard_parameterized=True, real_time_labels_preserved=True,
        comparison=comparison, original_spatial_threshold=.02, prefix_pair_gates=gates,
        prefix_pair_limits_met=all(gates.values()), prefix_physical_controls=physical_gates,
        prefix_physical_controls_met=all(physical_gates.values()), final_tau160_gate_pending=True,
        additional_reference_stability_robustness_pending=True, chi_rotation_used_for_acceptance=False,
        M2_steps_executed=0, physical_state_and_receipt_unchanged=True,
        correction_validated=False, CP12_closed=False)
    (output / 'RESULTADO.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--registration', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(run(parser.parse_args())))
