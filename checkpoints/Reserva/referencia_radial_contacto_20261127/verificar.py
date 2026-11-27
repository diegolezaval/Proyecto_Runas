"""Contrastes independientes de propagación y pérdidas contra las fuentes primarias."""
import csv
import ctypes
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent


def check_integrator():
    n, omega = 3, 0.9
    c = np.array([[0., 2., -2., -3., -5., 1., 2., -.3, .6],
                  [1., 3., -3., -1., -4., 2., 4., .4, -.2],
                  [2., 4., -1., -2., -3., 3., 6., -.1, .7]])
    size = 3*n
    gen = np.zeros((2*size+1, 2*size+1))
    gen[:size, size:2*size] = np.eye(size)
    for i, (lo, hi, a, b, z, az, za, sa, sz) in enumerate(c):
        j = 3*i
        block = np.array([[a, 0, az], [0, b, 0], [za, 0, z]])
        ix = slice(j, j+3)
        iv = slice(j+size, j+size+3)
        gen[iv, ix] = block - np.eye(3)*(hi+(lo if i else 0))
        if i:
            gen[iv, j-3:j] = np.eye(3)*lo
        if i+1 < n:
            gen[iv, j+3:j+6] = np.eye(3)*hi
        gen[iv, iv] = [[0, 2*omega, 0], [-2*omega, 0, 0], [0, 0, 0]]
        gen[iv, -1] = [sa, 0, sz]
    initial = np.r_[np.linspace(-.3, .4, 2*size), 1.]
    exact = (expm(.5*gen) @ initial)[:-1]
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        lib = Path(tmp)/"test.so"
        subprocess.run(["cc", "-O3", "-ffp-contract=off", "-shared", "-fPIC",
                        str(HERE/"tangente.c"), "-lm", "-o", str(lib)], check=True)
        step = ctypes.CDLL(str(lib)).advance
        ptr = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
        step.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ptr, ptr, ptr]
        step.restype = None
        for count in (10, 20, 40):
            x, v = initial[:size].copy(), initial[size:-1].copy()
            step(n, count, .5/count, omega, c, x, v)
            errors.append(np.max(abs(np.r_[x, v]-exact)))
            step(n, count, -.5/count, omega, c, x, v)
            assert np.max(abs(np.r_[x, v]-initial[:-1])) < 2e-13
    ratios = np.array(errors[:-1])/errors[1:]
    assert np.all((ratios > 3.9) & (ratios < 4.1))
    return ratios.tolist()


def check_observations():
    result = json.loads((HERE/"resultado.json").read_text())
    packed = gzip.decompress((HERE/"series.csv.gz").read_bytes())
    assert hashlib.sha256(packed).hexdigest() == result["sha256_series"]
    raw = HERE/"series.csv"
    if raw.exists():
        assert raw.read_bytes() == packed
    rows = list(csv.DictReader(packed.decode().splitlines()))
    assert len(rows) == 1288
    trajectories = {}
    for row in rows:
        key = (row["preparacion"], row["caso"], float(row["dt"]))
        trajectories.setdefault(key, []).append(float(row["s"]))
        assert all(np.isfinite(float(v)) for k, v in row.items() if k not in ("caso","preparacion") and v)
    assert len(trajectories) == 8 and all(ts == [i/4 for i in range(161)] for ts in trajectories.values())
    r = {(row["caso"], float(row["s"])): row for row in rows
         if row["preparacion"] == "dt0005" and float(row["dt"]) == .0025}
    root = HERE.parent/"mision_paquete_negativo_20261125/datos/principal"
    def archive(case):
        with (root/case/"serie.csv").open() as stream:
            return {int(float(a["s"])): a for a in csv.DictReader(stream)}
    loaded, twin = archive("cargada_sin"), archive("gemela_sin")
    for key, measures in result["controles"].items():
        diffs = []
        for t in range(41):
            physical = (float(loaded[0][key])-float(loaded[t][key]))-(float(twin[0][key])-float(twin[t][key]))
            model = float(r["gota_a010", t]["perdida_"+key])-float(r["gemelo", t]["perdida_"+key])
            diffs.append(abs(model-physical))
        assert abs(max(diffs)-measures["max_error"]) < 1e-15
        assert diffs.index(max(diffs)) == measures["s_max"]
    return len(rows)


if __name__ == "__main__":
    print("Razones frente a expm:", check_integrator())
    print("Filas verificadas:", check_observations(), "· 164 comparaciones con las series primarias")
