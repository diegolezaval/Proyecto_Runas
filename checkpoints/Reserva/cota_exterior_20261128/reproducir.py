"""Marcha desde cero; solo se activa la nueva conversión a partir de s=22,875."""
import json
import numpy as np
from diagnostico import work,d,cont,HERE,ref,last
from formas import coefficient

params={3:[(80,l,0.) for l in (0.,.17,.68)],
        4:[(320,l,a) for a in (.0625,.25,1.,4.) for l in (0.,.17,.68,2.72)]}

def study(step,march,table):
    loaded=json.loads((HERE/"entrada.json").read_text())
    target=ref["causal"]["filas"][-1]
    arr={b:np.array([coefficient(b,*p)[0] for p in ps]) for b,ps in params.items()}
    original=cont.solve
    traces={}
    def solve(*args,**kw):
        old=kw["point_refiner"]
        policy=kw["radii_policy"]
        fixed=kw["limit"] is None
        def baseline(j,radius,entry,current,state,pt):
            pt=old(j,radius,entry,current,state,pt)
            if j<last:
                return pt
            before=pt.copy()
            X,E=np.array(current["volumen"],np.longdouble),np.array(current["energia"],np.longdouble)
            if fixed:
                assert entry.tolist()==loaded["entrada"] and radius.tolist()==loaded["radios"]
                assert before.tolist()==target["punto"] and X.tolist()==loaded["X"] and E.tolist()==loaded["E"]
            winners={}
            for b,ps in params.items():
                a=np.array(ps,dtype=np.longdouble)
                budget=np.sqrt(E[b]**2+a[:,1]*X[b]**2+a[:,2]*E[7-b]**2)
                all_points=arr[b]*np.asarray(budget,float)[:,None]*(1+2e-12)
                env=all_points.min(axis=0)
                i=env.argmax()
                w=all_points[:,i].argmin()
                winners[str(b)]={"cota":float(env[i]),"r":float(d.g.r[d.bands[b]][i]),"parametros":list(ps[w])}
                pt[b]=min(pt[b],env[i])
            assert pt[:3].tolist()==before[:3].tolist()
            traces[str(j)]=dict(envolvente=pt.tolist(),original=before.tolist(),
                radios=radius.tolist(),entrada=entry.tolist(),formas=winners)
            return pt
        # Separate fixed inspection from the causal activation, using exactly the
        # archived final radii in the fixed inspection.
        if not fixed:
            kw["point_refiner"]=baseline
            return original(*args,**kw)
        policy_start=policy.start
        def fixed_start(j,ladder,idx,log):
            if j==last:
                return np.searchsorted(ladder,target["radios"])
            return policy_start(j,ladder,idx,log)
        policy.start=fixed_start
        kw["point_refiner"]=baseline
        kw["limit"]=last+1
        restored=original(*args,**kw)
        policy.start=policy_start
        policy.model.D=policy.model.Q=policy.model.beta=0.
        assert restored["filas"][:-1]==ref["causal"]["filas"][:-1]
        assert restored["filas"][-1]["aceptado"]
        fixed_trace=traces.pop(str(last))
        kw["limit"]=None
        def causal(j,radius,entry,current,state,pt):
            nonlocal fixed
            fixed=False
            return baseline(j,radius,entry,current,state,pt)
        kw["point_refiner"]=causal
        replay=original(*args,**kw)
        traces["entrada_fija"]=fixed_trace
        return replay
    cont.solve=solve
    try:
        run=work.study(step,march,table)
    finally:
        cont.solve=original
    assert all(run[m]==ref[m] for m in ("control","fijo"))
    rows=run["causal"]["filas"]
    assert rows[:last]==ref["causal"]["filas"][:last]
    assert rows[last]["aceptado"]
    return {"prefijo":run["causal"]["prefijo"],"filas":rows[last:],"evaluacion":traces}

if __name__=="__main__":
    cont.main(study,HERE/"marcha.json")
