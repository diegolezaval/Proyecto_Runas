"""Acumulación radial de mayorantes sobre puentes cúbicos de la tangente."""
import csv
import ctypes
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tempfile

import numpy as np

HERE=Path(__file__).resolve().parent
base=HERE.parent/"error_forzado_contacto_20261127"
spec=importlib.util.spec_from_file_location("forzado",base/"medir.py")
old=importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
ref,g,f,z,c,m,om=old.ref,old.g,old.f,old.z,old.c,old.m,old.om
regions=[(0,40),(40,60),(60,160),(160,256),(0,256)]
W=old.W
cuts=[round(r/g.dx) for r in (40,60,160)]
i40=cuts[0]
edge=(np.arange(g.n)+1)*g.dx
length=np.full(g.n,g.dx)
length[-1]=g.dx/2
face=edge**2/length
coef=g.r**4/face
trace_c=max(2*(coef[i40:]+np.r_[0.,coef[i40:-1]])/g.w[i40:])
quadrature=np.polynomial.legendre.leggauss(4)


# Energía exterior de la ecuación rotante homogénea, con traza interior separada.
eta=.1
weights=np.exp(-2*eta*np.maximum(g.r-60,0))
edges=face[i40:-1]*np.diff(weights[i40:])**2/(weights[i40:-1]+weights[i40+1:])
growth=np.sqrt(np.max((np.r_[edges,0]+np.r_[0,edges])/(g.w[i40:]*weights[i40:])))
mat=np.zeros((g.n-i40,2,2))
mat[:,0,0]=-c[i40:,2]
mat[:,1,1]=-c[i40:,4]
mat[:,0,1]=mat[:,1,0]=-np.sqrt(2)*c[i40:,5]
potential_min=min(np.linalg.eigvalsh(mat)[:,0].min(),-c[i40:,3].max())
assert potential_min>0


def trace(a):
    tail=a[i40:]
    grad=np.diff(tail,append=0.)
    vol=g.w[i40:]@(abs(tail)**2)
    stiffness=face[i40:]@(abs(grad)**2)
    lim=(trace_c*vol*stiffness)**.25/g.r[i40]
    ratio=max(g.r[i40:]*abs(tail))/g.r[i40]/max(lim,1e-300)
    assert ratio<=1+1e-11
    return lim,ratio


def initial(case):
    if case=="receptora":
        path=ref.RES/"paso2_20261117/datos/preparacion.npz"
        digest=ref.read(path.parents[1]/"MANIFIESTO.json")["archivos"]["datos/preparacion.npz"]["sha256"]
    else:
        path=ref.P3/"datos/dt0005"/case/"tau300.npz"
        digest=ref.read(ref.P3/"MANIFIESTO_RETENCION.json")[str(path.relative_to(ref.P3))]["sha256"]
    assert ref.sha(path)==digest
    with np.load(path) as source:
        assert source["dx"]==g.dx
        q,p=source["q"],source["v"]
    phase=np.exp(1j*np.angle(q[0,0]+1j*q[1,0]))
    field=(q[0]+1j*q[1])/phase
    speed=(p[0]+1j*p[1])/phase-1j*om*field
    return np.column_stack((field.real-f,field.imag,q[2]-z)),np.column_stack((speed.real,speed.imag,p[2]))


def flux(b,d):
    # Solo las seis celdas adyacentes a las caras. Integración exacta de grado ≤6.
    ix=np.array(cuts)
    cells=np.stack((ix-1,ix),axis=1)
    b=b[:,cells,:].copy()
    b[:,:,:,0]+=f[cells]
    b[:,:,:,2]+=z[cells]
    d=d[:,cells,:]
    result=np.zeros((3,2))
    for node,weight in zip(*quadrature):
        t=(1+node)/2
        q=(1-t)**3*b[0]+3*t*(1-t)**2*b[1]+3*t*t*(1-t)*b[2]+t**3*b[3]
        vel=(1-t)**2*d[0]+2*t*(1-t)*d[1]+t*t*d[2]
        phi=q[:,:,0]+1j*q[:,:,1]
        vphi=vel[:,:,0]+1j*vel[:,:,1]+1j*om*phi
        diff=phi[:,1]-phi[:,0]
        result[:,0]-=weight/2*(2*(vphi.mean(axis=1).conj()*diff).real+vel[:,:,2].mean(axis=1)*(q[:,1,2]-q[:,0,2]))
        result[:,1]-=weight*(phi.mean(axis=1).conj()*diff).imag
    return result*(4*np.pi*edge[ix-1]**2/g.dx)[:,None]


def measure(step,case,T,nsteps):
    h=nsteps*.0025
    X,V=initial(case)
    total=np.zeros((len(regions),6))
    signed=np.zeros((3,2))
    forced=np.zeros((3,2))
    peak=np.zeros(3)
    midratio=0.
    for j in range(round(T/h)):
        x,p=X.copy(),V.copy()
        step(g.n,nsteps,.0025,om,c,X,V)
        b=np.array([x,x+h*p/3,X-h*V/3,X])
        d=3*np.diff(b,axis=0)/h
        e=2*np.diff(d,axis=0)/h
        dq=[d[0],(d[0]+2*d[1])/3,(2*d[1]+d[2])/3,d[2]]
        rr=np.array([(1-i/3)*e[0]+(i/3)*e[1]-old.affine(b[i],dq[i]) for i in range(4)])
        phi2=2*(rr[:,:,0]**2+rr[:,:,1]**2)
        chi2=rr[:,:,2]**2
        U=np.hypot(b[:,:,0],b[:,:,1]).max(axis=0)
        Y=abs(b[:,:,2]).max(axis=0)
        den=2*abs(f)*U+U*U
        k=2*m.quartic*den+abs(m.trilinear+m.mixed*z)*Y+.5*m.mixed*Y**2
        rp=abs(f)*(2*m.quartic*U**2+.5*m.mixed*Y**2)+k*U
        rz=abs(m.trilinear+m.mixed*z)*U**2+m.mixed*den*Y
        for i,(a,l) in enumerate(regions):
            s=slice(round(a/g.dx),round(l/g.dx))
            tp=phi2[:,s]@W[s]
            tc=chi2[:,s]@W[s]
            np2=2*W[s]@(rp[s]**2)
            nc2=W[s]@(rz[s]**2)
            if T==40 and a>=40:
                ww=W[s]*weights[s]
                force=[np.sqrt(max((phi2[:,s]+chi2[:,s])@ww)),
                       np.sqrt(ww@(2*rp[s]**2+rz[s]**2))]
                # Máximo del propagador en todo el intervalo, suma de Duhamel.
                forced[i-1]+=h*np.exp(growth*(T-j*h)/2)*np.array(force)
            total[i]+=h*np.sqrt([max(tp),max(tc),max(tp+tc),np2,nc2,np2+nc2])
        if j in (0,round(T/h)//2,round(T/h)-1):
            q=(b[0]+3*b[1]+3*b[2]+b[3])/8
            q[:,0]+=f
            q[:,2]+=z
            vel=(d[0]+2*d[1]+d[2])/4
            acc=g.acceleration(q.T).T
            acc[:,0]+=om**2*q[:,0]+2*om*vel[:,1]
            acc[:,1]+=om**2*q[:,1]-2*om*vel[:,0]
            defect=old.canon*(e.mean(axis=0)-acc)
            for a,l in regions:
                s=slice(round(a/g.dx),round(l/g.dx))
                bound=max(np.sqrt((phi2[:,s]+chi2[:,s])@W[s]))+np.sqrt(W[s]@(2*rp[s]**2+rz[s]**2))
                midratio=max(midratio,np.linalg.norm(defect[s])/max(bound,1e-300))
        if T==40:
            signed+=h*flux(b,d)
            for bi in b:
                field=f+bi[:,0]+1j*bi[:,1]
                lim,ratio=trace(field)
                peak=np.maximum(peak,[max(abs(field)),lim,ratio])
    assert midratio<1.00001
    return total,dict(caso=case,T=T,h=h,razon_control=midratio,
             **(dict(max_campo=peak[0],max_cola_traza=peak[1],razon_traza=peak[2],flujos_EQ=signed.tolist(),error_lineal_exterior_por_banda=forced.tolist()) if T==40 else {}))


def main():
    rows,controls=[],[]
    with tempfile.TemporaryDirectory() as tmp:
        lib=Path(tmp)/"paso.so"
        subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",str(ref.HERE/"tangente.c"),"-lm","-o",str(lib)],check=True)
        step=ctypes.CDLL(str(lib)).advance
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        step.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_double,ptr,ptr,ptr]
        step.restype=None
        for case in ("gota_a010","gemelo","receptora"):
            for T,n in ([(1,n) for n in (100,50,20,10,4,2,1)] if case!="receptora" else [])+[(40,50)]:
                arr,check=measure(step,case,T,n)
                controls.append(check)
                for (a,l),vals in zip(regions,arr):
                    rows.append(dict(caso=case,T=T,h=n*.0025,r0=a,r1=l,**dict(zip(
                        ["tiempo_phi","tiempo_chi","tiempo","Taylor_phi","Taylor_chi","Taylor"],vals))))
    prev=ref.read(base/"resultado.json")["casos"]
    for r in rows:
        if r["caso"]!="receptora" and r["T"]==40 and r["r0"]==0 and r["r1"]==256:
            p=next(s for s in prev if s["caso"]==r["caso"] and s["h"]==r["h"])
            for key,oldkey in [("tiempo","suma_defecto_temporal"),("Taylor","suma_Taylor")]:
                assert np.isclose(r[key],p[oldkey],rtol=1e-10,atol=1e-12)
    full={r["caso"]:r for r in controls if r["T"]==40}
    terms={}
    for case in ("gota_a010","gemelo"):
        D,R=full[case],full["receptora"]
        terms[case]={}
        for name,de,re in [("D_exterior",True,False),("R_exterior",False,True)]:
            key=lambda ex:"max_cola_traza" if ex else "max_campo"
            a,b=D[key(de)],R[key(re)]
            terms[case][name]=[m.mixed*a*a,m.mixed*b*b,2*m.mixed*a*b]
    # Norma infinita del generador de primer orden (x,p/Omega), diagonales incluidas.
    scale=200.
    lap=g.lo+g.hi
    L=max(scale,max((lap+abs(c[:,2]-lap)+abs(c[:,5]))/scale+2*om),
          max((lap+abs(c[:,3]-lap))/scale+2*om),max((lap+abs(c[:,4]-lap)+abs(c[:,6]))/scale))
    hops=round((160-60)/g.dx)
    def logtail(T):
        t=T*L
        if hops>t:
            return (hops*np.log(t)-math.lgamma(hops+1)-np.log1p(-t/(hops+1)))/np.log(10)
        return t/np.log(10)
    with (HERE/"bandas.csv").open("w",newline="") as out:
        wr=csv.DictWriter(out,fieldnames=rows[0],lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)
    data=dict(energia_exterior=dict(eta=eta,B=growth,min_potencial=potential_min,
        factor_160_a_60_T40=np.exp(growth*20-eta*100),
        coef_traza_interior=g.lo[i40]*np.sqrt(W[i40]*weights[i40])),controles=controls,coef_traza=trace_c,H_terminos_D_R_interferencia=terms,
        cola_generador=dict(escala=scale,L=L,saltos=hops,log10_cota_T1=logtail(1),log10_cota_T40=logtail(40)),sha256=ref.sha(HERE/"bandas.csv"))
    (HERE/"resultado.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    main()
