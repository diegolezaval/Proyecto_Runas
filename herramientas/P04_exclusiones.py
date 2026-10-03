"""C0: chequeo independiente de onda larga y matriz EXACTA de 22 requisitos.

La exclusion analitica con arrollamiento esta en el capitulo 24. La matriz
no convierte casillas no estudiadas en aprobaciones ni agota M2.
"""
from pathlib import Path
import json
import numpy as np
from reproduccion_independiente import finite_elements, extrapolate
R=Path(__file__).resolve().parents[1];O=R/'validacion/P04/exclusiones';O.mkdir(parents=True,exist_ok=True)

def run():
    config=json.loads((R/'datos/campana_4_2.json').read_text());cfg=config['P04_long_wave']
    data=[]
    for k in cfg['k']:
        rows=[finite_elements('validacion/m2_guia_perfil.csv',2,int(round(cfg['radius']/h)),cfg['radius'],0,k) for h in cfg['dx']]
        rate=extrapolate(rows,'rate','h');data.append(dict(k=k,rows=rows,rate_extrapolated=rate,growth_over_k=rate/k))
    # Leading finite-k correction is O(k^2) to sigma/k.
    p0,p1=data;f=(p1['k']/p0['k'])**2
    limit=(f*p0['growth_over_k']-p1['growth_over_k'])/(f-1)
    hist=json.loads((R/'validacion/guia_m2.json').read_text());reference=np.sqrt(-hist['charge_derivative'][-1]['long_wave_cL_squared'])
    periodic=[]
    for mode in (1,2,3):
        k=2*np.pi*mode/config['P04_contract']['length_ell0']
        row=finite_elements('validacion/m2_guia_perfil.csv',2,2000,40,0,k)
        row['periodic_index']=mode;row['linear_time_1e4_to_1e2']=float(np.log(100)/row['rate']);periodic.append(row)
    result=dict(schema_version='1.0.0',stage='C0',long_wave_samples=data,limit_extrapolated=float(limit),
                charge_susceptibility_prediction=float(reference),relative_difference=float(abs(limit/reference-1)),
                periodic_modes=periodic,physical_finite_ends_solved=False,
                passed=bool(abs(limit/reference-1)<cfg['relative_tolerance_to_hydrodynamic_limit'] and all(x['rate']>0 for x in periodic)),
                proof='tratado/24_exclusiones_tubulares_y_busqueda.md',
                warning='Periodic axial modes are diagnostic, not physical end caps. No claim of a complete finite guide.')
    (O/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],long_wave_limit=limit,prediction=reference,relative_difference=result['relative_difference']),indent=2))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':run()
