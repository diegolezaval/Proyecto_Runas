"""Reconstruye los saldos diferenciales y las dos puertas de la espera."""
import argparse
import json
from pathlib import Path

import numpy as np
from retencion import CASOS, CORTES, DX, FIN, Grid, INICIO, MUESTREO, NAMES, PASOS, dump, entradas


def medir(carpeta):
    grid = Grid(DX)
    perfil, _, _ = grid.equilibrium()
    resultados = {}
    if entradas() != json.loads((carpeta / "INSUMOS.json").read_text()):
        raise ValueError("Procedencia del cálculo")
    for etiqueta, dt in PASOS.items():
        series = {}
        for caso in CASOS:
            base = carpeta / etiqueta / caso
            s = np.genfromtxt(base / "serie.csv", delimiter=",", names=True)
            if list(s.dtype.names) != NAMES or not np.array_equal(
                    s["tau"], np.arange(INICIO, FIN + MUESTREO, MUESTREO)):
                raise ValueError(f"Serie incompleta: {base}")
            for t in CORTES:
                with np.load(base / f"tau{t}.npz", allow_pickle=False) as estado:
                    if (estado["tau"], estado["dt"], estado["dx"]) != (t, dt, DX):
                        raise ValueError(f"Metadatos en τ{t}: {base}")
                    q, v = (np.pad(estado[k], ((0, 0), (1, 1))) for k in ("q", "v"))
                    fila = [*grid.measure(q, v, perfil), *estado["flujo_desde_240"]]
                    np.testing.assert_allclose(fila, [s[k][s["tau"] == t][0] for k in NAMES[1:]],
                                               rtol=5e-14, atol=1e-14)
            series[caso] = s
        gota, gemelo = (series[c] for c in CASOS)
        valores = {k: gota[k] - gemelo[k] for k in NAMES if k != "tau"}
        resumen = {}
        for x in ("E", "Q"):
            nucleo = valores[x + "40"]
            if nucleo[0] <= 0:
                raise ValueError(f"Saldo inicial no positivo: {x}")
            i280 = int((280 - INICIO) / MUESTREO)
            razon = nucleo[-1] / nucleo[0]
            cambio = abs(nucleo[-1] - nucleo[i280]) / nucleo[0]
            cortes = {}
            for r in ("40", "60"):
                interior, flujo = valores[x + r], valores["flujo" + x + r]
                residuo = interior - interior[0] + flujo
                cortes[r] = dict(inventario_240=interior[0], inventario_280=interior[i280],
                                 inventario_300=interior[-1], flujo_neto_saliente=flujo[-1],
                                 continuidad_final=residuo[-1], continuidad_max_abs=max(abs(residuo)))
            resumen[x] = dict(nucleo_300_sobre_240=razon, cambio_280_300_sobre_240=cambio,
                              pasa_90=bool(razon >= .9), pasa_5=bool(cambio < .05), por_radio=cortes,
                              deriva_diferencial_global_max_abs=max(abs(valores[x] - valores[x][0])))
        resultados[etiqueta] = resumen
    diferencia = {}
    for x in ("E", "Q"):
        a, b = (resultados[etiqueta][x] for etiqueta in PASOS)
        diferencia[x] = dict(inventario_40_300_abs=abs(a["por_radio"]["40"]["inventario_300"]
                                                       - b["por_radio"]["40"]["inventario_300"]),
                             razon_final_abs=abs(a["nucleo_300_sobre_240"] - b["nucleo_300_sobre_240"]),
                             cambio_tardio_abs=abs(a["cambio_280_300_sobre_240"] - b["cambio_280_300_sobre_240"]))
    return dict(aprobada=all(f["pasa_90"] and f["pasa_5"] for m in resultados.values() for f in m.values()),
                paso_temporal=resultados, diferencia_temporal=diferencia)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos", type=Path)
    p.add_argument("salida", type=Path)
    args = p.parse_args()
    dump(args.salida, medir(args.datos))
