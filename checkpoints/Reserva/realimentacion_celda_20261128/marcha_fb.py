"""Cotas de la realimentación para cada peso con el centro exterior absorbido."""
from pathlib import Path
import json
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"sx_causal_20261128"))
import marchar as sx
q,d,o=sx.q,sx.d,sx.o
archive=sx.archive[:108]+json.loads((sx.HERE/"resultado.json").read_text())["causal"]["filas"]
last=len(archive)-1
pad=sx.screen.pad


class Feedback:
    def __init__(self,model,shapes):
        self.m=model
        self.shapes=shapes
        self.units=np.array([np.sqrt(2),np.sqrt(2),1.])

    def caps(self,j,radii,current,cr):
        if j<self.start:
            return None
        m=self.m
        box=np.repeat(radii,np.diff(d.indices))[:,None]*np.ones((1,3))
        sl=d.bands[0]
        box[sl]=np.minimum(box[sl],pad*(m.diag*cr["D"]+m.kr*cr["Q"]+m.ur*cr["beta"])/self.units)
        box=m.transition_box(box,cr["D"]*pad,cr["Q"]*pad,cr["beta"]*pad)
        _,rad=d.columnas.jac_box(m.centre,m.width+box)
        U=d.blocks(np.minimum(rad,m.rad))
        assert U.min()>=0
        ext=d.loc.i40
        assert ext==d.bands[2].start
        U[:ext]+=abs(d.blocks(m.signed)[:ext])
        assert np.array_equal(U[ext:],d.blocks(np.minimum(rad,m.rad))[ext:])
        p=box*o.sw[:,None]*self.units
        local=np.linalg.norm(np.einsum("nij,nj->ni",U,p),axis=1)
        gain=np.sqrt(U.sum(axis=2).max(axis=1)*U.sum(axis=1).max(axis=1))
        costs=[]
        for sl,X in zip(d.bands,current["volumen"]):
            totals=[]
            for weight in self.shapes[:,sl]:
                value,_=q.wj.squared_dual(pad*weight*local[sl],pad*weight*gain[sl],pad*X)
                totals.append(pad*np.sqrt(value))
            costs.append(totals)
        self.by_band=np.array(costs)
        self.before=current["fuerza_resto"]
        self.old_energy=current["energia"]
        return pad*np.linalg.norm(self.by_band,axis=0)

    def observe(self,state,best,remainder,jump,op,row,cr,accepted):
        if len(state.rows)-1<self.start:
            return
        cur=state.rows[-1]
        assert np.all(np.array(cur["energia"])<=np.array(self.old_energy)*(1+1e-12)+1e-25)
        self.log.append(dict(t=row["t"],aceptada=bool(accepted),fb_previa=self.before,
            fb_usada=cur["fuerza_resto"],por_banda_y_peso=self.by_band.tolist(),
            energia=cur["energia"],Sx=cur["cota_Sx"],energia_previa=self.old_energy))


class Policy(q.Policy):
    def start(self,j,ladder,idx,log):
        idx=super().start(j,ladder,idx,log)
        if self.fixed and j==last:
            return np.searchsorted(ladder,archive[-1]["radios"])
        return idx


def study(step,march,table):
    model=q.Project(q.wj.prior["metrica"]["gamma"])
    shift=sx.Refiner(model)
    shift.start=108
    fb=Feedback(model,shift.shape)
    adj=q.base.prev.kernels()
    result={}
    for mode,start,limit in [("control",320,last+1),("fijo",last,last+1),("causal",108,None)]:
        model.D=model.Q=model.beta=0.
        fb.start=start
        fb.log=[]
        policy=Policy(model,"doce",108)
        policy.fixed=mode=="fijo"
        run=q.base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
            radii_policy=policy,limit=limit,shift_refiner=shift.caps,feedback_refiner=fb.caps,
            budget_observer=fb.observe)
        rows=run["filas"]
        assert rows[:start]==archive[:start]
        if mode=="fijo":
            assert rows[-1]["radios"]==archive[-1]["radios"]
        result[mode]=dict(prefijo=run["prefijo"],filas=rows[min(start,last):],presupuesto=fb.log)
        if mode=="fijo":
            old,new=archive[-1]["nucleo"],rows[-1]["nucleo"]
            if any(new[k]>=old[k]*(1-1e-6) for k in ("cara","punto")):
                break
    return result

if __name__=="__main__":
    q.base.cont.main(study,HERE/"resultado.json")
