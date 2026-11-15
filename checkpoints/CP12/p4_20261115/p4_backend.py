"""Acción P4 con el mismo espacio de estados y observadores de P3."""

from copy import copy

import numpy as np

from backend import lap2_general
from continuar_no_radial_m2 import Evolution
from observador_causal_CP12 import lap as lap_fv
from operador_pasivo import ChiP4Gauss, delta_lap
from p3_backend import MixedP3, MixedP3Gauss, lap_chi as lap_chi_p3


ACTION = "Phi_original_FV_chi_fixed_A2_plus_h2_A2_squared_over_12_plus_h4_A2_cubed_over_90_plus_h6_A2_fourth_over_560"


def lap_chi(sim, q):
    return lap_chi_p3(sim, q) + delta_lap(sim, q)


def lap_mixed_p4(sim, q):
    if q.shape[-3] != 3:
        raise ValueError("El operador mixto requiere los tres campos originales.")
    out = lap_fv(sim, q)
    out[..., 2:3, :, :] = lap_chi(sim, q[..., 2:3, :, :])
    return out


class MixedP4(MixedP3):
    def lap(self, q):
        out = Evolution.lap(self, q)
        out[2:3] = lap_chi(self, q[2:3])
        return out

    def components(self, q, v):
        bulk, faces, angular, boundary, charge = super().components(q, v)
        fourth = lap2_general(self, lap2_general(self, q[2:3]))[0]
        bulk = bulk + self.dx**6 / 1120 * self.w * np.sum(fourth*fourth, axis=1)
        return bulk, faces, angular, boundary, charge


def radial_view(sim):
    """Alinea las caras de χ por ℓ en la reducción angular de P3."""
    if sim.powers.shape[1] == sim.nm:
        return sim
    full_ells = np.array([ell for ell, _, _ in sim.labels])
    ids = [int(np.flatnonzero(full_ells == ell)[0]) for ell in sim.ell]
    reduced = copy(sim)
    reduced.powers = sim.powers[:, ids]
    reduced.conductance_u = sim.conductance_u[:, ids]
    reduced.boundary_u = sim.boundary_u[ids]
    return reduced


class MixedP4Gauss(MixedP3Gauss):
    def __init__(self, sim, fields, stages, initial_q, initial_v):
        sim = radial_view(sim)
        super().__init__(sim, fields, stages, initial_q, initial_v)
        chi = fields - 1
        self.scalar[chi] = ChiP4Gauss(sim, 1, stages, initial_q[chi:], initial_v[chi:])

    def action(self, q):
        lap = lap_chi if self.fields == 1 else lap_mixed_p4
        return self.masses[:, None, None]*q - lap(self.sim, q)
