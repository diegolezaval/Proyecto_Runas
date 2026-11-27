"""Controles independientes sobre la entrega publicada."""
import csv
import json
from pathlib import Path

import numpy as np

here = Path(__file__).resolve().parent
rows = json.loads((here/"resultado.json").read_text())["registros"]
previous = list(csv.DictReader((here.parent/"contacto_interno_20261126"/"medidas.csv").open()))
lookup = {(r["dt"],r["donante"],r["d"],r["fase"]):r for r in rows}
assert len(rows)==len(lookup)==36
surface_errors = []
for (dt,case,d,phase),r in lookup.items():
    h = r["fina"]
    # El teorema de Pitágoras del ajuste usa aquí las tasas y Gram publicados.
    c = np.asarray(h["tasas"])
    retained = c @ np.asarray(h["gram"]) @ c / h["norma_fuerza"]**2
    assert abs(retained+h["residuo_rel"]**2-1)<1e-12
    assert h["residuo_rel"]**2+1e-12>=h["fraccion_norma2_chi"]
    assert h["defecto_fase_comun"]<1e-12
    if phase==1:
        neg = lookup[dt,case,d,-1]["fina"]
        odd = (np.asarray(h["flujo_entrante_exacto"])[1]-neg["flujo_entrante_exacto"][1])/2
        prior = next(s for s in previous if s["dt"]==dt and s["donante"]==case
                     and s["d"]==str(d) and s["n"]=="192" and s["T"]=="40" and s["receptora"]=="preparada")
        surface_errors.append(abs(odd-[float(prior["inicial_Q_impar"]),float(prior["inicial_E_impar"])]))
print("Pares de caras contrastados:",len(surface_errors))
print("Máximo cambio absoluto de la corriente impar Q,E (48 frente a 192 nodos):",np.max(surface_errors,axis=0))
print("Para cada separación: defecto diferencial impar en R y global [Q,E], en M2/tiempo")
for d in (80,100,120):
    def contrast(step,grid):
        def odd(case):
            return (np.array(lookup[step,case,d,1][grid]["error_tasa_balance"])
                    -lookup[step,case,d,-1][grid]["error_tasa_balance"])/2
        return odd("gota_a010")-odd("gemelo")
    base = contrast("dt0005","fina")
    print(d,base[1:], "cambio cuadratura",abs(base-contrast("dt0005","gruesa"))[1:],
          "cambio dt",abs(base-contrast("dt001","fina"))[1:])
