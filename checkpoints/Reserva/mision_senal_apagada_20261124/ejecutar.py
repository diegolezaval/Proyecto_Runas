"""Ejecuta las seis parejas apagadas con el mismo integrador de la descarga original."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import monotonic

import numpy as np

AQUI = Path(__file__).resolve().parent
PASO3 = AQUI.parent / "paso3_20261118"
sys.path.insert(0, str(PASO3))
from descarga import COLUMNAS, MALLAS, Malla, compilar, dump, insumos, rama, sha
from balances_descarga import observar


def correr(destino, jobs):
    caminos, amplitud_original = insumos(PASO3)
    manifiesto = json.loads((PASO3 / "MANIFIESTO_RETENCION.json").read_text())
    for path in (caminos["cargada"], caminos["gemelo"], PASO3 / "calibracion/CALIBRACION.json"):
        if sha(path) != manifiesto[path.relative_to(PASO3).as_posix()]["sha256"]:
            raise ValueError(f"Insumo distinto del publicado: {path}")
    pares = [(m,c) for m in ("fina", "intermedia", "espacial") for c in ("cargada", "gemelo")]
    for m, c in pares:
        ori = json.loads((PASO3/"primera_descarga"/m/c/"origen.json").read_text())
        if ori["A"] != amplitud_original or ori["sha256"] != {k:sha(caminos[k]) for k in ("receptor",c)}:
            raise ValueError(f"Identidad de partida: {m}/{c}")
    destino.mkdir(parents=True, exist_ok=False)
    inicio = monotonic()
    with TemporaryDirectory() as tmp:
        native = compilar(tmp)
        mallas = {h:Malla(h) for h, _ in MALLAS.values()}
        def medir(par):
            m, c = par
            h, dt = MALLAS[m]
            antes = monotonic()
            rama(native, mallas[h], m, c, dt, caminos, 0., destino, 240)
            lugar = destino/m/c
            with np.load(lugar/"s240.npz", allow_pickle=False) as estado:
                if (estado["s"], estado["dt"], estado["A"], estado["trabajo"]) != (240, dt, 0., 0.):
                    raise ValueError(f"Metadatos finales: {par}")
                np.testing.assert_array_equal(estado["rho_caras"], mallas[h].re)
                np.testing.assert_array_equal(estado["z_caras"], mallas[h].ze)
                final = observar(native, mallas[h], estado["q"], estado["v"])
            datos = np.genfromtxt(lugar/"serie.csv", names=True, delimiter=",")
            esperado = [datos[k][-1] for k in COLUMNAS[1:9]]
            np.testing.assert_allclose(final, esperado, atol=2e-10, rtol=2e-13)
            return dict(malla=m, caso=c, segundos=monotonic()-antes,
                        max_diferencia_relectura=float(np.max(np.abs(final-esperado))),
                        sha256_estado=sha(lugar/"s240.npz"), bytes_estado=(lugar/"s240.npz").stat().st_size,
                        sha256_serie=sha(lugar/"serie.csv"), sha256_origen=sha(lugar/"origen.json"))
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            evidencia = list(pool.map(medir, pares))
    dump(destino/"EJECUCION.json", dict(segundos=monotonic()-inicio, trabajadores=jobs,
         pasos_por_montaje={m:round(240/dt) for m,(_,dt) in MALLAS.items()}, trayectorias=evidencia))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("destino", type=Path, help="Directorio nuevo para las series y los campos finales")
    p.add_argument("--jobs", type=int, default=6)
    args = p.parse_args()
    correr(args.destino, args.jobs)
