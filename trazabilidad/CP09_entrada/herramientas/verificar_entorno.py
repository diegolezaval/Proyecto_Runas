"""Comprueba dependencias declaradas sin ejecutar ni modificar campañas."""
from pathlib import Path
import argparse
import importlib.metadata
import json
import platform
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def report():
    packages = []
    for line in (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines():
        line = line.split('#')[0].strip()
        if not line:
            continue
        name, expected = line.split('==', 1)
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed = None
        packages.append(dict(package=name, expected=expected, installed=installed,
                             passed=installed == expected))
    return dict(python=platform.python_version(), python_supported=sys.version_info >= (3, 11),
                platform=platform.system(), adaptive_requires_posix=True,
                adaptive_platform_supported=sys.platform != 'win32',
                optional_C_compiler=shutil.which('cc') is not None,
                packages=packages,
                passed=sys.version_info >= (3, 11) and all(x['passed'] for x in packages),
                scope='Pins del entorno de referencia. La verificación de hashes sólo requiere stdlib; la integración adaptativa usa fcntl/POSIX. La fuerza C es opcional.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adaptativo', action='store_true', help='Exigir también plataforma POSIX para fcntl')
    args = parser.parse_args()
    result = report()
    if args.adaptativo:
        result['passed'] = result['passed'] and result['adaptive_platform_supported']
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
