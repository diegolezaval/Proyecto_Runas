"""Static regularity and variational contrast: no M2 evolution or trajectory changes."""
from pathlib import Path
import hashlib, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq
from scipy.special import spherical_jn

HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]
ROOT = HOME / 'science'
sys.path.insert(0, str(ROOT / 'herramientas'))
from continuar_no_radial_m2 import Evolution

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
identity = json.loads((HOME / 'preregistration/identidad_cientifica.json').read_text())
before = {n: sha(ROOT / n) for n in identity['code_hashes']}
assert before == identity['code_hashes']

def regular_data(sim, ell):
    power = 2 * ell + 3
    volumes = np.diff(sim.edges ** power) / power
    conductance = sim.edges[1:-1] ** (power - 1) / sim.dx
    diagonal = np.r_[conductance, 0.] + np.r_[0., conductance]
    diagonal[-1] += 2 * sim.radius ** (power - 1) / sim.dx
    return volumes, conductance, diagonal

def regular_lap(sim, ell, q):
    weights, conductance, diagonal = regular_data(sim, ell)
    u = q / sim.r ** ell
    force = -diagonal * u
    force[:-1] += conductance * u[1:]
    force[1:] += conductance * u[:-1]
    return sim.r ** ell * force / weights

def exact_original_residual(sim, ell):
    r, h = sim.r, sim.dx
    if ell < 2: return np.zeros_like(r)
    if ell == 2: return h * h / (2 * (r * r + h * h / 12))
    if ell == 3: return 3.5 * r * h * h / (r * r + h * h / 12)
    if ell == 4: return h * h * (13 * r * r + .5 * h * h) / (r * r + h * h / 12)
    raise ValueError(ell)

def roots(ell):
    grid = np.arange(.1, 40., np.pi / 20)
    zeros = []
    for a, b in zip(grid[:-1], grid[1:]):
        if spherical_jn(ell, a) * spherical_jn(ell, b) < 0:
            zeros.append(brentq(lambda x: spherical_jn(ell, x), a, b, xtol=5e-14))
            if len(zeros) == 3: return np.array(zeros)
    raise ValueError('Insufficient analytic roots')

def spectrum(sim, ell, family):
    if family == 'original':
        weight = sim.w
        conductance = sim.c
        diag = np.r_[conductance, 0.] + np.r_[0., conductance] + sim.dx * ell * (ell + 1)
        diag[-1] += 2 * sim.radius * sim.radius / sim.dx
    else:
        weight, conductance, diag = regular_data(sim, ell)
    normalized_diag = diag / weight
    normalized_off = -conductance / np.sqrt(weight[:-1] * weight[1:])
    values = eigh_tridiagonal(normalized_diag, normalized_off, select='i', select_range=(0, 2), eigvals_only=True, lapack_driver='stebz')
    return values

records, spectra = [], []
for count in [32, 64, 128, 256, 512]:
    sim = Evolution(1. / count, 1., 4)
    for ell in range(5):
        index = int(np.flatnonzero(sim.ell == ell)[0])
        solid = sim.r ** ell
        field = np.zeros((1, sim.n, sim.nm)); field[0, :, index] = solid
        original = sim.lap(field)[0, :, index]
        expected = exact_original_residual(sim, ell)
        identity_error = float(np.max(abs(original[:-1] - expected[:-1])))
        assert identity_error < 8e-9 * (count / 512) ** 2 + 2e-12
        naive = original - (ell * (ell + 1) / sim.r ** 2 - sim.cent[:, index]) * solid
        naive_linear_identity_error = None
        if ell == 1:
            exact_naive = -sim.dx ** 2 / (6 * sim.r * (sim.r ** 2 + sim.dx ** 2 / 12))
            naive_linear_identity_error = float(np.max(abs(naive[:-1] - exact_naive[:-1])))
            assert naive_linear_identity_error < 1e-9
        harmonic = regular_lap(sim, ell, solid)
        next_polynomial = regular_lap(sim, ell, sim.r ** (ell + 2))
        expected_next = (4 * ell + 6) * sim.r ** ell
        harm_error = float(np.max(abs(harmonic[:-1])))
        next_error = float(np.max(abs(next_polynomial[:-1] - expected_next[:-1])))
        assert max(harm_error, next_error) < 1e-7 * (count / 512) ** 2 + 2e-11
        records.append(dict(N=count, h=sim.dx, ell=ell, original_first_cell=float(original[0]), original_local_identity_error=identity_error,
            original_weighted_norm=float(np.sqrt(np.dot(sim.w[:-1], original[:-1] ** 2))),
            naive_first_cell=float(naive[0]), naive_weighted_norm=float(np.sqrt(np.dot(sim.w[:-1], naive[:-1] ** 2))),
            naive_l1_identity_error=naive_linear_identity_error, regular_harmonic_max_residual=harm_error, regular_next_polynomial_max_error=next_error))
        exact = roots(ell) ** 2
        for family in ['original', 'regular_variational_contrast']:
            eigenvalues = spectrum(sim, ell, family)
            assert np.all(eigenvalues > 0)
            spectra.append(dict(N=count, h=sim.dx, ell=ell, family=family, exact_eigenvalues=exact.tolist(), eigenvalues=eigenvalues.tolist(), relative_errors=(abs(eigenvalues / exact - 1)).tolist(), all_first_three_positive=True))

orders = []
for ell in range(5):
    for family in ['original', 'regular_variational_contrast']:
        rows = [r for r in spectra if r['ell'] == ell and r['family'] == family]
        for a, b in zip(rows[:-1], rows[1:]):
            orders.append(dict(ell=ell, family=family, coarse_N=a['N'], fine_N=b['N'], observed_orders=(np.log(np.array(a['relative_errors']) / np.array(b['relative_errors'])) / np.log(2)).tolist()))
after = {n: sha(ROOT / n) for n in identity['code_hashes']}
assert after == before
result = dict(schema='CP12_PASSIVE_REGULARITY_AND_QUADRATIC_ACTION_CONTRAST', new_M2_steps=0, original_trajectories_modified=False,
    original_sources_unchanged=before == after, code_hashes=after, preregistration_sha256=sha(HERE / 'PRERREGISTRO.md'), diagnostic_source_sha256=sha(Path(__file__)),
    original_solid_harmonic_identities_verified=True, naive_l1_defect_verified=True, regular_polynomials_verified=True, symmetric_positive_quadratic_form=True,
    physical_correction_tested=False, full_M2_contrast_discretization_implemented=False, scientific_cause_identified=False, CP12_closed=False, records=records, spectra=spectra, orders=orders)
target = HERE / 'resultados.json'; assert not target.exists()
target.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['records', 'spectra', 'orders', 'code_hashes']}, indent=2))
