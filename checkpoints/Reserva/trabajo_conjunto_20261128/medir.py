"""Contraste de trabajo directo por soportes disjuntos, con proyección separada."""
from importlib.util import module_from_spec, spec_from_file_location
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "gram_nucleo_20261128"))
spec=spec_from_file_location("gram_reproducido",HERE.parent/"gram_nucleo_20261128"/"evaluar.py")
gram=module_from_spec(spec)
spec.loader.exec_module(gram)

exterior = gram.exterior
ext, d, q, start = exterior.ext, exterior.d, exterior.q, exterior.start
archive = gram.archive
last = len(archive)-1
prior = json.loads((gram.HERE / "resultado.json").read_text())
pad = 1+2e-11


def combined(core, transition, faces):
    z = [np.longdouble(t) for t in (core, transition, faces)]
    return float(pad*np.hypot(z[0],z[1]+z[2]))


class Model(q.Project):
    active_work = False

    def direct_work(self,F,nl,faces,f0,tail):
        old = super().direct_work(F,nl,faces,f0,tail)
        if not self.active_work:
            return old
        assert np.all(tail[1:] == 0)
        b = combined(f0,tail[0],faces)
        self.work = dict(interior=f0,transicion=tail[0],caras=faces,anterior=nl+faces,conjunto=b)
        return min(old,float(pad*(np.longdouble(F)+b)))

    def refine(self,old,x,e,J,qcoeff,row,F,beta_in):
        # At this stage shift and feedback caps were computed from the unrevised trial.
        try:
            self.active_work=True
            r=self.trial(x,e,J,qcoeff,row,F)
        finally:
            self.active_work=False
        o=d.o
        beta=(beta_in+d.h*(self.phase_dual*r["D"]+(abs(o.gamma)+1e-12)*r["Q"]+r["cinematica"]))*(1+1e-12)
        r["beta"]=min(r["beta"],beta)
        r["punto"]=min(r["punto"],float(max(self.coef*r["D"]+np.hypot(self.kap*r["Q"],self.phase*r["beta"]))*pad))
        assert r["D"]<=old["D"]+1e-15 and r["punto"]<=old["punto"]+1e-15
        r["trabajo_conjunto"]=self.work.copy()
        return r


def study(step,march,table):
    sl=d.bands[1]
    rows,cols=gram.core.comm.nonzero()
    assert len(rows) and min(rows)>=sl.start and max(rows)<sl.stop
    assert np.all(gram.core.w[d.g.r>=38]==0)
    assert combined(3,4,0)>=5 and combined(3,4,0)<5*(1+3e-11)
    assert combined(0,4,5)>=9 and combined(0,4,5)<9*(1+3e-11)
    result={"soporte_filas_r":[d.g.r[min(rows)],d.g.r[max(rows)]],
            "soporte_columnas_r":[d.g.r[min(cols)],d.g.r[max(cols)]]}
    old=ext.Evaluator(np.array([ext.coefficients(v)[0] for v in ext.lambdas]))
    middle=ext.Evaluator(np.array([ext.coefficients(v,3)[0] for v in ext.lambdas]),3)
    old.first=middle.first=0
    coef=np.array([exterior.coefficients(v)[0] for v in ext.lambdas])
    model=Model(q.wj.prior["metrica"]["gamma"])
    # Reconstruct the certified phase coefficient used by Gram, not the rounded report.
    o=d.o
    residual=np.linalg.norm(o.C(o.kap)-2*o.om*gram.core.v)
    model.phase_dual=(o.kc+residual/np.sqrt(o.gap))*(1+1e-9)
    assert abs(model.phase_dual-prior["fase_dual"]["coef"])<1e-15
    shift=start.fb.sx.Refiner(model)
    fb=start.fb.Feedback(model,shift.shape)
    shift.start=fb.start=0
    adj=q.base.prev.kernels()
    for mode,first,limit in [("control",320,last+1),("fijo",last,last+1),("causal",0,None)]:
        model.D=model.Q=model.beta=0.
        class Policy(start.Activation):
            def start(self,j,ladder,idx,log):
                idx=super().start(j,ladder,idx,log)
                if mode=="fijo" and j==last:
                    return np.searchsorted(ladder,archive[-1]["radios"])
                return idx

        def points(j,radius,entry,current,state,pt):
            pt=middle.refine(j,radius,entry,current,state,old.refine(j,radius,entry,current,state,pt))
            E,X=old.details["E"],old.details["X"]
            budget=np.hypot(E,np.sqrt(ext.lambdas)*X)[:,None]*(1+1e-12)
            profile=np.min(old.coeff*budget,axis=0)
            better=np.min(coef*budget,axis=0)
            pt[-1]=min(pt[-1],np.minimum(profile,better).max())
            return pt

        def final(j,kernel,base,*args):
            if j<first:
                return base
            beta_in=prior["fase_dual"]["serie_beta"][j-1] if mode=="fijo" else model.beta
            if mode=="fijo":
                assert base==archive[-1]["nucleo"]
            return model.refine(base,*args,beta_in)

        run=q.base.cont.solve(step,march,table,adj=adj,core_model=model,box_observer=model.reference,
            radii_policy=Policy(model,"doce",0),limit=limit,shift_refiner=shift.caps,
            feedback_refiner=fb.caps,point_refiner=points,core_final_refiner=final)
        achieved=run["filas"]
        assert achieved[:first]==archive[:first]
        result[mode]={"prefijo":run["prefijo"],"filas":achieved[min(first,last):]}
        if mode=="fijo":
            fixed=achieved[-1]
            assert fixed["radios"]==archive[-1]["radios"] and fixed["punto"][1:]==archive[-1]["punto"][1:]
            if not fixed["aceptado"]:
                break
    return result


if __name__=="__main__":
    q.base.cont.main(study,HERE/"resultado.json")
