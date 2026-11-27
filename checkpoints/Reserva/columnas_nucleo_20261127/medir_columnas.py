"""Trabajo y carga de la jacobiana aplicada al error con corte escalar W."""
import json
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"nucleo_carga_fija_20261127"))
import continuar as cont

d=cont.d
o=d.o
core=cont.core


class Projected(cont.Core):
    def __init__(self,screen=False):
        super().__init__()
        self.screen=screen
        self.comparison=None
        V=d.floor_operator()[0]
        # Combine two lower bounds on the transverse energy: the FV gap and
        # a local potential bound retaining half the heavy-field mass term.
        mchi=min(V[:,2,2])/2
        V[:,2,2]-=mchi
        curvature=max(0,-np.linalg.eigvalsh(V)[:,0].min())
        theta=.5*o.gap/(curvature+o.gap)
        self.scales=[np.full(3,1/np.sqrt(o.gap)),
                     1/np.sqrt([.5*o.gap,.5*o.gap,.5*o.gap+theta*mchi])]

    def prepare(self,signed,rad,t,radii):
        self.active=(not self.screen) or (t==14 and np.all(radii==o.tube))
        if not self.active:return
        # J may be set to zero outside supp(W): JWe is unchanged pointwise.
        mask=core.w>0
        jc=signed*mask; jr=rad*mask
        cm=d.blocks(jc); box=abs(cm)+d.blocks(jr)
        row=cm[:,1,:]*o.u[:,None]
        row[:,1]-=(o.u@row[:,1])*o.u
        envelope=abs(row)+d.blocks(jr)[:,1,:]*abs(o.u[:,None])
        force=[];charge=[]
        for scale in self.scales:
            matrix=box*scale
            # Induced norm bounded by sqrt(||M||_1 ||M||_infty) per cell.
            force.append(np.sqrt(matrix.sum(axis=1).max(axis=1)*matrix.sum(axis=2).max(axis=1)).max())
            charge.append(np.linalg.norm(envelope*scale))
        k=d.columnas.column(jc,jr,False)
        u=d.columnas.column(jc,jr,True)
        self.direct=np.array([min(force),k[0],u[0]])
        self.parallel=np.array([min(charge),k[1],u[1]])
        self.raw=np.array([min(force),k[2],u[2]])

    def trial(self,x,e,J,qcoeff,row,F):
        prior=super().trial(x,e,J,qcoeff,row,F)
        if not self.active:return prior
        dq0=self.pw@x+self.cw@x+row["Fq"]+row["vel"]+2*o.om*row["pos"]
        qcap=self.uw@(e+2*o.om*x)
        bcap=self.uw@x
        state=np.array([prior[k] for k in ("D","Q","beta")])
        # Every pass starts from the same incoming physical state. Positive
        # comparisons from the previous upper bound remain valid for the slab.
        for _ in range(5):
            par=min(qcoeff@x,self.parallel@state)
            dq=dq0+par
            Q=min(self.Q+d.h*dq,qcap)
            work=min(prior["no_lineal"],self.direct@state)
            unprojected=min(prior["no_lineal"],self.raw@state)
            D=self.D+d.h*(F+work+prior["cara"]+row["vel"]+d.p.op*row["pos"]+
                          o.kc*dq+o.eps*bcap)
            beta=min(bcap,self.beta+d.h*(2*o.om/np.sqrt(o.gap)*D+abs(o.gamma)*Q+row["pos"]))
            new=np.array([D,Q,beta])
            assert np.all(new<=state+1e-15)
            state=new
        point=max(self.coef*D+self.kap*Q+self.phase*beta)
        result=dict(prior,D=D,Q=Q,beta=beta,punto=point,no_lineal=work,trabajo_carga=o.kc*dq,dq=dq,
                    fuente_paralela=par,trabajo_sin_proyectar=unprojected,
                    coef_trabajo=self.direct.tolist(),coef_paralelo=self.parallel.tolist(),
                    anterior=prior["punto"])
        if self.screen:
            self.comparison=dict(entrada=[self.D,self.Q,self.beta],previo=prior,proyectado=result)
            # Screening does not change acceptance or the archived incoming path.
            return prior
        return result


def verify_columns():
    rng=np.random.default_rng(291)
    centre=rng.normal(0,2e-5,(d.g.n,3))
    width=np.full_like(centre,2e-5)
    jc,jr=d.columnas.jac_box(centre,width)
    matrix=d.blocks(jc)
    field=rng.normal(size=centre.shape)
    left=np.einsum("nij,nj->ni",matrix,core.w[:,None]*field)
    right=core.w[:,None]*np.einsum("nij,nj->ni",matrix,field)
    err=np.max(abs(left-right))
    assert err<1e-12
    ratio=[]
    ka,kz=np.split(o.kap,2)
    for phase,direction in [(False,np.column_stack([ka,0*ka,kz])),(True,np.column_stack([0*o.u,o.u,0*o.u]))]:
        mid=(core.w>0)*jc
        rad=(core.w>0)*jr
        val=np.einsum("nij,nj->ni",d.blocks(mid),direction)
        raw=np.linalg.norm(val)
        parallel=o.u@val[:,1]
        val[:,1]-=parallel*o.u
        perp=np.linalg.norm(val)
        assert abs(raw**2-perp**2-parallel**2)<1e-13
        limit=d.columnas.column(mid,rad,phase)
        assert perp<=limit[0]+1e-15 and abs(parallel)<=limit[1]+1e-15
        ratio.append([perp,parallel,raw])
    return dict(error_conmutacion=err,columnas_manufacturadas=ratio)


def study(step,march,table):
    from nucleos import kernels
    adj,fine=kernels(d.indices)
    screen=Projected(screen=True)
    baseline=cont.solve(step,march,table,adj=adj,core_model=screen)
    assert baseline==json.loads((cont.HERE/"continuacion.json").read_text())
    comparison=screen.comparison
    assert comparison is not None
    report=dict(verificacion=verify_columns(),fila_14=comparison)
    if comparison["proyectado"]["punto"]>=comparison["previo"]["punto"]:return report
    forces=[]
    new=cont.solve(step,march,table,adj=adj,observe=forces.append,core_model=Projected())
    base=np.array([[r[k] for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for r in table])
    physical=np.array(forces)
    grouped=np.column_stack([np.linalg.norm(physical[:,:3],axis=1),physical[:,3:]])
    accepted=[]
    for j,r in enumerate(new["filas"]):
        n=j+1
        linear=d.h*np.einsum("lij,li->j",adj[:n],base[j::-1])
        linear[1]+=table[j]["pos"]/d.o.sw[d.loc.i40-1]
        coarse=adj[:n,:3]*grouped[j::-1,:,None]
        parts=fine[:n]*physical[j::-1,:,None]
        assert np.allclose(linear+d.h*coarse.sum(axis=(0,1)),[r["z"],r["dz"]],rtol=1e-12,atol=1e-22)
        sharp=d.h*(np.minimum(parts[:,:3].sum(axis=1),coarse[:,0])+
                   np.minimum(parts[:,3],coarse[:,1])+np.minimum(parts[:,4],coarse[:,2])).sum(axis=0)
        r["traza_cinco"]=(linear+sharp).tolist()
        if r["aceptado"]: accepted.append(r["traza_cinco"][1])
    report.update(continuacion=new,simple_cinco=d.h*sum(accepted),
                  propagada_cinco=d.h*np.exp(.051*(40-np.arange(len(accepted))*d.h))@accepted)
    return report


if __name__=="__main__":
    cont.main(study,HERE/"resultado.json")
