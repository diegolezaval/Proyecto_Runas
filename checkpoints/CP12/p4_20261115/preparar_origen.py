"""Armar una instancia P4 de τ0 desde una cápsula pública autenticada de P3."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
P3 = REPO / "checkpoints/CP12/p3_20261018"
sys.path.insert(0, str(HERE / "prueba_pasiva"))
from prueba_pasiva import HISTORY, read, sha, verify_file, write
from diagnosticar import module


ACTION = "Phi_original_FV_chi_fixed_A2_plus_h2_A2_squared_over_12_plus_h4_A2_cubed_over_90_plus_h6_A2_fourth_over_560"
ROOT_SOURCES = ("coordinator.py", "controlador_transporte.py", "transporte.py", "preservation.py",
                "seleccion_canonica.py", "CONTROLES_SINTETICOS.json", "CONTROL_ADAPTACION_ESTATICA.json")
ORIGINAL_META = ("identidad_cientifica_original.json", "RESULTADO_CAUSAL_ORIGINAL.json",
                 "CONTROLES_REUTILIZADOS.json", "antecedente_tau160.json")


def coordinator_p4(ancestor, dest):
    source = ancestor.read_text(encoding="utf-8")
    substitutions = {
        "h4_A2_cubed_over_90": "h4_A2_cubed_over_90_plus_h6_A2_fourth_over_560",
        "fixed positive cubic composition": "fixed positive quartic composition",
        "p3_backend": "p4_backend",
        "lap_mixed_p3": "lap_mixed_p4",
        "P3": "P4",
    }
    for a, b in substitutions.items():
        if a not in source:
            raise ValueError(f"No se encontró la ruta original {a}")
        source = source.replace(a, b)
    compile(source, str(dest), "exec")
    dest.write_text(source, encoding="utf-8")


def assemble(source, home, certificate):
    prior = read(HISTORY / "REGISTRO.json")
    archived = prior["capsules"]["112"]
    reg = read(HERE / "REGISTRO_PREFLIGHT.json")
    tested = read(certificate)
    assert tested["all_registered_preflight_controls_passed"] and not tested["DOP853_attempts"]
    assert tested["M2_steps_executed"] == 0 and tested["registration_sha256"] == sha(HERE / "REGISTRO_PREFLIGHT.json")
    assert all(tested["CP10_Cauchy_exact"]) and all(p["passed"] for p in tested["controls"].values())
    for rel, digest in reg["sources_sha256"].items():
        verify_file(REPO / rel, digest)
    if home.exists():
        raise FileExistsError(home)
    unpacker = module("cp12_unpack_origen_p4", REPO / prior["original_unpacker"])
    with __import__("tempfile").TemporaryDirectory(dir=home.parent) as scratch:
        ancestor = Path(scratch) / "P3_112"
        manifest = unpacker.unpack(source, ancestor, archived["sha256"], archived["bytes"])
        assert manifest["closed_boundary"] == manifest["observer_clock"] == 112
        assert len(manifest["files"]) == archived["payload_files"] and not manifest["capacity_probe"]
        for name, digest in prior["capture_sha256"].items():
            verify_file(ancestor / name, digest)
        home.mkdir(mode=0o700)
        ignore = shutil.ignore_patterns("cache", "__pycache__", "*.so", "*.pyc")
        for rel in ("science", "prior", "candidate"):
            shutil.copytree(ancestor / rel, home / rel, ignore=ignore)
        for rel in ("runtime/tmp", "runtime/force", "runtime/pycache", "outputs", "transport", "proofs",
                    "administracion_continuacion_20261030", "negative", "analysis", "capsules", "recoveries"):
            (home / rel).mkdir(parents=True)
        for name in ROOT_SOURCES:
            if name == "coordinator.py":
                coordinator_p4(ancestor / name, home / name)
            else:
                shutil.copyfile(ancestor / name, home / name)
        for name, path in (("p4_backend.py", HERE / "p4_backend.py"),
                           ("operador_pasivo.py", HERE / "prueba_pasiva/operador_pasivo.py"),
                           ("diagnostico_d2.py", HISTORY / "diagnostico_d2.py")):
            shutil.copyfile(path, home / "candidate" / name)
        prelim = home / "preregistration"
        shutil.copytree(ancestor / "preregistration/administration", prelim / "administration", ignore=ignore)
        for name in ORIGINAL_META:
            shutil.copyfile(ancestor / "preregistration" / name, prelim / name)
        shutil.copyfile(certificate, prelim / "preflight_certificate.json")
        for name in ("PRERREGISTRO_PILOTO.md", "REGISTRO_PREFLIGHT.json"):
            shutil.copyfile(HERE / name, prelim / name)
        historic = read(ancestor / "configuration.json")
        historic.update(schema="CP12_P4_PREREGISTERED_PHYSICAL_PILOT", action=ACTION,
                        global_eighth_order_claim=False, formal_radial_order=2,
                        fixed_dimensionless_polynomial_coefficients=[1., 1/12, 1/90, 1/560])
        historic.pop("global_sixth_order_claim", None)
        write(home / "configuration.json", historic)
        for name, data in manifest["files"].items():
            verify_file(ancestor / name, data["sha256"], data["bytes"])
    verify_file(source, archived["sha256"], archived["bytes"])
    capture = {p.relative_to(home).as_posix(): sha(p)
               for p in sorted(home.rglob("*")) if p.is_file() and p.relative_to(home).parts[0]
               not in ("science", "prior", "runtime")}
    uid = reg["execution_uuid"]
    run = hashlib.sha256(json.dumps(dict(execution_uuid=uid, sources=capture), sort_keys=True).encode()).hexdigest()
    branch = reg["scientific_branch"]
    write(prelim / "nueva_identidad.json", dict(execution_uuid=uid, execution_run_id=run, branch=branch,
          run_relative="outputs", initial_frontier=0, supervision_source_sha256=capture["coordinator.py"],
          captured_sources=capture, kind="NEW_CP12_P4"))
    write(prelim / "ubicacion.json", dict(execution_uuid=uid, branch=branch,
          scientific_source_asset=archived["github_asset_id"], execution_home=str(home)))
    write(prelim / "registro_publico.json", dict(registered_before_M2=True, captured_sources=capture,
                                               physical_steps_executed=0))
    write(home / "outputs/procedencia.json", dict(schema="CP12_NEW_P4_NUMERICAL_TRIAL_RECEIPT",
          execution_run_id=run, execution_uuid=uid, kind="P4_CHI_QUARTIC", physical_initial_time=0,
          time=0., status="NO_INICIADA", segments=[], physical_accepted_steps=[0, 0], output_hashes={},
          original_CP10_reproduction=False, correction_validated=False, CP12_closed=False))
    return dict(execution_uuid=uid, execution_run_id=run, captured_sources=capture)


def prepare(source, home, cert, out):
    identity = assemble(source, home, cert)
    env = dict(os.environ, TMPDIR=str(home / "runtime/tmp"), PYTHONPYCACHEPREFIX=str(home / "runtime/pycache"))
    result = subprocess.run([sys.executable, "-B", str(home / "coordinator.py"),
                             "--home", str(home), "--prepare-only"],
                            env=env, check=True, capture_output=True, text=True)
    audit = json.loads(result.stdout)
    assert audit["passed"] and audit["M2_steps_executed"] == audit["DOP853_construction_or_step_attempts"] == 0
    assert audit["time"] == 0 and audit["execution_uuid"] == identity["execution_uuid"]
    assert audit["run_id"] == identity["execution_run_id"]
    ignores = {"runtime", "cache", "__pycache__"}
    files = {p.relative_to(home).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size)
             for p in sorted(home.rglob("*")) if p.is_file()
             and not ignores.intersection(p.relative_to(home).parts)
             and p.suffix not in (".pyc", ".so", ".tmp")}
    write(home / "MANIFIESTO_NEGATIVO.json", dict(schema="CP12_P4_TAU0_INIT_V1", closed_boundary=0, files=files))
    write(out, dict(schema="CP12_P4_IDENTIDAD_TAU0_V1", **identity, audit=audit,
                    source_state_hash=sha(home / "outputs/MIXTO_par_estado.npz"), M2_steps_executed=0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archivo", "instancia", "certificado", "recibo"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    prepare(args.archivo.resolve(), args.instancia.resolve(), args.certificado.resolve(), args.recibo.resolve())
