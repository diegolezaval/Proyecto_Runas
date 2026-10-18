"""Exact symbol, independent graph positivity and manufactured P3 consistency."""
from controls_common import run
from fractions import Fraction
from math import factorial, comb
import json
import numpy as np
from numpy.polynomial import Polynomial as Poly
from scipy.sparse import diags


def multiply(a, b, degree):
    result = [Fraction(0) for _ in range(degree+1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if i+j <= degree:
                result[i+j] += x*y
    return result


def control(root, output):
    from p3_backend import MixedP3, weighted_bands_p3
    coefficients = [Fraction(2, j*j*comb(2*j, j)) for j in range(1, 4)]
    assert coefficients == [Fraction(1), Fraction(1, 12), Fraction(1, 90)]
    # Polynomial in z^2: x=2(1-cos z), through z^8, exact rational arithmetic.
    x = [Fraction(0)]+[Fraction(2*(-1)**(j+1), factorial(2*j)) for j in range(1, 5)]
    x2, x3 = multiply(x, x, 4), multiply(multiply(x, x, 4), x, 4)
    symbol = [x[j]+x2[j]/12+x3[j]/90 for j in range(5)]
    assert symbol == [Fraction(0), Fraction(1), Fraction(0), Fraction(0), Fraction(-1, 560)]
    rows = []
    for h in (.25, .125, .0625):
        sim = MixedP3(h, 4., 4)
        for ell in range(5):
            # Independent weighted face graph. No prototype diagonal or band calls.
            r, w = sim.r, sim.w
            mass = w*r**(2*ell)
            c = (2*ell+3)*np.cumsum(mass)[:-1]/(sim.edges[1:-1]*h)
            d = np.r_[c, 0.]+np.r_[0., c]
            d[-1] += 2*(2*ell+3)*mass.sum()/(sim.radius*h)
            d /= mass
            e = -c/np.sqrt(mass[:-1]*mass[1:])
            H = diags([e, d, e], [-1, 0, 1], format='csr')
            expected = (H+h*h/12*(H@H)+h**4/90*(H@H@H)).toarray()
            bands = weighted_bands_p3(sim, ell)
            actual = np.diag(bands[0])
            for j, band in enumerate(bands[1:], 1):
                actual += np.diag(band, j)+np.diag(band, -j)
            scale = max(1., float(np.max(abs(expected))))
            error = float(np.max(abs(actual-expected))/scale)
            eigen = np.linalg.eigvalsh(actual)
            eig2 = np.linalg.eigvalsh(H.toarray())
            expected_eigen = eig2+h*h/12*eig2**2+h**4/90*eig2**3
            spectral_error = float(np.max(abs(eigen-expected_eigen))/max(1., float(np.max(abs(expected_eigen)))))
            index = int(np.flatnonzero(sim.ell == ell)[0])
            field = np.zeros((3, sim.n, sim.nm))
            field[2, :, index] = r**ell
            harmonic = sim.lap(field)[2, :-3, index]
            harmonic_error = float(np.max(abs(harmonic), initial=0.))
            tests = dict(independent_seven_bands=error <= 2e-12,
                         positive_spectrum=float(eigen[0]) > 0,
                         polynomial_eigenvalues=spectral_error <= 2e-12,
                         regular_harmonic_before_boundary_stencil=harmonic_error <= 2e-12)
            row = dict(h=h, ell=ell, minimum_eigenvalue=float(eigen[0]),
                       matrix_error=error, spectral_error=spectral_error,
                       interior_harmonic_error=harmonic_error, tests=tests, passed=all(tests.values()))
            rows.append(row)
            print(json.dumps(row), flush=True)
            if not row['passed']:
                return dict(passed=False, structure=rows, manufactured=[])
    manufactured, orders, consistency = [], [], []
    for ell in range(5):
        for shape, g in [('centre', Poly([0, 0, -1/64])),
                         ('shell', -(Poly([-225, 0, 1])/60)**2)]:
            p = Poly([1, 0, -1/1600])**6
            polynomials = [p]
            for derivative in range(2):
                polynomials.append(polynomials[-1].deriv()+polynomials[-1]*g.deriv())
            errors = []
            for h in (.25, .125, .0625, .03125, .015625):
                sim = MixedP3(h, 40., 4)
                r = sim.r
                u, u1, u2 = [p(r)*np.exp(g(r)) for p in polynomials]
                q = r**ell*u
                exact = r**ell*(u2+(2*ell+2)/r*u1)
                leading = r**ell/(6*(2*ell+1))*(u2/r**2-u1/r**3)
                index = int(np.flatnonzero(sim.ell == ell)[0])
                field = np.zeros((3, sim.n, sim.nm))
                field[2, :, index] = q
                value = sim.lap(field)[2, :, index]
                inside = r < 32
                norm = lambda z: float(np.sqrt(np.dot(sim.w[inside], z[inside]**2)))
                error = norm(value-exact)/norm(q)
                errors.append(error)
                manufactured.append(dict(ell=ell, shape=shape, h=h,
                    error_over_field_norm=error,
                    after_subtracting_derived_h2=norm(value-exact-h*h*leading)/norm(q),
                    first_cell_error=float(value[0]-exact[0]),
                    outer_band_error_norm=float(np.sqrt(np.sum(sim.w[~inside]*(value-exact)[~inside]**2)))))
            measured = [float(np.log2(a/b)) for a, b in zip(errors[:-1], errors[1:])]
            order_pass = shape != 'centre' or ell not in (2, 4) or 1.5 <= measured[-1] <= 2.5
            consistent = errors[-1] < errors[0]
            orders.append(dict(ell=ell, shape=shape, observed_orders=measured,
                               formal_radial_order_claim=2, consistency=consistent,
                               registered_centre_order_passed=order_pass))
            consistency.append(consistent and order_pass)
    return dict(passed=all(consistency), exact_coefficients=list(map(str, coefficients)),
                exact_symbol_z_squared=list(map(str, symbol)), structure=rows,
                manufactured=manufactured, orders=orders, global_sixth_order_claim=False)


if __name__ == '__main__':
    raise SystemExit(run('F0', control))
