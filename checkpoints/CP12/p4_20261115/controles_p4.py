"""Controles propios P4 que reutilizan las comparaciones independientes F0–F5."""

import argparse
from fractions import Fraction
import math
from pathlib import Path
import shutil
import sys
import traceback
from types import ModuleType

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "prueba_pasiva"))
from prueba_pasiva import block_m2, environment, HISTORY, load_state, read, sha, verify_file, write

import numpy as np


P3 = HISTORY.parent
REPO = P3.parents[2]
COMMON = (
    ("from controls_common import run, snapshots", ""),
    ("from controls_common import run, sha", ""),
    ("from controls_common import run", ""),
    ("p3_backend", "p4_backend"),
    ("MixedP3", "MixedP4"),
    ("lap_mixed_p3", "lap_mixed_p4"),
    ("20261018001", "20261115004"),
    ("20261018002", "20261115005"),
    ("P3", "P4"),
    ("mixed80", "P3_tau160"),
)


EXACT_REPLACEMENTS = {
    "F0": (
        ("from p4_backend import MixedP4, weighted_bands_p3",
         "from p4_backend import MixedP4\n    from operador_pasivo import positive_operator"),
        ("range(1, 4)", "range(1, 5)"),
        ("Fraction(1, 90)]", "Fraction(1, 90), Fraction(1, 560)]"),
        ("symbol = [x[j]+x2[j]/12+x3[j]/90 for j in range(5)]",
         "x4 = multiply(x2, x2, 4)\n    symbol = [x[j]+x2[j]/12+x3[j]/90+x4[j]/560 for j in range(5)]"),
        ("Fraction(-1, 560)", "Fraction(0)"),
        ("h**4/90*(H@H@H)", "h**4/90*(H@H@H)+h**6/560*(H@H@H@H)"),
        ("            bands = weighted_bands_p3(sim, ell)\n            actual = np.diag(bands[0])\n"
         "            for j, band in enumerate(bands[1:], 1):\n                actual += np.diag(band, j)+np.diag(band, -j)",
         "            actual = positive_operator(sim, ell).toarray()"),
        ("h**4/90*eig2**3", "h**4/90*eig2**3+h**6/560*eig2**4"),
        (":-3, index", ":-4, index"),
        ("seven_bands", "nine_bands"),
        ("global_sixth_order_claim", "global_eighth_order_claim"),
    ),
    "F1": (
        ("sim.dx**4/90*sim.lap2(sim.lap2(sim.lap2(q)))",
         "sim.dx**4/90*sim.lap2(sim.lap2(sim.lap2(q)))-sim.dx**6/560*sim.lap2(sim.lap2(sim.lap2(sim.lap2(q))))"),
    ),
    "F2": (),
    "F3": (("(h**4/90)*(H2@H2@H2)", "(h**4/90)*(H2@H2@H2)+(h**6/560)*(H2@H2@H2@H2)"),),
    "F4": (("from control_F3_matrix import", "from cp12_p4_control_F3 import"),),
    "F5": (
        ("from mixed_backend import Mixed", "from p3_backend import MixedP3"),
        ("    package = Path(__file__).resolve().parent\n"
         "    registration = json.loads((package/'ENMIENDA_F5.json').read_text())\n"
         "    assert sha(Path(__file__)) == registration['source_sha256']",
         "    registration = {'coefficient': '1/560', 'energy_coefficient': '1/1120'}"),
        ("beta = h**4/90", "beta = h**6/560"),
        ("H3x = H@(H@(H@x))", "H3x = H@(H@(H@(H@x)))"),
        ("Mixed.components(sim, q, v)", "MixedP3.components(sim, q, v)"),
        ("Mixed.components(sim, qc, v)", "MixedP3.components(sim, qc, v)"),
    ),
}


def load_control(path, phase, snapshot_reader):
    source = path.read_text(encoding="utf-8")
    for old, new in COMMON:
        source = source.replace(old, new)
    for old, new in EXACT_REPLACEMENTS[phase]:
        if source.count(old) != 1:
            raise ValueError(f"La adaptación {phase} requiere exactamente una aparición de {old}")
        source = source.replace(old, new)
    obj = ModuleType(f"cp12_p4_control_{phase}")
    obj.__file__ = str(path)
    obj.snapshots = snapshot_reader
    sys.modules[obj.__name__] = obj
    exec(compile(source, str(path), "exec"), obj.__dict__)
    return obj.control


def spectral_control(home, saved, observer, config):
    from diagnostico_d2 import bessel_wavenumbers, coefficients, frequency, weighted_spectrum
    from p4_backend import MixedP4

    grids = [MixedP4(g["dx"], g["radius"], g["L"]) for g in config["physical_configurations"]]
    coarse, fine = grids
    c = coefficients()
    assert c == [float(Fraction(1)), float(Fraction(1, 12)), float(Fraction(1, 90)), float(Fraction(1, 560))]
    evidence = []
    mu = observer.model.mediator
    for ell in (2, 4):
        k = bessel_wavenumbers(coarse.n, ell, coarse.radius)
        k = k[(k > 8) & (k*coarse.dx <= np.pi)]
        grid_info = []
        for sim, loc in zip(grids, (slice(None, coarse.n), slice(coarse.n, None))):
            lam, U, _ = weighted_spectrum(sim, ell)
            kr = bessel_wavenumbers(sim.n, ell, sim.radius)
            select = (kr > 8) & (kr*coarse.dx <= np.pi)
            assert np.array_equal(kr[select], k)
            sqrtw = np.sqrt(sim.w*(sim.r < 40))[:, None]
            chi = saved["q"][2, loc][:, sim.ell == ell]
            vel = saved["v"][2, loc][:, sim.ell == ell]
            q = U.T @ (sqrtw*chi)
            v = U.T @ (sqrtw*vel/mu)
            weight = np.sum(q*q+v*v, axis=1)[select]
            assert float(np.sum(weight)) > 0
            grid_info.append((lam[select], weight))

        def flat_freq(k, h, degree):
            squared = 4*np.sin(k*h/2)**2/h**2
            return frequency(squared, h, degree, mu)

        def group(k, h, degree):
            x = 4*np.sin(k*h/2)**2
            derivative = np.polynomial.polynomial.polyval(x, np.arange(1, degree+1)*c[:degree])
            answer = np.sin(k*h)*derivative/(h*flat_freq(k, h, degree))
            step = 1e-4
            centered = (flat_freq(k+step, h, degree)-flat_freq(k-step, h, degree))/(2*step)
            error = float(np.max(abs(answer-centered)))
            assert error <= 1e-8, error
            return answer, error

        for degree in (3, 4):
            phase = [frequency(lam, s.dx, degree, mu) for (lam, _), s in zip(grid_info, grids)]
            gv = [group(k, s.dx, degree) for s in grids]
            for index, (_, w) in enumerate(grid_info):
                rms = lambda a: float(np.sqrt(np.average(a*a, weights=w)))
                evidence.append(dict(ell=ell, degree=degree, occupation_grid_dx=grids[index].dx,
                                     radial_omega_disagreement_rms=rms(phase[0]-phase[1]),
                                     flat_group_speed_disagreement_rms=rms(gv[0][0]-gv[1][0]),
                                     maximum_group_derivative_check=max(x[1] for x in gv)))
    return evidence


def execute(home, out):
    registered = read(HERE / "REGISTRO_PREFLIGHT.json")
    for path, expected in registered["sources_sha256"].items():
        verify_file(REPO / path, expected)
    observed = environment(read(HERE / "prueba_pasiva/REGISTRO.json"))
    verify_file(Path(shutil.which("cc")), registered["compiler_sha256"])
    out.mkdir(mode=0o700, parents=True)
    manifest = read(home / "MANIFIESTO_NEGATIVO.json")
    assert manifest["closed_boundary"] == 160 and len(manifest["files"]) == 747

    def verify_inputs():
        for path, meta in manifest["files"].items():
            verify_file(home / path, meta["sha256"], meta["bytes"])

    verify_inputs()
    sys.path[:0] = [str(home / "science/herramientas"), str(home / "candidate")]
    import observador_causal_CP12 as observer
    from continuar_no_radial_m2 import seed
    from ejecutar_con_procedencia import environment as physical_environment
    from p4_backend import MixedP4
    cfg = read(home / "configuration.json")["original_configuration"]
    assert physical_environment() == read(home / "preregistration/identidad_cientifica_original.json")["environment"]
    saved = load_state(home, 160, cfg, read(HISTORY / "REGISTRO.json"))
    refs = [home / "science" / p for p in cfg["reference_states"]]

    def snapshots(root, dx):
        idx = 0 if dx == .125 else 1
        sl = slice(None, int(saved["coarse_n"])) if idx == 0 else slice(int(saved["coarse_n"]), None)
        with np.load(refs[idx], allow_pickle=False) as ref:
            return [("initial", ref["initial_q"].copy(), ref["initial_v"].copy()),
                    ("original160", ref["q"].copy(), ref["v"].copy()),
                    ("P3_tau160", saved["q"][:, sl].copy(), saved["v"][:, sl].copy())]

    with block_m2(observer) as attempts:
        seeds = []
        for cfg_grid in cfg["physical_configurations"]:
            p4 = MixedP4(cfg_grid["dx"], cfg_grid["radius"], cfg_grid["L"])
            q, v, _ = seed(p4, cfg_grid["eps"])
            _, iq, iv = snapshots(home, cfg_grid["dx"])[0]
            seeds.append(bool(np.array_equal(q, iq) and np.array_equal(v, iv)))
        assert all(seeds)
        controls = {}
        for phase, path in registered["control_templates"].items():
            stage = out / phase
            stage.mkdir()
            try:
                code = load_control(REPO / path, phase, snapshots)
                result = code(home, stage)
            except Exception as error:
                result = dict(passed=False, exception_type=type(error).__name__,
                              error=str(error), traceback=traceback.format_exc())
            # Historical F1/F2 metadata referred to the 472-file ancestor.
            result.pop("original_input_manifest_files_verified", None)
            result.update(M2_steps_executed=0, input_payload_files=747)
            write(stage / "RESULTADO.json", result)
            controls[phase] = dict(passed=bool(result["passed"]), sha256=sha(stage / "RESULTADO.json"))
            print(f"P4 {phase}: {controls[phase]['passed']}", flush=True)
            if not result["passed"]:
                break
        spectra = spectral_control(home, saved, observer, cfg) if len(controls) == 6 and all(
            result["passed"] for result in controls.values()) else []
    verify_inputs()
    for path, expected in registered["sources_sha256"].items():
        verify_file(REPO / path, expected)
    ok = bool(len(controls) == 6 and all(v["passed"] for v in controls.values()) and not attempts and spectra)
    write(out / "CERTIFICADO_CONTROLES_P4.json", dict(
        schema="CP12_P4_CONTROLES_PROPIOS_V1", all_registered_preflight_controls_passed=ok,
        controls=controls, spectrum_and_group_velocity=spectra, CP10_Cauchy_exact=seeds,
        all_input_payload_hashes_unchanged=True, M2_steps_executed=0, DOP853_attempts=attempts,
        environment=observed, registration_sha256=sha(HERE / "REGISTRO_PREFLIGHT.json")))
    return 0 if ok else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origen-lectura", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    sys.exit(execute(args.origen_lectura.resolve(), args.salida.resolve()))
