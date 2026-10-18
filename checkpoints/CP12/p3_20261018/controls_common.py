"""Input verification and hard no-M2 guard shared only by the new P3 controls."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback

os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
assert not os.environ.get('OPENBLAS_CORETYPE')
import numpy as np
from scipy.integrate import DOP853
from scipy.integrate._ivp.base import OdeSolver

BLOCKED = []


def forbidden(*args, **kwargs):
    BLOCKED.append('DOP853_attempt')
    raise RuntimeError('No physical integration authorized in P3 preflight')


DOP853.__init__ = DOP853._step_impl = OdeSolver.step = forbidden


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def snapshots(root, dx):
    pattern = 'temporal_h0125__*' if dx == .125 else 'espacial_h00625__*'
    paths = list((root/'science/validacion/P06/no_radial/CP10').glob(pattern+'/*_estado.npz'))
    assert len(paths) == 1
    with np.load(paths[0], allow_pickle=False) as z:
        original = [('initial', z['initial_q'].copy(), z['initial_v'].copy()),
                    ('original160', z['q'].copy(), z['v'].copy())]
    path = root/'outputs/MIXTO_par_estado.npz'
    assert sha(path) == 'abfae6d6b88a1f5b6a58df1657ea3f860a81b02835fe6598b97315da3c1f3ba4'
    with np.load(path, allow_pickle=False) as z:
        n = int(z['coarse_n'])
        selection = slice(0, n) if dx == .125 else slice(n, None)
        original.append(('mixed80', z['q'][:, selection].copy(), z['v'][:, selection].copy()))
    return original


def run(phase, callback):
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.inputs, args.output = args.inputs.resolve(), args.output.resolve()
    assert not args.output.exists()
    args.output.mkdir(parents=True)
    manifest = None
    result = {}
    try:
        assert sha(args.manifest) == '1591cf07d208d3363de4f10676cb3bfb69f3b2500c7848c405825291d12fc5b2'
        manifest = json.loads(args.manifest.read_text())
        assert len(manifest['files']) == 472
        for name, record in manifest['files'].items():
            p = args.inputs/name
            assert p.stat().st_size == record['bytes'] and sha(p) == record['sha256'], name
        package = Path(__file__).resolve().parent
        registration = json.loads((package/'REGISTRO_CODIGO.json').read_text())
        for name, expected in registration['source_hashes'].items():
            assert sha(package/name) == expected, name
        sys.path[:0] = [str(args.inputs/'science/herramientas'), str(args.inputs/'candidate')]
        from threadpoolctl import threadpool_info
        from ejecutar_con_procedencia import environment
        pools = threadpool_info()
        assert pools and all(p['num_threads'] == 1 and p.get('architecture') == 'SkylakeX' for p in pools)
        original = json.loads((args.inputs/'preregistration/identidad_cientifica_original.json').read_text())
        assert environment() == original['environment']
        result = callback(args.inputs, args.output)
        result['registered_source_hashes'] = registration['source_hashes']
    except BaseException as error:
        result.update(passed=False, exception_type=type(error).__name__, exception=str(error), traceback=traceback.format_exc())
    unchanged = manifest is not None and all(
        (args.inputs/n).is_file() and sha(args.inputs/n) == r['sha256']
        for n, r in manifest['files'].items())
    result.update(schema='CP12_P3_NEW_PREFLIGHT_'+phase, phase=phase,
                  at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  old_P2_trial_resumed=False, M2_steps_executed=0, DOP853_attempts=len(BLOCKED),
                  all_472_input_hashes_unchanged=unchanged, physical_evolution_authorized=False,
                  correction_validated=False, CP12_closed=False)
    result['passed'] = bool(result.get('passed', False) and unchanged and not BLOCKED)
    dump(args.output/'RESULTADO.json', result)
    print(json.dumps(dict(phase=phase, passed=result['passed'], M2_steps_executed=0,
                          output=str(args.output/'RESULTADO.json'))), flush=True)
    return 0 if result['passed'] else 1
