"""Presupuestos de las cinco fuentes físicas con los adjuntos ya contrastados."""
import json
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"nucleo_carga_fija_20261127"))
import continuar as run
from nucleos import kernels

def study(step,march,table):
    d=run.d
    adj,fine=kernels(d.indices)
    forces=[]
    original=run.solve(step,march,table,adj=adj,observe=forces.append)
    published=json.loads((run.HERE/"continuacion.json").read_text())
    assert original==published
    physical=np.array(forces)
    base=np.array([[r[k] for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for r in table])
    grouped=np.column_stack([np.linalg.norm(physical[:,:3],axis=1),physical[:,3:]])
    rows=[]
    for j,r in enumerate(original["filas"]):
        n=j+1
        linear=d.h*np.einsum("lij,li->j",adj[:n],base[j::-1])
        linear[1]+=table[j]["pos"]/d.o.sw[d.loc.i40-1]
        coarse=adj[:n,:3]*grouped[j::-1,:,None]
        bands=fine[:n]*physical[j::-1,:,None]
        detail=d.h*bands.sum(axis=0)
        # Only the first three physical bands had been pooled. Keep the smaller
        # product per lag there and retain the last two groups independently.
        sharp=d.h*(np.minimum(bands[:,:3].sum(axis=1),coarse[:,0])+
                   np.minimum(bands[:,3],coarse[:,1])+np.minimum(bands[:,4],coarse[:,2])).sum(axis=0)
        previous=linear+d.h*coarse.sum(axis=(0,1))
        assert np.allclose(previous,[r["z"],r["dz"]],rtol=1e-12,atol=1e-22)
        rows.append(dict(t=r["t"],aceptado=r["aceptado"],fuerza=physical[j].tolist(),
                         lineal=linear.tolist(),bandas=detail.tolist(),anterior=previous.tolist(),
                         nuevo=(linear+sharp).tolist()))
    good=[r for r in rows if r["aceptado"]]
    discount=np.exp(.051*(40-np.arange(len(good))*d.h))
    total=np.array([r["nuevo"] for r in good])
    detail=np.array([r["bandas"] for r in good])
    return dict(prefijo=len(good)*d.h,integral_dz=d.h*sum(total[:,1]),
                integral_dz_ponderada=d.h*(discount@total[:,1]),z_ultimo=total[-1,0],
                integrales_banda_dz=(d.h*detail[:,:,1].sum(axis=0)).tolist(),
                ponderadas_banda_dz=(d.h*(discount@detail[:,:,1])).tolist(),
                lineal_ponderada_prefijo=d.h*(discount@np.array([r["lineal"][1] for r in good])),
                anterior_ponderada=original["integral_dz_con_peso_a_40"],filas=rows)


if __name__=="__main__":
    run.main(study,HERE/"resultado.json")
