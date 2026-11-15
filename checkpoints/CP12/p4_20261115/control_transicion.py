"""Contraste reservado de τ120/128 con el mismo factorial pasivo original."""

import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "prueba_pasiva"))
from prueba_pasiva import (HISTORY, REPO, SpectralPower, block_m2, environment, load_state,
                           read, recover, reduce_grid, run_cut, sha, verify_file, write)

import numpy as np


def main(input_dir, ciphertext, output):
    prereg = read(HERE / "REGISTRO_PREFLIGHT.json")
    for rel, digest in prereg["sources_sha256"].items():
        verify_file(REPO / rel, digest)
    environment(read(HERE / "prueba_pasiva/REGISTRO.json"))
    primary = REPO / (HERE / "prueba_pasiva/RECIBO.json").relative_to(REPO)
    assert read(primary)["decision"]["outcome"] == "PASA"
    assert read(primary)["M2_steps_executed"] == 0
    p3 = read(HISTORY / "REGISTRO.json")
    p3["capsules"] = {str(t): p3["capsules"][str(t)] for t in (120, 128, 160)}
    output.mkdir(mode=0o700, parents=True)
    inputs, used = recover(REPO, p3, input_dir, ciphertext, output)
    for home, _, _ in inputs.values():
        for rel, digest in p3["capture_sha256"].items():
            verify_file(home / rel, digest)
    source = inputs[160][0]
    sys.path[:0] = [str(source / "candidate"), str(source / "science/herramientas"), str(source)]
    import observador_causal_CP12 as obs
    from p3_backend import MixedP3, MixedP3Gauss
    import operador_pasivo as ops

    cfg = read(source / "configuration.json")["original_configuration"]
    sims = [MixedP3(c["dx"], c["radius"], c["L"]) for c in cfg["physical_configurations"]]
    result, arrays = {}, {}
    with block_m2(obs) as attempts:
        initial = load_state(source, 160, cfg, p3)
        S, reference_grid = obs.symmetry_basis(sims[1], initial["initial_q"][:, sims[0].n:])
        assert np.allclose(S, initial["coupled_angular_basis"], atol=2e-12, rtol=0)
        reduced = [reduce_grid(s, S, reference_grid.ell) for s in sims]
        spectra = [SpectralPower(s, obs.model.mediator) for s in reduced]
        geom = {(i, k): ops.RegularGeometry(s, k) for i, s in enumerate(sims) for k in (4, 8)}
        for t in (120, 128):
            z = load_state(inputs[t][0], t, cfg, p3)
            assert all(np.array_equal(z[k], initial[k]) for k in ("initial_q", "initial_v", "coupled_angular_basis"))
            measured = run_cut(t, z, sims, reduced, S, [("cubica_original", 0, 1, 1)],
                               geom, spectra, obs, ops, MixedP3Gauss, arrays)["cubica_original"]
            result[str(t)] = dict(maximum_order_relative=measured["maximum_order_relative"], band={})
            full = output / f"TAU{t}_COMPLETO.json"
            write(full, measured)
            result[str(t)]["full_sha256"] = sha(full)
            for ell, m in measured["windows"]["r_lt_40"].items():
                result[str(t)]["band"][ell] = {
                    name: d["relative_power_change"] for name, d in m["k_gt_8"]["GL7"]["effects"].items()}
    for home, archive, manifest in inputs.values():
        for name, data in manifest["files"].items():
            verify_file(home / name, data["sha256"], data["bytes"])
        verify_file(archive, p3["capsules"][str(manifest["closed_boundary"])]["sha256"])
    assert not attempts
    np.savez_compressed(output / "RESPUESTAS_TRANSICION.npz", **arrays)
    write(output / "TRANSICION.json", dict(schema="CP12_P4_TRANSICION_PASIVA_V1", cuts=result,
                                          M2_steps_executed=0, recoveries=used,
                                          responses_sha256=sha(output / "RESPUESTAS_TRANSICION.npz")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("archivos", "cifrado", "salida"):
        parser.add_argument("--"+flag, required=True, type=Path)
    args = parser.parse_args()
    main(args.archivos.resolve(), args.cifrado.resolve(), args.salida.resolve())
