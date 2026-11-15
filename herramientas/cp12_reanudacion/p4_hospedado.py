"""Origen verificable y pruebas de exclusividad de la variante hospedada P4."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace

from . import campana_hospedada as campaign, supervisor
from .evidencia import checked_audits, resolve
from .infra import (AUDITOR, BRANCH, CANDIDATE, CLAIM, HYBRID, ROOT, STATE, TAG, UID,
                    Destinations, Git, Timings, digest, encoded, find_asset, install,
                    module, now, read, record, require, sha)
from .preparacion import environment


HISTORY = "checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115"
ORIGIN = campaign.CAMPAIGN + "/origen_0000"
FIRST_ASSIGNMENT = campaign.CAMPAIGN + "/tramo_0000_0008/REGISTRO.json"
CONTROL = campaign.ADMIN / "INICIAR_P4_HOSPEDADO.json"
ORIGIN_LOCK = ORIGIN + "/INTENCION_PREPARACION.json"
NOVEL_SESSION = ORIGIN + "/PRUEBA_REANUDADOR_SESION_NUEVA.json"


def source_control(git, head, work):
    ticket = read(CONTROL)
    require(ticket["activate"] is True and ticket["execution_uuid"] == UID, "Activación P4 sin identidad aprobada")
    commit = git.pin(ticket["scientific_commit"])
    require(not git.run("merge-base", "--is-ancestor", commit, head, check=False).returncode,
            "Los controles propios no son antecesores de la rama del piloto")
    certificate = git.get(commit, ROOT + "/CERTIFICADO_CONTROLES_P4.json")
    require(digest(certificate) == ticket["preflight_certificate_sha256"], "Certificado de controles distinto")
    result = json.loads(certificate)
    require(result["all_registered_preflight_controls_passed"] and not result["DOP853_attempts"] and
            result["M2_steps_executed"] == 0, "Los controles científicos de P4 no autorizan iniciar")
    local = work / "ciencia"
    campaign.command("git", "clone", "--quiet", "--no-tags", "--single-branch",
                     "--branch", BRANCH, git.run("remote", "get-url", "origin").stdout.decode().strip(), local)
    campaign.command("git", "-C", local, "checkout", "--quiet", "--detach", commit)
    reg = read(local / ROOT / "REGISTRO_PREFLIGHT.json")
    require(reg["execution_uuid"] == UID, "La preparación pertenece a otro P4")
    return local


def origin(work):
    git = Git(campaign.REPOSITORY)
    head = git.head()
    existing = git.json(head, STATE, missing=True)
    if existing and existing.get("latest_full_frontier_proof"):
        require(existing["execution_uuid"] == UID, "El origen publicado pertenece a otro piloto")
        print("El registro P4 ya conserva su origen.", flush=True)
        return 0
    run = os.environ["GITHUB_RUN_ID"]
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", 1))
    intent = dict(execution_uuid=UID, run=run, attempt=attempt,
                  runner=os.environ.get("RUNNER_NAME"), at=now(), M2_steps_authorized=0)
    prev = git.json(head, ORIGIN_LOCK, missing=True)
    if prev:
        if (prev["run"], prev["attempt"]) == (run, attempt):
            print("Otro ejecutor de este intento prepara el origen.", flush=True)
            return 0
        campaign.accredit_previous_runner(prev["run"], prev["attempt"])
    try:
        head = git.publish(head, {ORIGIN_LOCK: encoded(intent)}, "CP12/P4: reservar la preparación de τ0")
    except Exception:
        current = git.json(git.head(), ORIGIN_LOCK, missing=True)
        if current and current != intent and (current["run"], current["attempt"]) == (run, attempt):
            return 0
        raise
    work.mkdir(mode=0o700, parents=True)
    local = source_control(git, head, work)
    historical = git.json(head, HISTORY + "/REGISTRO.json")["capsules"]["112"]
    prior_receipt = git.json(head, historical["public_receipt"])["recovery"]
    source = dict(historical, file_name=historical["download_url"].rsplit("/", 1)[-1])
    plan = SimpleNamespace(head=head, frontier_receipt=prior_receipt)
    dest = Destinations(work, work, Timings())
    listed = dest.assets()
    asset = find_asset(listed, source)
    require(asset and asset["id"] == historical["github_asset_id"], "Cápsula científica de origen distinta")
    env, fingerprint = environment(git, plan, dest, listed, work)
    os.environ.update(env)
    prior_zip = dest.archive(source, public=asset)
    home = work / "instancia_p4"
    identity_path = work / "identidad.json"
    campaign.command(sys.executable, "-B", local / ROOT / "preparar_origen.py",
                     "--archivo", prior_zip, "--instancia", home,
                     "--certificado", local / ROOT / "CERTIFICADO_CONTROLES_P4.json",
                     "--recibo", identity_path, env=env)
    identity = read(identity_path)
    require(identity["execution_uuid"] == UID and identity["M2_steps_executed"] == 0,
            "El preparador devolvió otra instancia o avanzó M2")
    ticket = read(CONTROL)
    require(identity["execution_run_id"] == ticket["execution_run_id"] and
            identity["audit"]["state_sha256"] == ticket["tau0_state_sha256"],
            "La reconstrucción hospedada no coincide con el origen P4 auditado localmente")
    py = local / HYBRID / "base_preservar.py"
    auditor = local / AUDITOR
    base = module(py, "_cp12_p4_preserver")
    label = f"FRONTERA_0000_P4_ORIGEN_{run}_{attempt}"
    prepared = base.prepare(home, work / "origen", label, "boundary", 0, 0)
    path = Path(prepared["archive_path"])
    asset = campaign.upload(path, dest)
    restored_zip = campaign.download(asset, work / path.name)
    exact = base.recover(restored_zip, prepared, work / "recuperacion", auditor)
    exact.pop("recovered_home")
    audited = exact["original_audits"]["boundary"]
    spec = dict(schema="CP12_P4_FORWARD_PUBLIC_RECOVERY_V2", kind="boundary", observer_clock=0,
                github_asset_id=asset["id"], sha256=prepared["sha256"], bytes=prepared["bytes"], passed=True,
                M2_steps_executed=0, recovery=exact, file_name=asset["name"], github_release_tag=TAG,
                github_reported_digest=asset["digest"], browser_download_url=asset["browser_download_url"],
                independently_downloaded_without_authentication=True)
    checked_audits(exact["original_audits"], dict(
        spec, closed_boundary=0, **{k: audited[k] for k in
                                    ("state_sha256", "receipt_sha256", "configuration_sha256")}))
    metrics = dict(schema="CP12_P4_ORIGEN_DATOS_CAUCHY_V1", time=0, M2_steps_executed=0,
                   prefix_pair_limits_met=True, prefix_physical_controls_met=True,
                   scope="Cauchy CP10 exacto y 30 controles de origen. El comparador de evolución aplica desde τ8.",
                   initial_CP10_verified=audited["tests"]["original_CP10_Cauchy_data_exact"],
                   physical_accepted_steps=[m["accepted"] for m in audited["metadata"]])
    proof = dict(spec)
    for k in ("schema", "recovery"):
        proof.pop(k)
    proof.update({k: audited[k] for k in ("state_sha256", "receipt_sha256", "configuration_sha256")})
    proof.update(closed_boundary=0, next_target=8, certificate=ORIGIN + "/CERTIFICADO_FRONTERA.json",
                 recovery_receipt=ORIGIN + "/RECUPERACION_PUBLICA.json", payload_files=exact["payload_files"],
                 original_spatial_and_physical_metrics=ORIGIN + "/METRICAS_ORIGINALES.json",
                 all_five_spatial_and_physical_gates_passed=True, initial_Cauchy_audit=True,
                 M2_steps_executed_during_recovery_and_metrics=0, CP12_closed=False)
    allocation = dict(schema="CP12_P4_FORWARD_SEGMENT_V2", allocation_id=campaign.allocation_name(0, 8),
                      execution_uuid=UID, execution_run_id=identity["execution_run_id"],
                      kind="boundary", clock=0, closed_boundary=0, target=8,
                      source_archive_sha256=prepared["sha256"], closed_state_sha256=audited["state_sha256"],
                      receipt_sha256=audited["receipt_sha256"], configuration_sha256=audited["configuration_sha256"],
                      source_github_asset_id=asset["id"], source_recovery_evidence=proof["recovery_receipt"],
                      original_auditor_sha256=sha(auditor),
                      administrative_sources={n: sha(local / HYBRID / n) for n in ("base_preservar.py", "continuar.py")},
                      hosted_executor_sha256=sha(campaign.__file__),
                      hosted_recovery_certificate_sha256=sha(campaign.RECIPIENT),
                      hosted_final_reader_sha256=sha(campaign.ADMIN / "p3_final.py"),
                      source_frontier_commit=head, registered_at_utc=now(), registered_before_M2=True)
    state = dict(schema="CP12_P4_CANONICAL_RECOVERY_REGISTER", branch=BRANCH,
                 execution_uuid=UID, execution_run_id=identity["execution_run_id"],
                 latest_full_frontier_proof=proof, latest_full_trial_frontier_recovered_and_audited=0,
                 latest_recoverable_observer_clock=0, latest_recoverable_kind="boundary", current_target=8,
                 current_assignment=FIRST_ASSIGNMENT, current_own_worker_status="FRONTERA_PUBLICA_VERIFICADA",
                 own_exit_observed=False, CP12_closed=False, correction_validated=False, updated_at=now())
    certificate = dict(schema="CP12_P4_TAU0_PERMANENTLY_RECOVERED", passed=True, time=0,
                       state_sha256=audited["state_sha256"], configuration_sha256=audited["configuration_sha256"],
                       receipt_sha256=audited["receipt_sha256"], **identity, environment=fingerprint)
    git.publish(head, {ORIGIN_LOCK: None, STATE: encoded(state), FIRST_ASSIGNMENT: encoded(allocation),
                       proof["certificate"]: encoded(certificate), proof["recovery_receipt"]: encoded(spec),
                       proof["original_spatial_and_physical_metrics"]: encoded(metrics)},
                "CP12/P4: acreditar τ0 y fijar la primera asignación")
    return 0


def exclusivity_fixture(work, plan=None):
    """Dos procesos Git compiten por la misma intención con la implementación real."""
    if plan is None:
        real = Git(campaign.REPOSITORY)
        plan = resolve(real, real.head())
    with tempfile.TemporaryDirectory(dir=work) as scratch:
        folder = Path(scratch)
        seed = folder / "seed"
        mirror = folder / "bare.git"
        campaign.command("git", "init", "-q", "-b", BRANCH, seed)
        campaign.command("git", "-C", seed, "config", "user.name", "Prueba CP12")
        campaign.command("git", "-C", seed, "config", "user.email", "cp12-prueba@example.invalid")
        campaign.command("git", "-C", seed, "commit", "--allow-empty", "-q", "-m", "Ensayo de exclusividad P4")
        campaign.command("git", "clone", "-q", "--bare", seed, mirror)
        clones = [folder / f"session{i}" for i in range(2)]
        for clone in clones:
            campaign.command("git", "clone", "-q", mirror, clone)
            campaign.command("git", "-C", clone, "config", "user.name", "Prueba CP12")
            campaign.command("git", "-C", clone, "config", "user.email", "cp12-prueba@example.invalid")
        shared = Git(clones[0]).head()
        fixture = SimpleNamespace(head=shared, allocation=plan.allocation, origin=plan.origin,
                                  registry_sha=plan.registry_sha)

        def contend(clone):
            return campaign.assign(Git(clone), fixture, clone, "p4-prueba-sin-M2")

        with ThreadPoolExecutor(max_workers=2) as pool:
            claims = list(pool.map(contend, clones))
        winner, = [claim for claim in claims if claim]
        durable = Git(clones[1])
        require(durable.json(durable.head(), CLAIM) == winner, "Lectura de segunda sesión distinta de la reserva")
        restarted = folder / "tercera_sesion"
        campaign.command("git", "clone", "-q", mirror, restarted)
        require(Git(restarted).json(Git(restarted).head(), CLAIM) == winner,
                "Una sesión nueva no recuperó la intención exclusiva")
    return {"candidate_claims": len(claims), "selected_workers": 1,
            "allocation_id": plan.allocation, "frontier_sha256": plan.frontier["sha256"],
            "observer_clock": plan.frontier["observer_clock"], "M2_steps_executed": 0,
            "separate_new_session_readback": True, "production_worker_started_during_fixture": False}


def verify(work):
    git = Git(campaign.REPOSITORY)
    head = git.head()
    earlier = git.json(head, NOVEL_SESSION, missing=True)
    if earlier:
        require(earlier["passed"] and earlier["execution_uuid"] == UID, "Prueba de sesión ajena al piloto")
        return 0
    plan = resolve(git, head)
    require(plan.frontier["observer_clock"] == 0 and plan.registry["target"] == 8 and not plan.claim,
            "La prueba del origen requiere el registro τ0 con el turno libre")
    work.mkdir(mode=0o700, parents=True)
    audits = []
    for number in (1, 2):
        directory = work / f"sesion_{number}"
        campaign.command(sys.executable, campaign.REPOSITORY / "herramientas/reanudar_cp12.py",
                         "hospedado", "verificar", "--objetivo", "8", "--trabajo", directory)
        proof = read(directory / "asignacion/RESTAURACION_EXACTA.json")
        require(proof["passed"] and proof["clock"] == 0 and proof["M2_steps_executed"] == 0,
                "Una sesión nueva recuperó un origen distinto")
        audits.append(proof)
    fixture = exclusivity_fixture(work)
    supervisor.check_destination(git)
    receipt = dict(schema="CP12_P4_DOS_SESIONES_REANUDADOR_V1", passed=True, audits=audits,
                   exclusivity=fixture, execution_uuid=UID, execution_run_id=plan.state["execution_run_id"],
                   at=now(), M2_steps_executed=0)
    try:
        git.publish(head, {NOVEL_SESSION: encoded(receipt)},
                    "CP12/P4: certificar recuperación y exclusividad desde nuevas sesiones")
    except Exception:
        stored = git.json(git.head(), NOVEL_SESSION, missing=True)
        require(stored and stored["passed"] and stored["execution_uuid"] == UID and
                stored["exclusivity"]["frontier_sha256"] == plan.frontier["sha256"],
                "La prueba de sesiones todavía no tiene un recibo verificable")
    return 0


def retryable():
    git = Git(campaign.REPOSITORY)
    head = git.head()
    state = git.json(head, STATE)
    return 0 if state["current_own_worker_status"] == "PENDIENTE_REINTENTO" and not git.json(
        head, CLAIM, missing=True) else 2


def main(argv=None):
    require(CANDIDATE == "P4", "Esta operación exige el perfil P4")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("origen", "verificar", "puede_reintentar"))
    parser.add_argument("--trabajo", required=True, type=Path)
    opts = parser.parse_args(argv)
    if opts.operation == "puede_reintentar":
        return retryable()
    return (origin if opts.operation == "origen" else verify)(opts.trabajo.resolve())


if __name__ == "__main__":
    sys.exit(main())
