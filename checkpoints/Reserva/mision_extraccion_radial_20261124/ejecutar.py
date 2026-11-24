"""Extracción de Reserva con la acción y los flujos del integrador radial original."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes as ct
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

import numpy as np

AQUI = Path(__file__).resolve().parent
PASO2 = AQUI.parent / "paso2_20261117"
PASO3 = AQUI.parent / "paso3_20261118"
sys.path[:0] = [str(PASO3), str(PASO2)]
import ensayo
from calibrar import soporte
from ensayo import dump, sha

CONFIG = {"historica": (256, .025, .0005), "principal": (384, .025, .0005),
          "temporal": (384, .025, .001), "espacial": (384, .05, .001),
          "caja416": (416, .025, .0005)}
CASOS = ("cargada", "gemela")
COLUMNAS = "s,tau,E,Q,E40,Q40,E60,Q60,FE40,FQ40,FE60,FQ60,W"
NOMBRES_I = ("E","Q","E40","Q40","E60","Q60")
RAIZ = PASO2.parents[2]
BASE = "bce7113d1cb9befef6699578d61f95613ed0dcdf"
PRE = "71057af265e24566f15c2c4858c6fb7dd9bc5f05"


def json_de(p):
    return json.loads(p.read_text())


def reloj():
    return datetime.now(timezone.utc).isoformat()


def compilar(tmp):
    ruta = Path(tmp)/"extraccion.so"
    args = ["cc","-std=c11","-O3","-march=native","-ffp-contract=off","-shared","-fPIC",
            str(AQUI/"senal.c"),"-lm","-o",str(ruta)]
    subprocess.run(args,check=True)
    lib = ct.CDLL(str(ruta))
    vec = np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
    I,D = ct.c_int,ct.c_double
    lib.advance.argtypes = [I,I,D,D]+[vec]*6
    lib.advance_source.argtypes = [I,I,I,D,D]+[vec]*6+[I,vec,vec,D,vec]
    lib.advance.restype = lib.advance_source.restype = None
    return lib


def construir_mallas():
    # Grid sólo consulta este radio al construirse. Se inicializa todo en un hilo.
    guardado = ensayo.RADIUS
    try:
        mallas = {}
        for R,h in sorted({(R,h) for R,h,_ in CONFIG.values()} | {(256,.05)}):
            ensayo.RADIUS = R
            mallas[R,h] = ensayo.Grid(h)
        return mallas
    finally:
        ensayo.RADIUS = guardado


def leer_campos(p, tau, h, dt):
    with np.load(p,allow_pickle=False) as z:
        if (float(z["tau"]),float(z["dx"]),float(z["dt"])) != (tau,h,dt):
            raise ValueError(f"Metadatos de {p}")
        q,v = (z[k].copy() for k in ("q","v"))
        if any(x.shape!=(3,round(256/h)) or x.dtype!=np.float64 or not np.isfinite(x).all()
               for x in (q,v)):
            raise ValueError(f"Campos de {p}")
        return q,v


def entradas():
    manifest = json_de(PASO2/"MANIFIESTO.json")
    ret = json_de(PASO3/"MANIFIESTO_RETENCION.json")
    cal = json_de(PASO3/"calibracion/CALIBRACION.json")
    rutas = {"cargada":PASO3/"datos/dt0005/gota_a010/tau300.npz",
             "gemela":PASO3/"datos/dt0005/gemelo/tau300.npz"}
    prep = PASO2/"datos/preparacion.npz"
    requeridas = {prep:manifest["archivos"]["datos/preparacion.npz"]["sha256"],
                  PASO2/"ensayo.py":manifest["archivos"]["ensayo.py"]["sha256"],
                  PASO2/"radial.c":manifest["archivos"]["radial.c"]["sha256"]}
    for p in (ensayo.PROFILE,ensayo.THETA,RAIZ/"herramientas/modelo_m2.py"):
        requeridas[p] = manifest["entradas"][p.relative_to(RAIZ).as_posix()]
    for p in (*rutas.values(),PASO3/"calibracion/CALIBRACION.json",PASO3/"calibracion/ensayo2.npz"):
        requeridas[p] = ret[p.relative_to(PASO3).as_posix()]["sha256"]
    for p, huella in requeridas.items():
        if sha(p)!=huella:
            raise ValueError(f"SHA-256 inesperado en {p}")
    if (requeridas[rutas["gemela"]]!=cal["sha256_gemelo_300"] or cal["error_rel"]>.02
        or not json_de(PASO3/"RETENCION.json")["aprobada"]
        or json_de(PASO2/"REPRODUCCION_INDEPENDIENTE.json")["archivos"]["datos/preparacion.npz"]["sha256"]!=requeridas[prep]):
        raise ValueError("Preparación, retención o calibración")
    historicos = {c:leer_campos(p,300.,.025,.0005) for c,p in rutas.items()}
    return (historicos,leer_campos(prep,0.,.025,.001),cal,
            {p.relative_to(RAIZ).as_posix():h for p,h in requeridas.items()})


def con_halo(campos, n):
    return tuple(np.pad(x,((0,0),(1,n-x.shape[1]+1))) for x in campos)


def referencia(q):
    return np.hypot(q[0,1:-1],q[1,1:-1])


def inventario(g,q,v,perfil):
    return np.array(g.measure(q,v,perfil)[:6])


def avanzar_libre(lib,g,q,v,dt,pasos,F):
    lib.advance(g.n,pasos,dt,g.dx,g.lo,g.hi,g.theta,q,v,F)


def forma_fuente(g):
    n = np.count_nonzero(g.r<6)
    forma = np.ascontiguousarray(soporte(g.r[:n]))
    return forma,np.ascontiguousarray(4*np.pi*g.w[:n]*forma)


def avanzar_senal(lib,g,q,v,dt,pasos,primero,F,A,forma,peso,W):
    lib.advance_source(g.n,pasos,primero,dt,g.dx,g.lo,g.hi,g.theta,q,v,F,len(forma),forma,peso,A,W)


def validar_integrador(lib,g,historicos,cal):
    q,v = con_halo(historicos["gemela"],g.n)
    q2,v2 = q.copy(),v.copy()
    fa,fb = np.zeros(6),np.zeros(6)
    forma,peso = forma_fuente(g)
    avanzar_libre(lib,g,q,v,.001,100,fa)
    avanzar_senal(lib,g,q2,v2,.001,100,0,fb,0.,forma,peso,np.zeros(1))
    for a,b in ((q,q2),(v,v2),(fa,fb)):
        np.testing.assert_array_equal(a,b)
    q,v = con_halo(historicos["gemela"],g.n)
    W = np.zeros(1)
    avanzar_senal(lib,g,q,v,.001,8000,0,np.zeros(6),cal["A"],forma,peso,W)
    with np.load(PASO3/"calibracion/ensayo2.npz",allow_pickle=False) as ref:
        dq = float(max(np.max(abs(q[:,1:-1]-ref["q"])),np.max(abs(v[:,1:-1]-ref["v"]))))
        dw = float(abs(W[0]-ref["trabajo"]))
    if dq>3e-9 or dw>1e-10:
        raise ValueError(f"Calibración radial {dq}, {dw}")
    return dict(pasos_regresion_sin_fuente=100,coincidencia_exacta=True,
                trabajo_s8=W[0],delta_trabajo_calibracion=dw,delta_max_campos_o_velocidades_s8=dq)


def reconstruir(clave,g,previa,historicos,lib,dest):
    R,h,c = clave
    q,v = con_halo(previa,g.n)
    ultima = round(1/h)
    cola = float(max(np.max(abs(x[:,-ultima:])) for x in previa))
    if cola >= 1e-20:
        raise ValueError(f"Cola de la preparación en τ0 {clave}: {cola}")
    if c=="cargada":
        dq,dv=ensayo.packet(g.r,.010)
        q[:,1:-1]+=dq
        v[:,1:-1]+=dv
    F=np.zeros(6)
    for dt,n,final in ((.001,240000,240),(.0005,120000,300)):
        avanzar_libre(lib,g,q,v,dt,n,F)
        print("preparación",clave,"tau",final,flush=True)
    info = dict(R=R,h=h,caso=c,tau=300,origen_tau=0,cola_ultima_unidad_tau0=cola)
    if h==.025:
        old=historicos[c]
        por_radio={}
        a=con_halo(old,g.n)
        # El relleno aquí sirve únicamente para leer las esferas interiores históricas.
        nuevo=inventario(g,q,v,referencia(q))
        antiguo=inventario(g,*a,referencia(a[0]))
        for radio,j in ((40,2),(60,4)):
            corte=round(radio/h)
            dif=[(u[:,1:corte+1]-o[:,:corte]) for u,o in zip((q,v),old)]
            por_radio[str(radio)]=dict(E=nuevo[j]-antiguo[j],Q=nuevo[j+1]-antiguo[j+1],
                max_abs_componentes_q=np.max(abs(dif[0]),axis=1).tolist(),
                max_abs_componentes_v=np.max(abs(dif[1]),axis=1).tolist())
            if max(abs(nuevo[j:j+2]-antiguo[j:j+2]))>1e-7:
                raise ValueError(f"Inventarios interiores distintos en {clave}, r={radio}")
        info["diferencia_con_tau300_verificado"]=por_radio
    sitio=dest/"estados_iniciales"/f"R{R}_h{h}_{c}.npz"
    np.savez_compressed(sitio,tau=300.,R=R,dx=h,q=q[:,1:-1],v=v[:,1:-1])
    info.update(archivo=sitio.relative_to(dest).as_posix(),sha256=sha(sitio))
    return (q,v),info


def trayectoria(config,c,activa,g,estado,lib,A,dest):
    R,h,dt=CONFIG[config]
    q,v=(x.copy() for x in estado)
    perfil=referencia(q)
    F,W=np.zeros(6),np.zeros(1)
    forma,peso=forma_fuente(g)
    n=round(1/dt)
    salida=dest/config/c/("encendida" if activa else "apagada")
    salida.mkdir(parents=True)
    with (salida/"serie.csv").open("w",buffering=1) as csv:
        csv.write(COLUMNAS+"\n")
        for s in range(241):
            if s:
                if activa and s<=8:
                    avanzar_senal(lib,g,q,v,dt,n,(s-1)*n,F,A,forma,peso,W)
                else:
                    avanzar_libre(lib,g,q,v,dt,n,F)
            fila=[s,300+s,*inventario(g,q,v,perfil),*F[[0,1,3,4]],W[0]]
            if not np.isfinite(fila).all():
                raise ValueError(f"Valores no finitos {salida}/{s}")
            csv.write(",".join(format(x,".17g") for x in fila)+"\n")
    final=salida/"s240.npz"
    np.savez_compressed(final,s=240,tau=540,R=R,dx=h,dt=dt,A=A if activa else 0.,
                        q=q[:,1:-1],v=v[:,1:-1],F=F,W=W)
    with np.load(final,allow_pickle=False) as z:
        qr,vr=con_halo((z["q"],z["v"]),g.n)
        lectura=inventario(g,qr,vr,perfil)
        diferencia=float(np.max(abs(lectura-np.array(fila[2:8]))))
        np.testing.assert_array_equal(lectura,fila[2:8])
        np.testing.assert_array_equal(z["F"][[0,1,3,4]],fila[8:12])
        np.testing.assert_array_equal(z["W"],fila[12:13])
    print("terminada",config,c,salida.name,flush=True)
    return dict(ruta=salida.relative_to(dest).as_posix(),pasos=240*n,
                sha256_serie=sha(salida/"serie.csv"),sha256_estado=sha(final),
                bytes_estado=final.stat().st_size,diferencia_relectura_final=diferencia)


def ejecutar(dest,jobs):
    historicos,preparacion,cal,hashes=entradas()
    dest.mkdir(parents=True,exist_ok=False)
    (dest/"estados_iniciales").mkdir()
    comienzo,antes=reloj(),monotonic()
    mallas=construir_mallas()
    with TemporaryDirectory() as temp:
        lib=compilar(temp)
        prueba=validar_integrador(lib,mallas[256,.025],historicos,cal)
        gr=mallas[256,.05]
        f,z,_=gr.equilibrium()
        qc,vc,pres=ensayo.prepare(gr,.001,f,z,Path(temp)/"gruesa")
        if not pres["aprobada"]:
            raise ValueError("Preparación espacial")
        origenes,recibos=[],[]
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futuros={}
            salidas=[]
            def lanzar(config,c,estado):
                R,h,_=CONFIG[config]
                for activa in (True,False):
                    salidas.append(pool.submit(trayectoria,config,c,activa,mallas[R,h],estado,lib,cal["A"],dest))
            for R,h in ((384,.025),(416,.025),(384,.05)):
                for c in CASOS:
                    clave=R,h,c
                    futuros[pool.submit(reconstruir,clave,mallas[R,h],preparacion if h==.025 else (qc,vc),
                                         historicos,lib,dest)]=clave
            for c in CASOS:
                lanzar("historica",c,con_halo(historicos[c],mallas[256,.025].n))
            for future in as_completed(futuros):
                R,h,c=futuros[future]
                estado,info=future.result()
                origenes.append(info)
                for config,(radio,paso,_) in CONFIG.items():
                    if (radio,paso)==(R,h):
                        lanzar(config,c,estado)
            for future in as_completed(salidas):
                recibos.append(future.result())
    dump(dest/"EJECUCION.json",dict(base=BASE,prerregistro=PRE,inicio_utc=comienzo,fin_utc=reloj(),
        duracion_segundos=monotonic()-antes,trabajadores=jobs,python=platform.python_version(),
        compilador=subprocess.check_output(["cc","--version"],text=True).splitlines()[0],
        insumos=hashes,senales=dict(A=cal["A"],radio=6,duracion=8),regresion=prueba,
        mallas=CONFIG,preparacion_espacial=pres,preparaciones=sorted(origenes,key=lambda x:x["archivo"]),
        series=sorted(recibos,key=lambda x:x["ruta"])))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("destino",type=Path)
    p.add_argument("--jobs",type=int,default=8)
    args=p.parse_args()
    ejecutar(args.destino,args.jobs)
