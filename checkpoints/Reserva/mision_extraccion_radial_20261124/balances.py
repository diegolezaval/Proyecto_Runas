"""Reconstruye balances, efecto de la pared y decisión con las series de la misión."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

AQUI=Path(__file__).resolve().parent
PASO3=AQUI.parent/"paso3_20261118"
MALLAS=("historica","principal","temporal","espacial","caja416")
LIMPIAS=MALLAS[1:]
CASOS=("cargada","gemela")
VARIANTES=("encendida","apagada")
RADIOS=(40,60)
CANALES=("E","Q")
SALDOS=(*CASOS,"D")
VENTANAS=((200,240),(200,220),(220,240))
PISO=1e-10
S=np.arange(241)
COLUMNAS="s tau E Q E40 Q40 E60 Q60 FE40 FQ40 FE60 FQ60 W".split()


def guardar(p,data):
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n")


def lectura(p):
    return json.loads(p.read_text())


def media(x,a=200,b=240):
    return float(np.trapezoid(x[a:b+1],x=S[a:b+1])/(b-a))


def delta(x):
    return x-x[0]


def maxabs(x):
    return float(np.max(np.abs(x)))


def resumir(x):
    return dict(ventanas={f"{a}-{b}":media(x,a,b) for a,b in VENTANAS},s240=float(x[-1]))


def series(ruta):
    ej=lectura(ruta/"EJECUCION.json")
    fichas={t["ruta"]:t for t in ej["series"]}
    if len(fichas)!=20 or len(ej["series"])!=20:
        raise ValueError("Se esperaban cinco réplicas de cuatro casos")
    datos={}
    for m in MALLAS:
        datos[m]={}
        for caso in CASOS:
            ramas={}
            for v in VARIANTES:
                rel=f"{m}/{caso}/{v}"
                p=ruta/rel/"serie.csv"
                if hashlib.sha256(p.read_bytes()).hexdigest()!=fichas[rel]["sha256_serie"]:
                    raise ValueError(f"SHA-256 incorrecto en {p}")
                arr=np.genfromtxt(p,delimiter=",",names=True)
                if list(arr.dtype.names)!=COLUMNAS or not np.array_equal(arr["s"],S) or not np.array_equal(arr["tau"],300+S):
                    raise ValueError(f"Cabecera o muestreo incorrectos en {p}")
                if not all(np.isfinite(arr[k]).all() for k in COLUMNAS):
                    raise ValueError(f"No finito en {p}")
                if any(arr[k][0]!=0 for k in ("W","FE40","FQ40","FE60","FQ60")):
                    raise ValueError(f"Integrales iniciales en {p}")
                if not np.all(arr["W"][8:]==arr["W"][8]) or (v=="apagada" and np.any(arr["W"])):
                    raise ValueError(f"Fuente fuera de ventana en {p}")
                ramas[v]=arr
            if any(ramas["encendida"][k][0]!=ramas["apagada"][k][0] for k in COLUMNAS):
                raise ValueError(f"Datos iniciales distintos en {m}/{caso}")
            datos[m][caso]=ramas
    return datos


def balances_rama(a):
    b={"trabajo":resumir(a["W"]),"global":{},"radios":{},"corona_40_60":{}}
    for k in CANALES:
        w=a["W"] if k=="E" else 0.
        eg=delta(a[k])-w
        b["global"][k]=dict(max_abs=maxabs(eg),final=float(eg[-1]))
        anillo=a[k+"60"]-a[k+"40"]
        er=delta(anillo)+a["F"+k+"60"]-a["F"+k+"40"]
        b["corona_40_60"][k]=dict(max_abs=maxabs(er),final=float(er[-1]),
                                 cambio_inventario=resumir(delta(anillo)))
        for r in RADIOS:
            interior=a[f"{k}{r}"]
            flujo=a[f"F{k}{r}"]
            err=delta(interior)+flujo-w
            b["radios"].setdefault(str(r),{})[k]=dict(inventario_inicial=float(interior[0]),
                cambio_inventario=resumir(delta(interior)),flujo_neto=resumir(flujo),
                max_abs_cierre=maxabs(err),cierre_final=float(err[-1]))
    return b


def curvas(datos,r,k):
    etiqueta=f"{k}{r}"
    salida={}
    for m,pares in datos.items():
        resp={}
        for c in CASOS:
            on,off=(pares[c][v] for v in VARIANTES)
            bruto=on["F"+etiqueta]-off["F"+etiqueta]
            trabajo=on["W"]-off["W"] if k=="E" else np.zeros(len(S))
            inv=-(delta(on[etiqueta])-delta(off[etiqueta]))
            resp[c]=dict(flujo_bruto=bruto,trabajo=trabajo,saldo=bruto-trabajo,por_inventario=inv)
        resp["D"]={n:resp["cargada"][n]-resp["gemela"][n] for n in resp["cargada"]}
        salida[m]=resp
    return salida


def incertidumbre(cs,b,r,k,nombre,stock):
    fuentes=CASOS if nombre=="D" else (nombre,)
    x=cs["principal"][nombre]["saldo"]
    t=media(x)
    m={m:media(v[nombre]["saldo"]) for m,v in cs.items()}
    fin_pre={40:30,60:50}[r]
    componentes={
        "espacio":abs(m["temporal"]-m["espacial"]),
        "tiempo":abs(t-m["temporal"]),
        "cajas_limpias":abs(t-m["caja416"]),
        "media_200_220":abs(t-media(x,200,220)),
        "media_220_240":abs(t-media(x,220,240)),
        "suma_maximos_cierre_de_ramas":sum(b["principal"][c][v]["radios"][str(r)][k]["max_abs_cierre"]
                                          for c in fuentes for v in VARIANTES),
        "flujo_frente_a_inventario":maxabs(x-cs["principal"][nombre]["por_inventario"]),
        "control_prearribo_de_flujo_bruto":max(maxabs(cs[m][nombre]["flujo_bruto"][:fin_pre+1]) for m in LIMPIAS),
        "piso":PISO}
    u=max(componentes.values())
    return dict(media=t,U=u,tres_U=3*u,componentes=componentes,componente_maxima=max(componentes,key=componentes.get),
                intervalo_sensibilidad=[t-3*u,t+3*u],limite_positivo=max(0.,t+3*u),
                limite_magnitud=abs(t)+3*u,limite_positivo_fraccion_stock=max(0.,t+3*u)/stock,
                limite_magnitud_fraccion_stock=(abs(t)+3*u)/stock,
                medias_de_saldo_por_replica=m,
                principales={n:resumir(y) for n,y in cs["principal"][nombre].items()})


def efecto_pared(datos,cs,r,k):
    pared={"flujos_por_rama":{},"contrastes":{}}
    def comparar(x,y):
        d=x-y
        cruces=np.flatnonzero(np.abs(d)>PISO)
        return dict(R256_media=media(x),R384_media=media(y),diferencia_media=media(d),
                    max_abs=maxabs(d),s_del_maximo=int(np.argmax(np.abs(d))),
                    primera_muestra_abs_mayor_1e_10=int(cruces[0]) if len(cruces) else None,
                    hitos={str(s):float(d[s]) for s in (0,8,28,34,54,100,160,200,240)})
    for c in CASOS:
        pared["flujos_por_rama"][c]={v:comparar(datos["historica"][c][v][f"F{k}{r}"],
                                                 datos["principal"][c][v][f"F{k}{r}"]) for v in VARIANTES}
    for n in SALDOS:
        pared["contrastes"][n]={cant:comparar(cs["historica"][n][cant],cs["principal"][n][cant])
                                for cant in ("flujo_bruto","saldo")}
    return pared


def tabla_curvas(p,todos):
    with p.open("w",newline="") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(["replica","r","canal","s",*[n+"_"+a for n in SALDOS for a in
                   ("flujo_bruto","trabajo","saldo","por_inventario")]])
        for (r,k),cs in todos.items():
            for m in MALLAS:
                for s in S:
                    w.writerow([m,r,k,s,*[format(x[s],".17g") for n in SALDOS for x in cs[m][n].values()]])


def analizar(datos,dest):
    dest.mkdir(parents=True,exist_ok=True)
    b={m:{c:{v:balances_rama(a) for v,a in ramas.items()} for c,ramas in pares.items()} for m,pares in datos.items()}
    ret=lectura(PASO3/"RETENCION.json")["paso_temporal"]["dt0005"]
    stock={k:ret[k]["por_radio"]["40"]["inventario_300"] for k in CANALES}
    todos,medidas,frontera,decision={},{},{},{}
    for r in RADIOS:
        medidas[str(r)],frontera[str(r)]={},{}
        ver={}
        for k in CANALES:
            cs=curvas(datos,r,k)
            todos[r,k]=cs
            vals={n:incertidumbre(cs,b,r,k,n,stock[k]) for n in SALDOS}
            medidas[str(r)][k]=vals
            pared=efecto_pared(datos,cs,r,k)
            pared["diferencia_D_en_unidades_de_U_limpia"]=abs(pared["contrastes"]["D"]["saldo"]["diferencia_media"])/vals["D"]["U"]
            frontera[str(r)][k]=pared
            inf=min(vals[n]["intervalo_sensibilidad"][0] for n in ("D","cargada"))
            ver[k]=dict(umbral=.01*stock[k],D_positivo=bool(vals["D"]["intervalo_sensibilidad"][0]>0),
                        salida_positiva_resuelta=bool(inf>0),supera_uno_por_ciento=bool(inf>.01*stock[k]),
                        D_excluye_uno_por_ciento=bool(vals["D"]["limite_positivo"]<.01*stock[k]))
        decision[str(r)]=dict(por_canal=ver,salida_conjunta_resuelta=all(v["salida_positiva_resuelta"] for v in ver.values()),
                              conjunta_supera_uno_por_ciento=all(v["supera_uno_por_ciento"] for v in ver.values()))
    guardar(dest/"BALANCES.json",b)
    guardar(dest/"PARED.json",frontera)
    guardar(dest/"RESULTADO.json",dict(ventana_s=[200,240],ventana_tau=[500,540],unidad="M2 normalizada",
        stock_tau300=stock,lecturas=medidas,decision=decision,primera_entrega_util_a_receptora=False,
        recarga_habilitada=False,segunda_descarga_habilitada=False))
    tabla_curvas(dest/"CONTRASTES.csv",todos)
    return todos


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos",type=Path,nargs="?",default=AQUI/"datos")
    p.add_argument("--salida",type=Path,default=AQUI)
    args=p.parse_args()
    analizar(series(args.datos),args.salida)
