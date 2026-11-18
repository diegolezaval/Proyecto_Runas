"""Continúa las dos trayectorias de τ240 con los operadores originales de Reserva."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np

HERE = Path(__file__).resolve().parent
PASO2 = HERE.parent / "paso2_20261117"
sys.path.insert(0, str(PASO2))
from ensayo import Grid, NAMES, PROFILE, ROOT, THETA, dump, native, sha

PASOS = {"dt001": 0.001, "dt0005": 0.0005}
CASOS = ("gota_a010", "gemelo")
DX = 0.025
INICIO = 240
FIN = 300
MUESTREO = 0.5
CORTES = (260, 280, 300)


def entradas():
    manifiesto = json.loads((PASO2 / "MANIFIESTO.json").read_text())
    reproduccion = json.loads((PASO2 / "REPRODUCCION_INDEPENDIENTE.json").read_text())
    huellas = {}
    for path in (PROFILE, THETA, ROOT / "herramientas/modelo_m2.py"):
        esperado = manifiesto["entradas"][str(path.relative_to(ROOT))]
        if sha(path) != esperado:
            raise ValueError(f"Huella de entrada diferente: {path}")
        huellas[str(path.relative_to(ROOT))] = esperado
    for nombre in ("ensayo.py", "radial.c", "datos/fina_series.zip",
                   *(f"datos/{caso}.npz" for caso in CASOS)):
        path = PASO2 / nombre
        ficha = manifiesto["archivos"][nombre]
        if sha(path) != ficha["sha256"] or path.stat().st_size != ficha["bytes"]:
            raise ValueError(f"Manifiesto de paso 2: {nombre}")
        if nombre.startswith("datos/") and reproduccion["archivos"][nombre] != ficha:
            raise ValueError(f"Recibo independiente diferente: {nombre}")
        huellas[str(path.relative_to(ROOT))] = ficha["sha256"]
    for nombre in ("MANIFIESTO.json", "REPRODUCCION_INDEPENDIENTE.json",
                   "RECUPERACION_GITHUB.json", "ESTADO.json"):
        path = PASO2 / nombre
        huellas[str(path.relative_to(ROOT))] = sha(path)
    huellas[str((HERE / "PRERREGISTRO.md").relative_to(ROOT))] = sha(HERE / "PRERREGISTRO.md")
    return huellas


def estado_inicial(caso, grid, perfil):
    with np.load(PASO2 / "datos" / f"{caso}.npz", allow_pickle=False) as estado:
        if (estado["tau"] != INICIO or estado["dx"] != DX
                or estado["dt"] != PASOS["dt001"]):
            raise ValueError(f"Metadatos de partida: {caso}")
        q, v = (np.pad(estado[k], ((0, 0), (1, 1))) for k in ("q", "v"))
    for campo in (q, v):
        if (campo.shape != (3, grid.n + 2) or campo.dtype != np.float64
                or not np.isfinite(campo).all()):
            raise ValueError(f"Campos de partida: {caso}")
    with ZipFile(PASO2 / "datos/fina_series.zip") as archivo:
        with archivo.open(f"{caso}/serie.csv") as stream:
            anterior = np.genfromtxt(stream, delimiter=",", names=True)[-1]
    medido = grid.measure(q, v, perfil)
    if anterior["tau"] != INICIO or not np.allclose(
            medido, [anterior[k] for k in NAMES[1:10]], rtol=2e-13, atol=2e-14):
        raise ValueError(f"Discontinuidad al recuperar τ240: {caso}")
    return q, v


def trayectoria(trabajo, etiqueta, caso, grid, perfil, avanzar):
    dt = PASOS[etiqueta]
    destino = trabajo / etiqueta / caso
    destino.mkdir(parents=True)
    q, v = estado_inicial(caso, grid, perfil)
    flujo = np.zeros(6)
    filas = []
    for indice in range(round((FIN - INICIO) / MUESTREO) + 1):
        tau = INICIO + indice * MUESTREO
        if indice:
            avanzar(grid.n, round(MUESTREO / dt), dt, DX, grid.lo, grid.hi,
                    grid.theta, q, v, flujo)
        fila = [tau, *grid.measure(q, v, perfil), *flujo]
        if not np.isfinite(fila).all():
            raise FloatingPointError(f"{etiqueta} {caso} τ{tau}")
        filas.append(fila)
        if tau in CORTES:
            np.savez_compressed(destino / f"tau{int(tau)}.npz", tau=tau, dx=DX, dt=dt,
                                q=q[:, 1:-1], v=v[:, 1:-1], flujo_desde_240=flujo)
            print(f"{etiqueta} {caso} τ{int(tau)}", flush=True)
    np.savetxt(destino / "serie.csv", filas, delimiter=",", header=",".join(NAMES),
               comments="", fmt="%.17g")


def ejecutar(destino, procesos):
    huellas = entradas()
    grid = Grid(DX)
    perfil, _, _ = grid.equilibrium()
    destino.mkdir(parents=True, exist_ok=True)
    if any(destino.iterdir()):
        raise FileExistsError(f"Usar una carpeta vacía para la reproducción: {destino}")
    dump(destino / "INSUMOS.json", huellas)
    with TemporaryDirectory() as temp, ThreadPoolExecutor(max_workers=procesos) as pool:
        avanzar = native(Path(temp))
        trabajos = [pool.submit(trayectoria, destino, etiqueta, caso, grid, perfil, avanzar)
                    for etiqueta in PASOS for caso in CASOS]
        for trabajo in trabajos:
            trabajo.result()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path)
    parser.add_argument("--procesos", type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    ejecutar(args.destino.resolve(), args.procesos)
