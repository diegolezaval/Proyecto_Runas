"""Contrastes independientes en matrices densas y en el registro de continuidad."""
from pathlib import Path
import csv
import gzip
import json
import numpy as np
from scipy.linalg import eigvalsh,null_space,expm
from scipy.sparse import csc_matrix
# Localizar el módulo explícitamente: otras etapas también contienen medir.py.
import importlib.util
spec=importlib.util.spec_from_file_location("multiplicador",Path(__file__).with_name("medir.py"))
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def small():
    u=np.array([1.,2.,3.,4.]);u/=np.linalg.norm(u)
    H=np.diag([1.,2.,3.,4.])-3*np.outer(u,u)
    w=np.array([.3,.2,.9,.1]);I=np.eye(4)
    for beta in (0.,4.):
        Z=null_space(u[None,:]) if beta==0 else I
        K=Z.T@(H+beta*np.outer(u,u))@Z
        exact=np.sqrt(eigvalsh(Z.T@np.diag(w*w)@Z,K)[-1])
        got=a.Block(csc_matrix(H),u,beta,np.arange(4)).bound(w)
        assert abs(exact-got["estimacion"])<1e-10
        assert min(eigvalsh(got["limite"]**2*K-Z.T@np.diag(w*w)@Z))>got["margen_I"]


def main():
    small()
    results=json.loads((a.HERE/"resultado.json").read_text())
    with gzip.open(a.p.HERE/"bandas.csv.gz","rt") as stream:
        rows={(r["caso"],float(r["t"])):{k:float(v) for k,v in r.items() if k!="caso"} for r in csv.DictReader(stream)}
    for case,report in results["controles"].items():
        y=np.array([0.,0.,0.,1.]);time=0.
        for block in report["bloques"]:
            co={v["radio"]:v for v in block.get("coeficientes_por_radio",[])}
            for t,rad,D,q,beta,point in block.get("pasos_aceptados",[]):
                assert t==time+a.h and point<=rad<=1e-4
                r=rows[case,t];v=co[rad]
                M=a.p.matrix(r["F"],r["Fq"],r["pos"],r["vel"],0)
                M[0,:3]+=np.array(v["coef_F"])+a.o.kc*np.array(v["coef_q"])
                M[1,:3]+=v["coef_q"]
                y=expm(a.h*M/2)@(expm(a.h*M/2)@y)
                assert np.allclose(y[:3],[D,q,beta],atol=1e-18,rtol=1e-10)
                assert abs(a.trace@y[:3]-point)<1e-13
                time=t
        assert (time==40 if report["primer_exceso_por_paso"] is None else time+a.h==report["primer_exceso_por_paso"])
    print("Contrastes densos, inercia y secuencia de radios aceptados verificados")

if __name__=="__main__":
    main()
