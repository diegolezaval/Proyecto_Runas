"""Puerta prerregistrada CP10 desde los estados, sin repetir evolución."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np
from diagnosticar_mediador_CP10 import compare, load
from ejecutar_con_procedencia import verify_receipt

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'validacion/P06/no_radial'


def completed_case(case):
    candidates = []
    for p in (BASE/'CP10').glob(case+'__*/procedencia.json'):
        receipt = json.loads(p.read_text())
        if receipt['status'] == 'COMPLETADA':
            result = verify_receipt(p)
            if not result['passed']:
                raise ValueError('Procedencia inválida: '+str(p))
            candidates.append(p.parent)
    if len(candidates) != 1:
        raise ValueError('Se requiere exactamente una ejecución completada de '+case)
    run = candidates[0]
    states = list(run.glob('*_estado.npz'))
    if len(states) != 1:
        raise ValueError('Estado ambiguo')
    return run, states[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads((ROOT/json.loads(args.config.read_text())['protocol']).read_text())
    original_protocol = json.loads((ROOT/protocol['unchanged_gate_source']).read_text())
    criteria = protocol['criteria']
    if criteria['field_and_phase_space_relative_error_max'] != original_protocol['criteria']['radial_norm_relative_change_max']:
        raise ValueError('Puerta modificada')
    temporal_run, temporal_state = completed_case('temporal_h0125')
    spatial_run, spatial_state = completed_case('espacial_h00625')
    original_state = BASE/'dop853e9_L4_h0.125_dt0.0200_R220_eps0.020_T160_estado.npz'
    pairs = [('temporal_fino_h0125', original_state, temporal_state), ('radial_fino_h0125_h00625', temporal_state, spatial_state)]
    comparisons = []
    keys = ['norm_relative_sup_error', 'final_complex_nonradial_field_error_over_initial_norm',
            'final_phi_phase_space_error_over_initial_norm', 'final_mediator_nonradial_error_over_initial_norm',
            'final_mediator_phase_space_error_over_initial_norm']
    for control, left, right in pairs:
        metric = compare(left, right)
        metric.update(control=control, left=left.relative_to(ROOT).as_posix(), right=right.relative_to(ROOT).as_posix(),
                      threshold=criteria['field_and_phase_space_relative_error_max'])
        metric['passed'] = all(metric[k] < metric['threshold'] for k in keys)
        comparisons.append(metric)
    records = {}
    run_gates = []
    for label, folder, state in [('temporal_h0125', temporal_run, temporal_state), ('espacial_h00625', spatial_run, spatial_state)]:
        result_path = state.with_name(state.name.replace('_estado.npz', '.json'))
        record = json.loads(result_path.read_text())
        data = load(state)
        if data['time'] != 160 or data['rows'][0, 0] != 0 or data['rows'][-1, 0] != 160 or not np.all(np.diff(data['rows'][:, 0]) > 0):
            raise ValueError('Evolución incompleta')
        if not all(np.isfinite(data[k]).all() for k in ['q', 'v', 'initial_q', 'initial_v', 'rows']):
            raise ValueError('Estado no finito')
        passed = record['relative_energy_drift'] < criteria['energy_drift_max'] and record['relative_charge_drift'] < criteria['charge_drift_max'] and record['relative_core_charge_change'] < criteria['core_charge_change_max'] and record['max_amplification'] <= criteria['amplification_max']
        run_gates.append(dict(case=label, passed=bool(passed), receipt=(folder/'procedencia.json').relative_to(ROOT).as_posix(), result=result_path.relative_to(ROOT).as_posix()))
        records[label] = record
    old = json.loads((BASE/'resultados.json').read_text())
    superseded = {'radial_mediador_grueso', 'radial_mediador_refinado', 'angular_L2_L4'}
    inherited = [dict(control=x['control'], passed=x['passed'], source='validacion/P06/no_radial/resultados.json', scope='Resolución histórica declarada; no prueba conjunta en la malla CP10') for x in old['comparisons'] if x['control'] not in superseded]
    unaddressed = [x for x in old['issues'] if not x.startswith('radial_mediador_refinado:')]
    passed = all(x['passed'] for x in comparisons+run_gates+inherited) and old['box_control']['passed'] and not unaddressed
    result = dict(checkpoint='CP10_MEDIADOR_ESPACIOTEMPORAL', status='SUBENSAYO_FINITO_SUPERADO' if passed else 'REFINAMIENTO_PENDIENTE',
                  finite_campaign_passed=bool(passed), configuration='datos/ensayo_mediador_CP10.json', comparisons=comparisons,
                  run_gates=run_gates, records=records, inherited_controls=inherited, inherited_box_control=old['box_control'],
                  unaddressed_historical_issues=unaddressed, preserved_old_result='validacion/P06/no_radial/resultados.json',
                  same_action_and_Theta=True, chi_phase_fitted_for_acceptance=False,
                  completed_new_evolutions=2, old_evolutions_repeated=False,
                  complete_E03=False, complete_E04=False, complete_RES0=False, complete_RES1=False,
                  nonlinear_orbital_stability_proven=False, continuum_error_certified=False,
                  angular_spatial_temporal_joint_convergence_certified=False,
                  scope='Deformación cuadrupolar CP04, todos los m hasta L=4, R=220, ε=.02, τ≤160; nuevos controles de espacio/tiempo y controles históricos con sus resoluciones. No perturbaciones arbitrarias ni dispositivo.')
    output = args.output_dir
    (output/'resultados.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    with (output/'comparaciones.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=['control', *keys, 'threshold', 'passed'])
        writer.writeheader()
        writer.writerows({k: row[k] for k in writer.fieldnames} for row in comparisons)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['svg.hashsalt'] = 'Runica_CP10_mediador'
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    metric_names = ['Φ campo', 'Φ fase', 'χ campo', 'χ fase']
    plotted = keys[1:]
    x = np.arange(len(plotted))
    for offset, row, label in [(-.18, comparisons[0], 'Temporal: h=.125, rtol 1e-9→1e-10'), (.18, comparisons[1], 'Espacial: h=.125→.0625, rtol=1e-10')]:
        ax.bar(x+offset, [max(1e-12, 100*row[k]) for k in plotted], width=.35, label=label)
    ax.axhline(2, color='black', linestyle='--', label='Puerta 2 % (sin cambios)')
    ax.set_yscale('log')
    ax.set_xticks(x, metric_names)
    ax.set_ylabel('Diferencia / perturbación inicial (%)')
    ax.set_title('M2 · CP10 · núcleo r<40, τ=160, L=4')
    ax.legend(fontsize=9)
    fig.savefig(output/'CP10_errores_mediador.svg', metadata={'Date': None})
    plt.close(fig)
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
