"""Cajas físicas del núcleo y dos rutas de la respuesta de fuentes antiguas."""
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"nucleo_carga_fija_20261127"))
import continuar as cont
from nucleos import kernels

d,core=cont.d,cont.core
o=d.o


class Components(cont.Core):
    def __init__(self,compare):
        super().__init__()
        self.compare=compare
        self.comparison=None
        self.diag,self.res=core.evaluation(components=True)
        assert np.all(self.diag<=self.coef[:,None]*(1+1e-8))
        ix=d.bands[0]
        ka,kz=np.split(o.kap,2)
        self.kr=np.column_stack([abs(ka[ix]),0*ka[ix],abs(kz[ix])])/o.sw[ix,None]
        self.ur=np.column_stack([0*o.u[ix],abs(o.u[ix]),0*o.u[ix]])/o.sw[ix,None]

    def reference(self,centre,width):
        self.centre,self.width=centre,width

    def prepare(self,signed,rad,t,radius):
        self.active=not self.compare or (t==14 and np.all(radius==o.tube))
        self.signed,self.rad,self.radius=signed,rad,radius

    def transition_box(self,cell,D,Q,b):
        return cell

    def transition_force(self,previous,upper,cell,snorm,X):
        return previous

    def trial(self,x,e,J,qcoeff,row,F):
        original=super().trial(x,e,J,qcoeff,row,F)
        if not self.active:return original
        result=original.copy()
        sl=d.bands[0]
        for _ in range(4):
            D,Q,b=(result[k] for k in ("D","Q","beta"))
            physical=(self.diag*D+self.kr*Q+self.ur*b)/np.array([np.sqrt(2),np.sqrt(2),1.])
            cell=np.repeat(self.radius,np.diff(d.indices))[:,None]*np.ones((1,3))
            cell[sl]=np.minimum(cell[sl],physical)
            cell=self.transition_box(cell,D,Q,b)
            _,rad=d.columnas.jac_box(self.centre,self.width+cell)
            upper=abs(d.blocks(self.signed))+d.blocks(np.minimum(rad,self.rad))
            snorm=np.sqrt(upper.sum(axis=2).max(axis=1)*upper.sum(axis=1).max(axis=1))
            # Intersect per-cell force and projected-force cones with band volume.
            # On the nucleus both the componentwise and band L2 constraints hold.
            bandJ=np.minimum(J,[max(snorm[b]) for b in d.bands])
            U=upper[sl]
            canonical=np.minimum(physical,cell[sl])*np.array([np.sqrt(2),np.sqrt(2),1.])*o.sw[sl,None]
            per_cell=np.einsum("nij,nj->ni",U,canonical)
            f0=min(np.linalg.norm(per_cell),bandJ[0]*x[0])
            q0=min(abs(o.u[sl])@per_cell[:,1],
                   np.linalg.norm(o.u[sl,None]*U[:,1,:])*x[0],qcoeff[0]*x[0])
            tail=(self.bandmax*bandJ*x)[1:]
            tail[0]=self.transition_force(tail[0],upper,cell,snorm,x[1])
            nl=np.linalg.norm(np.r_[f0,tail])
            charge_source=q0+qcoeff[1:]@x[1:]
            dq=self.pw@x+self.cw@x+row["Fq"]+charge_source+row["vel"]+2*o.om*row["pos"]
            Q=min(self.Q+d.h*dq,self.uw@(e+2*o.om*x))
            DD=F+nl+original["cara"]+row["vel"]+d.p.op*row["pos"]+o.kc*dq+o.eps*(self.uw@x)
            D=self.D+d.h*DD
            b=min(self.uw@x,self.beta+d.h*(2*o.om/np.sqrt(o.gap)*D+abs(o.gamma)*Q+row["pos"]))
            point=max(self.coef*D+self.kap*Q+self.phase*b)
            assert point<=result["punto"]+1e-15
            result=dict(original,D=D,Q=Q,beta=b,punto=point,dq=dq,trabajo_carga=o.kc*dq,
                        no_lineal=nl,caja_mediana=np.median(cell[sl],axis=0).tolist(),
                        fila_imaginaria_nucleo=q0,fuerza_nucleo=f0)
        if self.compare:
            self.comparison=dict(entrada=[self.D,self.Q,self.beta],previo=original,nuevo=result)
            return original
        return result


def response(adj,fine,table,forces,archive=None):
    h=d.h
    count=len(forces)
    physical=np.zeros((320,5))
    physical[:count]=forces
    grouped=np.column_stack([np.linalg.norm(physical[:,:3],axis=1),physical[:,3:]])
    prescribed=np.array([[r[k] for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for r in table])
    linear=[];extra=[];bands=[]
    for j in range(320):
        n=j+1
        z=h*np.einsum("lij,li->j",adj[:n],prescribed[j::-1])
        z[1]+=table[j]["pos"]/o.sw[d.loc.i40-1]
        a=adj[:n,:3]*grouped[j::-1,:,None];b=fine[:n]*physical[j::-1,:,None]
        pn=h*(np.minimum(b[:,:3].sum(axis=1),a[:,0])+np.minimum(b[:,3],a[:,1])+np.minimum(b[:,4],a[:,2])).sum(axis=0)
        if archive and j<count:
            assert np.allclose(z+pn,archive[j]["nuevo"],rtol=1e-12,atol=1e-25)
        linear.append(z);extra.append(pn);bands.append(h*b.sum(axis=0))
    linear,extra,bands=map(np.array,(linear,extra,bands))
    weight=np.exp(.051*(40-np.arange(320)*h))
    summaries={}
    for tag,wt in (("simple",np.ones(320)),("ponderada",weight)):
        def integral(series,sl):
            return h*wt[sl]@series[sl]
        pre=slice(0,count);tail=slice(count,None)
        summaries[tag]=dict(lineal_total=integral(linear[:,1],slice(None)),
            nl_prefijo=integral(extra[:,1],pre),nl_cola=integral(extra[:,1],tail),
            total_fuentes_conocidas=integral(linear[:,1]+extra[:,1],slice(None)),
            cola_por_banda_antes_del_minimo=integral(bands[:,:,1],tail).tolist())
    l=json.loads((HERE.parent/"interfaz_cargada_20261127/resultado.json").read_text())["interfaz"]["levantamiento_energia"]
    return dict(prefijo=h*count,integrales=summaries,
                terminal=dict(z_lineal=linear[-1,0],z_fuentes_antiguas=extra[-1,0],
                              restitucion_lineal=l*linear[-1,0],restitucion_antiguas=l*extra[-1,0]),
                filas=np.column_stack([np.arange(1,321)*h,linear,extra]).tolist())


def study(step,march,table):
    adj,fine=kernels(d.indices)
    old=json.loads((HERE.parent/"traza_cinco_bandas_20261127/resultado.json").read_text())
    sources=[r["fuerza"] for r in old["filas"] if r["aceptado"]]
    past=response(adj,fine,table,sources,old["filas"])
    assert abs(past["integrales"]["simple"]["lineal_total"]-1.890728261884745e-6)<1e-16
    screen=Components(True)
    baseline=cont.solve(step,march,table,adj=adj,core_model=screen,box_observer=screen.reference)
    assert baseline==json.loads((cont.HERE/"continuacion.json").read_text())
    comparison=screen.comparison
    out=dict(antiguas=past,prueba_14=comparison,residuo_inversas=screen.res)
    if comparison["nuevo"]["punto"]<comparison["previo"]["punto"]:
        model=Components(False)
        forces=[]
        continuation=cont.solve(step,march,table,adj=adj,observe=forces.append,
                                core_model=model,box_observer=model.reference)
        good=[force for force,r in zip(forces,continuation["filas"]) if r["aceptado"]]
        out.update(continuacion=continuation,traza_nueva=response(adj,fine,table,good))
    return out


if __name__=="__main__":
    cont.main(study,HERE/"resultado.json")
