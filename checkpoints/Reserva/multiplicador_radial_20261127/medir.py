"""Multiplicador radial de las dos referencias de control sobre la malla FV."""
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
from scipy.sparse import bmat,csc_matrix,diags
from scipy.sparse.linalg import LinearOperator,eigsh,splu

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"energia_fisica_corregida_20261127"))
import auditar as p
o,g,a=p.o,p.g,p.a
h,om=p.h,p.om
trace=np.array(json.loads((p.HERE/"traza.json").read_text())["coeficientes"])
ka,kz=np.split(o.kap,2)
order=np.column_stack((np.arange(g.n),np.arange(g.n)+g.n)).ravel()


class Block:
    def __init__(self,base,mode,beta,perm):
        self.H=base[perm,:][:,perm].tocsc()
        self.u=mode[perm]
        self.perm=perm
        self.beta=beta
        # El bloque con esquina nula impone u^T b=0 exactamente en la resolución.
        v=csc_matrix(self.u[:,None])
        corner=0. if beta==0 else -1/beta
        self.lu=splu(bmat([[self.H,v],[v.T,csc_matrix([[corner]])]],format="csc"))

    def bound(self,weights):
        w=weights[self.perm]
        def apply(x):
            return w*self.lu.solve(np.r_[w*x,0.])[:-1]
        op=LinearOperator(self.H.shape,matvec=apply)
        val,vec=eigsh(op,k=1,which="LA",tol=1e-9,v0=np.cos(np.arange(len(w))*.007))
        residual=np.linalg.norm(apply(vec[:,0])-val[0]*vec[:,0])/val[0]
        upper=1.001*np.sqrt(val[0])
        slack=1e-7*upper**2*o.gap
        mat=upper**2*self.H-diags(w**2+slack,format="csc")
        lu=splu(mat,permc_spec="NATURAL",diag_pivot_thresh=0.,options={"Equil":False})
        assert np.array_equal(lu.perm_r,np.arange(len(w))) and np.array_equal(lu.perm_c,lu.perm_r)
        piv=lu.U.diagonal()
        v=lu.solve(self.u)
        schur=-self.u@v-(1/(upper**2*self.beta) if self.beta else 0.)
        count=int(np.count_nonzero(piv<0))+int(schur<0)-1
        backward=np.linalg.norm(mat@v-self.u,np.inf)/(1+abs(mat).sum(axis=1).max()*np.linalg.norm(v,np.inf))
        assert count==0 and min(abs(piv))>1e-13 and abs(schur)>1e-12
        assert residual<1e-7 and backward<1e-10
        return dict(limite=upper,estimacion=np.sqrt(val[0]),margen_I=slack,
                    negativos=count,pivote_min=min(abs(piv)),schur=schur,
                    residuo_rel=residual,error_atras=float(backward))


def multipliers(A,P,U,Y,B,radius):
    U,Y,B=U+radius,Y+radius,B+radius
    L=p.jac(U,Y)
    amp=A.bound(np.tile(L,2));phase=P.bound(L)
    kmag=np.hypot(ka,kz)
    force=np.array([max(amp["limite"],phase["limite"]),np.linalg.norm(L*kmag),np.linalg.norm(L*o.u)])
    # Fase imaginaria: fila del jacobiano de deltaK*b en coordenadas canónicas.
    m=p.m
    dens=2*abs(p.f)*U+U**2
    k=2*m.quartic*dens+abs(m.trilinear+m.mixed*p.z)*Y+.5*m.mixed*Y**2
    ra=4*m.quartic*(abs(p.f)+U)*B
    rb=k+4*m.quartic*B**2
    rz=np.sqrt(2)*(abs(m.trilinear+m.mixed*p.z)+m.mixed*Y)*B
    charge=np.minimum(force,[np.linalg.norm(o.u*np.sqrt(ra**2+rb**2+rz**2))/np.sqrt(o.gap),
                   abs(o.u)@(ra*abs(ka)+rz*abs(kz)),(o.u**2)@rb])
    return amp,phase,force,charge


def propagate(start,rows,force,charge):
    y=start.copy()
    values=[]
    for r in rows:
        M=p.matrix(r["F"],r["Fq"],r["pos"],r["vel"],0)
        M[1,:3]+=charge
        M[0,:3]+=force+o.kc*charge
        y=expm(h*M)@y
        values.append(float(trace@y[:3]))
    return y,values


def screen(case,step,march,A,P,rows):
    X,V=a.loc.initial(case)
    T,N=a.Forced(8,3,22),a.Forced(8,9,22)
    yn=ya=np.array([0.,0.,0.,1.])
    ys=yn.copy()
    uniform_failure=adaptive_failure=step_failure=None
    blocks=[]
    for block in range(8):
        U,Y,B=np.zeros((3,g.n))
        for j in range(40):
            x,w=X.copy(),V.copy()
            step(g.n,50,.0025,om,a.loc.c,X,V)
            bridge=np.stack([x,x+h*w/3,X-h*V/3,X])
            bt,tx,tv=p.advance(T,march,a.sample(bridge,3,True))
            bn,nx,nv=p.advance(N,march,a.sample(bridge,9,False))
            bd=bt+bn
            uj=np.hypot(bridge[:,:,0],bridge[:,:,1]).max(axis=0)+np.hypot(bd[:,0],bd[:,1])
            yj=abs(bridge[:,:,2]).max(axis=0)+bd[:,2]
            bj=abs(bridge[:,:,1]).max(axis=0)+bd[:,1]
            r=rows[40*block+j]
            assert abs(max(p.jac(uj+o.tube,yj+o.tube))-r["L"])<2e-12
            U=np.maximum(U,uj);Y=np.maximum(Y,yj);B=np.maximum(B,bj)
        section=rows[40*block:40*(block+1)]
        amp,phase,F,Q=multipliers(A,P,U,Y,B,o.tube)
        yn,pts=propagate(yn,section,F,Q)
        if uniform_failure is None:
            uniform_failure=next((r["t"] for r,v in zip(section,pts) if v>o.tube),None)
        audit=dict(fin=section[-1]["t"],amplitud=amp,fase=phase,
                   coef_F=F.tolist(),coef_q=Q.tolist(),uniforme_extremo=pts[-1])
        if adaptive_failure is None:
            # Intentos de radio por potencias de diez dentro del mismo tubo.
            attempts=[]
            for radius in (1e-9,1e-8,1e-7,1e-6,1e-5,1e-4):
                if radius<trace@ya[:3]:continue
                aa,pp,ff,qq=(amp,phase,F,Q) if radius==o.tube else multipliers(A,P,U,Y,B,radius)
                candidate,points=propagate(ya,section,ff,qq)
                attempts.append(dict(radio=radius,extremo=points[-1],amplitud=aa,fase=pp,
                                     coef_F=ff.tolist(),coef_q=qq.tolist()))
                if points[-1]<=radius:
                    ya=candidate
                    break
            else:
                # Solo el prefijo que respeta el radio ensayado queda cubierto.
                adaptive_failure=next(r["t"] for r,v in zip(section,points) if v>o.tube)
            audit["pruebas"]=attempts
        if step_failure is None:
            tests={o.tube:(amp,phase,F,Q)}
            records=[]
            for row in section:
                for rad in (1e-9,1e-8,1e-7,1e-6,1e-5,1e-4):
                    if rad<trace@ys[:3]:
                        continue
                    if rad not in tests:
                        tests[rad]=multipliers(A,P,U,Y,B,rad)
                    aa,pp,ff,qq=tests[rad]
                    candidate,pts=propagate(ys,[row],ff,qq)
                    if pts[-1]<=rad:
                        ys=candidate
                        records.append([row["t"],rad,*ys[:3],pts[-1]])
                        break
                else:
                    step_failure=row["t"]
                    audit["comparacion_fallida"]=pts[-1]
                    break
            audit["pasos_aceptados"]=records
            audit["coeficientes_por_radio"]=[dict(radio=rad,amplitud=aa,fase=pp,
                coef_F=ff.tolist(),coef_q=qq.tolist()) for rad,(aa,pp,ff,qq) in tests.items()]
        blocks.append(audit)
    return dict(bloques=blocks,primer_exceso_uniforme=uniform_failure,
                primer_exceso_adaptativo=adaptive_failure,primer_exceso_por_paso=step_failure,ultimo_estado_aceptado=ya[:3].tolist())


def main():
    with gzip.open(p.HERE/"bandas.csv.gz","rb") as stream:
        import hashlib
        assert hashlib.sha256(stream.read()).hexdigest()==json.loads((p.HERE/"resultado.json").read_text())["sha256"]
    with gzip.open(p.HERE/"bandas.csv.gz","rt") as stream:
        table=list(csv.DictReader(stream))
    A=Block(o.A,o.v,4*om**2,order)
    P=Block(o.P,o.u,0,np.arange(g.n))
    cases={}
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
            rows=[{k:float(v) for k,v in r.items() if k!="caso"} for r in table if r["caso"]==case]
            cases[case]=screen(case,step,march,A,P,rows)
    outer=json.loads((a.loc.HERE/"resultado.json").read_text())["energia_exterior"]
    loaded=json.loads((p.HERE/"resultado.json").read_text())["casos"]["gota_a010"]["integrales"]
    factor=outer["factor_160_a_60_T40"]
    data=dict(controles=cases,cargada=dict(factor=factor,cola_original=factor*loaded["banda2"],
              cola_ajustada=factor*loaded["ajustada2"],fuente_60_160=loaded["ajustada1"],
              fuente_r_menor_60=loaded["ajustada0"],coef_entrada=outer["coef_traza_interior"]))
    (HERE/"resultado.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")

if __name__=="__main__":
    main()
