"""Controles registrados, ejecutados antes de activar la producción."""
from time import perf_counter

import numpy as np

from fisica import Gauss8, M2, identities, manufactured, original_seed_check, tableau
from fisica import use_compensated_controls


def gates(values):
    return bool(all(values.values()))


def projection_error(m2, u, v):
    mesh = m2.mesh
    r = (np.arange(1280) + .5) / 32
    q0, v0 = m2.seed.sample(r)
    q, velocity = m2.fields(u, r), m2.fields(v, r)
    chi = m2.model.mediator
    scale = q0[2, :, 1:]**2 + (v0[2, :, 1:]/chi)**2
    diff = (q[2, :, 1:] - q0[2, :, 1:])**2 + ((velocity[2, :, 1:] - v0[2, :, 1:])/chi)**2
    w = np.diff((np.arange(1281) / 32)**3)[:, None] / 3
    return float(np.sqrt(np.sum(w * diff) / np.sum(w * scale)))


def run_controls(reg, source, build):
    A, b, c = tableau()
    B = np.diag(b)
    settings = reg["preflight"]
    tol = settings["symmetry_identity_max"]
    controls = dict(gauss_moments=bool(max(abs(b @ c**j - 1/(j+1)) for j in range(8)) <= tol),
                    gauss_symplectic=bool(np.max(abs(B @ A + A.T @ B - np.outer(b, b))) <= tol),
                    gauss_row_times=bool(np.max(abs(A.sum(axis=1)-c)) <= tol))
    cache = {}
    tested = {}
    manufactured_reports, invariants, projections = {}, {}, {}
    for case in ("R0", "R1", "R2"):
        m2 = M2(reg["cases"][case], source, build)
        u, v = m2.initialize()
        cache[case] = (m2, u, v)
        manufactured_reports[case] = {str(k): manufactured(m2.mesh, k, 3.)
                                      for k in settings["manufactured_waves"]}
        invariants[case] = identities(m2, u, v)
        projections[case] = projection_error(m2, u, v)
    seed = original_seed_check(cache["R2"][0], source)
    keys = ("angular_force_residual", "potential_residual", "angular_closure_residual",
            "energy_identity", "charge_identity")
    controls["identities"] = all(max(r[x] for x in keys) <= tol for r in invariants.values())
    controls["initial_values_CP04"] = all(max(r["field_max"], r["velocity_max"]) <= settings["cauchy_max_abs"]
                                          and r["origin_hash"] == reg["source_Cauchy"]["sha256"] for r in seed.values())
    controls["profiles_finite_and_Dirichlet"] = all(item["finite"] and abs(item["boundary_value"]) <= tol
        for case in manufactured_reports.values() for family in case.values() for item in family.values())
    radial = {}
    for k in ("0", "8"):
        for ell in ("0", "2", "4"):
            measured = [manufactured_reports[case][k][ell]["operator"] for case in ("R0", "R1", "R2")]
            radial[k + "_" + ell] = measured[-1] <= settings["operator_smooth_max" if k == "0" else "operator_band_k8_max"] and (
                measured[2] < measured[1] < measured[0] or max(measured) <= 1e-10)
    controls["manufactured_fine_and_refining"] = gates(radial)
    total_steps = 0
    if gates(controls):
        for name, case in reg["cases"].items():
            model, u, v = cache[name if name in cache else "R2"]
            stepper = Gauss8(model, case)
            initial = model.measure(0., u, v)
            balance = dict(energy=0., charge=0.)
            count = round(settings["tau_short"] / stepper.dt)
            started = perf_counter()
            for _ in range(count):
                u, v = stepper.step(u, v)
                e, q = model.energies(u, v)
                balance["energy"] = max(balance["energy"], float(abs(e/initial[1]-1)))
                balance["charge"] = max(balance["charge"], float(abs(q/initial[2]-1)))
                total_steps += 1
            rows = [initial, model.measure(settings["tau_short"], u, v, (e, q))]
            physical = use_compensated_controls(model, (u, v, rows, balance), reg["physical_limits"])
            tested[name] = dict(passed=gates(physical), physical=physical, balance=balance,
                                steps=count, time=settings["tau_short"],
                                seconds=perf_counter()-started, max_iterations=stepper.max_iterations,
                                max_normalized_stage_change=stepper.max_normalized_change,
                                degrees_of_freedom_radial=model.mesh.n)
    passed = gates(controls) and len(tested) == len(reg["cases"]) and all(r["passed"] for r in tested.values())
    return dict(controls=controls, manufactured=manufactured_reports, manufactured_gates=radial,
                Cauchy=seed, Cauchy_projection_chi_in_core=projections, identities=invariants,
                time_controls=tested, M2_steps_preflight=total_steps, M2_production_started=False, passed=passed)
