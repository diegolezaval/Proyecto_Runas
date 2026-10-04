"""Resolver enlaces de instantáneas sin editar ni reinterpretar sus bytes.

Las raíces históricas están declaradas en datos/arquitectura.json. Sólo esas
copias conservan el contexto de la raíz original; los documentos actuales
siguen resolviéndose respecto de su propia carpeta.
"""
from pathlib import Path
import json
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def snapshot_roots(root=ROOT):
    config = root / 'datos/arquitectura.json'
    if config.exists():
        return json.loads(config.read_text(encoding='utf-8'))['snapshot_document_roots']
    return ['trazabilidad/reanudacion_CP02', 'trazabilidad/CP07_entrada',
            'trazabilidad/CP07', 'trazabilidad/CP08_entrada']


def local_target(document, link, root=ROOT):
    """Devuelve el destino local o None si es URL/ancla; no hace fallback global."""
    if re.match(r'[A-Za-z][A-Za-z0-9+.-]*:', link) or link.startswith('#'):
        return None
    target = unquote(link.split('#')[0])
    if not target:
        return None
    for prefix in snapshot_roots(root):
        folder = root / prefix
        if document.is_relative_to(folder):
            original_path = document.relative_to(folder)
            return root / original_path.parent / target
    return document.parent / target


def document_links(document):
    """Los bloques de ecuaciones declarados con \\[ ... \\] no son enlaces.

    Sólo se omiten bloques con delimitadores en líneas propias; los enlaces
    documentales fuera del bloque siguen verificándose, incluidos los rotos.
    """
    content = document.read_text(encoding='utf-8')
    content = re.sub(r'(?ms)^[ \t]*\\\[[ \t]*\n.*?^[ \t]*\\\][ \t]*$', '', content)
    # Una expresión escrita como código tampoco es un enlace renderizado.
    content = re.sub(r'(?s)(`+)(.*?)\1', '', content)
    return re.findall(r'\]\(([^)]+)\)', content)


def missing_links(root=ROOT):
    missing = []
    for document in sorted(root.rglob('*.md')):
        if any(x in document.parts for x in ['.git', '.venv', '__pycache__']):
            continue
        for link in document_links(document):
            target = local_target(document, link, root)
            if target is not None and not target.exists():
                missing.append(f'{document.relative_to(root)} -> {link}')
    return missing
