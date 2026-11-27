"""Contraste de los desplazamientos y cajas contra derivación por paso complejo."""
import json
import numpy as np
import desplazar as d

V,S,s,rate=d.floor_operator()
lam,U=np.linalg.eigh(V)
assert np.max(abs(V@U-U*lam[:,None,:])) < 1e-10
for other in [np.maximum(0,.17-lam),s+.02,np.maximum(0,np.maximum(s-.01,.17-lam)),s+.8]:
    assert np.all(s/np.sqrt(lam+s)<=other/np.sqrt(lam+other)+1e-13)
assert np.all(S[d.loc.i40:]==0)
rng=np.random.default_rng(3459)
centre=rng.uniform(-3e-5,3e-5,(d.g.n,3))
width=rng.uniform(0,3e-5,centre.shape)
point=centre+rng.uniform(-1,1,centre.shape)*width
offset=rng.uniform(-d.tube,d.tube,centre.shape)
J,T=d.columnas.jac_box(centre,width)
_,total=d.columnas.jac_box(centre,width+d.tube)
unit=np.array([np.sqrt(2),np.sqrt(2),1.])
def exact(q):
    cols=[]
    for j in range(3):
        delta=np.zeros(3,dtype=complex)
        delta[j]=1j*1e-25/unit[j]
        cols.append(d.a.rest(q+delta).imag*unit/1e-25)
    return np.stack(cols,axis=2)
assert np.max(abs(exact(centre)-d.blocks(J)))<1e-12
assert np.all(abs(exact(point)-exact(centre))<=d.blocks(T)+1e-12)
assert np.all(abs(exact(point+offset)-exact(point))<=d.blocks(total-T)+1e-12)
result=json.loads((d.HERE/"resultado.json").read_text())
for key,case in result["comparaciones"].items():
    for r in case["filas"]:
        assert (max(r["punto"])<=d.tube)==r["aceptado"]
        if key=="firmado_radios" and r["aceptado"]:
            assert np.all(np.array(r["punto"])<=r["radios"])
print("Verificados mínimo espectral, soporte, tres contrastes del jacobiano y puertas puntuales.")
