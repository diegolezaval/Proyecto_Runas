"""Reconstruye en un directorio limpio los estados completos, usando sólo entradas públicas."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CASE=HERE.relative_to(ROOT)
SUB=Path("amplitud_menor")
RECEIPT=Path("REPRODUCCION_INDEPENDIENTE.json")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def raw_record(first,second):
    files={p:v for p,v in first["archivos"].items() if p.startswith("datos/")}
    files.update({str(SUB/p):v for p,v in second["archivos"].items() if p.startswith(("insumos/","datos/"))})
    return files


def copy_files(src,dst,paths):
    for rel in paths:
        p=dst/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src/rel,p)


def compare(reference,actual):
    differences={}
    def check(group,a,b):
        error=abs(a-b)
        tolerance=1e-8+1e-7*max(abs(a),abs(b))
        if error>tolerance:
            raise ArithmeticError((group,a,b,error,tolerance))
        differences[group]=max(differences.get(group,0.),error)
    for folder,name in ((Path("."),"CONTACTO.json"),(SUB,"RESULTADO.json")):
        x,y=(read(base/folder/name) for base in (reference,actual))
        assert x["status"]==y["status"] and x["habilita_disenar_paso3"]==y["habilita_disenar_paso3"]
        assert y["balances_aprobados"]
        for grid,rows in x["mediciones"].items():
            for case,r in rows.items():
                test=y["mediciones"][grid][case]
                for unit in ("E","Q"):
                    for key in ("entrada","reflejada","absorbida","nucleo","puerto"):
                        check(unit+"_"+key,r[unit][key],test[unit][key])
                check("fraccion_absorbida",r["fraccion_absorbida"],test["fraccion_absorbida"])
    x,y=(read(base/"ESTABILIDAD.json") for base in (reference,actual))
    assert x["aprobada"] and y["aprobada"]
    for g,mesh in x["mallas"].items():
        for case,r in mesh["casos"].items():
            for key in ("Q40_final","incremento_ext_max","flujo_E40_neto","error_perfil_max"):
                check(key,r[key],y["mallas"][g]["casos"][case][key])
    x,y=(read(base/"CONTACTO.json")["preparacion"] for base in (reference,actual))
    for g in x:
        assert x[g]["aprobada"] and y[g]["aprobada"]
        for key in ("E","Q","trabajo_Phi","trabajo_chi","carga_fuente"):
            check("preparacion_"+key,x[g][key],y[g][key])
    check("prediccion_lineal",read(reference/"BANDA.json")["fraccion_absorcion_lineal"],
          read(actual/"BANDA.json")["fraccion_absorcion_lineal"])
    return differences


def generate(out):
    if out.exists():
        raise FileExistsError(out)
    first=read(HERE/"MANIFIESTO.json")
    second=read(HERE/SUB/"RECUPERACION.json")
    with TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        root=tmp/"repo"
        work=tmp/"resultados"
        case=root/CASE
        for rel,digest in first["entradas"].items():
            assert sha(ROOT/rel)==digest,rel
        copy_files(ROOT,root,first["entradas"])
        scripts=[p for p in first["archivos"] if p.endswith((".py",".c",".md"))]
        copy_files(HERE,case,scripts+["PRERREGISTRO_AMPLITUD_MENOR.md",str(SUB/"contraste.py")])
        assert sha(case/"PRERREGISTRO_AMPLITUD_MENOR.md")==second["prerregistro_sha256"]
        def run(*args,cwd=case):
            subprocess.run([sys.executable,"-u",*map(str,args)],cwd=cwd,check=True)
        run("ensayo.py","estabilidad",work)
        run("ensayo.py","contacto",work)
        run("banda.py",work/"BANDA.json")
        run("evidencia.py","archivar",work)
        # Aquí los gemelos y las preparaciones acaban de calcularse en el mismo ejecutor.
        # El módulo confirmatorio usa estos estados, conservando el primer negativo.
        run("-c","import sys; from pathlib import Path; import contraste as c; "
            "w=Path(sys.argv[1]); c.run(w,3); c.decision(w); c.snapshot(w); c.verify()",work,cwd=case/SUB)
        diff=compare(HERE,case)
        original=raw_record(first,second)
        replica=raw_record(read(case/"MANIFIESTO.json"),read(case/SUB/"RECUPERACION.json"))
        if set(replica)!=set(original):
            raise ValueError("Inventarios de datos distintos")
        for rel,entry in replica.items():
            assert sha(case/rel)==entry["sha256"] and (case/rel).stat().st_size==entry["bytes"]
        copy_files(case,out,replica)
        for rel in ("ESTABILIDAD.json","CONTACTO.json","BANDA.json","MANIFIESTO.json",
                    str(SUB/"RESULTADO.json"),str(SUB/"RECUPERACION.json"),str(SUB/"INSUMOS.json")):
            copy_files(case,out/"reproduccion",[rel])
        equal=[p for p in sorted(replica) if replica[p]==original[p]]
        status=dict(estado="ESTADOS_COMPLETOS_REPRODUCIDOS",commit_de_fuentes=os.getenv("GITHUB_SHA"),
            accion=os.getenv("GITHUB_RUN_ID"),origen="Perfil, parámetros, ecuaciones y protocolos públicos de la rama.",
            archivos=replica,coincidencias_byte_a_byte_con_la_primera_ejecucion=equal,
            diferencias_maximas_observables=diff,criterio_absoluto=1e-8,criterio_relativo=1e-7,
            resumen="36 series, 13 estados finos (uno preparado y doce finales) y cuatro estados auxiliares para reanudar los contrastes.",
            decisiones=["CONTACTO_FINITO_NO_SUPERA_LA_PUERTA","ACCESO_FINITO_RESUELTO_EN_TRES_AMPLITUDES"])
        (out/RECEIPT).write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n")
        verify(out)


def verify(out):
    import numpy as np
    from zipfile import ZipFile
    from io import BytesIO
    status=read(out/RECEIPT)
    orig=raw_record(read(HERE/"MANIFIESTO.json"),read(HERE/SUB/"RECUPERACION.json"))
    assert set(status["archivos"])==set(orig)
    series=states=0
    for rel,entry in status["archivos"].items():
        p=out/rel
        assert p.stat().st_size==entry["bytes"] and sha(p)==entry["sha256"],rel
        if p.suffix==".npz":
            with np.load(p,allow_pickle=False) as s:
                assert s["q"].shape==s["v"].shape==(3,round(256/float(s["dx"])))
                assert np.isfinite(s["q"]).all() and np.isfinite(s["v"]).all()
                assert s["tau"]==(0. if "preparacion" in p.stem else 240.)
            states+=1
        else:
            with ZipFile(p) as z:
                assert z.testzip() is None
                for name in z.namelist():
                    rows=np.genfromtxt(BytesIO(z.read(name)),names=True,delimiter=",")
                    assert np.array_equal(rows["tau"],np.arange(481)/2)
                    series+=1
    assert (series,states)==(36,17)
    print(f"{series} series, {states} estados completos y {len(status['coincidencias_byte_a_byte_con_la_primera_ejecucion'])}/{len(orig)} archivos idénticos")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion",choices=("generar","verificar"))
    parser.add_argument("ruta",type=Path)
    args=parser.parse_args()
    if args.accion=="generar":
        generate(args.ruta.resolve())
    else:
        verify(args.ruta.resolve())
