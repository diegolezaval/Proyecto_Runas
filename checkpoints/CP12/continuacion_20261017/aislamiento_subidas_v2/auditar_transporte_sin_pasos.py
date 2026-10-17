"""Independent no-step audit of an already recovered, authenticated transport."""
from pathlib import Path
import argparse
import datetime
import importlib.util
import json
import os
import sys

os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')


def run(home):
    home = home.resolve()
    sys.path.insert(0, str(home))
    import transporte as tr
    from scipy.integrate import DOP853
    from scipy.integrate._ivp.base import OdeSolver
    import numpy as np
    from threadpoolctl import threadpool_info
    payload = tr.load(home / 'transport/current.npz')
    watched = [home / 'transport/current.npz', home / 'transport/current.json',
               home / 'outputs/MIXTO_par_estado.npz', home / 'outputs/procedencia.json',
               home / 'configuration.json']
    before = {str(p.relative_to(home)): tr.sha(p) for p in watched}
    blocked_calls = []
    def forbidden(*args, **kwargs):
        blocked_calls.append(True)
        raise AssertionError('Integrator construction or advancement forbidden during audit')
    saved = [(OdeSolver, 'step', OdeSolver.step), (DOP853, '_step_impl', DOP853._step_impl),
             (DOP853, '__init__', DOP853.__init__)]
    for cls, name, _ in saved:
        setattr(cls, name, forbidden)
    try:
        spec = importlib.util.spec_from_file_location('captured_transport_controller', home / 'controlador_transporte.py')
        controller = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(controller)
        legacy = controller.legacy_module(home)
        checked = controller.audit_transport(home, legacy)
        modules, streams, budget, dense, restored = tr.restore(home, legacy, home / 'transport/current.npz')
        tr.assert_equal(payload, restored)
        reproduced = tr.capture(home, streams, budget, dense, restored['observer_clock'],
                                restored['next_record'], restored['target'])
        tr.assert_equal(payload, reproduced)
        audit14 = checked['tests']
        assert checked['passed'] and len(audit14) == 14 and all(audit14.values())
        assert not blocked_calls
        identity = tr.read(home / 'preregistration/identidad_cientifica_original.json')
        assert len(identity['code_hashes']) == 14
        for relative, expected in {**identity['code_hashes'], **identity['input_hashes']}.items():
            assert tr.sha(home / 'science' / relative) == expected
        for i, stream in enumerate(streams):
            assert stream.accepted == payload['streams'][i]['accepted']
            assert stream.solver.nfev == payload['solvers'][i]['nfev']
            assert np.array_equal(stream.initial_q, modules['native'].source_state(
                home / 'science' / modules['cfg']['reference_states'][i])['initial_q'])
            assert np.array_equal(stream.initial_v, modules['native'].source_state(
                home / 'science' / modules['cfg']['reference_states'][i])['initial_v'])
        after = {str(p.relative_to(home)): tr.sha(p) for p in watched}
        assert before == after
        return dict(schema='CP12_INDEPENDENT_TRANSPORT_AUDIT_WITH_FORBIDDEN_M2_ADVANCEMENT',
            at=datetime.datetime.now(datetime.timezone.utc).isoformat(), passed=True,
            observer_clock=restored['observer_clock'], target=restored['target'],
            original_audit=checked, protected_file_hashes=before,
            scipy_identity=tr.scipy_identity(), numerical_environment=identity['environment'],
            threadpools=threadpool_info(), construction_and_step_attempts=len(blocked_calls),
            all_solver_stages_dense_outputs_counters_and_observers_bitwise_reproduced=True,
            scientific_sources_and_inputs_authenticated=True, CP10_Cauchy_arrays_exact=True,
            receipt_unchanged=True, M2_steps_executed=0, solver_not_restarted=True,
            scientific_frontier=False, correction_validated=False, CP12_closed=False)
    finally:
        for cls, name, value in saved:
            setattr(cls, name, value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.home)))
