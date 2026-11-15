"""D1/D2 de P3 sobre cápsulas verificadas. Nunca inicia un integrador."""

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

if os.environ.get("OPENBLAS_CORETYPE") or sys.flags.optimize:
    raise RuntimeError("Se exige BLAS sin arquitectura forzada y comprobaciones activas.")
os.environ.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
sys.dont_write_bytecode = True

import numpy as np
from scipy.integrate import DOP853
from scipy.integrate._ivp.base import OdeSolver
from threadpoolctl import threadpool_info

import diagnostico_d1 as d1
import diagnostico_d2 as d2

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STATE = "outputs/MIXTO_par_estado.npz"
PROOF = "outputs/procedencia.json"
CONFIG = "configuration.json"
METRICS = (
    "norm_relative_sup_error",
    "final_complex_nonradial_field_error_over_initial_norm",
    "final_phi_phase_space_error_over_initial_norm",
    "final_mediator_nonradial_error_over_initial_norm",
    "final_mediator_phase_space_error_over_initial_norm",
)


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, data, compact=False):
    def native(value):
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
        raise TypeError(type(value).__name__)

    path.write_text(
        json.dumps(data, default=native, ensure_ascii=False, allow_nan=False,
                   indent=None if compact else 2, separators=(",", ":") if compact else None)
        + "\n",
        encoding="utf-8",
    )


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


@contextmanager
def prohibit_steps():
    from observador_causal_CP12 import Budget, GaussResponse

    methods = [(DOP853, "__init__"), (DOP853, "_step_impl"), (OdeSolver, "step"),
               (Budget, "advance"), (GaussResponse, "advance")]
    original = [(cls, name, getattr(cls, name)) for cls, name in methods]
    attempts = []
    try:
        for cls, name in methods:
            def blocked(*args, _name=f"{cls.__name__}.{name}", **kwargs):
                attempts.append(_name)
                raise RuntimeError(f"Propagación prohibida: {_name}")
            setattr(cls, name, blocked)
        yield attempts
        assert not attempts
    finally:
        for cls, name, meth in original:
            setattr(cls, name, meth)


def verify_file(path, expected, size=None):
    assert path.is_file(), path
    assert size is None or path.stat().st_size == size, path
    assert sha(path) == expected, path


def recover(repo, registration, archives, encrypted, out):
    unpacker = module("recuperacion_original", repo / registration["original_unpacker"])
    cards = registration["capsules"]
    verify_file(encrypted, cards["160"]["encrypted"]["sha256"], cards["160"]["encrypted"]["bytes"])
    inputs, reused = {}, {}
    for label, spec in cards.items():
        t = int(label)
        source = archives / spec["local_name"]
        home = out / "entradas_extraidas" / label
        manifest = unpacker.unpack(source, home, spec["sha256"], spec["bytes"])
        assert manifest["kind"] == "boundary" and manifest["observer_clock"] == t
        assert manifest["closed_boundary"] == t and manifest["capacity_probe"] is False
        assert len(manifest["files"]) == spec["payload_files"]
        for name, key in [(STATE, "state_sha256"), (PROOF, "receipt_sha256"),
                          (CONFIG, "configuration_sha256")]:
            verify_file(home / name, spec[key])

        receipt = read(repo / spec["public_receipt"])
        if t == 160:
            assert receipt["phase"] == "puerta" and receipt["last_valid_frontier"] == 152
            assert receipt["metrics"]["final_protocol"]["passed"] is False
            receipt = receipt["backup"]
            assert receipt["encrypted_asset"] == spec["encrypted"]
        assert receipt["passed"] and receipt["observer_clock"] == t
        assert receipt["sha256"] == spec["sha256"] and receipt["bytes"] == spec["bytes"]
        original = receipt["recovery"]["original_audits"]["boundary"]
        assert original["passed"] and all(original["tests"].values())
        assert original["M2_steps_executed"] == original["DOP853_construction_or_step_attempts"] == 0
        assert original["state_sha256"] == spec["state_sha256"]
        assert original["configuration_sha256"] == spec["configuration_sha256"]
        assert original["receipt_sha256"] == spec["receipt_sha256"]
        assert original["run_id"] == registration["run_id"]
        assert original["execution_uuid"] == registration["execution_uuid"]
        reused[label] = {"scope": "Original recovery audits verified against exact bytes",
                         "clock": t, "tests": len(original["tests"]),
                         "M2_steps_executed_in_recorded_recovery": original["M2_steps_executed"]}
        inputs[t] = (home, source, manifest)
    return inputs, reused


def compare_official(original, saved, configs, labels, n, work):
    """Llamada directa a compare: código, guardia, mallas y tiempos originales."""
    work.mkdir()
    path = []
    for k, (use, rows) in enumerate(zip((slice(None, n), slice(n, None)), (
            saved["rows"][:, :10], np.column_stack((saved["rows"][:, 0], saved["rows"][:, 10:]))))):
        name = work / f"grid{k}.npz"
        np.savez(name, **{key: saved[key][:, use] for key in ("q", "v", "initial_q", "initial_v")},
                 rows=rows, time=saved["time"], config=json.dumps(configs[k]), labels=np.asarray(labels, dtype=str))
        path.append(name)
    return original.compare(*path)


def load_state(home, tick, config, registration):
    with np.load(home / STATE, allow_pickle=False) as obj:
        state = {name: obj[name] for name in obj.files}
    assert float(state["time"]) == tick
    assert str(state["schema"]) == "CP12_P3_NEW_EXPERIMENT_ORIGINAL_OBSERVER_EQUATIONS"
    assert str(state["experiment_id"]) == registration["run_id"]
    assert str(state["candidate_action"]) == registration["P3_action"]
    assert json.loads(str(state["config"])) == config
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivos", type=Path, required=True)
    parser.add_argument("--cifrado", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    start(args.archivos.resolve(), args.cifrado.resolve(), args.salida.resolve())


def start(archives, encrypted, out):
    reg_path = HERE / "REGISTRO.json"
    reg = read(reg_path)
    for rel, expected in reg["registered_files_sha256"].items():
        verify_file(REPO / rel, expected)
    for lib in threadpool_info():
        assert lib["architecture"] == "SkylakeX" and lib["num_threads"] == 1
    compiler = shutil.which("cc")
    assert compiler is not None and sha(Path(compiler)) == reg["compiler_sha256"]
    assert not out.exists() and not out.is_relative_to(REPO)
    out.mkdir(parents=True)
    inputs, reused = recover(REPO, reg, archives, encrypted, out)
    home = inputs[160][0]
    original_comparator = home / reg["captured_comparator"]
    verify_file(original_comparator, reg["comparator_sha256"])
    for folder, _, _ in inputs.values():
        for name, expected in reg["capture_sha256"].items():
            verify_file(folder / name, expected)
    sys.path[:0] = [str(home / "candidate"), str(home / "science/herramientas"), str(home)]
    import observador_causal_CP12 as obs
    from continuar_no_radial_m2 import SOURCE, harmonics
    from p3_backend import MixedP3, lap_chi

    with prohibit_steps() as attempts:
        coordinator = module("auditor_P3_capturado", home / "coordinator.py")
        boundary = coordinator.audit(home, 160)
        assert boundary["passed"] and all(boundary["tests"].values())
        assert boundary["M2_steps_executed"] == boundary["DOP853_construction_or_step_attempts"] == 0
        config = read(home / CONFIG)["original_configuration"]
        configs = config["physical_configurations"]
        sims = [MixedP3(c["dx"], c["radius"], c["L"]) for c in configs]
        m = obs.model.mediator
        final = load_state(home, 160, config, reg)
        failure = read(REPO / reg["capsules"]["160"]["public_receipt"])["metrics"]
        comparator = module("comparador_original_CP10", original_comparator)
        reference = compare_official(comparator, final, configs, sims[1].labels, sims[0].n,
                                     out / "entradas_comparador")
        limit = reg["official_limit"]
        assert np.allclose([reference[k] for k in METRICS], [failure["comparison"][k] for k in METRICS],
                           rtol=2e-12, atol=2e-14)
        gates = {k: np.isfinite(reference[k]) and reference[k] <= limit for k in METRICS}
        assert gates == failure["prefix_pair_gates"]
        published = {r["time"]: r["comparison"] for r in
                     (read(REPO / p) for p in reg["published_prefix_metrics"])}
        published[160] = reference
        timeline, times = d1.history(final, obs.BARE, obs.COUPLED, limit, published)
        preparation = d1.seed_regularity(SOURCE, configs[0]["eps"])
        leakage = d1.angular_source_leakage(final, sims, harmonics, obs.model)
        trace, spectra, values = [], d2.OccupiedSpectra(sims, m), {}
        spectra.initial(final)
        for t in sorted(inputs):
            saved = final if t == 160 else load_state(inputs[t][0], t, config, reg)
            for name in ("initial_q", "initial_v", "coupled_angular_basis"):
                assert np.array_equal(saved[name], final[name]), (t, name)
            measures, vectors = d1.snapshot(t, saved, sims, obs, lap_chi, published[t], limit)
            trace.append(measures)
            values[t] = spectra.snapshot(t, vectors)
            print(f"τ{t}: datos de campo, observadores y espectros leídos", flush=True)
        resolution = d2.manufactured(MixedP3, lap_chi)
        spectra_path = out / "ESPECTROS_COMPLETOS.npz"
        np.savez_compressed(spectra_path, **spectra.arrays)
        assert not attempts
    for t, (folder, archive, manifest) in inputs.items():
        spec = reg["capsules"][str(t)]
        for path, meta in manifest["files"].items():
            verify_file(folder / path, meta["sha256"], meta["bytes"])
        verify_file(archive, spec["sha256"], spec["bytes"])
        reused[str(t)]["all_payload_hashes_before_and_after"] = True
        reused[str(t)]["payload_files"] = len(manifest["files"])
    verify_file(encrypted, reg["capsules"]["160"]["encrypted"]["sha256"],
                reg["capsules"]["160"]["encrypted"]["bytes"])
    for rel, expected in reg["registered_files_sha256"].items():
        verify_file(REPO / rel, expected)
    write(out / "RECUPERACION.json", {
        "registered_inputs_sha256": sha(reg_path), "inputs": reg["capsules"], "reused": reused,
        "original_independent_audit_160": boundary, "M2_steps_executed": 0,
        "propagation_attempts": attempts, "CP12_closed": False, "correction_validated": False,
    })
    write(out / "HISTORIA.json", timeline, compact=True)
    write(out / "D1.json", {"official_comparison_tau160": reference, "official_spatial_gates": gates,
                           "limit": limit, "timeline_summary": times, "snapshots": trace,
                           "seed_regularity_CP04": preparation, "instantaneous_angular_leakage": leakage,
                           "published_final_physical_gates": failure["prefix_physical_controls"],
                           "published_final_causal_gate": failure["final_protocol"]["causal"]["passed"],
                           "published_prefix_metrics": published,
                           "M2_steps_executed": 0, "correction_validated": False, "CP12_closed": False})
    write(out / "D2.json", {"initial_spectra": spectra.initial_summary, "snapshots": values,
                           "coefficients": spectra.coefficients, "manufactured": resolution,
                           "full_spectra_npz_sha256": sha(spectra_path),
                           "M2_steps_executed": 0, "correction_validated": False, "CP12_closed": False},
          compact=True)
    print(json.dumps({"official_spatial_pass": all(gates.values()), "M2_steps_executed": 0,
                      "files": {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
