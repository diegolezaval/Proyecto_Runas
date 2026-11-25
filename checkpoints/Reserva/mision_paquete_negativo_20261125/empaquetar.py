"""Crea un ZIP portátil con las series, el análisis y los insumos de evolución."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


MISION = Path(__file__).resolve().parent
RAIZ = MISION.parents[2]
REL = MISION.relative_to(RAIZ)


def archivos():
    recibo = json.loads((MISION / "datos/EJECUCION.json").read_text())
    rutas = {RAIZ / ruta for ruta in recibo["insumos"]}
    reserva = MISION.parent
    dependencias = {
        "paso2_20261117": ["MANIFIESTO.json", "REPRODUCCION_INDEPENDIENTE.json", "BANDA.json"],
        "paso3_20261118": ["MANIFIESTO_RETENCION.json", "RETENCION.json", "calibrar.py", "retencion.py"],
        "mision_extraccion_radial_20261124": ["datos/EJECUCION.json", "ejecutar.py", "senal.c"]
    }
    for carpeta, nombres in dependencias.items():
        rutas.update(reserva / carpeta / n for n in nombres)
    rutas.add(RAIZ / "requirements.txt")
    for patron in ("*.md", "*.py", "*.svg", "*.csv", "*.json", "datos/*.json",
                   "datos/*/*/*.csv", "datos/referencias_tau300/*.npz"):
        rutas.update(MISION.glob(patron))
    # El recibo posterior del transporte hace referencia al ZIP ya publicado.
    rutas.discard(MISION / "RECIBO_GITHUB.json")
    return sorted(rutas)


def guardar(ruta):
    leeme = (
        "# Reserva · ensayo del paquete negativo en Φ\n\n"
        f"El informe y los comandos de reproducción están en `{REL}/README.md`.\n\n"
        "Desde esta carpeta, `sha256sum -c HUELLAS_PAQUETE.sha256` comprueba la descarga. "
        "Las 50 series permiten rehacer el análisis. Los insumos permiten regenerar las seis "
        "preparaciones amplias y los 25 estados finales, también publicados individualmente en la rama.\n"
    )
    huellas = []
    with ZipFile(ruta, "w") as archivo:
        def escribir(nombre, contenido):
            info = ZipInfo(nombre, (2026, 11, 25, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archivo.writestr(info, contenido, compresslevel=6)
        def incluir(nombre, contenido):
            escribir(nombre, contenido)
            huellas.append(f"{hashlib.sha256(contenido).hexdigest()}  {nombre}\n")
        incluir("LEEME.md", leeme.encode())
        for p in archivos():
            incluir(p.relative_to(RAIZ).as_posix(), p.read_bytes())
        escribir("HUELLAS_PAQUETE.sha256", "".join(huellas).encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("salida", type=Path, nargs="?", default=MISION / "Reserva_paquete_negativo_reproducible.zip")
    guardar(parser.parse_args().salida)
