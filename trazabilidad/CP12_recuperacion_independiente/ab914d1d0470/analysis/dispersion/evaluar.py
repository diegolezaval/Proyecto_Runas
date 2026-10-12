"""Principal-symbol reference, not a measurement of the CP12 fields."""
from pathlib import Path
import hashlib, json, math, sys
HERE=Path(__file__).resolve().parent;HOME=HERE.parents[1];ROOT=HOME/'science'
sys.path.insert(0,str(ROOT/'herramientas'))
from modelo_m2 import BENCHMARK as model
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
identity=json.loads((HOME/'preregistration/identidad_cientifica.json').read_text())
before={n:sha(ROOT/n) for n in identity['code_hashes']};assert before==identity['code_hashes']
original=json.loads((ROOT/'datos/ensayo_causal_chi_CP12.json').read_text())
cfg=identity['case']['configuration'];cuts=cfg['wave_number_cuts'];hs=[c['dx'] for c in cfg['physical_configurations']]
rows=[]
for k in cuts:
    continuous=math.sqrt(model.mediator**2+k*k)
    entries=[]
    for h in hs:
        omega=math.sqrt(model.mediator**2+4*math.sin(k*h/2)**2/h**2)
        entries.append(dict(h=h,omega=omega,omega_minus_continuum=omega-continuous,group_velocity=math.sin(k*h)/(h*omega),kh=k*h,coarse_or_fine_nyquist_respected=k<math.pi/h))
    delta=entries[0]['omega']-entries[1]['omega']
    rows.append(dict(k=k,continuum_omega=continuous,continuum_group_velocity=k/continuous,grids=entries,
        phase_contrasts=[dict(time=t,signed_unwrapped_phase=delta*t,unit_complex_wave_difference=2*abs(math.sin(delta*t/2))) for t in [24,32,160]]))
after={n:sha(ROOT/n) for n in identity['code_hashes']};assert before==after
result=dict(schema='CP12_PASSIVE_LOCAL_PRINCIPAL_SYMBOL_REFERENCE',mediator_mass=model.mediator,original_wave_number_cuts=cuts,maps=hs,rows=rows,M2_steps=0,
    scientific_sources_unchanged=before==after,model_sha256=sha(ROOT/'herramientas/modelo_m2.py'),preregistration_sha256=sha(HERE/'PRERREGISTRO.md'),source_sha256=sha(Path(__file__)),
    measured_CP12_chi_error=False,radial_geometry_and_feedback_included=False,physical_gate_evaluated=False,physical_correction_tested=False,CP12_closed=False)
target=HERE/'resultados.json';assert not target.exists();target.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result))
