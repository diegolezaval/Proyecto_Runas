"""Energía FV disponible y continuidad causal del contraste de caras."""
from pathlib import Path
import sys
import json
import numpy as np
from scipy.sparse import diags, eye
from scipy.linalg import cholesky_banded

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"radios_acoplados_20261127"))
import comparar as base
d,core,o=base.d,base.core,base.o
archive=json.loads((base.HERE/"resultado.json").read_text())["desde_cero"]["filas"]


def metric():
    rows,cols=core.comm.nonzero()
    outputs=np.unique(rows)
    support=np.arange(cols.min(),cols.max()+1)
    n=len(support)
    shapes,_=d.geometry()
    assert np.all(shapes[1,support]==1)
    C=core.comm[outputs][:,support].tocsc()
    assert C.nnz==len(rows)
    sw=o.sw[support]
    face=4*np.pi*d.loc.face[support[:-1]]
    grad=diags([-np.sqrt(face)/sw[:-1],np.sqrt(face)/sw[1:]],[0,1],shape=(n-1,n))
    V,S,_,_=d.floor_operator()
    floor=.17-1e-10
    assert np.linalg.eigvalsh((V+S)[support])[:,0].min()>floor
    assert np.max(abs(grad@sw))<1e-9
    K=(grad.T@grad+floor*eye(n)).tocsc()
    T=core.o.T[support][:,support]
    assert np.max(abs((grad.T@grad).diagonal(1)-T.diagonal(1)))<1e-9
    square=C.T@C
    widths=np.array([0,-1,-2])
    def factor(gamma,reserve):
        M=gamma**2*K-square
        M=M-reserve*eye(n)
        bands=np.zeros((3,n))
        for i,k in enumerate(widths):
            bands[i,:n-i]=M.diagonal(k)
        return cholesky_banded(bands,lower=True),M
    low=0.
    high=1.
    for _ in range(44):
        mid=(low+high)/2
        try:
            factor(mid,0.)
            high=mid
        except np.linalg.LinAlgError:
            low=mid
    reserve=1e-9
    gamma=high*1.00001
    L,M=factor(gamma,reserve)
    chol=diags([L[i,:n-i] for i in range(3)],widths,shape=(n,n))
    residual=abs(M-chol@chol.T).sum(axis=1).max()
    roundoff=128*np.finfo(float).eps*(1+abs(gamma**2*K).sum(axis=1).max()+abs(square).sum(axis=1).max())
    margin=reserve-residual-roundoff
    assert margin>0
    sample=np.sin(.87*core.g.r[support])*sw
    ratio=np.linalg.norm(C@sample)/np.sqrt(np.linalg.norm(grad@sample)**2+floor*(sample@sample))
    assert ratio<gamma
    return dict(gamma=gamma,filas=len(outputs),insumos=n,caras=n-1,
                radios=core.g.r[support[[0,-1]]].tolist(),piso=floor,
                reserva=reserve,residuo=residual,redondeo=roundoff,margen=margin,
                razon_prueba=ratio)


class Face(base.Transition):
    def __init__(self,gamma):
        super().__init__()
        self.gamma=gamma
        self.active_face=False

    def face_bound(self,x,e):
        old=super().face_bound(x,e)
        return min(old,self.gamma*e[1]) if self.active_face else old


class Policy(base.Policy):
    def __init__(self,model,first):
        super().__init__(model,"desde_cero")
        self.first=first

    def start(self,j,ladder,idx,log):
        self.model.active_face=j>=self.first
        return super().start(j,ladder,idx,log)


def study(step,march,table):
    stats=metric()
    model=Face(stats["gamma"])
    adj=base.prev.kernels()
    out=dict(metrica=stats)
    for label,first,limit in [("control",320,len(archive)),("fijo",len(archive)-1,len(archive)),
                              ("diez",108,None)]:
        model.D=model.Q=model.beta=0.
        policy=Policy(model,first)
        run=base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
                            radii_policy=policy,limit=limit)
        rows=run["filas"]
        assert rows[:first]==archive[:first]
        if label=="control": assert rows==archive
        if label=="fijo":
            assert rows[-1]["radios"]==archive[-1]["radios"]
        out[label]=dict(prefijo=run["prefijo"],filas=rows[min(first,len(archive)-1):],pruebas=policy.tests)
        if label=="fijo":
            old=archive[-1]["nucleo"]
            new=rows[-1]["nucleo"]
            if not (new["cara"]<old["cara"]*(1-1e-6) and new["punto"]<old["punto"]):
                break
    return out


if __name__=="__main__":
    base.cont.main(study,HERE/"resultado.json")
