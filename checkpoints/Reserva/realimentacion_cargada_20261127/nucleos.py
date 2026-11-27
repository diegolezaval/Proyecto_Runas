"""Recupera las envolventes de retardo no serializadas de la traza publicada."""
import sys
from pathlib import Path
import json

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"adjunta_cargada_20261127"))
import adjunta as old


def kernels():
    ref=json.loads((old.HERE/"resultado.json").read_text())
    K,O=old.matrices(old.n)
    R=np.tile(old.sign,old.n)[:,None]
    seed=np.zeros((3*old.n,6))
    seed[3*old.i:3*old.i+3,:3]=np.eye(3)/old.sw
    w=np.roll(seed,3,axis=1)
    v=R*(seed-O@w)
    w=R*w
    bins=np.zeros((320,5,2))
    edge=0.
    for step in range(1280):
        a,b=w,v
        W,V=w.copy(),v.copy()
        envelope=np.zeros((5,2))
        wall=np.zeros(2)
        for order in range(old.degree+1):
            envelope[0]+=old.norms(a[:3*old.loc.cuts[1]])
            envelope[1]+=old.norms(a[3*old.loc.cuts[1]:])
            envelope[3]+=old.norms(b-O@a)
            envelope[4]+=old.norms(a)
            wall+=old.norms(a[-3:])
            if order<old.degree:
                scale=old.h/(order+1)
                a,b=scale*b,scale*(-K@a+O@b)
                W+=a
                V+=b
        bins[step//4]=np.maximum(bins[step//4],envelope)
        edge=max(edge,max(wall))
        w,v=W,V
    assert edge<=max(ref["envolvente_pared"])
    remainder=ref["resto_total_energia"]
    bins[:,[0,1,2,4]]+=remainder/np.sqrt(.590)
    bins[:,3]+=remainder*(1+2*old.o.om/np.sqrt(.590))
    return np.maximum(bins,np.concatenate([bins[:1],bins[:-1]]))
