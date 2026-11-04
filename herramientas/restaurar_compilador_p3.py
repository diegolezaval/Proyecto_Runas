"""Recupera el compilador registrado de P3 en un prefijo privado, sin M2."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'trazabilidad/continuidad_20261104/RESTAURACION_COMPILADOR.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', type=Path, required=True)
    parser.add_argument('--paquetes-desde', type=Path)
    args = parser.parse_args()
    destination = args.destino.resolve()
    if destination.is_relative_to(ROOT):
        raise ValueError('El prefijo con binarios debe quedar fuera del árbol Git')
    destination.mkdir(parents=True, exist_ok=False)
    record = json.loads(RECORD.read_text())
    package_dir = destination / 'debs'
    package_dir.mkdir()
    prefix = destination / 'root'
    prefix.mkdir()
    receipts = []
    for expected in record['packages']:
        name = expected['name']
        if Path(name).name != name:
            raise ValueError('Nombre de paquete no canónico')
        package = package_dir / name
        url = record['official_build'] + '/+files/' + name
        if args.paquetes_desde:
            shutil.copyfile(args.paquetes_desde / name, package)
        else:
            with urllib.request.urlopen(url, timeout=60) as source, package.open('xb') as out:
                shutil.copyfileobj(source, out, 1024 * 1024)
        if package.stat().st_size != expected['bytes'] or digest(package) != expected['sha256']:
            raise ValueError('Paquete no coincide con identidad registrada: ' + name)
        subprocess.run(['dpkg-deb', '-x', str(package), str(prefix)], check=True)
        receipts.append(dict(expected, source_url=url))
    bin_dir = destination / 'bin'
    bin_dir.mkdir()
    compiler = bin_dir / 'cc'
    compiler.symlink_to(prefix / 'usr/bin/x86_64-linux-gnu-gcc-13')
    version = subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0]
    if version != record['cc_version'] or digest(compiler) != record['compiler_real_sha256']:
        raise ValueError('Ejecutable o versión de compilador distintos')
    receipt = dict(passed=True, packages=receipts, compiler_version=version,
        compiler_sha256=digest(compiler), bin_directory=str(bin_dir),
        registration_sha256=digest(RECORD), recovery_code_sha256=digest(Path(__file__)),
        M2_steps_executed=0, scientific_sources_changed=False,
        numerical_environment_still_requires_original_audits=True, CP12_closed=False)
    (destination / 'RECIBO.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
