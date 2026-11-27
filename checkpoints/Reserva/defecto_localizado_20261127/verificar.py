"""Controles independientes del borde, de la energía por cara y de las bandas."""
import csv
import json

import numpy as np
import localizar as loc

g=loc.g
r=g.r
for y in (np.exp(1j*r)*np.exp(-r/80),np.ones_like(r),np.eye(1,len(r),len(r)-1)[0]):
    loc.trace(y)
    # Identidad exacta de telescopaje con extremo de pared nulo.
    q=r*r*abs(y)**2
    a=-np.cumsum(np.diff(q,append=0.)[::-1])[::-1]
    assert np.allclose(q,a,atol=1e-9)
    grad=loc.face@(abs(np.diff(y,append=0))**2)
    assert np.isclose(grad,np.vdot(y,g.w*(g.A@y)).real,rtol=1e-10)
# Una onda manufacturada. Derivada del inventario cinético+gradiente de cada
# interior, asignando media cara en la frontera; debe igualar menos el flujo.
field=np.column_stack((np.cos(r/7),np.sin(r/11),np.cos(r/5)))
speed=np.column_stack((np.sin(r/3),np.cos(r/9),np.sin(r/13)))
b=field.copy()
b[:,0]-=loc.f
b[:,2]-=loc.z
p=speed.copy()
p[:,0]+=loc.om*field[:,1]
p[:,1]-=loc.om*field[:,0]
flux=loc.flux(np.stack([b]*4),np.stack([p]*3))
weights=np.array([2,2,1])
for i,k in enumerate(loc.cuts):
    rate=-np.sum(g.w[:k,None]*speed[:k]*(g.A@field)[:k]*weights)
    bonds=loc.face[:-1]*np.sum(np.diff(field,axis=0)*np.diff(speed,axis=0)*weights,axis=1)
    rate+=np.sum(bonds[:k-1])+.5*bonds[k-1]
    assert abs(4*np.pi*rate+flux[i,0])<2e-6
rows=list(csv.DictReader((loc.HERE/"bandas.csv").open()))
assert len(rows)==85
for i in range(0,len(rows),5):
    for key in ("tiempo","tiempo_phi","tiempo_chi","Taylor","Taylor_phi","Taylor_chi"):
        bounds=np.array([float(x[key]) for x in rows[i:i+5]])
        assert max(bounds[:-1])<=bounds[-1]*(1+1e-12)
        assert bounds[-1]<=sum(bounds[:-1])*(1+1e-12)
assert loc.ref.sha(loc.HERE/"bandas.csv")==json.loads((loc.HERE/"resultado.json").read_text())["sha256"]
print("85 filas; telescopaje, pared, flujo de energía por cara y agregación verificados")
