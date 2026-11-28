"""Contraste puntual reproducible sin modificar historia, radios ni presupuestos."""
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"trabajo_conjunto_20261128"))
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location("trabajo_base",HERE.parent/"trabajo_conjunto_20261128"/"medir.py")
work=module_from_spec(spec)
spec.loader.exec_module(work)
d,ext,cont=work.d,work.ext,work.q.base.cont
ref=json.loads((work.HERE/"resultado.json").read_text())
last=round(ref["causal"]["filas"][-1]["t"]/d.h)-1

def diagnostics(j,radius,entry,current,state,pt):
    assert len(state.rows)==j+1 and state.rows[-1] is current
    return dict(X=current["volumen"],E=current["energia"],entrada=entry.tolist(),
                radios=radius.tolist(),punto=pt.tolist(),cota_Sx=current["cota_Sx"],
                fuerza_resto=current["fuerza_resto"])

def capture(step,march,table):
    original=cont.solve
    trace={}
    def solve(*args,**kw):
        points=kw["point_refiner"]
        def hook(j,radius,entry,current,state,pt):
            pt=points(j,radius,entry,current,state,pt)
            if j==last:
                trace.update(diagnostics(j,radius,entry,current,state,pt))
            return pt
        kw["point_refiner"]=hook
        return original(*args,**kw)
    cont.solve=solve
    try:
        trial=work.study(step,march,table)
    finally:
        cont.solve=original
    assert trial==ref and trace["punto"]==ref["causal"]["filas"][-1]["punto"]
    return trace

if __name__=="__main__":
    cont.main(capture,HERE/"entrada.json")
