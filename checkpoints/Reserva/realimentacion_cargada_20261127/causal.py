"""Comparación causal de cinco bandas en coordenadas canónicas, sin evolución M2."""
import csv
import ctypes
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/"energia_fisica_corregida_20261127"))
import auditar as p

a, o, g, h = p.a, p.o, p.g, p.h
loc = a.loc
mu = 1/(2*np.sqrt(.590))
tube = o.tube
indices = np.searchsorted(g.r, [0,10,40,60,160,256])
bands = [slice(i,j) for i,j in zip(indices[:-1],indices[1:])]
bounds = lambda field: np.array([np.linalg.norm(field[s]) for s in bands])


def sources(step,march,table):
    """Mismo puente y dos correcciones que auditar.measure, restringidos a la cargada."""
    X,V = loc.initial("gota_a010")
    T,N = a.Forced(8,3,22),a.Forced(8,9,22)
    for row in table:
        x,v = X.copy(),V.copy()
        step(g.n,50,.0025,o.om,loc.c,X,V)
        bridge = np.stack([x,x+h*v/3,X-h*V/3,X])
        bt,tx,tv = p.advance(T,march,a.sample(bridge,3,True))
        bn,nx,nv = p.advance(N,march,a.sample(bridge,9,False))
        bd = bt+bn
        f,z,m,jac = p.f,p.z,p.m,p.jac
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
        J = jac(U+d+tube,Y+dy+tube)
        assert np.allclose([np.linalg.norm(best[s]) for s in p.cuts],
            [row[f"ajustada{k}"] for k in range(3)],rtol=2e-11,atol=1e-20)
        assert np.allclose([tx+nx,tv+nv,J.max()], [row[k] for k in ("pos","vel","L")],
                           rtol=2e-11,atol=1e-28)
        yield best,np.array([max(J[s]) for s in bands]),row


def gains(rate,lag):
    # Integral over a full source slab, largest at observation slab's right end.
    e = np.exp(rate*lag*h)*np.expm1(rate*h)/rate
    return (e-h)/rate,e


def kernels():
    lags = np.arange(320)[:,None]
    base_x,base_e = gains(mu,lags)
    K = np.zeros((320,5,5))
    E = K.copy()
    for j,sl in enumerate(bands):
        distance = np.maximum.reduce([g.r[sl.start]-g.r, g.r-g.r[sl.stop-1], 0*g.r])
        k = np.exp(.5*distance)
        edge = loc.face[:-1]*np.diff(k)**2/(k[:-1]+k[1:])
        growth = np.sqrt(np.max((np.r_[edge,0]+np.r_[0,edge])/(g.w*k)))
        attenuation = np.array([1/np.sqrt(min(k[s])) for s in bands])
        x,e = gains(mu+growth/2,lags)
        K[:,:,j] = np.minimum(base_x,x*attenuation)
        E[:,:,j] = np.minimum(base_e,e*attenuation)
    return K,E


def causal(K,E,source,J,position,velocity):
    n = len(source)-1
    def convolution(kernel,values):
        return np.einsum("lij,lj->i",kernel[:len(values)],values[::-1])
    rhs = convolution(K,source)+position
    M = K[0]*J
    row_sum = np.max(M.sum(axis=1))
    assert row_sum < 1
    inverse = np.linalg.solve(np.eye(5)-M,np.eye(5))
    assert inverse.min()>=-1e-15
    x = np.maximum(0,inverse)@rhs
    assert max(abs(x-rhs-M@x)) < 1e-15*max(1,max(x))
    source[n] = source[n]+J*x
    energy = convolution(E,source)+velocity
    return x,energy,row_sum


def measure(step,march,table):
    K,E = kernels()
    pu = bounds(o.P@o.u)
    u = bounds(o.u)
    vol = np.array([sum(o.W[s])**-.5 for s in bands])
    resist = np.array([np.sqrt(sum(1/(4*np.pi*loc.face[s.start:s.stop-1]))) for s in bands])
    invmass = np.array([1/min(o.sw[s]) for s in bands])
    op = np.sqrt(p.op**2+1)
    # A displacement-source impulse has energy <= op*|r_x| globally.
    _,Ek = gains(mu,np.arange(320))
    num_e, prescribed, total, feedback, results = [],[],[],[],[]
    integral_z=integral_dz=lift_integral=charge=0.
    for j,(best,J,row) in enumerate(sources(step,march,table)):
        F=bounds(best)
        num_e.append(op*row["pos"]+row["vel"])
        en = Ek[:j+1]@num_e[::-1]
        total.append(F.copy())
        prescribed.append(F)
        x,e,row_sum = causal(K,E,total,J,en/np.sqrt(.590),en)
        point = np.minimum(invmass*x,vol*x+resist*e)
        feedback.append(J*x)
        fn = np.array(feedback[::-1])
        # Derivative of z from an acceleration perturbation has no direct r_x.
        zn = min(np.einsum("lj,lj->",K[:j+1,1],fn)/o.sw[loc.i40-1],
                 (np.einsum("lj,lj->",K[:j+1,1],fn)*vol[1]+
                  np.einsum("lj,lj->",E[:j+1,1],fn)*resist[1]))
        dz = np.einsum("lj,lj->",E[:j+1,1],fn)/o.sw[loc.i40-1]
        qdot = pu@x+row["Fq"]+u@feedback[-1]+row["vel"]+2*o.om*row["pos"]
        qtrial = charge+h*qdot
        linear_x = np.einsum("lij,lj->i",K[:j+1],prescribed[::-1])+en/np.sqrt(.590)
        linear_e = np.einsum("lij,lj->i",E[:j+1],prescribed[::-1])+en
        linear_point = np.minimum(invmass*linear_x,vol*linear_x+resist*linear_e)
        ok = max(point)<=tube
        results.append(dict(t=row["t"],aceptado=bool(ok),J=J.tolist(),fuente=F.tolist(),
            volumen=x.tolist(),energia=e.tolist(),punto=point.tolist(),punto_lineal=linear_point.tolist(),
            fila=row_sum,qdot=qdot,q=min(qtrial,u@(e+2*o.om*x)),fase=u@x,
            z_adicional=zn,dz_adicional=dz,pos=row["pos"],vel=row["vel"]))
        if not ok:
            break
        charge=qtrial
        integral_z+=h*zn
        integral_dz+=h*dz
        lift_integral+=h*np.exp(.051*(40-j*h))*dz
    prior=json.loads((HERE.parent/"adjunta_cargada_20261127/resultado.json").read_text())
    # Linear response is a fixed input of the superposition. Feed zero extra
    # acceleration through the same volume kernels and reconstruction.
    zeros=np.zeros_like(feedback)
    zero_response=np.einsum("lij,lj->i",E[:len(zeros)],zeros)
    control=prior["integral_dz_propagada"]+max(zero_response)
    assert control==prior["integral_dz_propagada"]
    return dict(mu=mu,ganancia_propia=gains(mu,0)[0],producto_0465=.465*gains(mu,0)[0],
        intervalos=results,control_lineal_interfaz=control,
        ultimo_aceptado=sum(r["aceptado"] for r in results)*h,
        integral_z_adicional_prefijo=integral_z,integral_dz_adicional_prefijo=integral_dz,
        integral_dz_adicional_prefijo_con_peso_a_40=lift_integral)


def fixed_weights(step,march,table,adj):
    r=g.r
    shapes=[]
    rates=[]
    for sl in bands:
        distance=np.maximum.reduce([r[sl.start]-r,r-r[sl.stop-1],0*r])
        k=np.exp(-.5*distance)
        edge=loc.face[:-1]*np.diff(k)**2/(k[1:]+k[:-1])
        B=np.sqrt(np.max((np.r_[edge,0]+np.r_[0,edge])/(g.w*k)))
        rates.append(mu+B/2)
        shapes.append(np.sqrt(k))
    rates=np.array(rates)
    shapes=np.array(shapes)
    K,E=gains(rates,np.arange(320)[:,None])
    masks=np.array([[max(weight[sl]) for sl in bands] for weight in shapes])
    vol=np.array([sum(o.W[sl])**-.5 for sl in bands])
    inv=np.array([1/min(o.sw[sl]) for sl in bands])
    resistance=np.array([np.sqrt(sum(1/(4*np.pi*loc.face[sl.start:sl.stop-1]))) for sl in bands])
    op=np.sqrt(p.op**2+1)
    base=np.array([[r[k] for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for r in table])
    def traces(forces):
        n=len(forces)
        return h*np.einsum("lij,li->j",adj[:n],np.asarray(forces)[::-1])
    # Reproduce the whole published zero-feedback run with the real kernels.
    linear=np.array([traces(base[:j+1]) for j in range(320)])
    linear[:,1]+=base[:,3]/o.sw[loc.i40-1]
    discount=np.exp(.051*(40-np.arange(320)*h))
    ref=json.loads((HERE.parent/"adjunta_cargada_20261127/resultado.json").read_text())
    control=[linear[-1,0],h*sum(linear[:,1]),h*(discount@linear[:,1])]
    assert np.allclose(control,[ref[k] for k in ("z_terminal","integral_dz","integral_dz_propagada")],rtol=1e-12,atol=0)
    past=[]
    numeric=[]
    extra=[]
    accepted=[]
    rows=[]
    Q=0.
    for j,(best,J,row) in enumerate(sources(step,march,table)):
        Fj=np.linalg.norm(shapes*best,axis=1)
        numeric.append(op*row["pos"]+row["vel"])
        ne=np.sum(E[:j+1]*np.array(numeric[::-1])[:,None],axis=0)
        rhs=ne/np.sqrt(.590)+K[0]*Fj
        if j:
            rhs+=np.sum(K[1:j+1]*past[::-1],axis=0)
        m=K[0]*max(J)
        assert max(m)<1
        x=rhs/(1-m)
        # Descending iteration from a proved supersolution. Every iterate remains
        # valid even if the minimum of the two feedback bounds has not converged.
        for _ in range(3):
            fb=np.minimum(max(J)*x,np.linalg.norm(masks*(J*x),axis=1))
            x=rhs+K[0]*fb
        fb=np.minimum(max(J)*x,np.linalg.norm(masks*(J*x),axis=1))
        past.append(Fj+fb)
        e=ne+np.sum(E[:j+1]*past[::-1],axis=0)
        pt=np.minimum(inv*x,vol*x+resistance*e)
        force=J*x
        extra.append([np.linalg.norm(force[:3]),force[3],force[4],0.,0.])
        addition=traces(extra)
        qdot=bounds(o.P@o.u)@x+row["Fq"]+bounds(o.u)@force+row["vel"]+2*o.om*row["pos"]
        Q+=h*qdot
        ok=max(pt)<=tube
        rows.append(dict(t=row["t"],aceptado=bool(ok),J=J.tolist(),fila=max(m),
                         punto=pt.tolist(),volumen=x.tolist(),energia=e.tolist(),
                         fuerza_prescrita_ponderada=Fj.tolist(),fuerza_extra=force.tolist(),
                         q=min(Q,bounds(o.u)@(e+2*o.om*x)),qdot=qdot,fase=bounds(o.u)@x,
                         z_extra=addition[0],dz_extra=addition[1],pos=row["pos"],vel=row["vel"]))
        if not ok: break
        accepted.append(addition)
    n=len(accepted)
    tot=linear[:n]+np.array(accepted)
    return dict(filas=rows,ultimo_aceptado=n*h,tasas=rates.tolist(),
                lineal_40=control,traza_prefijo=tot[-1].tolist(),integral_dz_prefijo=h*sum(tot[:,1]),
                integral_dz_extra_prefijo=h*sum(np.array(accepted)[:,1]),
                integral_dz_prefijo_con_peso_a_40=h*(discount[:n]@tot[:,1]))


def main():
    with gzip.open(p.HERE/"bandas.csv.gz","rt") as stream:
        table=[{k:float(v) for k,v in r.items() if k!="caso"}
               for r in csv.DictReader(stream) if r["caso"]=="gota_a010"]
    assert len(table)==320
    with tempfile.TemporaryDirectory() as tmp:
        libs=[]
        for src in [a.ref.HERE/"tangente.c",a.HERE/"polinomio.c"]:
            target=Path(tmp)/(src.stem+".so")
            subprocess.run(["cc","-O3","-std=c11","-ffp-contract=off","-shared","-fPIC",
                            str(src),"-lm","-o",str(target)],check=True)
            libs.append(ctypes.CDLL(str(target)))
        step,march=libs[0].advance,libs[1].march
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        ci,cd=ctypes.c_int,ctypes.c_double
        step.argtypes=[ci,ci,cd,cd]+[ptr]*3
        march.argtypes=[ci,ci,ci,cd,cd]+[ptr]*8
        step.restype=march.restype=None
        data=measure(step,march,table)
        from nucleos import kernels as trace_kernels
        data["peso_conservado"]=fixed_weights(step,march,table,trace_kernels())
    (HERE/"resultado.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    main()
