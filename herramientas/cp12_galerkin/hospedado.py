"""Publicación y restauración de la referencia en GitHub Actions."""
from pathlib import Path
import argparse
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import time

from cp12_reanudacion.campana_hospedada import download, upload
from cp12_reanudacion.infra import Destinations, Git, REPO, Stop, Timings, asset_url, digest, encoded, install
from cp12_reanudacion.infra import now, read, require, sha
from cp12_reanudacion.p4_tercera_hospedada import make_capsule, unzip, verify_payload


ROOT = "checkpoints/CP12/p4_20261115/referencia_galerkin_20261116"
REFERENCE = "refs/heads/ciencia/cp12-p4-referencia-galerkin"
ADMIN = "refs/heads/administracion/cp12-p4-referencia-galerkin"
ACTIVATION = Path(__file__).with_name("ACTIVAR.json")
STATE = ROOT + "/ESTADO.json"
REGISTRATION = ROOT + "/REGISTRO.json"


class Context:
    def __init__(self, scratch):
        self.scratch = scratch
        self.root = ROOT
        self.scratch.mkdir(parents=True, exist_ok=False)
        self.git = Git(Path.cwd())
        self.activation = read(ACTIVATION)
        require(os.environ["GITHUB_REPOSITORY"] == REPO and os.environ["GITHUB_REF"] == ADMIN,
                "Trabajo fuera de la rama administrativa de la referencia")
        self.head = self.git.head(REFERENCE)
        self.prereg = self.git.pin(self.activation["preregistration_commit"])
        raw = self.git.get(self.prereg, REGISTRATION)
        require(raw == self.git.get(self.head, REGISTRATION), "El registro no coincide con el prerregistro")
        self.reg = json.loads(raw)
        require(self.reg["registered_before_M2"] and self.reg["campaign_uuid"] == self.activation["campaign_uuid"],
                "Identidad de campaña distinta")
        self.reg_hash = digest(raw)
        self.refs = self.reg["source_third_mesh_dir"]
        self.git.pin(self.reg["source_commit"])
        self.destinations = Destinations(scratch, scratch, Timings())
        self.hosted = dict(run_id=int(os.environ["GITHUB_RUN_ID"]),
                           attempt=int(os.environ["GITHUB_RUN_ATTEMPT"]), admin_commit=os.environ["GITHUB_SHA"])
        self.build = scratch / "build"
        self.build.mkdir()

    def publish(self, paths, message):
        for attempt in range(10):
            head = self.git.head(REFERENCE)
            try:
                self.head = self.git.publish(head, paths, message, ref=REFERENCE)
                return
            except Stop:
                if head == self.git.head(REFERENCE) and attempt >= 2:
                    raise
                time.sleep(.5 + .2 * attempt)
        raise RuntimeError("Git no pudo confirmar la publicación")

    def json(self, path, *, base=None, missing=False):
        commit = base if base is not None else self.git.head(REFERENCE)
        return self.git.json(commit, path, missing=missing)

    def sources(self):
        spec = self.reg["source_snapshot"]
        source = spec["asset_url"]
        require(source == asset_url(source.rsplit("/", 1)[-1]), "Origen fuera de la Release registrada")
        archive = download(dict(browser_download_url=source, size=spec["bytes"],
                                digest="sha256:" + spec["archive_sha256"]), self.scratch / "origen_piloto.zip")
        home = self.scratch / "piloto"
        unzip(archive, home)
        self.source = home / "science" / self.reg["source_Cauchy"]["path"]
        tools = home / "science/herramientas"
        require(sha(self.source) == self.reg["source_Cauchy"]["sha256"]
                and sha(tools / "continuar_no_radial_m2.py") == self.reg["source_preparation_sha256"]
                and sha(tools / "diagnosticar_mediador_CP10.py") == self.reg["source_comparator_sha256"],
                "Cauchy o lectores capturados distintos")
        self.sources_dir = tools
        sys.path.insert(0, str(tools))

    def environment(self):
        return dict(python=platform.python_version(), machine=platform.machine(),
                    packages={name: importlib.metadata.version(name) for name in ("numpy", "scipy")},
                    compiler=subprocess.check_output(["cc", "--version"], text=True).splitlines()[0],
                    numeric_flags=["-O3", "-fPIC", "-shared", "-std=c11", "-fno-fast-math"])


def preflight(ctx):
    from controles import run_controls

    ctx.sources()
    controls = run_controls(ctx.reg, ctx.source, ctx.build)
    receipt = dict(schema="CP12_P4_REFERENCIA_GALERKIN_CONTROL_V1",
                   campaign_uuid=ctx.reg["campaign_uuid"], registration_sha256=ctx.reg_hash,
                   preregistration_commit=ctx.prereg, hosted=ctx.hosted,
                   environment=ctx.environment(), **controls)
    state = ctx.json(STATE)
    require(state["campaign_uuid"] == ctx.reg["campaign_uuid"]
            and state["status"] in ("CONTROLES_PENDIENTES", "CONTROLES_APROBADOS", "CONTROLES_RECHAZADOS"),
            "El control no puede reemplazar un resultado de producción")
    state.update(status="CONTROLES_APROBADOS" if receipt["passed"] else "CONTROLES_RECHAZADOS",
                 preflight=ROOT + "/CONTROL_PREVIO.json", updated_at=now())
    ctx.publish({ROOT + "/CONTROL_PREVIO.json": encoded(receipt), STATE: encoded(state)},
                "CP12/P4 Galerkin: acreditar controles previos")
    print(json.dumps({"passed": receipt["passed"], "controls": receipt["controls"],
                      "time_controls": receipt["time_controls"]}, ensure_ascii=False), flush=True)
    return 0 if receipt["passed"] else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("preflight", "tramo", "comparar"))
    parser.add_argument("--case")
    parser.add_argument("--until", type=int)
    args = parser.parse_args()
    ctx = Context(args.work)
    if args.phase == "preflight":
        require(ctx.activation["phase"] == args.phase, "Fase ajena a la activación")
        return preflight(ctx)
    require(ctx.activation["phase"] == "production" and args.until in (8, 40, 80, 120, 160),
            "La activación de producción no coincide con este objetivo")
    control_sha = ctx.git.pin(ctx.activation["preflight_commit"])
    certificate = ctx.json(ROOT + "/CONTROL_PREVIO.json", base=control_sha)
    require(certificate["passed"] and certificate["campaign_uuid"] == ctx.reg["campaign_uuid"]
            and certificate["registration_sha256"] == ctx.reg_hash
            and certificate["M2_production_started"] is False
            and certificate["preregistration_commit"] == ctx.prereg, "Faltan controles previos aprobados")
    approved_code = ctx.git.pin(certificate["hosted"]["admin_commit"])
    for name in ("radial.py", "force.c", "fisica.py", "controles.py"):
        require((Path(__file__).with_name(name)).read_bytes() == ctx.git.get(
            approved_code, "herramientas/cp12_galerkin/" + name), "Cambió un núcleo registrado: " + name)
    if args.phase == "comparar":
        from lectura import analyze

        return analyze(ctx, args.until)
    from trayectoria import Series

    require(args.case in ctx.reg["cases"], "Brazo físico desconocido")
    ctx.sources()
    return Series(ctx, args.case).run(args.until)


if __name__ == "__main__":
    raise SystemExit(main())
