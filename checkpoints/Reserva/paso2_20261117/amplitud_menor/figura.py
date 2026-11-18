"""Dibuja el saldo neto tardío a partir de los CSV conservados."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

HERE=Path(__file__).resolve().parent
parent=HERE.parent


def read(archive,name):
    return np.genfromtxt(BytesIO(archive.read(name+"/serie.csv")),names=True,delimiter=",")


with ZipFile(parent/"datos/fina_series.zip") as original, ZipFile(HERE/"datos/fina_series.zip") as minor:
    result=json.loads((HERE/"RESULTADO.json").read_text())
    twin=read(original,"gemelo")
    with plt.rc_context({"font.size":10,"svg.hashsalt":"reserva-omega09","svg.fonttype":"none"}):
        fig,ax=plt.subplots(figsize=(7.6,3.8),layout="constrained")
        colors=["#12615D","#428582","#365C9C","#A64A25"]
        for label,amplitude,color in zip(("a0025","a0050","a010","a020"),
                                         ("0,0025","0,0050","0,010","0,020"),colors):
            s=read(minor if label in ("a0025","a0050") else original,"gota_"+label)
            net=s["flujoE60"]-twin["flujoE60"]
            inc=-net[s["tau"]==105][0]
            pick=s["tau"]>=215
            ax.plot(s["tau"][pick],-100*net[pick]/inc,label=amplitude,color=color,lw=2)
            ax.plot(240,-100*net[-1]/inc,"o",ms=4,color=color)
        ax.axhline(100*result["pronostico_lineal"],color="#3C4141",ls="--",lw=1.1,
                   label="Límite lineal del paquete")
        ax.set(xlim=(215,241),xlabel="Tiempo desde la preparación del pulso, τ",
               ylabel="Saldo dentro de r = 60 / energía incidente (%)")
        ax.set_title("Energía que queda dentro del puerto al final del ensayo",loc="left",fontsize=14,pad=10)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value,pos: f"{value:.2f}".replace(".",",")))
        ax.grid(axis="y",alpha=.23)
        ax.spines[["top","right"]].set_visible(False)
        ax.legend(title="Amplitud",ncol=3,fontsize=8.5,frameon=False)
        output=HERE/"retencion_tardia.svg"
        fig.savefig(output,metadata={"Date":None})
        output.write_text("\n".join(line.rstrip() for line in output.read_text().splitlines())+"\n")
