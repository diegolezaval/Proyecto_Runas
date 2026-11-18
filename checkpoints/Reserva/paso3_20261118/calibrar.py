"""Fija la amplitud de la fuente neutra con el gemelo radial aislado."""
import argparse
import json
from pathlib import Path

import numpy as np
from retencion import DX, Grid, dump, sha


def envolvente(t):
    return np.sin(np.pi * t / 8)**2 * np.sin(2.3 * t) if 0 < t < 8 else 0.


def soporte(r):
    return np.where(r < 6, np.cos(np.pi * r / 12)**4, 0.)


def ensayo(grid, q0, v0, forma, amplitud, dt, destino):
    q, v = q0.copy(), v0.copy()
    acc = grid.acceleration(q)
    trabajo = 0.
    anterior = 0.
    inc = np.flatnonzero(forma)
    pesos = 4 * np.pi * grid.w[inc] * forma[inc]
    for i in range(1, round(8 / dt) + 1):
        actual = amplitud * envolvente(i * dt)
        v += .5 * dt * acc
        q += dt * v
        trabajo += .5 * (anterior + actual) * dt * (pesos @ v[2, inc])
        acc = grid.acceleration(q)
        acc[2, inc] += actual * forma[inc]
        v += .5 * dt * acc
        anterior = actual
    np.savez_compressed(destino, q=q, v=v, dx=DX, dt=dt, s=8., A=amplitud, trabajo=trabajo)
    return trabajo


def calibrar(base, destino):
    ret = json.loads((base / "RETENCION.json").read_text())
    if not ret["aprobada"]:
        raise ValueError("Retención pendiente")
    objetivo = .10 * ret["paso_temporal"]["dt0005"]["E"]["por_radio"]["40"]["inventario_300"]
    inicial = base / "datos/dt0005/gemelo/tau300.npz"
    with np.load(inicial, allow_pickle=False) as s:
        q0, v0 = s["q"], s["v"]
    destino.mkdir(parents=True)
    grid = Grid(DX)
    forma = soporte(grid.r)
    dt, amplitud = .001, .01
    medidas = []
    for n in range(1, 9):
        archivo = destino / f"ensayo{n}.npz"
        trabajo = ensayo(grid, q0, v0, forma, amplitud, dt, archivo)
        medidas.append(dict(A=amplitud, trabajo=trabajo, estado=archivo.name, sha256=sha(archivo)))
        if not np.isfinite(trabajo) or trabajo <= 0:
            raise ArithmeticError("El ensayo radial no permite calibrar el trabajo positivo.")
        if abs(trabajo / objetivo - 1) <= .02:
            dump(destino / "CALIBRACION.json", dict(A=amplitud, objetivo=objetivo,
                 error_rel=abs(trabajo/objetivo - 1), dt=dt, sha256_gemelo_300=sha(inicial),
                 ensayos=medidas))
            print(amplitud, trabajo, objetivo, flush=True)
            return
        amplitud *= np.sqrt(objetivo / trabajo)
    raise ArithmeticError("Calibración sin converger")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("base", type=Path)
    p.add_argument("destino", type=Path)
    args = p.parse_args()
    calibrar(args.base, args.destino)
