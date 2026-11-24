"""Lee los seis CSV de A=0 y los CSV encendidos; aplica el criterio prerregistrado."""
import argparse
import csv
from pathlib import Path
import sys

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "diagnostico_primera_descarga_20261124"))
from diagnosticar import (COLUMNAS, MALLAS, ORIGEN, S, VENTANAS, cambio, guardar_json, leer_json,
                          media, originales, plt, serie, sha, variaciones)

CASOS = ("cargada", "gemelo")
PISO = 2e-9
MEDIDAS = ("D_on", "D_off", "P_c", "P_g", "I")


def verificar(destino, encendidas):
    recibo = leer_json(destino/"EJECUCION.json")
    fichas = {(x["malla"], x["caso"]):x for x in recibo["trayectorias"]}
    if set(fichas) != {(m,c) for m in MALLAS for c in CASOS} or len(recibo["trayectorias"]) != 6:
        raise ValueError("Faltan trayectorias")
    apagadas, controles = {}, {}
    for m in MALLAS:
        apagadas[m], controles[m] = {}, {}
        for c in CASOS:
            origen, ruta = (destino/m/c/n for n in ("origen.json", "serie.csv"))
            ficha = fichas[m,c]
            if (sha(origen), sha(ruta)) != (ficha["sha256_origen"], ficha["sha256_serie"]):
                raise ValueError(f"Huella distinta del recibo en {m}/{c}")
            ori_on = leer_json(ORIGEN/"primera_descarga"/m/c/"origen.json")
            ori_off = leer_json(origen)
            if ori_off != dict(ori_on, A=0.):
                raise ValueError(f"Preparación distinta en {m}/{c}")
            off, on = serie(ruta), encendidas[m][c]
            dif0 = max(abs(on[k][0] - off[k][0]) for k in COLUMNAS[1:])
            if dif0 > PISO or np.any(off["trabajo"] != 0):
                raise ValueError(f"Identidad inicial o fuente apagada en {m}/{c}")
            for estado, d in (("on",on), ("off",off)):
                controles[m][f"{c}_{estado}"] = {
                    "max_residuo_E": float(max(abs(cambio(d,"E")-d["trabajo"]))),
                    "max_residuo_Q": float(max(abs(cambio(d,"Q")))),
                    "max_residuo_particion_E": float(max(abs(d["E"]-d["E_d"]-d["E_r"]-d["E_ext"]))),
                    "max_residuo_particion_Q": float(max(abs(d["Q"]-d["Q_d"]-d["Q_r"]-d["Q_ext"]))),
                    "trabajo_final":float(d["trabajo"][-1])}
            controles[m][f"{c}_identidad_inicial_max_abs"] = float(dif0)
            apagadas[m][c] = off
    return apagadas, controles


def curvas_receptor(encendidas, apagadas):
    curvas = {}
    for k in ("E", "Q"):
        curvas[k] = {nombre:{} for nombre in MEDIDAS}
        for m in MALLAS:
            con_c, con_g = (cambio(encendidas[m][c], k+"_r") for c in CASOS)
            sin_c, sin_g = (cambio(apagadas[m][c], k+"_r") for c in CASOS)
            don, doff = con_c-con_g, sin_c-sin_g
            pc, pg = con_c-sin_c, con_g-sin_g
            interaccion = don-doff
            np.testing.assert_allclose(interaccion, pc-pg, rtol=0, atol=1e-14)
            for nombre, x in zip(MEDIDAS, (don,doff,pc,pg,interaccion)):
                curvas[k][nombre][m] = x
    return curvas


def clasificar(I, u, limite, doff, uoff):
    if doff + 3*uoff < 0 and abs(I) + 3*u <= limite:
        return "PREDOMINA_PREPARACION"
    if I + 3*u < -limite:
        return "SENAL_AGRAVA_MATERIALMENTE"
    if I - 3*u > limite:
        return "SENAL_ATENUA_MATERIALMENTE"
    return "INDETERMINADO"


def decidir(curvas, controles):
    original = leer_json(ORIGEN/"RESULTADO_DESCARGA.json")["contrastes"]["gemelo"]
    medidas, decisiones = {}, {}
    for k, por_medida in curvas.items():
        medidas[k] = {}
        for nombre, por_malla in por_medida.items():
            val, v = variaciones(por_malla)
            # D_on se reproduce con la definición histórica. En los demás se aplica el nuevo piso.
            if nombre != "D_on":
                v["piso"] = PISO
            if nombre in ("I", "P_c", "P_g"):
                v["prearribo_max_0_60"] = float(max(np.abs(x[:61]).max() for x in por_malla.values()))
            u = max(v.values())
            medidas[k][nombre] = dict(media_fina=val, U=u, tres_U=3*u,
                signo_resuelto=bool(abs(val)>3*u), variaciones=v,
                medias={m:{f"{a}-{b}":media(x,a,b) for a,b in VENTANAS} for m,x in por_malla.items()})
        doff, inter = (medidas[k][n] for n in ("D_off","I"))
        don = original[k]["D"]
        np.testing.assert_allclose([medidas[k]["D_on"]["media_fina"], medidas[k]["D_on"]["U"]],
                                   [don, original[k]["U"]], rtol=0, atol=2e-12)
        escala = .10*abs(don)
        suma = sum(controles["fina"][f"{c}_{a}"]["max_residuo_"+k] for c in CASOS for a in ("on","off"))
        us = max(inter["U"], suma)
        def lectura(u):
            return dict(U=u, limite_abs_I_mas_3U=abs(inter["media_fina"])+3*u,
                        fraccion_max_del_deficit=(abs(inter["media_fina"])+3*u)/abs(don),
                        dictamen=clasificar(inter["media_fina"],u,escala,doff["media_fina"],doff["U"]))
        decisiones[k] = dict(margen_material=escala,
                             Doff_mas_3U=doff["media_fina"]+3*doff["U"],
                             fraccion_deficit_conservado_sin_senal=doff["media_fina"]/don,
                             suma_residuos_globales_finos=suma,
                             principal=lectura(inter["U"]), conservadora=lectura(us))
    conjunta = all(d[t]["dictamen"] == "PREDOMINA_PREPARACION"
                   for d in decisiones.values() for t in ("principal","conservadora"))
    return dict(unidades="M2 normalizadas", ventana=[200,240], base_encendida="8a032793e8551e4cbc8b94ff99756741b99ca09a",
                prerregistro="561874fa850fbc7d93a85a9f7d43d99df8dabdd0", medidas=medidas,
                controles=controles, decision_por_canal=decisiones,
                predominio_preparacion_en_ambos_segun_prerregistro=conjunta,
                primera_entrega_util_demostrada=False, recarga_habilitada=False, segunda_descarga_habilitada=False)


def graficar(curvas):
    plt.rcParams.update({"svg.fonttype":"none","svg.hashsalt":"Reserva-causal-20261124","font.size":9})
    fig, axs = plt.subplots(2,3,figsize=(13.3,6.3),sharex=True)
    fig.subplots_adjust(left=.081,right=.98,top=.82,bottom=.15,hspace=.40,wspace=.39)
    fig.suptitle("Qué parte del saldo cambia al apagar la señal", x=.081, ha="left", fontsize=17, weight="bold")
    fig.text(.081,.906,"Malla fina  ·  Ámbar: señal activa en el ensayo original  ·  Punteada: llegada mínima (74)  ·  Gris: ventana de lectura",
             fontsize=9,color="#455064")
    titulos = ("Diferencia cargada − gemela","Respuesta de cada montaje al disparo","Respuesta adicional de la cargada")
    por_columna = ((("D_on","Encendida","#92274a","-"),("D_off","Apagada","#00736b","--")),
                   (("P_c","Cargada","#92274a","-"),("P_g","Gemela","#00736b","--")),
                   (("I","Interacción (por debajo del piso numérico)","#4a6daf","-"),))
    for j,(titulo,items) in enumerate(zip(titulos,por_columna)):
        axs[0,j].set_title(titulo,fontsize=11,pad=10)
        for i,k in enumerate(("E","Q")):
            ax = axs[i,j]
            ax.axvspan(0,8,alpha=.55,color="#f1cf89",lw=0)
            ax.axvspan(200,240,alpha=.7,color="#dde3ed",lw=0)
            ax.axvline(74,ls=":",lw=1,color="#786e61")
            ax.axhline(0,color="#59646c",lw=.75)
            maximo = max(np.abs(curvas[k][n]["fina"]).max() for n,*_ in items)
            exponente = 6 if maximo >= 5e-7 else 9 if maximo >= 5e-10 else 12
            for n,nom,color,ls in items:
                ax.plot(S,10**exponente*curvas[k][n]["fina"],ls=ls,color=color,lw=1.6,label=nom)
            ax.grid(axis="y",color="#dfe4e7",lw=.65)
            ax.spines[["right","top"]].set_visible(False)
            ax.set_xlim(0,240)
            ax.set_xticks([0,40,80,120,160,200,240])
            ax.set_ylabel(("Energía" if i==0 else "Carga")+f"  ($10^{{-{exponente}}}$ M2)")
            if i==1:
                ax.set_xlabel("Tiempo desde el disparo, s")
                ax.legend(loc="upper center",bbox_to_anchor=(.5,-.28),ncol=2,frameon=False)
    fig.savefig(AQUI/"04_contraste_senal.svg",metadata={"Date":None})
    plt.close(fig)


def guardar_curvas(curvas):
    with (AQUI/"CONTRASTES_POR_TIEMPO.csv").open("w",newline="") as f:
        w = csv.writer(f,lineterminator="\n")
        w.writerow(["malla","s",*[k+"_"+n for k in curvas for n in MEDIDAS]])
        for m in MALLAS:
            for s in S:
                w.writerow([m,s,*[format(curvas[k][n][m][s],".17g") for k in curvas for n in MEDIDAS]])


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos",type=Path,nargs="?",default=AQUI/"datos")
    args = p.parse_args()
    on = originales()
    off, controles = verificar(args.datos,on)
    curvas = curvas_receptor(on,off)
    guardar_json(AQUI/"RESULTADO.json",decidir(curvas,controles))
    guardar_curvas(curvas)
    graficar(curvas)
