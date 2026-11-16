"""Tercera malla P4 con el integrador, semillas y comparador capturados."""
import argparse
import ast
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import zipfile

from .infra import module, read, record, require, sha


METRICS = (
    "norm_relative_sup_error",
    "final_complex_nonradial_field_error_over_initial_norm",
    "final_phi_phase_space_error_over_initial_norm",
    "final_mediator_nonradial_error_over_initial_norm",
    "final_mediator_phase_space_error_over_initial_norm",
)
PHASE = METRICS[-1]


class Trial:
    def __init__(self, home, registration):
        self.reg = read(registration)
        self.home = home
        require(self.reg["registered_before_M2"] and self.reg["M2_steps_executed"] == 0,
                "Se requiere el prerregistro anterior a M2")
        require(sha(home / "configuration.json") == self.reg["pilot_configuration_sha256"],
                "Configuración del piloto distinta")
        self.legacy = module(home / "coordinator.py", "coordinador_p4_capturado")
        _, identity, science, _, _, _, self.modules = self.legacy.setup(home)
        require(identity["execution_uuid"] == self.reg["pilot_execution_uuid"]
                and identity["execution_run_id"] == self.reg["pilot_run_id"], "Origen de otro piloto")
        self.np = self.modules["np"]
        self.base = self.modules["base"]
        self.obs = self.modules["obs"]
        self.native = self.modules["native"]
        self.candidate = self.modules["Candidate"]
        self.cfg = self.reg["candidate"]
        self.criteria = self.reg["criteria"]
        self.reference_path = science / "herramientas/diagnosticar_mediador_CP10.py"
        for path, key in (
            (science / self.reg["original_Cauchy"], "original_Cauchy_sha256"),
            (self.reference_path, "original_comparator_sha256"),
            (science / "herramientas/continuar_no_radial_m2.py", "original_preparation_sha256"),
            (home / "candidate/p4_backend.py", "p4_backend_sha256"),
        ):
            require(sha(path) == self.reg[key], "Fuente capturada distinta: " + path.name)
        sys.path.insert(0, str(home))
        from transporte import scipy_identity
        require(scipy_identity() == read(home / "configuration.json")["dop853_implementation_identity"],
                "Implementación DOP853 distinta")
        original = self.modules["cfg"]["physical_configurations"]
        require(self.cfg == dict(original[1], dx=0.03125), "Cambió una variable distinta de h")
        self.original = original
        self.identity = {key: self.reg[key] for key in ("execution_uuid", "execution_run_id")}

    def stream(self, configuration, restored=None):
        trial = self
        np = self.np

        class Stream(self.native.PhysicalStream):
            def __init__(self):
                self.config = configuration
                dx, radius, degree = (configuration[k] for k in ("dx", "radius", "L"))
                self.sim = trial.candidate(dx, radius, degree)
                self.original_sim = trial.base.Evolution(dx, radius, degree)
                q, v, self.transfer = trial.base.seed(self.sim, configuration["eps"])
                self.initial_q, self.initial_v = q.copy(), v.copy()
                self.q, self.v = q, v
                self.t = 0.0
                self.accepted = self.nfev = 0
                self.maxe = self.maxe_original = self.maxq = 0.0
                self.rows = [self.sim.measure(0, q, v)]
                self.original_rows = [self.original_sim.measure(0, q, v)]
                self.shape = (2, 3, self.sim.n, self.sim.nm)
                self.solver = self.dense = None
                self.numpy_force = self.sim.force
                self.force_receipt = trial.modules["accelerated"].install(self.sim)
                if restored is not None:
                    require(np.array_equal(restored["initial_q"], self.initial_q)
                            and np.array_equal(restored["initial_v"], self.initial_v),
                            "La semilla recuperada no coincide con la preparación")
                    self.q, self.v = restored["q"], restored["v"]
                    self.rows = restored["consistent_rows"].tolist()
                    self.original_rows = restored["rows"].tolist()
                    for key, value in restored["metadata"].items():
                        setattr(self, key, value)
                self.nextobs = round(self.rows[-1][0] / .4 + 1) * .4

            def advance(self, bound):
                start = len(self.rows)
                dense = super().advance(bound)
                measured = self.original_sim.measure(self.t, self.q, self.v)
                self.maxe_original = max(self.maxe_original, abs(measured[1] / self.original_rows[0][1] - 1))
                for row in self.rows[start:]:
                    q, v = dense(min(row[0], self.t)).reshape(self.shape)
                    self.original_rows.append(self.original_sim.measure(row[0], q, v))
                if not np.isfinite(measured).all() or self.maxe_original > trial.criteria["energy_drift_max"]:
                    raise ValueError("Falló la puerta de energía FV")
                return dense

            def close_segment(self):
                require(self.solver.status == "finished", "Segmento incompleto")
                self.nfev += self.solver.nfev
                self.solver = self.dense = None

            def metadata(self):
                return dict(t=self.t, accepted=self.accepted, nfev=self.nfev, maxe=self.maxe,
                            maxe_original=self.maxe_original, maxq=self.maxq)

        return Stream()

    def pilot_pair(self, archive, t):
        spec = self.reg["pilot_frontiers"][str(t)]
        require(archive.stat().st_size == spec["bytes"] and sha(archive) == spec["archive_sha256"],
                "Cápsula del piloto distinta del prerregistro")
        with zipfile.ZipFile(archive) as z:
            payload = z.read("outputs/MIXTO_par_estado.npz")
            receipt = z.read("outputs/procedencia.json")
        from .infra import digest
        require(digest(payload) == spec["state_sha256"] and digest(receipt) == spec["run_receipt_sha256"],
                "Estado/recibo interno distinto del acreditado")
        old = json.loads(receipt)
        require(old["execution_uuid"] == self.reg["pilot_execution_uuid"]
                and old["execution_run_id"] == self.reg["pilot_run_id"] and old["time"] == t,
                "Trayectoria guardada de otra identidad o tiempo")
        np = self.np
        with np.load(io.BytesIO(payload), allow_pickle=False) as data:
            require(str(data["experiment_id"]) == old["execution_run_id"] and float(data["time"]) == t,
                    "NPZ del piloto en otro tiempo")
            require(json.loads(str(data["config"])) == self.modules["cfg"], "Configuración guardada distinta")
            n = int(data["coarse_n"])
            require(n == 1760 and data["q"].shape == (3, 5280, 25), "Retículos guardados inválidos")
            rows, energies = data["rows"], data["consistent_rows"]
            metadata = json.loads(str(data["metadata"]))
            arrays = {key: data[key] for key in ("q", "v", "initial_q", "initial_v")}
        pair = []
        labels = np.asarray(self.base.harmonics(self.cfg["L"])[0], dtype=str)
        for i, (sl, cfg) in enumerate(zip((slice(None, n), slice(n, None)), self.original)):
            blocks = slice(1, 10) if i == 0 else slice(10, None)
            pair.append(dict(**{key: a[:, sl].copy() for key, a in arrays.items()},
                             rows=np.column_stack((rows[:, 0], rows[:, blocks])),
                             consistent_rows=np.column_stack((energies[:, 0], energies[:, blocks])),
                             labels=labels, config=cfg, time=t, metadata=metadata[i]))
        return pair

    def read_state(self, path):
        np = self.np
        with np.load(path, allow_pickle=False) as data:
            require(json.loads(str(data["identity"])) == self.identity, "Checkpoint de otra identidad")
            require(json.loads(str(data["config"])) == self.cfg, "Checkpoint de otra configuración")
            return dict(**{key: data[key].copy() for key in (
                "q", "v", "initial_q", "initial_v", "rows", "consistent_rows", "labels")},
                        metadata=json.loads(str(data["metadata"])), time=float(data["time"]), config=self.cfg)

    def save(self, stream, folder):
        folder.mkdir(parents=True, exist_ok=True)
        self.np.savez_compressed(folder / "ESTADO.npz", q=stream.q, v=stream.v,
                                 initial_q=stream.initial_q, initial_v=stream.initial_v,
                                 rows=stream.original_rows, consistent_rows=stream.rows,
                                 labels=self.np.asarray(stream.sim.labels, dtype=str), time=stream.t,
                                 metadata=json.dumps(stream.metadata()), config=json.dumps(self.cfg),
                                 identity=json.dumps(self.identity))

    def physical(self, data):
        np = self.np
        rows = data["rows"]
        m = data["metadata"]
        gates = {
            "original_energy": m["maxe_original"] <= self.criteria["energy_drift_max"],
            "P4_energy": m["maxe"] <= self.criteria["energy_drift_max"],
            "charge": m["maxq"] <= self.criteria["charge_drift_max"],
            "core_charge": np.max(abs(rows[:, 4] / rows[0, 4] - 1)) <= self.criteria["core_charge_change_max"],
            "bounded_window": rows[:, 5].max() <= self.criteria["amplification_max"] * rows[0, 5],
        }
        return {key: bool(value) for key, value in gates.items()}

    def origin(self, folder):
        with self.legacy.zero_m2_audit():
            self.save(self.stream(self.cfg), folder)
        record(folder / "EVOLUCION.json", dict(**self.identity, status="ORIGEN_PREPARADO", time=0,
                                               new_M2_steps=0, state_sha256=sha(folder / "ESTADO.npz")))

    def advance(self, previous, target, folder):
        old = self.read_state(previous)
        require(old["time"] + 8 == target and target in range(8, 161, 8), "Tramo fuera de secuencia")
        stream = self.stream(self.cfg, old)
        before_steps = stream.accepted
        negative = None
        try:
            while stream.t < target:
                stream.advance(target)
                if stream.accepted == before_steps + 1:
                    print(f"Primer paso τ{stream.t:.10g}", flush=True)
            stream.close_segment()
        except (ValueError, RuntimeError) as exc:
            if stream.solver is None:
                raise
            original_stop = str(exc).startswith(("Balance original CP10", "Falló la puerta de energía FV"))
            if not original_stop and stream.solver.status != "failed":
                raise
            negative = str(exc)
            stream.nfev += stream.solver.nfev
        self.save(stream, folder)
        record(folder / "EVOLUCION.json", dict(**self.identity,
            status="FALLO_NUMERICO_O_FISICO" if negative else "FRONTERA_ESCRITA",
            from_time=old["time"], time=stream.t, target=target, negative=negative,
            metadata=stream.metadata(), new_M2_steps=stream.accepted - before_steps,
            state_sha256=sha(folder / "ESTADO.npz"), previous_state_sha256=sha(previous),
            original_trajectories_repeated=False))
        return 2 if negative else 0

    def comparator(self, t):
        original = module(self.reference_path, "comparador_original_cp10")
        if t == 160:
            return original.compare
        tree = ast.parse(self.reference_path.read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "compare")
        expected = ast.parse("if c['time'] != 160 or f['time'] != 160:\n    raise ValueError('Tiempo final incorrecto')").body[0]
        require(ast.dump(function.body[1]) == ast.dump(expected), "Guarda original del comparador distinta")
        for node in ast.walk(function.body[1].test):
            if isinstance(node, ast.Constant) and node.value == 160:
                node.value = t
        scope = dict(vars(original))
        exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                     "<comparador_original_tiempo_registrado>", "exec"), scope)
        return scope["compare"]

    def chi_parts(self, data):
        from scipy.interpolate import CubicSpline
        np = self.np
        finest = data[-1]
        h = finest["config"]["dx"]
        r = (np.arange(finest["q"].shape[1]) + .5) * h
        use = r < 40
        weights = (np.diff((np.arange(len(r) + 1) * h)**3) / 3)[use, None]
        mu = self.obs.model.mediator
        initial_q = finest["initial_q"][2, use, 1:]
        initial_v = finest["initial_v"][2, use, 1:] / mu
        scale = np.sum(weights * (initial_q**2 + initial_v**2))
        aligned = []
        for grid in data:
            r_grid = (np.arange(grid["q"].shape[1]) + .5) * grid["config"]["dx"]
            qv = [grid["q"][2, :, 1:], grid["v"][2, :, 1:] / mu]
            aligned.append([x[use] for x in qv] if grid is finest
                           else [CubicSpline(r_grid, x, axis=0)(r[use]) for x in qv])
        result = {}
        for name, left, right in zip(("01", "12"), aligned, aligned[1:]):
            field, velocity = [float(np.sqrt(np.sum(weights * (x - y)**2) / scale))
                               for x, y in zip(left, right)]
            result[name] = dict(field_over_initial_phase_norm=field, velocity_over_initial_phase_norm=velocity,
                                phase=float(np.hypot(field, velocity)))
        return result

    def measurements(self, pair, new, published, t, room):
        np = self.np
        data = [*pair, new]
        paths = [room / f"malla-{i}.npz" for i in range(3)]
        for path, grid in zip(paths, data):
            np.savez(path, **{k: grid[k] for k in ("q", "v", "initial_q", "initial_v", "labels", "rows", "time")},
                     config=json.dumps(grid["config"]))
        compare = self.comparator(t)
        baseline, refined = (compare(c, f) for c, f in zip(paths, paths[1:]))
        require(all(np.isclose(baseline[k], published["comparison"][k],
                               rtol=self.reg["reference_rtol"], atol=self.reg["reference_atol"]) for k in METRICS),
                "La lectura de la pareja del piloto no reproduce la publicada")
        threshold = self.criteria["field_and_phase_space_relative_error_max"]
        gates = [{k: bool(np.isfinite(result[k]) and result[k] <= threshold) for k in METRICS}
                 for result in (baseline, refined)]
        physical = [self.physical(grid) for grid in data]
        parts = [self.chi_parts(data[:2])["01"], self.chi_parts(data[1:])["01"]]
        shared = self.chi_parts(data)
        p = lambda a, b: float(np.log2(a / b)) if min(a, b) > 1e-12 else None
        return dict(pilot_pair=baseline, refined_pair=refined, pairs_passed=gates,
                    physical_gates=physical, field_velocity_parts=parts,
                    chi_phase_original_ratio=refined[PHASE] / baseline[PHASE] if baseline[PHASE] else None,
                    chi_phase_observed_order=p(baseline[PHASE], refined[PHASE]),
                    same_fine_grid_diagnostic=shared,
                    same_fine_grid_observed_order=p(shared["01"]["phase"], shared["12"]["phase"]),
                    passed=all(all(x.values()) for x in [*gates, *physical]))

    def audit(self, folder, pilot, published):
        np = self.np
        state = folder / "ESTADO.npz"
        before = sha(state)
        provenance = read(folder / "EVOLUCION.json")
        require(provenance["state_sha256"] == before and all(provenance[k] == v for k, v in self.identity.items()),
                "El recibo de evolución no corresponde a los bytes recuperados")
        with self.legacy.zero_m2_audit() as attempts:
            new = self.read_state(state)
            t = int(new["time"])
            require(t == new["time"] and provenance["time"] == t and t in range(0, 161, 8),
                    "La recuperación exige una frontera programada")
            saved = self.pilot_pair(pilot, t)
            stream = self.stream(self.cfg, new)
            stream_coarse = self.stream(self.original[1], saved[1])
            rows = np.arange(int(t * 2.5 + 1)) * .4
            for grid in (*saved, new):
                require(all(np.isfinite(grid[k]).all() for k in ("q", "v", "rows", "consistent_rows"))
                        and np.array_equal(grid["rows"][:, 0], rows)
                        and np.array_equal(grid["consistent_rows"][:, 0], rows), "Observaciones inválidas")
            measures = (stream.original_sim.measure(t, stream.q, stream.v), stream.sim.measure(t, stream.q, stream.v))
            require(all(np.allclose(grid[-1], measurement, rtol=2e-12, atol=2e-12)
                        for grid, measurement in zip((new["rows"], new["consistent_rows"]), measures)),
                    "Las últimas medidas recuperadas no coinciden")
            require(stream.nfev >= stream.accepted and (t == 0) == (stream.accepted == 0)
                    and stream.solver is None, "Contadores físicos de frontera incoherentes")
            require(stream.sim.n == 7040, "Número de celdas distinto")
            from p4_backend import lap_chi
            lap = stream.sim.lap(stream.q)
            routing = bool(np.array_equal(lap[:2], stream.original_sim.lap(stream.q)[:2])
                           and np.array_equal(lap[2:3], lap_chi(stream.sim, stream.q[2:3])))
            S, _ = self.obs.symmetry_basis(stream.sim, stream.initial_q)
            sym = max(self.obs.symmetry_residual(stream.sim, S, x) for x in (stream.q, stream.v))
            coefficients = self.native.reference(stream.sim,
                (stream_coarse.sim, stream.sim, stream_coarse.q, stream.q))
            algebra_pass = all(coefficients[k] <= 2e-12 for k in (
                "mean_jacobian_identity_extended_relative_residual", "weighted_jacobian_symmetry_residual",
                "fused_passive_jacobian_relative_error", "production_force_absolute_scaled_residual"))
            preflight = {}
            if t == 0:
                for cfg, old in zip(self.original, saved):
                    replay = self.stream(cfg, old)
                    require(np.array_equal(replay.initial_q, old["q"]) and np.array_equal(replay.initial_v, old["v"]),
                            "Cauchy original no coincide con el piloto")
                rng = np.random.default_rng(20261002)
                errors = []
                for k in range(5):
                    q = stream.q if k == 0 else stream.q + rng.normal(size=stream.q.shape) * 1e-5
                    a, b = stream.numpy_force(q), stream.sim.force(q)
                    errors.append(float(np.max(abs(a-b)) / max(1., np.max(abs(a)))))
                preflight = dict(original_Cauchy_both_meshes_exact=True, force=stream.force_receipt,
                                 force_relative_errors=errors, transfer=stream.transfer, passed=max(errors) < 2e-12)
            with tempfile.TemporaryDirectory() as temporary:
                result = self.measurements(saved, new, published, t, Path(temporary)) if t else {}
        require(sha(state) == before, "La auditoría modificó la frontera")
        return dict(schema="CP12_P4_TERCERA_MALLA_CONTROL_V1", **self.identity, time=t,
                    state_sha256=before, audit_zero_step=True, M2_steps_executed=0,
                    DOP853_construction_or_step_attempts=len(attempts),
                    accepted_steps=stream.accepted, nfev=stream.nfev, preflight=preflight,
                    P4_routes_exact=routing, symmetry_relative_residual=sym, extended_identity=coefficients,
                    compared_to_pilot_asset=self.reg["pilot_frontiers"][str(t)]["asset_id"],
                    comparison=result, CP12_closed=False, correction_validated=False,
                    passed=bool(routing and sym <= 2e-12 and algebra_pass
                                and result.get("passed", True) and preflight.get("passed", True)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("origen", "tramo", "auditar"))
    parser.add_argument("--home", required=True, type=Path)
    parser.add_argument("--registro", required=True, type=Path)
    parser.add_argument("--carpeta", required=True, type=Path)
    parser.add_argument("--anterior", type=Path)
    parser.add_argument("--objetivo", type=int)
    parser.add_argument("--piloto", type=Path)
    parser.add_argument("--metricas", type=Path)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    with redirect_stdout(sys.stderr):
        trial = Trial(args.home, args.registro)
    if args.operation == "origen":
        trial.origin(args.carpeta)
    elif args.operation == "tramo":
        return trial.advance(args.anterior, args.objetivo, args.carpeta)
    else:
        result = trial.audit(args.carpeta, args.piloto, read(args.metricas))
        record(args.salida, result)
        print(json.dumps({"passed": result["passed"], "time": result["time"]}), flush=True)
        return 0 if result["passed"] else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
