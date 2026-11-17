"""Ejecutar y acreditar los contrastes de validación CP12/P4 en GitHub."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

from .campana_hospedada import download, published_asset, upload
from .infra import Destinations, Git, REPO, Stop, Timings, asset_identity, asset_url
from .infra import digest, encoded, install, now, read, record, require, sha
from .p4_tercera_fisica import METRICS
from .p4_tercera_hospedada import make_capsule, unzip, verify_payload
from .preparacion import environment
from .p4_validacion_fisica import Contrast

ROOT = "checkpoints/CP12/p4_20261115/validacion_20261116"
STATE = f"{ROOT}/ESTADO.json"
REGISTRATION = f"{ROOT}/REGISTRO.json"
REF = "refs/heads/ciencia/cp12-p4-validacion"
ADMIN = "administracion/cp12-p4-validacion"
ACTIVATION = Path(__file__).with_name("ACTIVAR_P4_VALIDACION.json")
WORKFLOW = ".github/workflows/cp12-p4-validacion.yml"


class Context:
    def __init__(self, room):
        self.room = room
        room.mkdir(parents=True, exist_ok=False)
        self.git = Git(Path.cwd())
        self.trigger = read(ACTIVATION)
        require(os.environ["GITHUB_REPOSITORY"] == REPO and os.environ["GITHUB_REF"] == "refs/heads/" + ADMIN,
                "La ejecución no pertenece a la rama de validación")
        self.head = self.git.head(REF)
        self.prereg = self.git.pin(self.trigger["preregistration_commit"])
        raw = self.git.get(self.prereg, REGISTRATION)
        self.hash = digest(raw)
        require(raw == self.git.get(self.head, REGISTRATION) and self.hash == self.trigger["registration_sha256"],
                "Registro distinto de la activación")
        self.reg = json.loads(raw)
        self.uuid = self.reg["campaign_uuid"]
        require(self.uuid == self.trigger["campaign_uuid"] and self.reg["registered_before_M2"]
                and self.reg["new_M2_steps"] == 0, "La activación no corresponde al prerregistro")
        self.third = self.git.pin(self.reg["source_third_mesh_commit"])
        self.pilot = self.git.pin(self.reg["source_pilot_commit"])
        self.galerkin = self.git.pin(self.reg["source_galerkin_commit"])
        self.base_dir = self.reg["source_third_mesh_dir"]
        self.third_reg = self.room / "BASE_REGISTRO.json"
        self.reg_file = self.room / "REGISTRO.json"
        install(self.reg_file, raw)
        install(self.third_reg, self.git.get(self.third, self.base_dir + "/REGISTRO.json"))
        for path, digest_expected in self.reg["source_files_sha256"].items():
            commit = self.third if path.startswith(self.base_dir + "/") else self.galerkin
            require(digest(self.git.get(commit, path)) == digest_expected, "Cambió la evidencia de origen")
        self.home = room / "origen"
        self.destinations = Destinations(room, room, Timings())
        self.hosted = dict(run_id=int(os.environ["GITHUB_RUN_ID"]), attempt=int(os.environ["GITHUB_RUN_ATTEMPT"]),
                           admin_commit=os.environ["GITHUB_SHA"])

    def head_now(self):
        self.head = self.git.head(REF)
        return self.head

    def read(self, path, *, missing=False, head=None):
        return self.git.json(head or self.head, path, missing=missing)

    def publish(self, files, message, *, reservation=None):
        paths = {k: v.encode("utf-8") if isinstance(v, str) else encoded(v) for k, v in files.items()}
        for retry in range(16):
            head = self.head_now()
            if reservation:
                path, previous = reservation
                if self.read(path, missing=True, head=head) != previous:
                    return False
            try:
                self.head = self.git.publish(head, paths, message, ref=REF, partial_clone=True)
                return True
            except Stop:
                if self.head_now() == head and retry >= 2:
                    raise
            except subprocess.TimeoutExpired:
                if retry >= 2:
                    raise
            time.sleep(.5 + .3 * retry)
        raise RuntimeError("No se confirmó la publicación en la rama de validación")

    def identity(self, case):
        return dict(campaign_uuid=self.uuid, registration_sha256=self.hash, case=case)

    def state(self, case):
        identity = self.identity(case)
        state = self.read(f"{ROOT}/casos/{case}/ESTADO.json", missing=True)
        if state is None:
            return dict(**identity, status="ORIGEN_PENDIENTE", last_closed_time=None, latest=None, pending=None)
        require(all(state[k] == value for k, value in identity.items()), "Estado de otra trayectoria")
        return state

    def terminal(self):
        return self.read(STATE)["status"] in {"SUSPENDIDA", "COMPLETADA_TAU160"}

    def prepare(self):
        spec = read(self.third_reg)["pilot_frontiers"]["0"]
        raw = self.git.get(self.pilot, spec["receipt"])
        rec = json.loads(raw)
        binding = rec["recovery"]["original_audits"]["boundary"]
        require(digest(raw) == spec["receipt_sha256"] and rec["passed"] and binding["passed"]
                and rec["M2_steps_executed"] == binding["M2_steps_executed"] == 0
                and rec["github_asset_id"] == spec["asset_id"] and rec["sha256"] == spec["archive_sha256"]
                and rec["browser_download_url"] == spec["asset_url"] == asset_url(rec["file_name"])
                and rec["bytes"] == spec["bytes"] and binding["time"] == 0, "Origen del piloto sin acreditar")
        unzip(get_archive(rec, self.room / "piloto.zip"), self.home)
        source = SimpleNamespace(head=self.pilot, frontier_receipt=rec["recovery"])
        self.env, self.fingerprint = environment(self.git, source, self.destinations,
                                                  self.destinations.assets(), self.room)
        os.environ.update(self.env)

    def baseline(self, t):
        rx = self.git.json(self.third, f"{self.base_dir}/tau{t:04d}/RECUPERACION_PUBLICA.json")
        reg = read(self.third_reg)
        identity = {k: reg[k] for k in ("execution_uuid", "execution_run_id")}
        require(all(rx[k] == value for k, value in identity.items()) and rx["passed"]
                and rx["time"] == t and rx["M2_steps_executed"] == 0
                and rx["independently_downloaded_without_authentication"]
                and rx["all_payload_hashes_verified_before_and_after"], "La malla base no tiene un cierre válido")
        base = self.room / f"base-{t:04d}"
        if not base.exists():
            unzip(get_archive(rx, base.with_suffix(".zip")), base)
        verify_payload(base, identity)
        state = base / "ESTADO.npz"
        require(sha(state) == rx["state_sha256"], "Archivo base distinto de su recibo")
        return state, rx

    def previous_attempt(self, reservation):
        root = f"repos/{REPO}/actions/runs/{reservation['run_id']}/attempts/{reservation['attempt']}"
        run = github(root)
        jobs = github(root + "/jobs?per_page=100", paginate=True)
        require(run["status"] == "completed" and run["head_branch"] == ADMIN
                and run["path"].split("@", 1)[0] == WORKFLOW and run["id"] == reservation["run_id"]
                and run["run_attempt"] == reservation["attempt"] and jobs
                and all(j["status"] == "completed" for j in jobs), "Falta acreditar el fin del intento anterior")
        return {k: run[k] for k in ("id", "run_attempt", "status", "conclusion", "updated_at", "html_url")}


def github(path, paginate=False):
    args = ["gh", "api", path]
    if paginate:
        args.extend(("--paginate", "--slurp"))
    data = json.loads(subprocess.check_output(args, timeout=100))
    return [j for page in data for j in page["jobs"]] if paginate else data


def get_archive(receipt, path):
    url = receipt["browser_download_url"]
    require(url == asset_url(url.rsplit("/", 1)[-1]), "Adjunto fuera de la Release")
    return download(dict(browser_download_url=url, size=receipt["bytes"], digest="sha256:" + receipt["sha256"]), path)


class Series:
    def __init__(self, ctx, case, target, slot):
        self.ctx, self.case, self.target = ctx, case, target
        self.identity = ctx.identity(case)
        self.prefix = f"{ROOT}/casos/{case}"
        self.state_path = f"{self.prefix}/ESTADO.json"
        self.claim_path = f"{self.prefix}/reservas/TAU{target:04d}.json"
        self.claim = dict(**self.identity, **ctx.hosted, slot=slot, target=target, registered_at=now())
        self.room = ctx.room / case
        self.room.mkdir()

    def reserve(self):
        ctx = self.ctx
        ctx.head_now()
        self.state = ctx.state(self.case)
        if ctx.terminal() or (self.state["last_closed_time"] is not None
                              and self.state["last_closed_time"] >= self.target):
            return False
        previous = ctx.read(self.claim_path, missing=True)
        if previous:
            if all(previous[k] == ctx.hosted[k] for k in ("run_id", "attempt")):
                return False
            self.claim["ended_attempt"] = ctx.previous_attempt(previous)
        self.claim["frontier"] = self.state["latest"]
        owned = ctx.publish({self.claim_path: self.claim}, f"CP12/P4 {self.case}: reserva de tramo a τ{self.target}",
                            reservation=(self.claim_path, previous))
        if owned:
            self.state = ctx.state(self.case)
            print(json.dumps(self.claim), flush=True)
        return owned

    def change(self, files, verb):
        self.state["updated_at"] = now()
        self.ctx.publish(dict(files, **{self.state_path: self.state}), f"CP12/P4 {self.case}: {verb}")

    def unpack(self, receipt, room):
        recovered = room / "recuperada"
        unzip(get_archive(receipt, room / "descarga.zip"), recovered)
        count = verify_payload(recovered, self.identity)
        require(sha(recovered / "ESTADO.npz") == receipt["state_sha256"], "Estado descargado distinto")
        return recovered, count

    def close(self, pending, asset, room):
        ctx = self.ctx
        t = pending["target"]
        asset_identity(asset, pending)
        proof = dict(pending, github_asset_id=asset["id"], browser_download_url=asset["browser_download_url"])
        recovered, count = self.unpack(proof, room)
        base, rec = ctx.baseline(t)
        audit_path = room / "AUDITORIA.json"
        result = subprocess.run([sys.executable, "-m", "cp12_reanudacion.p4_validacion_fisica",
            "--registration", str(ctx.reg_file), "--third-registration", str(ctx.third_reg), "--home", str(ctx.home),
            "--case", self.case, "--folder", str(recovered), "--baseline", str(base), "--output", str(audit_path)],
            env=ctx.env, check=False)
        require(result.returncode in (0, 2) and audit_path.is_file(), "Falló la auditoría administrativa")
        audit = read(audit_path)
        require(audit["state_sha256"] == pending["state_sha256"] and audit["M2_steps_executed"] == 0
                and audit["DOP853_construction_or_step_attempts"] == 0
                and audit["passed"] == (result.returncode == 0)
                and verify_payload(recovered, self.identity) == count, "La auditoría no acredita el adjunto")
        proof.update(time=audit["time"], passed=audit["passed"], audited_by=ctx.hosted, M2_steps_executed=0,
                     independent_download=True, payload_files=count, audit=audit["passed"],
                     baseline_asset=rec["github_asset_id"], baseline_sha256=rec["sha256"])
        directory = f"{self.prefix}/tau{t:04d}"
        receipt_path = f"{directory}/RECUPERACION_PUBLICA.json"
        files = {receipt_path: proof, f"{directory}/PUERTAS.json": audit,
                 f"{directory}/EVOLUCION.json": read(recovered / "EVOLUCION.json")}
        self.state["pending"] = None
        if audit["passed"]:
            self.state.update(status="VERIFICADA", last_closed_time=t,
                              latest=dict(time=t, receipt=receipt_path, sha256=proof["sha256"]))
            self.change(files, f"acreditar τ{t}")
            return recovered / "ESTADO.npz"
        self.state.update(status="SUSPENDIDA", failure=receipt_path)
        ctx.head_now()
        general = ctx.read(STATE)
        if general["status"] != "SUSPENDIDA":
            general.update(status="SUSPENDIDA", failed_case=self.case, failure=receipt_path,
                           last_valid_time=self.state["last_closed_time"], updated_at=now())
            files[STATE] = general
        self.change(files, f"conservar el fallo a τ{t}")
        return None

    def restore(self):
        if self.state["pending"]:
            pending = self.state["pending"]
            asset = published_asset(pending)
            if asset:
                return self.close(pending, asset, self.room)
        frontier = self.state["latest"]
        if frontier is None:
            return None
        proof = self.ctx.read(frontier["receipt"])
        require(proof["passed"] and proof["M2_steps_executed"] == 0
                and proof["time"] == frontier["time"] == self.state["last_closed_time"]
                and proof["sha256"] == frontier["sha256"]
                and all(proof[k] == value for k, value in self.identity.items()), "Frontera de reinicio no acreditada")
        recovered, _ = self.unpack(proof, self.room)
        archived = read(recovered / "ENTORNO.json")
        fingerprints = ("packages", "blas", "solver", "compiler_sha256")
        require(all(archived[key] == self.ctx.fingerprint[key] for key in fingerprints),
                "El entorno numérico difiere del cierre anterior")
        return recovered / "ESTADO.npz"

    def run(self):
        ctx = self.ctx
        trial = Contrast(ctx.reg_file, ctx.third_reg, ctx.home, self.case)
        last_file = self.restore()
        first = 0 if self.state["last_closed_time"] is None else self.state["last_closed_time"] + 8
        for target in range(first, self.target + 1, 8):
            ctx.head_now()
            if ctx.terminal():
                return
            bucket = self.room / f"tau{target:04d}"
            local = bucket / "local"
            if target == 0:
                trial.variant.origin(local)
            else:
                trial.variant.advance(last_file, target, local)
            record(local / "ENTORNO.json", ctx.fingerprint)
            record(local / "RESERVA.json", self.claim)
            state_sha = sha(local / "ESTADO.npz")
            archive = bucket / (f"CP12_P4_VALIDACION_{ctx.uuid}_{self.case}_TAU{target:04d}_"
                                f"{ctx.hosted['run_id']}_{ctx.hosted['attempt']}_{state_sha[:12]}.zip")
            make_capsule(local, archive, self.identity)
            pending = dict(**self.identity, **ctx.hosted, target=target, file_name=archive.name,
                           bytes=archive.stat().st_size, sha256=sha(archive), state_sha256=state_sha,
                           previous=self.state["latest"])
            self.state["pending"] = pending
            self.change({}, f"registrar envío de τ{target}")
            last_file = self.close(pending, upload(archive, ctx.destinations), bucket)
            print(json.dumps(dict(case=self.case, target=target, valid=last_file is not None)), flush=True)
            if last_file is None:
                return


def certified(ctx, case, t):
    state = ctx.state(case)
    path = f"{ROOT}/casos/{case}/tau{t:04d}"
    rec = ctx.read(path + "/RECUPERACION_PUBLICA.json")
    proof = ctx.read(path + "/PUERTAS.json")
    binding = ctx.identity(case)
    require(state["last_closed_time"] is not None and state["last_closed_time"] >= t
            and all(all(item[k] == v for k, v in binding.items()) for item in (proof, rec))
            and proof["time"] == rec["time"] == t
            and proof["M2_steps_executed"] == rec["M2_steps_executed"] == 0
            and rec["independent_download"] and proof["passed"] and rec["passed"]
            and proof["state_sha256"] == rec["state_sha256"] and all(proof["physical"].values()),
            f"Cierre τ{t} de {case} sin acreditar")
    return proof, dict(receipt=path + "/RECUPERACION_PUBLICA.json", asset=rec["github_asset_id"], sha256=rec["sha256"])


def phases(reg):
    return {kind: [case for case, spec in reg["cases"].items() if spec["kind"] == kind]
            for kind in ("temporal", "robustez")}


def workers(ctx, phase, target, slot):
    if ctx.terminal():
        return
    names = list(ctx.reg["cases"]) if phase == "previo" else phases(ctx.reg)[phase]
    offset = (slot-1) % len(names)
    prepared = False
    for case in names[offset:] + names[:offset]:
        series = Series(ctx, case, target, slot)
        if not series.reserve():
            continue
        if not prepared:
            ctx.prepare()
            prepared = True
        series.run()


def finish(ctx, general):
    names = phases(ctx.reg)
    ref = ctx.git.json(ctx.galerkin, ctx.reg["source_galerkin_dir"] + "/RESULTADO.json")
    mesh = ctx.git.json(ctx.third, ctx.base_dir + "/RESULTADO.json")
    pilot = ctx.git.json(ctx.pilot, "checkpoints/CP12/p4_20261115/piloto_t0_t160/tramo_0152_0160/VALIDACION_FINAL.json")
    require(ref["all_nominal"] and ref["all_robust_margins"] and ref["reference_absolute_precision"]
            and mesh["original_gate_passed"] and mesh["physical_gates_passed"] and pilot["passed"],
            "El expediente de origen carece de una puerta aprobada")
    times = range(8, 161, 8)
    temporal = [ctx.read(f"{ROOT}/temporal/TAU{t:04d}.json") for t in times]
    require(all(x["passed"] and x["campaign_uuid"] == ctx.uuid and x["registration_sha256"] == ctx.hash
                for x in temporal), "Falta la decisión de estabilidad de un corte")
    robustness = {}
    for case in names["robustez"]:
        checkpoints = [certified(ctx, case, t) for t in times]
        robustness[case] = dict(configuration=ctx.reg["cases"][case]["configuration"],
            trials=[dict(proof, backup=backup) for proof, backup in checkpoints])
    scope = dict(config=ctx.reg["base_configuration"], terminal_time=160, source_CP04=read(ctx.third_reg)["original_Cauchy"],
                 Galerkin_empirical=True, robustness_at_fixed_h=True, sensitivity_scope="Variantes de un eje a la vez.")
    result = dict(schema="CP12_P4_VALIDACION_RESULTADO_V1", campaign_uuid=ctx.uuid, registration_sha256=ctx.hash,
                  status="COMPLETADA_TAU160", decision="CIERRE_EN_ALCANCE_P4_REGISTRADO", sources=dict(
                      pilot=ctx.pilot, third_mesh=ctx.third, Galerkin=ctx.galerkin), domain=scope,
                  temporal=temporal, robustness=robustness, all_registered_physical_gates_passed=True,
                  CP12_closed=True, correction_validated=True)
    phase = METRICS[-1]
    table = ["# CP12/P4 · Estabilidad, robustez y decisión", "",
             "Los controles del piloto, el refinamiento espacial y la referencia independiente constan en sus registros. "
             "Se aprobó el presupuesto temporal en los veinte cortes de la malla candidata.", "",
             "| τ | χ fase PASO | χ fase TOL | Suma | Presupuesto |",
             "| --- | --- | --- | --- | --- |"]
    for row in temporal[-6:]:
        x = (row["axes"]["PASO"][phase], row["axes"]["TOL"][phase], row["sum"][phase], row["budget"][phase])
        table.append(f"| {row['time']} | " + " | ".join(f"{100*v:.8f} %" for v in x) + " |")
    table += ["", "| Variante | χ fase en τ160 | Máximo χ fase τ120–160 | Puertas físicas |",
              "| --- | --- | --- | --- |"]
    for case, data in robustness.items():
        late = [row for row in data["trials"] if row["time"] >= 120]
        table.append(f"| {case} | {100*late[-1]['metrics'][phase]:.8f} % | "
                     f"{100*max(x['metrics'][phase] for x in late):.8f} % | Aprobadas |")
    table += ["", "Las variantes miden sensibilidad a configuración a h=.03125. Los cambios frente a la base "
              "se publican por reloj, banda y modo. La lectura angular compara los modos comunes y registra "
              "los añadidos. La lectura de amplitud conserva la respuesta normalizada de cada semilla.", "",
              "El cierre queda circunscrito a la semilla CP04, R=220, L=4, ε=.020 y τ≤160. "
              "Los contrastes respaldan E02, E03 y RES0 en ese alcance de estabilidad y sensibilidad.", "",
              "[Resultado y recibos](RESULTADO.json) · [Prerregistro](PRERREGISTRO.md) · "
              "[Referencia Galerkin](../referencia_galerkin_20261116/INFORME.md)", ""]
    general.update(status="COMPLETADA_TAU160", result=f"{ROOT}/RESULTADO.json", report=f"{ROOT}/INFORME.md",
                   last_temporal=160, last_robustness=160, CP12_closed=True, correction_validated=True, updated_at=now())
    progress = ctx.read("estado_progreso.json")
    progress["delivery_boundary"] = "CP12/P4 validado hasta τ160 en la configuración registrada."
    progress["next_calculation"] = "Paso 1 completado. Examinar el expediente de validación y su alcance."
    progress["next_actions"][0] = progress["next_calculation"]
    progress["current_operational_state"].update(CP12_status="CERRADO_EN_ALCANCE_P4", P4_status="VALIDADO_TAU160",
                                                 observed_at_utc=now(), validation_result=f"{ROOT}/RESULTADO.json")
    for stage in progress["stages"]:
        if stage.get("id") in ("E02", "E03", "RES0"):
            stage["CP12_P4_scope_evidence"] = f"{ROOT}/RESULTADO.json"
    ctx.publish({STATE: general, f"{ROOT}/RESULTADO.json": result, f"{ROOT}/INFORME.md": "\n".join(table),
                 "estado_progreso.json": progress}, "CP12/P4: cerrar el expediente de validación en τ160")


def verify(ctx, phase, t):
    ctx.head_now()
    general = ctx.read(STATE)
    if general["status"] == "COMPLETADA_TAU160":
        return 0
    if general["status"] == "SUSPENDIDA":
        print(json.dumps(general), flush=True)
        return 2
    groups = phases(ctx.reg)
    names = list(ctx.reg["cases"]) if phase == "previo" else groups[phase]
    checks = {k: certified(ctx, k, t) for k in names}
    if phase == "previo":
        require(all(checks[k][0]["preflight"]["passed"] for k in names), "Controles previos incompletos")
        evidence = dict(campaign_uuid=ctx.uuid, registration_sha256=ctx.hash, passed=True,
                        M2_steps_executed=0, cases={k: checks[k][1] for k in names})
        if general["status"] == "PRERREGISTRADA":
            general.update(status="CONTROLES_APROBADOS", preflight=f"{ROOT}/CONTROL_PREVIO.json", updated_at=now())
            ctx.publish({STATE: general, general["preflight"]: evidence}, "CP12/P4: acreditar los seis orígenes")
    elif phase == "temporal":
        axes = {name: checks[name][0]["metrics"] for name in names}
        total = {k: sum(x[k] for x in axes.values()) for k in METRICS}
        budget = ctx.reg["temporal_budget"][str(t)]["limit"]
        passed = all(total[k] <= budget[k] for k in METRICS)
        result = dict(campaign_uuid=ctx.uuid, registration_sha256=ctx.hash, time=t, axes=axes, sum=total, budget=budget,
                      passed=passed, M2_steps_executed=0, receipts={k: checks[k][1] for k in names},
                      balances={k: checks[k][0]["balances"] for k in names})
        path = f"{ROOT}/temporal/TAU{t:04d}.json"
        if passed and not ctx.read(path, missing=True):
            general.update(status="ESTABILIDAD_APROBADA" if t == 160 else "ESTABILIDAD_EN_CURSO",
                           last_temporal=t, updated_at=now())
            ctx.publish({STATE: general, path: result}, f"CP12/P4: acreditar presupuesto temporal en τ{t}")
        if not passed:
            general.update(status="SUSPENDIDA", failure=path, last_valid_time=t-8, updated_at=now())
            ctx.publish({STATE: general, path: result}, f"CP12/P4: conservar el fallo temporal en τ{t}")
            return 2
    elif t == 160:
        finish(ctx, general)
    elif t > general.get("last_robustness", 0):
        general.update(status="ROBUSTEZ_EN_CURSO", last_robustness=t, updated_at=now())
        ctx.publish({STATE: general}, f"CP12/P4: acreditar los contrastes de robustez hasta τ{t}")
    print(json.dumps(dict(phase=phase, t=t, passed=True)), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("previo", "temporal", "robustez"))
    parser.add_argument("--until", required=True, type=int)
    parser.add_argument("--slot", type=int)
    args = parser.parse_args()
    require(args.until in range(0, 161, 8) and (args.phase == "previo") == (args.until == 0),
            "Objetivo incompatible con la fase")
    ctx = Context(args.work.resolve())
    if args.slot:
        workers(ctx, args.phase, args.until, args.slot)
        return 0
    return verify(ctx, args.phase, args.until)


if __name__ == "__main__":
    raise SystemExit(main())
