"""Recuperar un transporte hospedado por su recibo y restaurarlo con cero M2."""

import argparse
import os
from pathlib import Path
import subprocess
import sys

from .campana_hospedada import RECIPIENT, REPOSITORY, decrypt, download, snapshot, use_preserver
from .evidencia import checked_audits, resolve
from .infra import AUDITOR, STATE, Destinations, Git, Timings, asset_url, module, read, record, require, sha
from .preparacion import environment, payloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trabajo", required=True, type=Path)
    parser.add_argument("--clave", required=True, type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    work, key = args.trabajo.resolve(), args.clave.resolve()
    work.mkdir(parents=True, exist_ok=False)
    git = Git(REPOSITORY)
    head = git.head()
    plan = resolve(git, head)
    state = git.json(head, STATE)
    pointer = state["hosted_latest_verified_transport"]
    require(pointer and pointer["target"] == plan.registry["target"] and
            pointer["observer_clock"] > plan.frontier["observer_clock"] and
            pointer["allocation"] == plan.allocation, "El último transporte pertenece a otro tramo.")
    saved = git.json(head, pointer["receipt"])
    sealed = saved["encrypted_asset"]
    require(saved["passed"] and saved["public_recipient_sha256"] == sha(RECIPIENT) and
            sealed == pointer["archive"] and sealed["browser_download_url"] == asset_url(sealed["name"]) and
            saved["observer_clock"] == pointer["observer_clock"],
            "La clave de recuperación o el adjunto difieren del recibo.")
    assets = Destinations(work, work, Timings()).assets()
    matches = [asset for asset in assets if asset["id"] == sealed["id"]]
    require(len(matches) == 1 and all(matches[0][k] == sealed[k] for k in ("name", "browser_download_url")) and
            matches[0]["size"] == sealed["bytes"] and matches[0]["digest"] == "sha256:" + sealed["sha256"],
            "Los metadatos remotos del transporte no coinciden.")
    copy = download(matches[0], work / sealed["name"])
    archive = work / saved["file_name"]
    require(archive.parent == work and archive.suffix == ".zip", "Nombre de cápsula inválido.")
    decrypt(copy, archive, RECIPIENT, key)
    require(archive.stat().st_size == saved["bytes"] and sha(archive) == saved["sha256"],
            "Los bytes del transporte descifrado difieren del recibo.")
    env, fp = environment(git, plan, Destinations(work, work, Timings()), assets, work)
    code = snapshot(git, plan, work)
    subprocess.run([sys.executable, "-m", "cp12_reanudacion.recuperar_transporte_hospedado", "--auditar",
                    str(work), str(code), str(archive), pointer["receipt"], head],
                   env=dict(env, PYTHONPATH=str(REPOSITORY / "herramientas")), check=True)
    receipt = read(work / "RECUPERACION_TRANSPORTE.json")
    record(work / "RECUPERACION_TRANSPORTE.json", dict(receipt, environment=fp))
    print(f"τ{pointer['observer_clock']:g} recuperado sin M2. Recibo: {work / 'RECUPERACION_TRANSPORTE.json'}")


def audit(work, code, archive, receipt_path, head):
    git = Git(REPOSITORY)
    plan = resolve(git, head)
    saved = git.json(head, receipt_path)
    original = saved["recovery"]["original_audits"]
    spec = dict(saved, receipt_sha256=plan.frontier["receipt_sha256"],
                configuration_sha256=plan.frontier["configuration_sha256"],
                closed_state_sha256=plan.frontier["state_sha256"])
    checked_audits(original, spec)
    home = work / "extraido"
    auditor = module(code / AUDITOR, "_cp12_auditor_recuperar_hospedado")
    manifest = auditor.unpack(archive, home, saved["sha256"], saved["bytes"])
    require(manifest["kind"] == "transport" and manifest["observer_clock"] == saved["observer_clock"],
            "El reloj del manifiesto difiere del recibo.")
    base, runner = use_preserver(code)
    audits = base.audit(home, "transport", saved["closed_boundary"], work / "auditoria")
    checked_audits(audits, spec)
    reg = dict(plan.registry, kind="transport", clock=saved["observer_clock"],
               source_archive_sha256=saved["sha256"], transport_sha256=saved["transport_state_sha256"])
    _, _, _, _, _, _, clock, _ = runner.restore(home, reg)
    require(clock == saved["observer_clock"], "El integrador exacto se restauró con otro reloj.")
    payloads(home, manifest)
    record(work / "RECUPERACION_TRANSPORTE.json", dict(
        passed=True, observer_clock=clock, target=saved["target"], source_commit=head,
        source_receipt=receipt_path, archive_sha256=saved["sha256"], original_audits=audits,
        M2_steps_executed=0, DOP853_construction_or_step_attempts=0,
    ))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--auditar"]:
        work, code, archive = (Path(path) for path in sys.argv[2:5])
        audit(work, code, archive, *sys.argv[5:])
    else:
        main()
