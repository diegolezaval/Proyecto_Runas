"""Inventario reproducible del material temporal. No integra ecuaciones M2."""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.interpolate import CubicHermiteSpline

HERE = Path(__file__).resolve().parent
RES = HERE.parent
ROOT = RES.parents[1]
BASE = "e8d99b4b0c5274bc773fc7e05d9d1e8b340a5f4b"
PACK = RES/"mision_paquete_negativo_20261125"
WINDOWS = (40, 80, 240)


def read(p):
    return json.loads(p.read_text())


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree():
    return subprocess.check_output(["git","ls-tree","-r","--name-only",BASE,"checkpoints/Reserva"],
                                   cwd=ROOT,text=True).splitlines()


def phase_control():
    # Dos instantáneas de prueba de una sola donante: fase ±b(r) y velocidad iωΦ.
    # El receptor de referencia, en cuadratura, está en el eje a d=80.
    path=ROOT/"validacion/P06/rama/perfil_w0.90000.csv"
    r,f,fp,_,_=np.loadtxt(path,delimiter=",",skiprows=1).T
    profile=CubicHermiteSpline(r,f,fp)
    x=np.linspace(.025,80.,3200)
    u=(x-36.)/2.
    inside=abs(u)<1
    b=np.where(inside,np.clip(1-u*u,0,1)**4,0.)
    bp=np.where(inside,-4*u*np.clip(1-u*u,0,1)**3,0.)
    def state(sign):
        phase=np.exp(sign*1j*b)
        field=profile(x)*phase
        grad=(profile(x,1)+sign*1j*bp*profile(x))*phase
        vel=.9j*field
        return field,abs(grad)**2,2*(field.conj()*vel).imag
    a,e,q=state(1)
    c,ee,qq=state(-1)
    receptor=1j*profile(abs(80-x))
    # Diferencia de |D+R|² sin cancelar dos fondos casi iguales en coma flotante.
    ds=2*((a-c).conj()*receptor).real
    reference=4*profile(x)*profile(abs(80-x))*np.sin(b)
    assert np.allclose(ds,reference,rtol=1e-13,atol=1e-30)
    assert np.array_equal(e,ee) and np.array_equal(q,qq)
    assert np.all(a[(x<34)|(x>38)]==c[(x<34)|(x>38)]) and max(abs(ds))>0
    return dict(fuente=digest(path),soporte_fase=[34,38],d=80,
                max_diferencia_densidad_gradiente=float(max(abs(e-ee))),
                max_diferencia_densidad_Q=float(max(abs(q-qq))),
                max_diferencia_s_en_eje=float(max(abs(ds))))


def run():
    files=tree()
    series=[]
    manifest=read(PACK/"datos/EJECUCION.json")
    for record in manifest["series"]:
        case,rep=record["caso"],record["replica"]
        if case not in ("cargada_sin","gemela_sin"):
            continue
        for kind,step in (("serie",1.),("sondas",.25)):
            path=PACK/"datos"/rep/case/(kind+".csv")
            sha=digest(path)
            assert sha==record["sha256_"+kind]
            with path.open() as stream:
                reader=csv.DictReader(stream)
                columns=reader.fieldnames
                times=[float(row["s"]) for row in reader]
            assert times==[i*step for i in range(round(record["fin_s"]/step)+1)]
            series.append(dict(replica=rep,caso=case,tipo=kind,sha256=sha,fin=times[-1],
                cadencia=step,columnas=columns,muestras_hasta={T:sum(t<=T for t in times) for T in WINDOWS}))
    assert len(series)==20
    capsules={}
    for p in sorted(n for n in files if n.endswith(".zip")):
        with ZipFile(ROOT/p) as z:
            members=[n for n in z.namelist() if not n.endswith("/")]
        capsules[p]=dict(archivos=len(members),estados=[n for n in members if n.endswith((".npz",".npy",".h5",".hdf5"))],
                         extensiones=sorted({Path(n).suffix for n in members}))
    radial=read(RES/"mision_extraccion_radial_20261124/datos/EJECUCION.json")
    off=[dict(ruta=r["ruta"],s_final=r["pasos"]*radial["mallas"][r["ruta"].split("/")[0]][2],
              sha256_final=r["sha256_estado"]) for r in radial["series"] if r["ruta"].endswith("/apagada")]
    off2=read(RES/"mision_senal_apagada_20261124/datos/EJECUCION.json")["trayectorias"]
    rem=read(RES/"paso3_20261118/RECIBO_GUARDADO_DESCARGA.json")["estados"]["por_archivo"]
    frozen=read(RES/"transitorio_chi_contacto_20261126/RECUPERACION.json")
    archives=set(files)
    for item in capsules.values():
        archives.update(item["estados"])
    times=sorted({int(m.group(1)) for n in archives
                  if (m:=re.search(r"/(?:cargada_sin|gemela_sin)/s([0-9]+)\.npz$",n))})
    times_with_receipts=sorted(set(times)|{int(r["s_final"]) for r in off}|{0})
    coverage={T:dict(tiempos_posibles_de_campo=[t for t in times_with_receipts if 0<=t<=T],
                     numero_de_tiempos_interiores=sum(0<t<T for t in times_with_receipts))
              for T in WINDOWS}
    result=dict(base=BASE,recibo_congelado=frozen["sha256_resultado"],ventanas=WINDOWS,series=series,
                instantaneas_git=[n for n in files if n.endswith((".npz",".npy",".h5",".hdf5"))],
                capsulas=capsules,radiales_apagadas=off,estados_dos_centros_s240=sorted(rem),
                dos_centros_sin_senal=[(r["malla"],r["caso"],r["sha256_estado"]) for r in off2],
                control_fase=phase_control(),cobertura_radial=coverage)
    (HERE/"resultado.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n")


if __name__=="__main__":
    run()
