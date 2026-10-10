"""Read-only comparison of saved CP12 counters with captured CP10 logs."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shutil
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'herramientas'))
from ejecutar_con_procedencia import verify_receipt

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def run(time_):
    pair = ROOT/'validacion/P06/no_radial/CP12/par_instrumentado__a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
    state = pair/'CP12_par_estado.npz'
    before = sha(state)
    with np.load(state, allow_pickle=False) as saved:
        metadata = json.loads(str(saved['metadata']))
        configuration = json.loads(str(saved['config']))
        actual_time = float(saved['time'])
        observations = len(saved['rows'])
    assert actual_time == time_ and time_ > 0 and time_ % 8 == 0
    folder = ROOT/'trazabilidad/CP12_reconstruccion/controles_contadores'/('tau'+str(int(time_)).zfill(4))
    if folder.exists():
        raise ValueError('Do not overwrite an earlier counter audit')
    folder.mkdir(parents=True)
    sources = folder/'fuentes'
    sources.mkdir()
    shutil.copyfile(__file__, sources/Path(__file__).name)
    inputs = {state.relative_to(ROOT).as_posix(): before}
    tests = {}
    reports = []
    for grid, reference in enumerate(configuration['reference_states']):
        original = ROOT/reference
        log = original.parent/'ejecucion.log'
        receipt = original.parent/'procedencia.json'
        for source in [log, receipt]:
            shutil.copyfile(source, sources/(str(grid)+'_'+source.name))
            inputs[source.relative_to(ROOT).as_posix()] = sha(source)
        tests[str(grid)+'_CP10_receipt_integrity'] = verify_receipt(receipt)['passed']
        rows = {}
        for line in log.read_text().splitlines():
            match = re.match(r'EVOLUCION .* tau ([0-9.]+) pasos (\d+) E ([^ ]+) Q ([^ ]+)', line)
            if match:
                key = float(match[1])
                value = dict(accepted=int(match[2]), maxe=float(match[3]), maxq=float(match[4]))
                if key in rows and rows[key] != value:
                    raise ValueError('Conflicting historical CP10 boundary records')
                rows[key] = value
        tests[str(grid)+'_twenty_original_boundaries'] = sorted(rows) == [float(x) for x in range(8,161,8)]
        observed = metadata[grid]
        expected = rows[time_]
        for key in ['accepted','maxe','maxq']:
            tests[str(grid)+'_'+key+'_exact_CP10_log'] = observed[key] == expected[key]
        segments = int(time_/8)
        # DOP853: 12 RHS calls per attempted step; 2 to initialize each
        # original segment, and 3 for each physical dense-output observation.
        # This checks accounting, not an unavailable historical rejection count.
        remainder = observed['nfev'] - 12*observed['accepted'] - 2*segments - 3*(observations-1)
        tests[str(grid)+'_nfev_integer_nonnegative_rejection_accounting'] = (
            int(observed['nfev']) == observed['nfev'] and remainder >= 0 and remainder % 12 == 0)
        known = {8.0:18266,16.0:36136}
        if time_ in known:
            tests[str(grid)+'_nfev_exact_prior_record'] = observed['nfev'] == known[time_]
        if time_ == 160:
            with np.load(original, allow_pickle=False) as reference_state:
                tests[str(grid)+'_nfev_exact_final_CP10'] = observed['nfev'] == int(reference_state['nfev'])
            inputs[reference] = sha(original)
        reports.append(dict(grid=configuration['physical_configurations'][grid]['dx'],
            observed=observed, CP10_log_expected=expected,
            rejected_attempts_implied_by_bookkeeping=int(remainder/12),
            exact_nfev_reference_available=time_ in [8,16,160]))
    tests['audited_state_unchanged'] = sha(state) == before
    result = dict(schema_version='1.0.0', time=time_, passed=all(tests.values()),
        checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        M2_steps_executed=0, physical_solver_or_observer_changes=False,
        code_sha256=sha(Path(__file__)), input_sha256=inputs,
        tests=tests, grids=reports,
        limitation='Intermediate nfev without a historical record is checked for DOP853 accounting only; final exact CP10 comparison remains mandatory.')
    (folder/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],time=time_,tests=tests)),flush=True)
    if not result['passed']:
        raise ValueError('Counter or original balance mismatch; stop and diagnose')

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--time',type=float,required=True)
    run(parser.parse_args().time)
