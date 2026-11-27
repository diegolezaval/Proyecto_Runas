"""Suelo del mayorante elegido, no del error de campo."""
import csv
import json
import numpy as np
import medir_correccion as a

def main():
    with (a.HERE/"series.csv").open() as stream:
        rows=list(csv.DictReader(stream))
    scale=np.sqrt(2/a.o.gap)
    conversions={"global":scale/min(np.sqrt(a.loc.weights)*a.o.sw),
                 "interior":scale/min(a.o.sw[a.g.r<60])}
    result={}
    for case in ("gota_a010","gemelo","receptora"):
        D=0.
        first={key:None for key in conversions}
        for row in rows:
            if row["caso"]!=case:
                continue
            D=D*np.exp(.5*a.h)+float(row["cota_cambio"])*np.expm1(.5*a.h)/.5
            for key,value in conversions.items():
                if first[key] is None and D*value>a.o.tube:
                    first[key]=float(row["t"])
        result[case]=dict(D40=D,primer_exceso=first,
                          conversion_final={k:D*v for k,v in conversions.items()})
    (a.HERE/"presupuesto.json").write_text(json.dumps(result,indent=2)+"\n")

if __name__=="__main__":
    main()
