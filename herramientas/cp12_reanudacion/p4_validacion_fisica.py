"""Lecturas y controles de las variantes prerregistradas de P4."""
import argparse
from copy import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .infra import read, record, require, sha
from .p4_tercera_fisica import METRICS, Trial


class Contrast:
    def __init__(self, registration, third_registration, home, case):
        self.reg = read(registration)
        self.baseline = Trial(home, third_registration)
        self.case = case
        self.spec = self.reg["cases"][case]
        self.variant = copy(self.baseline)
        self.variant.cfg = self.spec["configuration"]
        self.variant.identity = {
            "campaign_uuid": self.reg["campaign_uuid"],
            "registration_sha256": sha(registration),
            "case": case,
        }
        require(self.baseline.cfg == self.reg["base_configuration"]
                and self.variant.cfg == dict(self.baseline.cfg, **self.spec["changed"])
                and self.baseline.criteria == self.reg["physical_limits"],
                "La configuración no reproduce el contraste registrado")
        self.np = self.baseline.np

    def preflight(self, stream, baseline):
        np = self.np
        sim = stream.sim
        n, m = baseline["q"].shape[1:]
        require(sim.n >= n and sim.nm >= m
                and np.array_equal(np.asarray(sim.labels[:m], dtype=str), baseline["labels"])
                and np.array_equal(sim.r[:n], (np.arange(n) + .5) * self.baseline.cfg["dx"]),
                "No coinciden las celdas o los armónicos comunes")
        ratio = self.variant.cfg["eps"] / self.baseline.cfg["eps"]
        differences = []
        for k, field in enumerate((stream.initial_q, stream.initial_v)):
            original = baseline[("q", "v")[k]]
            expected = original.copy()
            expected[:, :, 1:] *= ratio
            differences.append(float(np.max(abs(field[:, :n, :m] - expected))))
            differences.append(float(np.max(abs(field[:, :, m:]))) if sim.nm > m else 0.)

        rng = np.random.default_rng(20261002)
        cases = [stream.q, stream.q + rng.normal(size=stream.q.shape) * 1e-5]
        force_errors = []
        for q in cases:
            a, b = stream.numpy_force(q), sim.force(q)
            force_errors.append(float(np.max(abs(a - b)) / max(1., np.max(abs(a)))))
        direction = rng.normal(size=stream.q.shape) * np.exp(-sim.r[None, :, None] / 20)
        weights = sim.w[None, :, None] * np.array([2., 2., 1.])[:, None, None]

        def gradient_residual(evolution, force):
            step = 1e-24
            parts = evolution.components(stream.q + 1j * step * direction, stream.v)
            numeric = sum(np.sum(p).imag for p in parts[:4]) / step
            exact = -np.sum(weights * direction * force)
            return float(abs(numeric - exact) / max(1., abs(numeric), abs(exact)))

        a = sim.force(stream.q)
        charge_terms = sim.w * 2 * np.sum(stream.q[0] * a[1] - stream.q[1] * a[0], axis=1)
        charge = float(abs(charge_terms.sum()) / max(1., abs(charge_terms).sum()))
        angular = float(np.max(abs((sim.Y * sim.wa) @ sim.Y.T - np.eye(sim.nm))))
        from p4_backend import lap_chi
        lap = sim.lap(cases[1])
        routes = bool(np.array_equal(lap[:2], stream.original_sim.lap(cases[1])[:2])
                      and np.array_equal(lap[2:], lap_chi(sim, cases[1][2:])))
        algebra = dict(force_C_NumPy=max(force_errors), angular_gram=angular, charge_gradient=charge,
                       P4_energy_gradient=gradient_residual(sim, stream.numpy_force(stream.q)),
                       FV_energy_gradient=gradient_residual(stream.original_sim,
                                                            stream.original_sim.force(stream.q)))
        checks = dict(common_Cauchy=max(differences) <= self.reg["initial_field_max_abs"],
                      routing=routes, algebra=all(x <= self.reg["algebra_max"] for x in algebra.values()),
                      source_CP04=stream.transfer["source_sha256"] == self.baseline.reg["original_Cauchy_sha256"])
        return dict(passed=all(checks.values()), checks=checks, algebra_residuals=algebra,
                    common_Cauchy_max_abs=max(differences), source_transfer=stream.transfer,
                    mode_count=sim.nm, cells=sim.n, force=stream.force_receipt)

    def original_metrics(self, baseline, variant):
        np = self.np
        labels = baseline["labels"]
        width = len(labels)
        projected = dict(variant)
        require(np.array_equal(variant["labels"][:width], labels), "Cambió la base angular común")
        if len(variant["labels"]) != width:
            for key in ("q", "v", "initial_q", "initial_v"):
                projected[key] = variant[key][:, :, :width]
            projected["labels"] = labels
            projected["rows"] = variant["rows"].copy()
            degree = self.baseline.cfg["L"]
            projected["rows"][:, 5] = np.linalg.norm(variant["rows"][:, 6:6+degree], axis=1)
        pair = (projected, baseline) if self.spec["kind"] == "temporal" else (baseline, projected)
        with TemporaryDirectory() as room:
            paths = [Path(room) / name for name in ("izquierda.npz", "derecha.npz")]
            for path, grid in zip(paths, pair):
                np.savez(path, **{k: grid[k] for k in ("q", "v", "initial_q", "initial_v", "labels", "rows", "time")},
                         config=json.dumps(grid["config"]))
            # Las fracciones descriptivas de un residuo exactamente cero pueden ser 0/0.
            with np.errstate(invalid="ignore", divide="ignore"):
                raw = self.baseline.comparator(int(variant["time"]))(*paths)
        metrics = {key: float(raw[key]) for key in METRICS}
        require(all(np.isfinite(x) and x >= 0 for x in metrics.values()), "Métricas originales no finitas")
        return metrics

    def observations(self, data):
        np = self.np
        rows, consistent, meta = data["rows"], data["consistent_rows"], data["metadata"]
        return dict(initial_FV_energy=float(rows[0, 1]), final_FV_energy=float(rows[-1, 1]),
                    initial_P4_energy=float(consistent[0, 1]), final_P4_energy=float(consistent[-1, 1]),
                    initial_charge=float(rows[0, 2]), final_charge=float(rows[-1, 2]),
                    max_FV_energy_drift=meta["maxe_original"], max_P4_energy_drift=meta["maxe"],
                    max_charge_drift=meta["maxq"],
                    max_core_charge_change=float(np.max(abs(rows[:, 4] / rows[0, 4] - 1))),
                    amplification=float(rows[:, 5].max() / rows[0, 5]),
                    accepted_steps=meta["accepted"], force_evaluations=meta["nfev"])

    def chi_windows(self, baseline, variant):
        np = self.np
        mu = self.baseline.obs.model.mediator
        h = self.baseline.cfg["dx"]
        n = baseline["q"].shape[1]
        edges = np.arange(n + 1) * h
        r = (edges[1:] + edges[:-1]) / 2
        weights = np.diff(edges**3) / 3
        degrees = variant["labels"][:, 0].astype(int)
        width = len(baseline["labels"])

        def phase(grid):
            return np.stack((grid["q"][2, :n], grid["v"][2, :n] / mu))

        def scale(grid):
            use = r < 40
            q, v = grid["initial_q"][2, :n], grid["initial_v"][2, :n]
            return float(np.sqrt(np.sum(weights[use, None] * (q[use, 1:]**2 + (v[use, 1:] / mu)**2))))

        left, right = phase(baseline), phase(variant)
        baseline_scale, variant_scale = scale(baseline), scale(variant)
        ratio = self.baseline.cfg["eps"] / self.variant.cfg["eps"]
        require(min(baseline_scale, variant_scale) > 0, "La semilla de χ tiene norma cero")
        windows = []
        for low, high in self.reg["radial_windows"]:
            use = (r >= low) & (r < high)
            w = weights[use, None]

            def norm(x):
                sq = np.sum(w * x[:, use]**2, axis=(1, 2))
                return dict(field=float(np.sqrt(sq[0])), velocity_over_mu=float(np.sqrt(sq[1])),
                            phase=float(np.sqrt(sq.sum())))

            modes = {}
            for ell in self.reg["chi_ells"]:
                indexes = degrees[:width] == ell
                a, b = left[:, :, indexes], right[:, :, :width][:, :, indexes]
                modes[str(ell)] = dict(baseline_normalized=norm(a / baseline_scale),
                                       variant_normalized=norm(b / variant_scale),
                                       difference_over_variant_seed=norm((b-a) / variant_scale))
                if "eps" in self.spec["changed"]:
                    modes[str(ell)]["difference_per_seed_amplitude"] = norm((ratio*b-a) / baseline_scale)
            if self.variant.cfg["L"] > self.baseline.cfg["L"]:
                modes["added"] = {str(ell): norm(right[:, :, degrees == ell] / variant_scale)
                                  for ell in range(self.baseline.cfg["L"]+1, self.variant.cfg["L"]+1)}
            windows.append(dict(r_min=low, r_max=high, modes=modes))
        return dict(initial_chi_phase_norm_base=baseline_scale,
                    initial_chi_phase_norm_variant=variant_scale, windows=windows)

    def exterior(self, stream):
        # Reparte la cara de corte a partes iguales, como en el observador original.
        result = {}
        cut = round(self.baseline.cfg["radius"] / stream.config["dx"])
        if cut >= stream.sim.n:
            return result
        for label, sim in (("P4", stream.sim), ("FV", stream.original_sim)):
            result[label] = []
            for clock, q, v in ((0., stream.initial_q, stream.initial_v), (stream.t, stream.q, stream.v)):
                bulk, faces, angular, boundary, charge = sim.components(q, v)
                energy = np_sum(bulk[cut:]) + np_sum(angular[cut:]) + np_sum(faces[cut:]) + .5*faces[cut-1] + boundary
                result[label].append(dict(time=clock, energy=float(energy), charge=np_sum(charge[cut:])))
        return result

    def recover(self, folder, baseline_file):
        np = self.np
        state_file = folder / "ESTADO.npz"
        state_hash = sha(state_file)
        evo = read(folder / "EVOLUCION.json")
        identity = self.variant.identity
        require(evo["state_sha256"] == state_hash and all(evo[k] == v for k, v in identity.items()),
                "Procedencia distinta del archivo recuperado")
        negative = evo.get("negative")
        with self.baseline.legacy.zero_m2_audit() as attempts:
            recovered = self.variant.read_state(state_file)
            t = recovered["time"]
            require(evo["time"] == t, "El reloj de evolución no coincide con el estado")
            if negative:
                controls = dict(passed=False, failure=negative, integrity_only=True)
            else:
                require(t in range(0, 161, 8), "La recuperación no es una frontera")
                baseline = self.baseline.read_state(baseline_file)
                require(baseline["time"] == t, "Referencia guardada de otro reloj")
                stream = self.variant.stream(self.variant.cfg, recovered)
                clocks = np.arange(round(t / .4) + 1) * .4
                rows = (recovered["rows"], recovered["consistent_rows"])
                m = (stream.original_sim.measure(t, stream.q, stream.v), stream.sim.measure(t, stream.q, stream.v))
                safe = self.reg["recovery_measure_max"]
                consistent = all(np.array_equal(a[:, 0], clocks)
                                 and np.allclose(a[-1], b, rtol=safe, atol=safe) for a, b in zip(rows, m))
                consistent &= all(np.isfinite(recovered[k]).all() for k in ("q", "v", "rows", "consistent_rows"))
                consistent &= stream.nfev >= stream.accepted and ((t == 0) == (stream.accepted == 0))
                require(consistent, "Las observaciones o los contadores recuperados no se reproducen")
                gates = self.variant.physical(recovered)
                controls = dict(passed=all(gates.values()), physical=gates,
                                balances=dict(variant=self.observations(recovered), base=self.observations(baseline)))
                if t == 0:
                    controls["preflight"] = self.preflight(stream, baseline)
                    controls["passed"] &= controls["preflight"]["passed"]
                else:
                    metrics = self.original_metrics(baseline, recovered)
                    controls.update(metrics=metrics, chi=self.chi_windows(baseline, recovered))
                    if self.spec["kind"] == "temporal":
                        limit = self.reg["physical_limits"]["field_and_phase_space_relative_error_max"]
                        budget = self.reg["temporal_budget"][str(int(t))]["limit"]
                        gate = {k: metrics[k] <= limit and metrics[k] <= budget[k] for k in METRICS}
                        controls.update(temporal_per_axis_gates=gate, passed=controls["passed"] and all(gate.values()))
                if "radius" in self.spec["changed"]:
                    controls["exterior_220_264"] = self.exterior(stream)
        require(sha(state_file) == state_hash and not attempts, "La auditoría alteró la frontera")
        return dict(**identity, **controls, time=t, state_sha256=state_hash, M2_steps_executed=0,
                    DOP853_construction_or_step_attempts=len(attempts))


def np_sum(x):
    return float(x.sum())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("registration", "third_registration", "home", "folder", "baseline", "output"):
        parser.add_argument("--" + name.replace("_", "-"), required=True, type=Path)
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    test = Contrast(args.registration, args.third_registration, args.home, args.case)
    result = test.recover(args.folder, args.baseline)
    record(args.output, result)
    print(json.dumps(dict(case=args.case, time=result["time"], passed=result["passed"])), flush=True)
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
