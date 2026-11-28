"""Trabajo directo en 10–40, con el presupuesto de desplazamiento común."""
import json
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"conmutador_fv_20261127"))
import evaluar_caras as face

base=face.base
d,core,o=face.d,face.core,face.o
prior=json.loads((face.HERE/"resultado.json").read_text())
archive=face.archive[:108]+prior["diez"]["filas"]
padding=1e-11


def squared_dual(a,b,X):
    keep=b>0
    if not np.any(keep):
        return 0.,0.
    aa=np.square(a[keep].astype(np.longdouble))
    bb=np.square(b[keep].astype(np.longdouble))
    budget=np.longdouble(X)**2
    # From largest gain to smallest, the maximizing allocation fills each
    # cell up to a²/b². The unsaturated marginal gain gives the dual breakpoint.
    order=np.argsort(-bb)
    cost=np.cumsum(aa[order]/bb[order])
    k=np.searchsorted(cost,budget)
    lam=bb[order[k]] if k<len(order) else 0.
    bound=lam*budget+aa@np.maximum(0,1-lam/bb)
    return float(bound*(1+padding)),float(lam)


def tests():
    log=[]
    for a,b,X,exact in [([1.,2.],[3.,3.],.5,2.25),([1.,2.],[3.,3.],1.,5.),
                        ([1.,8.,0.],[2.,1.,0.],1.,1.75),([0.],[0.],2.,0.)]:
        a,b=map(np.array,(a,b))
        val,lam=squared_dual(a,b,X)
        pos=b>0
        brute=min(t*X**2+np.sum(a[pos]**2*np.maximum(0,1-t/b[pos]**2))
                  for t in np.r_[0,b[pos]**2])
        assert exact<=val<=exact*(1+2*padding) and abs(brute-exact)<1e-13
        log.append(dict(exacto=exact,dual=val,lambda_optima=lam))
    return log


class Force(face.Face):
    def transition_force(self,previous,upper,cell,snorm,X):
        if self.mode=="control":
            return previous
        sl=d.bands[1]
        w=core.w[sl]
        p=cell[sl]*o.sw[sl,None]*np.array([np.sqrt(2),np.sqrt(2),1.])
        b=(1+padding)*w*snorm[sl]
        a=(1+padding)*w*np.linalg.norm(np.einsum("nij,nj->ni",upper[sl],p),axis=1)
        spatial=min(previous,(1+padding)*max(b)*X)
        sq,lam=squared_dual(a,b,X)
        joint=min(spatial,np.sqrt(sq)*(1+padding))
        selected=spatial if self.mode=="producto" else joint
        self.detail=dict(anterior=previous,producto=spatial,cajas=np.linalg.norm(a),
                         dual=np.sqrt(sq)*(1+padding),elegida=selected,X=X,lambda_optima=lam)
        return selected


class Policy(face.Policy):
    def __init__(self,model,mode,first):
        super().__init__(model,108)
        self.variant=mode
        self.change=first

    def start(self,j,ladder,idx,log):
        idx=super().start(j,ladder,idx,log)
        self.model.mode=self.variant if j>=self.change else "control"
        if j==len(archive)-1 and self.variant in ("producto","dual"):
            return np.searchsorted(ladder,archive[-1]["radios"])
        return idx

    def test(self,j,ladder,idx,entry,pt,cr,e,x):
        done,nxt=super().test(j,ladder,idx,entry,pt,cr,e,x)
        if self.model.mode!="control" and done:
            self.details.append(dict(t=(j+1)*d.h,**self.model.detail))
        return done,nxt


def study(step,march,table):
    adj=base.prev.kernels()
    model=Force(prior["metrica"]["gamma"])
    last=len(archive)-1
    result=dict(pruebas=tests())
    for label,first,limit in [("control",320,last+1),("producto",last,last+1),
                              ("dual",last,last+1),("diez",108,None)]:
        model.D=model.Q=model.beta=0.
        policy=Policy(model,label,first)
        policy.details=[]
        run=base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
                            radii_policy=policy,limit=limit)
        rows=run["filas"]
        assert rows[:first]==archive[:first]
        if label=="control":
            assert rows==archive
            cr=rows[-1]["nucleo"]
            result["punto_con_otras_tasas_fijas_y_fuerza_nula"]=max(
                model.coef*(cr["D"]-d.h*cr["no_lineal"])+model.kap*cr["Q"]+model.phase*cr["beta"])
        if label in ("producto","dual"):
            assert rows[-1]["radios"]==archive[-1]["radios"]
        result[label]=dict(prefijo=run["prefijo"],filas=rows[min(first,last):],fuerza=policy.details)
        if label=="dual":
            old,new=archive[-1]["nucleo"],rows[-1]["nucleo"]
            if new["no_lineal"]>=old["no_lineal"]*(1-1e-6) or new["punto"]>=old["punto"]:
                break
    return result


if __name__=="__main__":
    base.cont.main(study,HERE/"resultado.json")
