"""Cribado del coste espectral de caras sin volver a marchar el estado."""
from pathlib import Path
import json
from importlib.util import module_from_spec, spec_from_file_location
import numpy as np

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("historial_caras",HERE.parent/"historial_caras_20261127/auditar.py")
h=module_from_spec(spec)
spec.loader.exec_module(h)
q,d,o=h.q,h.d,h.q.o
pad=1+1e-11


def main():
    audit=json.loads((h.HERE/"resultado.json").read_text())
    model=q.Project(q.wj.prior["metrica"]["gamma"])
    _,S,ev,_=d.floor_operator()
    shape=d.geometry()[0][1]
    gain=shape*ev.max(axis=1)
    assert not np.any(S[d.bands[2].start:]) and np.all(q.core.w[d.bands[0]]==1)
    gram_check=np.abs(np.linalg.eigvalsh(S)).max(axis=1)
    assert np.max(abs(ev.max(axis=1)-gram_check))<1e-13
    units=np.array([np.sqrt(2),np.sqrt(2),1.])
    rows=[]
    for orig,record in zip(h.archive,audit["filas"],strict=True):
        assert orig["t"]==record["t"] and orig["aceptado"]==record["aceptada"]
        cr=orig["nucleo"]
        bands=[]
        for k,(diag,kap,phase) in enumerate([(model.diag,model.kr,model.ur),
                                            (model.local,model.k1,model.u1)]):
            sl=d.bands[k]
            old=np.sqrt(record["S_por_banda_cuadrado"][k])
            X=pad*old/max(gain[sl])
            cut=diag*cr["D"]+kap*cr["Q"]+phase*cr["beta"]
            w=q.core.w[sl,None]
            cap=np.broadcast_to(orig["radios"][k]*units,cut.shape).copy()
            np.minimum(cap,np.divide(pad*cut,w,out=cap.copy(),where=w>0),out=cap)
            p=cap*o.sw[sl,None]
            a=pad*shape[sl]*np.linalg.norm(np.einsum("nij,nj->ni",abs(S[sl]),p),axis=1)
            b=pad*gain[sl]
            dual,lam=q.wj.squared_dual(a,b,X)
            new=min(old,np.sqrt(dual)*pad)
            bands.append(dict(X=X,anterior=old,caja=pad*np.linalg.norm(a),nuevo=new,lam=lam))
        rows.append(dict(t=orig["t"],bandas=bands,
            fuente_previa=np.linalg.norm([b["anterior"] for b in bands]),
            fuente_nueva=pad*np.linalg.norm([b["nuevo"] for b in bands])))
    endpoints=[]
    for ext in audit["extremos"]:
        em=np.array(ext["emisiones"])
        n=len(em)
        data=rows[:n]
        old=em[:,3]*[r["fuente_previa"] for r in data]
        h.matches(old,em[:,5])
        new=np.minimum(old,em[:,3]*[r["fuente_nueva"] for r in data])
        base=audit["filas"][n-1]
        other=em[:,[4,6,7,8]].sum()
        assert base["usa_espectral"]
        h.matches(model.gamma*(other+old.sum()),base["coste_caras"])
        alternative=min(base["coste_caras"],pad*model.gamma*(other+new.sum()))
        endpoints.append(dict(t=ext["t"],S_previo=old.sum(),S_nuevo=new.sum(),otras=other,
            caras_previas=base["coste_caras"],caras_cribado=alternative,
            reduccion_relativa=1-alternative/base["coste_caras"]))
    (HERE/"resultado.json").write_text(json.dumps(dict(filas=rows,extremos=endpoints),
        separators=(",",":"),allow_nan=False)+"\n")

if __name__=="__main__":
    main()
