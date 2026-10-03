"""Verifica datos ya calculados de CP03 sin repetir E00, E01 ni las campañas.

Integra los perfiles crudos con Simpson; comprueba consistencia de las puertas,
residuos, refinamientos, requisitos originales e integridad de los fallos.
No certifica el continuo ni sustituye una revisión matemática independiente.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from scipy.integrate import simpson
from modelo_m2 import BENCHMARK as model

R = Path(__file__).resolve().parents[1]
def read(p): return json.loads((R/p).read_text())

def run():
    validity = read('validacion/validez/resultados.json')
    branch = read('validacion/P06/rama/resultados.json')
    tube = read('validacion/P04/exclusiones/resultados.json')
    search = read('datos/P04_busqueda.json')
    plan = read('hoja_ruta_original/Plan_investigacion.json')
    audit = read('trazabilidad/reanudacion_CP02/inventario.json')
    checks = {}
    checks['saved_results_and_failures_unchanged'] = all(
        hashlib.sha256((R/p).read_bytes()).hexdigest() == h for p,h in audit['files'].items())
    checks['requirements_22_exact_for_every_candidate'] = all(
        [{k:v for k,v in q.items() if k in plan['requisitos_P04'][0]} for q in c['requirements']] == plan['requisitos_P04']
        for c in search['candidates']) and len(plan['requisitos_P04']) == 22
    checks['sensitivity_10_points_recovered'] = len(validity['independent_sensitivity']) == 10 and all(
        x['status'] == 'SIMULADO' and max(x['E_relative_error'],x['Q_relative_error']) < 1e-7
        and x['result']['max_residual'] < 3e-9 and x['refined']['max_residual'] < 6e-10
        for x in validity['independent_sensitivity'])
    checks['capillary_18_points_refined'] = len(validity['capillary_extension']) == 18 and all(
        x['extrapolation']['relative_sequence_difference'] < .002 and len(x['samples']) == 3
        for x in validity['capillary_extension'])
    recomputed = []
    for b in branch['rows']:
        a = np.loadtxt(R/f"validacion/P06/rama/perfil_w{b['omega']:.5f}.csv",delimiter=',',skiprows=1)
        r,f,fp,z,zp = a.T; w = b['omega']; measure = 4*np.pi*r*r
        integ = lambda q: float(simpson(measure*q,x=r))
        gradient = integ(fp*fp+.5*zp*zp)
        potential = integ(model.potential(f,z))
        I = integ(f*f); E = w*w*I+gradient+potential; Q = 2*w*I
        recomputed.append(dict(omega=w,E=E,Q=Q,E_relative=abs(E/b['E']-1),Q_relative=abs(Q/b['Q']-1),
            virial_relative=abs(gradient+3*(potential-w*w*I))/E,
            binding_below_free_charge=bool(E<Q),fixed_charge_hessian_positive=b['fixed_charge_min']>0))
    checks['branch_23_profiles_consistent'] = len(recomputed) == 23 and all(max(x['E_relative'],x['Q_relative'],x['virial_relative'])<1e-7 for x in recomputed)
    checks['first_law'] = max(x['first_law_error'] for x in branch['derivatives']) < 2e-6
    checks['domain_refinements'] = all(max(x['E_relative'],x['Q_relative'])<1e-7 for x in branch['refinements'])
    checks['unstable_control_preserved'] = next(x for x in branch['rows'] if x['omega']==.985)['fixed_charge_min'] < 0
    checks['long_wave_crosscheck'] = tube['relative_difference'] < .01
    checks['no_complete_device_or_continuum_claim'] = not branch['complete_reserve'] and not branch['continuum_certified'] and not branch['full_3D_nonlinear_stability']
    summary = dict(schema_version='1.0.0',checks=checks,passed=all(checks.values()),recomputed_profiles=recomputed,
        max_profile_quadrature_error=max(max(x['E_relative'],x['Q_relative']) for x in recomputed),
        sensitivity_max_refinement_error=max(max(x['E_relative_error'],x['Q_relative_error']) for x in validity['independent_sensitivity']),
        capillary_max_sequence_difference=max(x['extrapolation']['relative_sequence_difference'] for x in validity['capillary_extension']),
        scope='Verification of saved new campaign data; no rerun of E00/E01 or declaration of completed E02/E03/RES0.')
    (R/'validacion/verificacion_CP03.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='recomputed_profiles'},ensure_ascii=False,indent=2))
    if not summary['passed']: raise SystemExit(1)

if __name__=='__main__': run()
