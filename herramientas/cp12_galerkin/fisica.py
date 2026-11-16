"""M2 semidiscreto Galerkin y evolución Gauss–Legendre de cuatro etapas."""
from pathlib import Path

import numpy as np
from numpy.polynomial import Polynomial
from scipy.sparse.linalg import splu

from radial import Angular, Cauchy, CHANNELS, Grid, RADIUS


class M2:
    def __init__(self, case, source, build):
        # Estos dos lectores sólo proporcionan datos angulares y Θ del benchmark.
        from continuar_no_radial_m2 import Evolution
        from modelo_m2 import BENCHMARK
        from observador_causal_CP12 import symmetry_basis

        self.model = BENCHMARK
        self.seed = Cauchy(source)
        angular_sim = Evolution(.125, RADIUS, 4)
        q0, _ = self.seed.sample(angular_sim.r)
        S, _ = symmetry_basis(angular_sim, q0)
        self.angular = Angular(angular_sim, S, build)
        self.mesh = Grid(case["radial_step"], self.angular.degrees)
        self.mass2 = np.array([self.model.mass2, self.model.mass2, self.model.mediator**2])
        self.linear = {m.ell: (m.stiffness + self.mass2[0] * m.mass,
                              m.stiffness + self.mass2[2] * m.mass) for m in self.mesh.modes}

    def initialize(self):
        mesh = self.mesh
        q, v = self.seed.sample(mesh.r)
        return tuple(mesh.mass_solve(mesh.weak_load(mesh.r[:, None, None] * self.angular.reduce(a)))
                     for a in (q, v))

    def linear_load(self, u):
        result = np.empty_like(u)
        for mode in self.mesh.modes:
            operators = self.linear[mode.ell]
            for assign, operator in zip((slice(0, 2), slice(2, 3)), operators):
                result[:, assign][..., mode.ids] = self.mesh.apply(operator, u[:, assign][..., mode.ids])
        return result

    def mass_load(self, u):
        result = np.empty_like(u)
        for mode in self.mesh.modes:
            result[..., mode.ids] = self.mesh.apply(mode.mass, u[..., mode.ids])
        return result

    def nonlinear_load(self, u):
        mesh = self.mesh
        field = mesh.values(u) / mesh.r[:, None, None]
        force, _ = self.angular.evaluate(field, self.model)
        return mesh.weak_load(mesh.r[:, None, None] * force)

    def acceleration(self, u):
        return self.mesh.mass_solve(self.nonlinear_load(u) - self.linear_load(u))

    def energies(self, u, v, direct=False, sampled=None):
        mesh = self.mesh
        field = (mesh.values(u) if sampled is None else sampled) / mesh.r[:, None, None]
        if direct:
            _, potential, _ = self.angular.direct(field, self.model)
        else:
            _, potential = self.angular.evaluate(field, self.model)
        mv = self.mass_load(v)
        ku = self.linear_load(u)
        quadratic = np.sum(CHANNELS[None, :, None] * (v * mv + u * ku))
        energy = quadratic + np.dot(mesh.w * mesh.r**2, potential)
        charge = 2 * (np.sum(u[:, 0] * mv[:, 1]) - np.sum(u[:, 1] * mv[:, 0]))
        return energy, charge

    def measure(self, time, u, v, balances=None):
        mesh = self.mesh
        U, V = mesh.values(u), mesh.values(v)
        kept = mesh.core
        rr = mesh.r[kept, None, None]
        w = mesh.w[kept]
        field, velocity = U[kept], V[kept]
        derivative = mesh.values(u, derivative=True)[kept] - field / rr
        weighted = CHANNELS[None, :, None]
        a, b, chi = np.moveaxis((field / rr) @ self.angular.y, 1, 0)
        local_potential = self.model.potential(np.sqrt(a*a + b*b), chi) @ self.angular.weights
        d = np.sum(weighted * (velocity**2 + derivative**2 +
                   self.angular.degrees * (self.angular.degrees + 1) * (field / rr)**2), axis=(1, 2))
        core_energy = np.dot(w, d + rr.ravel()**2 * local_potential)
        core_charge = 2 * np.dot(w, np.sum(field[:, 0] * velocity[:, 1] - field[:, 1] * velocity[:, 0], axis=1))
        norm = np.einsum("r,rak->k", w, field[:, :2]**2)
        nonradial = float(np.sqrt(norm[1:].sum() / norm[0]))
        by_ell = [float(np.sqrt(norm[self.angular.degrees == ell].sum() / norm[0])) for ell in range(1, 5)]
        energy, charge = self.energies(u, v, sampled=U) if balances is None else balances
        return [time, float(energy), float(charge), float(core_energy), float(core_charge), nonradial, *by_ell]

    def fields(self, u, r):
        return self.angular.lift(self.mesh.values(u, r=r) / r[:, None, None])


def tableau():
    c = .5 + .5 * np.polynomial.legendre.leggauss(4)[0]
    polynomials = [Polynomial.fromroots(np.delete(c, i)) for i in range(len(c))]
    antiderivatives = [(p / p(x)).integ() for p, x in zip(polynomials, c)]
    A = np.column_stack([p(c) - p(0) for p in antiderivatives])
    b = np.array([p(1) - p(0) for p in antiderivatives])
    return A, b, c


class Gauss8:
    """Colocación simpléctica Nyström. El bloque lineal se resuelve por LU."""
    def __init__(self, model, case):
        self.m2 = model
        self.dt, self.rtol, self.atol = (case[k] for k in ("dt", "stage_rtol", "stage_atol"))
        self.A, self.b, self.c = tableau()
        self.A2 = self.A @ self.A
        self.bA = self.b @ self.A
        eig, basis = np.linalg.eig(self.A2)
        chosen = eig.imag > 0
        if int(chosen.sum()) != 2:
            raise RuntimeError("Descomposición de las cuatro etapas inválida")
        self.from_basis = basis[:, chosen]
        self.to_basis = np.linalg.inv(basis)[chosen]
        self.factors = []
        for eigenvalue in eig[chosen]:
            self.factors.append({
                m.ell: tuple(splu((m.mass + self.dt**2 * eigenvalue * K).tocsc())
                             for K in model.linear[m.ell]) for m in model.mesh.modes
            })
        self.max_iterations = 0
        self.max_normalized_change = 0.

    @staticmethod
    def combine(matrix, stages):
        shape = stages.shape
        return (matrix @ stages.reshape(shape[0], -1)).reshape((-1, *shape[1:]))

    def decompose(self, rhs):
        basis = self.combine(self.to_basis, rhs)
        for i, matrices in enumerate(self.factors):
            for mode in self.m2.mesh.modes:
                for section, factor in zip((slice(0, 2), slice(2, 3)), matrices[mode.ell]):
                    part = basis[i, :, section]
                    rhs_i = part[..., mode.ids]
                    part[..., mode.ids] = factor.solve(rhs_i.reshape(rhs_i.shape[0], -1)).reshape(rhs_i.shape)
        return 2 * self.combine(self.from_basis, basis).real

    def step(self, u, v):
        t = self.dt
        c = self.c[:, None, None, None]
        base = self.m2.mass_load(u) + (t * c) * self.m2.mass_load(v)
        stage = u + t * c * v
        for iterations in range(1, 25):
            nonlinear = np.stack([self.m2.nonlinear_load(q) for q in stage])
            next_stage = self.decompose(base + t*t * self.combine(self.A2, nonlinear))
            scale = self.atol + self.rtol * np.maximum(abs(next_stage), abs(stage))
            change = float(np.max(abs(next_stage - stage) / scale))
            stage = next_stage
            if change <= 1.:
                break
        else:
            raise ArithmeticError("Las cuatro etapas Galerkin no convergieron")
        self.max_iterations = max(self.max_iterations, iterations)
        self.max_normalized_change = max(self.max_normalized_change, change)
        accel = np.stack([self.m2.acceleration(q) for q in stage])
        final_u = u + t * v + t*t * self.combine(self.bA[None, :], accel)[0]
        final_v = v + t * self.combine(self.b[None, :], accel)[0]
        return final_u, final_v


def manufactured(mesh, wave, scale):
    r = mesh.r
    z = 1 - (r / RADIUS)**2
    dz = -2 * r / RADIUS**2
    ddz = -2 / RADIUS**2
    g = np.exp(-(r / scale)**2)
    dg = -2 * r / scale**2 * g
    ddg = (4 * r*r / scale**4 - 2 / scale**2) * g
    c, s = np.cos(wave * r), np.sin(wave * r)
    w = z * g * c
    dw = (dz * g + z * dg) * c - wave * z * g * s
    ddw = (ddz * g + 2*dz*dg + z*ddg) * c - 2*wave*(dz*g+z*dg)*s - wave**2*w
    results = {}
    for m in mesh.modes:
        n = m.ell + 1
        envelope = (r / scale)**n
        exact, operator = envelope * w, envelope * (ddw + 2*n*dw/r)
        coeff = m.invert_mass.solve(m.sample.T @ (mesh.w * exact))
        result = m.sample @ m.invert_mass.solve(-m.stiffness @ coeff)
        norm = lambda a: np.linalg.norm(np.sqrt(mesh.w) * a)
        results[str(m.ell)] = dict(field=float(norm(m.sample @ coeff - exact) / norm(exact)),
                                    operator=float(norm(result - operator) / norm(operator)),
                                    boundary_value=float((mesh.evaluation(np.array([RADIUS]), m.ell) @ coeff)[0]),
                                    finite=bool(np.isfinite(result).all()))
    return results


def original_seed_check(model, source):
    from continuar_no_radial_m2 import Evolution, seed
    import continuar_no_radial_m2 as original

    if Path(original.SOURCE).resolve() != source.resolve():
        raise ValueError("La Cauchy esperada difiere de la ruta CP04 original")
    cases = {}
    for h in (.125, .0625, .03125):
        sim = Evolution(h, RADIUS, 4)
        q, v, transfer = seed(sim, .02)
        ref_q, ref_v = model.seed.sample(sim.r)
        cases[str(h)] = dict(field_max=float(np.max(abs(q-ref_q))), velocity_max=float(np.max(abs(v-ref_v))),
                             origin_hash=transfer["source_sha256"], omitted_charge=transfer["omitted_exterior_charge"])
    return cases


def identities(model, u, v):
    # Medir C y la proyección reducida contra una suma angular completa.
    rng = np.random.default_rng(20261116)
    grid = model.mesh
    points = np.linspace(0, len(grid.r)-1, 128, dtype=int)
    fields = grid.values(u)[points] / grid.r[points, None, None]
    fields = np.concatenate((fields, fields + rng.normal(size=fields.shape)*.02))
    f, p = model.angular.evaluate(fields, model.model)
    direct, pot, full = model.angular.direct(fields, model.model)
    defect = full - (full @ model.angular.projector) @ model.angular.projector.T
    scale = max(1., float(np.max(abs(full))))
    acceleration = model.acceleration(u)
    e, q = model.energies(u, v, direct=True)
    de, dq = np.imag(model.energies(u + 1e-27j*v, v + 1e-27j*acceleration, direct=True)) / 1e-27
    return dict(energy=float(e), charge=float(q), angular_products=model.angular.rank,
                angular_force_residual=float(np.max(abs(f-direct))/scale),
                potential_residual=float(np.max(abs(p-pot))/max(1., np.max(abs(pot)))),
                angular_closure_residual=float(np.max(abs(defect))/scale),
                energy_identity=float(abs(de)/max(1., abs(e))),
                charge_identity=float(abs(dq)/max(1., abs(q))))


def use_compensated_controls(model, state, limits):
    u, v, rows, balance = state
    return dict(energy=bool(balance["energy"] <= limits["energy_drift_max"]),
                charge=bool(balance["charge"] <= limits["charge_drift_max"]),
                core_charge=bool(max(abs(row[4]/rows[0][4]-1) for row in rows) <= limits["core_charge_change_max"]),
                amplification=bool(max(row[5] for row in rows) <= limits["amplification_max"] * rows[0][5]),
                finite=bool(np.isfinite(u).all() and np.isfinite(v).all() and np.isfinite(rows).all()))
