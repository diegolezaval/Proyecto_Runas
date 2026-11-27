"""Energía en toda la malla para el error entre M2 y las referencias aisladas."""
import csv
import ctypes
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from scipy.linalg import expm
from scipy.sparse import block_diag,diags
from scipy.sparse.linalg import splu

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"defecto_localizado_20261127"))
import localizar as loc
o=loc.old
g,f,z,m,om=loc.g,loc.f,loc.z,loc.m,loc.om
s=np.sqrt(loc.weights)
# J=T-S T S^-1. Calcular solo entradas fuera de la diagonal para evitar cancelación.
J=diags([o.off*(-np.expm1(np.diff(np.log(s)))),
         o.off*(-np.expm1(-np.diff(np.log(s))))],[-1,1],format="csc")
JA=block_diag((J,J),format="csc")
gap=o.gap
gauss=np.polynomial.legendre.leggauss(5)


def upper(base,comm,mode,beta,order):
    """Inercia de b²(base+beta vvᵀ)−JᵀJ en el orden radial local."""
    gram=(comm.T@comm).tocsc()
    tests=[]
    for b in (.2,.25,.35,.5,.75,1.,1.5,2.,3.,4.,8.,16.,32.):
        mat=(b*b*base-gram)[order,:][:,order].tocsc()
        v=mode[order]
        lu=splu(mat,permc_spec="NATURAL",diag_pivot_thresh=0.,options={"Equil":False})
        assert np.array_equal(lu.perm_r,np.arange(len(v))) and np.array_equal(lu.perm_c,lu.perm_r)
        inverse=lu.solve(v)
        piv=lu.U.diagonal()
        den=-1/(b*b*beta)-v@inverse
        count=int(sum(piv<0))+int(den<0)-1
        tests.append([b,count])
        if count==0 and min(abs(piv))>1e-12 and abs(den)>1e-12:
            return b,dict(pruebas=tests,min_pivote=min(abs(piv)),schur=den,
                residuo_resolucion=np.linalg.norm(mat@inverse-v))
    raise ArithmeticError("No se logró la cota espectral")


def norms():
    order=np.column_stack((np.arange(g.n),g.n+np.arange(g.n))).ravel()
    ca,ta=upper(o.A,JA,o.v,4*om**2,order)
    cb,tb=upper(o.P,J,o.u,1.,np.arange(g.n))
    # Los dos modos casi nulos se conservan individualmente.
    return dict(amplitud=ta,fase=tb,coef_D=max(ca,cb),Jk=np.linalg.norm(JA@o.kap),
        Ju=np.linalg.norm(J@o.u),Jtu=np.linalg.norm(J.T@o.u),
        delta_u=np.linalg.norm(np.expm1(-np.log(s))*o.u),
        proyector=np.linalg.norm((s-(o.u@(s*o.u)))*o.u),
        rango_uno=4*om**2*np.linalg.norm((s-(o.u@(s*o.u)))*o.u),
        cara40=max(abs(J[loc.i40-1,loc.i40]),abs(J[loc.i40,loc.i40-1])))


def forces(x,p,X,V,h):
    b=np.stack([x,x+h*p/3,X-h*V/3,X])
    d=3*np.diff(b,axis=0)/h
    e=2*np.diff(d,axis=0)/h
    speeds=[d[0],(d[0]+2*d[1])/3,(2*d[1]+d[2])/3,d[2]]
    rr=[(1-i/3)*e[0]+i/3*e[1]-o.affine(b[i],speeds[i]) for i in range(4)]
    U=np.hypot(b[:,:,0],b[:,:,1]).max(axis=0)
    Y=abs(b[:,:,2]).max(axis=0)
    density=2*abs(f)*U+U*U
    K=2*m.quartic*density+abs(m.trilinear+m.mixed*z)*Y+.5*m.mixed*Y**2
    rp=abs(f)*(2*m.quartic*U**2+.5*m.mixed*Y**2)+K*U
    rz=abs(m.trilinear+m.mixed*z)*U**2+m.mixed*density*Y
    time=max(np.linalg.norm(s[:,None]*o.canon*r) for r in rr)
    tail=np.sqrt((o.W*s*s)@(2*rp*rp+rz*rz))
    us=o.u*s*o.canon[:,1]
    fq=max(abs(us@r[:,1]) for r in rr)+abs(us)@(K*U)
    U+=o.tube
    Y+=o.tube
    density=2*abs(f)*U+U*U
    cross=np.sqrt(2)*((abs(m.trilinear+m.mixed*z)+m.mixed*Y)*U+m.mixed*Y*abs(f))
    lip=max(np.maximum(6*m.quartic*density+abs(m.trilinear+m.mixed*z)*Y+.5*m.mixed*Y*Y,
                       m.mixed*density)+cross)
    # Integral exacta dividida por h (impulso por unidad de tiempo).
    average=np.mean(rr,axis=0)
    independent=(V-p)/h-o.affine(b.mean(axis=0),d.mean(axis=0))
    assert np.max(abs(average-independent))<5e-8
    signed=np.zeros_like(x)
    for node,weight in zip(*gauss):
        t=(node+1)/2
        mid=(1-t)**3*b[0]+3*t*(1-t)**2*b[1]+3*t*t*(1-t)*b[2]+t**3*b[3]
        a,im,y=mid.T
        u2=a*a+im*im
        den=2*f*a+u2
        k=2*m.quartic*den+(m.trilinear+m.mixed*z)*y+.5*m.mixed*y*y
        re=f*(2*m.quartic*u2+.5*m.mixed*y*y)+k*a
        chi=(m.trilinear+m.mixed*z)*u2+m.mixed*den*y
        signed+=.5*weight*np.column_stack((re,k*im,chi))
    st=np.linalg.norm(s[:,None]*o.canon*average)
    sn=np.linalg.norm(s[:,None]*o.canon*signed)
    assert st<=time+1e-13 and sn<=tail+1e-13
    return time,tail,fq,lip,st,sn


def comparison(n,ft,fn,fq,lip):
    displacement=np.array([np.sqrt(2/gap),o.kn,1.])
    M=np.zeros((4,4))
    # q' = u^T (J-P)b + u^T S F.
    M[1,:3]=(o.eps+n["Jtu"])*np.array([1/np.sqrt(gap),0,1])+lip*displacement
    M[1,3]=fq
    M[0]=o.kc*M[1]
    M[0,:3]+=np.array([n["coef_D"],n["Jk"],n["Ju"]+o.eps])+lip*displacement
    M[0,3]+=ft+fn
    M[2,:3]=[2*om/np.sqrt(gap),abs(o.gamma),0]
    return M


def trajectory(step,case,n):
    X,V=loc.initial(case)
    fine=.0025
    h=.125
    linear=np.array([0.,0.,0.,1.])
    nonlinear=linear.copy()
    first=None
    arr=[]
    for i in range(320):
        x,p=X.copy(),V.copy()
        step(g.n,50,fine,om,loc.c,X,V)
        ft,fn,fq,lip,st,sn=forces(x,p,X,V,h)
        M=comparison(n,ft,fn,fq,0)
        linear=expm(h*M)@linear
        if first is None:
            nonlinear=expm(h*comparison(n,ft,fn,fq,lip))@nonlinear
            unorm=np.sqrt(2/gap)*nonlinear[0]+o.kn*nonlinear[1]+nonlinear[2]
            point=unorm/min(s*o.sw)
            if point>o.tube:
                first=dict(t=(i+1)*h,puntual_global=point,
                           puntual_r60=unorm/min(o.sw[g.r<60]),L=lip)
        arr.append(dict(caso=case,t=(i+1)*h,temporal=ft,Taylor=fn,proyeccion_q=fq,impulso_temporal_h=st,impulso_Taylor_h=sn,
                        D=linear[0],carga=linear[1],fase=linear[2]))
    D,q,beta=linear[:3]
    shift=n["delta_u"]
    return arr,dict(caso=case,integral_temporal=h*sum(r["temporal"] for r in arr),
        impulsos_temporales=h*sum(r["impulso_temporal_h"] for r in arr),
        impulsos_Taylor=h*sum(r["impulso_Taylor_h"] for r in arr),
        integral_Taylor=h*sum(r["Taylor"] for r in arr),primer_fallo=first,
        D=D,q=q,fase=beta,cota_desplazamiento=np.sqrt(2/gap)*D+o.kn*q+beta,
        correccion_carga_fisica=shift*((1+4*om/np.sqrt(gap))*D+(abs(o.gamma)+2*om*o.kn)*q),
        correccion_fase_fisica=shift*(D/np.sqrt(gap)+beta))


def main():
    n=norms()
    rows,stats=[],[]
    with tempfile.TemporaryDirectory() as tmp:
        lib=Path(tmp)/"paso.so"
        subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",str(loc.ref.HERE/"tangente.c"),"-lm","-o",str(lib)],check=True)
        step=ctypes.CDLL(str(lib)).advance
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        step.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_double,ptr,ptr,ptr]
        step.restype=None
        for case in ("gota_a010","gemelo","receptora"):
            a,b=trajectory(step,case,n)
            rows.extend(a)
            stats.append(b)
    with (HERE/"envolventes.csv").open("w",newline="") as out:
        writer=csv.DictWriter(out,fieldnames=rows[0],lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (HERE/"resultado.json").write_text(json.dumps(dict(operador=n,casos=stats,
        sha_csv=loc.ref.sha(HERE/"envolventes.csv")),allow_nan=False,indent=2)+"\n")


if __name__=="__main__":
    main()
