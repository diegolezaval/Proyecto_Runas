"""Usa |z| junto con |z'| en las mismas cotas del mapa exterior."""
from pathlib import Path
import sys
import csv
import gzip
import json
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"contraccion_escalon_20261127"))
import escalon

def main():
    records=json.loads((escalon.HERE/"contraccion.json").read_text())
    prior=json.loads((escalon.HERE/"escalon.json").read_text())
    kernel,ev,info,shifted=escalon.compute(return_static=True)
    with gzip.open(escalon.ex.source,"rt") as stream:
        table=[r for r in csv.DictReader(stream) if r["caso"]=="gota_a010"]
    result=dict(controles=info)
    for label in ("original","ampliado"):
        record=records[label]
        baseline=escalon.assess(record,kernel,ev,table)
        assert baseline==prior[label]
        new=escalon.assess(record,kernel,ev,table,shifted)
        series=np.array(new["filas"])
        assert np.all(series[:,4]<=np.array(baseline["filas"])[:,4]+1e-18)
        failed=series[series[:,4]>1e-4,0]
        new["primer_exceso"]=float(failed[0]) if len(failed) else None
        result[label]=new
    (HERE/"resultado.json").write_text(json.dumps(result,separators=(",",":"),allow_nan=False)+"\n")

if __name__=="__main__":
    main()
