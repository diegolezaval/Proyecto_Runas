"""Restrict backup enumeration to canonical payload files; no numerical calls."""
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def canonical_selection(home):
    home = home.resolve()
    original = Path.rglob
    def enumerate_canonical(path, pattern, *args, **kwargs):
        for item in original(path, pattern, *args, **kwargs):
            try:
                relative = item.relative_to(home)
            except ValueError:
                yield item
                continue
            inherited_manifest = len(relative.parts) == 1 and relative.name in (
                'MANIFIESTO_NEGATIVO.json', 'MANIFIESTO_RECUPERACION_INDEPENDIENTE.json')
            if not inherited_manifest and not any(part.startswith('.') for part in relative.parts):
                yield item
    Path.rglob = enumerate_canonical
    try:
        yield
    finally:
        Path.rglob = original
