"""P3 chi composition; Phi, potential, kinetic mass and Gauss tables unchanged."""
import time
import numpy as np
from scipy.linalg import solve_banded
from continuar_no_radial_m2 import Evolution
from mixed_backend import Mixed
from backend import lap2_general
from observador_causal_CP12 import GaussResponse, POOL, lap as lap_fv


def lap_chi(sim, q):
    second = lap2_general(sim, q)
    fourth = lap2_general(sim, second)
    sixth = lap2_general(sim, fourth)
    return second - sim.dx**2 / 12 * fourth + sim.dx**4 / 90 * sixth


def lap_mixed_p3(sim, q):
    if q.shape[-3] != 3:
        raise ValueError('Three original M2 fields required')
    out = lap_fv(sim, q)
    out[..., 2:3, :, :] = lap_chi(sim, q[..., 2:3, :, :])
    return out


class MixedP3(Mixed):
    def lap(self, q):
        out = Evolution.lap(self, q)
        second = self.lap2(q[2:3])
        fourth = self.lap2(second)
        sixth = self.lap2(fourth)
        out[2:3] = second - self.dx**2 / 12 * fourth + self.dx**4 / 90 * sixth
        return out

    def components(self, q, v):
        bulk, faces, angular, boundary, charge = Mixed.components(self, q, v)
        # Positive graph form of A2 q, including the same outer closure.
        u = self.lap2(q[2:3])[0] / self.powers
        beta = self.dx**4 / 90
        faces = faces + beta / 2 * np.sum(self.conductance_u * np.diff(u, axis=0)**2, axis=1)
        boundary = boundary + beta / 2 * np.sum(self.boundary_u * u[-1]**2)
        return bulk, faces, angular, boundary, charge


def weighted_bands_p3(sim, ell):
    """Explicit bandwidth-three polynomial; independent sparse control elsewhere."""
    if hasattr(sim, 'weighted_tridiagonal2') and len(sim.ell) == len(sim.powers[0]):
        d, e = sim.weighted_tridiagonal2(ell)
    else:
        power = sim.r**ell
        mass = sim.w * power**2
        c = (2*ell+3) * np.cumsum(mass)[:-1] / (sim.edges[1:-1]*sim.dx)
        d = np.r_[c, 0.] + np.r_[0., c]
        d[-1] += 2*(2*ell+3)*mass.sum()/(sim.radius*sim.dx)
        d /= mass
        e = -c/(power[:-1]*power[1:]*np.sqrt(sim.w[:-1]*sim.w[1:]))
    alpha, beta = sim.dx**2/12, sim.dx**4/90
    eleft, eright = np.r_[0., e*e], np.r_[e*e, 0.]
    cube0 = d**3
    cube0[1:] += e*e * (2*d[1:]+d[:-1])
    cube0[:-1] += e*e * (2*d[:-1]+d[1:])
    cube1 = e * (d[:-1]**2+d[:-1]*d[1:]+d[1:]**2
                 + np.r_[0., e[:-1]**2]+e**2+np.r_[e[1:]**2, 0.])
    cube2 = e[:-1]*e[1:] * (d[:-2]+d[1:-1]+d[2:])
    cube3 = e[:-2]*e[1:-1]*e[2:]
    return (d + alpha*(d*d+eleft+eright) + beta*cube0,
            e*(1+alpha*(d[:-1]+d[1:])) + beta*cube1,
            alpha*e[:-1]*e[1:] + beta*cube2, beta*cube3)


class P3Gauss(GaussResponse):
    """Scalar chi resolver; same five channels and original GL coefficients."""
    def __init__(self, sim, fields, stages, initial_q, initial_v):
        super().__init__(sim, fields, stages, initial_q, initial_v)
        self.hepta = {}
        for ell in np.unique(sim.ell):
            bands = weighted_bands_p3(sim, ell)
            self.hepta[ell] = (bands[0], *[
                (e*np.sqrt(sim.w[j:]/sim.w[:-j]), e*np.sqrt(sim.w[:-j]/sim.w[j:]))
                for j, e in enumerate(bands[1:], 1)])

    def action(self, q):
        return self.masses[:, None, None]*q - lap_chi(self.sim, q)

    def stage_solve(self, h, forcing):
        clock = time.perf_counter()
        rhs = self.q[None] + h*self.A1[:, None, None, None, None]*self.v[None]
        rhs += h*h*np.tensordot(self.A2, forcing, axes=(1, 0))
        self.timings['rhs'] += time.perf_counter()-clock
        clock = time.perf_counter()
        transformed = np.tensordot(self.Si, rhs, axes=(1, 0))
        self.timings['transform'] += time.perf_counter()-clock
        clock = time.perf_counter()
        solved = np.empty_like(transformed)
        tasks = [(j, f, ell) for j, ev in enumerate(self.ev) if ev.imag >= -1e-12
                 for f in range(self.fields) for ell in self.hepta]

        def solve(task):
            j, f, ell = task
            di, *pairs = self.hepta[ell]
            selected = np.flatnonzero(self.sim.ell == ell)
            band = np.zeros((7, self.sim.n), dtype=complex)
            factor = (h*self.ev[j])**2
            band[3] = 1+factor*(self.masses[f]+di)
            for offset, (upper, lower) in enumerate(pairs, 1):
                band[3-offset, offset:] = factor*upper
                band[3+offset, :-offset] = factor*lower
            plane = transformed[j, :, f]
            values = plane[:, :, selected].transpose(1, 0, 2).reshape(self.sim.n, -1).copy()
            answer = solve_banded((3, 3), band, values, overwrite_ab=True,
                                  overwrite_b=True, check_finite=False)
            return j, f, selected, answer.reshape(self.sim.n, 5, len(selected)).transpose(2, 1, 0)

        for j, f, selected, answer in POOL.map(solve, tasks):
            solved[j, :, f, :, selected] = answer
        for j, ev in enumerate(self.ev):
            if ev.imag > 1e-12:
                solved[int(np.argmin(abs(self.ev-ev.conjugate())))] = solved[j].conjugate()
        self.timings['tridiagonal'] += time.perf_counter()-clock
        clock = time.perf_counter()
        result = np.tensordot(self.S, solved, axes=(1, 0)).real
        self.timings['back_transform'] += time.perf_counter()-clock
        return result


class MixedP3Gauss(GaussResponse):
    def __init__(self, sim, fields, stages, initial_q, initial_v):
        super().__init__(sim, fields, stages, initial_q, initial_v)
        if fields not in (1, 3):
            raise ValueError('Only original bare/coupled spaces')
        self.scalar = []
        for f in range(fields):
            cls = P3Gauss if fields == 1 or f == 2 else GaussResponse
            sub = cls(sim, 1, stages, initial_q[f:f+1], initial_v[f:f+1])
            sub.masses = self.masses[f:f+1].copy()
            self.scalar.append(sub)

    def action(self, q):
        action = lap_chi(self.sim, q) if self.fields == 1 else lap_mixed_p3(self.sim, q)
        return self.masses[:, None, None]*q-action

    def stage_solve(self, h, forcing):
        out = np.empty((self.stages, *self.q.shape))
        for f, sub in enumerate(self.scalar):
            sub.q, sub.v = self.q[:, f:f+1], self.v[:, f:f+1]
            out[:, :, f:f+1] = sub.stage_solve(h, forcing[:, :, f:f+1])
        return out
