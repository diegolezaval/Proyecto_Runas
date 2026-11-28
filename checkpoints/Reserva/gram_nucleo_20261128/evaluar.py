"""Envolvente local trasladada del Hessiano en la misma fila causal."""
import json
import sys
from pathlib import Path
import numpy as np
from scipy.sparse import bmat, csc_matrix
from scipy.sparse.linalg import splu

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"extension_r160_20261128"))
import contraste as exterior

core=exterior.q.base.cont.core
o=core.o
sl=exterior.d.bands[0]
archive=json.loads((exterior.HERE/"resultado.json").read_text())["causal"]["filas"]


def grams():
    # Solve the amplitude block as a bordered system, independently of Sherman-Morrison.
    n=core.n
    v=csc_matrix(core.v[:,None])
    u=csc_matrix(core.u[:,None])
    amp=splu(bmat([[o.A,v],[v.T,csc_matrix([[-1/(4*o.om**2)]])]],format="csc"))
    phase=splu(bmat([[o.P,u],[u.T,None]],format="csc"))
    matrices=[]
    errors=[]
    for first in range(0,sl.stop,10):
        cells=np.arange(first,min(first+10,sl.stop))
        size=len(cells)
        idx=np.r_[cells,n+cells]
        rhs=np.zeros((2*n+1,2*size))
        rhs[idx]=np.eye(2*size)
        a=amp.solve(rhs)[:-1]
        ra=np.linalg.norm(rhs[:-1]-o.A@a-4*o.om**2*core.v[:,None]*(core.v@a),axis=0)
        rhs=np.zeros((n+1,size))
        rhs[cells]=np.eye(size)
        b=phase.solve(rhs)[:-1]
        b-=core.u[:,None]*(core.u@b)
        rb=o.P@b-rhs[:-1]
        rb-=core.u[:,None]*(core.u@rb)
        rb=np.linalg.norm(rb,axis=0)
        for j,i in enumerate(cells):
            pair=[j,j+size]
            sub=a[np.ix_([i,i+n],pair)]
            G=np.zeros((3,3))
            G[:2,:2]=(sub+sub.T)/2
            G[2,2]=b[i,j]
            err=max(np.linalg.norm(ra[pair]),rb[j])/o.gap+1e-10
            matrices.append(G/o.sw[i]**2)
            errors.append(err/o.sw[i]**2)
    return np.array(matrices),np.array(errors)


def envelope(G,err,shift,D):
    vals,vec=np.linalg.eigh(G)
    upper=vals+err[:,None]
    lower=np.maximum(0,vals-err[:,None])
    tr=np.einsum("nji,nj->ni",vec,shift)
    top=upper[:,-1]
    bounds=D*np.sqrt(top)+np.linalg.norm(shift,axis=1)
    witness=np.max(D*np.sqrt(lower)+abs(tr),axis=1)
    # Every strict multiplier supplies an upper bound even away from the minimizer.
    for ratio in np.geomspace(1e-6,100,121):
        mu=top*(1+ratio)
        den=mu[:,None]-upper
        assert den.min()>0
        dual=mu*D**2+np.sum(tr**2*mu[:,None]/den,axis=1)
        bounds=np.minimum(bounds,np.sqrt(dual))
        direction=tr/den
        norm=np.linalg.norm(direction,axis=1)
        direction/=np.where(norm>0,norm,1)[:,None]
        support=D*np.sqrt(np.sum(lower*direction**2,axis=1))+np.abs(np.sum(tr*direction,axis=1))
        witness=np.maximum(witness,support)
    assert np.all(witness<=bounds*(1+1e-10))
    return bounds*(1+1e-10),witness*(1-1e-10)


def main():
    G,err=grams()
    old,_=core.evaluation()
    ka,kz=np.split(o.kap,2)
    charge=np.column_stack((ka[sl],kz[sl],0*ka[sl]))/o.sw[sl,None]
    phase=np.column_stack((0*ka[sl],0*ka[sl],core.u[sl]))/o.sw[sl,None]
    assert np.all(charge*phase==0)
    row=archive[-1]
    cr=row["nucleo"]
    D,Q,beta=[cr[k] for k in ("D","Q","beta")]
    shift=charge*Q+phase*beta
    base=old*D+np.linalg.norm(charge,axis=1)*Q+np.linalg.norm(phase,axis=1)*beta
    assert abs(max(base)-cr["punto"])<1e-15 and cr["punto"]==row["punto"][0]
    joint=old*D+np.linalg.norm(shift,axis=1)
    cap,witness=envelope(G,err,shift,D)
    pure,_=envelope(G,err,0*shift,D)
    assert np.allclose(pure,old*D,rtol=1e-7,atol=0)
    # Block symmetry makes all four signs of q,beta equivalent for this upper bound.
    opposite,_=envelope(G,err,charge*Q-phase*beta,D)
    assert np.allclose(opposite,cap,rtol=1e-12,atol=0)
    # (real Phi, chi, imaginary Phi), before canonical sqrt(2) rescaling.
    scale=np.array([1/np.sqrt(2),1.,1/np.sqrt(2)])
    phys,_=envelope(G*scale[:,None]*scale[None,:],err,shift*scale,D)
    best=np.minimum.reduce([base,joint*(1+1e-10),cap])
    pts=row["punto"].copy()
    pts[0]=min(pts[0],max(best))
    entry=archive[-2]["punto"]
    accept=bool(np.all(np.maximum(entry,pts)<=row["radios"]))
    ix=int(best.argmax())
    zero_rest=D*old[ix]
    v=csc_matrix(core.v[:,None])
    system=bmat([[o.A,v],[v.T,csc_matrix([[-1/(4*o.om**2)]])]],format="csc")
    dual_rhs=2*o.om*core.v
    response=splu(system).solve(np.r_[dual_rhs,0.])[:-1]
    residual=np.linalg.norm(o.C(o.kap)-dual_rhs)
    dual=(o.kc+residual/np.sqrt(o.gap))*(1+1e-9)
    check=np.sqrt(dual_rhs@response)
    assert check<=dual and abs(dual-check)<1e-7
    beta_cap=0.
    hist=[]
    for j,sample in enumerate(archive):
        assert sample["t"]==(j+1)*core.h and (sample["aceptado"] or j==len(archive)-1)
        c=sample["nucleo"]
        derivative=dual*c["D"]+(abs(o.gamma)+1e-12)*c["Q"]+c["cinematica"]
        beta_cap=min(c["beta"],(beta_cap+core.h*derivative)*(1+1e-12))
        hist.append(beta_cap)
    moved=charge*Q+phase*beta_cap
    revised,model_lower=envelope(G,err,moved,D)
    revised=np.minimum(best,revised)
    rest=np.linalg.norm(moved,axis=1)
    sufficient=min((o.tube/(1+1e-10)-rest)/old)
    phase_test=dict(coef=dual,contraste=check,residuo=residual,coef_previo=2*o.om/np.sqrt(o.gap),
        beta=beta_cap,serie_beta=hist,punto=max(revised),testigo=max(model_lower),
        D_suficiente_ortogonal=sufficient,ahorro_D_suficiente=max(0.,D-sufficient),
        incremento_D_caras=core.h*cr["cara"])
    return dict(fase_dual=phase_test,t=row["t"],entrada=entry,radios=row["radios"],puntos=pts,aceptada=accept,
        nucleo=cr,cota_previa=max(base),restauraciones_ortogonales=max(joint)*(1+1e-10),
        gram=max(cap),testigo_modelo=max(witness),solo_transversal=max(pure),fisica=max(phys),
        r=float(core.g.r[ix]),D_local_sin_restauraciones=zero_rest,
        carga_local=np.linalg.norm(charge[ix])*Q,fase_local=np.linalg.norm(phase[ix])*beta,
        max_diferencia_control_sin_restauracion=max(abs(pure-old*D)),
        celdas=[dict(r=float(r),previa=a,ortogonal=b,gram=c,testigo=w,final=f)
                for r,a,b,c,w,f in zip(core.g.r[sl],base,joint*(1+1e-10),cap,witness,best)])


if __name__=="__main__":
    (HERE/"resultado.json").write_text(json.dumps(main(),separators=(",",":"),allow_nan=False)+"\n")
