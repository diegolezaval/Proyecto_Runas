"""Contracción física por componentes y subregiones con historia FV inalterada."""
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"nucleo_carga_fija_20261127"))
import continuar as run
from nucleos import kernels

d=run.d
edges=np.r_[0,np.arange(10,41,2),np.arange(60,161,2),256]
split=np.searchsorted(d.g.r,edges)
sources=(1,3)
parts=[np.where((edges[:-1]>=lo)&(edges[1:]<=hi))[0] for lo,hi in [(10,40),(60,160)]]


def series(step,march,table,records,adj,linear):
    shapes,rates=d.geometry()
    V,S,s,rate=d.floor_operator()
    exterior=d.loc.i40
    state=d.Comparison("firmado",shapes,rates,s,rate)
    old=None
    history=[]
    for j,(best,J,row,signed,time,total,centre,width) in enumerate(d.sources(step,march,table)):
        if j==len(records):break
        radius=records[j]["radios"]
        mat=d.blocks(signed);H=V[exterior:]+mat[exterior:]
        jump=1.
        if old is not None:
            C=np.linalg.inv(np.linalg.cholesky(old))
            jump=np.sqrt(1+max(0,np.linalg.eigvalsh(C@(H-old)@C.transpose(0,2,1))[:,-1].max()))
        old=H
        cells=np.repeat(radius,np.diff(d.indices))[:,None]
        _,rad=d.columnas.jac_box(centre,width+cells)
        bounds=abs(mat)+d.blocks(rad)
        physical=np.minimum(J,[max(bounds[b].sum(axis=2).max(axis=1)) for b in d.bands])
        rem=physical.copy()
        rem[2:]=[max(d.blocks(rad)[b].sum(axis=2).max(axis=1)) for b in d.bands[2:]]
        state.advance(best,physical,row,adj,linear,rem,jump,abs(mat[exterior:]).sum(axis=2).max())
        cur=state.rows[-1]
        assert np.allclose([cur["z_total"],cur["dz_total"]],[records[j]["z"],records[j]["dz"]],rtol=1e-12,atol=1e-25)
        X=np.array(cur["volumen"])
        matrices=np.maximum.reduceat(bounds,split[:-1],axis=0)
        history.append((X,physical,matrices))
    return history


def profile(adj,fine,sub,err,hist,linear,prior):
    bands=np.array([X*J for X,J,M in hist])
    grouped=np.column_stack([np.linalg.norm(bands[:,:3],axis=1),bands[:,3:]])
    rows=[]
    # Each source slab feeds all subsequent observation slabs.
    summed=np.zeros((320,2))
    control=summed.copy()
    contrib=np.zeros((320,5,2))
    for i,(X,J,M) in enumerate(hist):
        n=320-i
        five=fine[:n]*bands[i,:,None]
        coarse=adj[:n,:3]*grouped[i,:,None]
        inner=np.minimum(five[:,:3].sum(axis=1),coarse[:,0])
        outer=np.minimum(five[:,3],coarse[:,1])
        tail=np.minimum(five[:,4],coarse[:,2])
        control[i:]+=d.h*(inner+outer+tail)
        contracted=five.copy()
        for b,k in zip(sources,parts):
            product=np.einsum("sij,lsio->lsjo",M[k],sub[:n,k])
            # One global Taylor/crop remainder for this band and observation.
            norm=np.sqrt(np.sum(product**2,axis=(1,2)))+err*J[b]
            contracted[:,b]=np.minimum(five[:,b],X[b]*norm)
        inner=np.minimum(contracted[:,:3].sum(axis=1),coarse[:,0])
        summed[i:]+=d.h*(inner+np.minimum(contracted[:,3],outer)+tail)
        contrib[i:]+=d.h*contracted
    assert np.allclose(control,np.array(prior["filas"])[:,3:5],rtol=1e-11,atol=1e-22)
    total=linear+summed
    weight=np.exp(.051*(40-np.arange(320)*d.h))
    for j in range(320):
        rows.append(dict(t=(j+1)*d.h,z=total[j,0],dz=total[j,1],nl=summed[j].tolist(),
                         antes=control[j].tolist(),bandas_dz=contrib[j,:,1].tolist()))
    return dict(prefijo=len(hist)*d.h,simple=d.h*sum(total[:,1]),ponderada=d.h*(weight@total[:,1]),
                antigua_simple=prior["integrales"]["simple"]["total_fuentes_conocidas"],
                simple_posterior_nl=d.h*sum(summed[len(hist):,1]),
                contribuciones=d.h*contrib[:,:,1].sum(axis=0), filas=rows,
                fuentes=bands.tolist())


def study(step,march,table):
    past=json.loads((HERE.parent/"caja_componentes_20261127/resultado.json").read_text())
    before=json.loads((run.HERE/"continuacion.json").read_text())
    adj,fine,sub,err=kernels(d.indices,split)
    base=np.array([[r[k] for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for r in table])
    linear=np.array([d.h*np.einsum("lij,li->j",adj[:j+1],base[j::-1]) for j in range(320)])
    linear[:,1]+=base[:,3]/d.o.sw[d.loc.i40-1]
    rng=np.random.default_rng(47)
    J=rng.normal(size=(64,3,3))
    P=rng.normal(size=(64,3,3))
    actual=np.linalg.norm(np.einsum("nij,nio->njo",J,P))
    cap=np.linalg.norm(np.abs(J).max(axis=0).T@np.sqrt(np.sum(P**2,axis=(0,2))))
    assert actual<=cap
    out=dict(test_contraccion=[actual,cap],bordes=edges.tolist(),resto=err)
    for label,record,prior in [("original",before,past["antiguas"]),("ampliado",past["continuacion"],past["traza_nueva"])]:
        hist=series(step,march,table,[r for r in record["filas"] if r["aceptado"]],adj,linear)
        result=profile(adj,fine,sub,err,hist,linear,prior)
        result["contribuciones"]=result["contribuciones"].tolist()
        out[label]=result
    return out


if __name__=="__main__":
    run.main(study,HERE/"contraccion.json")
