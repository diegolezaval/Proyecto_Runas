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
            if not any(part.startswith('.') for part in relative.parts):
                yield item
    Path.rglob = enumerate_canonical
    try:
        yield
    finally:
        Path.rglob = original
