"""Exact origin-row identities for the fixed P3 action; no M2 import or step.

This is a new rational derivation of the first three row coefficients, not a
repeat of the manufactured-profile F0 preflight or a measured trajectory rate.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json


def apply_radial(values, ell, h):
    radii = [(F(i) + F(1, 2)) * h for i in range(len(values))]
    mass = [h * (r*r + h*h/F(12)) * r**(2*ell) for r in radii]
    cumulative = F(0)
    flux = []
    for i in range(len(values)-1):
        cumulative += mass[i]
        conductance = (2*ell+3)*cumulative / ((i+1)*h*h)
        flux.append(conductance*(values[i+1]-values[i]))
    # Trim one right row rather than introduce any artificial outer closure.
    return [(flux[i] - (flux[i-1] if i else F(0))) / mass[i]
            for i in range(len(values)-1)]


def result(ell, degree, h):
    radius = [(F(i)+F(1,2))*h for i in range(10)]
    u = [r**degree for r in radius]
    t1 = apply_radial(u, ell, h)
    t2 = apply_radial(t1, ell, h)
    t3 = apply_radial(t2, ell, h)
    p3 = [t1[i]-h*h*t2[i]/12+h**4*t3[i]/90 for i in range(3)]
    exact = [F(0) if degree == 0 else
             degree*(degree+2*ell+1)*r**(degree-2) for r in radius[:3]]
    # q = r**ell u; return the scalar coefficients after factoring r**ell.
    return [a-b for a,b in zip(p3,exact)]


def main(output):
    rows = []
    tests = {}
    for ell in range(5):
        for degree in (0,2,4,6):
            full = result(ell,degree,F(1))
            half = result(ell,degree,F(1,2))
            if degree in (0,2):
                tests[f'l{ell}_degree{degree}_exact_first_three_rows'] = all(x == 0 for x in full+half)
            scale = F(1,2)**(degree-2)
            tests[f'l{ell}_degree{degree}_homogeneous_scaling'] = half == [x*scale for x in full]
            rows.append(dict(ell=ell,u_degree=degree,origin_three_residual_coefficients=[str(x) for x in full],
                factored_error='r_i**ell * h**(degree-2) * coefficient',
                first_three_cells_weighted_norm_exponent=(str(F(2*ell+2*degree-1,2)) if degree>=4 else None),
                q_equals_r_power_ell_times_u=True))
    value=dict(schema='CP12_P3_EXACT_FIRST_THREE_ORIGIN_ROWS_NEW_DERIVATION',
        tests=tests,passed=all(tests.values()),rows=rows,arithmetic='fractions.Fraction exact',
        rows_retained=3,minimum_infinite_grid_nodes_used=10,outer_boundary_used=False,
        fixed_composition_coefficients=['1','-1/12','1/90'],
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scientific_worker_sources_imported=False,M2_steps_executed=0,
        preflight_F0_F5_repeated=False,manufactured_profile_campaign_repeated=False,
        trajectory_order_measured=False,trajectory_cause_identified=False,
        correction_validated=False,CP12_closed=False)
    output.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(dict(passed=value['passed'],exact_checks=len(tests),output=str(output))))
    if not value['passed']:
        raise SystemExit(2)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
