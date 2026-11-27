"""Cotas en el volumen para una referencia de Hermite; solo se integra la tangente."""
import ctypes
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from scipy.linalg import expm
from scipy.sparse import bmat, diags
from scipy.sparse.linalg import splu

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"referencia_radial_contacto_20261127"))
import medir as ref

om=ref.om
m=ref.m
g=ref.Grid(.025)
f,z,c,_=ref.operator(g)
W=4*np.pi*g.w
sw=np.sqrt(W)
canon=sw[:,None]*np.array([np.sqrt(2),np.sqrt(2),1.])
u=sw*f/np.linalg.norm(sw*f)
v=np.r_[u,np.zeros(g.n)]
off=-np.sqrt(g.lo[1:]*g.hi[:-1])
T=diags([off,g.A.diagonal(),off],[-1,0,1],format="csc")
P=T-diags(c[:,3])
B=diags(-np.sqrt(2)*c[:,5])
A=bmat([[T-diags(c[:,2]),B],[B,T-diags(c[:,4])]],format="csc")
w=splu(A).solve(v)
kap=2*om*w/(1+4*om**2*(v@w))
def C(x):
    return A@x+4*om**2*v*(v@x)
kn=np.linalg.norm(kap)
kc=np.sqrt(kap@C(kap))
gamma=1-2*om*(v@kap)
eps=np.linalg.norm(P@u)
gap=.17
tube=1e-4


def affine(x,p):
    a,b,y=x.T
    return -g.A@x+np.column_stack((c[:,2]*a+c[:,5]*y+c[:,7]+2*om*p[:,1],
        c[:,3]*b-2*om*p[:,0],c[:,4]*y+c[:,6]*a+c[:,8]))


def interval(x,p,X,V,h):
    # Coeficientes de Bernstein de posición, velocidad y aceleración.
    b=np.stack([x,x+h*p/3,X-h*V/3,X])
    d=3*np.diff(b,axis=0)/h
    e=2*np.diff(d,axis=0)/h
    ds=[d[0],(d[0]+2*d[1])/3,(2*d[1]+d[2])/3,d[2]]
    resid=np.array([(1-i/3)*e[0]+(i/3)*e[1]-affine(b[i],ds[i]) for i in range(4)])
    U=np.hypot(b[:,:,0],b[:,:,1]).max(axis=0)
    Y=abs(b[:,:,2]).max(axis=0)
    density=2*abs(f)*U+U**2
    k=2*m.quartic*density+abs(m.trilinear+m.mixed*z)*Y+.5*m.mixed*Y**2
    rp=abs(f)*(2*m.quartic*U**2+.5*m.mixed*Y**2)+k*U
    rz=abs(m.trilinear+m.mixed*z)*U**2+m.mixed*density*Y
    taylor=np.sqrt(W@(2*rp**2+rz**2))
    time=max(np.linalg.norm(canon*r) for r in resid)
    charge=max(abs(u@(canon[:,1]*r[:,1])) for r in resid)+abs(u)@(canon[:,1]*k*U)
    # Comprobación independiente de la aceleración completa en el centro.
    mid=(b[0]+3*b[1]+3*b[2]+b[3])/8
    vel=(d[0]+2*d[1]+d[2])/4
    lab=mid.copy()
    lab[:,0]+=f
    lab[:,2]+=z
    acc=g.acceleration(lab.T).T
    acc[:,0]+=om**2*lab[:,0]+2*om*vel[:,1]
    acc[:,1]+=om**2*lab[:,1]-2*om*vel[:,0]
    defect=canon*(e.mean(axis=0)-acc)
    ratio=np.linalg.norm(defect)/(time+taylor)
    assert ratio<=1.000001 and abs(u@defect[:,1])<=charge+1e-10
    # Norma del jacobiano del resto sobre el tubo: bloques simétricos canónicos.
    U+=tube
    Y+=tube
    den=2*abs(f)*U+U**2
    cross=np.sqrt(2)*((abs(m.trilinear+m.mixed*z)+m.mixed*Y)*U+m.mixed*Y*abs(f))
    lip=max(np.maximum(6*m.quartic*den+abs(m.trilinear+m.mixed*z)*Y+.5*m.mixed*Y**2,
                       m.mixed*den)+cross)
    full=max(np.linalg.norm(canon*(bi+np.column_stack((f,np.zeros_like(z),z)))) for bi in b)
    return time,taylor,charge,ratio,lip,full


def run_case(step,case,h):
    path=ref.P3/"datos/dt0005"/case/"tau300.npz"
    assert ref.sha(path)==ref.read(ref.P3/"MANIFIESTO_RETENCION.json")[str(path.relative_to(ref.P3))]["sha256"]
    with np.load(path) as src:
        fields,speed=src["q"],src["v"]
    energy=g.measure(np.pad(fields,((0,0),(1,1))),np.pad(speed,((0,0),(1,1))),f)[0]
    phase=np.exp(1j*np.angle(fields[0,0]+1j*fields[1,0]))
    F=(fields[0]+1j*fields[1])/phase
    vel=(speed[0]+1j*speed[1])/phase-1j*om*F
    X=np.column_stack((F.real-f,F.imag,fields[2]-z))
    V=np.column_stack((vel.real,vel.imag,speed[2]))
    # Desplazamiento canónico ≤ sqrt(2/gap) D + ||κ|| |q| + |fase|.
    coeff=np.array([np.sqrt(2/gap),kn,1.])
    budget=np.zeros(3)
    frozen=np.zeros(3)
    failed=None
    rows=[]
    for i in range(round(40/h)):
        x,p=X.copy(),V.copy()
        step(g.n,round(h/.0025),.0025,om,c,X,V)
        ft,fn,fq,ratio,lip,full=interval(x,p,X,V,h)
        rows.append(dict(caso=case,h=h,s=i*h,tiempo=ft,Taylor=fn,carga=fq,
                         razon_centro=ratio,L_tubo=lip,norma_referencia=full))
        linear=np.zeros((4,4))
        linear[1]=[eps/np.sqrt(gap),0,eps,fq]
        linear[0]=kc*linear[1]
        linear[0,2]+=eps
        linear[0,3]+=ft+fn
        linear[2]=[2*om/np.sqrt(gap),abs(gamma),0,0]
        frozen=(expm(h*linear)@np.r_[frozen,1.])[:3]
        if failed is None:
            # Comparación positiva para (D, |q|, |b0|, 1).
            M=np.zeros((4,4))
            M[1,:3]=eps*np.array([1/np.sqrt(gap),0,1])+lip*coeff
            M[1,3]=fq
            M[0]=kc*M[1]
            M[0,:3]+=lip*coeff
            M[0,2]+=eps
            M[0,3]+=ft+fn
            M[2,:3]=[2*om/np.sqrt(gap),abs(gamma),0]
            budget=(expm(h*M)@np.r_[budget,1.])[:3]
            if coeff@budget/sw.min()>tube:
                failed=(i+1)*h
    # Independiente de la aproximación lineal, energía semidiscreta conservada.
    mu2=m.coexistence()["omega_squared"]
    phi=np.sqrt(energy/mu2)
    chi=np.sqrt(2*energy)/m.mediator+abs(m.trilinear)*phi/(2*m.mediator*np.sqrt(m.mixed))
    return rows,dict(caso=case,h=h,E0=energy,mu2=mu2,primer_extremo_sin_tubo=failed,
        cota_lineal_D_q_fase=frozen.tolist(),cota_lineal_extremo=coeff@frozen,
        suma_defecto_temporal=h*sum(r["tiempo"] for r in rows),
        suma_Taylor=h*sum(r["Taylor"] for r in rows),suma_proyeccion_carga=h*sum(r["carga"] for r in rows),
        razon_max_centro=max(r["razon_centro"] for r in rows),
        cota_L2_error_global=np.hypot(np.sqrt(2)*phi,chi)+max(r["norma_referencia"] for r in rows))


if __name__=="__main__":
    rows,summary=[],[]
    with tempfile.TemporaryDirectory() as tmp:
        lib=Path(tmp)/"step.so"
        subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",
                        str(ref.HERE/"tangente.c"),"-lm","-o",str(lib)],check=True)
        step=ctypes.CDLL(str(lib)).advance
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        step.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_double,ptr,ptr,ptr]
        step.restype=None
        for case in ("gota_a010","gemelo"):
            for h in (.25,.125):
                blocks,stats=run_case(step,case,h)
                rows.extend(blocks)
                summary.append(stats)
    with (HERE/"envolventes.csv").open("w",newline="") as out:
        writer=csv.DictWriter(out,fieldnames=rows[0],lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    results=dict(kappa_L2=kn,kappa_C=kc,gamma=gamma,residuo_identidad=np.linalg.norm(C(kap)-2*om*v),
                 defecto_fase=eps,casos=summary,sha256_csv=ref.sha(HERE/"envolventes.csv"))
    (HERE/"resultado.json").write_text(json.dumps(results,indent=2,allow_nan=False)+"\n")
