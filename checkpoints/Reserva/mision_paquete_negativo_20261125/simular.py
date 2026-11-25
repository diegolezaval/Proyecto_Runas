"""Evolución radial libre de cinco casos del paquete negativo y sondas de dos celdas."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import monotonic

import numpy as np

from diseno import AQUI, ANTERIOR, PASO2, ensayo, paquete
sys.path.insert(0,str(ANTERIOR))
import ejecutar as previo
from ensayo import dump, sha

CONFIG={"principal":(512,.025,.0005,480),"temporal":(512,.025,.001,480),
        "espacial":(512,.05,.001,480),"caja576":(576,.025,.0005,480),
        "archivo416":(416,.025,.0005,300)}
CASOS=("cargada_con","cargada_sin","gemela_con","gemela_sin","vacio")
COL="s,tau,E,Q,E40,Q40,E60,Q60,FE40,FQ40,FE60,FQ60,W"
SONDAS="s,Re40i,Im40i,Re40e,Im40e,Re60i,Im60i,Re60e,Im60e"
PRE="0793ff4b1ed4ecc94cb8c8e5b0f5e666084e5969"


def rejillas():
    old=ensayo.RADIUS
    try:
        out={}
        for R,h in sorted({(R,h) for R,h,_,_ in CONFIG.values()}|{(384,.05),(256,.05)}):
            ensayo.RADIUS=R
            out[R,h]=ensayo.Grid(h)
        return out
    finally:
        ensayo.RADIUS=old


def leer_estado(p,g):
    with np.load(p,allow_pickle=False) as z:
        if (z["tau"],z["R"],z["dx"])!=(300,g.n*g.dx,g.dx):
            raise ValueError(f"Rejilla distinta: {p}")
        campos=[z[k] for k in ("q","v")]
        if any(a.dtype!=np.float64 or a.shape!=(3,g.n) or not np.isfinite(a).all() for a in campos):
            raise ValueError(f"Campos de {p}")
    return previo.con_halo(campos,g.n)


def cotejar(campos,arch,g,gm):
    q,v=campos
    aq,av=arch
    i=round(144/g.dx)
    dq=np.max(abs(q[:,1:i+1]-aq[:,1:i+1]),axis=1)
    dv=np.max(abs(v[:,1:i+1]-av[:,1:i+1]),axis=1)
    dI=previo.inventario(g,q,v,previo.referencia(q))[2:]-previo.inventario(gm,aq,av,previo.referencia(aq))[2:]
    if max(np.max(dq),np.max(dv),np.max(abs(dI)))>=1e-7:
        raise ValueError("No se reprodujo el interior de la preparación de τ300")
    return dict(max_abs_q_r144=dq.tolist(),max_abs_v_r144=dv.tolist(),
                delta_inventarios_40_60=dI.tolist())


def observar_sonda(q,g):
    # El halo en índice 0 deja las caras de corte entre índices r/h y r/h+1.
    return q[:2,[g.core,g.core+1,g.port,g.port+1]].T.ravel()


def ejecutar_caso(m,c,g,estado,lib,amplitud,dest):
    R,h,dt,T=CONFIG[m]
    root=dest/m/c
    root.mkdir(parents=True)
    tiene=c.endswith("_con") or c=="vacio"
    q,v=(x.copy() for x in estado)
    perfil=np.ones(g.n)  # Sólo el indicador histórico de perfil usa esta referencia.
    i0=previo.inventario(g,q,v,perfil)
    if tiene:
        dq,dv=paquete(g.r,amplitud)
        q[:,1:-1]+=dq
        v[:,1:-1]+=dv
    nuevo=previo.inventario(g,q,v,perfil)
    if np.max(abs(nuevo[2:]-i0[2:]))>1e-11:
        raise ValueError("El paquete tocó un interior al inicio")
    n=round(.25/dt)
    if n*dt!=.25:
        raise ValueError("Cadencia no múltiplo del paso")
    sumas=np.zeros(6)
    with (root/"serie.csv").open("w") as f,(root/"sondas.csv").open("w") as tr:
        f.write(COL+"\n")
        tr.write(SONDAS+"\n")
        for j in range(4*T+1):
            if j:
                previo.avanzar_libre(lib,g,q,v,dt,n,sumas)
            s=j/4
            son=observar_sonda(q,g)
            if not np.isfinite(son).all():
                raise ValueError(f"Sonda no finita {m}/{c}/{s}")
            tr.write(",".join(format(x,".17g") for x in (s,*son))+"\n")
            if j%4==0:
                inv=previo.inventario(g,q,v,perfil)
                fila=[s,300+s,*inv,*sumas[[0,1,3,4]],0.]
                if not np.isfinite(fila).all():
                    raise ValueError(f"Inventario no finito {m}/{c}/{s}")
                f.write(",".join(format(x,".17g") for x in fila)+"\n")
    final=root/f"s{T}.npz"
    np.savez_compressed(final,s=T,R=R,h=h,dt=dt,q=q[:,1:-1],v=v[:,1:-1],F=sumas)
    with np.load(final,allow_pickle=False) as z:
        qr,vr=previo.con_halo([z["q"],z["v"]],g.n)
        np.testing.assert_array_equal(previo.inventario(g,qr,vr,perfil),fila[2:8])
        np.testing.assert_array_equal(z["F"][[0,1,3,4]],fila[8:12])
    print("terminada",m,c,T,flush=True)
    return dict(replica=m,caso=c,fin_s=T,pasos=4*T*n,
                incremento_inicial_global_E_Q=(nuevo[:2]-i0[:2]).tolist(),
                incremento_inicial_interiores=(nuevo[2:]-i0[2:]).tolist(),
                W_posterior=0.,sha256_serie=sha(root/"serie.csv"),sha256_sondas=sha(root/"sondas.csv"),
                sha256_estado_final=sha(final))


def ejecutar(dest,archivos,jobs):
    inicio=previo.reloj()
    tick=monotonic()
    hist,fina,_,insumos=previo.entradas()
    dis=json.loads((AQUI/"DISENO_ESPECTRAL.json").read_text())
    amp=dis["A"]
    dest.mkdir(parents=True,exist_ok=False)
    (dest/"estados_iniciales").mkdir()
    mallas=rejillas()
    anterior=json.loads((ANTERIOR/"datos/EJECUCION.json").read_text())
    certificados={x["archivo"].split("/")[-1]:x["sha256"] for x in anterior["preparaciones"]}
    origenes,recibos=[],[]
    with TemporaryDirectory() as temp:
        lib=previo.compilar(temp)
        gc=mallas[256,.05]
        ff,zz,_=gc.equilibrium()
        qc,vc,pres=ensayo.prepare(gc,.001,ff,zz,Path(temp)/"preparacion")
        if not pres["aprobada"]:
            raise ValueError("Preparación espacial")
        cache={}
        for R,h in ((416,.025),(384,.05)):
            for c in ("cargada","gemela"):
                name=f"R{R}_h{h}_{c}.npz"
                path=archivos/name
                if path.exists():
                    modo="archivo recuperado"
                else:
                    previo.reconstruir((R,h,c),mallas[R,h],fina if h==.025 else (qc,vc),hist,lib,dest)
                    path=dest/"estados_iniciales"/name
                    modo="regenerado desde τ0"
                if sha(path)!=certificados[name]:
                    raise ValueError(f"Huella histórica de {name}: use las preparaciones del recibo o su entorno de reproducción")
                cache[R,h,c]=leer_estado(path,mallas[R,h])
                origenes.append(dict(R=R,h=h,caso=c,modo=modo,sha256=certificados[name]))
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            corridas=[]
            def lanzar(m,c,estado):
                R,h,_,_=CONFIG[m]
                ramas=("vacio",) if c=="vacio" else (c+"_con",c+"_sin")
                for rama in ramas:
                    corridas.append(pool.submit(ejecutar_caso,m,rama,mallas[R,h],estado,lib,amp,dest))
            ampliaciones={}
            for R,h in ((512,.025),(576,.025),(512,.05)):
                for c in ("cargada","gemela"):
                    clave=R,h,c
                    ampliaciones[pool.submit(previo.reconstruir,clave,mallas[R,h],
                        fina if h==.025 else (qc,vc),hist,lib,dest)]=clave
            for c in ("cargada","gemela"):
                lanzar("archivo416",c,cache[416,.025,c])
            for m,(R,h,_,_) in CONFIG.items():
                vac=np.zeros((3,mallas[R,h].n+2))
                lanzar(m,"vacio",(vac,vac))
            for fu in as_completed(ampliaciones):
                R,h,c=ampliaciones[fu]
                estado,reg=fu.result()
                refR=416 if h==.025 else 384
                reg["comparacion_amplia"]=cotejar(estado,cache[refR,h,c],mallas[R,h],mallas[refR,h])
                reg["archivo_de_referencia"]=f"R{refR}_h{h}_{c}.npz"
                origenes.append(reg)
                for m,(rr,hh,_,_) in CONFIG.items():
                    if (rr,hh)==(R,h):
                        lanzar(m,c,estado)
            for fu in as_completed(corridas):
                recibos.append(fu.result())
    dump(dest/"EJECUCION.json",dict(base="c7e36153a6f1742cb83e1524e68b6955cc1e1d95",
         prerregistro=PRE,inicio_utc=inicio,fin_utc=previo.reloj(),segundos=monotonic()-tick,jobs=jobs,
         A=amp,mallas=CONFIG,insumos=insumos,sha256_recibo_preparaciones=sha(ANTERIOR/"datos/EJECUCION.json"),
         sha256_diseno=sha(AQUI/"DISENO_ESPECTRAL.json"),origenes=origenes,
         series=sorted(recibos,key=lambda x:(x["replica"],x["caso"]))))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("destino",type=Path)
    p.add_argument("--preparaciones",type=Path,default=ANTERIOR/"datos/estados_iniciales")
    p.add_argument("--jobs",type=int,default=8)
    a=p.parse_args()
    ejecutar(a.destino,a.preparaciones,a.jobs)
