"""Primera corrección radial firmada, siempre sobre un puente prescrito."""
import csv
import ctypes
import gzip
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from scipy.sparse import bmat,block_diag,csr_matrix,diags,eye,kron
from scipy.sparse.linalg import expm_multiply

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"defecto_localizado_20261127"))
import localizar as loc
o,ref,g,m,f,z,om=loc.old,loc.ref,loc.g,loc.m,loc.f,loc.z,loc.om
h=.125
weighted=o.canon*np.sqrt(loc.weights[:,None])
def norm(a):
    return np.linalg.norm(a*weighted)


def rest(q):
    a,b,y=q.T
    d2=a*a+b*b
    den=2*f*a+d2
    dk=2*m.quartic*den+(m.trilinear+m.mixed*z)*y+.5*m.mixed*y*y
    return np.column_stack((f*(2*m.quartic*d2+.5*m.mixed*y*y)+dk*a,
                  dk*b,(m.trilinear+m.mixed*z)*d2+m.mixed*den*y))


def shift_matrix(deg,sub,j):
    # De muestras Chebyshev-Lobatto globales a potencias en el subintervalo.
    nodes=(1-np.cos(np.arange(deg+1)*np.pi/deg))/2
    translate=np.zeros((deg+1,deg+1))
    for i in range(deg+1):
        for k in range(i,deg+1):
            translate[i,k]=comb(k,i)*(j/sub)**(k-i)/sub**i
    return np.linalg.solve(np.vander(nodes,deg+1,increasing=True).T,translate.T).T.copy()


def bridge(b,t):
    d=3*np.diff(b,axis=0)/h
    e=2*np.diff(d,axis=0)/h
    return ((1-t)**3*b[0]+3*t*(1-t)**2*b[1]+3*t*t*(1-t)*b[2]+t**3*b[3],
            (1-t)**2*d[0]+2*t*(1-t)*d[1]+t*t*d[2],(1-t)*e[0]+t*e[1])


def sample(b,deg,temporal):
    nodes=(1-np.cos(np.arange(deg+1)*np.pi/deg))/2
    result=[]
    for t in nodes:
        x,v,acc=bridge(b,t)
        result.append(o.affine(x,v)-acc if temporal else -rest(x))
    return np.array(result).reshape(deg+1,-1)


class Forced:
    def __init__(self,sub,deg,order):
        self.sub,self.deg,self.order=sub,deg,order
        self.maps=[shift_matrix(deg,sub,j) for j in range(sub)]
        self.x=np.zeros((g.n,3));self.v=np.zeros_like(self.x)
        self.work=np.empty((5,g.n,3))

    def advance(self,march,values):
        bound=np.zeros_like(self.x);ex=np.empty_like(bound);ev=np.empty_like(bound)
        dx=dv=0.
        for mapping in self.maps:
            source=np.ascontiguousarray(mapping@values)
            march(g.n,self.deg,self.order,h/self.sub,om,loc.c,source,self.x,self.v,self.work,bound,ex,ev)
            dx=max(dx,norm(ex));dv=max(dv,norm(ev))
        return bound,ex,ev,dx,dv


def generator():
    # Verificación afín independiente. Orden por celdas; velocidad dividida por 100.
    c=loc.c
    local=np.zeros((g.n,3,3))
    for i,j,k in [(0,0,2),(1,1,3),(2,2,4),(0,2,5),(2,0,6)]:
        local[:,i,j]=c[:,k]
    A=-kron(g.A,eye(3))+block_diag(local,format="csr")
    gyro=kron(eye(g.n),np.array([[0,2*om,0],[-2*om,0,0],[0,0,0]]))
    const=np.column_stack((c[:,7],np.zeros(g.n),c[:,8])).reshape(-1,1)/100
    N=3*g.n
    return bmat([[None,100*eye(N),None],[A/100,gyro,csr_matrix(const)],
                 [csr_matrix((1,N)),None,csr_matrix((1,1))]],format="csr")


def inventory(x,v):
    a,b,y=x.T
    field=f+a+1j*b
    speed=v[:,0]+1j*v[:,1]+1j*om*field
    q=np.array([field.real,field.imag,z+y]);p=np.array([speed.real,speed.imag,v[:,2]])
    return np.array(g.measure(np.pad(q,((0,0),(1,1))),np.pad(p,((0,0),(1,1))),f)[2:6])


def run_case(case,march,step,G):
    X,V=loc.initial(case)
    N=X.size
    aff1=np.r_[X.ravel(),V.ravel()/100,1.]
    aff2=aff1.copy()
    T,Tc=Forced(8,3,22),Forced(4,3,22)
    Nf,Nc,Ns=Forced(8,9,22),Forced(4,9,22),Forced(8,3,22)
    begin=inventory(X,V)
    if case!="receptora":
        series,probes=ref.load_reference(case)
        with np.load(ref.P3/"datos/dt0005"/case/"tau300.npz") as src:
            phase=np.exp(1j*np.angle(src["q"][0,0]+1j*src["q"][1,0]))
    rows=[]
    for i in range(320):
        x,p=X.copy(),V.copy()
        step(g.n,50,.0025,om,loc.c,X,V)
        b=np.stack([x,x+h*p/3,X-h*V/3,X])
        ft=sample(b,3,True);fn=sample(b,9,False);fs=sample(b,3,False)
        bt,xt,vt,dt_x,dt_v=T.advance(march,ft)
        bn,xn,vn,dn_x,dn_v=Nf.advance(march,fn)
        Tc.advance(march,ft);Nc.advance(march,fn);Ns.advance(march,fs)
        aff1=expm_multiply(G*h,aff1,traceA=0.)
        for _ in range(2):
            aff2=expm_multiply(G*(h/2),aff2,traceA=0.)
        xc=X+T.x+Nf.x;vc=V+T.v+Nf.v
        rt=rest(xc)-rest(X)
        # Derivada de velocidad del polinomio corregido en el extremo izquierdo
        # del salto entre puentes, usando la ecuación lineal de cada corrección.
        qcorr=xc.copy();qcorr[:,0]+=f;qcorr[:,2]+=z
        full=g.acceleration(qcorr.T).T
        full[:,0]+=om**2*qcorr[:,0]+2*om*vc[:,1]
        full[:,1]+=om**2*qcorr[:,1]-2*om*vc[:,0]
        measured=bridge(b,1)[2]+(o.affine(T.x,T.v)-o.affine(np.zeros_like(X),np.zeros_like(V)))+ft[-1].reshape(X.shape)+vt
        measured+=(o.affine(Nf.x,Nf.v)-o.affine(np.zeros_like(X),np.zeros_like(V)))+fn[-1].reshape(X.shape)+vn
        direct=np.max(abs(measured-full-(rt+vt+vn)))
        assert direct<1e-8
        # Mayorante local del cambio del resto sobre TODOS los subintervalos.
        bd=bt+bn; up=np.hypot(bd[:,0],bd[:,1])
        U=np.hypot(b[:,:,0],b[:,:,1]).max(axis=0)+up
        Y=np.max(abs(b[:,:,2]),axis=0)+bd[:,2]
        den=2*abs(f)*U+U**2
        cross=np.sqrt(2)*((abs(m.trilinear+m.mixed*z)+m.mixed*Y)*U+m.mixed*Y*abs(f))
        lip=np.maximum(6*m.quartic*den+abs(m.trilinear+m.mixed*z)*Y+.5*m.mixed*Y**2,m.mixed*den)+cross
        t=(i+1)*h
        row=dict(caso=case,t=t,cT_x=norm(T.x),cT_v=norm(T.v),cN_x=norm(Nf.x),cN_v=norm(Nf.v),
            identidad1_x=norm(aff1[:N].reshape(X.shape)-X-T.x),
            identidad2_x=norm(aff2[:N].reshape(X.shape)-X-T.x),
            identidad1_v=norm(100*aff1[N:-1].reshape(X.shape)-V-T.v),
            identidad2_v=norm(100*aff2[N:-1].reshape(X.shape)-V-T.v),
            resol_T_x=norm(T.x-Tc.x),resol_T_v=norm(T.v-Tc.v),resol_N_x=norm(Nf.x-Nc.x),
            resol_N_v=norm(Nf.v-Nc.v),muestreo_N_x=norm(Nf.x-Ns.x),muestreo_N_v=norm(Nf.v-Ns.v),
            defecto_T_x=dt_x,defecto_T_v=dt_v,defecto_N_x=dn_x,defecto_N_v=dn_v,
            resto_original=norm(rest(X)),cambio_resto=norm(rt),cota_cambio=norm(lip[:,None]*bd),
            directo=direct)
        for label,sol in (("T",T),("N",Nf)):
            y=sol.x*o.canon;pv=sol.v*o.canon
            row["q_"+label]=o.u@(pv[:,1]+2*om*y[:,0]);row["fase_"+label]=o.u@y[:,1]
        if case!="receptora" and (i+1)%2==0:
            j=(i+1)//2
            fid=[g.core-1,g.core,g.port-1,g.port]
            obs=np.array([probes["Re"+k][j]+1j*probes["Im"+k][j] for k in ref.PROBES])
            for tag,field in (("puente",X),("corregida",xc)):
                data=f+field[:,0]+1j*field[:,1]
                row["sonda_"+tag]=max(abs(phase*np.exp(1j*om*t)*data[fid]-obs))
        if (i+1)%8==0:
            for tag,value in (("puente",begin-inventory(X,V)),("corregida",begin-inventory(xc,vc))):
                for k,vv in zip(ref.NAMES,value):row[tag+"_"+k]=vv
            if case!="receptora":
                for k in ref.NAMES:row["archivo_"+k]=series[k][0]-series[k][int(t)]
        rows.append(row)
    return rows


def main():
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        for src,name in ((ref.HERE/"tangente.c","step"),(HERE/"polinomio.c","forced")):
            subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",str(src),"-lm","-o",tmp+"/"+name+".so"],check=True)
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        ci,cd=ctypes.c_int,ctypes.c_double
        step=ctypes.CDLL(tmp+"/step.so").advance;step.argtypes=[ci,ci,cd,cd]+[ptr]*3
        march=ctypes.CDLL(tmp+"/forced.so").march;march.argtypes=[ci,ci,ci,cd,cd]+[ptr]*8
        step.restype=march.restype=None
        G=generator()
        for case in ("gota_a010","gemelo","receptora"):
            rows+=run_case(case,march,step,G)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with (HERE/"series.csv").open("w",newline="") as out:
        wr=csv.DictWriter(out,fieldnames=keys,lineterminator="\n");wr.writeheader();wr.writerows(rows)
    maxima={}
    for case in ("gota_a010","gemelo","receptora"):
        rr=[r for r in rows if r["caso"]==case]
        maxima[case]={k:max(abs(r[k]) for r in rr if k in r) for k in keys[2:]
                      if any(k in r for r in rr) and not any(k.startswith(a+"_") for a in ("puente","corregida","archivo"))}
        maxima[case]["integral_cota_cambio"]=h*sum(r["cota_cambio"] for r in rr)
    channels={}
    for k in ref.NAMES:
        diffs={}
        for tag in ("puente","corregida"):
            errors=[]
            for i in range(7,320,8):
                a,b=rows[i],rows[320+i]
                errors.append((a[tag+"_"+k]-b[tag+"_"+k])-(a["archivo_"+k]-b["archivo_"+k]))
            diffs[tag]=max(map(abs,errors))
        channels[k]=diffs
    info=dict(maximos=maxima,contraste_inventarios=channels,sha_csv=ref.sha(HERE/"series.csv"))
    (HERE/"resultado.json").write_text(json.dumps(info,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    main()
