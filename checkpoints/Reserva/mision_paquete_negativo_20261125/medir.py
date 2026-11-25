"""Lee las series de inventario y las trazas complejas y aplica el prerregistro."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

from diseno import AQUI, BNEG, BPOS, OMEGA, model

CASOS=("cargada_con","cargada_sin","gemela_con","gemela_sin","vacio")
GOTAS=("cargada","gemela")
MALLAS=("espacial","temporal","principal","caja576")
CANALES=("E","Q")
RADIOS=(40,60)
LECTURA=(400,480)
MITADES=((400,440),(440,480))
PISO=1e-10


def dump(p,d):
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+"\n")


def media(x,a=400,b=480):
    return float(np.trapezoid(x[a:b+1])/(b-a))


def maxabs(x):
    return float(np.max(np.abs(x)))


def leer_series(ruta):
    ej=json.loads((ruta/"EJECUCION.json").read_text())
    datos,sondas={},{}
    if len(ej["series"])!=25 or len({(x["replica"],x["caso"]) for x in ej["series"]})!=25:
        raise ValueError("Cobertura de casos")
    for reg in ej["series"]:
        m,c=reg["replica"],reg["caso"]
        T=ej["mallas"][m][3]
        for nombre,sha,paso,contenedor in (("serie",reg["sha256_serie"],1,datos),("sondas",reg["sha256_sondas"],.25,sondas)):
            p=ruta/m/c/(nombre+".csv")
            if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
                raise ValueError(f"Huella de {p}")
            arr=np.genfromtxt(p,delimiter=",",names=True)
            if not np.array_equal(arr["s"],np.arange(round(T/paso)+1)*paso) or not np.isfinite(arr.view(np.float64)).all():
                raise ValueError(f"Muestreo o dato en {p}")
            contenedor.setdefault(m,{})[c]=arr
    for m,ds in datos.items():
        for c,d in ds.items():
            if (not np.array_equal(d["tau"],300+d["s"]) or np.any(d["W"]) or
                any(d[n][0]!=0 for n in ("FE40","FQ40","FE60","FQ60"))):
                raise ValueError(f"Reloj, trabajo o integrales de {m}/{c}")
        for c in GOTAS:
            for k in ("E40","E60","Q40","Q60"):
                if ds[c+"_con"][k][0]!=ds[c+"_sin"][k][0]:
                    raise ValueError(f"Inventarios iniciales {m}/{c}/{k}")
    return ej,datos,sondas


def analizar_flujo(datos,dis):
    presupuesto,balances={},{}
    for m,ds in datos.items():
        presupuesto[m],balances[m]={},{}
        for c in GOTAS:
            y={}
            for k in CANALES:
                a=ds[c+"_con"][k][0]-ds[c+"_sin"][k][0]
                vac=ds["vacio"][k][0]
                y[k]=dict(incremento_superpuesto=float(a),paquete_aislado=float(vac),cruzado=float(a-vac))
            presupuesto[m][c]=y
        for n,a in ds.items():
            errores={}
            for k in CANALES:
                g=a[k]-a[k][0]
                errores["global_"+k]=maxabs(g)
                for r in RADIOS:
                    col=f"{k}{r}"
                    err=a[col]-a[col][0]+a["F"+col]
                    errores[col]=maxabs(err)
                change=(a[k+"60"]-a[k+"60"][0])-(a[k+"40"]-a[k+"40"][0])
                errores["corona_"+k]=maxabs(change+a["F"+k+"60"]-a["F"+k+"40"])
            balances[m][n]=dict(max_abs_cierre=errores,inventario_inicial={k:float(a[k][0]) for k in ("E","Q","E40","Q40","E60","Q60")},
                final={k:float(a[k][-1]) for k in a.dtype.names if k not in ("s","tau")})
            if m in MALLAS:
                balances[m][n]["ventana_400_480"] = {
                    col: {"flujo_bruto": media(a["F"+col]),
                          "perdida_de_inventario": media(a[col][0]-a[col])}
                    for col in ("E40", "Q40", "E60", "Q60")
                }
    medidas={}
    compara={}
    for r in RADIOS:
        medidas[str(r)],compara[str(r)]={},{}
        for k in CANALES:
            col=f"{k}{r}"
            X,inv={},{}
            for m,ds in datos.items():
                X[m],inv[m]={},{}
                for c in GOTAS:
                    h,l=ds[c+"_con"],ds[c+"_sin"]
                    X[m][c]=h["F"+col]-l["F"+col]
                    inv[m][c]=(l[col]-l[col][0])-(h[col]-h[col][0])
                X[m]["D"]=X[m]["cargada"]-X[m]["gemela"]
                inv[m]["D"]=inv[m]["cargada"]-inv[m]["gemela"]
            salida,cmp={},{}
            for n in (*GOTAS,"D"):
                x=X["principal"][n]
                med={m:media(X[m][n]) for m in MALLAS}
                y=med["principal"]
                usadas=GOTAS if n=="D" else (n,)
                v=dict(espacio=abs(med["temporal"]-med["espacial"]),tiempo=abs(y-med["temporal"]),
                       caja=abs(y-med["caja576"]),
                       mitad_400_440=abs(y-media(x,*MITADES[0])),mitad_440_480=abs(y-media(x,*MITADES[1])),
                       suma_cierres=sum(balances["principal"][c+v]["max_abs_cierre"][col] for c in usadas for v in ("_con","_sin")),
                       contraste_flujo_inventario=maxabs(x-inv["principal"][n]),
                       antes_llegada=max(maxabs(X[m][n][:(51 if r==40 else 31)]) for m in MALLAS),
                       piso=PISO)
                if n!="D":
                    v["vacio_residual"]=maxabs(datos["principal"]["vacio"]["F"+col][400:481])
                u_principal = max(v.values())
                # Para los controles puntuales y las mitades se conservan también
                # los valores de cada réplica y se toma la envolvente más amplia.
                por_replica = {}
                for m in MALLAS:
                    curva = X[m][n]
                    por_replica[m] = {
                        "mitad_400_440": abs(media(curva, *MITADES[0])-med[m]),
                        "mitad_440_480": abs(media(curva, *MITADES[1])-med[m]),
                        "contraste_flujo_inventario": maxabs(curva-inv[m][n])
                    }
                for componente in por_replica["principal"]:
                    v[componente] = max(valores[componente] for valores in por_replica.values())
                u=max(v.values())
                stock=dis["stock"][k]
                salida[n]=dict(Y_o_D=y,U=u,tres_U=3*u,inferior=y-3*u,superior=y+3*u,
                    maximo_adicional_positivo=max(0.,y+3*u),limite_de_magnitud=abs(y)+3*u,
                    maximo_positivo_fraccion_stock=max(0.,y+3*u)/stock,
                    limite_magnitud_fraccion_stock=(abs(y)+3*u)/stock,
                    fraccion_stock=y/stock,domina=max(v,key=v.get),componentes=v,
                    controles_por_replica=por_replica,
                    U_con_mitades_y_desacuerdo_solo_en_principal=u_principal,
                    por_inventario=media(inv["principal"][n]),valor_s480=float(x[-1]),
                    ventanas={m:[media(X[m][n],*ab) for ab in (LECTURA,*MITADES)] for m in MALLAS})
                dif=X["archivo416"][n]-x[:301]
                cmp[n]=dict(max_abs_s0_300=maxabs(dif),en_s300=float(dif[-1]))
            medidas[str(r)][k]=salida
            compara[str(r)][k]=cmp
    return presupuesto,balances,medidas,compara


def pares_de_cara(s,r,h):
    def canal(a):
        return s[f"Re{r}{a}"]+1j*s[f"Im{r}{a}"]
    return np.stack(((r-h/2)*canal("i"),(r+h/2)*canal("e")))


def dispersion_sonda(z,r,h,dt,T,paso=.25,tiempos=None):
    # w = r Phi en las dos celdas. FFT positiva corresponde a exp(+i*nu*t).
    n=round(T/paso)
    z=z[:, :4*T:round(paso/.25)]
    if z.shape!=(2,n):
        raise ValueError("Tamaño temporal de sonda")
    t=np.arange(n)*paso
    taper=np.sin(.5*np.pi*np.clip(np.minimum(t,T-t)/12,0.,1.))**2
    iz,der=np.fft.fft(z*taper,axis=1)
    nu=2*np.pi*np.fft.fftfreq(n,paso)
    nu_c=2*np.sin(nu*dt/2)/dt
    k2=nu_c**2-model.mass2
    # Sólo los modos propagantes tienen dos direcciones. En Nyquist el signo
    # temporal se pliega y la descomposición direccional sería ambigua.
    mask=(k2>0)&(h*h*k2<4)&(abs(nu)<np.pi/paso)
    nu=nu[mask]
    ang=2*np.arcsin(h*np.sqrt(nu_c[mask]**2-model.mass2)/2)
    iz,der=iz[mask],der[mask]
    suma=(der+iz)/(2*np.cos(ang/2))
    resta=(der-iz)/(2j*np.sign(nu)*np.sin(ang/2))
    inc,sal=(suma+resta)/2,(suma-resta)/2
    fac=8*np.pi*r**2/(r**2-h**2/4)/h*paso/n
    base=fac*np.sin(ang)*np.sign(nu)
    qi,qo=-base*abs(inc)**2,base*abs(sal)**2
    directo=-fac*np.imag(iz.conj()*der)
    np.testing.assert_allclose(qi+qo,directo,rtol=4e-12,atol=2e-15)
    velocidad_t=np.sin(nu*dt)/dt
    if tiempos is not None:
        # Reconstrucción de la envolvente direccional con peso de energía positivo.
        # Sus cuantiles son diagnósticos de llegada; la puerta usa los cortes prerregistrados.
        for banda,lo,hi in (("negativa",-BNEG[1],-BNEG[0]),("positiva",*BPOS)):
            sel=(nu>=lo)&(nu<=hi)
            for direccion,amplitud in (("entrada",inc),("salida",sal)):
                espectro=np.zeros(n,dtype=complex)
                espectro[np.flatnonzero(mask)[sel]]=amplitud[sel]*np.sqrt(abs(velocidad_t[sel]*base[sel]))
                energia=abs(np.fft.ifft(espectro))**2
                total=float(energia.sum())
                if total>0:
                    cumul=np.cumsum(energia)/total
                    tiempos[banda+"_"+direccion]=dict(s_001_50_999=[float(t[np.searchsorted(cumul,q)]) for q in (.001,.5,.999)],
                        fraccion_ultimas_40=float(energia[t>=T-40].sum()/total))
    return dict(nu=nu,E_entrada=velocidad_t*qi,E_salida=velocidad_t*qo,Q_entrada=qi,Q_salida=qo)


def integrar_bandas(sp):
    out={}
    for name,lo,hi in (("negativa",-BNEG[1],-BNEG[0]),("positiva",*BPOS)):
        nu=sp["nu"]
        sel=(nu>=lo)&(nu<=hi)
        b={k:float(np.sum(y[sel])) for k,y in sp.items() if k!="nu"}
        b["centro_salida"]=float(np.average(nu[sel],weights=sp["E_salida"][sel])) if b["E_salida"]>0 else None
        b["E_neta"]=b["E_entrada"]+b["E_salida"]
        b["Q_neta"]=b["Q_entrada"]+b["Q_salida"]
        out[name]=b
    return out


def analizar_bandas(ej,datos,sondas,dis,dest):
    bandas,cruces,cobertura,controles,tiempos={},{},{},{},{}
    with (dest/"ESPECTRO.csv").open("w",newline="") as f:
        cs=csv.writer(f,lineterminator="\n")
        cs.writerow(["r","preparacion","nu","E_entrada","E_salida","Q_entrada","Q_salida"])
        for m in MALLAS:
            _,h,dt,T=ej["mallas"][m]
            bandas[m]={}
            for r in RADIOS:
                rkey=str(r)
                bandas[m][rkey]={}
                zs={n:pares_de_cara(s,r,h) for n,s in sondas[m].items()}
                for c in (*GOTAS,"vacio"):
                    z=zs[c+"_con"]-zs[c+"_sin"] if c!="vacio" else zs["vacio"]
                    b={}
                    for fin,ds,nombre in ((T,.25,"lectura"),(440,.25,"corte440"),(T,.5,"cadencia05")):
                        temporales=tiempos.setdefault(rkey,{}).setdefault(c,{}) if m=="principal" and nombre=="lectura" else None
                        sp=dispersion_sonda(z,r,h,dt,fin,ds,temporales)
                        b[nombre]=integrar_bandas(sp)
                        if m=="principal" and nombre=="lectura":
                            for fila in zip(*(sp[n] for n in ("nu","E_entrada","E_salida","Q_entrada","Q_salida"))):
                                cs.writerow([r,c,*[format(x,".17g") for x in fila]])
                    bandas[m][rkey][c]=b
                    if m=="principal" and c!="vacio":
                        con,sin=(integrar_bandas(dispersion_sonda(zs[c+a],r,h,dt,T)) for a in ("_con","_sin"))
                        cr={}
                        for rama in ("negativa","positiva"):
                            cr[rama]={n:con[rama][n]-sin[rama][n] for n in ("E_entrada","E_salida","Q_entrada","Q_salida","E_neta","Q_neta")}
                        cruces.setdefault(rkey,{})[c]=cr
    for r in RADIOS:
        rk=str(r)
        cob={}
        for m in MALLAS:
            cajas={}
            vac,ds=bandas[m][rk]["vacio"]["lectura"]["negativa"],datos[m]["vacio"]
            en=ds["E"][0]
            for n in ("E_entrada","E_salida"):
                err=abs(abs(vac[n])/en-1)
                cajas["vacio_"+n]=dict(desvio_rel=err,pasa=bool(err<=.005))
            for k in CANALES:
                resid=maxabs(ds[f"F{k}{r}"][400:481])
                cajas["vacio_residual_"+k]=dict(valor=resid,umbral=.1*dis["umbral"][k],pasa=bool(resid<.1*dis["umbral"][k]))
            for c in GOTAS:
                x=bandas[m][rk][c]
                for banda,n in (("negativa","E_entrada"),("negativa","E_salida"),("positiva","E_salida")):
                    y=x["lectura"][banda][n]
                    dev=abs(y-x["corte440"][banda][n])
                    lim=max(.0025*abs(y),.05*dis["umbral"]["E"])
                    cajas[c+"_"+banda+"_"+n]=dict(cambio=dev,admisible=lim,pasa=bool(dev<=lim))
            cob[m]=cajas
        cobertura[rk]=cob
        pruebas={}
        for c in GOTAS:
            pruebas[c]={}
            for k in CANALES:
                def b(m,obs,n):
                    return bandas[m][rk][c][obs]["positiva"][k+"_"+n]
                y=b("principal","lectura","salida")
                piso_v=abs(bandas["principal"][rk]["vacio"]["lectura"]["positiva"][k+"_salida"])
                v={"espacio":abs(b("temporal","lectura","salida")-b("espacial","lectura","salida")),
                   "tiempo":abs(y-b("temporal","lectura","salida")),"caja":abs(y-b("caja576","lectura","salida")),
                   "corte":max(abs(b(m,"lectura","salida")-b(m,"corte440","salida")) for m in MALLAS),
                   "cadencia":max(abs(b(m,"lectura","salida")-b(m,"cadencia05","salida")) for m in MALLAS),
                   "vacio":max(abs(bandas[m][rk]["vacio"]["lectura"]["positiva"][k+"_salida"]) for m in MALLAS),
                   "entrada_positiva":max(abs(b(m,"lectura","entrada")) for m in MALLAS),"piso":PISO}
                u=max(v.values())
                centro=bandas["principal"][rk][c]["lectura"]["positiva"]["centro_salida"]
                pruebas[c][k]=dict(salida=y,vacio=piso_v,exceso_sobre_vacio=y-piso_v,U=u,tres_U=3*u,centro=centro,
                    componentes=v,detectada=bool(y-piso_v>3*u and y>v["entrada_positiva"] and BPOS[0]<=centro<=BPOS[1]))
        controles[rk]=pruebas
    return dict(unidad="M2 normalizada; energías y cargas integradas por dirección y signo temporal",
                espectro_csv="Todos los modos propagantes con signo por debajo de Nyquist de la réplica principal. Las sondas conservan la señal completa.",
                lecturas=bandas,diferencia_espectral_de_campos_completos=cruces,conversion=controles,cobertura=cobertura,
                tiempos_envolvente_direccional=tiempos)


def analizar(ruta,dest):
    dest.mkdir(exist_ok=True,parents=True)
    ej,datos,tr=leer_series(ruta)
    dis=json.loads((AQUI/"DISENO_ESPECTRAL.json").read_text())
    p,b,med,archivo=analizar_flujo(datos,dis)
    bandas=analizar_bandas(ej,datos,tr,dis,dest)
    completa=all(v["pasa"] for dic in bandas["cobertura"].values() for z in dic.values() for v in z.values())
    solapamiento={}
    for c in CASOS:
        observables={}
        for coleccion in (datos,tr):
            corto=coleccion["archivo416"][c]
            largo=coleccion["principal"][c][:len(corto)]
            assert np.array_equal(corto["s"],largo["s"])
            for col in corto.dtype.names:
                if col not in ("s","tau","W","E","Q"):
                    observables[col]=maxabs(corto[col]-largo[col])
        solapamiento[c]=observables
    retornos={}
    for m,(R,h,dt,T) in ej["mallas"].items():
        retornos[m]={}
        for r in RADIOS:
            historico=2*R-144-r-300
            if T>=historico:
                raise ValueError(f"La adquisición {m} alcanza el primer retorno a r={r}")
            retornos[m][str(r)]=dict(historico=historico,paquete_nuevo=historico+300,
                                      fin_registro=T,margen_historico=historico-T)
    decisiones={}
    for r in RADIOS:
        ms=med[str(r)]
        def ambas(n):
            return all(ms[k][n]["inferior"]>0 for k in CANALES)
        decisiones[str(r)]=dict(cobertura_completa=completa,extraccion_fondo=bool(completa and ambas("gemela")),
            salida_atribuible_conjunta=bool(completa and ambas("cargada") and ambas("D")),
            atribuible_supera_uno_por_ciento=bool(completa and all(ms[k][n]["inferior"]>dis["umbral"][k] for k in CANALES for n in ("D","cargada"))),
            equivalencia_al_uno_por_ciento=bool(completa and all(ms[k]["D"]["limite_magnitud_fraccion_stock"]<.01 for k in CANALES)),
            conversion_positiva_por_preparacion={c:all(bandas["conversion"][str(r)][c][k]["detectada"] for k in CANALES) for c in GOTAS})
    dump(dest/"BANDAS.json",bandas)
    dump(dest/"BALANCES.json",dict(presupuesto_inicial=p,por_trayectoria=b,comparacion_con_archivo416=archivo,
                                  max_abs_solapamiento_bruto_s0_300=solapamiento,primeros_retornos=retornos))
    dump(dest/"RESULTADO.json",dict(A=ej["A"],ventana=[400,480],stock=dis["stock"],umbrales=dis["umbral"],mediciones=med,
        extension_560_640_requerida=not completa,extension_560_640_ejecutada=False,
        decisiones=decisiones,indicios_de_captura=decisiones["60"]["salida_atribuible_conjunta"],recarga_habilitada=False))
    return decisiones


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("datos",type=Path,nargs="?",default=AQUI/"datos")
    p.add_argument("--salida",type=Path,default=AQUI)
    a=p.parse_args()
    print(json.dumps(analizar(a.datos,a.salida),indent=2))
