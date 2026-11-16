"""Asignación única en Actions. La evolución usa los módulos registrados."""

import argparse
import fcntl
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import supervisor, trabajador
from .evidencia import checked_audits, first_step, recovery, resolve
from .infra import (
    AUDITOR, BRANCH, CANDIDATE, CLAIM, HYBRID, PREFIX, RELEASE, REPO, ROOT, STATE, TAG, UID, WORKER_LOCK,
    Destinations, Git, Stop,
    Timings, digest, encoded, find_asset, install, module, now, optional, read, record, request, require, sha,
)
from .preparacion import environment, payloads

CAMPAIGN = ROOT + ("/piloto_t0_t160" if CANDIDATE == "P4" else "/continuacion_t32_t160_20261114")
ALLOCATION_SUFFIX = "_hospedada_20261115" if CANDIDATE == "P4" else "_hospedada_20261114"
REPOSITORY = Path(__file__).resolve().parents[2]
ADMIN = REPOSITORY / "herramientas/cp12_reanudacion"
RECIPIENT = ADMIN / "p3_recuperacion_publica.pem"


def command(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def allocation_name(start, target):
    base = "p4_piloto" if CANDIDATE == "P4" else "p3_repeticion"
    return f"{base}_{start}_a{target}{ALLOCATION_SUFFIX}"


def accredit_previous_runner(run, attempt):
    require(re.fullmatch(r"[0-9]+", str(run)) and type(attempt) is int and attempt > 0,
            "Identificación inválida del intento anterior")
    path = f"repos/{REPO}/actions/runs/{run}/attempts/{attempt}"
    answer = json.loads(command("gh", "api", path, capture_output=True).stdout)
    require(answer["status"] == "completed" and answer["id"] == int(run) and
            answer["run_attempt"] == attempt and answer["head_branch"] == "administracion/cp12-p4" and
            answer["path"].split("@", 1)[0] == ".github/workflows/cp12-p4-campana.yml",
            "GitHub aún no acredita que el intento anterior de P4 terminó")
    return {name: answer[name] for name in (
        "id", "run_attempt", "status", "conclusion", "head_branch", "updated_at", "html_url")}


def reconcile_lost_runner(git, plan):
    claim = plan.claim
    evidence = accredit_previous_runner(claim["actions_run_id"], claim["actions_attempt"])
    remote = supervisor.recover(git, claim)
    stop = git.json(plan.head, plan.directory + "/PUERTA_DETENIDA.json", missing=True)
    disposition = "SUSPENDIDO" if stop else "PENDIENTE_REINTENTO"
    result = dict(schema="CP12_P4_INTERRUPCION_HOSPEDADA_V1", at=now(), actions=evidence,
                  observed_supervisor_exit=remote, last_valid_frontier=plan.frontier["observer_clock"],
                  previous_claim=claim, status=disposition, CP12_closed=False)
    path = plan.directory + f"/INTERRUPCION_{claim['session_id']}.json"
    files = {CLAIM: None, path: encoded(result)}
    if stop:
        path = plan.directory + "/SUSPENSION.json"
        files[path] = encoded(dict(stop, last_valid_frontier=plan.frontier["observer_clock"]))
    state = dict(plan.state, current_own_worker_status=disposition, own_exit_observed=bool(remote),
                 interruption=path, updated_at=now())
    files[STATE] = encoded(state)
    head = git.publish(plan.head, files, "CP12/P4: conciliar un intento anterior terminado en GitHub")
    require(not stop, "Se recuperó una puerta científica terminal de P4")
    return resolve(git, head)


def snapshot(git, plan, work):
    code = work / "codigo"
    paths = {AUDITOR: plan.registry["original_auditor_sha256"]}
    paths.update({f"{HYBRID}/{name}": expected for name, expected in plan.registry["administrative_sources"].items()})
    for path, expected in paths.items():
        data = git.get(plan.head, path)
        require(digest(data) == expected, f"Fuente registrada distinta: {path}")
        install(code / path, data, once=True)
    return code


def use_preserver(code):
    sys.path.insert(0, str(code / HYBRID))
    return importlib.import_module("base_preservar"), importlib.import_module("continuar")


def download(asset, destination):
    for delay in (1, 2, 4, 8, 16, 30):
        require(not destination.exists(), "La descarga independiente requiere una ruta nueva")
        try:
            with request(asset["browser_download_url"]) as response, destination.open("xb") as stream:
                shutil.copyfileobj(response, stream, 1024 * 1024)
            break
        except (HTTPError, URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code not in (404, 429, 502, 503, 504):
                raise
            destination.unlink(missing_ok=True)
            time.sleep(delay)
    else:
        raise RuntimeError("GitHub no sirvió los bytes del adjunto")
    require(destination.stat().st_size == asset["size"] and "sha256:" + sha(destination) == asset["digest"],
            "Bytes descargados distintos del adjunto")
    return destination


def upload(path, destinations):
    identity = dict(file_name=path.name, sha256=sha(path), bytes=path.stat().st_size)
    asset = published_asset(identity)
    if asset:
        return asset
    journal = path.with_name(path.name + ".subida.json")
    require(not journal.exists(), "La subida anterior requiere conciliación")
    record(journal, dict(at=now(), **identity), once=True)
    exit_code = None
    try:
        exit_code = destinations.upload(path)
    except subprocess.TimeoutExpired:
        pass
    for delay in (1, 2, 4, 8, 16, 30, 30, 30):
        asset = published_asset(identity)
        if asset:
            print(f"Adjunto {asset['id']} leído después de subir {identity['file_name']}", flush=True)
            return asset
        time.sleep(delay)
    raise RuntimeError(f"GitHub aún no acredita el adjunto {identity['file_name']}; gh terminó con {exit_code}")


def published_asset(identity):
    headers = {"User-Agent": "CP12-P3-Hosted", "Cache-Control": "no-cache",
               "Accept": "application/vnd.github+json", "Authorization": "Bearer " + os.environ["GH_TOKEN"]}
    for page in range(1, 51):
        url = f"https://api.github.com/repos/{REPO}/releases/{RELEASE}/assets?per_page=100&page={page}"
        with urlopen(Request(url, headers=headers), timeout=45) as response:
            assets = json.load(response)
        candidates = [asset for asset in assets if asset["name"] == identity["file_name"]]
        if candidates:
            if candidates[0]["state"] != "uploaded" or not candidates[0].get("digest"):
                return None
            return find_asset(candidates, identity)
        if len(assets) < 100:
            return None
    raise RuntimeError("El listado autenticado de adjuntos no está completo")


def decrypt(sealed, output, certificate, key):
    command("openssl", "cms", "-decrypt", "-binary", "-inform", "DER", "-in", sealed,
            "-recip", certificate, "-inkey", key, "-out", output)


def encrypted_copy(base, spec, folder, auditor, destinations, ephemeral):
    archive = Path(spec["archive_path"])
    encrypted = archive.with_suffix(".cms")
    command("openssl", "cms", "-encrypt", "-aes-256-gcm", "-binary", "-outform", "DER",
            "-in", archive, "-out", encrypted, RECIPIENT, ephemeral / "sesion.crt")
    asset = upload(encrypted, destinations)
    with tempfile.TemporaryDirectory(dir=folder) as tmp:
        tmp = Path(tmp)
        replica = download(asset, tmp / encrypted.name)
        decrypted = tmp / archive.name
        decrypt(replica, decrypted, ephemeral / "sesion.crt", ephemeral / "sesion.key")
        checked = base.recover(decrypted, spec, tmp / "verificacion", auditor)
        checked.pop("recovered_home")
    encrypted.unlink()
    return dict(
        kind=spec["kind"], observer_clock=spec["observer_clock"], closed_boundary=spec["closed_boundary"],
        file_name=archive.name, bytes=spec["bytes"], sha256=spec["sha256"], passed=True,
        encrypted_asset=dict(id=asset["id"], name=asset["name"], sha256=asset["digest"].removeprefix("sha256:"),
                             bytes=asset["size"], browser_download_url=asset["browser_download_url"]),
        public_recipient_sha256=sha(RECIPIENT), recovery=checked, M2_steps_executed=0,
    )


def publication(git, job, files, message, *, terminal=False, expected_head=None):
    head = git.head()
    require(expected_head is None or head == expected_head, "Cambió el registro antes de publicar el recibo")
    claim = read(job / "INTENCION.json")
    require(git.json(head, CLAIM, missing=True) == claim, "La intención remota pertenece a otra sesión")
    if terminal:
        require(supervisor.recover(git, claim) is not None, "La salida del trabajador aún no está acreditada")
    return git.publish(head, files, message)


def scientific_stop(git, job, result):
    if CANDIDATE == "P4":
        head = git.head()
        path = str(Path(git.json(head, STATE)["current_assignment"]).with_name("PUERTA_DETENIDA.json"))
        publication(git, job, {path: encoded(result)}, "CP12/P4: conservar la puerta científica observada",
                    expected_head=head)


def boundary_failure(job, target):
    path = job / f"frontera_{target:04d}/auditoria_local/boundary.stderr.txt"
    if CANDIDATE != "P4" or not path.is_file():
        return None
    for line in reversed(path.read_text().splitlines()):
        prefix = "ValueError: "
        if not line.startswith(prefix + "{"):
            continue
        report = json.loads(line.removeprefix(prefix))
        if report.get("schema") != "CP12_P4_CORRECTION_TRIAL_ZERO_STEP_AUDIT" or report.get("passed") is not False:
            return None
        gates = ("energy_gate", "charge_gate", "closure", "Parseval", "symmetry", "defect_identity")
        if any(passed is False and any(mark in name for mark in gates)
               for name, passed in report["tests"].items()):
            return report
        return None
    return None


def wait_ready(job, parent):
    for _ in range(3600):
        for name in ("SALIDA_OBSERVADA.json", "RECHAZO.json"):
            if (job / name).is_file():
                raise RuntimeError("El trabajador salió antes de completar la preparación")
        if (job / "CAPACIDAD.json").is_file():
            proc = read(job / "PROCESO.json")
            pid = proc["pid"]
            require(trabajador.identity(pid) == proc and trabajador.identity(parent["pid"]) == parent and
                    trabajador.lock_owner(job / WORKER_LOCK, pid) and
                    trabajador.lock_owner(job / "home/runtime/worker.lock", pid),
                    "No se acreditaron ambos locks del trabajador")
            return
        time.sleep(1)
    raise TimeoutError("La capacidad previa no llegó al supervisor")


def assign(git, plan, job, run_id):
    claim = dict(schema=supervisor.WORKER_SCHEMA, allocation_id=plan.allocation, worker_id=uuid.uuid4().hex,
                 session_id=uuid.uuid4().hex, registry_sha256=plan.registry_sha,
                 source_archive_sha256=plan.origin["sha256"], at=now(), actions_run_id=run_id,
                 actions_job=os.environ.get("GITHUB_JOB"), actions_attempt=int(os.environ.get("GITHUB_RUN_ATTEMPT", 1)))
    record(job / "INTENCION.json", claim, once=True)
    try:
        git.publish(plan.head, {CLAIM: encoded(claim)}, f"CP12/{CANDIDATE}: registrar intención exclusiva hospedada")
    except (Stop, ValueError):
        other = git.json(git.head(), CLAIM, missing=True)
        if other and other["allocation_id"] == plan.allocation:
            return None
        raise
    return claim


def activate(git, plan, job, parent, fingerprint):
    wait_ready(job, parent)
    claim = read(job / "INTENCION.json")
    capacity = read(job / "CAPACIDAD.json")
    require(capacity["passed"] and capacity["recovery"]["M2_steps_executed"] == 0 and
            capacity["recovery"]["original_audits"]["boundary"]["state_sha256"] == plan.frontier["state_sha256"],
            "Capacidad distinta del origen")
    capacity.update(environment=fingerprint, public_origin=plan.frontier["github_asset_id"])
    folder = plan.directory
    reservation = dict(
        worker_id=claim["worker_id"], session_id=claim["session_id"], registry_sha256=plan.registry_sha,
        source_archive_sha256=plan.origin["sha256"], exclusive=True, locks=dict(registration=True, instance=True),
        scope=dict(clock=plan.origin["observer_clock"], target=plan.registry["target"]),
        new_M2_steps_executed=0,
    )
    reserve_path = folder + "/ASIGNACION_REANUDADOR.json"
    reserved = publication(git, job, {reserve_path: encoded(reservation),
                                      folder + "/CAPACIDAD_HOSPEDADA.json": encoded(capacity)},
                           f"CP12/{CANDIDATE}: acreditar capacidad y reservar trabajador hospedado")
    require(git.get(reserved, reserve_path) == encoded(reservation), "Los bytes de la reserva difieren")
    wait_ready(job, parent)
    activation = dict(
        schema=f"CP12_{CANDIDATE}_FORWARD_ACTIVATION_V2", allocation_id=plan.allocation,
        worker_id=claim["worker_id"], session_id=claim["session_id"], registered_commit=reserved,
        registry_sha256=plan.registry_sha, capacity_acceptance_sha256=digest(encoded(capacity)),
        single_worker_reserved=True, source_clock=plan.origin["observer_clock"], target=plan.registry["target"],
        CP12_closed=False,
    )
    activation_path = folder + "/ACTIVACION.json"
    commit = publication(git, job, {activation_path: encoded(activation)}, f"CP12/{CANDIDATE}: activar el tramo hospedado")
    wait_ready(job, parent)
    require(git.head() == commit and git.get(commit, activation_path) == encoded(activation),
            "La activación remota no es la observada")
    install(job / "ACTIVACION.json", encoded(activation), once=True)


def prefix(base, original, request_spec, local, target, folder):
    if target < 160:
        return original.metrics({"github": {"recovery": local}}, folder, target)
    from .p3_final import review
    return review(Path(local["recovered_home"]), request_spec, local["original_audits"]["boundary"], folder)


def save_transport(base, controller, legacy, streams, budget, dense, clock, next_record, target,
                   job, home, spec, auditor, destinations, keys, git):
    controller.tr.save(home / "transport/current.npz",
                       controller.tr.capture(home, streams, budget, dense, clock, next_record, target))
    checked = controller.audit_transport(home, legacy)
    require(checked["passed"] and checked["M2_steps_executed"] == 0, "Falló el transporte exacto")
    controller.tr.write(home / "proofs" / f"auditoria_forward_{round(clock * 10):06d}.json", checked)
    if CANDIDATE == "P4" or round(clock / .4) % 4:
        return
    folder = job / f"transporte_{round(clock * 10):06d}"
    label = f"TRANSPORTE_{round(clock * 10):06d}_{spec['allocation_id'].upper()}"
    prepared = base.prepare(home, folder, label, "transport", clock, spec["closed_boundary"])
    saved = encrypted_copy(base, prepared, folder, auditor, destinations, keys)
    saved["target"] = target
    saved["transport_state_sha256"] = saved["recovery"]["original_audits"]["transport"]["state_sha256"]
    head = git.head()
    state = git.json(head, STATE)
    path = str(Path(state["current_assignment"]).parent / f"TRANSPORTE_{round(clock * 10):06d}.json")
    state["hosted_latest_verified_transport"] = dict(receipt=path, archive=saved["encrypted_asset"],
                                                    observer_clock=clock, target=target, allocation=spec["allocation_id"])
    state["updated_at"] = now()
    publication(git, job, {path: encoded(saved), STATE: encoded(state)},
                f"CP12/P3: acreditar transporte exacto τ{clock:g}", expected_head=head)
    Path(prepared["archive_path"]).unlink()
    print(f"Transporte recuperado y publicado τ{clock:g}", flush=True)


def finish_boundary(base, original, home, job, spec, auditor, destinations, git, keys):
    target = spec["target"]
    folder = job / f"frontera_{target:04d}"
    label = f"FRONTERA_{target:04d}_{spec['allocation_id'].upper()}"
    if CANDIDATE == "P4":
        label += "_" + read(job / "INTENCION.json")["session_id"].upper()
    prepared = base.prepare(home, folder, label, "boundary", target, target)
    archive = Path(prepared["archive_path"])
    independent = base.recover(archive, prepared, folder / "previa", auditor)
    output = folder / "controles_previos"
    output.mkdir()
    measured = prefix(base, original, prepared, independent, target, output)
    final_ok = CANDIDATE != "P4" or target != 160 or measured["final_protocol"]["passed"]
    if not (measured["prefix_pair_limits_met"] and measured["prefix_physical_controls_met"] and final_ok):
        rejected = dict(phase="puerta", time=target, metrics=measured)
        record(job / "RECHAZO.json", rejected, once=True)
        scientific_stop(git, job, rejected)
        negative = encrypted_copy(base, prepared, folder, auditor, destinations, keys)
        record(job / "RECHAZO.json", dict(rejected, backup=negative))
        return 2
    asset = upload(archive, destinations)
    public_dir = folder / "publica"
    public_dir.mkdir()
    public_archive = download(asset, public_dir / archive.name)
    independent_public = base.recover(public_archive, prepared, public_dir / "recuperacion", auditor)
    saved = dict(schema=f"CP12_{CANDIDATE}_FORWARD_PUBLIC_RECOVERY_V2", passed=True,
                 github_asset_id=asset["id"], bytes=prepared["bytes"], sha256=prepared["sha256"],
                 observer_clock=target, kind="boundary", recovery=independent_public,
                 M2_steps_executed=0, CP12_closed=False)
    output = folder / "controles_publicos"
    output.mkdir()
    measure_public = prefix(base, original, prepared, saved["recovery"], target, output)
    require(measure_public == measured and measure_public["M2_steps_executed"] == 0,
            "La lectura de la cápsula pública difiere de los controles previos")
    saved["recovery"].pop("recovered_home")
    saved.update(file_name=asset["name"], browser_download_url=asset["browser_download_url"],
                 github_reported_digest=asset["digest"], independently_downloaded_without_authentication=True,
                 metrics_sha256=digest(encoded(measure_public)), github_release_tag=TAG)
    record(job / "FRONTERA.json", saved)
    record(job / "METRICAS.json", measure_public)
    record(job / "CERTIFICADO.json", read(output / "CERTIFICADO_FRONTERA.json"))
    return 0


def worker(job):
    git = Git(REPOSITORY)
    claim = read(job / "INTENCION.json")
    spec = read(job / "REGISTRO.json")
    work = job.parent
    home, code = job / "home", work / "codigo"
    base, original = use_preserver(code)
    auditor = code / AUDITOR
    destinations = Destinations(work, work, Timings())
    os.umask(0o077)
    (home / "runtime/tmp").mkdir(parents=True, exist_ok=True)
    (home / "runtime/pycache").mkdir(exist_ok=True)
    keys = job / "claves"
    keys.mkdir()
    command("openssl", "req", "-new", "-x509", "-newkey", "rsa:2048", "-noenc", "-days", "2",
            "-subj", f"/CN=CP12 {CANDIDATE} worker", "-keyout", keys / "sesion.key", "-out", keys / "sesion.crt",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with (job / WORKER_LOCK).open("a+") as registration, (home / "runtime/worker.lock").open("a+") as instance:
        fcntl.flock(registration, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(instance, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(git.json(git.head(), CLAIM) == claim and sha(job / "REGISTRO.json") == claim["registry_sha256"],
                "Intención o registro alterados antes de la restauración")
        record(job / "PROCESO.json", trabajador.identity(os.getpid()), once=True)
        controller, legacy, modules, streams, budget, dense, clock, next_record = original.restore(home, spec)
        before = [stream.accepted for stream in streams]
        provenance = home / "administracion_continuacion_20261030" / spec["allocation_id"]
        provenance.mkdir(parents=True)
        shutil.copyfile(job / "REGISTRO.json", provenance / "REGISTRO.json")
        capacity_dir = job / "capacidad"
        label = "CONTROL_" + spec["allocation_id"].upper()
        if CANDIDATE == "P4":
            label += "_" + claim["session_id"].upper()
        capacity = base.prepare(home, capacity_dir, label,
                                "boundary", spec["closed_boundary"], spec["closed_boundary"], capacity=True)
        saved = encrypted_copy(base, capacity, capacity_dir, auditor, destinations, keys)
        record(job / "CAPACIDAD.json", saved, once=True)
        print(f"Capacidad de {saved['bytes']} bytes recuperada para {spec['allocation_id']}", flush=True)
        for _ in range(3600):
            activation = optional(job / "ACTIVACION.json")
            if activation:
                break
            if (job / "SUPERVISOR_FALLO.json").is_file():
                raise RuntimeError("El supervisor rechazó la activación")
            time.sleep(1)
        else:
            raise TimeoutError("No llegó una activación publicada")
        head = git.head()
        state = git.json(head, STATE)
        path = str(Path(state["current_assignment"]).parent / "ACTIVACION.json")
        require(git.json(head, CLAIM) == claim and git.get(head, path) == encoded(activation) and
                activation["worker_id"] == claim["worker_id"] and activation["registry_sha256"] == sha(job / "REGISTRO.json"),
                "Activación de otro trabajador o no recuperable")
        target = spec["target"]
        phase = "evolucion"
        try:
            if dense is None:
                dense = [stream.advance(target) for stream in streams]
            while clock < target - 1e-12:
                clock, next_record, dense, recorded = controller.interval(modules, streams, budget, dense, clock,
                                                                           next_record, target)
                first_path = job / "INICIO_FISICO.json"
                if not first_path.is_file():
                    first = dict(at=now(), clock=clock,
                                 accepted_steps_since_restore=[s.accepted - n for s, n in zip(streams, before)],
                                 replay96_to112_executed=False, CP12_closed=False)
                    first_step(first, spec)
                    record(first_path, first, once=True)
                    phase = "conservacion"
                    publication(git, job, {str(Path(path).with_name("INICIO_FISICO.json")): encoded(first)},
                                f"CP12/{CANDIDATE}: acreditar el primer paso nuevo en ambas mallas")
                    phase = "evolucion"
                    print(f"Inicio físico τ{clock:g} {first['accepted_steps_since_restore']}", flush=True)
                if recorded and clock < target - 1e-12:
                    save_transport(base, controller, legacy, streams, budget, dense, clock, next_record, target,
                                   job, home, spec, auditor, destinations, keys, git)
            for stream in streams:
                stream.close_segment()
            check = modules["native"].reference(streams[1].sim,
                                                (streams[0].sim, streams[1].sim, streams[0].q, streams[1].q))
            budget.algebra.append(dict(time=clock, **check))
            legacy.save_state(home, streams, budget)
            phase = "conservacion"
            return finish_boundary(base, original, home, job, spec, auditor, destinations, git, keys)
        except Exception as error:
            negative = home / "negative" / spec["allocation_id"]
            negative.mkdir(parents=True, exist_ok=True)
            np = modules["np"]
            arrays = {f"grid_{i}_{name}": getattr(s, name) for i, s in enumerate(streams)
                      for name in ("q", "v", "initial_q", "initial_v")}
            for family in ("raw", "coupled"):
                for i, observer in enumerate(getattr(budget, family)):
                    arrays[f"{family}_{i}_q"], arrays[f"{family}_{i}_v"] = observer.q, observer.v
            np.savez_compressed(negative / "ESTADO_NO_CERTIFICADO.npz", **arrays)
            boundary = boundary_failure(job, target)
            scientific_phase = "evolucion" if boundary else phase
            result = dict(phase=scientific_phase if CANDIDATE == "P4" else "evolucion_o_conservacion",
                          time=clock, error_type=type(error).__name__,
                          traceback=traceback.format_exc(), metadata=[s.metadata() for s in streams],
                          last_closed_boundary=spec["closed_boundary"], CP12_closed=False)
            if boundary:
                result["boundary_audit"] = boundary
            record(negative / "FALLO.json", result)
            previous = optional(job / "RECHAZO.json")
            result = previous if previous and previous["phase"] == "puerta" else result
            record(job / "RECHAZO.json", result)
            folder = job / "negativo"
            try:
                if result["phase"] == "evolucion":
                    scientific_stop(git, job, result)
                label = "FALLO_" + spec["allocation_id"].upper()
                if CANDIDATE == "P4":
                    label += "_" + claim["session_id"].upper()
                prepared = base.prepare(home, folder, label,
                                        "negative", clock, spec["closed_boundary"])
                result["backup"] = encrypted_copy(base, prepared, folder, auditor, destinations, keys)
                record(job / "RECHAZO.json", result)
            except Exception:
                traceback.print_exc()
            traceback.print_exc()
            return 2


def close(git, plan, job, exit_info):
    head = git.head()
    state = git.json(head, STATE)
    result = optional(job / "RECHAZO.json")
    root = plan.directory
    terminal_record = dict(exit_info, last_valid_frontier=plan.frontier["observer_clock"])
    files = {root + "/SALIDA_TRABAJADOR.json": encoded(terminal_record), CLAIM: None}
    if exit_info["receipt"]["returncode"] or result:
        result = result or dict(phase="preparacion", new_M2_steps_observed=0)
        scientific = CANDIDATE == "P3" or result["phase"] in ("puerta", "evolucion")
        record_name = "SUSPENSION.json" if scientific else "INTERRUPCION_ADMINISTRATIVA.json"
        if not scientific:
            record_name = f"INTERRUPCION_ADMINISTRATIVA_{exit_info['receipt']['session_id']}.json"
        files[root + "/" + record_name] = encoded(dict(result, last_valid_frontier=plan.frontier["observer_clock"]))
        state.update(current_own_worker_status="SUSPENDIDO" if scientific else "PENDIENTE_REINTENTO",
                     own_exit_observed=True, updated_at=now(), interruption=root + "/" + record_name,
                     next_recovery="Consultar el fallo y el último cierre verificado.")
        files[STATE] = encoded(state)
        publication(git, job, files, f"CP12/{CANDIDATE}: registrar interrupción junto a la frontera válida",
                    terminal=True, expected_head=head)
        return 2
    recovered, metrics, certificate = (read(job / name) for name in ("FRONTERA.json", "METRICAS.json", "CERTIFICADO.json"))
    target = plan.registry["target"]
    receipt_path = root + "/RECUPERACION_PUBLICA.json"
    metrics_path = root + "/METRICAS_ORIGINALES.json"
    certificate_path = root + "/CERTIFICADO_FRONTERA.json"
    audit = recovered["recovery"]["original_audits"]["boundary"]
    frontier = {key: recovered[key] for key in ("kind", "observer_clock", "file_name", "bytes", "sha256", "github_asset_id")}
    frontier.update(
        {key: audit[key] for key in ("receipt_sha256", "state_sha256", "configuration_sha256")},
        closed_boundary=target, next_target=None if target == 160 else target + 8,
        certificate=certificate_path, recovery_receipt=receipt_path, original_spatial_and_physical_metrics=metrics_path,
        payload_files=recovered["recovery"]["payload_files"], source_allocation=plan.allocation, passed=True,
        all_five_spatial_and_physical_gates_passed=True, boundary_audits=30, spatial_metrics=5,
        physical_prefix_gates=10, M2_steps_executed_during_recovery_and_metrics=0,
        CP12_closed=False, correction_validated=False, final_protocol_acceptance=False,
    )
    checked_audits(recovery(recovered, frontier)["original_audits"], frontier)
    state.update(
        latest_full_trial_frontier_recovered_and_audited=target, latest_recoverable_observer_clock=target,
        latest_recoverable_kind="boundary", latest_full_frontier_proof=frontier, hosted_latest_verified_transport=None,
        own_exit_observed=True, current_own_worker_status="FRONTERA_PUBLICA_VERIFICADA", current_target=frontier["next_target"],
        own_observed_start=None, updated_at=now(), current_assignment=None,
    )
    files.update({receipt_path: encoded(recovered), metrics_path: encoded(metrics), certificate_path: encoded(certificate)})
    if target < 160:
        next_path = CAMPAIGN + f"/tramo_{target:04d}_{target + 8:04d}/REGISTRO.json"
        reg = {key: value for key, value in plan.registry.items() if key != "isolation"}
        reg.update(
            allocation_id=allocation_name(target, target + 8), clock=target, closed_boundary=target,
            target=target + 8, source_archive_sha256=frontier["sha256"], closed_state_sha256=audit["state_sha256"],
            source_recovery_evidence=receipt_path, source_github_asset_id=frontier["github_asset_id"],
            source_frontier_commit=head, previous_intervals_through_clock_must_not_repeat=target,
            receipt_sha256=audit["receipt_sha256"], registered_at_utc=now(),
        )
        state.update(current_assignment=next_path, next_recovery=f"Verificar capacidad y locks propios de τ{target}→τ{target + 8}.")
        files[next_path] = encoded(reg)
    else:
        validation_path = root + "/VALIDACION_FINAL.json"
        state.update(final_protocol_result=validation_path,
                     next_recovery="Consultar el resultado final y las obligaciones de referencia y robustez.")
        files[validation_path] = encoded(metrics["final_protocol"])
    files[STATE] = encoded(state)
    commit = publication(git, job, files, f"CP12/{CANDIDATE}: cerrar y acreditar recuperación pública τ{target}",
                         terminal=True, expected_head=head)
    print(json.dumps(dict(boundary=target, commit=commit, asset=recovered["github_asset_id"],
                          receipt=receipt_path, sha256=recovered["sha256"])), flush=True)
    return 0


def execute(target, work, *, check=False):
    git = Git(REPOSITORY)
    head = git.head()
    state = git.json(head, STATE)
    if state["latest_full_trial_frontier_recovered_and_audited"] >= target:
        print(f"τ{target} ya tiene frontera verificada.", flush=True)
        return 0
    require(state["latest_full_trial_frontier_recovered_and_audited"] + 8 == target and
            state["current_own_worker_status"] != "SUSPENDIDO", "El tramo anterior requiere conciliación")
    plan = resolve(git, head)
    require(plan.assignment_matches() and plan.registry["target"] == target and
            plan.registry["source_archive_sha256"] == plan.frontier["sha256"] and plan.registry["clock"] == target - 8 and
            plan.registry["allocation_id"].endswith(ALLOCATION_SUFFIX), "Asignación ajena a la trayectoria")
    require(sha(__file__) == plan.registry["hosted_executor_sha256"] and
            sha(RECIPIENT) == plan.registry["hosted_recovery_certificate_sha256"] and
            sha(ADMIN / "p3_final.py") == plan.registry["hosted_final_reader_sha256"],
            "Cambió una fuente administrativa registrada")
    if plan.claim:
        current_run = plan.claim.get("actions_run_id") == os.environ.get("GITHUB_RUN_ID")
        current_attempt = plan.claim.get("actions_attempt") == int(os.environ.get("GITHUB_RUN_ATTEMPT", 1))
        if current_run and (CANDIDATE == "P3" or current_attempt) and supervisor.supervised(plan.claim) and not check:
            print("Otro ejecutor de esta ejecución posee la intención exclusiva.", flush=True)
            return 0
        if check or CANDIDATE == "P3":
            raise RuntimeError("La intención persistente requiere conciliación")
        try:
            plan = reconcile_lost_runner(git, plan)
        except Stop:
            latest = resolve(git, git.head())
            if latest.claim and latest.claim.get("actions_run_id") == os.environ.get("GITHUB_RUN_ID"):
                return 0
            if latest.claim:
                raise
            plan = latest
    require(not state.get("hosted_latest_verified_transport"), "Hay un transporte posterior pendiente de recuperar")
    destinations = Destinations(work, work, Timings())
    assets = destinations.assets()
    asset = find_asset(assets, plan.frontier)
    require(asset and asset["id"] == plan.frontier["github_asset_id"], "Adjunto de origen distinto")
    env, fp = environment(git, plan, destinations, assets, work)
    code = snapshot(git, plan, work)
    archive = destinations.archive(plan.frontier, public=asset)
    job = work / "asignacion"
    job.mkdir(parents=True)
    install(job / "REGISTRO.json", plan.registry_bytes, once=True)
    script = (
        "import sys;from pathlib import Path;from cp12_reanudacion.campana_hospedada "
        "import verificar_origen;verificar_origen(*(Path(x) for x in sys.argv[1:]))"
    )
    command(sys.executable, "-c", script, code, archive, job, env=dict(env, PYTHONPATH=str(REPOSITORY / "herramientas")))
    print(f"Origen τ{plan.origin['observer_clock']:g} auditado con cero pasos M2", flush=True)
    if check:
        return 0
    if CANDIDATE == "P4":
        fresh = git.json(plan.head, CAMPAIGN + "/origen_0000/PRUEBA_REANUDADOR_SESION_NUEVA.json")
        require(fresh["passed"] and fresh["execution_uuid"] == UID and fresh["M2_steps_executed"] == 0 and
                fresh["exclusivity"]["selected_workers"] == 1 and
                fresh["execution_run_id"] == plan.state["execution_run_id"],
                "Falta la recuperación y la prueba exclusiva de nuevas sesiones de P4")
    require(bool(os.environ.get("GITHUB_RUN_ID")) and bool(os.environ.get("GH_TOKEN")), "Falta la identidad del ejecutor hospedado")
    supervisor.check_destination(git)
    claim = assign(git, plan, job, os.environ["GITHUB_RUN_ID"])
    if not claim:
        return 0
    parent = trabajador.identity(os.getpid())
    errors = []

    def activation_thread():
        try:
            activate(git, plan, job, parent, fp)
        except Exception as error:
            errors.append(error)
            record(job / "SUPERVISOR_FALLO.json", dict(error_type=type(error).__name__, error=str(error)))
            traceback.print_exc()

    thread = threading.Thread(target=activation_thread, daemon=True)
    thread.start()
    # El mismo proceso observa al hijo con waitpid y acredita su código en GitHub.
    os.environ.update(env)
    cp = supervisor.supervise(git, job, claim,
                              [sys.executable, str(REPOSITORY / "herramientas/reanudar_cp12.py"), "hospedado", "trabajador", str(job)])
    if errors and not (job / "RECHAZO.json").is_file():
        record(job / "RECHAZO.json", dict(phase="activacion", error=str(errors[0])), once=True)
    remote = supervisor.recover(git, claim)
    require(cp == 0 and remote, "El supervisor carece de recibo de salida remoto")
    return close(git, plan, job, remote)


def verificar_origen(code, archive, job):
    git = Git(REPOSITORY)
    plan = resolve(git, git.head())
    require(sha(job / "REGISTRO.json") == plan.registry_sha, "El origen cambió durante la descarga")
    base, original = use_preserver(code)
    auditor = module(code / AUDITOR, "_cp12_auditor_hospedado")
    spec = plan.frontier
    home = job / "home"
    manifest = auditor.unpack(archive, home, spec["sha256"], spec["bytes"])
    require(len(manifest["files"]) == spec["payload_files"], "Manifiesto distinto")
    audits = base.audit(home, spec["kind"], spec["closed_boundary"], job / "auditoria")
    checked_audits(audits, spec)
    payloads(home, manifest)
    if CANDIDATE == "P4":
        control = plan.registry["transport_registration"]
        require(control["path"] == CAMPAIGN + "/origen_0000/REGISTRO_TRANSPORTE.json",
                "Ruta ajena a la preparación de transporte de P4")
        data = git.get(plan.head, control["path"])
        require(digest(data) == control["sha256"], "Registro P4 de transporte alterado")
        transport = json.loads(data)
        require(transport["execution_uuid"] == UID and
                transport["execution_run_id"] == plan.state["execution_run_id"] and
                all(sha(home / name) == checksum for name, checksum in transport["files"].items()),
                "El registro de transporte no corresponde al estado P4 recuperado")
        install(home / "preregistration/registro_transporte.json", data, once=True)
    _, _, _, _, _, _, clock, _ = original.restore(home, plan.registry)
    require(clock == spec["observer_clock"], "La restauración exacta devolvió otro reloj")
    record(job / "RESTAURACION_EXACTA.json", dict(passed=True, clock=clock, M2_steps_executed=0,
                                                 DOP853_construction_or_step_attempts=0))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for mode in ("verificar", "retomar"):
        entry = subparsers.add_parser(mode)
        entry.add_argument("--objetivo", type=int, required=True, choices=range(8 if CANDIDATE == "P4" else 40, 161, 8))
        entry.add_argument("--trabajo", type=Path, required=True)
    child = subparsers.add_parser("trabajador")
    child.add_argument("job", type=Path)
    args = parser.parse_args(argv)
    if args.operation == "trabajador":
        return worker(args.job.resolve())
    return execute(args.objetivo, args.trabajo.resolve(), check=args.operation == "verificar")
