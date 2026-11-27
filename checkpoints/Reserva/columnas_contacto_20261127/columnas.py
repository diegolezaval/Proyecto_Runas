"""Contraste factorial de las dos columnas restauradas y de las escaleras."""
import csv
import ctypes
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np

HERE=Path(__file__).resolve().parent
previous=HERE.parent/"multiplicador_radial_20261127"
spec=importlib.util.spec_from_file_location("mult",previous/"medir.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
a,p,o=m.a,m.p,m.o
sparse=[1e-9,1e-8,1e-7,1e-6,1e-5,1e-4]
dense=sorted({float(f"{n}e{k}") for n in (1,1.5,2,3,5,7) for k in range(-9,-3) if float(f"{n}e{k}")<=o.tube})
modes=("base","kappa","fase","ambas_sin_proyectar","ambas")


def jac_box(centre,width):
    x,b,y=centre.T;dx,db,dy=width.T
    f=p.f
    lam,g,h=p.m.quartic,p.m.trilinear,p.m.mixed
    gz=g+h*p.z
    aa=2*f*x+x*x
    da=2*abs(f+x)*dx+dx**2
    d2b=2*abs(b)*db+db**2
    density=aa+b*b
    K=2*lam*density+gz*y+.5*h*y*y
    dK=2*lam*(da+d2b)+abs(gz+h*y)*dy+.5*h*dy**2
    sq=np.sqrt(2)
    centreJ=np.array([K+4*lam*aa,4*lam*(f+x)*b,sq*(gz*x+h*y*(f+x)),
                      K+4*lam*b*b,sq*(gz+h*y)*b,h*density])
    radiusJ=np.array([dK+4*lam*da,4*lam*(abs(f+x)*db+abs(b)*dx+dx*db),
                      sq*(abs(gz+h*y)*dx+h*abs(f+x)*dy+h*dx*dy),
                      dK+4*lam*d2b,sq*(abs(gz+h*y)*db+h*abs(b)*dy+h*dy*db),h*(da+d2b)])
    return centreJ,radiusJ


def column(J,R,phase):
    xx,xb,xz,bb,bz,zz=J
    rx,rb,rz,rb2,rbz,rzz=R
    u=o.u
    if phase:
        mid=np.array([xb*u,bb*u,bz*u])
        rad=np.array([rb*abs(u),rb2*abs(u),rbz*abs(u)])
    else:
        k,l=m.ka,m.kz
        mid=np.array([xx*k+xz*l,xb*k+bz*l,xz*k+zz*l])
        rad=np.array([rx*abs(k)+rz*abs(l),rb*abs(k)+rbz*abs(l),rz*abs(k)+rzz*abs(l)])
    parallel=u@mid[1]
    q=abs(parallel)+abs(u)@rad[1]
    amp=np.linalg.norm(abs(mid[[0,2]])+rad[[0,2]])
    raw=np.linalg.norm(abs(mid)+rad)
    # Π elimina cualquier múltiplo de u. Minimizar una cota convexa escalar;
    # todo desplazamiento candidato ya da un mayorante válido.
    from scipy.optimize import minimize_scalar
    scale=np.linalg.norm(abs(mid[1])+rad[1])
    def upper(alpha):
        return np.linalg.norm(abs(mid[1]-alpha*scale*u)+rad[1])
    if scale:
        best=minimize_scalar(upper,bounds=(-2,2),method="bounded",options={"xatol":1e-10})
        perp=min(scale,upper(parallel/scale),best.fun)
    else:
        perp=0.
    return [min(raw,np.hypot(amp,perp)),q,raw]


def bounds(A,P,U,Y,B,lo,hi,radius):
    amp,phase,F,Q=m.multipliers(A,P,U,Y,B,radius)
    J,R=jac_box((lo+hi)/2,(hi-lo)/2+radius)
    k,u=column(J,R,False),column(J,R,True)
    return dict(F=F.tolist(),Q=Q.tolist(),kappa=k,fase=u,amplitud=amp,transversal=phase)


def coeff(data,mode):
    F=np.array(data["F"]);Q=np.array(data["Q"])
    for i,name in enumerate(("kappa","fase"),1):
        if mode in (name,"ambas","ambas_sin_proyectar"):
            projected,parallel,raw=data[name]
            F[i]=min(F[i],raw if mode=="ambas_sin_proyectar" else projected)
            Q[i]=min(Q[i],parallel)
    return F,Q


def screen(case,rows,step,march,A,P):
    X,V=a.loc.initial(case);T,N=a.Forced(8,3,22),a.Forced(8,9,22)
    methods=[(grid,mode) for grid in ("decadas","intermedia") for mode in modes]
    states={key:np.array([0.,0.,0.,1.]) for key in methods}
    failed={};history=[];blocks=[]
    for k in range(8):
        lo=np.full_like(X,np.inf);hi=-lo.copy()
        U,Y,B=np.zeros((3,m.g.n))
        for j in range(40):
            x,w=X.copy(),V.copy()
            step(m.g.n,50,.0025,m.om,a.loc.c,X,V)
            bridge=np.stack([x,x+m.h*w/3,X-m.h*V/3,X])
            bt,*_=p.advance(T,march,a.sample(bridge,3,True))
            bn,*_=p.advance(N,march,a.sample(bridge,9,False))
            bd=bt+bn
            lo=np.minimum(lo,bridge.min(axis=0)-bd);hi=np.maximum(hi,bridge.max(axis=0)+bd)
            uj=np.hypot(bridge[:,:,0],bridge[:,:,1]).max(axis=0)+np.hypot(bd[:,0],bd[:,1])
            U=np.maximum(U,uj)
            Y=np.maximum(Y,abs(bridge[:,:,2]).max(axis=0)+bd[:,2])
            B=np.maximum(B,abs(bridge[:,:,1]).max(axis=0)+bd[:,1])
            assert np.isclose(max(p.jac(uj+o.tube,
                    abs(bridge[:,:,2]).max(axis=0)+bd[:,2]+o.tube)),rows[k*40+j]["L"],rtol=1e-12)
        cache={}
        for row in rows[k*40:k*40+40]:
            for key in methods:
                if key in failed:continue
                grid,mode=key;y=states[key]
                for radius in sparse if grid=="decadas" else dense:
                    if m.trace@y[:3]>radius:continue
                    if radius not in cache:cache[radius]=bounds(A,P,U,Y,B,lo,hi,radius)
                    F,Q=coeff(cache[radius],mode)
                    candidate,pts=m.propagate(y,[row],F,Q)
                    if pts[-1]<=radius:
                        states[key]=candidate
                        history.append([case,grid,mode,row["t"],radius,*candidate[:3],pts[-1]])
                        break
                else:failed[key]=(row["t"],pts[-1])
        blocks.append(dict(fin=(k+1)*5,radios=cache))
    summary=[dict(escalera=grid,columnas=mode,fallo=failed.get((grid,mode)),
                  ultimo=states[grid,mode][:3].tolist(),cota=m.trace@states[grid,mode][:3]) for grid,mode in methods]
    return history,dict(bloques=blocks,resumen=summary)


def main():
    file=p.HERE/"bandas.csv.gz"
    with gzip.open(file,"rb") as s:
        assert hashlib.sha256(s.read()).hexdigest()==json.loads((p.HERE/"resultado.json").read_text())["sha256"]
    with gzip.open(file,"rt") as s:rows=list(csv.DictReader(s))
    A=m.Block(o.A,o.v,4*m.om**2,m.order);P=m.Block(o.P,o.u,0,np.arange(m.g.n))
    data={};history=[]
    with tempfile.TemporaryDirectory() as tmp:
        libs=[]
        for src in (a.ref.HERE/"tangente.c",a.HERE/"polinomio.c"):
            path=Path(tmp)/(src.stem+".so")
            subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",str(src),"-lm","-o",str(path)],check=True)
            libs.append(ctypes.CDLL(str(path)))
        step,march=libs[0].advance,libs[1].march
        ci,cd=ctypes.c_int,ctypes.c_double
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        step.argtypes=[ci,ci,cd,cd]+[ptr]*3;march.argtypes=[ci,ci,ci,cd,cd]+[ptr]*8
        step.restype=march.restype=None
        for case in ("gemelo","receptora"):
            rs=[{k:float(v) for k,v in r.items() if k!="caso"} for r in rows if r["caso"]==case]
            hist,data[case]=screen(case,rs,step,march,A,P)
            history+=hist
    with (HERE/"pasos.csv").open("w",newline="") as s:
        w=csv.writer(s,lineterminator="\n")
        w.writerow(["caso","escalera","columnas","s","radio","D","q","beta","cota"])
        w.writerows(history)
    (HERE/"resultado.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")

if __name__=="__main__":
    main()
