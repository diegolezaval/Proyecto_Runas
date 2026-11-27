"""Presupuesto físico en la malla de la primera corrección, sin otra evolución."""
import csv
import ctypes
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from scipy.linalg import expm

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"correccion_firmada_20261127"))
import medir_correccion as a

o,g,f,z,m,h=a.o,a.g,a.f,a.z,a.m,a.h
W=o.W
om=a.om
cuts=[slice(None,round(60/g.dx)),slice(round(60/g.dx),round(160/g.dx)),slice(round(160/g.dx),None)]
disp=np.array([np.sqrt(2/o.gap),o.kn,1.])
conv=disp[0]/min(o.sw)
limit=o.tube/conv
op=np.sqrt(max(abs(o.A).sum(axis=1).max()+4*om**2,abs(o.P).sum(axis=1).max()))


def advance(solver,step,values):
    bounds=np.zeros_like(solver.x)
    ex=np.empty_like(bounds);ev=np.empty_like(bounds)
    maxx=maxv=0.
    for mapping in solver.maps:
        coeff=np.ascontiguousarray(mapping@values)
        step(g.n,solver.deg,solver.order,h/solver.sub,om,a.loc.c,coeff,solver.x,solver.v,
             solver.work,bounds,ex,ev)
        maxx=max(maxx,np.linalg.norm(o.canon*ex))
        maxv=max(maxv,np.linalg.norm(o.canon*ev))
    return bounds,maxx,maxv


def jac(U,Y):
    den=2*abs(f)*U+U**2
    cross=np.sqrt(2)*((abs(m.trilinear+m.mixed*z)+m.mixed*Y)*U+m.mixed*Y*abs(f))
    return np.maximum(6*m.quartic*den+abs(m.trilinear+m.mixed*z)*Y+.5*m.mixed*Y**2,m.mixed*den)+cross


def charge(x,v):
    u=x[:,0]+1j*x[:,1]
    p=v[:,0]+1j*v[:,1]
    field=f+u
    Q=2*sum64(W*((field.conj()*p).imag+om*abs(field)**2))
    quad=2*sum64(W*((u.conj()*p).imag+om*abs(u)**2))
    q=o.u@(o.canon[:,1]*v[:,1]+2*om*o.canon[:,0]*x[:,0])
    return np.array([Q,quad,q])


def sum64(values):
    return float(np.sum(values,dtype=np.longdouble))


def matrix(F,Fq,ex,ev,L):
    M=np.zeros((4,4))
    M[1,:3]=o.eps*np.array([1/np.sqrt(o.gap),0,1])+L*disp
    M[1,3]=Fq+ev+2*om*ex
    M[0]=o.kc*M[1]
    M[0,:3]+=L*disp
    M[0,2]+=o.eps
    M[0,3]+=F+ev+op*ex
    M[2]=[2*om/np.sqrt(o.gap),abs(o.gamma),0,ex]
    return M


def measure(case,step,march,prior):
    X,V=a.loc.initial(case)
    T,N=a.Forced(8,3,22),a.Forced(8,9,22)
    initial=charge(X,V)
    scale=np.sqrt(2)*np.linalg.norm(o.sw*f)
    lin=np.array([0.,0.,0.,1.]);nonlin=lin.copy();failed=None
    rows=[]
    for i in range(320):
        x,p=X.copy(),V.copy()
        step(g.n,50,.0025,om,a.loc.c,X,V)
        bridge=np.stack([x,x+h*p/3,X-h*V/3,X])
        bt,tx,tv=advance(T,march,a.sample(bridge,3,True))
        bn,nx,nv=advance(N,march,a.sample(bridge,9,False))
        bd=bt+bn
        U=np.hypot(bridge[:,:,0],bridge[:,:,1]).max(axis=0)
        Y=abs(bridge[:,:,2]).max(axis=0)
        d=np.hypot(bd[:,0],bd[:,1]);dy=bd[:,2]
        bulk=jac(U+d,Y+dy)*np.linalg.norm(o.canon*bd,axis=1)
        # Evitar un mismo coeficiente escalar para tres componentes físicas.
        ds=(2*U+d)*d
        dens=2*abs(f)*U+U**2
        dd=2*abs(f)*bd[:,0]+ds
        gz=abs(m.trilinear+m.mixed*z)
        K=2*m.quartic*dens+gz*Y+.5*m.mixed*Y**2
        dk=2*m.quartic*dd+gz*dy+.5*m.mixed*(2*Y+dy)*dy
        dr=abs(f)*(2*m.quartic*ds+.5*m.mixed*(2*Y+dy)*dy)+K*d+dk*(U+d)
        dz=gz*ds+m.mixed*(dens*dy+dd*(Y+dy))
        alt=o.sw*np.hypot(np.sqrt(2)*dr,dz)
        best=np.minimum(bulk,alt)
        imag=K*bd[:,1]+dk*(abs(bridge[:,:,1]).max(axis=0)+bd[:,1])
        fq=abs(o.u)@np.minimum(best,o.canon[:,1]*imag)
        t=(i+1)*h
        xc=X+T.x+N.x;vc=V+T.v+N.v
        actual=o.canon*(a.rest(xc)-a.rest(X))
        assert np.all(np.linalg.norm(actual,axis=1)<=best+1e-14)
        old=np.linalg.norm(bulk*np.sqrt(a.loc.weights))
        assert np.isclose(old,prior[case,t],rtol=1e-12,atol=1e-20)
        F=np.linalg.norm(best);ex=tx+nx;ev=tv+nv
        lin=expm(h*matrix(F,fq,ex,ev,0))@lin
        L=max(jac(U+d+o.tube,Y+dy+o.tube))
        if failed is None:
            nonlin=expm(h*matrix(F,fq,ex,ev,L))@nonlin
            if disp@nonlin[:3]/min(o.sw)>o.tube:failed=t
        dQ,dQ2,dq=charge(xc,vc)-initial
        if i in (0,159,319):
            field=f+xc[:,0]+1j*xc[:,1]
            speed=vc[:,0]+1j*vc[:,1]+1j*om*field
            qlab=np.array([field.real,field.imag,z+xc[:,2]])
            plab=np.array([speed.real,speed.imag,vc[:,2]])
            archived_formula=g.measure(np.pad(qlab,((0,0),(1,1))),np.pad(plab,((0,0),(1,1))),f)[1]
            assert abs(archived_formula-initial[0]-dQ)<2e-10
        bare=charge(X,V)
        quad_corr=charge(xc,vc)[1]-bare[1]
        rec=(dQ-dQ2)/scale
        assert abs(rec-dq)<2e-12
        row=dict(caso=case,t=t,F=F,F_original=np.linalg.norm(bulk),Fq=fq,
                 pos=ex,vel=ev,L=L,D=lin[0],q=lin[1],fase=lin[2],
                 punto_lineal=disp@lin[:3]/min(o.sw),dQ=dQ,dQ2=dQ2,dq=dq,
                 diferencia_Q2_puente=quad_corr,identidad_q=abs(rec-dq))
        for k,sl in enumerate(cuts):
            row["banda"+str(k)]=np.linalg.norm(bulk[sl])
            row["ajustada"+str(k)]=np.linalg.norm(best[sl])
        rows.append(row)
    sums={k:h*sum(r[k] for r in rows) for k in ["F","F_original","Fq","pos","vel"]+
          ["banda"+str(i) for i in range(3)]+["ajustada"+str(i) for i in range(3)]}
    return rows,dict(integrales=sums,cribado_original=bool(sums["F_original"]<=limit),
        cribado_ajustado=bool(sums["F"]<=limit),fin_lineal=lin[:3].tolist(),
        punto_lineal=rows[-1]["punto_lineal"],primer_fallo_no_lineal=failed,
        maximos={k:max(abs(r[k]) for r in rows) for k in ["dQ","dQ2","dq","diferencia_Q2_puente","identidad_q","L"]})


def main():
    with gzip.open(a.HERE/"series.csv.gz","rt") as stream:
        prior={(r["caso"],float(r["t"])):float(r["cota_cambio"]) for r in csv.DictReader(stream)}
    allrows=[];out={}
    with tempfile.TemporaryDirectory() as tmp:
        libs=[]
        for src in (a.ref.HERE/"tangente.c",a.HERE/"polinomio.c"):
            path=Path(tmp)/(src.stem+".so")
            subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",str(src),"-lm","-o",str(path)],check=True)
            libs.append(ctypes.CDLL(str(path)))
        ci,cd=ctypes.c_int,ctypes.c_double
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        step,march=libs[0].advance,libs[1].march
        step.argtypes=[ci,ci,cd,cd]+[ptr]*3;march.argtypes=[ci,ci,ci,cd,cd]+[ptr]*8
        step.restype=march.restype=None
        for case in ("gota_a010","gemelo","receptora"):
            rr,out[case]=measure(case,step,march,prior)
            allrows.extend(rr)
    with (HERE/"bandas.csv").open("w",newline="") as stream:
        wr=csv.DictWriter(stream,fieldnames=allrows[0],lineterminator="\n")
        wr.writeheader();wr.writerows(allrows)
    (HERE/"resultado.json").write_text(json.dumps(dict(conversion=conv,limite=limit,casos=out,
        sha256=a.ref.sha(HERE/"bandas.csv")),indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    main()
