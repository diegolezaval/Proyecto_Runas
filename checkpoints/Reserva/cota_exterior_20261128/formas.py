"""Conversión escalar con presupuestos no negativos y prueba LDL independiente."""
import json
import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import splu
from diagnostico import HERE,d,ext,work

weights=np.asarray(d.geometry()[0],np.longdouble)**2
r=d.g.r

def coefficient(band,extend,lam,alpha=0):
    """E_b² + α E_vecina² + λ X_b². Se descartan solo términos no negativos."""
    sl=d.bands[band]
    start=max(0,sl.start-extend)
    stop=min(d.g.n,sl.stop+extend)
    target=slice(sl.start-start,sl.stop-start)
    cut=slice(start,stop)
    k=weights[band,cut]+np.longdouble(alpha)*weights[3 if band==4 else 4,cut]
    m=d.o.W[cut].astype(np.longdouble)
    km=m*k
    f=4*np.longdouble(np.pi)*d.loc.face[cut]*np.r_[(k[1:]+k[:-1])/2,k[-1]]
    if stop<d.g.n:
        f[-1]=0
    left=np.r_[0,f[:-1]]
    potential=ext.floor*km
    potential[target]+=lam*m[target]
    dg=potential+f+left
    safe=dg-1e-8*km
    piv=safe.copy()
    ell=np.zeros_like(piv)
    for i in range(1,len(piv)):
        ell[i]=-f[i-1]/piv[i-1]
        piv[i]+=ell[i]*f[i-1]
    assert piv.min()>0
    err=abs(ell[1:]*piv[:-1]+f[:-1])
    residual=abs(piv+np.r_[0,ell[1:]**2*piv[:-1]]-safe)+np.r_[0,err]+np.r_[err,0]
    margin=min(1e-8*km-residual-128*np.finfo(float).eps*(dg+f+left))
    assert margin>0
    up=lambda a: np.nextafter(a,np.longdouble(np.inf))
    G=up(1/piv)
    for i in range(len(G)-2,-1,-1):
        G[i]=up(G[i]+up(up(ell[i+1]**2)*G[i+1]))
    co=np.asarray(np.sqrt(G),float)*(1+1e-12)
    b=np.asarray(m,float)
    ff=np.asarray(f,float)
    B=diags([-np.sqrt(ff/b),np.sqrt(ff[:-1]/b[1:])],[0,1],shape=(len(b),len(b)))
    K=(B.T@B+diags(np.asarray(potential/m,float))).tocsc()
    ids=np.unique([0,target.start,(target.start+target.stop)//2,target.stop-1,len(b)-1])
    rhs=np.zeros((len(b),len(ids)))
    rhs[ids,np.arange(len(ids))]=1
    sol=splu(K).solve(rhs)
    independent=np.sqrt(sol[ids,np.arange(len(ids))]/b[ids])
    assert np.all(independent<=co[ids]) and np.allclose(independent,co[ids],rtol=1e-7,atol=0)
    return co[target],float(margin)

def profile(band,params,budgets):
    X,E=np.asarray(budgets["X"]),np.asarray(budgets["E"])
    rb=r[d.bands[band]]
    profiles=[]
    margins=[]
    for extend,lam,alpha in params:
        c,margin=coefficient(band,extend,lam,alpha)
        b=np.sqrt(np.longdouble(E[band])**2+np.longdouble(alpha)*E[3 if band==4 else 4]**2+np.longdouble(lam)*X[band]**2)
        profiles.append(c*float(b)*(1+2e-12))
        margins.append(margin)
    arr=np.asarray(profiles)
    env=arr.min(axis=0)
    i=env.argmax()
    ix=arr[:,i].argmin()
    return env,dict(cota=float(env[i]),r=float(rb[i]),parametros=[float(v) for v in params[ix]],
                      margen=min(margins),n_formas=len(params))

def study(budgets):
    reports={}
    for band in (3,4):
        base=[(n,float(l),0.) for n in ([0] if band==3 else [0,80]) for l in ext.lambdas]
        env,old=profile(band,base,budgets)
        assert np.isclose(old["cota"],budgets["punto"][band],rtol=1e-9,atol=0)
        ladder=sorted(set([*ext.lambdas,*np.geomspace(.001,128.,29)]))
        extension=[(80,float(l),0.) for l in ext.lambdas]
        singles=[(n,float(l),0.) for n in (80,320) for l in ladder]
        mix=[(320,float(l),a) for a in (.0625,.25,1.,4.) for l in ladder[::2]]
        result={}
        for key,params in [("base",base),("extension_2",base+extension),
                          ("escalera_densa",base+singles),("formas_mixtas",base+singles+mix)]:
            _,result[key]=profile(band,params,budgets)
        reports[str(band)]=result
    return reports

if __name__=="__main__":
    result=study(json.loads((HERE/"entrada.json").read_text()))
    (HERE/"evaluacion.json").write_text(json.dumps(result,separators=(",",":"),allow_nan=False)+"\n")
    print(json.dumps(result,indent=2))
