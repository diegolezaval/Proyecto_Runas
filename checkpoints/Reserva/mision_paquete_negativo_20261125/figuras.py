"""Figuras reproducibles del paquete finito a partir de las series y las lecturas."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np

from medir import AQUI

ROJO,VERDE,AZUL="#9b3654","#087569","#305c92"


def estilo(ax):
    ax.grid(axis="y",color="#d8e0e5",linewidth=.7)
    ax.spines[["top","right"]].set_visible(False)
    ax.axhline(0,color="#495866",lw=.7)


def graficar(datos,origen,dest):
    plt.rcParams.update({"font.size":9,"svg.fonttype":"none","svg.hashsalt":"Reserva-Phim-20261125"})
    res=json.loads((origen/"RESULTADO.json").read_text())
    raw={c:np.genfromtxt(datos/"principal"/c/"serie.csv",names=True,delimiter=",")
         for c in ("cargada_con","cargada_sin","gemela_con","gemela_sin","vacio")}
    f,axs=plt.subplots(2,2,figsize=(11.6,6.6),gridspec_kw={"width_ratios":[1.35,1.]})
    f.subplots_adjust(left=.09,right=.98,top=.82,bottom=.13,wspace=.28,hspace=.38)
    f.suptitle("Extracción neta durante el paso del paquete",x=.09,y=.98,ha="left",fontsize=17,weight="bold")
    f.text(.09,.91,"Signo positivo hacia fuera. La entrada de carga negativa suma flujo de carga positivo mientras entra.",color="#425264")
    for i,k in enumerate(("E","Q")):
        a,b=axs[i]
        for ax in (a,b):
            estilo(ax)
        nr="F"+k+"60"
        a.axvspan(400,480,color="#dce5ef",alpha=.8,lw=0)
        for prep,color,ls,nom in (("cargada",ROJO,"-","Cargada"),("gemela",VERDE,"--","Gemela")):
            a.plot(raw[prep+"_con"]["s"],1e3*(raw[prep+"_con"][nr]-raw[prep+"_sin"][nr]),color=color,ls=ls,label=nom,lw=1.65)
        a.plot(raw["vacio"]["s"],1e3*raw["vacio"][nr],color=AZUL,ls=":",lw=1.5,label="Vacío")
        a.set_xlabel("Tiempo desde la preparación del paquete, s")
        a.set_ylabel(("Energía" if k=="E" else "Carga")+" (×10⁻³ M2)")
        a.set_xlim(0,480)
        a.set_xticks(np.arange(0,481,80))
        b.axhline(1e6*res["umbrales"][k],ls=":",color="#996524",lw=1.5,label="1 % almacenado")
        for r,shift,color,marker in (("40",-.10,AZUL,"o"),("60",.10,ROJO,"D")):
            regs=[res["mediciones"][r][k][c] for c in ("cargada","gemela","D")]
            b.errorbar(np.arange(3)+shift,[1e6*x["Y_o_D"] for x in regs],yerr=[1e6*x["tres_U"] for x in regs],
                       ls="",marker=marker,color=color,ms=4.8,capsize=4,label="r = "+r)
        b.set_xticks([0,1,2],["Cargada","Gemela","Diferencia"])
        b.set_xlim(-.5,2.5)
        b.set_ylim(bottom=-1.75)
        b.set_ylabel(("Energía" if k=="E" else "Carga")+" (×10⁻⁶ M2)")
        if i==0:
            a.set_title("Flujo neto adicional acumulado en r = 60")
            b.set_title("Saldo medio de 400 a 480, con ±3U")
            a.legend(frameon=False,loc="lower right")
            b.legend(frameon=False,loc="center right",fontsize=8)
    f.savefig(dest/"flujos_y_saldos.svg",metadata={"Date":None})
    plt.close(f)

    sp=np.genfromtxt(origen/"ESPECTRO.csv",names=True,delimiter=",",dtype=None,encoding="utf8")
    f,axs=plt.subplots(1,2,figsize=(11.4,4.25))
    f.subplots_adjust(left=.09,right=.98,bottom=.22,top=.75,wspace=.28)
    f.suptitle("La banda incidente y la banda convertida en r = 60",x=.09,y=.98,ha="left",fontsize=16,weight="bold")
    f.text(.09,.87,"Malla principal. Ondas de Φ descompuestas por su frecuencia con signo y dirección de propagación.",color="#425264")
    for j,(ax,limits,carrier) in enumerate(zip(axs,[(-1.85,-1.02),(2.82,3.65)],[-1.4,3.2])):
        estilo(ax)
        for c,color,ls,nom in (("cargada",ROJO,"-","Cargada"),("gemela",VERDE,"--","Gemela"),("vacio",AZUL,":","Vacío")):
            s=sp[(sp["r"]==60)&(sp["preparacion"]==c)&(sp["nu"]>=limits[0])&(sp["nu"]<=limits[1])]
            inds=np.argsort(s["nu"]);s=s[inds]
            factor=(1e3 if j==0 else 1e6)/(2*np.pi/480)
            y=(-s["E_entrada"] if j==0 else s["E_salida"])*factor
            ax.plot(s["nu"],y,color=color,ls=ls,lw=1.8,label=nom)
        ax.axvline(carrier,color="#797064",ls=":",lw=1)
        ax.set_xlim(*limits)
        ax.set_xlabel("Frecuencia angular física ν")
        ax.set_ylabel("Energía por unidad de ν "+("(×10⁻³ M2)" if j==0 else "(×10⁻⁶ M2)"))
        ax.set_title("Energía incidente de carga negativa" if j==0 else "Energía saliente de carga positiva")
    axs[1].legend(frameon=False)
    f.savefig(dest/"bandas_direccionales.svg",metadata={"Date":None})
    plt.close(f)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos",type=Path,nargs="?",default=AQUI/"datos")
    p.add_argument("--resultados",type=Path,default=AQUI)
    p.add_argument("--salida",type=Path,default=AQUI)
    a=p.parse_args()
    graficar(a.datos,a.resultados,a.salida)
