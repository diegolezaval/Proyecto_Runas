"""Forma exterior extendida dos unidades bajo el peso de energía registrado."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import splu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "evaluacion_60_160_20261128"))
import contrastar as previous

ext = previous.ext
d, q, start = ext.d, ext.q, ext.start
rows_before = json.loads((previous.HERE / "resultado.json").read_text())["causal"]["filas"]
last = len(rows_before) - 1


def coefficients(lam):
    r = d.g.r
    first = np.searchsorted(r, 158.)
    target = d.bands[-1].start - first
    k = np.array(d.geometry()[0][-1, first:], dtype=np.longdouble)**2
    mass = ext.o.W[first:].astype(np.longdouble)
    assert target == 80 and np.all(k[target:] == 1)
    weight = np.r_[(k[1:] + k[:-1])/2, k[-1]]
    faces = (4*np.longdouble(np.pi))*d.loc.face[first:]*weight
    # X bounds only the observed band. Omit its lambda term inside r160.
    potential = (ext.floor*k + lam*(r[first:] >= 160.))*mass
    left = np.r_[0, faces[:-1]]
    diag = potential + faces + left
    safe = diag - 1e-8*mass*k
    piv = safe.copy()
    ell = np.zeros_like(piv)
    for i in range(1,len(piv)):
        ell[i] = -faces[i-1]/piv[i-1]
        piv[i] += ell[i]*faces[i-1]
    assert piv.min()>0
    off = abs(ell[1:]*piv[:-1]+faces[:-1])
    residual = max(abs(piv+np.r_[0,ell[1:]**2*piv[:-1]]-safe)+np.r_[0,off]+np.r_[off,0])
    allowance = 128*np.finfo(float).eps*max(diag+faces+left)
    margin = 1e-8*min(mass*k)-residual-allowance
    assert margin>0
    up = lambda x: np.nextafter(x,np.longdouble(np.inf))
    inv = up(1/piv)
    for i in range(len(inv)-2,-1,-1):
        inv[i] = up(inv[i]+up(up(ell[i+1]**2)*inv[i+1]))
    coef = np.asarray(np.sqrt(inv),float)*(1+1e-12)
    # Independent assembly from gradients in mass-normalized coordinates.
    b = np.array(mass,float)
    f = np.array(faces,float)
    grad = diags([-np.sqrt(f/b),np.sqrt(f[:-1]/b[1:])],[0,1],shape=(len(b),len(b)))
    K = (grad.T@grad + diags(np.asarray(potential/mass,float))).tocsc()
    v = np.cos(.087*r[first:]) + .18*np.sin(1.3*r[first:])
    z = np.sqrt(b)*v
    direct = sum(potential*v*v)+sum(faces[:-1]*np.diff(v)**2)+faces[-1]*v[-1]**2
    mismatch = abs(z@(K@z)/direct-1)
    assert mismatch < 1e-11
    idx = [0,target-1,target,target+1,(target+len(b))//2,len(b)-1]
    rhs = np.zeros((len(b),len(idx)))
    rhs[idx,np.arange(len(idx))]=1
    sol = splu(K).solve(rhs)
    check = np.sqrt(sol[idx,np.arange(len(idx))]/b[idx])
    assert np.all(check<=coef[idx]) and np.allclose(check,coef[idx],rtol=1e-7,atol=0)
    return coef[target:], dict(lam=float(lam),margin=float(margin),residual=float(residual),
        allowance=float(allowance),form_defect=float(mismatch),cells=idx,
        reference=check.tolist(),upper=coef[idx].tolist())


def study(step,march,table):
    old = ext.Evaluator(np.array([ext.coefficients(v)[0] for v in ext.lambdas]))
    middle = ext.Evaluator(np.array([ext.coefficients(v,3)[0] for v in ext.lambdas]),3)
    old.first = middle.first = 0
    coef, margins = zip(*(coefficients(v) for v in ext.lambdas))
    coef = np.array(coef)
    result = dict(matrices=margins)
    model = q.Project(q.wj.prior["metrica"]["gamma"])
    shift = start.fb.sx.Refiner(model)
    fb = start.fb.Feedback(model,shift.shape)
    shift.start = fb.start = 0
    adj = q.base.prev.kernels()
    for mode, first, limit in [("control",320,last+1),("fijo",last,last+1),("causal",0,None)]:
        model.D = model.Q = model.beta = 0.
        class Policy(start.Activation):
            def start(self,j,ladder,idx,log):
                if mode=="fijo" and j==last:
                    return np.searchsorted(ladder,rows_before[-1]["radios"])
                return super().start(j,ladder,idx,log)
        trace = {}
        def points(j,radius,entry,current,state,pt):
            pt = middle.refine(j,radius,entry,current,state,old.refine(j,radius,entry,current,state,pt))
            if j<first:
                return pt
            E,X = old.details["E"],old.details["X"]
            budget = np.hypot(E,np.sqrt(ext.lambdas)*X)[:,None]*(1+1e-12)
            profile = np.min(old.coeff*budget,axis=0)
            idx = profile.argmax()
            radii = d.g.r[d.bands[-1]]
            if mode=="fijo":
                assert radii[idx]<162 and np.isclose(profile[idx],pt[-1],rtol=1e-10,atol=0)
            better = np.min(coef*budget,axis=0)
            joint = np.minimum(profile,better)
            trace.update(X=X,E=E,antes=pt[-1],r_antes=radii[idx],despues=joint.max(),
                         r_despues=radii[joint.argmax()],entrada=entry.tolist(),radios=radius.tolist())
            pt[-1] = min(pt[-1],joint.max())
            return pt
        run = q.base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
            radii_policy=Policy(model,"doce",0),limit=limit,shift_refiner=shift.caps,
            feedback_refiner=fb.caps,point_refiner=points)
        rows=run["filas"]
        assert rows[:first]==rows_before[:first]
        result[mode]=dict(prefijo=run["prefijo"],filas=rows[min(first,last):],ultima=trace)
        if mode=="fijo":
            assert rows[-1]["radios"]==rows_before[-1]["radios"] and rows[-1]["punto"][:-1]==rows_before[-1]["punto"][:-1]
            if not rows[-1]["aceptado"]:
                break
    return result


if __name__=="__main__":
    q.base.cont.main(study,HERE/"resultado.json")
