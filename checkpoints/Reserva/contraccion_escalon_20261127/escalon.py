"""Tres columnas del escalón exterior y fuentes de volumen por separado."""
import csv
import gzip
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import bmat,block_diag,csc_matrix,eye
from scipy.sparse.linalg import expm_multiply,splu

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"interfaz_cargada_20261127"))
import interfaz as ex

n=ex.n
nc=ex.loc.cuts[1]-ex.cut
h=1/32
unit=np.array([np.sqrt(2),np.sqrt(2),1.])


def spectral(a):
    return np.linalg.svd(a,compute_uv=False)[:,0]


def compute():
    K=ex.stiffness()
    eye_n=eye(n)
    O=bmat([[None,2*ex.o.om*eye_n,None],[-2*ex.o.om*eye_n,None,None],
            [None,None,csc_matrix((n,n))]],format="csr")
    B=np.zeros((3*n,3))
    B[np.arange(3)*n,np.arange(3)]=ex.sw[0]*ex.g.lo[ex.cut]
    L=splu(K).solve(B)
    def local(x):
        return x.reshape(3,n,3)[:,:nc].transpose(1,0,2)/ex.sw[:nc,None,None]
    def size(x):
        values=local(x)
        return np.column_stack([spectral(values),spectral(values/unit[None,:,None])])
    kabs=np.max(abs(K).sum(axis=1))
    gen=np.sqrt(kabs)+2*ex.o.om
    order=40
    trunc=np.exp(gen*h)*(gen*h)**(order+1)/math.factorial(order+1)
    initial=np.sqrt(np.linalg.eigvalsh(L.T@(K@L))[-1])
    m=ex.loc.potential_min
    residue=np.linalg.norm(K@L-B,2)/np.sqrt(m)
    limit=1281*trunc*initial*np.exp(1281*trunc)+2*residue
    resistance=np.sqrt(np.cumsum(1/(4*np.pi*ex.loc.face[ex.cut-1:ex.cut-1+nc])))
    ev=np.minimum(resistance,1/(ex.sw[:nc]*np.sqrt(m)))
    interp=(h/2)**2/8*np.linalg.norm(B,2)/ex.sw[:nc]
    envelope=np.zeros((320,nc,2))
    x=L.copy();v=np.zeros_like(L);zero=size(L-x)
    assert max(zero.ravel())==0
    previous=zero
    drift=0.
    for j in range(1280):
        a,b=x,v
        X,V=x.copy(),v.copy()
        mid=x.copy()
        for k in range(1,order+1):
            factor=h/k
            a,b=factor*b,factor*(-K@a+O@b)
            X+=a;V+=b
            mid+=2.**(-k)*a
        # Subtract before applying the observation and taking any norm.
        midpoint=size(L-mid);endpoint=size(L-X)
        bound=np.maximum(np.maximum(previous,midpoint),endpoint)+(ev*limit+interp)[:,None]
        envelope[j//4]=np.maximum(envelope[j//4],bound)
        x,v,previous=X,V,endpoint
        if j==3: sample=x.copy()
        if j%64==63:
            gram=x.T@(K@x)+v.T@v
            drift=max(drift,np.linalg.norm(gram-L.T@(K@L),2)/initial**2)
    assert drift<1e-9
    # Smooth boundary input z=sin(t)*p. Compare direct augmented exponential
    # with a quadrature of the step response on the full exterior.
    I=eye(3*n)
    G=bmat([[None, I],[-K,O]],format="csr")
    t=4*h
    stack=np.vstack([L,np.zeros_like(L)])
    ref=expm_multiply(t*G,stack,traceA=0.)
    rel=np.linalg.norm(sample-ref[:3*n])/np.linalg.norm(sample)
    p=np.array([.3,-.4,.5])
    bfield=np.r_[np.zeros(3*n),B@p][:,None]
    aux=csc_matrix(np.array([[0.,1.],[-1.,0.]]))
    forcing=csc_matrix(np.column_stack([bfield[:,0],np.zeros(6*n)]))
    aug=bmat([[G,forcing],[None,aux]],format="csr")
    direct=expm_multiply(t*aug,np.r_[np.zeros(6*n+1),1.],traceA=0.)[:3*n]
    def gauss(nodes):
        acc=np.zeros(3*n)
        for node,weight in zip(*np.polynomial.legendre.leggauss(nodes)):
            s=t*(node+1)/2
            u=expm_multiply((t-s)*G,stack@p,traceA=0.)[:3*n]
            acc+=t/2*weight*np.cos(s)*(L@p-u)
        return acc
    a=gauss(8);b=gauss(16)
    err=np.linalg.norm(b-direct)/np.linalg.norm(direct)
    assert err<1e-9 and rel<1e-10
    return np.maximum(envelope,np.concatenate([envelope[:1],envelope[:-1]])),ev,dict(
        H0=0.,resto_rel_paso=trunc,resto_energia=limit,residuo_L=residue,
        interpolacion_max=max(interp),deriva_gram=drift,exponencial_rel=rel,
        forzado_rel=err,cuadraturas_rel=np.linalg.norm(a-b)/np.linalg.norm(b))


def assess(record,kernel,ev,table):
    forces=np.array(record["fuentes"])
    dz=np.array([row["dz"] for row in record["filas"]])
    gamma=ex.moving_budget()["gamma"]
    op=np.sqrt(abs(ex.stiffness()).sum(axis=1).max())
    rows=[]
    all_cells=np.zeros((nc,4))
    limiting=None
    for j,r in enumerate(table):
        nobs=j+1
        boundary=.125*np.einsum("lij,l->ij",kernel[:nobs],dz[j::-1])
        # Cell conversion on interior faces of the corona. The inner Dirichlet
        # neighbor has prescribed zero for the independent volume problem.
        s=np.arange(nobs)/8
        front=100-s
        att=np.exp(-.1*np.maximum(np.array([40,60,160])[None,:]-front[:,None],0))
        fixed=np.array([[float(z[f"ajustada{k}"]) for k in range(3)] for z in table[:nobs]])
        extra=np.zeros_like(fixed)
        m=min(nobs,len(forces));extra[:m]=forces[:m,2:5]
        numerical=np.array([op*float(z["pos"])+float(z["vel"]) for z in table[:nobs]])
        weight=.125*np.exp(gamma*(nobs/8-s)/2)
        epres=weight@np.linalg.norm(att*fixed,axis=1)
        enon=weight@np.linalg.norm(att*extra,axis=1)
        enum=weight@numerical
        volume=ev*(epres+enon+enum)
        total=boundary+volume[:,None]
        all_cells=np.maximum(all_cells,np.column_stack([boundary,total]))
        i=int(np.argmax(total[:,0]))
        if limiting is None or total[i,0]>limiting["total"]:
            limiting=dict(t=nobs/8,r=ex.r[i],total=total[i,0],borde=boundary[i,0],
                          prescrita=ev[i]*epres,no_lineal_exterior=ev[i]*enon,
                          numerica=ev[i]*enum)
        rows.append([nobs/8,max(boundary[:,0]),max(boundary[:,1]),max(volume),
                     max(total[:,0]),max(total[:,1])])
    return dict(prefijo=record["prefijo"],maximos_por_celda=np.column_stack([ex.r[:nc],all_cells]).tolist(),
                maximo=limiting,filas=rows)


def main():
    data=json.loads((HERE/"contraccion.json").read_text())
    kernel,ev,diagnostics=compute()
    with gzip.open(ex.source,"rt") as f:
        rows=[r for r in csv.DictReader(f) if r["caso"]=="gota_a010"]
    result=dict(controles=diagnostics,maximo_nucleo=float(kernel.max()),
                columnas=["t","max_borde_canonico","max_borde_fisico","max_volumen","max_total_canonico","max_total_fisico"])
    for k in ("original","ampliado"):
        result[k]=assess(data[k],kernel,ev,rows)
    (HERE/"escalon.json").write_text(json.dumps(result,separators=(",",":"),allow_nan=False)+"\n")


if __name__=="__main__":
    main()
