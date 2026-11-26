"""Contraste reproducible de tres fondos de Reserva con un espectro físico fijo."""
import csv
import hashlib
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / "mision_paquete_negativo_20261125"
sys.path.insert(0, str(PREVIOUS))
import diseno
import dispersion_reserva_m2 as scattering

PROFILES = (.895, .900, .905)
STEPS = (.0125, .00625)
FREQ = np.round(1 + np.arange(91) * .01, 2)
PRIMARY = "h0.00625_d1_L4096"


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solve_at(profile, f, h, radius=60):
    # El solucionador escribe la solución completa. Se libera después de extraer
    # las probabilidades y controles que necesita la cuadratura.
    with TemporaryDirectory() as folder, redirect_stdout(io.StringIO()):
        scattering.O = Path(folder)
        row = scattering.solve(float(round(profile + f, 8)), h, radius, profile)
    if not row["balance_passed"]:
        raise ArithmeticError(row["configuration"])
    case = next(c for c in row["cases"] if c["incoming_channel"] == 1)
    return [case["outgoing_probabilities"][0], row["unitary_error"],
            row["linear_residual_relative"]]


def sample(central):
    rows = []
    for profile in PROFILES:
        for h in STEPS:
            for physical in FREQ[1:]:
                if profile == .900:
                    p, unitary, residual = central[h, round(profile + physical, 5)]
                else:
                    p, unitary, residual = solve_at(profile, physical, h)
                if not (0 <= p <= 1 and unitary < 1e-8 and residual < 1e-9):
                    raise ArithmeticError((profile, physical, h, p, unitary, residual))
                rows.append(dict(omega=profile, h=h, f_abs=physical, P=p,
                                 defecto_unitariedad=unitary, residuo_relativo=residual))
    return rows


def integrate(rows, design):
    spectra = {L: diseno.espectro(float(L)) for L in (2048, 4096)}
    E = design["E_paquete_vacio"]
    estimates = {w: {} for w in PROFILES}
    for w in PROFILES:
        for h in STEPS:
            probs = np.r_[0., [row["P"] for row in rows if row["omega"] == w and row["h"] == h]]
            for stride in (1, 2):
                for length, (freq, weight, _) in spectra.items():
                    prob = np.interp(freq, FREQ[::stride], probs[::stride], right=0.)
                    yq = 2 * E * np.sum(weight * prob / freq)
                    estimates[w][f"h{h}_d{stride}_L{length}"] = dict(Q=float(yq), E=float(w*yq))
    f, weight, fractions = spectra[4096]
    # Cota de contribución por perfil usando unitariedad en la cola.
    tail = float(2 * E * np.sum(weight[f > FREQ[-1]] / f[f > FREQ[-1]]))
    return estimates, fractions, tail


def project(estimates, profiles, design, tail):
    pairs = []
    for a, b in zip(PROFILES[:-1], PROFILES[1:]):
        delta = profiles[b]["Q"] - profiles[a]["Q"]
        channels = {}
        for k in ("E", "Q"):
            def ratio(key):
                slope = (estimates[b][key][k] - estimates[a][key][k]) / delta
                return float(slope * design["stock"]["Q"] / design["umbral"][k])
            values = [ratio(key) for key in estimates[a]]
            central = ratio(PRIMARY)
            # Suma de cotas de cola de los dos fondos, sin postular cancelación.
            tail_factor = a+b if k == "E" else 2.
            tail_margin = tail_factor*tail/abs(delta)*design["stock"]["Q"]/design["umbral"][k]
            channels[k] = dict(
                pendiente_por_Q=(estimates[b][PRIMARY][k]-estimates[a][PRIMARY][k])/delta,
                fraccion_del_umbral=central, rango_numerico=[min(values), max(values)],
                cota_cola_en_fraccion_del_umbral=tail_margin,
                inferior_con_cola=min(values)-tail_margin, superior_con_cola=max(values)+tail_margin)
        pairs.append(dict(omega=[a, b], diferencia_Q_equilibrio=delta, canales=channels))
    return pairs


def annulus(stock):
    directory = PREVIOUS / "datos/principal"
    receipt = read(PREVIOUS / "datos/EJECUCION.json")["series"]
    names = ("cargada_con", "cargada_sin", "gemela_con", "gemela_sin")
    series = []
    for name in names:
        path = directory / name / "serie.csv"
        expected = next(row["sha256_serie"] for row in receipt
                        if row["replica"] == "principal" and row["caso"] == name)
        if digest(path) != expected:
            raise ValueError(path)
        row = np.genfromtxt(path, delimiter=",", names=True)
        if not np.array_equal(row["s"], np.arange(481)):
            raise ValueError("Eje temporal")
        series.append(row)
    def contrast(values):
        return (values[0]-values[1]) - (values[2]-values[3])
    def mean(arr):
        return float(np.trapezoid(arr[400:481]) / 80)
    out = {}
    for k in ("E", "Q"):
        flux = contrast([x["F"+k+"40"] - x["F"+k+"60"] for x in series])
        shell = [x[k+"60"] - x[k+"40"] for x in series]
        inventory = contrast([v-v[0] for v in shell])
        out[k] = dict(flujo=mean(flux), inventario=mean(inventory),
                      residuo_medio=mean(flux-inventory),
                      max_residuo_en_ventana=float(np.max(abs((flux-inventory)[400:481]))),
                      fraccion_stock=mean(inventory)/stock[k])
    return out


def run():
    design_path = PREVIOUS / "DISENO_ESPECTRAL.json"
    table_path = HERE.parent / "paso2_20261117/BANDA.json"
    branch_path = ROOT / "validacion/P06/rama/resultados.json"
    profiles = {r["omega"]: {k:r[k] for k in ("Q","E")} for r in read(branch_path)["rows"]
                if r["omega"] in PROFILES}
    design = read(design_path)
    if digest(table_path) != design["sha256_dispersion"]:
        raise ValueError(table_path)
    central = {(h,round(om,5)):(p,u,res) for h,om,p,u,res in read(table_path)["dispersion"]}
    rows = sample(central)
    estimates, fractions, tail = integrate(rows, design)
    center = estimates[.900][PRIMARY]
    relative = {k: abs(center[k]/design["prediccion"]["delta_"+k]-1) for k in center}
    if max(relative.values()) > 1e-8:
        raise ArithmeticError(relative)
    # Comparación de caja y reciprocidad central con incidencia negativa directa.
    controls = {}
    for w in PROFILES:
        p60 = next(x["P"] for x in rows if x["omega"] == w and x["h"] == STEPS[-1] and x["f_abs"] == 1.4)
        p80 = solve_at(w, 1.4, STEPS[-1], 80)[0]
        controls[w] = dict(P60=p60, P80=p80, diferencia=abs(p80-p60))
        if abs(p80-p60) > 1e-7:
            raise ArithmeticError(controls[w])
    secants = project(estimates, profiles, design, tail)
    gate = all(v["inferior_con_cola"] > 1 for pair in secants for v in pair["canales"].values())
    with (HERE/"dispersion.csv").open("w",newline="") as f:
        writer = csv.DictWriter(f,fieldnames=rows[0],lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    paths = [design_path, table_path, branch_path, Path(diseno.__file__), Path(scattering.__file__),
             ROOT/"datos/theta_comun.json", *(ROOT/f"validacion/P06/rama/perfil_w{w:.5f}.csv" for w in PROFILES)]
    result = dict(perfiles=profiles, estimaciones=estimates, principal=PRIMARY,
                  paquetes=dict(A=design["A"], nu=design["nu_incidente"], E=design["E_paquete_vacio"],
                                fracciones_E=fractions, cota_cola_Q_por_perfil=tail),
                  stock=design["stock"], umbral=design["umbral"], secantes=secants,
                  max_defecto_unitariedad=max(x["defecto_unitariedad"] for x in rows),
                  max_residuo=max(x["residuo_relativo"] for x in rows), controles_caja=controls,
                  error_relativo_reproduccion_centro=relative, corona=annulus(design["stock"]),
                  piloto_por_sensibilidad_justificado=gate,
                  sha256={str(p.relative_to(ROOT)):digest(p) for p in paths})
    (HERE/"resultado.json").write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n")


if __name__ == "__main__":
    run()
