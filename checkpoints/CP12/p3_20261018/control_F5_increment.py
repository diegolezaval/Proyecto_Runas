"""Isolate the new quadratic energy against an independently cubed face graph."""
from controls_common import run, sha
from pathlib import Path
import json
import numpy as np
from scipy.sparse import diags


def control(root, output):
    from p3_backend import MixedP3
    from mixed_backend import Mixed
    package = Path(__file__).resolve().parent
    registration = json.loads((package/'ENMIENDA_F5.json').read_text())
    assert sha(Path(__file__)) == registration['source_sha256']
    rng = np.random.default_rng(20261018002)
    rows = []
    for radius, h in [(4., .25), (4., .125), (4., .0625), (220., .125), (220., .0625)]:
        sim = MixedP3(h, radius, 4)
        def total(parts):
            b, f, a, bd, charge = parts
            return b.sum()+f.sum()+a.sum()+bd
        for ell in range(5):
            mass = sim.w*sim.r**(2*ell)
            c = (2*ell+3)*np.cumsum(mass)[:-1]/(sim.edges[1:-1]*h)
            diagonal = np.r_[c, 0.]+np.r_[0., c]
            diagonal[-1] += 2*(2*ell+3)*mass.sum()/(radius*h)
            diagonal /= mass
            off = -c/np.sqrt(mass[:-1]*mass[1:])
            H = diags([off, diagonal, off], [-1, 0, 1], format='csr')
            x, direction = rng.normal(size=(2, sim.n))
            x /= np.linalg.norm(x)
            direction /= np.linalg.norm(direction)
            beta = h**4/90
            H3x = H@(H@(H@x))
            expected_energy = beta/2*np.dot(x, H3x)
            expected_gradient = beta*np.dot(direction, H3x)
            mode = int(np.flatnonzero(sim.ell == ell)[0])
            q = np.zeros((3, sim.n, sim.nm))
            q[2, :, mode] = x/np.sqrt(sim.w)
            v = np.zeros_like(q)
            actual = total(sim.components(q, v))-total(Mixed.components(sim, q, v))
            qc = q.astype(complex)
            qc[2, :, mode] += 1e-30j*direction/np.sqrt(sim.w)
            gradient = (total(sim.components(qc, v))-total(Mixed.components(sim, qc, v))).imag/1e-30
            energy_error = float(abs(actual-expected_energy)/max(abs(expected_energy), 1e-300))
            gradient_error = float(abs(gradient-expected_gradient)/max(1., abs(expected_gradient)))
            tests = dict(positive_added_energy=float(actual) > 0,
                         isolated_added_energy=energy_error <= 2e-12,
                         isolated_added_gradient=gradient_error <= 2e-12)
            row = dict(radius=radius, h=h, ell=ell, added_energy=float(actual),
                       independent_added_energy=float(expected_energy),
                       isolated_energy_relative_error=energy_error,
                       isolated_gradient_scaled_error=gradient_error,
                       tests=tests, passed=all(tests.values()))
            rows.append(row)
            print(json.dumps(row), flush=True)
            if not row['passed']:
                return dict(passed=False, rows=rows, amendment=registration)
    return dict(passed=True, rows=rows, amendment=registration)


if __name__ == '__main__':
    raise SystemExit(run('F5', control))
