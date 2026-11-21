"""Reconstruye la lectura prerregistrada de la primera descarga sin avanzar M2."""
import argparse
import ctypes as ct
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from descarga import COLUMNAS, DX, Grid, HERE, MALLAS, RAMAS, Malla, compilar, dump, insumos, preparado, sha


VENTANAS = ((200, 240), (200, 220), (220, 240))
MAGNITUDES = ("E", "Q")


def leer_serie(path):
    serie = np.genfromtxt(path, delimiter=",", names=True)
    if list(serie.dtype.names) != COLUMNAS or not np.array_equal(serie["s"], np.arange(241)):
        raise ValueError(f"Serie incompleta: {path}")
    if not all(np.isfinite(serie[k]).all() for k in COLUMNAS):
        raise ValueError(f"Observación no finita: {path}")
    return serie


def medias(serie):
    # El paso de muestreo es uno, incluidos los dos extremos de cada ventana.
    salida = {}
    for k in MAGNITUDES:
        saldo = serie[k + "_r"] - serie[k + "_r"][0]
        salida[k] = {f"{a}-{b}": float(np.trapezoid(saldo[a:b + 1], x=serie["s"][a:b + 1]) / (b - a))
                     for a, b in VENTANAS}
    return salida


def contraste(ganancias, control, k):
    diferencias = {}
    for m in MALLAS:
        cargada = ganancias[m]["cargada"][k]
        testigo = ganancias[m][control][k]
        diferencias[m] = {ventana: cargada[ventana] - testigo[ventana] for ventana in cargada}
    d = diferencias["fina"]["200-240"]
    variaciones = {
        "espacio": abs(diferencias["intermedia"]["200-240"] - diferencias["espacial"]["200-240"]),
        "tiempo": abs(d - diferencias["intermedia"]["200-240"]),
        "ventana_200_220": abs(d - diferencias["fina"]["200-220"]),
        "ventana_220_240": abs(d - diferencias["fina"]["220-240"]),
    }
    u = max(variaciones.values())
    return dict(D=d, U=u, tres_U=3*u, pasa=bool(d > 0 and d > 3*u),
                variaciones=variaciones, diferencias=diferencias)


def observar(native, malla, campos, velocidades):
    q, v = (np.pad(x, ((0, 0), (1, 1), (1, 1))) for x in (campos, velocidades))
    out = np.zeros(8)
    # El modo 2 sólo lee q y v. No reconstruye ni avanza el estado.
    native.observar(ct.byref(malla.c), q, np.zeros(1), v, 0., 0., 2, out)
    return out


def proyeccion(native, malla, insumos_radiales):
    radial = Grid(DX)
    salida = {}
    for caso, path in insumos_radiales.items():
        with np.load(path, allow_pickle=False) as f:
            q, v = f["q"], f["v"]
        q0, v0 = (np.pad(x, ((0, 0), (1, 1))) for x in (q, v))
        base = radial.measure(q0, v0, np.hypot(q[0], q[1]))[:4]
        es_receptor = caso == "receptor"
        mapeado, _ = preparado(path, malla.rr if es_receptor else malla.rd)
        obs = observar(native, malla, mapeado[:3], mapeado[3:])
        indice = 4 if es_receptor else 2
        cil = [*obs[:2], *obs[indice:indice+2]]
        salida[caso] = {k: dict(radial=float(r), cilindrico=float(c), diferencia=float(c-r))
                        for k, r, c in zip(("E", "Q", "E40", "Q40"), base, cil)}
    return salida


def revisar_rama(native, malla, dt, caso, directorio, paths, amplitud):
    serie = leer_serie(directorio / "serie.csv")
    origen = json.loads((directorio / "origen.json").read_text())
    esperadas = ("receptor",) if caso == "directa" else ("receptor", caso)
    if origen["sha256"] != {k: sha(paths[k]) for k in esperadas}:
        raise ValueError(f"Insumos de {directorio}")
    if (origen["h"], origen["dt"], origen["A"], origen["nr"], origen["nz"]) != (
            malla.re[1], dt, amplitud, malla.c.nr, malla.c.nz):
        raise ValueError(f"Malla o señal de {directorio}")
    if not np.all(serie["trabajo"][8:] == serie["trabajo"][8]):
        raise ValueError(f"Trabajo después de apagar la fuente: {directorio}")
    with np.load(directorio / "s240.npz", allow_pickle=False) as f:
        if (f["s"], f["dt"], f["A"], f["trabajo"]) != (240, dt, amplitud, serie["trabajo"][-1]):
            raise ValueError(f"Metadatos finales de {directorio}")
        np.testing.assert_array_equal(f["rho_caras"], malla.re)
        np.testing.assert_array_equal(f["z_caras"], malla.ze)
        q, v = f["q"], f["v"]
        if not all(x.shape == (3, malla.c.nr, malla.c.nz) and x.dtype == np.float64
                   and np.isfinite(x).all() for x in (q, v)):
            raise ValueError(f"Campos finales de {directorio}")
        final = observar(native, malla, q, v)
    esperado = [serie[k][-1] for k in COLUMNAS[1:9]]
    np.testing.assert_allclose(final, esperado, atol=2e-10, rtol=2e-13)
    residuos = {"E_menos_trabajo_max_abs": float(max(abs(serie["E"]-serie["E"][0]-serie["trabajo"]))),
                "Q_max_abs": float(max(abs(serie["Q"]-serie["Q"][0])))}
    for k in MAGNITUDES:
        suma = serie[k+"_d"] + serie[k+"_r"] + serie[k+"_ext"]
        residuos[k+"_particion_max_abs"] = float(max(abs(serie[k]-suma)))
    return medias(serie), dict(inventario_inicial={k: float(serie[k][0]) for k in COLUMNAS[1:9]},
                               trabajo=float(serie["trabajo"][-1]), residuos=residuos,
                               diferencia_max_abs_al_releer_campos=float(max(abs(final-esperado))))


def medir(datos):
    paths, amplitud = insumos(HERE)
    retencion = json.loads((HERE / "MANIFIESTO_RETENCION.json").read_text())
    for path in (paths["gemelo"], paths["cargada"], HERE/"calibracion/CALIBRACION.json"):
        if sha(path) != retencion[str(path.relative_to(HERE))]["sha256"]:
            raise ValueError(f"Huella del checkpoint: {path}")
    ganancias, balances, mapeos = {}, {}, {}
    with TemporaryDirectory() as temp:
        native = compilar(temp)
        mallas = {h: Malla(h) for h in sorted({h for h, _ in MALLAS.values()})}
        for h, malla in mallas.items():
            mapeos[str(h)] = proyeccion(native, malla, paths)
        for nombre, (h, dt) in MALLAS.items():
            ganancias[nombre], balances[nombre] = {}, {}
            for caso in RAMAS:
                ganancias[nombre][caso], balances[nombre][caso] = revisar_rama(
                    native, mallas[h], dt, caso, datos/nombre/caso, paths, amplitud)
    contrastes = {control: {k: contraste(ganancias, control, k) for k in MAGNITUDES}
                  for control in ("gemelo", "directa")}
    aprobados = sum(ficha["pasa"] for control in contrastes.values() for ficha in control.values())
    return dict(unidades="M2 normalizadas", A=amplitud, muestras_por_trayectoria=241,
                ventana_principal=[200, 240], contrastes=contrastes, contrastes_aprobados=aprobados,
                pasa_primera_puerta=(aprobados == 4), ganancias_receptor=ganancias,
                balances_por_trayectoria=balances, mapeo_aislado_por_h=mapeos)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos", type=Path)
    p.add_argument("salida", type=Path)
    args = p.parse_args()
    dump(args.salida, medir(args.datos))
