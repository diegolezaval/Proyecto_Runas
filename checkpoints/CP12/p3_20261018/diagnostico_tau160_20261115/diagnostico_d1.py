"""D1: historia guardada, canales firmados y geometría espacial del defecto."""

import json

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator

BANDS = ((0, 2), (2, 5), (5, 10), (10, 20), (20, 40), (40, 220))
CUTS = ("2", "4", "8", "12", "20")
CHI_GATE = "final_mediator_phase_space_error_over_initial_norm"
METRIC_COLS = ("relative_error", "signed_projection", "cosine", "removal_squared_reduction")


def radial_weights(sim):
    return np.diff((np.arange(sim.n + 1) * sim.dx)**3) / 3


def distribution(q, v, sim, mass):
    # Misma cuadratura y normalización del comparador, antes de excluir r>=40.
    w = radial_weights(sim)
    pos = sim.ell > 0
    q_power = w[:, None] * q[:, pos]**2
    v_power = w[:, None] * (v[:, pos] / mass)**2 if v is not None else np.zeros_like(q_power)
    power = q_power + v_power
    ells = sim.ell[pos]
    core = sim.r < 40
    all_cells = sim.r < sim.radius
    total = power.sum()
    core_total = power[core].sum()

    def slice_values(selected):
        p = power[selected].sum()
        if p == 0:
            return {"squared_norm": 0.0, "velocity_fraction": None, "multipoles": {}}
        by_mode = {str(l): {"field_squared_norm": q_power[selected][:, ells == l].sum(),
                            "velocity_scaled_squared_norm": v_power[selected][:, ells == l].sum()}
                   for l in range(1, 5)}
        return {"squared_norm": p, "field_squared_norm": q_power[selected].sum(),
                "velocity_scaled_squared_norm": v_power[selected].sum(),
                "velocity_fraction": v_power[selected].sum() / p,
                "multipoles": {str(l): power[selected][:, ells == l].sum() / p for l in range(1, 5)},
                "field_and_velocity_squares_by_ell": by_mode,
                "radial_centroid": np.dot(sim.r[selected], power[selected].sum(axis=1)) / p}

    return {"core": slice_values(core), "full_box": slice_values(all_cells),
            "outer_edge_200_220": slice_values(sim.r >= 200),
            "bands": [dict(**slice_values(selected), r_min=lo, r_max=hi,
                           fraction_full=power[selected].sum() / total if total else None,
                           fraction_core=power[selected].sum() / core_total if hi <= 40 and core_total else None)
                      for lo, hi in BANDS if (selected := (sim.r >= lo) & (sim.r < hi)).any()]}


def gram(q, v, sim, mass, radial, angular):
    weight = np.sqrt(radial_weights(sim)[radial])[None, :, None]
    q, v = [a[:, radial, :][:, :, angular] for a in (q, v)]
    flat = np.concatenate(((q * weight).reshape(len(q), -1),
                           (v * weight / mass).reshape(len(v), -1)), axis=1)
    return flat @ flat.T


def channel_metrics(q, v, sim, mass, radial, angular, scale, names):
    g = gram(q, v, sim, mass, radial, angular)
    observed = g[0, 0]
    assert observed > 0 and scale > 0
    d = g.diagonal()
    individual = {}
    for j, name in enumerate(names[1:], 1):
        individual[name] = dict(relative_norm=np.sqrt(max(d[j], 0) / scale),
                                signed_projection=g[0, j] / observed,
                                cosine=g[0, j] / np.sqrt(observed * d[j]) if d[j] else None,
                                squared_reduction_if_removed=(2*g[0, j] - d[j]) / observed)
    r = names.index("raw:operador_chi")
    c = names.index("coupled:operador_chi")
    cross = 2 * (g[r, c] - d[r]) / observed
    change = max(0, d[r] + d[c] - 2*g[r, c])
    rows = {"raw": slice(1, 6), "coupled": slice(6, 11)}
    for family, sel in rows.items():
        summed = g[sel, sel].sum()
        individually = d[sel].sum()
        rows[family] = dict(
            sum_norm_over_initial=np.sqrt(summed / scale),
            total_pair_cross_over_residual_squared=(summed - individually) / observed,
            others_op_cross_over_residual_squared=2*(g[sel, r if family == "raw" else c].sum()
                                                     - d[r if family == "raw" else c]) / observed,
        )
    return dict(gram_scaled_by_initial=g / scale, gram_labels=names, all_channels=individual,
                families=rows, coupling_contrast=dict(
                    same_chi_forcing_norm_raw=np.sqrt(d[r] / scale),
                    same_chi_forcing_norm_coupled=np.sqrt(d[c] / scale),
                    coupled_minus_raw_norm=np.sqrt(change / scale),
                    coupled_minus_raw_signed_projection=(g[0, c]-g[0, r]) / observed,
                    twice_raw_dot_change_over_observed_squared=cross,
                    change_squared_over_observed_squared=change / observed),
                direct_residual_after_coupled_chi_removal=np.sqrt(
                    gram(q[[0]] - q[[c]], v[[0]] - v[[c]], sim, mass, radial, angular)[0, 0] / scale))


def interpolation_tests(qc, vc, qf, vf, initial_q, initial_v, sc, sf, mass, official, limit):
    def power(grid, q, v, inside):
        use = np.logical_and(grid.r >= inside[0], grid.r < inside[1])
        return np.sum(radial_weights(grid)[use, None]*(q[use, 1:]**2 + (v[use, 1:]/mass)**2))

    core = (0, 40)
    box = (0, 220)
    scale = power(sf, initial_q, initial_v, core)
    scale_box = power(sf, initial_q, initial_v, box)
    cubic = [CubicSpline(sc.r, a, axis=0)(sf.r) for a in (qc, vc)]
    parity = (-1.)**sc.ell
    even = [CubicSpline(np.r_[-sc.r[::-1], sc.r], np.concatenate([a[::-1]*parity, a]),
                        axis=0)(sf.r) for a in (qc, vc)]
    pchip = [PchipInterpolator(sc.r, a, axis=0)(sf.r) for a in (qc, vc)]
    estimates = {}
    for tag, (q, v) in (("original_cubic", cubic), ("origin_parity", even), ("pchip", pchip)):
        estimates[tag] = dict(core=np.sqrt(power(sf, q-qf, v-vf, core) / scale),
                              full_box=np.sqrt(power(sf, q-qf, v-vf, box) / scale_box))
    q, v, iq, iv = [CubicSpline(sf.r, a, axis=0)(sc.r) for a in (qf, vf, initial_q, initial_v)]
    estimates["reverse_cubic"] = dict(
        core=np.sqrt(power(sc, qc-q, vc-v, core)/power(sc, iq, iv, core)),
        full_box=np.sqrt(power(sc, qc-q, vc-v, box)/power(sc, iq, iv, box)))
    assert np.isclose(estimates["original_cubic"]["core"], official, rtol=2e-12, atol=2e-14)
    for tag, value in estimates.items():
        value["core_at_or_below_two_percent"] = value["core"] <= limit
        value["used_for_acceptance"] = tag == "original_cubic"
    return estimates, scale, (cubic[0]-qf, cubic[1]-vf)


def commutators(qc, sc, sf, obs, lap_chi):
    """Cambio algebraico de fuente. Las fuerzas no son respuestas integradas."""
    def transfer(a):
        return CubicSpline(sc.r, a, axis=-2)(sf.r)

    qi = transfer(qc)
    base = transfer(lap_chi(sc, qc[2:3]))[0] - lap_chi(sf, qi[2:3])[0]
    nonlinear = transfer(obs.nonlinear(sc, qc @ sc.Y))[2] - obs.nonlinear(sf, qi @ sf.Y)[2]

    def perturbation(sim, q):
        field = q.copy()
        for _ in range(4):
            field = sim.lap2(field)
        return -(sim.dx**6/560) * field

    delta = transfer(perturbation(sc, qc[2:3]))[0] - perturbation(sf, qi[2:3])[0]
    change = {}
    for tag, rad in (("core", sf.r < 40), ("middle_10_20", (sf.r >= 10) & (sf.r < 20)),
                     ("shell_20_40", (sf.r >= 20) & (sf.r < 40)), ("exterior", sf.r >= 40)):
        change[tag] = {}
        for ell in (2, 4):
            a, b = base[rad][:, sf.ell == ell], delta[rad][:, sf.ell == ell]
            w = radial_weights(sf)[rad, None]
            a2, b2, dot = np.sum(w*a*a), np.sum(w*b*b), np.sum(w*a*b)
            change[tag][str(ell)] = dict(base_norm=np.sqrt(a2), added_norm=np.sqrt(b2),
                                        signed_projection=dot/a2 if a2 else None,
                                        cosine=dot/np.sqrt(a2*b2) if a2 and b2 else None,
                                        norm_ratio_after=np.sqrt(np.sum(w*(a+b)**2)/a2) if a2 else None)
    return dict(P3_operator=distribution(base, None, sf, obs.model.mediator),
                nonlinear_transfer=distribution(nonlinear, None, sf, obs.model.mediator),
                P4_algebraic_increment=distribution(delta, None, sf, obs.model.mediator),
                signed_P4_increment=change)


def snapshot(t, z, sims, obs, lap_chi, official, limit):
    sc, sf = sims
    n, mass = sc.n, obs.model.mediator
    assert n == int(z["coarse_n"]) and sf.n + n == z["q"].shape[1]
    qc, qf, vc, vf = z["q"][:, :n], z["q"][:, n:], z["v"][:, :n], z["v"][:, n:]
    estimates, scale, (dq, dv) = interpolation_tests(
        qc[2], vc[2], qf[2], vf[2], z["initial_q"][2, n:], z["initial_v"][2, n:],
        sc, sf, mass, official[CHI_GATE], limit)
    basis = z["coupled_angular_basis"]
    raw_q, raw_v = [z[f"raw_0_{field}"][:, 0] for field in ("q", "v")]
    cq, cv = [z[f"coupled_0_{field}"] @ basis.T for field in ("q", "v")]
    ci, ri = obs.COUPLED.index("operador_chi"), obs.BARE.index("operador_chi")
    src = dict(observed=(dq, dv), raw_chi=(raw_q[ri], raw_v[ri]), coupled_chi=(cq[ci, 2], cv[ci, 2]))
    dists = {label: distribution(q, v, sf, mass) for label, (q, v) in src.items()}
    actual = dists["observed"]
    assert np.isclose(np.sqrt(actual["core"]["squared_norm"] / scale), official[CHI_GATE],
                      rtol=2e-12, atol=2e-14)
    assert np.allclose([b["fraction_core"] for b in actual["bands"][:-1]],
                       [b["fraction_of_chi_squared_difference"] for b in official["chi_radial_bands"]],
                       rtol=2e-12, atol=2e-15)
    assert np.allclose(list(actual["core"]["multipoles"].values()),
                       list(official["chi_multipole_fractions"].values()), rtol=2e-12, atol=2e-15)
    names = ["observed"] + [f"raw:{x}" for x in obs.BARE] + [f"coupled:{x}" for x in obs.COUPLED]
    gq, gv = [np.concatenate((a[None], b, c[:, 2])) for a, b, c in
              [(dq, raw_q, cq), (dv, raw_v, cv)]]
    scopes = {"core": sf.r < 40, "full_box": sf.r < sf.radius}
    grams = {k: channel_metrics(gq, gv, sf, mass, use, sf.ell > 0, scale, names)
             for k, use in scopes.items()}
    phiq, phiv = cq[ci, :2], cv[ci, :2]
    phi_response = np.sqrt(np.sum(radial_weights(sf)[None, :, None] *
                                  (phiq**2 + phiv**2/obs.model.mass2)))
    return dict(time=t, initial_core_squared_scale=scale, interpolation=estimates,
                distributions=dists, gram=grams, chi_operator_induced_phi_full_box_norm=phi_response,
                instantaneous=commutators(qc, sc, sf, obs, lap_chi)), dict(
                    coarse=(qc[2], vc[2]), fine=(qf[2], vf[2]),
                    observed=src["observed"], coupled_chi=src["coupled_chi"])


def history(z, bare, coupled, limit, published):
    rows = json.loads(str(z["budget_rows"]))
    assert len(rows) == 401
    t = np.asarray([row["time"] for row in rows])
    assert np.allclose(t, z["rows"][:, 0], rtol=0, atol=1e-12)
    errors = np.asarray([row["observed_relative_error"] for row in rows])
    assert all(np.isclose(errors[round(clock/.4)], values[CHI_GATE], rtol=2e-12, atol=2e-14)
               for clock, values in published.items())
    records = []
    for row in rows:
        window = row["short_modes"]
        records.append([
            row["time"], row["observed_relative_error"],
            [[channel[key] for key in METRIC_COLS] for channel in row["raw"]],
            [[channel[key] for key in METRIC_COLS] for channel in row["coupled"]],
            [window["core"]["observed_error_fraction_above_k"][key] for key in CUTS],
            [window["smooth"]["observed_error_fraction_above_k"][key] for key in CUTS],
            row["verification"]["raw_closure"], row["verification"]["coupled_closure"],
        ])
    hits = np.flatnonzero(errors > limit)
    k = int(hits[0]) if len(hits) else 0
    summary = dict(
        first_saved_observation_over_limit=[t[k], errors[k]] if len(hits) else None,
        previous_saved_observation=[t[k-1], errors[k-1]] if k > 0 else None,
        observations_over_limit=len(hits), observations=len(rows),
        max_observed_with_clock=[t[int(errors.argmax())], errors.max()],
        scope="Tiempos guardados cada 0,4. Las puertas oficiales se evalúan en múltiplos de ocho.",
    )
    return dict(columns=["time", "observed_chi_phase", "raw", "coupled", "core_fraction_above_k",
                         "smooth_fraction_above_k", "raw_closure", "coupled_closure"],
                channel_columns=METRIC_COLS, raw_order=bare, coupled_order=coupled,
                modal_cuts=CUTS, modal_basis="base FV original del observador, no base A2 de D2",
                rows=records), summary


def seed_regularity(source, eps):
    """Contraste histórico D1 sobre el mismo CP04, evaluando sólo sus splines."""
    report = {}
    with np.load(source, allow_pickle=False) as data:
        config = json.loads(str(data["config"]))
        r = (np.arange(config["n"]) + .5)*config["dx"]
        for name in ("chi", "vchi"):
            f = data[name]
            spline = CubicSpline(np.r_[-r[::-1], r], np.r_[f[::-1], f])
            knots = spline.x[1:-1]
            use = (knots > 0) & (knots < 40)
            x = knots[use]
            third_jump = 6*np.diff(spline.c[0])[use]
            second_quad_jump = -eps*x*np.exp(-(x/20)**4)*third_jump
            report[name] = {
                "largest_seed_quadrupolar_second_derivative_jump": np.max(abs(second_quad_jump)),
                "radius_of_largest_jump": x[np.argmax(abs(second_quad_jump))],
                "max_background_third_derivative_jump": np.max(abs(third_jump)),
            }
    return report


def angular_source_leakage(z, sims, harmonics, model):
    """Fuente instantánea sobre campos L4, reconstruida con cuadratura L12."""
    basis, values, weights = harmonics(12)
    ell = np.array([key[0] for key in basis])
    projection = (values*weights).T
    report = []
    for time, states in [(0, z["initial_q"]), (160, z["q"])]:
        for sim, q in zip(sims, np.split(states, [sims[0].n], axis=1)):
            use = sim.r < 40
            a, b, mediator = q[:, use] @ values[:sim.nm]
            rho = a*a+b*b
            factor = 2*model.quartic*rho+model.trilinear*mediator+.5*model.mixed*mediator**2
            nonlinear = np.array([-factor*a, -factor*b, -(model.trilinear+model.mixed*mediator)*rho])
            coeff = nonlinear @ projection
            power = np.sum(radial_weights(sim)[None, use, None]*coeff**2, axis=1)
            report.append(dict(time=time, h=sim.dx,
                               leakage_fraction_of_squared_nonlinear_force=power[:, ell > 4].sum(axis=1)/power.sum(axis=1)))
    return report
