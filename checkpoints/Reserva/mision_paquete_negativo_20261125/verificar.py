"""Verifica las lecturas por sumas compensadas y la conversión mediante DFT y solve de dos sondas."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

AQUI=Path(__file__).resolve().parent
sys.path.insert(0,str(AQUI.parents[2]/"herramientas"))
from modelo_m2 import BENCHMARK as modelo

def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def tabla(p):
    with p.open() as f:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]


def media(x,a=400,b=480):
    return math.fsum([x[a]/2,*x[a+1:b],x[b]/2])/(b-a)


def igual(x,y,tol=2e-14):
    if not math.isclose(x,y,rel_tol=1e-9,abs_tol=tol):
        raise ValueError((x,y,tol))


def estado(p):
    with np.load(p,allow_pickle=False) as z:
        R,h=float(z["R"]),float(z["h"])
        a,b,c=z["q"];va,vb,vc=z["v"]
    rf=np.arange(round(R/h)+1)*h
    w=np.diff(rf**3)/3
    cell=w*(va*va+vb*vb+.5*vc*vc+modelo.potential(np.hypot(a,b),c))
    charge=w*(a*vb-b*va)
    faces=(rf[1:-1]**2/h)*(np.diff(a)**2+np.diff(b)**2+.5*np.diff(c)**2)
    out={}
    for r in (R,40,60):
        i=round(r/h)
        last=2*R**2/h*(a[-1]**2+b[-1]**2+.5*c[-1]**2) if r==R else faces[i-1]/2
        su="" if r==R else str(r)
        out["E"+su]=4*np.pi*math.fsum((math.fsum(cell[:i]),math.fsum(faces[:i-1]),last))
        out["Q"+su]=8*np.pi*math.fsum(charge[:i])
    return out


def bandas_dft(a,b,r,tag,h,dt,ds,T):
    # Evalúa sólo las frecuencias de la banda con las sumas explícitas de Fourier.
    # Las amplitudes normalizadas en el centro de la cara se obtienen por dos ecuaciones complejas.
    n=round(T/ds)
    t=np.arange(n)*ds
    muestras=slice(0,4*T,round(ds/.25))
    y=[]
    for side,rad in (("i",r-h/2),("e",r+h/2)):
        re,im=f"Re{r}{side}",f"Im{r}{side}"
        d=a[re][muestras]+1j*a[im][muestras]
        if b is not None:
            d=d-(b[re][muestras]+1j*b[im][muestras])
        edge=np.clip(np.minimum(t,T-t)/12,0,1)
        y.append(rad*d*(.5-.5*np.cos(np.pi*edge)))
    lo,hi=(-1.85,-1.02) if tag=="negativa" else (2.82,3.65)
    nu=np.arange(math.ceil(lo*T/(2*np.pi)),math.floor(hi*T/(2*np.pi))+1)*2*np.pi/T
    hats=np.exp(-1j*nu[:,None]*t)@np.asarray(y).T
    half=np.arcsin(h*np.sqrt((2*np.sin(nu*dt/2)/dt)**2-modelo.mass2)/2)
    e=np.exp(1j*np.sign(nu)*half)
    mats=np.zeros((len(nu),2,2),complex)
    mats[:,0,0],mats[:,0,1]=1/e,e
    mats[:,1,0],mats[:,1,1]=e,1/e
    io=np.linalg.solve(mats,hats[...,None])[...,0]
    factor=np.sign(nu)*8*np.pi*r*r/(r*r-h*h/4)*ds/(n*h)*np.sin(2*half)
    qi,qo=-factor*abs(io[:,0])**2,factor*abs(io[:,1])**2
    vel=np.sin(nu*dt)/dt
    eo=math.fsum(qo*vel)
    return dict(E_entrada=math.fsum(qi*vel),E_salida=eo,Q_entrada=math.fsum(qi),
                Q_salida=math.fsum(qo),centro_salida=math.fsum(nu*qo*vel)/eo)


def verificar_espectros(ej,ds,son,spec,umbrales):
    mallas=("principal","temporal","espacial","caja576")
    calculo={}
    nflujo=ncob=npuerta=0
    for m in mallas:
        _,h,dt,_=ej["mallas"][m]
        for r in (40,60):
            cob=spec["cobertura"][str(r)][m]
            vacio=ds[m,"vacio"]
            for c in ("gemela","cargada","vacio"):
                a=son[m,"vacio"] if c=="vacio" else son[m,c+"_con"]
                b=None if c=="vacio" else son[m,c+"_sin"]
                for obs,T,paso in (("lectura",480,.25),("corte440",440,.25),("cadencia05",480,.5)):
                    for tag in ("positiva","negativa"):
                        valores=bandas_dft(a,b,r,tag,h,dt,paso,T)
                        calculo[m,r,c,obs,tag]=valores
                        ref=spec["lecturas"][m][str(r)][c][obs][tag]
                        for nombre in ("E_entrada","E_salida","Q_entrada","Q_salida"):
                            igual(valores[nombre],ref[nombre],3e-13)
                            nflujo+=1
                        if c!="vacio" or tag=="negativa":
                            igual(valores["centro_salida"],ref["centro_salida"],2e-9)
            for k in ("E","Q"):
                resid=max(abs(row[f"F{k}{r}"]) for row in vacio[400:481])
                assert (resid < .1*umbrales[k]) == cob["vacio_residual_"+k]["pasa"]
                ncob+=1
            for flujo in ("E_entrada","E_salida"):
                energia=abs(calculo[m,r,"vacio","lectura","negativa"][flujo])
                assert (abs(energia/vacio[0]["E"]-1)<=.005) == cob["vacio_"+flujo]["pasa"]
                ncob+=1
            for c in ("cargada","gemela"):
                for tag,flujo in (("negativa","E_entrada"),("negativa","E_salida"),("positiva","E_salida")):
                    y=calculo[m,r,c,"lectura",tag][flujo]
                    y440=calculo[m,r,c,"corte440",tag][flujo]
                    admisible=max(.0025*abs(y),.05*umbrales["E"])
                    ref=cob["_".join((c,tag,flujo))]
                    igual(abs(y-y440),ref["cambio"],3e-13)
                    assert (abs(y-y440)<=admisible)==ref["pasa"]
                    ncob+=1
    for r in (40,60):
        for c in ("cargada","gemela"):
            for k in ("E","Q"):
                flujo=k+"_salida"
                def salida(m,obs="lectura"):
                    return calculo[m,r,c,obs,"positiva"][flujo]
                principal=calculo["principal",r,c,"lectura","positiva"]
                y=principal[flujo]
                entrada=abs(principal[k+"_entrada"])
                vac=abs(calculo["principal",r,"vacio","lectura","positiva"][flujo])
                u=max(1e-10,abs(salida("espacial")-salida("temporal")),
                      abs(y-salida("temporal")),abs(y-salida("caja576")))
                for m in mallas:
                    u=max(u,abs(salida(m)-salida(m,"corte440")),abs(salida(m)-salida(m,"cadencia05")),
                          abs(calculo[m,r,c,"lectura","positiva"][k+"_entrada"]),
                          abs(calculo[m,r,"vacio","lectura","positiva"][flujo]))
                puerta=spec["conversion"][str(r)][c][k]
                igual(u,puerta["U"],3e-13)
                assert (y-vac>3*u and y>entrada and 2.82<=principal["centro_salida"]<=3.65)==puerta["detectada"]
                npuerta+=1
    return nflujo,ncob,npuerta


def verificar(root,resultados,campos=False):
    ej=json.loads((root/"EJECUCION.json").read_text())
    res=json.loads((resultados/"RESULTADO.json").read_text())
    spec=json.loads((resultados/"BANDAS.json").read_text())
    ds,son={},{}
    max_estado=0.
    for reg in ej["series"]:
        m,c=reg["replica"],reg["caso"]
        d=root/m/c
        assert sha(d/"serie.csv")==reg["sha256_serie"] and sha(d/"sondas.csv")==reg["sha256_sondas"]
        ds[m,c]=tabla(d/"serie.csv")
        if m!="archivo416":
            son[m,c]=np.genfromtxt(d/"sondas.csv",names=True,delimiter=",")
        if campos:
            p=d/f"s{reg['fin_s']}.npz"
            assert sha(p)==reg["sha256_estado_final"]
            last=ds[m,c][-1]
            dif=max(abs(last[k]-v) for k,v in estado(p).items())
            max_estado=max(max_estado,dif)
            assert dif<5e-10
    ver_m,ver_u=0,0
    ms=("espacial","temporal","principal","caja576")
    for r in (40,60):
        for k in ("E","Q"):
            col=f"{k}{r}"
            for caso in ("cargada","gemela","D"):
                ramas=("cargada","gemela") if caso=="D" else (caso,)
                curvas,pre,tot={},0.,0.
                desacuerdos = {}
                for m in ms:
                    listas=[];invs=[]
                    for c in ramas:
                        on,off=(ds[m,c+su] for su in ("_con","_sin"))
                        listas.append([a["F"+col]-b["F"+col] for a,b in zip(on,off)])
                        invs.append([math.fsum((b[col]-off[0][col],-(a[col]-on[0][col]))) for a,b in zip(on,off)])
                        if m=="principal":
                            for rama in (on,off):
                                tot+=max(abs(math.fsum((e[col]-rama[0][col],e["F"+col]))) for e in rama)
                    x=listas[0] if len(ramas)==1 else [a-b for a,b in zip(*listas)]
                    inv=invs[0] if len(ramas)==1 else [a-b for a,b in zip(*invs)]
                    desacuerdos[m]=max(abs(a-b) for a,b in zip(x,inv))
                    pre=max(pre,max(abs(v) for v in x[:(51 if r==40 else 31)]))
                    curvas[m]=x
                    entry=res["mediciones"][str(r)][k][caso]
                    for i,(a,b) in enumerate(((400,480),(400,440),(440,480))):
                        igual(media(x,a,b),entry["ventanas"][m][i])
                        ver_m+=1
                y=media(curvas["principal"])
                est={m:media(x) for m,x in curvas.items()}
                u=max(abs(est["temporal"]-est["espacial"]),abs(y-est["temporal"]),abs(y-est["caja576"]),
                      abs(y-media(curvas["principal"],400,440)),abs(y-media(curvas["principal"],440,480)),
                      tot,desacuerdos["principal"],pre,1e-10)
                if caso!="D":
                    u=max(u,max(abs(row["F"+col]) for row in ds["principal","vacio"][400:481]))
                igual(u,entry["U_con_mitades_y_desacuerdo_solo_en_principal"])
                diferencias_de_mitad = [abs(media(x,a,b)-est[m]) for m,x in curvas.items()
                                        for a,b in ((400,440),(440,480))]
                u=max(u,*desacuerdos.values(),*diferencias_de_mitad)
                igual(u,entry["U"]);igual(y+3*u,entry["superior"]);ver_u+=1
    ver_b,ncob,npuerta=verificar_espectros(ej,ds,son,spec,res["umbrales"])
    return dict(series_y_sondas_cotejadas=2*len(ds),medias_independientes=ver_m,
                sensibilidades_reconstruidas=ver_u,flujos_de_banda_reconstruidos_por_DFT=ver_b,
                controles_de_cobertura_verificados=ncob,criterios_de_conversion_verificados=npuerta,
                estados_finales_remedidos=len(ds) if campos else 0,max_abs_inventarios_independientes=max_estado if campos else None,
                sha256={n:sha(resultados/n) for n in ("RESULTADO.json","BALANCES.json","BANDAS.json","ESPECTRO.csv")})


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos",type=Path,nargs="?",default=AQUI/"datos")
    p.add_argument("--resultados",type=Path,default=AQUI)
    p.add_argument("--campos",action="store_true")
    p.add_argument("--recibo",type=Path)
    a=p.parse_args()
    j=json.dumps(verificar(a.datos,a.resultados,a.campos),indent=2,allow_nan=False)+"\n"
    if a.recibo:
        a.recibo.write_text(j)
    print(j,end="")
