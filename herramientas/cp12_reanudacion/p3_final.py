"""Leer la frontera original de τ160 y las tres ventanas causales con cero M2."""

from pathlib import Path

from .infra import CANDIDATE, module, record, require, sha


WINDOWS = {"core_phase": None, "short_core_k4": "core", "short_smooth_k4": "smooth"}


def review(home, spec, audit, output):
    state, receipt = home / "outputs/MIXTO_par_estado.npz", home / "outputs/procedencia.json"
    expected = audit["state_sha256"], audit["receipt_sha256"]
    require(spec["observer_clock"] == audit["time"] == 160 and expected == (sha(state), sha(receipt)),
            "La lectura final requiere la frontera exacta τ160")
    coordinator = module(home / "coordinator.py", "_cp12_final_original")
    # El resultado se conserva junto a la cápsula pública por el supervisor.
    coordinator.preserve_negative = lambda *a, **k: None
    coordinator.event = lambda *a, **k: None
    with coordinator.zero_m2_audit() as attempts:
        original = coordinator.final_review(home)
        modules, streams, budget = coordinator.streams_and_budget(home)
        causal = analyze(home, coordinator, modules, streams, budget, audit)
        require(not attempts and expected == (sha(state), sha(receipt)), "La lectura final alteró la frontera")
    require(len(original["original_physical_gates"]) == 15, "Puertas finales originales incompletas")
    gates = original["original_physical_gates"]
    spatial = {key: gate for key, gate in gates.items() if not key[0].isdigit()}
    physical = {key: gate for key, gate in gates.items() if key[0].isdigit()}
    result = dict(
        schema=f"CP12_{CANDIDATE}_LECTURA_FINAL_PROTOCOLO_V1", time=160, source_state_sha256=sha(state),
        source_receipt_sha256=sha(receipt), comparison=original["comparison"],
        prefix_pair_gates=spatial, prefix_physical_controls=physical,
        prefix_pair_limits_met=all(spatial.values()), prefix_physical_controls_met=all(physical.values()),
        M2_steps_executed=0, physical_state_and_receipt_unchanged=True, CP12_closed=False,
        correction_validated=False,
        final_protocol=dict(
            schema=f"CP12_{CANDIDATE}_VALIDACION_FINAL_V1", time=160,
            passed=original["two_original_grid_gates_passed"] and causal["passed"],
            spatial=spatial, physical=physical, causal=causal, M2_steps_executed=0,
            source_capsule_sha256=spec["sha256"], source_state_sha256=sha(state),
            additional_reference_stability_robustness_pending=True, CP12_closed=False,
            correction_validated=False,
        ),
    )
    certificate = dict(
        schema=f"CP12_{CANDIDATE}_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED", passed=True, time=160,
        all_payload_hashes_verified=True, independent_extracted_audit=audit, state_sha256=audit["state_sha256"],
        configuration_sha256=audit["configuration_sha256"], receipt_sha256=audit["receipt_sha256"],
    )
    record(output / "CERTIFICADO_FRONTERA.json", certificate)
    return result


def analyze(home, coordinator, modules, streams, budget, audit):
    np, obs = modules["np"], modules["obs"]
    series = budget.rows
    require(len(series) == 401 and series[0]["time"] == 0 and series[-1]["time"] == 160,
            "La serie causal no cubre el intervalo registrado")
    reference = coordinator.read(home / "preregistration/RESULTADO_CAUSAL_ORIGINAL.json")
    require(reference["time"] == 160 and reference["reproduces_CP10_exactly"] and reference["observer_checks_passed"],
            "La referencia causal original no está acreditada")
    source = home / "science/herramientas/interpretar_presupuesto_CP12.py"
    if not source.exists():
        source = Path(__file__).resolve().parents[1] / source.name
    original = coordinator.load_module("_cp12_causal_original", source)
    criteria = reference["criteria"]
    q0, v0 = streams[0].q, streams[0].v
    q1, v1 = streams[1].q, streams[1].v
    dq = obs.interpolate(budget.sc, q0, budget.sf)[2] - q1[2]
    dv = obs.interpolate(budget.sc, v0, budget.sf)[2] - v1[2]
    rawq, rawv = budget.family_arrays("raw", 0)
    coupledq, coupledv = budget.family_arrays("coupled", 0)
    q = np.concatenate([dq[None], rawq[:, 0], coupledq[:, 2]])
    v = np.concatenate([dv[None], rawv[:, 0], coupledv[:, 2]])
    core = np.array([[obs.chi_inner(budget.sf, a, b, c, d) for c, d in zip(q, v)] for a, b in zip(q, v)])
    final = series[-1]
    times = [row["time"] for row in series]
    windows = {}
    for label, short in WINDOWS.items():
        gram = core if short is None else np.array(final["short_modes"][short]["short_response_gram_matrix"])
        observed = final["observed_relative_error"] if short is None else final["short_modes"][short]["short_relative_error"]
        threshold = criteria["onset_final_observed_norm_fraction"] * observed
        groups, terms, crossings = {}, {}, {}
        for family, names, offset in (("raw", obs.BARE, 1), ("coupled", obs.COUPLED, 6)):
            names_to_indices = {name: [i] for i, name in enumerate(names)} | original.GROUPS[family]
            groups[family] = {name: original.metrics(gram, [offset + i for i in indices], budget.scale)
                              for name, indices in names_to_indices.items()}
            terms[family] = gram[offset:offset + 5, offset:offset + 5].tolist()
            for index, name in enumerate(names):
                if short is None:
                    norms = [row[family][index]["relative_error"] for row in series]
                else:
                    norms = [next(item["relative_error"] for item in row["short_modes"][short]["metrics"]
                                  if item["family"] == family and item["name"] == name) for row in series]
                crossings[f"{family}:{name}"] = original.onset(norms, times, threshold, criteria["onset_consecutive_samples"])
        old_norm = reference["tables"]["coupled"][label]["operador_chi"]["relative_error"]
        new_norm = groups["coupled"]["operador_chi"]["relative_error"]
        require(old_norm > 0 and np.isfinite(old_norm) and np.isfinite(new_norm), "Norma causal indefinida")
        reduction = 1 - new_norm / old_norm
        windows[label] = dict(
            original_chi_operator_norm=old_norm, **{f"{CANDIDATE}_chi_operator_norm": new_norm},
            reduction=reduction, passed=bool(reduction >= 0.5), signed_channel_metrics=groups,
            cross_terms=terms, sustained_crossings=crossings, onset_threshold=threshold,
        )
    return dict(
        passed=all(result["passed"] for result in windows.values()), windows=windows,
        minimum_required_reduction=0.5, shared_initial_chi_scale=budget.scale,
        full_box_chi_closure=audit["full_box_chi_closure"], observer_maximum_errors=audit["maximum_errors"],
        scope="Atribución causal condicionada a las historias de las dos mallas originales.",
    )
