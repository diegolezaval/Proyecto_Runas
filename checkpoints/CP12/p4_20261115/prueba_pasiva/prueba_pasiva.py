"""Factorial pasivo de P4 en cortes recuperados de P3. Cero pasos M2."""

import argparse
from contextlib import contextmanager
from copy import copy
from datetime import datetime, timezone
from importlib.metadata import version
import os
from pathlib import Path
import platform
import sys

if os.environ.get("OPENBLAS_CORETYPE") or sys.flags.optimize:
    raise RuntimeError("Se exigen comprobaciones activas y arquitectura BLAS autodetectada.")
os.environ.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
sys.dont_write_bytecode = True

import numpy as np
from scipy.integrate import DOP853
from scipy.integrate._ivp import base, rk
from scipy.interpolate import CubicSpline
from threadpoolctl import threadpool_info

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
HISTORY = REPO / "checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115"
sys.path.insert(0, str(HISTORY))
from diagnosticar import load_state, read, recover, sha, verify_file, write
from diagnostico_d2 import bessel_wavenumbers, weighted_spectrum

ARMS = ("base", "conmutador", "propagador", "combinado", "geometria_k4", "geometria_k8")
INTERPS = ("cubica_original", "paridad_origen", "cubica_inversa")
WINDOWS = {"r_lt_40": (0, 40), "r_10_20": (10, 20), "r_20_40": (20, 40),
           "r_40_220": (40, 220)}
ORDERS = (7, 6)
P3_STEP = .01
NSTEPS = 40


@contextmanager
def block_m2(observer):
    methods = ((DOP853, "__init__"), (DOP853, "_step_impl"), (DOP853, "_dense_output_impl"),
               (base.OdeSolver, "step"), (observer.Budget, "advance"))
    originals = [(cls, name, getattr(cls, name)) for cls, name in methods]
    attempts = []
    try:
        for cls, name, _ in originals:
            def blocked(*args, _name=f"{cls.__name__}.{name}", **kwargs):
                attempts.append(_name)
                raise RuntimeError(f"Operación M2 prohibida: {_name}")
            setattr(cls, name, blocked)
        yield attempts
    finally:
        for cls, name, method in originals:
            setattr(cls, name, method)


def reduce_grid(sim, S, ells):
    reduced = copy(sim)
    ids = [int(np.flatnonzero(sim.ell == ell)[0]) for ell in ells]
    reduced.ell, reduced.nm = ells, len(ells)
    reduced.angular = ells*(ells+1)
    reduced.cent = sim.dx/sim.w[:, None]*reduced.angular
    reduced.Y, reduced.YW = S.T @ sim.Y, sim.YW @ S
    reduced.powers = sim.powers[:, ids]
    reduced.conductance_u = sim.conductance_u[:, ids]
    reduced.boundary_u = sim.boundary_u[ids]
    return reduced


def transfer(source, target, x, tag, parity=None):
    if tag == "paridad_origen":
        assert parity is not None
        return CubicSpline(np.r_[-source.r[::-1], source.r],
                           np.concatenate((x[..., ::-1, :]*parity, x), axis=-2),
                           axis=-2)(target.r)
    return CubicSpline(source.r, x, axis=-2)(target.r)


def norm(sim, masses, qv):
    q, v = qv
    return np.sqrt(np.sum(sim.w[None, :, None]*(q*q + (v*v)/masses[:, None, None])))


def simulate(sim, forces, jac, stages, P3, P4):
    zero = np.zeros((3, sim.n, sim.nm))
    c3, delta, g4, g8 = forces
    b3 = np.stack((c3, c3+delta, c3-g4, c3-g8, delta))
    b4 = np.stack((c3, c3+delta, zero, zero, delta))
    solvers = [cls(sim, 3, stages, zero, zero) for cls in (P3, P4)]
    for solver, data in zip(solvers, (b3, b4)):
        forcing = np.broadcast_to(data, (stages, *data.shape))
        jacobians = np.broadcast_to(jac, (stages, *jac.shape))
        for _ in range(NSTEPS):
            solver.advance(P3_STEP, forcing, jacobians)

    p3, p4 = solvers
    relative = []
    vectors = []
    for x3, x4 in ((p3.q, p4.q), (p3.v, p4.v)):
        vectors.append(np.stack((x3[0], x3[1], x4[0], x4[1], x3[2], x3[3])))
    for solver in solvers:
        q, v = solver.q, solver.v
        residual = (q[1]-q[0]-q[4], v[1]-v[0]-v[4])
        relative.append(norm(sim, solver.masses, residual)/norm(sim, solver.masses, (q[1], v[1])))
    diagnostics = dict(linearity_closures=relative,
                       stage_residuals=[s.max_iteration_residual for s in solvers],
                       stage_max_iterations=[s.max_iterations for s in solvers])
    assert max(relative) <= 2e-10 and max(diagnostics["stage_residuals"]) <= 1e-12
    assert not np.any(p4.q[2:4]) and not np.any(p4.v[2:4])
    return tuple(vectors), diagnostics


class SpectralPower:
    def __init__(self, sim, mu):
        self.sim, self.mu = sim, mu
        self.modes = {}
        for ell in (2, 4):
            _, basis, residual = weighted_spectrum(sim, ell)
            k = bessel_wavenumbers(sim.n, ell, sim.radius)
            self.modes[ell] = (k, basis, residual)

    def project(self, vectors, lo, hi, ell):
        use = (self.sim.r >= lo) & (self.sim.r < hi)
        sw = np.sqrt(self.sim.w*use)[:, None]
        k, U, _ = self.modes[ell]
        angular = self.sim.ell == ell
        q, v = (a[:, 2][..., angular] for a in vectors)
        weighted = (q*sw, v*(sw/self.mu))
        modal = tuple(U.T @ a for a in weighted)
        parseval = max(float(np.max(abs(np.sum(x*x, axis=(1, 2))-np.sum(y*y, axis=(1, 2))) /
                                    np.maximum(np.sum(x*x, axis=(1, 2)), 1e-300)))
                      for x, y in zip(weighted, modal))
        assert parseval <= 2e-11
        return weighted, tuple(a[:, k > 8] for a in modal), parseval


def scores(qv, scale):
    def dot(x, y):
        return sum(float(np.vdot(a, b)) for a, b in zip(x, y))

    u = np.concatenate([a.reshape(len(ARMS), -1) for a in qv], axis=1)
    G = u @ u.T
    start = G[0, 0]
    assert start > 0
    effect = {}
    for index, name in enumerate(ARMS[1:], 1):
        x, delta = [a[0] for a in qv], [a[index]-a[0] for a in qv]
        signed, square = 2*dot(x, delta), dot(delta, delta)
        change = (signed+square)/start
        closure = abs(change-(G[index, index]-start)/start)
        assert closure <= 2e-11
        effect[name] = dict(relative_power_change=change, twice_inner_over_base=signed/start,
                            increment_power_over_base=square/start, power_identity_residual=closure)
    return dict(base_power_over_initial=start/scale,
                field_power_over_initial=np.sum(qv[0]**2, axis=(1, 2))/scale,
                scaled_velocity_power_over_initial=np.sum(qv[1]**2, axis=(1, 2))/scale,
                gram_over_initial=G/scale, effects=effect,
                interaction_power_over_base=dot([a[3]-a[1]-a[2]+a[0] for a in qv],
                                                [a[3]-a[1]-a[2]+a[0] for a in qv])/start)


def measure(orders, spectrum, scale):
    metrics, max_order = {}, 0.
    for window, (lo, hi) in WINDOWS.items():
        metrics[window] = {}
        for ell in (2, 4):
            all7, high7, err7 = spectrum.project(orders[7], lo, hi, ell)
            all6, high6, err6 = spectrum.project(orders[6], lo, hi, ell)
            m = dict(max_parseval=max(err7, err6))
            for name, x7, x6 in (("toda_k", all7, all6), ("k_gt_8", high7, high6)):
                delta2 = sum(np.sum((a-b)**2, axis=(1, 2)) for a, b in zip(x7, x6))
                base2 = sum(np.sum(a*a, axis=(1, 2)) for a in x7)
                rel = np.sqrt(delta2/np.maximum(base2, 1e-300))
                max_order = max(max_order, float(np.max(rel)))
                m[name] = dict(GL7=scores(x7, scale), GL6=scores(x6, scale),
                               order_relative_by_arm=rel)
            metrics[window][str(ell)] = m
    return metrics, max_order


def classify(results, limit):
    relevant = results["160"]
    by_interp = {}
    for tag, branch in relevant.items():
        by_interp[tag] = {}
        for ell, m in branch["windows"]["r_lt_40"].items():
            d = m["k_gt_8"]
            signs = [d[f"GL{s}"]["effects"]["combinado"]["relative_power_change"] for s in ORDERS]
            by_interp[tag][ell] = dict(relative_power_changes=signs,
                                      GL_sign_agrees=bool(np.sign(signs[0]) == np.sign(signs[1])))

    modes = [m for pair in by_interp.values() for m in pair.values()]
    max_obs = max(case["maximum_order_relative"] for cut in results.values() for case in cut.values())
    if max_obs > limit or not all(m["GL_sign_agrees"] for m in modes):
        outcome = "INCONCLUSO_ORDEN"
    else:
        outcome = "PASA" if all(max(m["relative_power_changes"]) < 0 for m in modes) else "REFUTADO"

    geometry = []
    for ell, m in relevant["cubica_original"]["windows"]["r_lt_40"].items():
        for cut in ("geometria_k4", "geometria_k8"):
            effects = m["k_gt_8"]["GL7"]["effects"]
            numerator = abs(effects[cut]["relative_power_change"])
            denominator = abs(effects["combinado"]["relative_power_change"])
            ratio = numerator/denominator if denominator else None
            geometry.append(dict(ell=int(ell), cut=cut, ratio_to_combined_abs_change=ratio,
                                 comparable=ratio is None or ratio >= .5))
    return dict(outcome=outcome, opens_physical_pilot=outcome == "PASA", by_interp=by_interp,
                geometry=geometry, maximum_order_relative=max_obs)


def run_cut(tick, saved, sims, reduced, S, branches, geometry, spectra, observer, ops, P3, out_arrays):
    sc, sf = sims
    qc, qf = np.split(saved["q"], [sc.n], axis=1)
    iq, iv = (saved[name][2, sc.n:] for name in ("initial_q", "initial_v"))
    scale = observer.chi_inner(sf, iq, iv, iq, iv)
    assert scale > 0
    raw_jac = observer.terms(sc, sf, qc, qf)[2]
    products = (reduced[1].Y[:, None, :]*reduced[1].Y[None, :, :]*sf.wa)
    jac_fine = (raw_jac.reshape(-1, len(sf.wa)) @ products.reshape(36, -1).T)
    jac_fine = jac_fine.reshape(6, sf.n, 6, 6)
    jac_coarse = CubicSpline(sf.r, jac_fine, axis=1)(sc.r)
    q = (qc @ S, qf @ S)
    sym = [observer.symmetry_residual(s, S, field) for s, field in zip(sims, (qc, qf))]
    assert max(sym) <= 2e-12
    results = {}

    for tag, src, dst, orientation in branches:
        source, target = reduced[src], reduced[dst]
        source_chi = q[src][2:3]
        def I(x):
            return transfer(source, target, x, tag, (-1.)**source.ell)

        chi = I(source_chi)
        c3 = I(ops.lap_chi(source, source_chi)) - ops.lap_chi(target, chi)
        delta = I(ops.delta_lap(source, source_chi)) - ops.delta_lap(target, chi)
        corrections = []
        for cutoff in (4, 8):
            gs = geometry[src, cutoff].evaluate(source_chi[0])
            gt = geometry[dst, cutoff].evaluate(chi[0])
            corrections.append((source.dx**2 * I(gs) - target.dx**2 * gt)[None])

        def in_chi(x):
            force = np.zeros((3, target.n, target.nm))
            force[2:3] = orientation*x
            return force

        data = tuple(in_chi(fn) for fn in (c3, delta, *corrections))
        all_orders, checks = {}, {}
        for stages in ORDERS:
            all_orders[stages], checks[f"GL{stages}"] = simulate(
                target, data, (jac_coarse, jac_fine)[dst], stages, P3, ops.MixedP4Gauss)
            a, b = all_orders[stages]
            prefix = f"t{tick}_{tag}_GL{stages}"
            out_arrays.update({prefix+"_chi": a[:, 2], prefix+"_dotchi_over_mu": b[:, 2]/spectra[dst].mu})
            print(f"τ{tick}, {tag}, GL{stages}: respuestas y cierre calculados", flush=True)
        windows, maximum = measure(all_orders, spectra[dst], scale)
        results[tag] = dict(windows=windows, maximum_order_relative=maximum, controls=checks,
                            target_h=target.dx, orientation=orientation,
                            initial_phase_scale=scale, symmetry_residuals=sym)
    return results


def environment(reg):
    now = dict(python=platform.python_version(), packages={name: version(name) for name in reg["packages"]},
               blas=[{k: p[k] for k in ("version", "architecture", "num_threads", "threading_layer")}
                     for p in threadpool_info()])
    assert now["python"] == reg["python"] and now["packages"] == reg["packages"]
    assert now["blas"] and all(p == reg["blas"] for p in now["blas"])
    verify_file(Path(rk.__file__), reg["rk_sha256"])
    verify_file(Path(base.__file__), reg["ivp_base_sha256"])
    return now


def start(archives, encrypted, out):
    regpath = HERE / "REGISTRO.json"
    registration_sha = sha(regpath)
    reg = read(regpath)
    p3 = read(HISTORY / "REGISTRO.json")
    assert reg["M2_steps_authorized"] == 0
    for rel, expected in reg["files_sha256"].items():
        verify_file(REPO / rel, expected)
    env = environment(reg)
    assert not out.exists() and not out.is_relative_to(REPO)
    out.mkdir(parents=True, mode=0o700)
    start_time = datetime.now(timezone.utc).isoformat()
    p3["capsules"] = {str(n): p3["capsules"][str(n)] for n in reg["cuts"]}
    inputs, reused = recover(REPO, p3, archives, encrypted, out)
    for folder, _, _ in inputs.values():
        for rel, expected in p3["capture_sha256"].items():
            verify_file(folder / rel, expected)
    home = inputs[160][0]
    sys.path[:0] = [str(home / "candidate"), str(home / "science/herramientas"), str(home)]
    import observador_causal_CP12 as observer
    from p3_backend import MixedP3, MixedP3Gauss
    import operador_pasivo as ops

    print("Identidad P3 y cargas de ambas cápsulas acreditadas", flush=True)
    with block_m2(observer) as attempts:
        same_config = read(home / "configuration.json")["original_configuration"]
        assert same_config["observer_max_step"] == P3_STEP
        assert same_config["observer_stages"] == list(ORDERS)
        assert same_config["observer_relative_tolerance"] == reg["GL_relative_limit"]
        configs = same_config["physical_configurations"]
        sims = [MixedP3(c["dx"], c["radius"], c["L"]) for c in configs]
        small_sims = [MixedP3(c["dx"], 8., 4) for c in configs]
        manufactured = {str(s.dx): ops.manufactured_resolvent(s, P3_STEP, NSTEPS) for s in small_sims}
        geometry = {(j, k): ops.RegularGeometry(sim, k)
                    for j, sim in enumerate(sims) for k in (4, 8)}
        fabricated = {f"{j}_k{k}": g.manufactured() for (j, k), g in geometry.items()}
        write(out / "CONTROLES_PREVIOS.json", dict(scalar_resolvent=manufactured, geometry=fabricated))
        print("Perfiles fabricados y resolventes compatibles con la referencia", flush=True)

        saved = {t: load_state(folder, t, same_config, p3) for t, (folder, _, _) in inputs.items()}
        a, b = saved[112], saved[160]
        for name in ("initial_q", "initial_v", "coupled_angular_basis"):
            assert np.array_equal(a[name], b[name])
        S, fine_reduced = observer.symmetry_basis(sims[1], b["initial_q"][:, sims[0].n:])
        assert np.allclose(S, b["coupled_angular_basis"], atol=2e-12, rtol=0)
        assert np.max(abs(S.T @ S - np.eye(S.shape[1]))) <= 2e-12
        reduced = [reduce_grid(sim, S, fine_reduced.ell) for sim in sims]
        spectra = [SpectralPower(sim, observer.model.mediator) for sim in reduced]
        arrays = {"S_angular": S, "ells": fine_reduced.ell, "armas": ARMS,
                  "r_gruesa": sims[0].r, "r_fina": sims[1].r, "W_gruesa": sims[0].w, "W_fina": sims[1].w}
        branches = list(zip(INTERPS, (0, 0, 1), (1, 1, 0), (1, 1, -1)))
        results = {}
        # Evaluate the decisive cut first. Persist each finished cut privately.
        for t in (160, 112):
            results[str(t)] = run_cut(t, saved[t], sims, reduced, S, branches, geometry, spectra,
                                      observer, ops, MixedP3Gauss, arrays)
            write(out / f"TAU{t}_COMPLETO.json", results[str(t)])
        assert not attempts, attempts

    for t, (folder, archive, manifest) in inputs.items():
        spec = p3["capsules"][str(t)]
        for path, meta in manifest["files"].items():
            verify_file(folder / path, meta["sha256"], meta["bytes"])
        verify_file(archive, spec["sha256"], spec["bytes"])
        reused[str(t)].update(all_payload_hashes_before_and_after=True, payload_files=len(manifest["files"]),
                              sha256=spec["sha256"], state_sha256=spec["state_sha256"],
                              github_asset_id=spec["github_asset_id"])
    verify_file(encrypted, p3["capsules"]["160"]["encrypted"]["sha256"],
                p3["capsules"]["160"]["encrypted"]["bytes"])
    verify_file(regpath, registration_sha)
    for rel, expected in reg["files_sha256"].items():
        verify_file(REPO / rel, expected)

    decision = classify(results, reg["GL_relative_limit"])
    arrays_path = out / "RESPUESTAS_PRIVADAS.npz"
    np.savez_compressed(arrays_path, **arrays)
    write(out / "RECIBO.json", dict(
        schema="CP12_P4_PRUEBA_PASIVA_FACTORIAL_V1", registration_sha256=registration_sha,
        started_at_utc=start_time, completed_at_utc=datetime.now(timezone.utc).isoformat(),
        P3_execution_uuid=p3["execution_uuid"], P3_run_id=p3["run_id"], recoveries=reused,
        ciphertext_sha256=p3["capsules"]["160"]["encrypted"]["sha256"], controls=manufactured,
        geometry_controls=fabricated, observed_environment=env,
        M2_steps_executed=0, M2_attempts=attempts, passive_interval=NSTEPS*P3_STEP, passive_step=P3_STEP,
        passive_steps_per_cut_interpolation_order_and_propagator=NSTEPS, arm_order=ARMS,
        max_eigenpair_residual=max(r for sp in spectra for _, _, r in sp.modes.values()),
        CP12_closed=False, P4_pilot_started=False, decision=decision, response_vectors_sha256=sha(arrays_path),
        complete_results_sha256={str(t): sha(out / f"TAU{t}_COMPLETO.json") for t in (112, 160)}))
    print(decision["outcome"], flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("archivos", "cifrado", "salida"):
        cli.add_argument(f"--{name}", required=True, type=Path)
    opts = cli.parse_args()
    start(opts.archivos.resolve(), opts.cifrado.resolve(), opts.salida.resolve())
