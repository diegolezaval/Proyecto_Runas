"""Contrasta una repetición física con los SHA-256 del recibo de producción."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(ruta):
    with ruta.open("rb") as archivo:
        return hashlib.file_digest(archivo, "sha256").hexdigest()


def productos(recibo):
    archivos = {}
    for item in recibo["series"]:
        prefijo = Path(item["replica"], item["caso"])
        archivos[prefijo / "serie.csv"] = item["sha256_serie"]
        archivos[prefijo / "sondas.csv"] = item["sha256_sondas"]
        archivos[prefijo / f"s{item['fin_s']}.npz"] = item["sha256_estado_final"]
    for item in recibo["origenes"]:
        if "comparacion_amplia" in item:
            archivos[Path(item["archivo"])] = item["sha256"]
    if len(archivos) != 81:
        raise ValueError("Se esperaban 50 CSV, 25 estados finales y seis preparaciones amplias")
    return archivos


def cotejar(base, repeticion):
    if base.resolve() == repeticion.resolve():
        raise ValueError("La producción y la repetición deben tener directorios distintos")
    recibos = [d / "EJECUCION.json" for d in (base, repeticion)]
    original, nueva = [json.loads(p.read_text()) for p in recibos]
    for clave in ("prerregistro", "A", "mallas", "insumos", "sha256_recibo_preparaciones", "sha256_diseno"):
        if original[clave] != nueva[clave]:
            raise ValueError(f"Cambió el origen o parámetro {clave}")
    referencias = [
        {(x["R"], x["h"], x["caso"]): x["sha256"] for x in rec["origenes"] if "comparacion_amplia" not in x}
        for rec in (original, nueva)
    ]
    if len(referencias[0]) != 4 or referencias[0] != referencias[1]:
        raise ValueError("Discrepancia entre las cuatro referencias históricas")
    archivos = productos(original)
    if archivos != productos(nueva):
        raise ValueError("Las huellas en los dos recibos difieren")
    comprobados_en_base = 0
    for nombre, esperado in sorted(archivos.items()):
        if sha(repeticion / nombre) != esperado:
            raise ValueError(f"Datos de la repetición distintos en {nombre}")
        if (base / nombre).is_file():
            if sha(base / nombre) != esperado:
                raise ValueError(f"Datos de producción distintos en {nombre}")
            comprobados_en_base += 1
    lista = "".join(f"{h}  {p.as_posix()}\n" for p,h in sorted(archivos.items()))
    return {
        "prerregistro": original["prerregistro"], "amplitud": original["A"],
        "recibos_sha256": dict(produccion=sha(recibos[0]), repeticion=sha(recibos[1])),
        "ejecucion_independiente": {
            "inicio_utc": nueva["inicio_utc"], "fin_utc": nueva["fin_utc"],
            "segundos": nueva["segundos"], "trabajadores": nueva["jobs"],
            "pasos_posteriores_a_tau300": sum(v["pasos"] for v in nueva["series"]),
            "preparaciones_nuevas_desde_tau0": 6, "referencias_historicas": len(referencias[0])
        },
        "productos_releidos_produccion": comprobados_en_base, "productos_releidos_repeticion": len(archivos),
        "series_y_sondas_identicas": 50, "estados_finales_identicos": 25, "preparaciones_amplias_identicas": 6,
        "sha256_lista_ordenada_de_productos": hashlib.sha256(lista.encode()).hexdigest()
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repeticion", type=Path)
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent / "datos")
    parser.add_argument("--recibo", type=Path)
    args = parser.parse_args()
    texto = json.dumps(cotejar(args.base, args.repeticion), indent=2, ensure_ascii=False) + "\n"
    if args.recibo:
        args.recibo.write_text(texto)
    print(texto, end="")
