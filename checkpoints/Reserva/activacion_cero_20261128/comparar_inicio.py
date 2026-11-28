"""Comparar las emisiones heredadas y dos momentos de activación."""
import json
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"realimentacion_celda_20261128"))
import marcha_fb as fb
q,d,o=fb.q,fb.d,fb.o
CUT=108
control=fb.archive[:CUT]+json.loads((fb.HERE/"resultado.json").read_text())["causal"]["filas"]


class Activation(q.Policy):
    def start(self,j,ladder,idx,log):
        idx=super().start(j,ladder,idx,log)
        self.model.active_face=j>=self.first_new
        self.model.mode="diez" if self.model.active_face else "control"
        return idx


class Ledger:
    def __init__(self,model):
        self.m=model
        self.rows=[]
        self.in_D=0.
        self.face_D=np.zeros(3)
        self.other_D=0.

    def observe(self,state,best,remainder,jump,op,row,cr,ok):
        n=len(state.rows)
        current=state.rows[-1]
        # Signed-mode history and numeric already include every later metric jump.
        emissions=(np.asarray(state.history)[:,1]+np.array(state.numeric))*state.E[:n,1][::-1]
        early=emissions[:CUT].sum()
        late=emissions[CUT:].sum()
        energy=current["energia"][1]
        assert np.isclose(early+late,energy,rtol=2e-12,atol=1e-25)
        x=np.array(current["volumen"])
        old=self.m.s*energy+self.m.c*x[1]
        spectral=self.m.active_face and self.m.gamma*energy<=old
        factor=self.m.gamma if spectral else self.m.s
        split=np.array([factor*early,factor*late,0 if spectral else self.m.c*x[1]])
        assert np.isclose(split.sum(),cr["cara"],rtol=2e-12,atol=1e-25)
        if n<=CUT:
            self.in_D=cr["D"]
        else:
            self.face_D+=d.h*split
            rest=cr["prescrita"]+cr["no_lineal"]+row["vel"]+d.p.op*row["pos"]+cr["trabajo_carga"]+o.eps*(self.m.uw@x)
            self.other_D+=d.h*rest
        assert np.isclose(self.in_D+self.face_D.sum()+self.other_D,cr["D"],rtol=2e-12,atol=1e-25)
        point=max(self.m.coef*(cr["D"]-self.in_D)+self.m.kap*cr["Q"]+self.m.phase*cr["beta"])
        self.rows.append(dict(t=row["t"],aceptada=bool(ok),D_corte=self.in_D,
            energia_pre=early,energia_post=late,caras_desglose=split.tolist(),caras=cr["cara"],
            D_caras_post=self.face_D.tolist(),D_demas_post=self.other_D,D=cr["D"],
            punto=cr["punto"],punto_sin_D_corte=point))


def study(step,march,table):
    model=q.Project(q.wj.prior["metrica"]["gamma"])
    shift=fb.sx.Refiner(model)
    feedback=fb.Feedback(model,shift.shape)
    adj=q.base.prev.kernels()
    result={}
    for mode,start in [("tardio",CUT),("cero",0)]:
        model.D=model.Q=model.beta=0.
        shift.start=feedback.start=start
        ledger=Ledger(model)
        run=q.base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
            radii_policy=Activation(model,"doce",start),shift_refiner=shift.caps,
            feedback_refiner=feedback.caps,budget_observer=ledger.observe)
        rows=run["filas"]
        result[mode]=dict(prefijo=run["prefijo"],filas=rows,contabilidad=ledger.rows)
        if mode=="tardio":
            assert rows==control
            r=ledger.rows[-1]
            if not (r["punto_sin_D_corte"]<o.tube<r["punto"] and r["caras_desglose"][0]>0):
                break
    return result

if __name__=="__main__":
    q.base.cont.main(study,HERE/"resultado.json")
