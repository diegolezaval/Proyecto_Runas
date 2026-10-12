"""Static prototype with original mass/potential: regular action and positive composition."""
import numpy as np
from continuar_no_radial_m2 import Evolution

class Candidate(Evolution):
    def __init__(self, dx, radius, L):
        super().__init__(dx, radius, L)
        self.powers = self.r[:, None] ** self.ell[None, :]
        mass_u = self.w[:, None] * self.powers ** 2
        cumulative = np.cumsum(mass_u, axis=0)
        factors = 2 * self.ell + 3
        self.conductance_u = factors[None, :] * cumulative[:-1] / (self.edges[1:-1, None] * self.dx)
        self.boundary_u = 2 * factors * cumulative[-1] / (self.radius * self.dx)

    def lap2(self, q):
        u = q / self.powers[None, :, :]
        flux = self.conductance_u[None, :, :] * np.diff(u, axis=1)
        force = np.zeros_like(q)
        force[:, :-1] += flux; force[:, 1:] -= flux
        force[:, -1] -= self.boundary_u[None, :] * u[:, -1]
        return force / (self.w[:, None] * self.powers)[None, :, :]

    def lap(self, q):
        second = self.lap2(q)
        return second - self.dx ** 2 / 12 * self.lap2(second)

    def components(self, q, v):
        bulk, unused_faces, unused_angular, unused_boundary, charge = super().components(q, v)
        u = q / self.powers[None, :, :]
        difference = np.diff(u, axis=1)
        faces = np.sum(self.conductance_u * (difference[0] ** 2 + difference[1] ** 2 + .5 * difference[2] ** 2), axis=1)
        second = self.lap2(q)
        extra = self.dx ** 2 / 12 * self.w * np.sum(second[0] ** 2 + second[1] ** 2 + .5 * second[2] ** 2, axis=1)
        boundary = np.sum(self.boundary_u * (u[0, -1] ** 2 + u[1, -1] ** 2 + .5 * u[2, -1] ** 2))
        return bulk + extra, faces, np.zeros_like(bulk), boundary, charge

    def weighted_tridiagonal2(self, ell):
        index = int(np.flatnonzero(self.ell == ell)[0]);power = self.powers[:, index];c = self.conductance_u[:, index]
        diagonal = np.r_[c, 0.] + np.r_[0., c];diagonal[-1] += self.boundary_u[index]
        diagonal /= power ** 2 * self.w
        off = -c / (power[:-1] * power[1:] * np.sqrt(self.w[:-1] * self.w[1:]))
        return diagonal, off
