"""Contraste confirmado en dos amplitudes nuevas, reutilizando las preparaciones y gemelos."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import itertools
import json
from pathlib import Path
import shutil
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
sys.path.insert(0,str(BASE))
from ensayo import GRIDS, Grid, dump, evolve, native, packet, response, sha

NEW={"a0025":.0025,"a0050":.005}
ALL={**NEW,"a010":.01}


def restore_inputs(work):
    expected=json.loads((HERE/"INSUMOS.json").read_text())
    for entry in expected.values():
        if sha(BASE/entry["archivo"])!=entry["sha256"]:
            raise ValueError(entry["archivo"])
    for mesh in GRIDS:
        for case in ("preparacion","gemelo"):
            folder=work/mesh/case
            folder.mkdir(parents=True,exist_ok=True)
            src=BASE/"datos"/(case+".npz") if mesh=="fina" else HERE/"insumos"/(mesh+"_"+case+".npz")
            if (folder/"estado.npz").exists():
                if sha(folder/"estado.npz")!=sha(src):
                    raise ValueError("Estado previo distinto: "+str(folder))
            else:
                shutil.copyfile(src,folder/"estado.npz")
        with ZipFile(BASE/"datos"/(mesh+"_series.zip")) as z:
            (work/mesh/"gemelo/serie.csv").write_bytes(z.read("gemelo/serie.csv"))


def run(work,jobs):
    source=json.loads((BASE/"CONTACTO.json").read_text())
    background=json.loads((BASE/"ESTABILIDAD.json").read_text())
    if not background["aprobada"] or not all(p["aprobada"] for p in source["preparacion"].values()):
        raise ValueError("Falta estabilidad o preparación")
    fun=native(work)
    def mesh_run(pair):
        name,(dx,dt)=pair
        grid=Grid(dx)
        f,_,_=grid.equilibrium()
        with np.load(work/name/"preparacion/estado.npz",allow_pickle=False) as state:
            assert state["dx"]==dx and state["dt"]==dt and state["tau"]==0
            q,v=state["q"],state["v"]
        for label,a in NEW.items():
            dq,dv=packet(grid.r,a)
            for medium,baseq,basev in (("gota",q,v),("vacio",0.,0.)):
                evolve(grid,dt,baseq+dq,basev+dv,f,fun,work/name/(medium+"_"+label))
                print("confirmatorio",name,medium,label,flush=True)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(mesh_run,GRIDS.items()))


def decision(work):
    first=json.loads((BASE/"CONTACTO.json").read_text())
    measured={g:{k:response(work,g,k) for k in NEW} for g in GRIDS}
    for g in GRIDS:
        measured[g]["a010"]=first["mediciones"][g]["a010"]
    gates={}
    for label in NEW:
        m={}
        for x in ("E","Q"):
            f,t,c=(measured[g][label][x] for g in ("fina","temporal","espacial"))
            terms=dict(espacio=abs(t["absorbida"]-c["absorbida"]),tiempo=abs(f["absorbida"]-t["absorbida"]),
                       vacio=f["vacio_saldo"],flujo_inventario=f["cierre_max"],
                       espera=f["cambio_220_a_240"],separacion=f["corte_100_110"])
            u=max(terms.values())
            m[x]=dict(U=u,componentes=terms,senal_sobre_U=f["absorbida"]/u,
                signo_y_resolucion=bool(f["absorbida"]>3*u),nucleo_puerto=bool(abs(f["anillo"])<=max(3*u,1e-8)))
        gates[label]=m
    gates["a010"]=first["incertidumbre_empirica"]["a010"]
    ratios={}
    for a,b in itertools.combinations(ALL,2):
        ratios[a+"_"+b]=abs(measured["fina"][a]["fraccion_absorbida"]/measured["fina"][b]["fraccion_absorbida"]-1)
    balances=all(r["derivas_"+s]["E"]<2e-4 and r["derivas_"+s]["Q"]<1e-9 for grid in measured.values()
                 for r in grid.values() for s in ("gota","vacio","gemelo"))
    ok=balances and max(ratios.values())<.25 and all(v["signo_y_resolucion"] and v["nucleo_puerto"]
                               for point in gates.values() for v in point.values())
    result=dict(status="ACCESO_FINITO_RESUELTO_EN_TRES_AMPLITUDES" if ok else "RANGO_MENOR_NO_SUPERA_LA_PUERTA",
        amplitudes=ALL,mediciones=measured,incertidumbre_empirica=gates,discrepancias_fraccion_absorbida=ratios,
        balances_aprobados=bool(balances),habilita_disenar_paso3=bool(ok),ciclo_realizado=False,
        pronostico_lineal=json.loads((BASE/"BANDA.json").read_text())["fraccion_absorcion_lineal"])
    dump(work/"AMPLITUD_MENOR.json",result)
    return result


def snapshot(work):
    inputs=HERE/"insumos"
    data=HERE/"datos"
    inputs.mkdir(exist_ok=True)
    data.mkdir(exist_ok=True)
    for mesh in GRIDS:
        if mesh!="fina":
            for case in ("gemelo","preparacion"):
                shutil.copyfile(work/mesh/case/"estado.npz",inputs/(mesh+"_"+case+".npz"))
        with ZipFile(data/(mesh+"_series.zip"),"w",compression=ZIP_DEFLATED) as z:
            for label in NEW:
                for medium in ("gota","vacio"):
                    case=medium+"_"+label
                    member=ZipInfo(case+"/serie.csv",date_time=(1980,1,1,0,0,0))
                    z.writestr(member,(work/mesh/case/"serie.csv").read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
                    if mesh=="fina":
                        shutil.copyfile(work/mesh/case/"estado.npz",data/(case+".npz"))
    sources={}
    for mesh in GRIDS:
        for case in ("gemelo","preparacion"):
            p=BASE/"datos"/(case+".npz") if mesh=="fina" else inputs/(mesh+"_"+case+".npz")
            sources[mesh+"/"+case]=dict(archivo=str(p.relative_to(BASE)),sha256=sha(p))
    dump(HERE/"INSUMOS.json",sources)
    shutil.copyfile(work/"AMPLITUD_MENOR.json",HERE/"RESULTADO.json")
    files=[*data.iterdir(),*inputs.iterdir(),HERE/"RESULTADO.json",HERE/"contraste.py",HERE/"INSUMOS.json"]
    dump(HERE/"RECUPERACION.json",dict(archivos={str(p.relative_to(HERE)):dict(sha256=sha(p),bytes=p.stat().st_size)
                                         for p in sorted(files)},
        prerregistro_sha256=sha(BASE/"PRERREGISTRO_AMPLITUD_MENOR.md"),
        primer_manifiesto_sha256=sha(BASE/"MANIFIESTO.json")))


def verify():
    m=json.loads((HERE/"RECUPERACION.json").read_text())
    assert sha(BASE/"PRERREGISTRO_AMPLITUD_MENOR.md")==m["prerregistro_sha256"]
    assert sha(BASE/"MANIFIESTO.json")==m["primer_manifiesto_sha256"]
    for p,rec in m["archivos"].items():
        assert (HERE/p).stat().st_size==rec["bytes"] and sha(HERE/p)==rec["sha256"],p
    result=json.loads((HERE/"RESULTADO.json").read_text())
    grid=Grid(GRIDS["fina"][0])
    f,_,_=grid.equilibrium()
    from io import BytesIO
    for mesh in GRIDS:
        with (ZipFile(HERE/"datos"/(mesh+"_series.zip")) as z,
              ZipFile(BASE/"datos"/(mesh+"_series.zip")) as prior):
            twin=np.genfromtxt(BytesIO(prior.read("gemelo/serie.csv")),names=True,delimiter=",")
            for label in NEW:
                for medium in ("gota","vacio"):
                    name=medium+"_"+label
                    s=np.genfromtxt(BytesIO(z.read(name+"/serie.csv")),names=True,delimiter=",")
                    assert np.array_equal(s["tau"],twin["tau"])
                    if medium=="gota":
                        for x in ("E","Q"):
                            net=s["flujo"+x+"60"]-twin["flujo"+x+"60"]
                            rec=result["mediciones"][mesh][label][x]
                            assert abs(-net[-1]-rec["absorbida"])<1e-12
                            assert abs(-net[s["tau"]==105][0]-rec["entrada"])<1e-12
                    if mesh=="fina":
                        with np.load(HERE/"datos"/(name+".npz"),allow_pickle=False) as st:
                            assert st["tau"]==240 and st["dt"]==GRIDS[mesh][1] and st["dx"]==grid.dx
                            obs=grid.measure(np.pad(st["q"],((0,0),(1,1))),np.pad(st["v"],((0,0),(1,1))),f)
                            assert np.allclose(obs[:6],[s[col][-1] for col in ("E","Q","E40","Q40","E60","Q60")],rtol=2e-13,atol=2e-12)
    print(result["status"],"12 series y 4 estados finales comprobados")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("accion",choices=["ejecutar","archivar","verificar"])
    p.add_argument("trabajo",type=Path,nargs="?")
    p.add_argument("--procesos",type=int,choices=[1,2,3],default=3)
    args=p.parse_args()
    if args.accion=="ejecutar":
        args.trabajo.mkdir(parents=True,exist_ok=True)
        restore_inputs(args.trabajo)
        run(args.trabajo,args.procesos)
        print(decision(args.trabajo)["status"])
    if args.accion=="archivar":
        snapshot(args.trabajo)
    if args.accion in ("archivar","verificar"):
        verify()
