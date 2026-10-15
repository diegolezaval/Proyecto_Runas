"""New transport tests on generic ODEs, not CP12 preflight or M2 evolution."""
from pathlib import Path
import argparse
import json
import tempfile
import numpy as np
from scipy.integrate import DOP853
from transporte import solver_state, restore_solver, save, load, assert_equal, scipy_identity


def test(directory):
    results = []
    for name, equation, initial in (
        ('damped_oscillator', lambda t, y: np.array([y[1], -3*y[0]-.2*y[1]]), np.array([1., .3])),
        ('nonlinear_forced', lambda t, y: np.array([y[1], -y[0]-.4*y[0]**3+np.sin(1.7*t)]), np.array([.7, -.2])),
    ):
        counter = [0]
        def rhs(t, y):
            counter[0] += 1
            return equation(t, y)
        original = DOP853(rhs, 0., initial, 2., max_step=.02, rtol=1e-10, atol=1e-12)
        for _ in range(13):
            original.step()
        original.dense_output()
        payload = dict(schema='CP12_EXACT_DOP853_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER',
                       scipy=scipy_identity(), observer_clock=.2, target=2,
                       source_closed_state_sha256='synthetic_no_M2', solver=solver_state(original))
        path = directory / (name + '.npz')
        save(path, payload)
        restored_payload = load(path)
        assert_equal(payload, restored_payload)
        calls = counter[0]
        recovered = restore_solver(restored_payload['solver'], rhs)
        assert counter[0] == calls, 'Restoration evaluated an RHS'
        assert_equal(solver_state(original), solver_state(recovered))
        assert np.shares_memory(recovered.K, recovered.K_extended)
        for _ in range(17):
            original.step()
            recovered.step()
            assert_equal(solver_state(original), solver_state(recovered))
            first, second = original.dense_output(), recovered.dense_output()
            assert_equal(first.__dict__, second.__dict__)
            times = np.linspace(first.t_min, first.t_max, 9)
            assert_equal(first(times), second(times))
        results.append(dict(case=name, byte_roundtrip=True, restore_RHS_evaluations=0,
              seventeen_subsequent_steps_bitwise_exact=True, live_stage_alias_restored=True,
              dense_coefficients_and_samples_bitwise_exact=True, nfev_equal=original.nfev == recovered.nfev))
    return dict(schema='CP12_NEW_INTERNAL_TRANSPORT_SYNTHETIC_CONTROLS', passed=True,
                cases=results, M2_steps_executed=0, A_D_repeated=False, CP12_closed=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        result = test(Path(temporary))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result))
