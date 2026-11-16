"""Avance, conservación y lectura de cada uno de los cinco brazos Galerkin."""
from pathlib import Path
import json
import os
import time

import numpy as np

from cp12_reanudacion.campana_hospedada import download, published_asset, upload
from cp12_reanudacion.infra import asset_identity, asset_url, digest, encoded, now, read, record, require, sha
from cp12_reanudacion.p4_tercera_hospedada import make_capsule, unzip, verify_payload
from fisica import Gauss8, M2, use_compensated_controls
from radial import Angular, RADIUS

BOUNDARY = "VERIFICADA"


def case_binding(ctx, case):
    identity = dict(campaign_uuid=ctx.reg["campaign_uuid"], case=case, registration_sha256=ctx.reg_hash)
    return dict(identity, trajectory_id=digest(encoded(identity)))


def model_at(ctx, case, saved_basis=None):
    m2 = M2(ctx.reg["cases"][case], ctx.source, ctx.build)
    if saved_basis is not None and not np.array_equal(m2.angular.projector, saved_basis):
        from continuar_no_radial_m2 import Evolution

        current = m2.angular.projector
        require(saved_basis.shape == current.shape
                and np.max(abs(saved_basis.T @ saved_basis-np.eye(6))) <= 2e-12
                and np.max(abs(saved_basis @ saved_basis.T-current @ current.T)) <= 2e-12,
                "El respaldo usa otro subespacio angular")
        m2.angular = Angular(Evolution(.125, RADIUS, 4), saved_basis, ctx.build)
    return m2


def read_state(path, binding):
    names = ("u", "v", "initial_u", "initial_v", "rows", "basis")
    with np.load(path, allow_pickle=False) as f:
        require(json.loads(str(f["identity"])) == binding, "NPZ de otra trayectoria")
        return dict({k: f[k].copy() for k in names}, steps=int(f["steps"]), balance=json.loads(str(f["balance"])),
                    time=float(f["time"]))


def check_state(path, binding, expected, ctx, control):
    before = sha(path)
    state = read_state(path, binding)
    cfg = ctx.reg["cases"][binding["case"]]
    names = ("u", "v", "initial_u", "initial_v", "rows")
    if not control["passed"]:
        require(sha(path) == before, "Se alteró el negativo")
        return dict(passed=False, state_sha256=before, integrity_only=True, M2_steps_executed=0)
    grid = model_at(ctx, binding["case"], state["basis"])
    time = expected
    rows = state["rows"]
    for name in names:
        require(np.isfinite(state[name]).all(), "Estado recuperado no finito")
    require(state["time"] == time and state["steps"] == round(time / cfg["dt"])
            and np.array_equal(rows[:, 0], np.arange(round(time/.4)+1)*.4),
            "Reloj de la frontera distinto")
    require(state["u"].shape == state["initial_u"].shape == (grid.mesh.n, 3, 6)
            and state["v"].shape == state["u"].shape == state["initial_v"].shape, "Dimensiones Galerkin distintas")
    u, v = state["u"], state["v"]
    q0, v0 = grid.initialize()
    require(np.allclose(q0, state["initial_u"], rtol=2e-12, atol=2e-12)
            and np.allclose(v0, state["initial_v"], rtol=2e-12, atol=2e-12),
            "Cauchy reconstruida distinta")
    row = grid.measure(time, u, v)
    require(np.allclose(row, rows[-1], rtol=2e-12, atol=2e-12)
            and sha(path) == before, "Los balances no se reproducen en el respaldo")
    physical = use_compensated_controls(grid, (u, v, rows, state["balance"]), ctx.reg["physical_limits"])
    require(all(physical.values()) and physical == control["physical"], "Puertas de recuperación distintas")
    return dict(passed=True, time=time, state_sha256=before, physical=physical,
                samples=len(rows), total_physical_steps=state["steps"], M2_steps_executed=0)


def archive_record(receipt, destination_dir):
    name = receipt["file_name"]
    require(receipt["browser_download_url"] == asset_url(name), "Adjunto fuera de la Release del proyecto")
    return download(dict(browser_download_url=receipt["browser_download_url"], size=receipt["bytes"],
                         digest="sha256:" + receipt["sha256"]), destination_dir / name)


class Series:
    def __init__(self, ctx, case):
        self.ctx = ctx
        self.case = case
        self.identity = case_binding(ctx, case)
        self.path = f"casos/{case}"
        self.dir = ctx.scratch / case
        self.dir.mkdir()
        self.state_file = f"{self.path}/ESTADO.json"
        self.state = ctx.json(ctx.root + "/" + self.state_file, missing=True) or dict(
            **self.identity, status="ORIGEN", last_closed_time=None, latest=None, pending=None)
        require(all(self.state[k] == v for k, v in self.identity.items()), "Registro de otra trayectoria")
        self.cfg = ctx.reg["cases"][case]

    def publish(self, files, verb):
        self.state.update(updated_at=now())
        paths = {self.ctx.root + "/" + key: encoded(value) for key, value in
                 dict(files, **{self.state_file: self.state}).items()}
        self.ctx.publish(paths, f"CP12/P4 Galerkin {self.case}: {verb}")

    def restore_file(self, receipt, name):
        room = self.dir / name
        room.mkdir()
        archive = archive_record(receipt, room)
        recovered = room / "recuperado"
        unzip(archive, recovered)
        count = verify_payload(recovered, self.identity)
        return recovered, count

    def close_publication(self, pending, asset):
        ctx, target = self.ctx, pending["target"]
        asset_identity(asset, pending)
        observed = dict(pending, github_asset_id=asset["id"], browser_download_url=asset["browser_download_url"])
        extracted, count = self.restore_file(observed, "relectura-" + str(target))
        state = extracted / "ESTADO.npz"
        control = read(extracted / "PUERTAS.json")
        proof = check_state(state, self.identity, target, ctx, control)
        require(proof["state_sha256"] == pending["state_sha256"], "NPZ publicado distinto del preparado")
        require(verify_payload(extracted, self.identity) == count, "El auditor alteró la carga")
        receipt = dict(observed, recovery=proof, time=control["time"], passed=proof["passed"],
                       M2_steps_executed=0, payload_files=count, independently_downloaded_without_authentication=True)
        folder = f"{self.path}/tau{target:04d}"
        receipt_location = ctx.root + "/" + folder + "/RECUPERACION_PUBLICA.json"
        files = {f"{folder}/RECUPERACION_PUBLICA.json":receipt, f"{folder}/PUERTAS.json":control}
        self.state["pending"] = None
        if proof["passed"]:
            self.state.update(status=BOUNDARY, last_closed_time=target,
                              latest=dict(time=target, receipt=receipt_location, sha256=receipt["sha256"]))
        else:
            self.state.update(status="SUSPENDIDA", failure=receipt_location)
        self.publish(files, f"acreditar τ{target}" if proof["passed"] else "conservar un fallo de puerta")
        print(json.dumps(dict(case=self.case, target=target, verified=proof["passed"], asset=asset["id"])),
              flush=True)
        return state if proof["passed"] else None

    def initialize(self):
        if self.state["pending"]:
            pending = self.state["pending"]
            asset = published_asset(pending)
            if asset:
                return self.close_publication(pending, asset)
            self.state["pending"] = None
        if self.state["latest"] is None:
            return None
        receipt = self.ctx.json(self.state["latest"]["receipt"])
        require(receipt["sha256"] == self.state["latest"]["sha256"] and receipt["passed"]
                and receipt["time"] == self.state["last_closed_time"]
                and receipt["M2_steps_executed"] == 0, "Recibo anterior incoherente")
        recovered, _ = self.restore_file(receipt, "reinicio")
        control = read(recovered / "PUERTAS.json")
        proof = check_state(recovered / "ESTADO.npz", self.identity, receipt["time"], self.ctx, control)
        require(proof["passed"] and proof["state_sha256"] == receipt["state_sha256"], "Falló la restauración")
        return recovered / "ESTADO.npz"

    def run(self, until):
        ctx = self.ctx
        if self.state["status"] == "SUSPENDIDA":
            return 2
        previous = self.initialize()
        if self.state["status"] == "SUSPENDIDA":
            return 2
        prior = read_state(previous, self.identity) if previous is not None else None
        self.model = model_at(ctx, self.case, prior["basis"] if prior else None)
        self.stepper = Gauss8(self.model, self.cfg)
        if prior:
            time_from = int(prior["time"])
            u, v = prior["u"], prior["v"]
            q0, v0 = prior["initial_u"], prior["initial_v"]
            steps = prior["steps"]
            rows, balance = prior["rows"].tolist(), prior["balance"]
            first_target = time_from + 8
        else:
            u, v = self.model.initialize()
            q0, v0 = u.copy(), v.copy()
            rows = [self.model.measure(0., u, v)]
            steps, balance, first_target = 0, dict(energy=0., charge=0.), 0
        sample = round(.4/self.stepper.dt)
        for target in range(first_target, until+1, 8):
            t0 = steps
            allocation = dict(**self.identity, hosted=ctx.hosted, target=target, start_accepted_steps=steps,
                              source_frontier=self.state["latest"], registered_before_advancing=True)
            folder = f"{self.path}/tau{target:04d}"
            instance = f"{ctx.hosted['run_id']}_{ctx.hosted['attempt']}"
            self.publish({f"{folder}/ASIGNACION_{instance}.json": allocation}, f"registrar el tramo a τ{target}")
            start = time.perf_counter()
            failure = None
            goal_steps = round(target/self.stepper.dt)
            try:
                while steps < goal_steps:
                    u, v = self.stepper.step(u, v)
                    steps += 1
                    e, q = self.model.energies(u, v)
                    if not np.isfinite((e, q)).all():
                        failure = "No finitud del estado o balance"
                        break
                    balance["energy"] = max(balance["energy"], float(abs(e/rows[0][1]-1)))
                    balance["charge"] = max(balance["charge"], float(abs(q/rows[0][2]-1)))
                    if steps % sample == 0:
                        rows.append(self.model.measure(steps // sample * .4, u, v, (e, q)))
                    if balance["energy"] > ctx.reg["physical_limits"]["energy_drift_max"] or \
                            balance["charge"] > ctx.reg["physical_limits"]["charge_drift_max"]:
                        failure = "Deriva de energía o carga fuera del límite"
                        break
                    if steps % (sample * 5) == 0:
                        print(f"{self.case} τ{steps * self.stepper.dt:g} · {steps} pasos", flush=True)
            except ArithmeticError as err:
                failure = str(err)
            physical = use_compensated_controls(self.model, (u, v, rows, balance), ctx.reg["physical_limits"])
            actual = float(steps * self.stepper.dt) if steps != goal_steps else target
            passed = failure is None and all(physical.values()) and steps == goal_steps
            working = self.dir / f"local-{target}"
            working.mkdir()
            statepath = working / "ESTADO.npz"
            np.savez_compressed(statepath, u=u, v=v, initial_u=q0, initial_v=v0,
                                rows=rows, steps=steps, time=actual, balance=json.dumps(balance),
                                basis=self.model.angular.projector, identity=json.dumps(self.identity))
            summary = dict(**self.identity, **ctx.hosted, time=actual, target=target, passed=bool(passed),
                           physical=physical, balance=balance.copy(), failure=failure, solver="Gauss–Legendre 4",
                           steps_this_segment=steps-t0, total_steps=steps, environment=ctx.environment(),
                           max_iterations=self.stepper.max_iterations,
                           max_normalized_stage_change=self.stepper.max_normalized_change,
                           wall_seconds=time.perf_counter()-start)
            record(working / "PUERTAS.json", summary)
            name = f"CP12_P4_GALERKIN_{self.identity['campaign_uuid']}_{self.case}_TAU{target:04d}_{instance}.zip"
            archive = make_capsule(working, self.dir / name, self.identity)
            pending = dict(file_name=archive.name, bytes=archive.stat().st_size, sha256=sha(archive),
                           **self.identity, state_sha256=sha(statepath), target=target)
            self.state["pending"] = pending
            self.publish({f"{folder}/ENVIO_{instance}.json":pending}, f"fijar el envío de τ{target}")
            asset = upload(archive, ctx.destinations)
            if self.close_publication(pending, asset) is None:
                return 2
        return 0
