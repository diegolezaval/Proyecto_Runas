"""Auditoría de las series pasivas, sin integración de campos."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "mision_paquete_negativo_20261125"
REPLICAS = ("principal", "temporal", "espacial", "caja576")
CASES = ("cargada_sin", "gemela_sin")
CHANNELS = ("E", "Q")
REGIONS = ("40", "60", "corona")


def read(path):
    return json.loads(path.read_text())


def require(test, detail):
    if not test:
        raise ValueError(detail)


def maximum(x):
    return float(np.max(np.abs(x)))


def means(x):
    return [float(np.trapezoid(x[a:b+1])/(b-a))
            for a, b in ((400, 480), (400, 440), (440, 480))]


def inputs():
    receipt = read(SRC / "datos/EJECUCION.json")
    prior = read(SRC / "BALANCES.json")
    data, hashes, overlap = {}, {}, {}
    for m in (*REPLICAS, "archivo416"):
        end = receipt["mallas"][m][-1]
        require(end == (300 if m == "archivo416" else 480), m)
        require(prior["primeros_retornos"][m]["60"]["historico"] > end, m)
        for c in CASES:
            path = SRC/"datos"/m/c/"serie.csv"
            key = f"{m}/{c}"
            hashes[key] = hashlib.sha256(path.read_bytes()).hexdigest()
            records = [r for r in receipt["series"] if (r["replica"], r["caso"]) == (m,c)]
            require(len(records)==1 and records[0]["sha256_serie"]==hashes[key], key)
            d = np.genfromtxt(path, names=True, delimiter=",")
            require(np.isfinite(d.view(np.float64)).all(), key)
            require(np.array_equal(d["s"], np.arange(end+1)) and
                    np.array_equal(d["tau"], 300+d["s"]) and not np.any(d["W"]), key)
            require(all(d["F"+k+r][0]==0 for k in CHANNELS for r in ("40","60")), key)
            data[m,c] = d
    for c in CASES:
        overlap[c] = {}
        for col in ("FE40","FE60","FQ40","FQ60"):
            value = maximum(data["archivo416",c][col]-data["principal",c][col][:301])
            require(abs(value-prior["max_abs_solapamiento_bruto_s0_300"][c][col])<1e-18,col)
            overlap[c][col] = value
    return data, hashes, overlap, prior


def curves(d, k):
    inner, outer = d[k+"40"], d[k+"60"]
    f, g = d["F"+k+"40"], d["F"+k+"60"]
    # Las tres columnas son inventario, flujo saliente y pérdida por inventario.
    shell = outer-inner
    return {"40":(inner,f,inner[0]-inner), "60":(outer,g,outer[0]-outer),
            "corona":(shell,g-f,shell[0]-shell)}


def run():
    data, hashes, overlap, prior = inputs()
    design = read(SRC/"DISENO_ESPECTRAL.json")
    summaries, limits = {}, {}
    with (HERE/"series_auditadas.csv").open("w", newline="") as out:
        writer = csv.writer(out,lineterminator="\n")
        writer.writerow(("replica","rama","canal","region","s","inventario","flujo_neto","perdida_inventario","residuo"))
        for k in CHANNELS:
            summaries[k], limits[k] = {}, {}
            for m in REPLICAS:
                states = {c:curves(data[m,c],k) for c in CASES}
                states["delta"] = {r:tuple(a-b for a,b in zip(states[CASES[0]][r],states[CASES[1]][r])) for r in REGIONS}
                block = summaries[k][m] = {}
                for c, state in states.items():
                    block[c] = {}
                    for r,(x,flux,loss) in state.items():
                        err = flux-loss
                        closure = maximum(err)
                        if c in CASES:
                            tag = "corona_"+k if r=="corona" else k+r
                            reference = prior["por_trayectoria"][m][c]["max_abs_cierre"][tag]
                            require(abs(closure-reference)<1e-11,(m,c,k,r,closure,reference))
                        block[c][r] = dict(X0=x[0], X480=x[-1], inventario=means(x),
                            flujo=means(flux), perdida=means(loss), residuo=means(err), cierre=closure)
                        writer.writerows((m,c,k,r,s,x[s],flux[s],loss[s],err[s]) for s in range(len(x)))
            for c in (*CASES,"delta"):
                limits[k][c] = {}
                for r in REGIONS:
                    rows = {m:summaries[k][m][c][r] for m in REPLICAS}
                    av = {m:t["flujo"][0] for m,t in rows.items()}
                    y = av["principal"]
                    involved = CASES if c=="delta" else (c,)
                    components = dict(espacio=abs(av["espacial"]-av["temporal"]),
                        tiempo=abs(av["temporal"]-y), caja=abs(av["caja576"]-y),
                        mitades=max(abs(t["flujo"][i]-t["flujo"][0]) for t in rows.values() for i in (1,2)),
                        cierres_individuales=max(sum(summaries[k][m][case][r]["cierre"] for case in involved) for m in REPLICAS),
                        desacuerdo=max(t["cierre"] for t in rows.values()), piso=1e-10)
                    u = max(components.values())
                    lo,hi = y-3*u,y+3*u
                    threshold = design["umbral"][k]
                    limits[k][c][r] = dict(media=y,U=u,inferior=lo,superior=hi,
                        porcentaje_stock=[100*n/design["stock"][k] for n in (lo,y,hi)],
                        fuga_positiva=bool(lo>0), objetivo="debajo" if hi<threshold else
                        "supera" if lo>threshold else "indeterminado", componentes=components)
    votes = [limits[k]["delta"][r]["objetivo"] for k in CHANNELS for r in ("40","60")]
    verdict = "cerrada" if "debajo" in votes else "habilita_diseno" if all(v=="supera" for v in votes) else "indeterminada"
    result = dict(origen="9c8091ea99a9305301e3abffab0b2c1a92d48dfd",huellas=hashes,
                  solapamiento=overlap, ventanas=[[400,480],[400,440],[440,480]],
                  stock=design["stock"],umbral=design["umbral"],resumen=summaries,
                  cotas=limits,via_pasiva=verdict,
                  sha256_csv=hashlib.sha256((HERE/"series_auditadas.csv").read_bytes()).hexdigest())
    (HERE/"resultado.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n")


if __name__ == "__main__":
    run()
