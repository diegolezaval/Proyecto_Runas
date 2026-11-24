"""Comprobación separada con CSV estándar, trapecios por sumas compensadas y estados finales."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

AQUI=Path(__file__).resolve().parent
RAIZ=AQUI.parents[2]
sys.path.insert(0,str(RAIZ/"herramientas"))
from modelo_m2 import BENCHMARK as modelo


def digest(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def trap(val,a=200,b=240):
    return math.fsum((val[a]/2,*val[a+1:b],val[b]/2))/(b-a)


def cerca(a,b,tol=3e-15):
    if not math.isclose(a,b,rel_tol=1e-9,abs_tol=tol):
        raise AssertionError((a,b,tol))


def inventarios(p):
    with np.load(p,allow_pickle=False) as z:
        h,R=float(z["dx"]),float(z["R"])
        a,b,c=z["q"]
        va,vb,vc=z["v"]
        n=round(R/h)
        assert all(t.shape==(n,) for t in (a,b,c,va,vb,vc))
        rf=np.arange(n+1)*h
        w=np.diff(rf**3)/3
        H=w*(va**2+vb**2+.5*vc**2+modelo.potential(np.hypot(a,b),c))
        Q=w*(a*vb-b*va)
        caras=rf[1:-1]**2/h*(np.diff(a)**2+np.diff(b)**2+.5*np.diff(c)**2)
        pared=2*R**2/h*(a[-1]**2+b[-1]**2+.5*c[-1]**2)
        out={}
        for r,ks in [(R,("E","Q")),(40,("E40","Q40")),(60,("E60","Q60"))]:
            i=round(r/h)
            media_cara=pared if i==n else caras[i-1]/2
            out[ks[0]]=4*math.pi*math.fsum((math.fsum(H[:i]),math.fsum(caras[:i-1]),media_cara))
            out[ks[1]]=8*math.pi*math.fsum(Q[:i])
        return out


def verificar(lugar,resultados,con_estados):
    ejec=json.loads((lugar/"EJECUCION.json").read_text())
    resumen=json.loads((resultados/"RESULTADO.json").read_text())
    balances=json.loads((resultados/"BALANCES.json").read_text())
    test,rastro,err_estados={},[],[]
    for reg in ejec["series"]:
        m,c,v=reg["ruta"].split("/")
        p=lugar/reg["ruta"]/"serie.csv"
        assert digest(p)==reg["sha256_serie"]
        with p.open() as f:
            t=[{k:float(i) for k,i in row.items()} for row in csv.DictReader(f)]
        assert len(t)==241 and all(a["s"]==s and a["tau"]==300+s for s,a in enumerate(t))
        test[m,c,v]=t
        for r in (40,60):
            for k in ("E","Q"):
                e=max(abs(math.fsum((a[f"{k}{r}"]-t[0][f"{k}{r}"],a[f"F{k}{r}"],-a["W"] if k=="E" else 0.)))
                      for a in t)
                cerca(e,balances[m][c][v]["radios"][str(r)][k]["max_abs_cierre"])
        if con_estados:
            npz=p.with_name("s240.npz")
            assert digest(npz)==reg["sha256_estado"]
            inv=inventarios(npz)
            dist=max(abs(x-t[-1][nom]) for nom,x in inv.items())
            if dist>5e-10:
                raise AssertionError((npz,dist))
            err_estados.append(dist)
    if con_estados:
        for reg in ejec["preparaciones"]:
            assert digest(lugar/reg["archivo"])==reg["sha256"]
    nombres=("D","cargada","gemela")
    lecturas=0
    for r in (40,60):
        for k in ("E","Q"):
            cs={}
            for m in ejec["mallas"]:
                por_caso={}
                for c in ("cargada","gemela"):
                    on,off=(test[m,c,v] for v in ("encendida","apagada"))
                    y=[math.fsum((a[f"F{k}{r}"],-b[f"F{k}{r}"],-a["W"] if k=="E" else 0.,
                                  b["W"] if k=="E" else 0.)) for a,b in zip(on,off)]
                    por_caso[c]=y
                por_caso["D"]=[a-b for a,b in zip(por_caso["cargada"],por_caso["gemela"])]
                cs[m]=por_caso
                for n in nombres:
                    cerca(trap(cs[m][n]),resumen["lecturas"][str(r)][k][n]["medias_de_saldo_por_replica"][m])
                    lecturas+=1
            for n in nombres:
                xx=cs["principal"][n]
                medios={m:trap(t[n]) for m,t in cs.items()}
                principal=medios["principal"]
                ac=resumen["lecturas"][str(r)][k][n]
                for a,b in ((200,240),(200,220),(220,240)):
                    cerca(trap(xx,a,b),ac["principales"]["saldo"]["ventanas"][f"{a}-{b}"])
                ramas=(n,) if n!="D" else ("cargada","gemela")
                cierre=math.fsum(balances["principal"][c][v]["radios"][str(r)][k]["max_abs_cierre"]
                                  for c in ramas for v in ("encendida","apagada"))
                # Las lecturas por inventario y de prearribo se comprueban a partir de cada muestra.
                iv=[]
                for s in range(241):
                    vals=[]
                    for c in ramas:
                        on,off=(test["principal",c,v] for v in ("encendida","apagada"))
                        col=f"{k}{r}"
                        vals.append((off[s][col]-off[0][col])-(on[s][col]-on[0][col]))
                    iv.append(vals[0] if len(vals)==1 else vals[0]-vals[1])
                pre=[]
                for m in ("principal","temporal","espacial","caja416"):
                    for s in range((30 if r==40 else 50)+1):
                        par=[test[m,c,"encendida"][s][f"F{k}{r}"]-test[m,c,"apagada"][s][f"F{k}{r}"] for c in ramas]
                        pre.append(abs(par[0] if len(par)==1 else par[0]-par[1]))
                u=max(abs(medios["espacial"]-medios["temporal"]),abs(medios["temporal"]-principal),
                      abs(medios["caja416"]-principal),abs(trap(xx,200,220)-principal),
                      abs(trap(xx,220,240)-principal),cierre,max(abs(x-i) for x,i in zip(xx,iv)),max(pre),1e-10)
                cerca(u,ac["U"])
                cerca(principal+3*u,ac["intervalo_sensibilidad"][1])
                rastro.append([r,k,n,principal,u])
    return dict(series_verificadas=len(test),muestras_por_serie=241,medias_de_replica_cotejadas=lecturas,
                sensibilidades_reconstruidas=len(rastro),cierres_por_trayectoria_cotejados=4*len(test),
                estados_finales_cotejados=len(err_estados),
                maxima_diferencia_de_inventario_con_suma_compensada=max(err_estados,default=None),
                estados_iniciales_amplios_cotejados=len(ejec["preparaciones"]) if con_estados else 0,
                huellas_de_informes={n:digest(resultados/n) for n in ("RESULTADO.json","PARED.json","BALANCES.json","CONTRASTES.csv")})


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos",type=Path,nargs="?",default=AQUI/"datos")
    p.add_argument("--resultados",type=Path,default=AQUI)
    p.add_argument("--estados",action="store_true",help="Coteja también los 26 estados y remide los 20 finales")
    p.add_argument("--recibo",type=Path)
    args=p.parse_args()
    info=verificar(args.datos,args.resultados,args.estados)
    txt=json.dumps(info,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    if args.recibo:
        args.recibo.write_text(txt)
    print(txt,end="")
