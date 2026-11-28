"""Comparación causal de cinco bandas en coordenadas canónicas, sin evolución M2."""
import copy
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
sys.path.insert(0,str(HERE.parent/"realimentacion_cargada_20261127"))
sys.path.insert(0,str(HERE.parent/"columnas_contacto_20261127"))
import causal
import columnas
from nucleos import kernels as trace_kernels

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
        lo,hi=bridge.min(axis=0)-bd,bridge.max(axis=0)+bd
        centre=(lo+hi)/2
        width=(hi-lo)/2
        signed,time=columnas.jac_box(centre,width)
        _,combined=columnas.jac_box(centre,width+tube)
        yield best,np.array([max(J[s]) for s in bands]),row,signed,time,combined,centre,width


def blocks(six):
    xx,xb,xz,bb,bz,zz = six
    return np.array([[xx,xb,xz],[xb,bb,bz],[xz,bz,zz]]).transpose(2,0,1)


def floor_operator():
    V=np.zeros((g.n,3,3))
    V[:,range(3),range(3)]=-loc.c[:,2:5]
    V[:,0,2]=V[:,2,0]=-np.sqrt(2)*loc.c[:,5]
    lam,U=np.linalg.eigh(V)
    s=np.maximum.reduce([0*lam,.17-lam,-2*lam])
    shifted=(U*s[:,None,:])@U.transpose(0,2,1)
    assert np.min(np.linalg.eigvalsh(V+shifted))>.17-1e-11
    return V,shifted,s,np.max(s/np.sqrt(lam+s))/2


def geometry():
    r=g.r
    shapes=[];rates=[]
    for sl in bands:
        k=np.exp(-.5*np.maximum.reduce([r[sl.start]-r,r-r[sl.stop-1],0*r]))
        edge=loc.face[:-1]*np.diff(k)**2/(k[:-1]+k[1:])
        rates.append(.5*np.sqrt(max((np.r_[edge,0]+np.r_[0,edge])/(g.w*k))))
        shapes.append(np.sqrt(k))
    return np.array(shapes),np.array(rates)


class Comparison:
    def __init__(self,mode,shapes,rates,s,mu_local):
        self.mode=mode
        self.shapes=shapes
        self.mask=np.array([[max(w[sl]) for sl in bands] for w in shapes])
        self.shift=np.array([[max(w[sl]*s[sl].max(axis=1)) for sl in bands] for w in shapes])
        if mode in ("publicado","exponente"):
            self.shift*=0
        rate=rates+({"publicado":mu,"exponente":mu_local}.get(mode,0.))
        self.K,self.E=causal.gains(rate,np.arange(320)[:,None])
        self.floor=.590 if mode=="publicado" else .17-1e-10
        self.op=np.sqrt(p.op**2+1)
        self.vol=np.array([sum(o.W[sl])**-.5 for sl in bands])
        self.inv=np.array([1/min(o.sw[sl]) for sl in bands])
        self.res=np.array([np.sqrt(sum(1/(4*np.pi*loc.face[sl.start:sl.stop-1]))) for sl in bands])
        self.history=[];self.numeric=[];self.rows=[];self.extra=[]
        self.Q=0.;self.failed=False

    def advance(self,best,J,row,adj,linear,remainder,jump,op_extra,shift_cap=None,feedback_cap=None):
        j=len(self.rows)
        Fj=np.linalg.norm(self.shapes*best,axis=1)
        if self.mode=="firmado":
            self.history=[val*jump for val in self.history]
            self.numeric=[v*jump for v in self.numeric]
            op=np.sqrt(self.op**2+op_extra)
        else:
            op=self.op
            remainder=J
        self.numeric.append(op*row["pos"]+row["vel"])
        ne=np.sum(self.E[:j+1]*np.array(self.numeric[::-1])[:,None],axis=0)
        rhs=ne/np.sqrt(self.floor)+self.K[0]*Fj
        if j: rhs+=np.sum(self.K[1:j+1]*self.history[::-1],axis=0)
        # Nonnegative block comparison for the work of the added shift.
        M=self.K[0,:,None]*(self.shift+np.eye(5)*max(remainder))
        norm=max(M.sum(axis=1))
        assert norm<1
        inverse=np.linalg.solve(np.eye(5)-M,np.eye(5))
        assert inverse.min()>=-1e-15
        x=np.maximum(inverse,0)@rhs
        for _ in range(4):
            shifted=np.linalg.norm(self.shift*x,axis=1)
            if shift_cap is not None:
                shifted=np.minimum(shifted,shift_cap)
            fb=np.minimum(max(remainder)*x,np.linalg.norm(self.mask*(remainder*x),axis=1))
            if feedback_cap is not None:
                fb=np.minimum(fb,feedback_cap)
            if _<3: x=rhs+self.K[0]*(shifted+fb)
        self.history.append(Fj+fb+shifted)
        e=ne+np.sum(self.E[:j+1]*self.history[::-1],axis=0)
        pt=np.minimum(self.inv*x,self.vol*x+self.res*e)
        force=J*x
        self.extra.append([np.linalg.norm(force[:3]),force[3],force[4],0.,0.])
        addition=h*np.einsum("lij,li->j",adj[:j+1],self.extra[::-1])
        qdot=bounds(o.P@o.u)@x+row["Fq"]+bounds(o.u)@force+row["vel"]+2*o.om*row["pos"]
        self.Q+=h*qdot
        self.failed=max(pt)>tube
        self.rows.append(dict(t=row["t"],aceptado=bool(not self.failed),punto=pt.tolist(),
             volumen=x.tolist(),energia=e.tolist(),cota_Sx=shifted.tolist(),
             trabajo_S_por_peso=(shifted*e).tolist(),fuerza_resto=fb.tolist(),fila=norm,
             q=min(self.Q,bounds(o.u)@(e+2*o.om*x)),fase=bounds(o.u)@x,qdot=qdot,
             z_total=linear[j,0]+addition[0],dz_total=linear[j,1]+addition[1]))


def study(step,march,table):
    adj=trace_kernels()
    base=np.array([[r[k] for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for r in table])
    linear=np.array([h*np.einsum("lij,li->j",adj[:j+1],base[j::-1]) for j in range(320)])
    linear[:,1]+=base[:,3]/o.sw[loc.i40-1]
    control=h*np.exp(.051*(40-np.arange(320)*h))@linear[:,1]
    prior=json.loads((causal.HERE/"resultado.json").read_text())["peso_conservado"]
    assert np.isclose(control,prior["lineal_40"][2],rtol=1e-12,atol=0)
    V,S,s,rate=floor_operator()
    shapes,rates=geometry()
    states=[Comparison(mode,shapes,rates,s,rate) for mode in ("publicado","exponente","local","firmado")]
    ext=loc.i40
    adaptive=Comparison("firmado",shapes,rates,s,rate)
    ladder=np.array(columnas.dense)
    signed_info=[]
    signed_old=None
    for j,(best,J,row,signed,time,total,centre,width) in enumerate(sources(step,march,table)):
        signed_mat=blocks(signed)[ext:]
        H=V[ext:]+signed_mat
        low=np.linalg.eigvalsh(H)[:,0]
        # Exterior potential floor for the comparison, throughout this frozen slab.
        jump=1.
        if signed_old is not None:
            C=np.linalg.inv(np.linalg.cholesky(signed_old))
            change=C@(H-signed_old)@C.transpose(0,2,1)
            jump=np.sqrt(1+max(0,np.linalg.eigvalsh(change)[:,-1].max()))
        signed_old=H
        rt=blocks(time).sum(axis=2).max(axis=1)
        rn=blocks(total-time).sum(axis=2).max(axis=1)
        assert min(rn)>=0
        temporal=np.array([max(rt[b]) for b in bands])
        nonlinear=np.array([max(rn[b]) for b in bands])
        rem=J.copy()
        rem[2:]=temporal[2:]+nonlinear[2:]
        op_extra=max(abs(signed_mat).sum(axis=2).max(axis=1))
        signed_info.append(dict(t=row["t"],piso=min(low),salto=jump,variacion=temporal.tolist(),
                                no_lineal=nonlinear.tolist(),J=J.tolist()))
        for st in states:
            if st.failed: continue
            if st.mode=="firmado" and min(low)<st.floor:
                st.failed=True
                continue
            st.advance(best,J,row,adj,linear,rem,jump,op_extra)
            if st.mode=="publicado":
                r=prior["filas"][j]
                assert np.allclose(r["punto"],st.rows[-1]["punto"],rtol=1e-11,atol=1e-18)
                assert r["aceptado"]==st.rows[-1]["aceptado"]
        if not adaptive.failed:
            entry=np.array(adaptive.rows[-1]["punto"] if adaptive.rows else [0.]*5)
            idx=np.minimum(np.searchsorted(ladder,entry),len(ladder)-1)
            idx[:2]=len(ladder)-1
            if min(low)<adaptive.floor:
                adaptive.failed=True
            while not adaptive.failed:
                radius=ladder[idx]
                cells=np.repeat(radius,np.diff(indices))[:,None]
                _,box=columnas.jac_box(centre,width+cells)
                bounded=blocks(box-time).sum(axis=2).max(axis=1)
                rem_local=J.copy()
                rem_local[2:]=temporal[2:]+np.array([max(bounded[b]) for b in bands[2:]])
                candidate=copy.copy(adaptive)
                candidate.extra=adaptive.extra.copy()
                candidate.rows=adaptive.rows.copy()
                candidate.advance(best,J,row,adj,linear,rem_local,jump,op_extra)
                last=candidate.rows[-1]
                last["radios"]=radius.tolist()
                last["resto_coef"]=rem_local.tolist()
                need=np.maximum(entry,last["punto"])
                if np.all(need<=radius) or np.all(radius==tube):
                    adaptive=candidate
                    break
                if max(need)>tube:
                    idx[:]=len(ladder)-1
                else:
                    idx=np.maximum(idx,np.searchsorted(ladder,need))
        if all(st.failed for st in states) and adaptive.failed: break
    results={}
    adaptive.mode="firmado_radios"
    for st in [*states,adaptive]:
        accepted=[r for r in st.rows if r["aceptado"]]
        results[st.mode]=dict(prefijo=len(accepted)*h,filas=st.rows,
            integral_dz_prefijo=h*sum(r["dz_total"] for r in accepted))
    return dict(control_lineal_40=control,piso=.17,mu_local=rate,mu_previo=mu,
            radio_max_S=max(g.r[s.max(axis=1)>0]),celdas_S=int(sum(s.max(axis=1)>0)),
            max_S=max(s.max(axis=1)),tasas_cara=rates.tolist(),firmado=signed_info,comparaciones=results)


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
        data=study(step,march,table)
    (HERE/"resultado.json").write_text(json.dumps(data,separators=(",",":"),allow_nan=False)+"\n")


if __name__=="__main__":
    main()
