"""Evaluación FV por nodo con corte libre interior y pared física exterior."""
from pathlib import Path
import sys
import json

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import splu

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"activacion_cero_20261128"))
import comparar_inicio as start
q,d,o=start.q,start.d,start.o
archive=json.loads((start.HERE/"resultado.json").read_text())["cero"]["filas"]
last=len(archive)-1
sl=d.bands[-1]
floor=.17-1e-10
lambdas=np.r_[0,.17*np.array([.25,1,4,16,64,256])]


def coefficients(lam,band=-1):
    sl=d.bands[band]
    mass=o.W[sl].astype(np.longdouble)
    edges=4*np.longdouble(np.pi)*d.loc.face[sl].astype(np.longdouble)
    assert np.isclose(d.loc.length[-1],d.g.dx/2) and np.all(d.geometry()[0][band,sl]==1)
    if sl.stop<d.g.n:
        edges[-1]=0.
    left=np.r_[np.longdouble(0),edges[:-1]]
    off=-edges[:-1]
    diagonal=(floor+lam)*mass+edges+left
    # K acts on physical field values. No factor of 1/sqrt(mass) at observation.
    reserve=1e-8
    safe=diagonal-reserve*mass
    piv=safe.copy()
    ell=np.zeros_like(piv)
    for i in range(1,len(piv)):
        ell[i]=off[i-1]/piv[i-1]
        piv[i]-=ell[i]*off[i-1]
    assert piv.min()>0
    dr=abs(piv+np.r_[0,ell[1:]**2*piv[:-1]]-safe)
    side=abs(ell[1:]*piv[:-1]-off)
    residual=max(dr+np.r_[0,side]+np.r_[side,0])
    rounding=128*np.finfo(float).eps*max(diagonal+edges+left)
    margin=reserve*mass.min()-residual-rounding
    assert margin>0
    up=lambda x: np.nextafter(x,np.longdouble(np.inf))
    G=up(1/piv)
    for i in range(len(piv)-2,-1,-1):
        G[i]=up(G[i]+up(up(ell[i+1]**2)*G[i+1]))
    coef=np.asarray(np.sqrt(G),dtype=float)*(1+1e-12)
    # Independent assembly in mass-normalized coordinates, including wall test.
    b=np.asarray(mass,float)
    face=np.asarray(edges,float)
    n=len(b)
    grad=diags([-np.sqrt(face)/np.sqrt(b),np.sqrt(face[:-1])/np.sqrt(b[1:])],[0,1],shape=(n,n))
    normK=(grad.T@grad+diags(np.full(n,floor+lam),0)).tocsc()
    assert np.isclose(np.linalg.norm(grad@np.sqrt(b))**2,face[-1],rtol=1e-11,atol=1e-18)
    indices=np.array([0,n//4,n//2,3*n//4,n-1])
    rhs=np.zeros((n,len(indices)))
    rhs[indices,np.arange(len(indices))]=1
    y=splu(normK).solve(rhs)
    ref=np.sqrt(y[indices,np.arange(len(indices))]/b[indices])
    assert np.all(ref<=coef[indices]) and np.allclose(ref,coef[indices],rtol=1e-7,atol=0)
    meta=dict(lam=float(lam),coef_max=float(max(coef)),r_max=float(d.g.r[sl][coef.argmax()]),
        margen=float(margin),residuo=float(residual),holgura=float(rounding),pivote_min=float(piv.min()),
        indices=indices.tolist(),contraste=ref.tolist(),certificados=coef[indices].tolist())
    return coef,meta


class Evaluator:
    def __init__(self,coeff,band=-1):
        self.coeff=coeff
        self.band=band

    def refine(self,j,radius,entry,current,state,pt):
        if j<self.first:
            return pt
        assert state.floor==floor
        x=current["volumen"][self.band]
        e=current["energia"][self.band]
        old1=state.inv[self.band]*x
        old2=state.vol[self.band]*x+state.res[self.band]*e
        assert pt[self.band]==min(old1,old2)
        energy=self.coeff[0]*e*(1+1e-12)
        use=bool(min(energy.max(),pt[self.band])>radius[self.band])
        env=energy
        if use:
            env=np.min(self.coeff*np.hypot(e,np.sqrt(lambdas)*x)[:,None]*(1+1e-12),axis=0)
        bound=min(pt[self.band],env.max())
        self.details=dict(X=x,E=e,masa=old1,gradiente=old2,energia_sola=energy.max(),
            combinado=env.max(),uso_lambda=use,final=bound,entrada=entry.tolist(),radios=radius.tolist())
        pt[self.band]=bound
        return pt


class Policy(start.Activation):
    def start(self,j,ladder,idx,log):
        idx=super().start(j,ladder,idx,log)
        if self.fixed and j==last:
            return np.searchsorted(ladder,archive[-1]["radios"])
        return idx


def study(step,march,table):
    coeff,meta=zip(*(coefficients(lam) for lam in lambdas))
    ev=Evaluator(np.array(coeff))
    model=q.Project(q.wj.prior["metrica"]["gamma"])
    shift=start.fb.sx.Refiner(model)
    fb=start.fb.Feedback(model,shift.shape)
    shift.start=fb.start=0
    adj=q.base.prev.kernels()
    result=dict(matrices=meta)
    for mode,first,limit in [("control",320,last+1),("fijo",last,last+1),("causal",0,None)]:
        model.D=model.Q=model.beta=0.
        policy=Policy(model,"doce",0)
        policy.fixed=mode=="fijo"
        ev.first=first
        log=[]
        def observe(state,best,rem,jump,op,row,cr,ok):
            if len(state.rows)-1>=first:
                log.append(dict(t=row["t"],aceptado=bool(ok),**ev.details))
        run=q.base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
            radii_policy=policy,limit=limit,shift_refiner=shift.caps,feedback_refiner=fb.caps,
            budget_observer=observe,point_refiner=ev.refine)
        rows=run["filas"]
        assert rows[:first]==archive[:first]
        result[mode]=dict(prefijo=run["prefijo"],filas=rows[min(first,last):],evaluacion=log)
        if mode=="fijo":
            assert rows[-1]["radios"]==archive[-1]["radios"] and rows[-1]["nucleo"]==archive[-1]["nucleo"]
            if not rows[-1]["aceptado"]:
                break
    return result

if __name__=="__main__":
    q.base.cont.main(study,HERE/"resultado.json")
