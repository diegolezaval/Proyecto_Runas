"""Recupera las envolventes de retardo no serializadas de la traza publicada."""
import sys
from pathlib import Path
import json

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"adjunta_cargada_20261127"))
import adjunta as old


def kernels(cuts=None,subcuts=None):
    ref=json.loads((old.HERE/"resultado.json").read_text())
    K,O=old.matrices(old.n)
    R=np.tile(old.sign,old.n)[:,None]
    seed=np.zeros((3*old.n,6))
    seed[3*old.i:3*old.i+3,:3]=np.eye(3)/old.sw
    w=np.roll(seed,3,axis=1)
    v=R*(seed-O@w)
    w=R*w
    bins=np.zeros((320,5,2))
    fine=np.zeros((320,len(cuts)-1,2)) if cuts is not None else None
    if subcuts is not None:
        sub=np.zeros((320,len(subcuts)-1,3,2))
        starts=np.asarray(subcuts[:-1])
        present=starts<old.n
    edge=0.
    for step in range(1280):
        a,b=w,v
        W,V=w.copy(),v.copy()
        envelope=np.zeros((5,2))
        wall=np.zeros(2)
        if subcuts is not None: by_component=np.zeros_like(sub[0])
        if cuts is not None: detail=np.zeros_like(fine[0])
        for order in range(old.degree+1):
            if subcuts is not None:
                viewed=a.reshape(old.n,3,2,3)
                squares=np.einsum("nijk,nijk->nij",viewed,viewed)
                by_component[present]+=np.sqrt(np.add.reduceat(squares,starts[present],axis=0))
            if cuts is not None:
                for j,(left,right) in enumerate(zip(cuts,cuts[1:])):
                    block=a[3*left:3*right]
                    if len(block): detail[j]+=old.norms(block)
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
        if cuts is not None: fine[step//4]=np.maximum(fine[step//4],detail)
        if subcuts is not None: sub[step//4]=np.maximum(sub[step//4],by_component)
        edge=max(edge,max(wall))
        w,v=W,V
    assert edge<=max(ref["envolvente_pared"])
    remainder=ref["resto_total_energia"]
    bins[:,[0,1,2,4]]+=remainder/np.sqrt(.590)
    bins[:,3]+=remainder*(1+2*old.o.om/np.sqrt(.590))
    combined=np.maximum(bins,np.concatenate([bins[:1],bins[:-1]]))
    if cuts is None: return combined
    fine+=remainder/np.sqrt(.590)
    grouped=np.maximum(fine,np.concatenate([fine[:1],fine[:-1]]))
    if subcuts is not None:
        return combined,grouped,np.maximum(sub,np.concatenate([sub[:1],sub[:-1]])),remainder/np.sqrt(.590)
    return combined,grouped
