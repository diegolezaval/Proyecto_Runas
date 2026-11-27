"""Comparación con la traza radial discreta y la misma pared."""
import csv
import json
import numpy as np
from scipy.linalg import expm
import auditar as a

def main():
    c=a.a.loc.c
    vm=np.empty((a.g.n,2,2))
    vm[:,0,0]=-c[:,2];vm[:,1,1]=-c[:,4]
    vm[:,0,1]=vm[:,1,0]=-np.sqrt(2)*c[:,5]
    minimum=min(np.linalg.eigvalsh(vm)[:,0].min(),min(-c[:,3]))
    resistance=1/(4*np.pi*a.a.loc.face)
    tail=np.cumsum(resistance[::-1])[::-1]
    gradient=np.sum(np.diff(tail,append=0)**2/resistance)
    assert np.isclose(gradient,tail[0],rtol=1e-12)
    # D controla la suma de ambas formas (amplitud reducida y fase transversal).
    C=np.sqrt(tail[0]*(1+max(0,-minimum)/a.o.gap))
    ka,kz=np.split(a.o.kap,2)
    coefficients=np.array([C,max(np.hypot(ka,kz)/a.o.sw),max(abs(a.o.u)/a.o.sw)])
    with (a.HERE/"bandas.csv").open() as stream:
        rows=list(csv.DictReader(stream))
    stats={}
    for case in ("gota_a010","gemelo","receptora"):
        linear=conditional=np.array([0.,0.,0.,1.])
        failed=None
        for r in [x for x in rows if x["caso"]==case]:
            x=[float(r[k]) for k in ("F","Fq","pos","vel")]
            linear=expm(a.h*a.matrix(*x,0))@linear
            assert np.allclose(linear[:3],[float(r[k]) for k in ("D","q","fase")],atol=1e-16,rtol=1e-11)
            if failed is None:
                conditional=expm(a.h*a.matrix(*x,float(r["L"])))@conditional
                if coefficients@conditional[:3]>a.o.tube:
                    failed=float(r["t"])
        stats[case]=dict(lineal_punto40=coefficients@linear[:3],primer_exceso=failed)
    (a.HERE/"traza.json").write_text(json.dumps(dict(min_potencial=minimum,
        resistencia=tail[0],coeficientes=coefficients.tolist(),limite_transversal=a.o.tube/C,
        casos=stats),indent=2)+"\n")

if __name__=="__main__":
    main()
