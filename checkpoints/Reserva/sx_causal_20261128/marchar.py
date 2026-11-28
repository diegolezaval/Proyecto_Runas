"""Comparación causal de Sx con cinco energías y el mismo estado entrante."""
from pathlib import Path
import sys
import json
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cribado_sx_20261127"))
import cribar as screen
h,q,d,o=screen.h,screen.q,screen.d,screen.o
archive=h.archive
last=len(archive)-1


class Refiner:
    def __init__(self,model):
        self.model=model
        _,S,ev,_=d.floor_operator()
        self.matrix=abs(S)
        self.shape=d.geometry()[0]
        self.gain=self.shape*ev.max(axis=1)
        assert not np.any(S[d.bands[2].start:])
        self.units=np.array([np.sqrt(2),np.sqrt(2),1.])

    def caps(self,j,radii,current,cr):
        if j<self.start:
            return None
        cols=[]
        m=self.model
        for k,(diag,kap,phase) in enumerate([(m.diag,m.kr,m.ur),(m.local,m.k1,m.u1)]):
            sl=d.bands[k]
            X=current["volumen"][k]
            w=q.core.w[sl,None]
            cut=diag*cr["D"]+kap*cr["Q"]+phase*cr["beta"]
            box=np.broadcast_to(radii[k]*self.units,cut.shape).copy()
            box=np.minimum(box,np.divide(screen.pad*cut,w,out=box.copy(),where=w>0))
            p=box*o.sw[sl,None]
            norm=np.linalg.norm(np.einsum("nij,nj->ni",self.matrix[sl],p),axis=1)
            costs=[]
            for shape,gain in zip(self.shape[:,sl],self.gain[:,sl]):
                value,_=q.wj.squared_dual(screen.pad*shape*norm,screen.pad*gain,screen.pad*X)
                costs.append(min(gain.max()*X,np.sqrt(value)*screen.pad))
            cols.append(costs)
        self.before=np.array(current["cota_Sx"])
        self.after=screen.pad*np.linalg.norm(cols,axis=0)
        self.initial_energy=current["energia"]
        return self.after

    def observe(self,state,best,remainder,jump,op,row,cr,accepted):
        if len(state.rows)-1<self.start:
            return
        current=state.rows[-1]
        assert np.all(np.array(current["energia"])<=np.array(self.initial_energy)*(1+1e-12)+1e-25)
        self.log.append(dict(t=row["t"],aceptado=bool(accepted),S_original=self.before.tolist(),
            techos=self.after.tolist(),S_usado=current["cota_Sx"],energia=current["energia"],
            prescrita=np.linalg.norm(state.shapes*best,axis=1).tolist(),
            realimentacion=current["fuerza_resto"],energia_sin_refinar=self.initial_energy))


class Policy(q.Policy):
    def start(self,j,ladder,idx,log):
        idx=super().start(j,ladder,idx,log)
        if self.fixed and j==last:
            return np.searchsorted(ladder,archive[-1]["radios"])
        return idx


def study(step,march,table):
    model=q.Project(q.wj.prior["metrica"]["gamma"])
    refine=Refiner(model)
    adj=q.base.prev.kernels()
    fixed=json.loads((screen.HERE/"resultado.json").read_text())["filas"][-1]
    result={}
    for mode,start,limit in [("control",320,last+1),("fijo",last,last+1),("causal",108,None)]:
        model.D=model.Q=model.beta=0.
        policy=Policy(model,"doce",108)
        policy.fixed=mode=="fijo"
        refine.start=start
        refine.log=[]
        out=q.base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
            radii_policy=policy,limit=limit,shift_refiner=refine.caps,budget_observer=refine.observe)
        rows=out["filas"]
        assert rows[:start]==archive[:start]
        if mode=="fijo":
            assert rows[-1]["radios"]==archive[-1]["radios"]
            assert np.isclose(refine.log[-1]["techos"][1],fixed["fuente_nueva"],rtol=5e-11,atol=1e-25)
        result[mode]=dict(prefijo=out["prefijo"],filas=rows[min(start,last):],presupuesto=refine.log)
        if mode=="fijo":
            old,new=archive[-1]["nucleo"],rows[-1]["nucleo"]
            if any(new[k]>=old[k]*(1-1e-6) for k in ("cara","punto")):
                break
    return result


if __name__=="__main__":
    q.base.cont.main(study,HERE/"resultado.json")
