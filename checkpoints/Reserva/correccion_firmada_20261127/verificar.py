"""Control interior con exponencial aumentada y derivada del polinomio."""
import csv
import ctypes
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from scipy.sparse import bmat,csr_matrix,diags
from scipy.sparse.linalg import expm_multiply
import medir_correccion as a

g,h,o=a.g,a.h,a.o
zero=np.zeros((g.n,3))
offset=o.affine(zero,zero)


def physical(x,v):
    q=x.copy();q[:,0]+=a.f;q[:,2]+=a.z
    acc=g.acceleration(q.T).T
    acc[:,0]+=a.om**2*q[:,0]+2*a.om*v[:,1]
    acc[:,1]+=a.om**2*q[:,1]-2*a.om*v[:,0]
    return acc


def check(case,step,march,G):
    x,p=a.loc.initial(case);X,V=x.copy(),p.copy()
    step(g.n,50,.0025,a.om,a.loc.c,X,V)
    b=np.stack([x,x+h*p/3,X-h*V/3,X])
    y,w,acc=a.bridge(b,.5)
    corrected=y.copy();vcorrected=w.copy();derivative=acc.copy()
    defects=[]
    for deg,temporal in ((3,True),(9,False)):
        values=a.sample(b,deg,temporal)
        # Referencia independiente con generador homogéneo y reloj polinómico.
        coeff=a.shift_matrix(deg,1,0)@values
        N=x.size
        force=csr_matrix(np.vstack((np.zeros((N,deg+1)),coeff.T/100)))
        clock=diags(np.arange(1,deg+1)/h,-1,shape=(deg+1,deg+1))
        big=bmat([[G[:-1,:-1],force],[None,clock]],format="csr")
        initial=np.zeros(big.shape[0]);initial[2*N]=1
        exact=expm_multiply(big*(h/2),initial,traceA=0.)
        solver=a.Forced(8,deg,22)
        for j in range(4):
            src=np.ascontiguousarray(solver.maps[j]@values)
            # Derivada en t=h/2 evaluada directamente a partir de coeficientes.
            if j==3:
                ax,av=solver.x.copy(),solver.v.copy()
                dvd=np.zeros_like(av)
                for k in range(22):
                    force_k=src[k].reshape(x.shape) if k<=deg else 0.
                    vel=o.affine(ax,av)-offset+force_k
                    dvd+=vel
                    fac=(h/8)/(k+1)
                    ax,av=fac*av,fac*vel
                derivative+=dvd
            outputs=[np.zeros_like(x) for _ in range(3)]
            march(g.n,deg,22,h/8,a.om,a.loc.c,src,solver.x,solver.v,solver.work,*outputs)
        defects.append([a.norm(solver.x-exact[:N].reshape(x.shape)),
                        a.norm(solver.v-100*exact[N:2*N].reshape(x.shape))])
        corrected+=solver.x;vcorrected+=solver.v
    residual=derivative-physical(corrected,vcorrected)
    identity=np.max(abs(residual-(a.rest(corrected)-a.rest(y))))
    assert max(max(pair) for pair in defects)<1e-8 and identity<1e-8
    return dict(errores_exponencial=defects,residuo_identidad_interior=identity)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        libs=[]
        for src in (a.ref.HERE/"tangente.c",a.HERE/"polinomio.c"):
            path=Path(tmp)/(src.stem+".so")
            subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",str(src),"-lm","-o",str(path)],check=True)
            libs.append(ctypes.CDLL(str(path)))
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        ci,cd=ctypes.c_int,ctypes.c_double
        step,march=libs[0].advance,libs[1].march
        step.argtypes=[ci,ci,cd,cd]+[ptr]*3
        march.argtypes=[ci,ci,ci,cd,cd]+[ptr]*8
        step.restype=march.restype=None
        G=a.generator()
        result={s:check(s,step,march,G) for s in ("gota_a010","gemelo","receptora")}
    (a.HERE/"control_interior.json").write_text(json.dumps(result,indent=2)+"\n")
    if (a.HERE/"series.csv").exists():
        summary=json.loads((a.HERE/"resultado.json").read_text())
        assert summary["sha_csv"]==a.ref.sha(a.HERE/"series.csv")
        with (a.HERE/"series.csv").open() as stream:
            rows=list(csv.DictReader(stream))
        assert len(rows)==960
        for i in range(3):
            assert [float(r["t"]) for r in rows[320*i:320*(i+1)]]==[(j+1)/8 for j in range(320)]
        for r in rows:
            for branch in ("1","2"):
                assert float(r["identidad"+branch+"_x"])<1e-8
                assert float(r["identidad"+branch+"_v"])<1e-7
            assert float(r["cambio_resto"])<=float(r["cota_cambio"])+1e-12
        for name in a.ref.NAMES:
            for tag in ("puente","corregida"):
                diffs=[]
                for j in range(7,320,8):
                    loaded,twin=rows[j],rows[j+320]
                    predicted=float(loaded[tag+"_"+name])-float(twin[tag+"_"+name])
                    archived=float(loaded["archivo_"+name])-float(twin["archivo_"+name])
                    diffs.append(abs(predicted-archived))
                assert abs(max(diffs)-summary["contraste_inventarios"][name][tag])<1e-15
    print(result)


if __name__=="__main__":
    main()
