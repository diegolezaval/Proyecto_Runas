"""Incremento de χ y resolvente de diagnóstico. Importar desde la captura P3."""

import numpy as np
from scipy.linalg import solve_banded
from scipy.sparse import diags
from scipy.special import spherical_jn

from backend import lap2_general
from observador_causal_CP12 import GaussResponse, POOL, lap as lap_fv
from p3_backend import MixedP3Gauss, P3Gauss, lap_chi
from diagnostico_d2 import bessel_wavenumbers, weighted_spectrum


def delta_lap(sim, q):
    for _ in range(4):
        q = lap2_general(sim, q)
    return -sim.dx**6 / 560 * q


def positive_operator(sim, ell):
    diag, off = sim.weighted_tridiagonal2(ell)
    a2 = diags((off, diag, off), (-1, 0, 1), format="csr")
    square = a2 @ a2
    return a2 + (sim.dx**2 / 12) * square + (sim.dx**4 / 90) * (a2 @ square) + (
        sim.dx**6 / 560) * (square @ square)


class ChiP4Gauss(GaussResponse):
    """El mismo cuadro GL de P3 con resolvente de nueve bandas para χ."""

    def __init__(self, sim, fields, stages, initial_q, initial_v):
        super().__init__(sim, fields, stages, initial_q, initial_v)
        assert fields == 1
        self.bands = {}
        for ell in np.unique(sim.ell):
            operator = positive_operator(sim, ell)
            band = np.zeros((9, sim.n))
            band[4] = operator.diagonal()
            for offset in range(1, 5):
                upper, lower = operator.diagonal(offset), operator.diagonal(-offset)
                ratio = np.sqrt(sim.w[offset:] / sim.w[:-offset])
                band[4-offset, offset:] = upper * ratio
                band[4+offset, :-offset] = lower / ratio
            self.bands[ell] = band

    def action(self, q):
        return self.masses[:, None, None]*q - lap_chi(self.sim, q) - delta_lap(self.sim, q)

    def stage_solve(self, h, forcing):
        rhs = self.q[None] + h*self.A1[:, None, None, None, None]*self.v[None]
        rhs += h*h*np.tensordot(self.A2, forcing, axes=(1, 0))
        transformed = np.tensordot(self.Si, rhs, axes=(1, 0))
        solved = np.empty_like(transformed)
        tasks = [(j, ell) for j, ev in enumerate(self.ev) if ev.imag >= -1e-12
                 for ell in self.bands]

        def solve(task):
            j, ell = task
            selected = np.flatnonzero(self.sim.ell == ell)
            factor = (h*self.ev[j])**2
            band = factor * self.bands[ell]
            band[4] += 1 + factor*self.masses[0]
            plane = transformed[j, :, 0][:, :, selected]
            plane = plane.transpose(1, 0, 2).reshape(self.sim.n, -1).copy()
            values = solve_banded((4, 4), band, plane, overwrite_ab=True,
                                  overwrite_b=True, check_finite=False)
            return j, selected, values.reshape(self.sim.n, 5, len(selected)).transpose(2, 1, 0)

        for j, selected, values in POOL.map(solve, tasks):
            solved[j, :, 0, :, selected] = values
        for j, ev in enumerate(self.ev):
            if ev.imag > 1e-12:
                partner = int(np.argmin(abs(self.ev-ev.conjugate())))
                solved[partner] = solved[j].conjugate()
        return np.tensordot(self.S, solved, axes=(1, 0)).real


class MixedP4Gauss(MixedP3Gauss):
    def __init__(self, sim, fields, stages, initial_q, initial_v):
        super().__init__(sim, fields, stages, initial_q, initial_v)
        chi = fields-1
        self.scalar[chi] = ChiP4Gauss(sim, 1, stages, initial_q[chi:], initial_v[chi:])

    def action(self, q):
        spatial = lap_fv(self.sim, q)
        chi = q[..., 2:3, :, :]
        spatial[..., 2:3, :, :] = lap_chi(self.sim, chi) + delta_lap(self.sim, chi)
        return self.masses[:, None, None]*q - spatial


class RegularGeometry:
    """Proyección W de modos regulares. Gℓ se evalúa por recurrencia de Bessel."""

    def __init__(self, sim, cutoff):
        from scipy.linalg import cho_factor

        self.sim = sim
        self.basis = {}
        for ell in (0, 2, 4):
            k = bessel_wavenumbers(int(cutoff*sim.radius/np.pi)+1, ell, sim.radius)
            k = k[k <= cutoff]
            z = sim.r[:, None]*k
            u = spherical_jn(ell, z)
            u /= np.sqrt(sim.radius**3/2)*abs(spherical_jn(ell+1, sim.radius*k))
            g = spherical_jn(ell+2, z)*k**2 / (6*(2*ell+1)*sim.r[:, None]**2)
            g /= np.sqrt(sim.radius**3/2)*abs(spherical_jn(ell+1, sim.radius*k))
            weighted = u.T*sim.w
            self.basis[ell] = (weighted, cho_factor(weighted @ u), g, k)

    def evaluate(self, q):
        from scipy.linalg import cho_solve

        out = np.zeros_like(q)
        for ell, (weighted, factor, g, _) in self.basis.items():
            mode = self.sim.ell == ell
            out[:, mode] = g @ cho_solve(factor, weighted @ q[:, mode])
        return out

    def manufactured(self):
        errors = {}
        r = self.sim.r
        for ell, (_, _, _, k) in self.basis.items():
            # Prueba base libre, con dos frecuencias y signos, frente a D_a u.
            ks = k[[len(k)//3, 2*len(k)//3]]
            z = r[:, None]*ks
            coefficients = np.array([1., -.36])
            u = spherical_jn(ell, z)
            up = ks*spherical_jn(ell, z, derivative=True)
            upp = -2*up/r[:, None] - (ks**2-ell*(ell+1)/r[:, None]**2)*u
            expected = (upp - (2*ell+1)*up/r[:, None] + ell*(ell+2)*u/r[:, None]**2)
            expected = (expected/(6*(2*ell+1)*r[:, None]**2)) @ coefficients
            q = np.zeros((self.sim.n, self.sim.nm))
            column = int(np.flatnonzero(self.sim.ell == ell)[0])
            q[:, column] = u @ coefficients
            result = self.evaluate(q)[:, column]
            err = np.linalg.norm((result-expected)*np.sqrt(self.sim.w))
            errors[str(ell)] = float(err/np.linalg.norm(expected*np.sqrt(self.sim.w)))
        assert max(errors.values()) <= 2e-9
        return errors


def manufactured_resolvent(sim, step, steps):
    """Soluciones cerradas de modos propios forzados, en los dos órdenes."""
    evidence = {}
    sw = np.sqrt(sim.w)
    for ell in (2, 4):
        eigenvalues, basis, _ = weighted_spectrum(sim, ell)
        for degree, solver_class in ((3, P3Gauss), (4, ChiP4Gauss)):
            for stages in (7, 6):
                zero = np.zeros((1, sim.n, sim.nm))
                solver = solver_class(sim, 1, stages, zero, zero)
                data = np.zeros_like(solver.q)
                column = int(np.flatnonzero(sim.ell == ell)[0])
                index = int(np.argmin(abs(np.sqrt(eigenvalues)-11)))
                lam, shape = eigenvalues[index], basis[:, index]/sw
                data[1, 0, :, column] = shape
                omega = np.sqrt(solver.masses[0]+lam + sim.dx**2*lam**2/12
                                + sim.dx**4*lam**3/90 + (degree == 4)*sim.dx**6*lam**4/560)
                exact = [(1-np.cos(omega*steps*step))/omega**2, np.sin(omega*steps*step)/omega]
                for _ in range(steps):
                    solver.advance(step, np.broadcast_to(data, (stages, *data.shape)))
                err = max(float(np.linalg.norm((a[1, 0, :, column]-x*shape)*sw)/abs(x))
                          for a, x in zip((solver.q, solver.v), exact))
                assert err <= 2e-9, (ell, degree, stages, err)
                evidence[f"ell{ell}_P{degree}_GL{stages}"] = err
    return evidence
