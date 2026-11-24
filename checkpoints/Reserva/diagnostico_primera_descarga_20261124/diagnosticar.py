"""Reconstruye las cuentas y figuras del diagnóstico desde los nueve CSV originales."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np

AQUI = Path(__file__).resolve().parent
ORIGEN = AQUI.parent / "paso3_20261118"
MALLAS = ("espacial", "intermedia", "fina")
PASOS = ("h = 0,40 · dt = 0,01", "h = 0,30 · dt = 0,01", "h = 0,30 · dt = 0,005")
CASOS = ("cargada", "gemelo", "directa")
NOMBRES = ("Donante cargada", "Gemela", "Transmisión directa")
COLORES = ("#92274a", "#00736b", "#4a6daf")
PARTES = ("Receptora", "Donante", "Exterior")
COLUMNAS = "s E Q E_d Q_d E_r Q_r E_ext Q_ext trabajo".split()
VENTANAS = ((200, 240), (200, 220), (220, 240))
S = np.arange(241)


def leer_json(p):
    return json.loads(p.read_text())


def guardar_json(p, data):
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def serie(p):
    d = np.genfromtxt(p, delimiter=",", names=True)
    if list(d.dtype.names) != COLUMNAS or not np.array_equal(d["s"], S):
        raise ValueError(f"Muestreo incorrecto en {p}")
    if not all(np.isfinite(d[k]).all() for k in COLUMNAS):
        raise ValueError(f"Inventario no finito en {p}")
    return d


def originales():
    recibo = leer_json(ORIGEN / "RECIBO_GUARDADO_DESCARGA.json")
    manifiesto = ORIGEN / recibo["manifiesto"]
    if sha(manifiesto) != recibo["sha256_manifiesto"]:
        raise ValueError("Manifiesto distinto del recibo")
    fichas = leer_json(manifiesto)["archivos"]
    datos = {}
    for m in MALLAS:
        datos[m] = {}
        for c in CASOS:
            p = ORIGEN / "primera_descarga" / m / c / "serie.csv"
            if fichas[p.relative_to(ORIGEN).as_posix()] != {"bytes": p.stat().st_size, "sha256": sha(p)}:
                raise ValueError(f"Contenido distinto del manifiesto en {p}")
            datos[m][c] = serie(p)
    return datos


def cambio(d, k):
    return d[k] - d[k][0]


def media(x, a=200, b=240):
    return float(np.trapezoid(x[a:b + 1], x=S[a:b + 1]) / (b - a))


def variaciones(curvas):
    d = media(curvas["fina"])
    v = {"espacio": abs(media(curvas["intermedia"]) - media(curvas["espacial"])),
         "tiempo": abs(d - media(curvas["intermedia"])),
         "ventana_200_220": abs(d - media(curvas["fina"], 200, 220)),
         "ventana_220_240": abs(d - media(curvas["fina"], 220, 240))}
    return d, v


def muestra(x):
    hitos = {str(s): float(x[s]) for s in (0, 1, 8, 40, 74, 120, 200, 220, 240)}
    return dict(hitos, media_200_240=media(x))


def diagnosticar(datos, original):
    brechas, balances, mapas, refinamiento = {}, {}, {}, {}
    for m, d in datos.items():
        brechas[m], balances[m] = {}, {}
        for c in CASOS:
            balances[m][c] = {k: muestra(cambio(d[c], k)) for k in COLUMNAS[1:]}
            for k in ("E", "Q"):
                for a, b in VENTANAS:
                    ref = original["ganancias_receptor"][m][c][k][f"{a}-{b}"]
                    np.testing.assert_allclose(media(cambio(d[c], k+"_r"), a, b), ref, atol=2e-12, rtol=0)
        for c in CASOS[1:]:
            brechas[m][c] = {}
            for k in COLUMNAS[1:]:
                absoluto = d["cargada"][k] - d[c][k]
                saldo = cambio(d["cargada"], k) - cambio(d[c], k)
                ficha = {"diferencia_de_cambios": muestra(saldo)}
                if k in ("E_r", "Q_r"):
                    primero = np.flatnonzero(saldo < 0)
                    ficha.update(ventaja_bruta=muestra(absoluto),
                                 primera_muestra_negativa=int(primero[0]),
                                 muestras_negativas=int(len(primero)),
                                 minimo_bruto=float(absoluto.min()),
                                 fraccion_erosion_media=-media(saldo)/absoluto[0],
                                 fraccion_erosion_s240=-saldo[-1]/absoluto[0])
                brechas[m][c][k] = ficha
    for c in CASOS[1:]:
        refinamiento[c] = {}
        for k in ("E", "Q"):
            curvas = {m: cambio(d["cargada"], k+"_r") - cambio(d[c], k+"_r") for m,d in datos.items()}
            d, v = variaciones(curvas)
            ref = original["contrastes"][c][k]
            np.testing.assert_allclose([d, max(v.values()), *v.values()],
                                       [ref["D"], ref["U"], *[ref["variaciones"][a] for a in v]],
                                       atol=2e-12, rtol=0)
            cambio_h = {cc: (media(cambio(datos["intermedia"][cc], k+"_r"))
                             - media(cambio(datos["espacial"][cc], k+"_r"))) for cc in ("cargada", c)}
            residual = cambio_h["cargada"] - cambio_h[c]
            refinamiento[c][k] = dict(cambios_h=cambio_h, residual=residual,
                                      fraccion_cancelada=1-abs(residual/cambio_h["cargada"]))
    for h, casos in original["mapeo_aislado_por_h"].items():
        mapas[h] = {}
        for k in ("E40", "Q40", "E", "Q"):
            shifts = {c: f[k]["diferencia"] for c, f in casos.items()}
            residual = shifts["cargada"] - shifts["gemelo"]
            radial = casos["cargada"][k]["radial"] - casos["gemelo"][k]["radial"]
            cilindrico = casos["cargada"][k]["cilindrico"] - casos["gemelo"][k]["cilindrico"]
            mapas[h][k] = dict(cambio_mapeo=shifts, exceso_radial=radial, exceso_cilindrico=cilindrico,
                               residual=residual, fraccion_cancelada=1-abs(residual/shifts["gemelo"]),
                               fraccion_cambio_exceso=residual/radial)
    return dict(base="8a032793e8551e4cbc8b94ff99756741b99ca09a", unidades="M2 normalizadas",
                brechas=brechas, cambios_propios=balances, mapeo_aislado=mapas,
                refinamiento_del_saldo=refinamiento, dictamen_original=original["contrastes"])


def lienzo(titulo, nfilas=2, ncols=3):
    fig, axs = plt.subplots(nfilas, ncols, figsize=(4.4*ncols, 2.72*nfilas+0.75),
                            sharex=True, sharey="row", squeeze=False)
    fig.subplots_adjust(left=.088, right=.985, bottom=.19, top=.84, wspace=.075, hspace=.30)
    fig.suptitle(titulo, x=.088, y=.985, ha="left", fontsize=16, weight="bold")
    for ax in axs.flat:
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#dfe4e7", linewidth=.65)
        ax.axvspan(0, 8, color="#f1cf89", alpha=.55, lw=0)
        ax.axvspan(200, 240, color="#dde3ed", alpha=.7, lw=0)
        ax.axvline(74, color="#786e61", ls=":", lw=1)
        ax.axhline(0, color="#59646c", lw=.75)
        ax.set_xlim(0, 240)
        ax.set_xticks([0, 40, 80, 120, 160, 200, 240])
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axs[-1]:
        ax.set_xlabel("Tiempo desde el disparo, s")
    return fig, axs


def leyenda_guardar(fig, ax, nombre, ncol):
    h, labels = ax.get_legend_handles_labels()
    fig.legend(h, labels, loc="lower center", ncol=ncol, frameon=False, bbox_to_anchor=(.5,.025))
    fig.text(.088, .917, "Ámbar: señal activa (0–8)     ·     Punteada: llegada geométrica más temprana (74)     ·     Gris: ventana original (200–240)",
             fontsize=9, color="#455064")
    fig.savefig(AQUI / (nombre+".svg"), metadata={"Date": None})
    plt.close(fig)


def graficas(datos):
    plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "svg.fonttype": "none",
                         "svg.hashsalt": "Reserva-20261124"})
    fig, axs = lienzo("Cambio del inventario de la receptora desde su propio inicio")
    for j, (m, d) in enumerate(datos.items()):
        axs[0,j].set_title(m.capitalize()+"   |   "+PASOS[j], fontsize=10)
        for i, k in enumerate(("E", "Q")):
            for c, color, label, ls in zip(CASOS, COLORES, NOMBRES, ("-", "--", ":")):
                axs[i,j].plot(S, 1e6*cambio(d[c], k+"_r"), color=color, ls=ls, lw=1.6, label=label)
            if j == 0:
                axs[i,j].set_ylabel(("Energía" if i == 0 else "Carga")+"  (×10⁻⁶ M2)")
    leyenda_guardar(fig, axs[0,0], "01_inventario_receptora", 3)

    fig, axs = lienzo("Ventaja inicial y pérdida de esa ventaja en la receptora")
    for j, (m, d) in enumerate(datos.items()):
        axs[0,j].set_title(m.capitalize()+"   |   "+PASOS[j], fontsize=10)
        for i, k in enumerate(("E_r", "Q_r")):
            for c, color, nombre in zip(CASOS[1:], COLORES[1:], ("gemela", "directa")):
                bruto = d["cargada"][k] - d[c][k]
                axs[i,j].plot(S, bruto*1e6, color=color, lw=1.6, label="Inventario frente a "+nombre)
                axs[i,j].plot(S, (bruto-bruto[0])*1e6, color=color, ls="--", lw=1.6,
                              label="Cambio frente a "+nombre)
            if j == 0:
                axs[i,j].set_ylabel(("Energía" if i == 0 else "Carga")+"  (×10⁻⁶ M2)")
    leyenda_guardar(fig, axs[0,0], "02_ventaja_y_cambio", 4)

    fig, axs = lienzo("Dónde cambian la energía y la carga en la malla fina", ncols=2)
    d = datos["fina"]
    for j, c in enumerate(CASOS[1:]):
        axs[0,j].set_title("Cargada menos "+("gemela" if j == 0 else "transmisión directa"))
        for i, k in enumerate(("E", "Q")):
            for suf, color, nom in zip(("_r", "_d", "_ext"), COLORES, PARTES):
                x = cambio(d["cargada"], k+suf)-cambio(d[c], k+suf)
                axs[i,j].plot(S, x*1e6, color=color, lw=1.5, label=nom)
            if i == 0:
                axs[i,j].plot(S, 1e6*(d["cargada"]["trabajo"]-d[c]["trabajo"]), color="#493b2d",
                              lw=1.25, ls="--", label="Trabajo diferencial")
            if j == 0:
                axs[i,j].set_ylabel(("Energía" if i == 0 else "Carga")+"  (×10⁻⁶ M2)")
    leyenda_guardar(fig, axs[0,0], "03_balances_regionales", 4)


if __name__ == "__main__":
    datos = originales()
    guardar_json(AQUI/"DIAGNOSTICO.json", diagnosticar(datos, leer_json(ORIGEN/"RESULTADO_DESCARGA.json")))
    graficas(datos)
