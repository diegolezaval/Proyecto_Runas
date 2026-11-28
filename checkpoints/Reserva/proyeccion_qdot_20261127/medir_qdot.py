"""Cotas de la proyección imaginaria, distintas del trabajo directo de WJ."""
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"fuerza_wj_20261127"))
import medir_wj as wj
base,d,core,o=wj.base,wj.d,wj.core,wj.o
control=json.loads((wj.HERE/"resultado.json").read_text())["diez"]["filas"]
archive=wj.archive[:108]+control
pad=1+1e-11


def projection(a,c,X):
    valid=c>0
    a,c=(np.asarray(t[valid],np.longdouble) for t in (a,c))
    caps=a/c
    X=np.longdouble(X)
    if not X or not len(c):
        return 0.,0.
    if caps@caps<=X*X:
        return float(pad*a.sum()),0.
    lo=np.longdouble(0)
    hi=np.sqrt(c@c)/(2*X)
    for _ in range(75):
        lam=(lo+hi)/2
        r=np.minimum(caps,c/(2*lam))
        if r@r>X**2:
            lo=lam
        else:
            hi=lam
    r=np.minimum(caps,c/(2*hi))
    return float(pad*(hi*X**2+r@(c-hi*r))),float(hi)


def controls():
    out=[]
    for X,exact in [(1.,1+np.sqrt(.75)),(.25,np.sqrt(5)*.25),(12.,9.)]:
        val,lam=projection(np.array([1.,8.,0.]),np.array([2.,1.,0.]),X)
        assert exact<=val<=exact*(1+2e-11)
        out.append(dict(X=X,exacto=exact,dual=val,multiplicador=lam))
    return out


class Project(wj.Force):
    def charge_source(self,q0,qcoeff,x,upper,cell,transition,row):
        old=super().charge_source(q0,qcoeff,x,upper,cell,transition,row)
        band=qcoeff*x
        band[0]=q0
        comparison=None
        if self.variant!="control":
            sl=d.bands[1]
            p=cell[sl]*o.sw[sl,None]*np.array([np.sqrt(2),np.sqrt(2),1.])
            weights=abs(o.u[sl])*core.w[sl]
            imaginary=upper[sl,1,:]
            a=pad*weights*np.einsum("ij,ij->i",imaginary,p)
            c=pad*weights*np.linalg.norm(imaginary,axis=1)
            box=pad*a.sum()
            cauchy=pad*np.linalg.norm(c)*x[1]
            certified=pad*np.linalg.norm(o.u[sl])*transition
            simple=min(band[1],box,cauchy,certified)
            dual,lam=projection(a,c,x[1])
            comparison=dict(previa=band[1],caja=box,cauchy=cauchy,WJ=certified,dual=dual,lam=lam)
            band[1]=simple if self.variant=="simples" else min(simple,dual)
        self.parts=dict(proyeccion=band.tolist(),fase=(self.pw*x).tolist(),
                        conmutador=(self.cw*x).tolist(),fuente=row["Fq"],
                        defecto_vel=row["vel"],defecto_pos=2*o.om*row["pos"],
                        contraste=comparison)
        return old if self.variant=="control" else min(old,band.sum()*pad)


class Policy(wj.face.Policy):
    def __init__(self,model,variant,first):
        super().__init__(model,108)
        self.variant=variant
        self.first_new=first
        self.record=[]

    def start(self,j,ladder,idx,log):
        idx=super().start(j,ladder,idx,log)
        self.model.mode="diez" if j>=108 else "control"
        self.model.variant=self.variant if j>=self.first_new else "control"
        if j==len(archive)-1 and self.variant in ("simples","dual"):
            return np.searchsorted(ladder,archive[-1]["radios"])
        return idx

    def test(self,j,ladder,idx,entry,pt,cr,e,x):
        done,nxt=super().test(j,ladder,idx,entry,pt,cr,e,x)
        if done and j>=min(len(archive)-1,self.first_new):
            parts=self.model.parts
            total=sum(sum(parts[k]) for k in ("proyeccion","fase","conmutador"))
            total+=sum(parts[k] for k in ("fuente","defecto_vel","defecto_pos"))
            assert np.isclose(total,cr["dq"],rtol=3e-11,atol=1e-30)
            self.record.append(dict(t=(j+1)*d.h,**parts))
        return done,nxt


def study(step,march,table):
    result=dict(controles=controls())
    adj=base.prev.kernels()
    model=Project(wj.prior["metrica"]["gamma"])
    last=len(archive)-1
    for label,first,limit in [("control",320,last+1),("simples",last,last+1),
                              ("dual",last,last+1),("doce",108,None)]:
        model.D=model.Q=model.beta=0.
        policy=Policy(model,label,first)
        run=base.cont.solve(step,march,table,adj=adj,core_model=model,
                            box_observer=model.reference,radii_policy=policy,limit=limit)
        rows=run["filas"]
        assert rows[:first]==archive[:first]
        if label=="control":
            assert rows==archive
            r=rows[-1]["nucleo"]
            result["punto_dq_cero_tasas_fijas"]=max(model.coef*(r["D"]-d.h*r["trabajo_carga"])
                +model.kap*min(rows[-2]["nucleo"]["Q"],r["Q"])+model.phase*r["beta"])
        if label in ("simples","dual"):
            assert rows[-1]["radios"]==archive[-1]["radios"]
        result[label]=dict(prefijo=run["prefijo"],filas=rows[min(first,last):],desglose=policy.record)
        if label=="dual":
            old,new=archive[-1]["nucleo"],rows[-1]["nucleo"]
            if new["dq"]>=old["dq"]*(1-1e-6) or new["punto"]>=old["punto"]:
                break
    return result


if __name__=="__main__":
    base.cont.main(study,HERE/"resultado.json")
