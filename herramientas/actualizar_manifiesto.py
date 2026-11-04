"""Regenera y verifica el manifiesto con las funciones del empaquetador."""
import argparse
import importlib.util
import json
from pathlib import Path


def refresh(root):
    root = root.resolve()
    spec = importlib.util.spec_from_file_location('empaquetador_registrado', root / 'herramientas/checkpoint.py')
    packager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packager)
    state = packager.validate_context()
    manifest = root / 'MANIFIESTO_SHA256.json'
    hashes = {p.relative_to(root).as_posix(): packager.digest(p) for p in packager.files() if p != manifest}
    data = dict(algorithm='SHA256', edition=state['project_version'], checkpoint=state['checkpoint'],
        scientific_checkpoint=state.get('scientific_checkpoint', state['checkpoint']),
        excluded=packager.EXCLUDED, files=hashes)
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return packager.verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raiz', type=Path, default=Path(__file__).resolve().parents[1])
    print(json.dumps(refresh(parser.parse_args().raiz), ensure_ascii=False))
