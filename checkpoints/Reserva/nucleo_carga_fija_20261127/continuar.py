"""Continuación conjunta del exterior firmado y el núcleo reducido."""
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

import nucleo as core

HERE=core.HERE
sys.path.insert(0,str(HERE.parent/"desplazamiento_local_20261127"))
import desplazar as d


class Core:
    def __init__(self):
        self.coef,_=core.evaluation()
        sl=d.bands[0]
        ka,ky=np.split(d.o.kap,2)
        self.kap=np.hypot(ka[sl],ky[sl])/d.o.sw[sl]
        self.phase=abs(d.o.u[sl])/d.o.sw[sl]
        self.s,self.c=core.cutoff()
        self.bandmax=np.array([max(core.w[b]) for b in d.bands])
        self.uw=core.norms(core.u*core.w)
        self.pw=core.norms((d.o.P@core.u)*core.w)
        self.cw=core.norms(core.comm.T@core.u)
        self.D=self.Q=self.beta=0.

    def face_bound(self,x,e):
        return self.s*e[1]+self.c*x[1]

    def trial(self,x,e,J,qcoeff,row,F):
        h=d.h
        qdot=self.pw@x+self.cw@x+row["Fq"]+qcoeff@x+row["vel"]+2*d.o.om*row["pos"]
        Q=min(self.Q+h*qdot,self.uw@(e+2*d.o.om*x))
        beta_cap=self.uw@x
        nl=np.linalg.norm(self.bandmax*J*x)
        face=self.face_bound(x,e)
        charge=d.o.kc*qdot
        deriv=F+nl+face+row["vel"]+d.p.op*row["pos"]+charge+d.o.eps*beta_cap
        D=self.D+h*deriv
        beta=min(beta_cap,self.beta+h*(2*d.o.om/np.sqrt(d.o.gap)*D+abs(d.o.gamma)*Q+row["pos"]))
        point=max(self.coef*D+self.kap*Q+self.phase*beta)
        return dict(D=D,Q=Q,beta=beta,punto=point,cara=face,trabajo_carga=charge,
                    no_lineal=nl,prescrita=F,dq=qdot,cinematica=row["pos"],velocidad=row["vel"])


def solve(step,march,table,adj=None,observe=None,core_model=None,box_observer=None,radii_policy=None,limit=None):
    V,S,s,rate=d.floor_operator()
    shapes,rates=d.geometry()
    ext=d.loc.i40
    if adj is None:
        adj=d.trace_kernels()
    base=np.array([[r[k] for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for r in table])
    linear=np.array([d.h*np.einsum("lij,li->j",adj[:j+1],base[j::-1]) for j in range(320)])
    linear[:,1]+=base[:,3]/d.o.sw[ext-1]
    control=d.h*np.exp(.051*(40-np.arange(320)*d.h))@linear[:,1]
    prior=json.loads((d.HERE/"resultado.json").read_text())
    assert abs(control-prior["control_lineal_40"])<1e-16
    state=d.Comparison("firmado",shapes,rates,s,rate)
    kernel=Core() if core_model is None else core_model
    ladder=np.array(d.columnas.dense)
    entry=np.zeros(5)
    log=[]
    prev=None
    for j,(best,J,row,signed,time,total,centre,width) in enumerate(d.sources(step,march,table[:limit])):
        if box_observer is not None:
            box_observer(centre,width)
        mat=d.blocks(signed)
        H=V[ext:]+mat[ext:]
        assert min(np.linalg.eigvalsh(H)[:,0])>state.floor
        jump=1.
        if prev is not None:
            C=np.linalg.inv(np.linalg.cholesky(prev))
            jump=np.sqrt(1+max(0,np.linalg.eigvalsh(C@(H-prev)@C.transpose(0,2,1))[:,-1].max()))
        prev=H
        op=max(abs(mat[ext:]).sum(axis=2).max(axis=1))
        idx=np.minimum(np.searchsorted(ladder,entry),len(ladder)-1)
        if radii_policy is not None:
            idx=radii_policy.start(j,ladder,idx,log)
        F=np.linalg.norm(core.w*best)
        while True:
            radius=ladder[idx]
            cells=np.repeat(radius,np.diff(d.indices))[:,None]
            _,rad=d.columnas.jac_box(centre,width+cells)
            # Jacobiano medio de la fuerza física sobre el segmento referencia-error.
            bound=abs(mat)+d.blocks(rad)
            physical=np.minimum(J,[max(bound[b].sum(axis=2).max(axis=1)) for b in d.bands])
            parallel=core.norms(abs(core.u*core.w)*np.linalg.norm(bound[:,1,:],axis=1))
            parallel=np.minimum(parallel,kernel.uw*physical)
            rem=physical.copy()
            rem[2:]=[max(d.blocks(rad)[b].sum(axis=2).max(axis=1)) for b in d.bands[2:]]
            candidate=copy.copy(state)
            candidate.extra=state.extra.copy()
            candidate.rows=state.rows.copy()
            candidate.advance(best,physical,row,adj,linear,rem,jump,op)
            current=candidate.rows[-1]
            if core_model is not None:
                kernel.prepare(signed,rad,row["t"],radius)
            cr=kernel.trial(np.array(current["volumen"]),np.array(current["energia"]),
                            physical,parallel,row,F)
            pt=np.array(current["punto"]);pt[0]=min(pt[0],cr["punto"])
            need=np.maximum(entry,pt)
            ok=np.all(need<=radius)
            done=ok or np.all(radius==d.tube)
            if radii_policy is not None:
                done,new_idx=radii_policy.test(j,ladder,idx,entry,pt,cr,e=current['energia'],x=current['volumen'])
            if done:
                if observe is not None:
                    observe(physical*np.array(current["volumen"]))
                log.append(dict(t=row["t"],aceptado=bool(ok),punto=pt.tolist(),radios=radius.tolist(),
                      previo_nucleo=current["punto"][0],nucleo=cr,fila=current["fila"],
                      dz=current["dz_total"],z=current["z_total"],q_completa=current["q"],
                      fase_completa=current["fase"],salto=jump))
                if ok:
                    state=candidate
                    kernel.D,kernel.Q,kernel.beta=cr["D"],cr["Q"],cr["beta"]
                    entry=pt
                break
            if radii_policy is not None:
                idx=new_idx
            elif max(need)>d.tube:
                idx[:]=len(ladder)-1
            else:
                idx=np.maximum(idx,np.searchsorted(ladder,need))
        if not ok:break
    good=[r for r in log if r["aceptado"]]
    return dict(control_lineal_40=control,prefijo=d.h*len(good),integral_dz=d.h*sum(r["dz"] for r in good),
                integral_dz_con_peso_a_40=d.h*sum(np.exp(.051*(40-r["t"]+d.h))*r["dz"] for r in good),filas=log)


def main(solver=solve,output=HERE/"continuacion.json"):
    with gzip.open(d.p.HERE/"bandas.csv.gz","rt") as stream:
        table=[{k:float(v) for k,v in r.items() if k!="caso"}
               for r in csv.DictReader(stream) if r["caso"]=="gota_a010"]
    assert len(table)==320
    with tempfile.TemporaryDirectory() as tmp:
        libs=[]
        for src in [d.a.ref.HERE/"tangente.c",d.a.HERE/"polinomio.c"]:
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
        data=solver(step,march,table)
    output.write_text(json.dumps(data,separators=(",",":"),allow_nan=False)+"\n")


if __name__=="__main__":
    main()
