"""D2: espectro radial ocupado y contrastes fabricados de P3, sin propagación."""

import math

import numpy as np
from numpy.polynomial import Polynomial
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq
from scipy.special import spherical_jn

ELLS = (2, 4)
SPECTRAL_CUTS = (2, 4, 8, 12, 20)
REFINEMENTS = (.25, .125, .0625, .03125, .015625)
ORDERS = (1, 2, 3, 4)


def coefficients():
    return [2 / (j*j*math.comb(2*j, j)) for j in ORDERS]


def frequency(squared_wavenumber, h, degree, mass):
    x = h*h*squared_wavenumber
    terms = coefficients()[:degree]
    return np.sqrt(mass*mass + x*np.polynomial.polynomial.polyval(x, terms)/(h*h))


def bessel_wavenumbers(n, ell, radius):
    # Orden radial por el número de nodos, como el contraste histórico D2.
    centres = (np.arange(1, n+1) + ell/2) * np.pi
    half = .499999 * np.pi
    return np.array([brentq(lambda z: spherical_jn(ell, z), c-half, c+half, xtol=1e-12)
                     for c in centres]) / radius


def weighted_spectrum(sim, ell):
    d, e = sim.weighted_tridiagonal2(ell)
    lam, vectors = eigh_tridiagonal(d, e, lapack_driver="stemr")
    sample = np.array([0, 1, 2, len(d)//2, len(d)-1])
    u = vectors[:, sample]
    residual = d[:, None]*u - u*lam[sample]
    residual[:-1] += e[:, None]*u[1:]
    residual[1:] += e[:, None]*u[:-1]
    relative = np.linalg.norm(residual, axis=0).max()/(np.max(abs(d))+2*np.max(abs(e)))
    assert lam.min() > 0 and relative <= 2e-11
    return lam, vectors, relative


def spectral_window(r, name):
    if name == "full_box":
        return np.ones_like(r)
    if name == "core_r_lt_40":
        return (r < 40).astype(float)
    return np.where(r < 32, 1., np.where(r < 40, .5*(1+np.cos(np.pi*(r-32)/8)), 0.))


class OccupiedSpectra:
    def __init__(self, sims, mass):
        self.sims = sims
        self.mass = mass
        self.coefficients = coefficients()
        self.arrays = {}
        self.bases = {}
        self.matched = {}
        for ell in ELLS:
            for grid, sim in enumerate(sims):
                lam, vectors, residual = weighted_spectrum(sim, ell)
                k = bessel_wavenumbers(sim.n, ell, sim.radius)
                self.bases[ell, grid] = (k, lam, vectors, residual)
                self.arrays[f"ell{ell}_g{grid}_k_ref"] = k
                self.arrays[f"ell{ell}_g{grid}_lambda_A2"] = lam
                for degree in ORDERS:
                    self.arrays[f"ell{ell}_g{grid}_P{degree}_omega"] = frequency(lam, sim.dx, degree, mass)

            coarse = sims[0]
            k = self.bases[ell, 0][0]
            n = np.count_nonzero(k*coarse.dx <= np.pi)
            assert np.array_equal(k[:n], self.bases[ell, 1][0][:n])
            radial = np.array([[self.arrays[f"ell{ell}_g{g}_P{p}_omega"][:n] for g in range(2)]
                               for p in ORDERS])
            flat = np.array([[frequency((2*np.sin(k[:n]*s.dx/2)/s.dx)**2, s.dx, p, mass)
                              for s in sims] for p in ORDERS])
            self.matched[ell] = (k[:n], radial, flat)
            self.arrays[f"ell{ell}_matched_k"] = k[:n]
            self.arrays[f"ell{ell}_matched_omega_radial"] = radial
            self.arrays[f"ell{ell}_matched_omega_flat"] = flat

    def initial(self, z):
        n = self.sims[0].n
        self.initial_summary = self.snapshot(0, {"coarse": (z["initial_q"][2, :n], z["initial_v"][2, :n]),
                                                 "fine": (z["initial_q"][2, n:], z["initial_v"][2, n:])})

    def snapshot(self, tick, fields):
        output = {}
        for ell in ELLS:
            by_name = {}
            for name, (q, v) in fields.items():
                g = 0 if name == "coarse" else 1
                sim = self.sims[g]
                k, _, basis, eigen_residual = self.bases[ell, g]
                angular = sim.ell == ell
                axes = dict()
                for window in ("full_box", "core_r_lt_40", "smooth_core"):
                    w = np.sqrt(sim.w)*spectral_window(sim.r, window)
                    pos, vel = w[:, None]*q[:, angular], w[:, None]*v[:, angular]/self.mass
                    p = np.sum((basis.T @ pos)**2, axis=1)
                    u = np.sum((basis.T @ vel)**2, axis=1)
                    target = np.array([np.sum(pos*pos), np.sum(vel*vel)])
                    discrepancies = abs(np.array([p.sum(), u.sum()])-target)/np.maximum(target, 1e-300)
                    assert max(discrepancies) <= 2e-11, (tick, ell, g, name, window)
                    stem = f"t{tick}_ell{ell}_{name}_{window}"
                    self.arrays[stem+"_q_power"], self.arrays[stem+"_v_over_m_power"] = p, u
                    axes[window] = dict(
                        q=spectrum_summary(k, p), v_over_m=spectrum_summary(k, u),
                        phase=spectrum_summary(k, p+u),
                        Parseval_field_and_velocity=discrepancies,
                        matched_frequency_contrast=self.exposure(ell, tick, p+u),
                    )
                by_name[name] = dict(grid_step=sim.dx, eigenpair_residual=eigen_residual, windows=axes)
            output[str(ell)] = by_name
        return output

    def exposure(self, ell, tick, power):
        k, radial, flat = self.matched[ell]
        w = power[:len(k)]
        if not w.sum():
            return None
        w = w/w.sum()
        radial_pair = radial[:, 0] - radial[:, 1]
        flat_pair = flat[:, 0] - flat[:, 1]
        radial_rest = radial_pair - flat_pair
        exact = np.hypot(self.mass, k)

        def wm(x):
            return float(np.dot(w, x))

        def rms(x):
            return np.sqrt(wm(x*x))

        alternatives = {}
        for i, p in enumerate(ORDERS):
            a, b = flat_pair[i], radial_rest[i]
            diff = radial_pair[i]
            alternatives[f"P{p}"] = dict(
                rms_pair_domega=rms(diff),
                rms_flat_pair_domega=rms(a),
                rms_radial_remainder_pair_domega=rms(b),
                mean_flat_pair_domega=wm(a),
                mean_radial_remainder_pair_domega=wm(b),
                twice_flat_dot_remainder_in_domega_squared=2*wm(a*b),
                rms_vs_bessel_on_each_grid=[rms(radial[i, j]-exact) for j in range(2)],
                free_phase_proxy_at_160_nondiagnostic_gate=rms(2*np.sin(80*diff)),
                free_phase_proxy_at_snapshot_clock=rms(2*np.sin(.5*tick*diff)),
            )
        return dict(matched_modes=len(k), matched_power_fraction=power[:len(k)].sum()/power.sum(),
                    maximum_matched_k_ref=k[-1], alternatives=alternatives)


def spectrum_summary(k, power):
    total = power.sum()
    if not total:
        return dict(squared_norm=0.0, identically_zero=True)
    cdf = np.cumsum(power)
    return dict(squared_norm=total, identically_zero=False,
                k_ref_at_peak=k[np.argmax(power)],
                k_ref_quantiles={str(f): k[min(np.searchsorted(cdf, f*total), len(k)-1)]
                                 for f in (.5, .9, .99, .999)},
                fraction_above_k_ref={str(c): power[k > c].sum()/total for c in SPECTRAL_CUTS})


def manufactured(Candidate, lap_chi):
    """Repite los dos perfiles históricos y añade portadoras fijas de contraste."""
    profiles = [
        ("center", Polynomial([0, 0, -1/64]), 0),
        ("shell15", -(Polynomial([-225, 0, 1])/60)**2, 0),
        ("shell28", -(Polynomial([-784, 0, 1])/120)**2, 0),
    ]
    profiles.extend((f"shell28_k{k}", profiles[2][1], k) for k in (2, 4, 8, 12))
    deltas = {h: Candidate(h, 40., 4) for h in REFINEMENTS}
    tests = []
    for ell in (0, *ELLS):
        a = 2*ell + 2
        for name, envelope, k in profiles:
            if ell == 0 and k:
                continue
            p = (Polynomial([1, 0, -1/1600]))**6
            p1 = p.deriv() + p*envelope.deriv()
            p2 = p1.deriv() + p1*envelope.deriv()
            for h, sim in deltas.items():
                r = sim.r
                expon = np.exp(envelope(r))
                c, s = np.cos(k*r), np.sin(k*r)
                u = expon*p(r)*c
                u1 = expon*(p1(r)*c - k*p(r)*s)
                u2 = expon*((p2(r)-k*k*p(r))*c - 2*k*p1(r)*s)
                q = r**ell*u
                exact = r**ell*(u2+a/r*u1)
                geom = (h*h*r**ell/(6*(2*ell+1))) * (u2/r**2-u1/r**3)
                mode = int(np.flatnonzero(sim.ell == ell)[0])
                field = np.zeros((1, sim.n, sim.nm))
                field[0, :, mode] = q
                p3 = lap_chi(sim, field)[0, :, mode]
                fourth = field.copy()
                for _ in range(4):
                    fourth = sim.lap2(fourth)
                p4 = p3 - (h**6/560)*fourth[0, :, mode]
                interior = r < 32
                scale = np.sqrt(np.dot(sim.w[interior], q[interior]**2))

                def norm(array, use=interior):
                    return np.sqrt(np.dot(sim.w[use], array[use]**2))/scale

                err = p3 - exact
                measure = {
                    "ell": ell, "shape": name, "carrier_k": k, "h": h,
                    "P3_error_relative_to_field": norm(err), "P4_error_relative_to_field": norm(p4-exact),
                    "P3_minus_radial_h2_error_relative_to_field": norm(err-geom),
                    "radial_h2_relative_to_field": norm(geom),
                    "first_cell_P3_error": err[0], "first_cell_P4_error": p4[0]-exact[0],
                    "outer_32_40_P3_error_on_interior_scale": norm(err, ~interior),
                    "outer_32_40_P4_error_on_interior_scale": norm(p4-exact, ~interior),
                }
                tests.append(measure)
    return tests
