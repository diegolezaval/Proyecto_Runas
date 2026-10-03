"""Assemble a scoped gate from saved results only; never rerun a background."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/acceso_lineal'
def load(n):return json.loads((O/n).read_text())
fd=load('resultados.json');col=load('verificacion_colocacion_real.json');audit=load('auditoria_linealizacion_y_flujos.json')
cfg=json.loads((R/'datos/ensayo_acceso_lineal_CP07.json').read_text())
sourcehash=hashlib.sha256((R/cfg['source']).read_bytes()).hexdigest()
records=fd['records']+fd['controls']
assert all(x['source_sha256']==sourcehash for x in records)
assert all(x['configuration']['ell']==0 and not x['finite_amplitude_backreaction_simulated'] for x in records)
unitarity=max(x['unitary_error'] for x in records);residual=max(x['linear_residual_relative'] for x in records)
relation=max(c['energy_charge_relation_error'] for x in records for c in x['cases'])
vac=[x for x in fd['controls'] if x['configuration']['vacuum']]
one=[x for x in fd['controls'] if len(x['open_channels'])==1]
vacuum_error=max(abs(c['energy_flux_gain']-1) for x in vac for c in x['cases'])
one_error=max(abs(c['energy_flux_gain']-1) for x in one for c in x['cases'])
passed=fd['numerical_campaign_passed'] and col['passed'] and audit['passed'] and all(x['balance_passed'] for x in records) and max(vacuum_error,one_error)<1e-8
out=dict(checkpoint='CP07',status='SUBPREGUNTA_LINEAL_COMPLETADA' if passed else 'PARCIAL',passed=bool(passed),
    source=cfg['source'],source_sha256=sourcehash,finite_difference_cases=len(fd['records']),control_cases=len(fd['controls']),
    independent_continuous_ode_cases=len(col['records']),max_unitarity_error=unitarity,max_solver_residual=residual,
    max_energy_charge_relation_error=relation,vacuum_gain_error=vacuum_error,one_open_channel_gain_error=one_error,
    max_last_relative_grid_difference=max(x['last_relative_conversion_difference'] for x in fd['convergence']),
    max_independent_relative_conversion_difference=max(x['relative_conversion_difference_vs_fd'] for x in col['records']),
    scope='Infinitesimal ell=0 monochromatic scattering at omega=.9 on the saved interpolated profile, nine sampled frequencies; no interval or background uncertainty certificate',
    complete_E03=False,complete_RES0=False,complete_RES2=False,complete_device=False,
    earlier_failed_meshes_preserved=True,earlier_failed_complex_collocation_preserved=True,
    gate_decision='Accept the linear conversion subresult only. Functional gates remain unsatisfied.',
    next='Finite wave packets with explicit incident resource, full backreaction, error controls, reception and recharge remain required.')
(O/'puerta_decision.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2));assert passed
