"""Diagnóstico de lectura: tres mallas guardadas, sin repetir evoluciones."""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicSpline
from modelo_m2 import BENCHMARK as model

R=Path(__file__).resolve().parents[1]
O=R/'validacion/P06/no_radial'
result=json.loads((O/'resultados.json').read_text())
assert not result['pending']
controls={x['control']:x for x in result['comparisons']}
coarse=controls['radial_mediador_grueso']
fine=controls['radial_mediador_refinado']
keys=['norm_relative_sup_error','final_complex_nonradial_field_error_over_initial_norm',
      'final_phi_phase_space_error_over_initial_norm','final_mediator_nonradial_error_over_initial_norm',
      'final_mediator_phase_space_error_over_initial_norm']
ratios={k:dict(coarse_difference=coarse[k],fine_difference=fine[k],
              reduction_ratio=coarse[k]/fine[k],observed_log2_ratio=float(np.log2(coarse[k]/fine[k]))) for k in keys}

def initial_difference(left,right):
    arrays=[]
    for name in [left,right]:
        with np.load(O/f'{name}_estado.npz',allow_pickle=False) as d:
            arrays.append((d['initial_q'],d['initial_v'],json.loads(str(d['config']))))
    qc,vc,cc=arrays[0];qf,vf,cf=arrays[1]
    rc=(np.arange(qc.shape[1])+.5)*cc['dx']
    rf=(np.arange(qf.shape[1])+.5)*cf['dx'];use=rf<40;rr=rf[use]
    edges=np.arange(len(rf)+1)*cf['dx'];w=(np.diff(edges**3)/3)[use,None]
    ac=CubicSpline(rc,qc,axis=1)(rr);bc=CubicSpline(rc,vc,axis=1)(rr)
    af=qf[:,use];bf=vf[:,use]
    out={}
    for name,field,velocity,ref,refv,mass2 in [
        ('phi',ac[0]+1j*ac[1],bc[0]+1j*bc[1],af[0]+1j*af[1],bf[0]+1j*bf[1],model.mass2),
        ('chi',ac[2],bc[2],af[2],bf[2],model.mediator**2)]:
        error=abs(field[:,1:]-ref[:,1:])**2
        verror=abs(velocity[:,1:]-refv[:,1:])**2/mass2
        denom=np.sum(w*abs(ref[:,1:])**2)
        denomv=np.sum(w*(abs(ref[:,1:])**2+abs(refv[:,1:])**2/mass2))
        out[name]=dict(initial_field_relative_difference=float(np.sqrt(np.sum(w*error)/denom)),
                       initial_phase_space_relative_difference=float(np.sqrt(np.sum(w*(error+verror))/denomv)))
    return out

report=dict(checkpoint='CP08_REFINAMIENTO_NO_RADIAL',evolutions_repeated=False,
    method='Cocientes de diferencias entre tres mallas al mismo tau=160; comparación inicial por spline cúbico en r<40 y modos no radiales.',
    ratios=ratios,initial_coarse=initial_difference(coarse['left'],coarse['right']),
    initial_fine=initial_difference(fine['left'],fine['right']),
    conclusion='El campo Phi muestra reducción próxima a cuatro, pero chi con velocidades no mejora. No se justifica extrapolación de Richardson ni predecir que otra malla superará el umbral.',
    cause_identified=False,continuum_error_certified=False,
    next_question='Discriminar error de fase del mediador y sensibilidad espacial/temporal conjunta con un protocolo adicional prerregistrado; no relajar la puerta.')
(O/'diagnostico_convergencia_CP08.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
