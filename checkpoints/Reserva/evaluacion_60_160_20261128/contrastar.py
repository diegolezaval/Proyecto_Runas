"""Evaluación intermedia con dos cortes libres y control exterior publicado."""
from pathlib import Path
import sys
import json
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"evaluacion_exterior_20261128"))
import medir_exterior as ext
q,start=ext.q,ext.start
arch=json.loads((ext.HERE/"resultado.json").read_text())["causal"]["filas"]
last=len(arch)-1


class Policy(start.Activation):
    def start(self,j,ladder,idx,log):
        idx=super().start(j,ladder,idx,log)
        if self.fixed and j==last:
            return np.searchsorted(ladder,arch[-1]["radios"])
        return idx


def study(step,march,table):
    outer=ext.Evaluator(np.array([ext.coefficients(v)[0] for v in ext.lambdas]))
    outer.first=0
    coef,meta=zip(*(ext.coefficients(v,3) for v in ext.lambdas))
    middle=ext.Evaluator(np.array(coef),3)
    def points(j,radius,entry,current,state,pt):
        pt=outer.refine(j,radius,entry,current,state,pt)
        return middle.refine(j,radius,entry,current,state,pt)
    model=q.Project(q.wj.prior["metrica"]["gamma"])
    sh=start.fb.sx.Refiner(model)
    fb=start.fb.Feedback(model,sh.shape)
    sh.start=fb.start=0
    adj=q.base.prev.kernels()
    out=dict(matrices=meta)
    for mode,first,limit in [("control",320,last+1),("fijo",last,last+1),("causal",0,None)]:
        middle.first=first
        model.D=model.Q=model.beta=0.
        policy=Policy(model,"doce",0)
        policy.fixed=mode=="fijo"
        log=[]
        def observe(state,best,rem,jump,op,row,cr,ok):
            if len(state.rows)-1>=first:
                log.append(dict(t=row["t"],aceptado=bool(ok),**middle.details))
        run=q.base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
            radii_policy=policy,limit=limit,shift_refiner=sh.caps,feedback_refiner=fb.caps,
            point_refiner=points,budget_observer=observe)
        rows=run["filas"]
        assert rows[:first]==arch[:first]
        out[mode]=dict(prefijo=run["prefijo"],filas=rows[min(first,last):],evaluacion=log)
        if mode=="fijo":
            assert rows[-1]["radios"]==arch[-1]["radios"]
            assert all(rows[-1]["punto"][i]==arch[-1]["punto"][i] for i in (0,1,2,4))
            if not rows[-1]["aceptado"]:
                break
    return out


if __name__=="__main__":
    q.base.cont.main(study,HERE/"resultado.json")
