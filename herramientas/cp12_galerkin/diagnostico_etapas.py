"""Leer el estado suspendido y contrastar etapas congeladas con cero avance."""
import argparse
from pathlib import Path

from cp12_reanudacion.infra import encoded, read, require, sha
from cp12_reanudacion.p4_tercera_hospedada import unzip, verify_payload
from etapas_estables import original_trace, residual_correction
from fisica import Gauss8
from hospedado import Context
from trayectoria import archive_record, case_binding, model_at, read_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path)
    args = parser.parse_args()
    ctx = Context(args.work)
    lock = read(Path(__file__).with_name("DIAGNOSTICO_ETAPAS.json"))
    require(lock["campaign_uuid"] == ctx.reg["campaign_uuid"], "Diagnóstico de otra trayectoria")
    ctx.sources()
    commit = ctx.git.pin(lock["failure_commit"])
    receipt = ctx.json(lock["failure_receipt"], base=commit)
    identity = case_binding(ctx, "EPS")
    require(all(receipt[k] == v for k, v in identity.items()) and not receipt["passed"]
            and receipt["sha256"] == lock["failure_capsule_sha256"]
            and receipt["github_asset_id"] == lock["failure_asset_id"], "Se requería el estado negativo exacto")
    archive = archive_record(receipt, ctx.scratch)
    folder = ctx.scratch / "negativo"
    unzip(archive, folder)
    files = verify_payload(folder, identity)
    npz = folder / "ESTADO.npz"
    with_hash = sha(npz)
    require(with_hash == receipt["state_sha256"], "Estado negativo distinto")
    state = read_state(npz, identity)
    gates = read(folder / "PUERTAS.json")
    require(all(gates["physical"].values()) and state["steps"] == 830, "Registro de suspensión distinto")
    stepper = Gauss8(model_at(ctx, "EPS", state["basis"]), ctx.reg["cases"]["EPS"])
    old = original_trace(stepper, state["u"], state["v"])
    improved, trace = residual_correction(stepper, state["u"], state["v"])
    require(sha(npz) == with_hash and verify_payload(folder, identity) == files, "Se modificó el estado")
    result = dict(schema="CP12_P4_GALERKIN_DIAGNOSTICO_ETAPAS_V1", **identity, hosted=ctx.hosted,
                  time=state["time"], failure_commit=commit, input_asset=receipt["github_asset_id"],
                  input_sha256=receipt["sha256"], source_state_sha256=with_hash,
                  original=old, corrected=trace, original_converged=old[-1]["change"] <= 1.,
                  passed=improved is not None, method="Resolver por corrección del residuo en las cuatro etapas",
                  identical_step_and_tolerances=True, M2_steps_executed=0, CP12_closed=False,
                  correction_code_sha256=sha(Path(__file__).with_name("etapas_estables.py")))
    ctx.publish({ctx.root + "/incidencias/EPS_ETAPAS_CONGELADAS.json": encoded(result)},
                "CP12/P4 Galerkin: diagnosticar la resolución de etapas en el negativo EPS")
    print(result, flush=True)
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
