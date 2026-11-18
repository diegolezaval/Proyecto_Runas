"""Contraste diagnóstico del paquete con la dispersión lineal del capítulo 29."""
import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ensayo import OMEGA, ROOT, dump, envelope, model
import numpy as np
import dispersion_reserva_m2 as scattering


def incident():
    dx=.025
    x=np.arange(-512.,512.,dx)
    k=2*np.pi*np.fft.fftfreq(len(x),dx)
    nu=3.2
    k0=np.sqrt(nu*nu-model.mass2)
    b,bp=envelope(x)
    field=np.fft.fft(b*np.exp(1j*k0*x))
    vel=np.fft.fft((1j*nu*b+(k0/nu)*bp)*np.exp(1j*k0*x))
    frequency=np.sqrt(model.mass2+k*k)
    plus=frequency**2*abs((field+vel/(1j*frequency))/2)**2
    minus=frequency**2*abs((field-vel/(1j*frequency))/2)**2
    positive=k>0
    w=plus[positive]/plus[positive].sum()
    offsets=frequency[positive]-OMEGA
    fraction=float(plus[positive].sum()/(plus+minus).sum())
    return offsets,w,fraction


def run(destination):
    raw=json.loads((ROOT/"validacion/P06/acceso_lineal/resultados.json").read_text())
    cache={(round(row["configuration"]["Omega"],6),row["configuration"]["dx"]):row
           for row in raw["records"] if row["configuration"]["radius"]==60 and not row["configuration"]["vacuum"]}
    offsets,w,fraction=incident()
    # Debajo del segundo umbral hay únicamente reflexión elástica de la banda incidente.
    nodes=np.round(np.arange(1.90,2.8001,.01),2)
    summaries={}
    records=[]
    reused=0
    with TemporaryDirectory() as tmp:
        scattering.O=Path(tmp)
        for dx in (.0125,.00625):
            probabilities=[0.]
            for om in nodes[1:]:
                result=cache.get((om,dx))
                if result is None:
                    with redirect_stdout(io.StringIO()):
                        result=scattering.solve(float(om),dx)
                else:
                    reused+=1
                if not result["balance_passed"]:
                    raise ValueError((dx,om))
                case=next(c for c in result["cases"] if c["incoming_channel"]==0)
                probabilities.append(case["outgoing_probabilities"][1])
                records.append([dx,om,probabilities[-1],result["unitary_error"],
                                result["linear_residual_relative"]])
            loss=2*OMEGA*np.array(probabilities)/(nodes+OMEGA)
            for stride in (1,2):
                response=np.interp(offsets,nodes[::stride],loss[::stride],left=0.,right=0.)
                summaries[f"h{dx}_dOmega{.01*stride}"]=float(w@response)
    mid=float(summaries["h0.00625_dOmega0.01"])
    cumulative=np.cumsum(w)
    band=[float(offsets[np.searchsorted(cumulative,p)]) for p in (.025,.975)]
    receipt=dict(interpretacion="Predicción infinitesimal ponderada por energía de la banda entrante positiva del paquete, en vacío asintótico.",
        Omega_central=2.3,banda_central_95_por_ciento_E=band,fraccion_E_preparada_entrante_positiva=fraction,
        peso_fuera_por_encima_2_8=float(w[offsets>2.8].sum()),
        estimaciones=summaries,fraccion_absorcion_lineal=mid,
        diferencia_malla_frecuencia=abs(mid-summaries["h0.00625_dOmega0.02"]),
        diferencia_malla_radial=abs(mid-summaries["h0.0125_dOmega0.01"]),
        frecuencia_U1=OMEGA,puntos_reutilizados_CP07=reused,
        columnas=["dx","Omega","P_positivo_a_negativo","defecto_unitariedad","residuo_relativo"],
        dispersion=records)
    dump(destination,receipt)
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("salida",type=Path)
    args=p.parse_args()
    print(run(args.salida)["fraccion_absorcion_lineal"])
