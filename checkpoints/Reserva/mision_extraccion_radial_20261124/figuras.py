"""Figuras de los flujos medidos y de la prueba de pared."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np

from balances import AQUI, S, curvas, series


def pagina(titulo,subtitulo,filas,columnas):
    fig,axs=plt.subplots(filas,columnas,figsize=(5.5*columnas,2.75*filas+1.25),sharex=True,squeeze=False)
    fig.subplots_adjust(left=.10,right=.98,bottom=.15,top=.82,hspace=.38,wspace=.25)
    fig.suptitle(titulo,ha="left",x=.10,y=.97,size=16,weight="bold")
    fig.text(.10,.885,subtitulo,color="#374656",fontsize=9)
    for ax in axs.flat:
        ax.set_xlim(0,240)
        ax.set_xticks([0,40,80,120,160,200,240])
        ax.axhline(0,color="#545f68",lw=.8)
        ax.axvspan(200,240,color="#dce4ed",alpha=.75,lw=0)
        ax.grid(axis="y",lw=.65,color="#dfe4e8")
        ax.spines[["top","right"]].set_visible(False)
    for ax in axs[-1]:
        ax.set_xlabel("Tiempo desde el disparo, s")
    return fig,axs


def graficar(datos,dest):
    plt.rcParams.update({"svg.hashsalt":"Reserva-extraccion-20261124","svg.fonttype":"none","font.size":9})
    azul,verde,rojo="#305d95","#00766b","#9b344e"
    f,axs=pagina("Qué atravesó la esfera de radio 60",
        "Caja R = 384  ·  Punteada vertical: llegada mínima en s = 54  ·  Fondo gris: ventana prerregistrada",2,2)
    for i,k in enumerate(("E","Q")):
        cs=curvas(datos,60,k)["principal"]
        a,b=axs[i]
        label="Energía" if k=="E" else "Carga"
        for ax in (a,b):
            ax.axvline(54,color="#6a6258",ls=":",lw=1)
        y=cs["cargada"]
        a.plot(S,y["flujo_bruto"]*1e6,color=azul,label="Flujo encendida − apagada",lw=1.7)
        if k=="E":
            a.plot(S,y["trabajo"]*1e6,color="#665430",ls=":",label="Trabajo del actuador",lw=1.6)
            a.plot(S,y["saldo"]*1e6,color=rojo,ls="--",label="Flujo menos trabajo",lw=1.6)
        a.plot(S,cs["gemela"]["saldo"]*1e6,color=verde,ls="-.",label="Saldo de la gemela",lw=1.4)
        b.plot(S,cs["D"]["saldo"]*1e9,color=rojo,label="Cargada − gemela",lw=1.45)
        a.set_ylabel(label+" (×10⁻⁶ M2)")
        b.set_ylabel(label+" (×10⁻⁹ M2)")
        a.legend(frameon=False,fontsize=8,loc="best")
        if i==0:
            a.set_title("Respuesta al disparo")
            b.set_title("Saldo adicional de la preparación cargada")
    f.savefig(dest/"extraccion.svg",metadata={"Date":None})
    plt.close(f)

    f,axs=pagina("Cuánto cambia la medida al mover la pared",
        "Diferencias R = 256 menos R = 384 en r = 60  ·  Punteadas: primer retorno permitido (8) y llegada de la señal (54)",2,2)
    for i,k in enumerate(("E","Q")):
        cs=curvas(datos,60,k)
        raw=datos["historica"]["cargada"]["apagada"]["F"+k+"60"]-datos["principal"]["cargada"]["apagada"]["F"+k+"60"]
        d=cs["historica"]["D"]["saldo"]-cs["principal"]["D"]["saldo"]
        axs[i,0].plot(S,raw*1e9,color=azul,lw=1.45)
        axs[i,1].plot(S,d*1e12,color=verde,lw=1.4)
        for j,exp in enumerate(("⁻⁹","⁻¹²")):
            ax=axs[i,j]
            ax.axvline(8,color="#766752",ls=":",lw=1)
            ax.axvline(54,color="#766752",ls=":",lw=1)
            ax.set_ylabel(("Energía" if k=="E" else "Carga")+" (×10"+exp+" M2)")
        if i==0:
            axs[i,0].set_title("Flujo de la cargada sin disparar")
            axs[i,1].set_title("Tras restar apagadas, trabajo y gemela")
    f.savefig(dest/"retorno.svg",metadata={"Date":None})
    plt.close(f)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos",type=Path,nargs="?",default=AQUI/"datos")
    p.add_argument("--salida",type=Path,default=AQUI)
    a=p.parse_args()
    graficar(series(a.datos),a.salida)
