"""Presupuesto del núcleo con carga fija y fase separada. Sin integración M2."""
import csv
import gzip
import json
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import bmat,csc_matrix,diags
from scipy.sparse.linalg import splu

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"realimentacion_cargada_20261127"))
import causal as old

o,g,loc,h=old.o,old.g,old.loc,old.h
v,u,om=o.v,o.u,o.om
n=g.n
t=np.clip((g.r-12)/26,0.,1.)
w=1-t*t*(3-2*t)
diag=diags(w)
comm=(o.T@diag-diag@o.T).tocsc()
norms=old.bounds


def cutoff():
    delta=np.diff(w)
    face=loc.face[:-1]
    slope=np.sqrt(max(2*(g.w[:-1]*g.hi[:-1]**2+g.w[1:]*g.lo[1:]**2)*delta**2/face))
    curve=max(abs(g.A@w))
    rows,cols=comm.nonzero()
    assert min(g.r[rows])>10 and max(g.r[cols])<40
    return slope,curve


def evaluation(components=False):
    # Inverse of C by Sherman-Morrison, inverse of P on u-perpendicular by bordering.
    la=splu(o.A)
    av=la.solve(v)
    den=1/(4*om**2)+v@av
    col=csc_matrix(u[:,None])
    lp=splu(bmat([[o.P,col],[col.T,None]],format="csc"))
    coeff=[];worst=0.
    for start in range(0,old.indices[1],10):
        ix=np.arange(start,min(old.indices[1],start+10))
        short=np.eye(len(ix))
        rhs=np.zeros((2*n,2*len(ix)))
        rows=np.r_[ix,n+ix]
        rhs[rows]=np.eye(len(rows))
        a=la.solve(rhs)
        a-=av[:,None]*((v@a)/den)
        ra=np.linalg.norm(rhs-o.A@a-4*om**2*v[:,None]*(v@a),axis=0)
        b_rhs=np.zeros((n+1,len(ix)));b_rhs[ix]=short
        b=lp.solve(b_rhs)[:-1]
        b-=u[:,None]*(u@b)
        rb=o.P@b-b_rhs[:-1]
        rb-=u[:,None]*(u@rb)
        rb=np.linalg.norm(rb,axis=0)
        worst=max(worst,max(ra),max(rb))
        for j,i in enumerate(ix):
            k=[j,j+len(ix)]
            gram=a[np.ix_([i,n+i],k)]
            amp=np.linalg.eigvalsh((gram+gram.T)/2)[-1]+np.linalg.norm(ra[k])/o.gap
            phase=b[i,j]+rb[j]/o.gap
            if components:
                diagonal=np.array([gram[0,0]+ra[k[0]]/o.gap,phase,gram[1,1]+ra[k[1]]/o.gap])
                coeff.append(np.sqrt(diagonal+1e-10)/o.sw[i])
            else:
                coeff.append(np.sqrt(max(amp,phase)+1e-10)/o.sw[i])
    assert worst<1e-8
    return np.array(coeff),worst


def homogeneous():
    # Full-domain direct dynamics, then restriction. Independent of reduced balance.
    r=g.r
    x=np.column_stack([np.cos(r*.19),np.sin(r*.15+.2),np.cos(r*.25+.7)])*np.exp(-r[:,None]/14)
    speed=np.column_stack([np.sin(r*.14+.4),np.cos(r*.22),np.sin(r*.13)])*np.exp(-r[:,None]/11)
    a=np.r_[x[:,0],x[:,2]];b=x[:,1]
    p=np.r_[speed[:,0],speed[:,2]];z=speed[:,1]
    aa=-o.A@a+2*om*np.r_[z,np.zeros(n)]
    ab=-o.P@b-2*om*p[:n]
    ww=np.tile(w,2)
    F=np.r_[comm@x[:,0],comm@x[:,2]];f=comm@b
    a,p,aa=a*ww,p*ww,aa*ww
    b,z,ab=b*w,z*w,ab*w
    q=u@z+2*om*(v@a); beta=u@b
    dq=u@ab+2*om*(v@p);dbeta=u@z
    X=a-o.kap*q;B=b-u*beta
    zp=z-u*dbeta
    enz=p@aa+zp@ab+o.C(X)@(p-o.kap*dq)+(o.P@B)@zp
    work=p@F+zp@(f-beta*(o.P@u))-(o.C(X)@o.kap)*dq
    assert abs(dq-u@f+(o.P@u)@b)<1e-9
    assert abs(enz-work)<1e-9*(1+abs(work))
    return dict(derivada=enz,trabajo=work,error=abs(enz-work),dq=dq)


def main():
    coef,res=evaluation()
    trace=json.loads((old.p.HERE/"traza.json").read_text())["coeficientes"][0]
    assert max(coef)<trace
    s,c=cutoff()
    cw=norms(comm.T@u); uw=norms(u*w); pw=norms((o.P@u)*w)
    bandmax=np.array([max(w[sl]) for sl in old.bands])
    ka,ky=np.split(o.kap,2);sl=old.bands[0]
    kap=np.hypot(ka[sl],ky[sl])/o.sw[sl]
    phase=abs(u[sl])/o.sw[sl]
    with gzip.open(old.p.HERE/"bandas.csv.gz","rt") as fh:
        src=[r for r in csv.DictReader(fh) if r["caso"]=="gota_a010"]
    data=json.loads((HERE.parent/"desplazamiento_local_20261127/resultado.json").read_text())
    prev=data["comparaciones"]["firmado_radios"]["filas"]
    D=Q=beta=0.
    rows=[]
    for j,r in enumerate(prev):
        assert r["t"]==float(src[j]["t"])
        coeffJ=np.array(data["firmado"][j]["J"])
        x=np.array(r["volumen"]);e=np.array(r["energia"])
        rx,rv,Fq=[float(src[j][k]) for k in ("pos","vel","Fq")]
        F=float(src[j]["ajustada0"])
        nonlinear=np.linalg.norm(bandmax*coeffJ*x)
        # A pointwise envelope on the imaginary force was used in the archived Fq.
        qdot=pw@x+cw@x+Fq+uw@(coeffJ*x)+rv+2*om*rx
        Q=min(Q+h*qdot,uw@(e+2*om*x))
        beta_cap=uw@x
        work=s*e[1]+c*x[1]
        DD=F+nonlinear+work+rv+old.p.op*rx+o.kc*qdot+o.eps*beta_cap
        D+=h*DD
        beta=min(beta_cap,beta+h*(2*om/np.sqrt(o.gap)*D+abs(o.gamma)*Q+rx))
        points=coef*D+kap*Q+phase*beta
        point=max(points)
        crude=trace*D+max(kap)*Q+max(phase)*beta
        physical_q_error=norms((1-w)*u)@(e+2*om*x)
        physical_beta_error=norms((1-w)*u)@x
        other=max(r["punto"][1:])
        rows.append(dict(t=r["t"],D=D,q=Q,beta=beta,dq=qdot,punto=point,traza=crude,
                         punto_previo=r["punto"][0],otras=other,intercambio=work,
                         gradiente=s*e[1],curvatura=c*x[1],no_lineal=nonlinear,
                         prescrita=F,cinematica=rx,velocidad=rv,trabajo_carga=o.kc*qdot,
                         trabajo_fase=o.eps*beta_cap,restauracion_q=max(kap)*Q,
                         restauracion_fase=max(phase)*beta,diferencia_q_fisica=physical_q_error,
                         diferencia_fase_fisica=physical_beta_error,
                         aceptado=bool(max(min(point,r["punto"][0]),other)<=o.tube)))
        if not rows[-1]["aceptado"]:break
    result=dict(gradiente=s,curvatura=c,proyeccion_conmutador=cw.tolist(),coef_inversa=max(coef),
                coef_traza=trace,residuo_inversa=res,balance=homogeneous(),filas=rows)
    (HERE/"resultado.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    main()
