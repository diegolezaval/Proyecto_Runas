"""Ejecutar o recuperar P4 h=.03125, con un solo trabajador y cierres públicos."""
import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid
import zipfile

from .campana_hospedada import download, upload
from .infra import Destinations, Git, REPO, Stop, Timings, asset_identity, asset_url
from .infra import digest, encoded, install, now, read, record, require, sha
from .p4_tercera_fisica import METRICS, PHASE


ROOT = "checkpoints/CP12/p4_20261115/tercera_malla_20261116"
STATE = ROOT + "/ESTADO_REANUDACION.json"
CLAIM = ROOT + "/REANUDADOR_ACTUAL.json"
REGISTER = ROOT + "/REGISTRO.json"
REF = "refs/heads/ciencia/cp12-p4-20261115"
ADMIN = "administracion/cp12-p4-tercera-malla"
WORKFLOW = ".github/workflows/cp12-p4-tercera-malla.yml"
START = Path(__file__).with_name("INICIAR_P4_TERCERA_MALLA.json")
TERMINAL = {"COMPLETADA_TAU160", "SUSPENDIDA_POR_PUERTA"}


def unzip(archive, destination):
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zipped:
        entries = zipped.infolist()
        require(len({x.filename for x in entries}) == len(entries), "Rutas duplicadas en la cápsula")
        for entry in entries:
            name = Path(entry.filename)
            require(not name.is_absolute() and ".." not in name.parts and "\\" not in entry.filename
                    and not stat.S_ISLNK(entry.external_attr >> 16), "Ruta ZIP inválida")
        zipped.extractall(destination)


def make_capsule(folder, output, identity):
    files = {path.name: {"sha256": sha(path), "bytes": path.stat().st_size}
             for path in sorted(folder.iterdir()) if path.is_file()}
    manifest = {"schema": "CP12_P4_TERCERA_MALLA_CAPSULA_V1", **identity, "files": files}
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_STORED) as zipped:
        for name in files:
            zipped.write(folder / name, name)
        zipped.writestr("MANIFIESTO.json", encoded(manifest))
    return output


def verify_payload(folder, identity):
    manifest = read(folder / "MANIFIESTO.json")
    require(all(manifest[k] == value for k, value in identity.items()), "Cápsula de otra malla o ejecución")
    files = {p.name for p in folder.iterdir() if p.is_file() and p.name != "MANIFIESTO.json"}
    require(files == set(manifest["files"]), "Manifiesto incompleto")
    for name, info in manifest["files"].items():
        path = folder / name
        require(path.stat().st_size == info["bytes"] and sha(path) == info["sha256"],
                "No coincide la carga " + name)
    return len(files)


def previous_attempt(claim):
    run, attempt = int(claim["actions_run_id"]), int(claim["actions_attempt"])
    answer = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{REPO}/actions/runs/{run}/attempts/{attempt}"], timeout=45))
    require(answer["id"] == run and answer["run_attempt"] == attempt and answer["status"] == "completed"
            and answer["head_branch"] == ADMIN and answer["path"].split("@", 1)[0] == WORKFLOW,
            "GitHub todavía no acredita el fin del intento de la tercera malla")
    return {key: answer[key] for key in ("id", "run_attempt", "status", "conclusion", "html_url", "updated_at")}


class Campaign:
    def __init__(self, work):
        self.work = work
        self.work.mkdir(parents=True, exist_ok=False)
        self.git = Git(Path.cwd())
        self.head = self.git.head(REF)
        self.start = read(START)
        require(self.start["activate"] and os.environ["GITHUB_REPOSITORY"] == REPO
                and os.environ["GITHUB_REF"] == "refs/heads/" + ADMIN, "Activación fuera del piloto registrado")
        self.prereg = self.start["preregistration_commit"]
        self.git.pin(self.prereg)
        registration = self.git.get(self.prereg, REGISTER)
        require(registration == self.git.get(self.head, REGISTER)
                and digest(registration) == self.start["registration_sha256"], "Cambió el prerregistro")
        self.reg_path = work / "REGISTRO.json"
        install(self.reg_path, registration)
        self.reg = json.loads(registration)
        self.git.pin(self.reg["pilot_commit"])
        self.identity = {key: self.reg[key] for key in ("execution_uuid", "execution_run_id")}
        require(self.start["execution_uuid"] == self.identity["execution_uuid"] and
                self.start["execution_run_id"] == self.identity["execution_run_id"], "Activación de otra identidad")
        self.state = self.git.json(self.head, STATE)
        require(all(self.state[k] == v for k, v in self.identity.items()), "Estado de otra identidad")
        self.claim = dict(**self.identity, actions_run_id=int(os.environ["GITHUB_RUN_ID"]),
                          actions_attempt=int(os.environ["GITHUB_RUN_ATTEMPT"]),
                          actions_slot=int(os.environ["CP12_MALLA_SLOT"]), source_head=self.head,
                          worker_id=uuid.uuid4().hex, admin_commit=os.environ["GITHUB_SHA"],
                          registration_commit=self.prereg, registered_at=now(),
                          last_verified_boundary=self.state["last_closed_boundary"])
        self.destinations = Destinations(work, work, Timings())

    def publish(self, files, message):
        self.head = self.git.publish(self.head, files, message, ref=REF)

    def own(self):
        head = self.git.head(REF)
        if self.git.json(head, STATE)["status"] in TERMINAL:
            return False
        current = self.git.json(head, CLAIM, missing=True)
        if current and (current["actions_run_id"], current["actions_attempt"]) == (
                self.claim["actions_run_id"], self.claim["actions_attempt"]):
            return False
        if current:
            evidence = previous_attempt(current)
            self.claim["previous_attempt"] = dict(evidence, prior_worker_exit_observed=False)
        self.head = head
        try:
            self.publish({CLAIM: encoded(self.claim)}, "CP12/P4 tercera malla: reservar un único trabajador")
        except Stop:
            observed = self.git.json(self.git.head(REF), CLAIM, missing=True)
            if (observed and observed["actions_run_id"] == self.claim["actions_run_id"]
                    and observed["actions_attempt"] == self.claim["actions_attempt"]):
                return False
            raise
        require(self.git.json(self.head, CLAIM) == self.claim, "La reserva publicada pertenece a otro proceso")
        self.state = self.git.json(self.head, STATE)
        print(f"Reserva exclusiva {self.claim['worker_id']} desde {self.state['last_closed_boundary']}", flush=True)
        return True

    def pilot(self, t, folder):
        spec = self.reg["pilot_frontiers"][str(t)]
        raw = self.git.get(self.reg["pilot_commit"], spec["receipt"])
        metrics = self.git.get(self.reg["pilot_commit"], spec["metric_file"])
        require(digest(raw) == spec["receipt_sha256"] and digest(metrics) == spec["metric_file_sha256"],
                "Recibo o métricas del piloto cambiaron")
        receipt = json.loads(raw)
        audit = receipt["recovery"]["original_audits"]["boundary"]
        require(receipt["passed"] and receipt["independently_downloaded_without_authentication"]
                and audit["passed"] and audit["M2_steps_executed"] == 0
                and audit["execution_uuid"] == self.reg["pilot_execution_uuid"]
                and audit["run_id"] == self.reg["pilot_run_id"] and audit["time"] == t
                and receipt["github_asset_id"] == spec["asset_id"]
                and receipt["browser_download_url"] == asset_url(receipt["file_name"])
                and receipt["browser_download_url"] == spec["asset_url"]
                and receipt["sha256"] == spec["archive_sha256"] and receipt["bytes"] == spec["bytes"],
                "La evidencia guardada no acredita una frontera del piloto")
        folder.mkdir(parents=True, exist_ok=True)
        meta = folder / "PILOTO_METRICAS.json"
        install(meta, metrics, once=True)
        archive = folder / "piloto.zip"
        if not archive.is_file():
            download(dict(browser_download_url=spec["asset_url"], size=spec["bytes"],
                          digest="sha256:" + spec["archive_sha256"]), archive)
        return archive, meta

    def worker(self, action, folder, *extra, codes=(0,)):
        args = [sys.executable, "-m", "cp12_reanudacion.p4_tercera_fisica", action,
                "--registro", str(self.reg_path), "--home", str(self.work / "origen_piloto"),
                "--carpeta", str(folder), *(str(v) for v in extra)]
        with subprocess.Popen(args) as process:
            pid = process.pid
            exit_code = process.wait()
        require(exit_code in codes, f"{action} terminó con código {exit_code}")
        return dict(operation=action, PID=pid, observed_exit=True, exit_code=exit_code, observed_at=now(),
                    actions_run_id=self.claim["actions_run_id"], actions_attempt=self.claim["actions_attempt"],
                    worker_id=self.claim["worker_id"])

    def restore(self):
        proof = self.state["latest_full_frontier_proof"]
        if proof is None:
            return None
        receipt = self.git.json(self.head, proof["recovery_receipt"])
        require(all(receipt[k] == v for k, v in self.identity.items())
                and receipt["passed"] and receipt["M2_steps_executed"] == 0
                and receipt["time"] == proof["time"] == self.state["last_closed_boundary"]
                and receipt["sha256"] == proof["sha256"], "La frontera registrada no está acreditada")
        restored = self.work / "recuperada"
        archive = download(dict(browser_download_url=receipt["browser_download_url"], size=receipt["bytes"],
                                digest="sha256:" + receipt["sha256"]), self.work / "recuperada.zip")
        unzip(archive, restored)
        verify_payload(restored, self.identity)
        require(sha(restored / "ESTADO.npz") == receipt["state_sha256"], "NPZ recuperado distinto")
        return restored / "ESTADO.npz"

    def terminal_report(self):
        rows = []
        for t in range(8, 161, 8):
            audit = self.git.json(self.head, f"{ROOT}/tau{t:04d}/METRICAS_ORIGINALES.json")
            require(audit["passed"] and all(audit[k] == v for k, v in self.identity.items()),
                    "Falta acreditar un cierre intermedio")
            p = audit["comparison"]
            rows.append(dict(time=t, pilot={k: p["pilot_pair"][k] for k in METRICS},
                             refined={k: p["refined_pair"][k] for k in METRICS},
                             ratio_chi=p["chi_phase_original_ratio"], order_chi=p["chi_phase_observed_order"],
                             order_common_grid=p["same_fine_grid_observed_order"]))
        final = rows[-1]
        improves = final["refined"][PHASE] < final["pilot"][PHASE]
        result = dict(schema="CP12_P4_TERCERA_MALLA_RESULTADO_V1", **self.identity, time=160,
                      time_series=rows, original_gate_passed=True, physical_gates_passed=True,
                      chi_phase_agreement_improved=improves, final_frontier=self.state["latest_full_frontier_proof"],
                      scope="Tres resoluciones de la misma acción, caja, proyección y preparación.",
                      independent_reference_stability_robustness_pending=True,
                      correction_validated=False, CP12_closed=False)
        text = ["# CP12/P4 · Resultado de tercera malla", "",
                "| τ | χ fase h=.125/.0625 | χ fase h=.0625/.03125 | Orden observado |",
                "| --- | --- | --- | --- |"]
        for row in rows:
            p = row["order_chi"]
            text.append(f"| {row['time']} | {100*row['pilot'][PHASE]:.6f} % | "
                        f"{100*row['refined'][PHASE]:.6f} % | {format(p, '.4f') if p is not None else '—'} |")
        text += ["", ("El refinamiento redujo la discrepancia de χ en espacio de fases en τ160."
                      if improves else "El refinamiento conservó el acuerdo exigido en τ160."), "",
                 "Se aprobaron las cinco métricas del comparador original y las puertas físicas de las tres mallas. "
                 "La serie de órdenes es descriptiva y depende de la normalización de cada par. "
                 "El resultado JSON incluye el contraste en el mismo retículo fino.", "",
                 "[Resultado completo](RESULTADO.json) · [Recuperación de τ160](tau0160/RECUPERACION_PUBLICA.json) · "
                 "[Referencia independiente, estabilidad y robustez pendientes](SIGUIENTE_CONTRASTE.md)", ""]
        self.state.update(status="COMPLETADA_TAU160", result=ROOT + "/RESULTADO.json", report=ROOT + "/INFORME.md",
                          next_target=None, updated_at=now())
        self.publish({STATE: encoded(self.state), ROOT + "/RESULTADO.json": encoded(result),
                      ROOT + "/INFORME.md": "\n".join(text).encode(), CLAIM: None},
                     "CP12/P4 tercera malla: publicar los dos pares y el dictamen en τ160")

    def checkpoint(self, t, previous):
        room = self.work / f"tau{t:04d}"
        local = room / "frontera"
        local.mkdir(parents=True)
        registered = dict(**self.identity, from_time=None if t == 0 else t - 8, target=t, claim=self.claim,
                          source_frontier=self.state["latest_full_frontier_proof"], registered_before_M2=True)
        directory = f"{ROOT}/tau{t:04d}"
        self.publish({directory + f"/ASIGNACION_{self.claim['worker_id']}.json": encoded(registered)},
                     f"CP12/P4 tercera malla: asignar τ{t} desde el respaldo exacto")
        if t == 0:
            exit_info = self.worker("origen", local)
        else:
            exit_info = self.worker("tramo", local, "--anterior", previous, "--objetivo", t, codes=(0, 2))
        record(local / "SALIDA.json", exit_info)
        shutil.copyfile(self.reg_path, local / "REGISTRO.json")
        if exit_info["exit_code"] == 0:
            pilot, metric = self.pilot(t, room)
            local_exit = self.worker("auditar", local, "--piloto", pilot, "--metricas", metric,
                                     "--salida", local / "CONTROL_LOCAL.json", codes=(0, 2))
        else:
            local_exit = None
        first = read(local / "EVOLUCION.json")
        archive = room / (f"CP12_P4_MALLA3_{self.identity['execution_uuid']}_TAU{t:04d}_"
                          f"{sha(local / 'ESTADO.npz')[:16]}.zip")
        make_capsule(local, archive, self.identity)
        uploaded = upload(archive, self.destinations)
        asset_identity(uploaded, dict(file_name=archive.name, bytes=archive.stat().st_size, sha256=sha(archive)))
        downloaded = download(uploaded, room / "descargado.zip")
        recovered = room / "recuperacion"
        unzip(downloaded, recovered)
        count = verify_payload(recovered, self.identity)
        recovered_state = recovered / "ESTADO.npz"
        audit_path = room / "AUDITORIA.json"
        if local_exit is not None:
            audit_exit = self.worker("auditar", recovered, "--piloto", pilot, "--metricas", metric,
                                     "--salida", audit_path, codes=(0, 2))
            audit = read(audit_path)
            require(audit == read(recovered / "CONTROL_LOCAL.json")
                    and audit_exit["exit_code"] == local_exit["exit_code"],
                    "La auditoría de sesión nueva no reproduce la local")
        else:
            audit_exit = None
            audit = dict(**self.identity, time=first["time"], passed=False, integrity_only=True,
                         M2_steps_executed=0, negative=first["negative"], state_sha256=sha(recovered_state))
        receipt = dict(schema="CP12_P4_TERCERA_MALLA_RECUPERACION_V1", **self.identity,
                       time=audit["time"], target=t, github_asset_id=uploaded["id"], bytes=uploaded["size"],
                       browser_download_url=uploaded["browser_download_url"], sha256=sha(downloaded),
                       state_sha256=sha(recovered_state), passed=audit["passed"], payload_files=count,
                       all_payload_hashes_verified_before_and_after=verify_payload(recovered, self.identity) == count,
                       M2_steps_executed=0, audit_process=audit_exit, independently_downloaded_without_authentication=True)
        files = {directory + "/RECUPERACION_PUBLICA.json": encoded(receipt),
                 directory + "/EVOLUCION.json": (recovered / "EVOLUCION.json").read_bytes(),
                 directory + "/SALIDA.json": (recovered / "SALIDA.json").read_bytes(),
                 directory + "/METRICAS_ORIGINALES.json": encoded(audit)}
        if not audit["passed"]:
            self.state.update(status="SUSPENDIDA_POR_PUERTA", next_target=None, updated_at=now(),
                              failure_receipt=directory + "/SUSPENSION.json")
            files[self.state["failure_receipt"]] = encoded(dict(**self.identity, target=t, time=audit["time"],
                last_valid_boundary=self.state["last_closed_boundary"], recovery=receipt,
                metrics=directory + "/METRICAS_ORIGINALES.json", CP12_closed=False))
            files[CLAIM] = None
        else:
            self.state.update(status="FRONTERA_VERIFICADA", last_closed_boundary=t,
                              latest_full_frontier_proof=dict(time=t, sha256=receipt["sha256"],
                                  state_sha256=receipt["state_sha256"], github_asset_id=uploaded["id"],
                                  recovery_receipt=directory + "/RECUPERACION_PUBLICA.json",
                                  metrics=directory + "/METRICAS_ORIGINALES.json"),
                              updated_at=now(), next_target=t + 8 if t < 160 else None)
        files[STATE] = encoded(self.state)
        self.publish(files, f"CP12/P4 tercera malla: acreditar τ{t}" if audit["passed"]
                     else f"CP12/P4 tercera malla: conservar el fallo al objetivo τ{t}")
        print(f"τ{t} · adjunto {uploaded['id']} · puertas {audit['passed']}", flush=True)
        if t:
            (room / "piloto.zip").unlink(missing_ok=True)
        return recovered_state if audit["passed"] else None

    def run(self):
        if not self.own():
            print("La reserva corresponde a otro trabajador o hay evidencia terminal.", flush=True)
            return
        origin, _ = self.pilot(0, self.work / "origen_publico")
        unzip(origin, self.work / "origen_piloto")
        previous = self.restore()
        start = 0 if previous is None else self.state["last_closed_boundary"] + 8
        for t in range(start, 161, 8):
            previous = self.checkpoint(t, previous)
            if previous is None:
                return
        self.terminal_report()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trabajo", type=Path, required=True)
    Campaign(parser.parse_args().trabajo.resolve()).run()


if __name__ == "__main__":
    main()
