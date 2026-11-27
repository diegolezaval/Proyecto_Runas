"""Controles variacionales, pares de fase y convergencia manufacturada."""
import csv
import json
from pathlib import Path

import numpy as np

from respuesta import Cylinder, digest

here=Path(__file__).resolve().parent
rows=list(csv.DictReader((here/"medidas.csv").open()))
result=json.loads((here/"resultado.json").read_text())
assert len(rows)==result["filas"]==108 and result["sha256_csv"]==digest(here/"medidas.csv")
lookup={(r["dt"],r["donante"],int(r["d"]),r["malla"],int(r["fase"])):r for r in rows}
assert len(lookup)==108
for r in rows:
    val=lambda k:float(r[k])
    assert val("max_rel_eliptico")<1e-10
    assert val("norma_w")<=val("cota_norma_w")*(1+1e-10)
    assert val("energia_cuadratica")>=0
    assert np.isclose(val("energia_cuadratica"),val("media_fuente_w"),rtol=1e-10,atol=0)
for c in result["contrastes_energia"]:
    k=c["magnitud"]
    def val(case,ph):
        return float(lookup[c["dt"],case,c["d"],c["malla"],ph][k])
    delta=((val("gota_a010",1)-val("gemelo",1))-(val("gota_a010",-1)-val("gemelo",-1)))/2
    assert abs(delta-c["diferencia"])<1e-18
# Solución analítica en un cilindro de prueba, potencial positivo variable.
# Verifica por separado la implementación del operador. No cambia el benchmark M2.
errors=[]
for h in (1.,.5,.25):
    R,L=8.,12.
    grid=Cylinder(R,L,h)
    r,z=grid.r,grid.z
    U=(1-(r/R)**2)*np.cos(np.pi*z/(2*L))
    V=10000+r**2/64
    source=(V+(np.pi/(2*L))**2)*U+4/R**2*np.cos(np.pi*z/(2*L))
    u,_=grid.solve(V,source)
    errors.append(np.sqrt(grid.inner(u-U,u-U)/grid.inner(U,U)))
assert errors[2]<errors[1]<errors[0]
print("Error relativo de la prueba manufacturada:",errors)
print("108 registros y 72 contrastes de montaje comprobados.")
