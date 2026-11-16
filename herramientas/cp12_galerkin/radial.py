"""Galerkin conforme en u=r q, sin diferencia radial de P4."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import ctypes
import json
import subprocess

import numpy as np
from numpy.polynomial import Legendre, Polynomial
from scipy.interpolate import CubicSpline
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import splu
from scipy.special import eval_jacobi

RADIUS = 220.0
DEGREE = 5
CHANNELS = np.array([1., 1., .5])


class Cauchy:
    """Las seis funciones y la deformación cuadrupolar que usa CP04→CP10."""
    def __init__(self, path):
        with np.load(path, allow_pickle=False) as data:
            config = json.loads(str(data["config"]))
            if int(data["step"]) * config["dt"] != 1200:
                raise ValueError("Cauchy CP04 con reloj distinto")
            r = (np.arange(config["n"]) + .5) * config["dx"]
            rv = np.r_[-r[::-1], r]
            fields = (data["phi"].real, data["phi"].imag, data["chi"],
                      data["vel"].real, data["vel"].imag, data["vchi"])
            self.splines = tuple(CubicSpline(rv, np.r_[field[::-1], field]) for field in fields)
        self.coefficients = np.array([1., .3, -.2, .7, .4])
        self.coefficients *= np.sqrt(4 * np.pi) / np.linalg.norm(self.coefficients)

    def sample(self, r):
        qv = np.zeros((2, 3, len(r), 25))
        window = np.exp(-(r / 20)**4)
        for functions, values in zip((self.splines[:3], self.splines[3:]), qv):
            for i, f in enumerate(functions):
                values[i, :, 0] = np.sqrt(4 * np.pi) * f(r)
                values[i, :, 4:9] = (-.02 * r * window * f(r, 1))[:, None] * self.coefficients
        return qv


@lru_cache
def lagrange(degree):
    nodes = np.r_[0., (.5 + .5 * Legendre.basis(degree).deriv().roots()), 1.]
    functions = []
    for i, node in enumerate(nodes):
        poly = Polynomial.fromroots(np.delete(nodes, i))
        functions.append(poly / poly(node))
    return functions


def basis(s, ell, origin=False, derivative=False):
    if not origin:
        values = np.column_stack([p.deriv()(s) if derivative else p(s) for p in lagrange(DEGREE)])
        if not derivative:
            values[s == 0.] = np.eye(DEGREE + 1)[0]
            values[s == 1.] = np.eye(DEGREE + 1)[-1]
        return values
    z = 2 * s**2 - 1
    n = ell + 1
    jacobi = [eval_jacobi(j, 2, ell + .5, z) for j in range(DEGREE - 1)]
    if derivative:
        differentiated = [np.zeros_like(s)] + [
            2 * s * (j + ell + 3.5) * eval_jacobi(j - 1, 3, ell + 1.5, z)
            for j in range(1, DEGREE - 1)
        ]
        gradient = n * s**(n-1) * (1 - s**2) - 2 * s**(n+1)
        columns = [gradient * a + s**n * (1 - s**2) * b for a, b in zip(jacobi, differentiated)]
        return np.column_stack([*columns, n * s**(n-1)])
    return np.column_stack([*(s**n * (1 - s**2) * p for p in jacobi), s**n])


@dataclass
class Mode:
    ell: int
    ids: np.ndarray
    sample: csr_matrix
    derivative: csr_matrix
    mass: object
    stiffness: object
    invert_mass: object


class Grid:
    def __init__(self, step, degrees):
        self.h = step
        self.elements = round(RADIUS / step)
        if self.elements * step != RADIUS:
            raise ValueError("La malla Galerkin debe cubrir R=220")
        self.n = self.elements * DEGREE - 1
        self.degrees = np.asarray(degrees)
        # La primera celda usa una familia regular distinta y cuadratura propia.
        rfirst, wfirst = np.polynomial.legendre.leggauss(24)
        rother, wother = np.polynomial.legendre.leggauss(12)
        self.r = np.r_[.5 * step * (rfirst + 1),
                       (np.arange(1, self.elements)[:, None] * step + .5 * step * (rother + 1)).ravel()]
        self.w = .5 * step * np.r_[wfirst, np.tile(wother, self.elements - 1)]
        self.core = self.r < 40
        self.modes = []
        for ell in np.unique(self.degrees):
            b = self.evaluation(self.r, int(ell))
            db = self.evaluation(self.r, int(ell), derivative=True)
            mass = (b.T @ b.multiply(self.w[:, None])).tocsc()
            stiffness = (db.T @ db.multiply(self.w[:, None])
                         + ell * (ell + 1) * b.T @ b.multiply((self.w / self.r**2)[:, None])).tocsc()
            self.modes.append(Mode(int(ell), np.flatnonzero(self.degrees == ell), b, db, mass,
                                   stiffness, splu(mass)))

    def evaluation(self, r, ell, derivative=False):
        e = np.minimum((r / self.h).astype(int), self.elements - 1)
        s = r / self.h - e
        first = e == 0
        grid = []
        for selection, origin in ((first, True), (~first, False)):
            rows = np.flatnonzero(selection)
            if rows.size == 0:
                continue
            values = basis(s[selection], ell, origin, derivative)
            if derivative:
                values /= self.h
            columns = (e[selection, None] * DEGREE - int(not origin)
                       + np.arange(values.shape[1]))
            keep = columns < self.n
            grid.append((np.broadcast_to(rows[:, None], values.shape)[keep], columns[keep], values[keep]))
        ri, ci, values = (np.concatenate(array) for array in zip(*grid))
        return csr_matrix((values, (ri, ci)), shape=(len(r), self.n))

    @staticmethod
    def apply(mat, values):
        shape = values.shape
        return (mat @ values.reshape(shape[0], -1)).reshape((-1, *shape[1:]))

    def values(self, coefficients, r=None, derivative=False):
        result = np.empty((len(self.r) if r is None else len(r), *coefficients.shape[1:]),
                          dtype=coefficients.dtype)
        for mode in self.modes:
            matrix = (mode.derivative if derivative else mode.sample) if r is None else self.evaluation(
                r, mode.ell, derivative)
            result[..., mode.ids] = self.apply(matrix, coefficients[..., mode.ids])
        return result

    def weak_load(self, values):
        result = np.empty((self.n, *values.shape[1:]), dtype=values.dtype)
        for mode in self.modes:
            result[..., mode.ids] = self.apply(mode.sample.T, self.w[:, None, None] * values[..., mode.ids])
        return result

    def mass_solve(self, rhs):
        result = np.empty_like(rhs)
        for mode in self.modes:
            data = rhs[..., mode.ids]
            result[..., mode.ids] = mode.invert_mass.solve(data.reshape(self.n, -1)).reshape(data.shape)
        return result


class Angular:
    def __init__(self, sim, projector, build):
        self.labels = np.asarray(sim.labels, dtype=str)
        self.projector = projector
        self.y = projector.T @ sim.Y
        self.full_y = sim.Y
        self.weights = sim.wa
        self.degrees = np.array([0, 2, 2, 4, 4, 4])
        pairs = np.einsum("ir,jr->rij", self.y, self.y).reshape(len(self.weights), -1)
        weights_sqrt = self.weights**.5
        left, singular, _ = np.linalg.svd(weights_sqrt[:, None] * pairs, full_matrices=False)
        keep = singular > singular[0] * 2e-14
        self.tensor = np.ascontiguousarray(
            (left[:, keep].T @ (weights_sqrt[:, None] * pairs)).reshape(-1, 6, 6))
        self.linear = np.ascontiguousarray(left[:, keep].T @ (weights_sqrt[:, None] * self.y.T))
        self.rank = int(keep.sum())
        self.discarded = float(max(singular[~keep], default=0.) / singular[0])
        shared = build / "m2_angular.so"
        if not shared.is_file():
            subprocess.run(["cc", "-O3", "-fPIC", "-shared", "-std=c11", "-fno-fast-math",
                            str(Path(__file__).with_name("force.c")), "-o", str(shared)], check=True)
        self._library = ctypes.CDLL(str(shared))
        self._kernel = self._library.m2_angular
        ptr = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
        self._kernel.argtypes = [ctypes.c_size_t, ctypes.c_int, ptr, ptr, ptr,
                                 ctypes.c_double, ctypes.c_double, ctypes.c_double, ptr, ptr]
        self._kernel.restype = None

    def evaluate(self, sampled, model):
        nodes = sampled.shape[0]
        force, potential = np.empty_like(sampled, order="C"), np.empty(nodes)
        self._kernel(nodes, self.rank, np.ascontiguousarray(sampled), self.tensor, self.linear,
                     model.quartic, model.trilinear, model.mixed, force, potential)
        return force, potential

    def direct(self, amplitudes, model):
        a, b, chi = np.moveaxis(amplitudes @ self.y, 1, 0)
        density = a*a + b*b
        coupling = 2 * model.quartic * density + model.trilinear * chi + .5 * model.mixed * chi*chi
        full_force = -np.stack((coupling * a, coupling * b,
                               (model.trilinear + model.mixed * chi) * density), axis=1)
        potential = (model.quartic * density**2 + model.trilinear * chi * density
                     + .5 * model.mixed * chi**2 * density) @ self.weights
        full = full_force @ (self.full_y * self.weights).T
        return full @ self.projector, potential, full

    def reduce(self, values):
        return np.moveaxis(values @ self.projector, 1, 0)

    def lift(self, values):
        return np.moveaxis(values @ self.projector.T, 0, 1)
