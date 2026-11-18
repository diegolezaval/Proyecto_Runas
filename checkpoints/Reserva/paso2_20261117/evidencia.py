"""Archivar las series originales y comprobar la recuperación de los estados finos."""
import argparse
import json
from pathlib import Path
import shutil
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import numpy as np

from ensayo import AMPLITUDES, GRIDS, HERE, KICKS, NAMES, PROFILE, ROOT, THETA, Grid, dump, sha


def archive(work, dest):
    dest.mkdir(parents=True,exist_ok=True)
    payload=dest/"datos"
    payload.mkdir(exist_ok=True)
    for grid in GRIDS:
        with ZipFile(payload/(grid+"_series.zip"),"w",compression=ZIP_DEFLATED) as z:
            for csv in sorted((work/grid).glob("*/serie.csv")):
                name=csv.parent.name
                member=ZipInfo(name+"/serie.csv",date_time=(1980,1,1,0,0,0))
                z.writestr(member,csv.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
    for state in sorted((work/"fina").glob("*/estado.npz")):
        shutil.copyfile(state,payload/(state.parent.name+".npz"))
    for name in ("ESTABILIDAD.json","CONTACTO.json","BANDA.json"):
        shutil.copyfile(work/name,dest/name)
    inputs=[PROFILE,THETA,ROOT/"validacion/P06/acceso_lineal/resultados.json",
            ROOT/"herramientas/modelo_m2.py",ROOT/"herramientas/dispersion_reserva_m2.py"]
    files=[*payload.iterdir(),*(dest/i for i in ("ESTABILIDAD.json","CONTACTO.json","BANDA.json")),
           *(dest/i for i in ("PRERREGISTRO.md","ensayo.py","radial.c","banda.py","evidencia.py"))]
    dump(dest/"MANIFIESTO.json",dict(prerregistro_git="4394eb547106b348b3f20ca186b4cbd5c41bcd9d",
        unidades="M2 normalizadas",entradas={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        archivos={str(p.relative_to(dest)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)},
        estado="q=(Re Phi, Im Phi, chi), v=derivadas, dimensiones (3,N); centros (i+1/2) dx. Los tiempos de pulso son relativos al fin de la preparación.",
        series="Flujos acumulados con signo saliente. SalidaE40 y salidaE60 integran solo la parte positiva. Muestreo de inventarios cada 0,5."))
    audit(dest)


def audit(dest, work=None):
    reference=json.loads((dest/"MANIFIESTO.json").read_text())
    for name,digest in reference["entradas"].items():
        assert sha(ROOT/name)==digest,name
    for name,entry in reference["archivos"].items():
        if work is not None and name.startswith("datos/"):
            continue
        assert (dest/name).stat().st_size==entry["bytes"] and sha(dest/name)==entry["sha256"],name
    if work is not None:
        # Recrear sólo los contenedores deterministas, manteniendo intactos los resultados públicos.
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            copy=Path(temp)
            for name in ("PRERREGISTRO.md","ensayo.py","radial.c","banda.py","evidencia.py"):
                shutil.copyfile(dest/name,copy/name)
            archive(work,copy)
            reproduced=json.loads((copy/"MANIFIESTO.json").read_text())
            for name,entry in reference["archivos"].items():
                assert entry==reproduced["archivos"][name],name
            print("Estados, series y resultados recuperados coinciden con el manifiesto publicado.")
        return
    results=json.loads((dest/"CONTACTO.json").read_text())
    stability=json.loads((dest/"ESTABILIDAD.json").read_text())
    assert stability["aprobada"]
    grid=Grid(GRIDS["fina"][0])
    f,_,_=grid.equilibrium()
    cases=set(KICKS)|{"gemelo"}|{k+"_"+a for a in AMPLITUDES for k in ("gota","vacio")}
    errors=[]
    for g in GRIDS:
        with ZipFile(dest/"datos"/(g+"_series.zip")) as z:
            assert set(z.namelist())=={c+"/serie.csv" for c in cases}
            for name in sorted(cases):
                with z.open(name+"/serie.csv") as csv:
                    s=np.genfromtxt(csv,delimiter=",",names=True)
                assert list(s.dtype.names)==NAMES and np.array_equal(s["tau"],np.arange(481)/2)
                assert all(np.isfinite(s[col]).all() for col in NAMES)
                if g=="fina":
                    with np.load(dest/"datos"/(name+".npz"),allow_pickle=False) as state:
                        q,v=state["q"],state["v"]
                        assert q.shape==v.shape==(3,grid.n) and state["tau"]==240
                        assert state["dx"]==grid.dx and state["dt"]==GRIDS[g][1]
                        obs=grid.measure(np.pad(q,((0,0),(1,1))),np.pad(v,((0,0),(1,1))),f)
                    for col,val in zip(NAMES[1:10],obs,strict=True):
                        error=abs(s[col][-1]-val)/max(1.,abs(val))
                        assert error<2e-12,(name,col,error)
                        errors.append(error)
    with np.load(dest/"datos/preparacion.npz",allow_pickle=False) as state:
        assert state["tau"]==0 and state["t_preparacion"]==8
        E,Q,*_=grid.measure(np.pad(state["q"],((0,0),(1,1))),np.pad(state["v"],((0,0),(1,1))),f)
        p=results["preparacion"]["fina"]
        assert np.allclose([E,Q],[p["E"],p["Q"]],rtol=1e-13,atol=0)
    print(json.dumps(dict(series=len(cases)*len(GRIDS),estados_finales=len(cases),preparaciones=1,
                          peor_diferencia_rel_escalada=max(errors),decision=results["status"])))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("operacion",choices=("archivar","verificar","verificar-reproduccion"))
    p.add_argument("origen",type=Path)
    args=p.parse_args()
    if args.operacion=="archivar":
        archive(args.origen,HERE)
    elif args.operacion=="verificar-reproduccion":
        audit(HERE,args.origen)
    else:
        audit(args.origen)
