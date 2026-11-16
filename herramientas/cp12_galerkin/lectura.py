"""Lectura de P4 conservado y presupuesto de incertidumbre de Galerkin."""
import ast
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile

import numpy as np
from scipy.interpolate import CubicSpline

from cp12_reanudacion.campana_hospedada import download
from cp12_reanudacion.infra import asset_url, digest, encoded, module, now, require, sha
from cp12_reanudacion.p4_tercera_fisica import METRICS, PHASE
from cp12_reanudacion.p4_tercera_hospedada import unzip, verify_payload
from trayectoria import archive_record, case_binding, model_at, read_state


def comparer(ctx, t, alternative=False, degrees=None):
    path = ctx.sources_dir / "diagnosticar_mediador_CP10.py"
    original = module(path, "comparador_original_cp10")
    if t == 160 and not alternative:
        return original.compare
    node = next(x for x in ast.parse(path.read_text()).body if isinstance(x, ast.FunctionDef) and x.name == "compare")
    guard = ast.parse("if c['time'] != 160 or f['time'] != 160:\n    raise ValueError('Tiempo final incorrecto')").body[0]
    require(ast.dump(node.body[1]) == ast.dump(guard), "Guarda original distinta")
    if t != 160:
        for value in ast.walk(node.body[1].test):
            if isinstance(value, ast.Constant) and value.value == 160:
                value.value = t
    scope = dict(vars(original))
    if alternative:
        power = degrees[None, None, :]

        def regular(r, data, axis):
            require(axis == 1, "Eje distinto en la interpolación")
            values = data / r[None, :, None]**power
            spline = CubicSpline(np.r_[-r[::-1], r], np.concatenate((values[:, ::-1], values), axis=1), axis=1)
            return lambda fresh: spline(fresh) * fresh[None, :, None]**power

        scope["CubicSpline"] = regular
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 "<lector_CP10_de_fronteras_con_tiempos_reales>", "exec"), scope)
    return scope["compare"]


def as_npz(dir, name, inputs):
    path = dir / (name + ".npz")
    np.savez(path, **inputs)
    return path


def pilot_pair(ctx, t, room, p4):
    spec = p4["pilot_frontiers"][str(t)]
    rd = ctx.git.get(ctx.reg["source_commit"], spec["receipt"])
    require(digest(rd) == spec["receipt_sha256"], "Recibo original del piloto distinto")
    receipt = json.loads(rd)
    check = receipt["recovery"]["original_audits"]["boundary"]
    require(receipt["passed"] and receipt["observer_clock"] == t and check["time"] == t
            and check["execution_uuid"] == ctx.reg["source_original_pilot_uuid"]
            and check["run_id"] == ctx.reg["source_original_pilot_run"]
            and receipt["M2_steps_executed"] == check["M2_steps_executed"] == 0
            and receipt["github_asset_id"] == spec["asset_id"]
            and receipt["bytes"] == spec["bytes"] and receipt["sha256"] == spec["archive_sha256"]
            and receipt["browser_download_url"] == asset_url(receipt["file_name"]) == spec["asset_url"],
            "La pareja P4 guardada no coincide con la evidencia")
    archive = archive_record(receipt, room)
    with zipfile.ZipFile(archive) as zip:
        data, prov = zip.read("outputs/MIXTO_par_estado.npz"), zip.read("outputs/procedencia.json")
    require(digest(data) == spec["state_sha256"] and digest(prov) == spec["run_receipt_sha256"],
            "La pareja P4 contiene otro estado")
    with np.load(io.BytesIO(data), allow_pickle=False) as pair:
        require(float(pair["time"]) == t and str(pair["experiment_id"]) == p4["pilot_run_id"], "Reloj P4 distinto")
        n = int(pair["coarse_n"])
        config = json.loads(str(pair["config"]))["physical_configurations"]
        rows = pair["rows"]
        fields = {key: pair[key] for key in ("q", "v", "initial_q", "initial_v")}
        require(n == 1760 and fields["q"].shape == (3, 5280, 25), "Dimensiones del piloto distintas")
    from continuar_no_radial_m2 import harmonics
    labels = np.asarray(harmonics(4)[0], dtype=str)
    return [as_npz(room, f"P4_{i}", dict(**{k: f[:, selection] for k, f in fields.items()},
             time=t, labels=labels, rows=np.column_stack([rows[:, 0], rows[:, cols]]),
             config=json.dumps(config[i])))
            for i, (selection, cols) in enumerate(((slice(0, n), slice(1, 10)), (slice(n, None), slice(10, None))))], receipt


def third_mesh(ctx, t, room):
    p = f"{ctx.refs}/tau{t:04d}/RECUPERACION_PUBLICA.json"
    receipt = ctx.json(p, base=ctx.reg["source_commit"])
    identity = dict(execution_uuid=ctx.reg["source_third_mesh_uuid"], execution_run_id=ctx.reg["source_third_mesh_run"])
    require(all(receipt[k] == v for k, v in identity.items()) and receipt["passed"] and receipt["time"] == t
            and receipt["M2_steps_executed"] == 0 and receipt["independently_downloaded_without_authentication"],
            "La tercera malla no tiene recuperación positiva en el reloj registrado")
    if t == 160:
        pinned = ctx.reg["source_terminal"]
        require(receipt["github_asset_id"] == pinned["asset"] and receipt["sha256"] == pinned["sha256"]
                and receipt["bytes"] == pinned["bytes"] and receipt["state_sha256"] == pinned["state_sha256"],
                "El origen final P4 difiere del registrado")
    asset = dict(receipt, file_name=receipt["browser_download_url"].rsplit("/", 1)[-1])
    archive = archive_record(asset, room)
    folder = room / "P4_fina"
    unzip(archive, folder)
    verify_payload(folder, identity)
    file = folder / "ESTADO.npz"
    require(sha(file) == receipt["state_sha256"], "Estado P4 .03125 distinto")
    with np.load(file, allow_pickle=False) as trial:
        require(float(trial["time"]) == t and json.loads(str(trial["config"]))["dx"] == .03125,
                "La tercera malla está en otro tiempo o resolución")
    return file, receipt


def reference_case(ctx, case, t, room, model_cache):
    receipt = ctx.json(f"{ctx.root}/casos/{case}/tau{t:04d}/RECUPERACION_PUBLICA.json")
    identity = case_binding(ctx, case)
    require(receipt["passed"] and all(receipt[k] == v for k, v in identity.items())
            and receipt["time"] == t and receipt["M2_steps_executed"] == 0
            and receipt["independently_downloaded_without_authentication"] and receipt["recovery"]["passed"],
            "Todavía no hay cierre acreditado del brazo " + case)
    archive = archive_record(receipt, room)
    extracted = room / case
    unzip(archive, extracted)
    verify_payload(extracted, identity)
    path = extracted / "ESTADO.npz"
    require(sha(path) == receipt["state_sha256"], "NPZ de referencia distinto")
    saved = read_state(path, identity)
    if case not in model_cache:
        model_cache[case] = model_at(ctx, case, saved["basis"])
    model = model_cache[case]
    require(saved["time"] == t and np.array_equal(saved["basis"], model.angular.projector),
            "Reloj o base angular cambiaron en la serie")
    h = ctx.reg["configuration"]["comparison_reticle_h"]
    r = (np.arange(round(220/h)) + .5) * h
    fields = {a: model.fields(saved[b], r) for a, b in
              (("q", "u"), ("v", "v"), ("initial_q", "initial_u"), ("initial_v", "initial_v"))}
    return dict(**fields, time=t, labels=model.angular.labels, rows=saved["rows"],
                config=json.dumps({"dx": h, "radius": 220, "L": 4})), receipt


def audit_comparison_inputs(pair, original):
    for i, metrics in enumerate(pair):
        for key in METRICS:
            require(np.isclose(metrics[key], original[i][key], rtol=1e-11, atol=1e-13),
                    "La lectura de P4 guardado no reproduce sus métricas en " + key)


def evaluate(ctx, t, room, p4, published, model_cache):
    compare = comparer(ctx, t)
    pair, pair_input = pilot_pair(ctx, t, room, p4)
    fine, fine_input = third_mesh(ctx, t, room)
    pilot = [*pair, fine]
    archived_pairs = [compare(left, right) for left, right in zip(pilot, pilot[1:])]
    audit_comparison_inputs(archived_pairs, (published["pilot"], published["refined"]))
    raw, ref_sources = {}, {}
    for name in ctx.reg["cases"]:
        raw[name], rc = reference_case(ctx, name, t, room, model_cache)
        ref_sources[name] = {k: rc[k] for k in ("github_asset_id", "sha256", "state_sha256")}
    expected = np.arange(round(t / .4) + 1) * .4
    require(all(np.array_equal(r["rows"][:, 0], expected) for r in raw.values()), "Tiempos de comparación distintos")
    reference = raw["R2"]
    refs = {name: as_npz(room, name, dict(data, initial_q=reference["initial_q"], initial_v=reference["initial_v"]))
            for name, data in raw.items()}
    adj = compare(refs["R0"], refs["R1"])
    # Expresar todo el presupuesto con la misma norma inicial y el mismo
    # normalizador de la historia que usa el comparador contra R2.
    adj[METRICS[0]] *= float(raw["R1"]["rows"][:, 5].max() / reference["rows"][:, 5].max())
    fine_radial = compare(refs["R1"], refs["R2"])
    dt = compare(refs["T"], refs["R2"])
    eps = compare(refs["EPS"], refs["R2"])
    rules = ctx.reg["reference_limits"]
    u = {key: fine_radial[key] + dt[key] + eps[key] for key in METRICS}
    decays = {key: fine_radial[key] < adj[key] or
              max(fine_radial[key], adj[key]) <= rules["comparison_roundoff_floor"] for key in METRICS}
    alt = comparer(ctx, t, True, reference["labels"][:, 0].astype(int))
    acceptance = ctx.reg["physical_limits"]["field_and_phase_space_relative_error_max"]
    measurements = {}
    for address, grid in zip(("0.125", "0.0625", "0.03125"), pilot):
        official = compare(grid, refs["R2"])
        alternative = alt(grid, refs["R2"])
        sensitivity = {key: abs(official[key]-alternative[key]) for key in METRICS}
        margins = {}
        for key in METRICS:
            d, i, variation = official[key], sensitivity[key], u[key]
            reliable = bool(decays[key] and variation <= rules["absolute_variation_max"]
                            and variation < rules["relative_discrepancy_fraction_strict"] * d)
            margins[key] = dict(official_error=d, alternate_error=alternative[key], interpolation_sensitivity=i,
                                reference_variation=variation, quantitative=reliable,
                                reference_at_discrepancy_scale=d <= variation,
                                joint_upper_empirical=d+variation+i, nominal_pass=d <= acceptance,
                                margin_robust_to_variations=acceptance-d-variation-i)
        measurements[address] = dict(official=official, alternative=alternative, decisions=margins,
                                    all_five_nominal=all(r["nominal_pass"] for r in margins.values()),
                                    all_five_robust_margins=all(r["margin_robust_to_variations"] >= 0 for r in margins.values()))
    return dict(schema="CP12_P4_REFERENCIA_GALERKIN_COMPARACION_V1", time=t,
                campaign_uuid=ctx.reg["campaign_uuid"], registered_hash=ctx.reg_hash, hosted=ctx.hosted,
                original_comparator_sha256=ctx.reg["source_comparator_sha256"], chi_rotation_used=False,
                thresholds=rules, M2_steps_executed=0,
                P4_archived_pairs_verified=True,
                P4_assets=[{k: x[k] for k in ("github_asset_id", "sha256", "bytes")} for x in (pair_input, fine_input)],
                Galerkin_assets=ref_sources, radial_change_01={k: adj[k] for k in METRICS},
                radial_change_12={k: fine_radial[k] for k in METRICS}, radial_decreasing=decays,
                time_step_change={k: dt[k] for k in METRICS}, stage_tolerance_change={k: eps[k] for k in METRICS},
                empirical_reference_variation=u, comparison=measurements, CP12_closed=False)


def final_report(ctx, result):
    data = result["comparisons"]
    rows = []
    for point in data[-6:]:
        part = point["comparison"]
        values = [part[name]["decisions"][PHASE]["official_error"] for name in ("0.125", "0.0625", "0.03125")]
        fine = part["0.03125"]["decisions"][PHASE]
        rows.append("| " + " | ".join([str(point["time"]), *(f"{d*100:.6f} %" for d in values),
                                      f"{fine['reference_variation']*100:.6f} %",
                                      f"{fine['interpolation_sensitivity']*100:.6f} %",
                                      f"{fine['joint_upper_empirical']*100:.6f} %",
                                      "Sí" if fine["quantitative"] else "Cota conjunta"]) + " |")
    r = data[-1]
    fine = r["comparison"]["0.03125"]["decisions"][PHASE]
    nominal = "Las cinco métricas oficiales de las tres mallas quedaron dentro del 2 % en todos los cierres." if result["all_nominal"] else \
        "La puerta oficial del 2 % falló en al menos una malla, corte o métrica. El resultado JSON conserva la evidencia."
    robust = "Todos los márgenes al 2 % siguen siendo positivos al incluir la variación observada de referencia y la sensibilidad a interpolación." if result["all_robust_margins"] else \
        "Al menos un margen al 2 % depende de la variación observada de referencia o de la interpolación."
    verdict = (f"En τ160, la discrepancia más fina de χ en espacio de fases admite interpretación cuantitativa "
               f"de {fine['official_error']*100:.6f} % con variación de referencia {fine['reference_variation']*100:.6f} %."
               if fine["quantitative"] else
               f"En τ160, para χ en espacio de fases de la malla más fina se informa la cota empírica conjunta "
               f"{fine['joint_upper_empirical']*100:.6f} %. La lectura oficial fue {fine['official_error']*100:.6f} %.")
    return "\n".join([
        "# CP12/P4 · Contraste Galerkin hasta τ160", "",
        nominal, robust, verdict, "",
        "La comparación cubre la semilla CP04 registrada, R=220, L=4 y el horizonte τ160. "
        "Las variaciones son observadas entre discretizaciones y se publican por métrica en cada corte.",
        "",
        "| τ | χ fase P4 .125 | χ fase P4 .0625 | χ fase P4 .03125 | U referencia | Sensibilidad de interpolación h=.03125 | Cota conjunta h=.03125 | Precisión h=.03125 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |", *rows, "",
        "Siguen pendientes los contrastes de estabilidad temporal de P4, caja, truncamiento angular y amplitud inicial antes de decidir el cierre de CP12.", "",
        "[Resultados y presupuestos](RESULTADO.json) · [Controles previos](CONTROL_PREVIO.json) · "
        "[Prerregistro](PRERREGISTRO.md) · [Plan de estabilidad y robustez](../tercera_malla_20261116/SIGUIENTE_CONTRASTE.md)", ""
    ])


def analyze(ctx, until):
    ctx.sources()
    pre = ctx.json(ctx.root + "/CONTROL_PREVIO.json", base=ctx.activation["preflight_commit"])
    require(pre["passed"] and pre["registration_sha256"] == ctx.reg_hash, "Controles de otra referencia")
    p4 = ctx.json(ctx.refs + "/REGISTRO.json", base=ctx.reg["source_commit"])
    original = ctx.json(ctx.refs + "/RESULTADO.json", base=ctx.reg["source_commit"])
    expected = {x["time"]:x for x in original["time_series"]}
    data, models = [], {}
    for t in range(8, until+1, 8):
        path = f"{ctx.root}/comparaciones/TAU{t:04d}.json"
        previous = ctx.json(path, missing=True)
        if previous is None:
            with TemporaryDirectory(dir=ctx.scratch) as room:
                previous = evaluate(ctx, t, Path(room), p4, expected[t], models)
            ctx.publish({path: encoded(previous)}, f"CP12/P4 Galerkin: publicar comparación en τ{t}")
        require(previous["time"] == t and previous["registered_hash"] == ctx.reg_hash, "Lectura de otra campaña")
        data.append(previous)
    state = ctx.json(ctx.root + "/ESTADO.json")
    state.update(comparaciones_publicadas=len(data), ultimo_tau_comparado=until, updated_at=now(),
                 status="COMPLETADA_TAU160" if until == 160 else "COMPARACIONES_PARCIALES")
    paths = {ctx.root + "/ESTADO.json": encoded(state)}
    if until == 160:
        result = dict(schema="CP12_P4_REFERENCIA_GALERKIN_RESULTADO_V1", campaign_uuid=ctx.reg["campaign_uuid"],
                      source_commit=ctx.reg["source_commit"], registration_sha256=ctx.reg_hash, comparisons=data,
                      all_nominal=all(p["all_five_nominal"] for d in data for p in d["comparison"].values()),
                      all_robust_margins=all(p["all_five_robust_margins"] for d in data for p in d["comparison"].values()),
                      reference_absolute_precision=all(max(r["empirical_reference_variation"].values()) <= .0025 for r in data),
                      P4_stability_and_robustness_pending=True, CP12_closed=False, correction_validated=False)
        state.update(result=ctx.root + "/RESULTADO.json", report=ctx.root + "/INFORME.md")
        paths.update({ctx.root + "/RESULTADO.json":encoded(result), ctx.root + "/INFORME.md": final_report(ctx, result).encode(),
                      ctx.root + "/ESTADO.json": encoded(state)})
    ctx.publish(paths, f"CP12/P4 Galerkin: constatar la lectura hasta τ{until}")
    print(json.dumps(dict(comparisons=len(data), time=until)), flush=True)
    return 0
