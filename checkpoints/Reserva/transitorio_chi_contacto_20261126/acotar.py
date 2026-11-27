"""Cotas del transitorio homogéneo de chi. No evoluciona M2."""
import csv
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "respuesta_chi_contacto_20261126/medidas.csv"
expected = "f97298cadedbe199e994ded5af3dea535adabf878d3a54d772533b4795ab3701"
assert hashlib.sha256(src.read_bytes()).hexdigest() == expected
with src.open(newline="") as handle:
    data = list(csv.DictReader(handle))
keys = ("dt", "donante", "d", "malla", "fase")
combos = {tuple(r[k] for k in keys) for r in data}
assert len(data) == len(combos) == 108
assert combos == set(itertools.product(*(sorted({r[k] for r in data}) for k in keys)))
M, T = 100., 240.
def bounds(C, w, v):
    assert all(math.isfinite(x) and x >= 0 for x in (C,w,v))
    assert M*M*w*w <= 2*C*(1+1e-11)
    E = C + 0.5*v*v
    R = math.sqrt(2*E)
    s, h = w/M+2*v/M**2, (R+v)/M**2
    return dict(energia_inicial=E, amplitud_L2=R/M, integral_norma_L2=T*R/M,
                integral_firmada_propagadores_L2=s, integral_firmada_extremos_L2=h,
                integral_firmada_mejor_L2=min(s,h), integral_cuadratica_L1=T*(R/M)**2)
for omega, time, w0, v0 in itertools.product((100.,101.,217.), (0.,0.051,1.,240.),
                                           (0.1,-0.3),(0.,0.22,-0.17)):
    x = omega*time
    exact = w0*math.sin(x)/omega + v0*(1-math.cos(x))/omega**2
    end = -omega*w0*math.sin(x)+v0*math.cos(x)
    b = bounds(0.5*omega**2*w0*w0,abs(w0),abs(v0))
    assert math.isclose(exact,(v0-end)/omega**2,rel_tol=1e-12,abs_tol=1e-15)
    assert abs(exact) <= b["integral_firmada_mejor_L2"] + 1e-15
rows = [{**{k:r[k] for k in keys}, **bounds(float(r["energia_cuadratica"]),float(r["norma_w"]),float(r["norma_wt"]))} for r in data]
metrics = list(rows[0])[len(keys):]
def summary(items):
    return {k:max(r[k] for r in items) for k in metrics}
print(json.dumps({"sha256_fuente":expected, "ventana_referencia":T, "M":M,
                  "controles_modo_escalar":72, "maximos":summary(rows),
                  "maximos_malla_fina":summary([r for r in rows if r["malla"]=="fina"]),
                  "filas":rows}, ensure_ascii=False, indent=2, sort_keys=True))
