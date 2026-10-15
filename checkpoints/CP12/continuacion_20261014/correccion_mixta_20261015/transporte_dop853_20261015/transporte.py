"""Lossless numerical transport, never a new scientific boundary or solver step."""
from pathlib import Path
import hashlib
import inspect
import json
import os
import stat
import subprocess
import sys
import zipfile
import numpy as np
import scipy
from scipy.integrate import DOP853
from scipy.integrate._ivp.base import OdeSolver
from scipy.integrate._ivp.rk import Dop853DenseOutput

CALLBACKS = {'_fun', 'fun', 'fun_single', 'fun_vectorized'}
STREAM = ('q', 'v', 't', 'accepted', 'nfev', 'maxe', 'maxq', 'maxe_original',
          'rows', 'original_rows', 'nextobs')
BUDGET = ('rows', 'algebra', 'maximum_errors', 'max_step_phase', 'maximum_symmetry_residual')
OBSERVER = ('q', 'v', 'last_iterations', 'max_iterations', 'max_iteration_residual', 'timings')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    with temp.open('rb') as stream:
        os.fsync(stream.fileno())
    temp.replace(path)


def scipy_identity():
    return dict(version=scipy.__version__, rk_sha256=sha(inspect.getsourcefile(DOP853)),
                base_sha256=sha(inspect.getsourcefile(OdeSolver)))


def encode(value, arrays):
    if isinstance(value, (np.ndarray, np.generic)):
        array = np.asarray(value)
        assert not array.dtype.hasobject
        key = 'array_%05d' % len(arrays)
        arrays[key] = array
        return {'array': key, 'scalar': isinstance(value, np.generic),
                'C': bool(array.flags.c_contiguous), 'F': bool(array.flags.f_contiguous)}
    if isinstance(value, dict):
        return {'dict': [[key, encode(item, arrays)] for key, item in value.items()]}
    if isinstance(value, (list, tuple)):
        return {'tuple' if isinstance(value, tuple) else 'list': [encode(item, arrays) for item in value]}
    assert value is None or isinstance(value, (bool, int, float, str)), type(value)
    return {'value': value}


def decode(value, arrays):
    if 'array' in value:
        array = arrays[value['array']].copy(order='K')
        assert array.flags.c_contiguous == value['C'] and array.flags.f_contiguous == value['F']
        return array[()] if value['scalar'] else array
    if 'dict' in value:
        return {key: decode(item, arrays) for key, item in value['dict']}
    if 'list' in value:
        return [decode(item, arrays) for item in value['list']]
    if 'tuple' in value:
        return tuple(decode(item, arrays) for item in value['tuple'])
    return value['value']


def solver_state(solver):
    assert isinstance(solver, DOP853)
    assert solver.K.shape == solver.K_extended[:solver.n_stages + 1].shape
    assert np.shares_memory(solver.K, solver.K_extended)
    return {key: value for key, value in solver.__dict__.items() if key not in CALLBACKS | {'K'}}


def restore_solver(saved, rhs):
    # OdeSolver.__init__ wires callbacks and checks shapes; it evaluates no RHS.
    solver = DOP853.__new__(DOP853)
    OdeSolver.__init__(solver, rhs, saved['t'], saved['y'], saved['t_bound'],
                       saved['vectorized'], support_complex=True)
    assert solver.nfev == 0
    solver.__dict__.update(saved)
    solver.K = solver.K_extended[:solver.n_stages + 1]
    assert set(solver.__dict__) == set(saved) | CALLBACKS | {'K'}
    assert np.shares_memory(solver.K, solver.K_extended)
    return solver


def capture(home, streams, budget, dense, clock, next_record, target):
    return dict(schema='CP12_EXACT_DOP853_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER',
                scipy=scipy_identity(), observer_clock=clock, next_record=next_record, target=target,
                source_closed_state_sha256=sha(home / 'outputs/MIXTO_par_estado.npz'),
                source_receipt_sha256=sha(home / 'outputs/procedencia.json'),
                configuration_sha256=sha(home / 'configuration.json'),
                streams=[{key: getattr(stream, key) for key in STREAM} for stream in streams],
                solvers=[solver_state(stream.solver) for stream in streams],
                dense=[dict(item.__dict__) for item in dense],
                budget={key: getattr(budget, key) for key in BUDGET},
                basis=budget.S,
                observers={name: [{key: getattr(item, key) for key in OBSERVER} for item in family]
                           for name, family in [('raw', budget.raw), ('coupled', budget.coupled)]},
                CP12_closed=False, transport_is_scientific_acceptance=False)


def save(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {}
    metadata = encode(payload, arrays)
    inventory = {key: dict(dtype=item.dtype.str, shape=list(item.shape),
                           sha256=hashlib.sha256(item.tobytes(order='C')).hexdigest())
                 for key, item in arrays.items()}
    encoded = json.dumps(dict(tree=metadata, arrays=inventory), ensure_ascii=False, allow_nan=False)
    temp = path.with_suffix('.tmp')
    with temp.open('wb') as stream:
        np.savez_compressed(stream, metadata=encoded, **arrays)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)
    write(path.with_suffix('.json'), dict(schema='CP12_INTERNAL_TRANSPORT_BYTE_INTEGRITY',
          state_sha256=sha(path), bytes=path.stat().st_size, observer_clock=payload['observer_clock'],
          target=payload['target'], closed_state_sha256=payload['source_closed_state_sha256'],
          CP12_closed=False, scientific_frontier=False))


def load(path):
    path = Path(path)
    certificate = read(path.with_suffix('.json'))
    assert path.stat().st_size == certificate['bytes'] and sha(path) == certificate['state_sha256']
    with np.load(path, allow_pickle=False) as zipped:
        metadata = json.loads(str(zipped['metadata']))
        assert set(zipped.files) == set(metadata['arrays']) | {'metadata'}
        arrays = {key: zipped[key].copy(order='K') for key in metadata['arrays']}
    for key, item in arrays.items():
        expected = metadata['arrays'][key]
        assert item.dtype.str == expected['dtype'] and list(item.shape) == expected['shape']
        assert hashlib.sha256(item.tobytes(order='C')).hexdigest() == expected['sha256']
    payload = decode(metadata['tree'], arrays)
    assert payload['schema'] == 'CP12_EXACT_DOP853_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER'
    assert payload['scipy'] == scipy_identity(), 'SciPy implementation changed'
    return payload


def restore(home, legacy, path):
    payload = load(path)
    assert sha(home / 'outputs/MIXTO_par_estado.npz') == payload['source_closed_state_sha256']
    assert sha(home / 'configuration.json') == payload['configuration_sha256']
    current_receipt = sha(home / 'outputs/procedencia.json')
    assert current_receipt == payload['source_receipt_sha256'], 'Restore the authenticated receipt with its transport'
    modules, streams, budget = legacy.streams_and_budget(home)
    assert np.array_equal(budget.S, payload['basis'])
    for stream, values, solver in zip(streams, payload['streams'], payload['solvers']):
        for key, value in values.items():
            setattr(stream, key, value)
        stream.solver = restore_solver(solver, stream.rhs)
        assert np.array_equal(np.stack([stream.q, stream.v]).ravel(), stream.solver.y)
        stream.q, stream.v = stream.solver.y.reshape(stream.shape)
    dense = []
    for stream, values in zip(streams, payload['dense']):
        item = Dop853DenseOutput.__new__(Dop853DenseOutput)
        item.__dict__.update(values)
        stream.dense = item
        dense.append(item)
    for key, value in payload['budget'].items():
        setattr(budget, key, value)
    for name in ('raw', 'coupled'):
        for item, values in zip(getattr(budget, name), payload['observers'][name]):
            for key, value in values.items():
                setattr(item, key, value)
    return modules, streams, budget, dense, payload


def assert_equal(left, right, where='state'):
    if isinstance(left, np.ndarray):
        assert isinstance(right, np.ndarray) and left.dtype == right.dtype and left.shape == right.shape, where
        assert left.tobytes(order='C') == right.tobytes(order='C'), where
    elif isinstance(left, np.generic):
        assert type(left) is type(right) and left.tobytes() == right.tobytes(), where
    elif isinstance(left, dict):
        assert list(left) == list(right), where
        for key in left:
            if key != 'timings':
                assert_equal(left[key], right[key], where + '.' + key)
    elif isinstance(left, (list, tuple)):
        assert type(left) is type(right) and len(left) == len(right), where
        for i, (a, b) in enumerate(zip(left, right)):
            assert_equal(a, b, where + '.' + str(i))
    else:
        assert type(left) is type(right) and left == right, where


def unpack_verified(archive, destination, expected_sha, expected_bytes):
    assert not destination.exists()
    assert archive.stat().st_size == expected_bytes and sha(archive) == expected_sha
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        assert len(names) == len(set(names))
        for item in zipped.infolist():
            path = Path(item.filename)
            assert not path.is_absolute() and '..' not in path.parts and not stat.S_ISLNK(item.external_attr >> 16)
        manifest = json.loads(zipped.read('MANIFIESTO_NEGATIVO.json'))
        assert set(names) == set(manifest['files']) | {'MANIFIESTO_NEGATIVO.json'}
        for name, item in manifest['files'].items():
            data = zipped.read(name)
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], name
        destination.mkdir(parents=True)
        zipped.extractall(destination)
    return manifest
