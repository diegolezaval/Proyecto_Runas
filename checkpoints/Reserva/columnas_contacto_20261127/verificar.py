"""Derivada por paso complejo y cotejo de cada comparación desde cero."""
import csv
import gzip
import json
import numpy as np
from scipy.linalg import expm
import columnas as c


def jacobian():
    rng=np.random.default_rng(2742)
    n=c.m.g.n
    centre=rng.normal(size=(n,3))*2e-5
    width=rng.uniform(2e-7,1e-4,size=(n,3))
    unit=np.array([np.sqrt(2),np.sqrt(2),1])
    J,R=c.jac_box(centre,width)
    ids=[(0,0),(0,1),(0,2),(1,1),(1,2),(2,2)]
    for position in [centre,centre+width,centre-width,centre+width*rng.uniform(-1,1,(n,3))]:
        exact=np.empty((n,3,3))
        for j in range(3):
            delta=np.zeros(3,dtype=complex);delta[j]=1e-25j/unit[j]
            exact[:,:,j]=c.a.rest(position+delta).imag*unit/1e-25
        for i,(j,k) in enumerate(ids):
            assert np.all(abs(exact[:,j,k]-J[i])<=R[i]+1e-14)
            if position is centre:
                assert np.max(abs(exact[:,j,k]-J[i]))<1e-14
        for phase in (False,True):
            vec=np.zeros((n,3))
            if phase:vec[:,1]=c.o.u
            else:vec[:,0],vec[:,2]=c.m.ka,c.m.kz
            v=np.einsum("nij,nj->ni",exact,vec)
            parallel=c.o.u@v[:,1]
            raw=np.linalg.norm(v)
            v[:,1]-=parallel*c.o.u
            upper=c.column(J,R,phase)
            assert np.all(np.array([np.linalg.norm(v),abs(parallel),raw])<=np.array(upper)+1e-13)
            assert abs(raw**2-np.linalg.norm(v)**2-parallel**2)<1e-12


def main():
    jacobian()
    data=json.loads((c.HERE/"resultado.json").read_text())
    old=json.loads((c.previous/"resultado.json").read_text())
    with gzip.open(c.p.HERE/"bandas.csv.gz","rt") as s:
        inputs={(r['caso'],float(r['t'])):r for r in csv.DictReader(s)}
    with (c.HERE/"pasos.csv").open() as s:rows=list(csv.DictReader(s))
    for name,case in data.items():
        for result in case["resumen"]:
            grid,mode=result["escalera"],result["columnas"]
            seq=[r for r in rows if (r["caso"],r["escalera"],r["columnas"])==(name,grid,mode)]
            prev=np.array([0.,0.,0.,1.])
            for j,r in enumerate(seq):
                t=(j+1)/8;rad=float(r["radio"])
                assert float(r["s"])==t and c.m.trace@prev[:3]<=rad<=1e-4
                coeff={float(k):v for k,v in case["bloques"][j//40]["radios"].items()}[rad]
                F,Q=c.coeff(coeff,mode)
                src=inputs[name,t]
                M=c.p.matrix(*[float(src[k]) for k in ("F","Fq","pos","vel")],0)
                M[0,:3]+=F+c.o.kc*Q;M[1,:3]+=Q
                E=expm(M/16);prev=E@(E@prev)
                assert np.allclose(prev[:3],[float(r[k]) for k in ("D","q","beta")],atol=1e-17,rtol=2e-11)
                assert abs(c.m.trace@prev[:3]-float(r["cota"]))<1e-13 and float(r["cota"])<=rad
            assert (len(seq)==320 if result["fallo"] is None else result["fallo"][0]==(len(seq)+1)/8)
            if grid=="decadas" and mode=="base":
                ref=[row for block in old["controles"][name]["bloques"] for row in block.get("pasos_aceptados",[])]
                assert len(ref)==len(seq)
                assert np.allclose([float(r['cota']) for r in seq],np.array(ref)[:,-1],atol=1e-17,rtol=1e-11)
    print("Jacobiano, proyecciones, control anterior y 20 continuaciones verificados.")

if __name__=="__main__":
    main()
