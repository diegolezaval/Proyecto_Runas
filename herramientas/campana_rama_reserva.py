"""E03/RES0: continuacion, Morse restringido y presupuesto de carga util.

No interpreta E(Q) como bateria ni una malla como prueba orbital continua.
"""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq
from modelo_m2 import BENCHMARK
from soluciones_m2 import solve_state, measures
from cierre_m2 import spectrum
from capilaridad_m2 import radial_state, FourFields
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/rama';O.mkdir(parents=True,exist_ok=True)

def seed():
    a=np.loadtxt(R/'validacion/m2_perfil_convergente.csv',delimiter=',',skiprows=1)
    f=CubicHermiteSpline(a[:,0],a[:,1],a[:,2]);z=CubicHermiteSpline(a[:,0],a[:,3],a[:,4])
    def evaluate(x):
        xx=np.minimum(x,a[-1,0]);y=np.array([f(xx),f(xx,1),z(xx),z(xx,1)])
        y[:,x>a[-1,0]]=0
        return y
    return evaluate

def compute(w,bg=None,radius=100,n=2400,tol=2e-9):
    if w<.89999:
        # The fixed-frequency Newton branch becomes ill-conditioned toward
        # thin walls. Continue by norm (the method already validated in 4.1),
        # then match omega. This changes no physical boundary or parameter.
        tau=json.loads((R/'validacion/capilaridad/resultados.json').read_text())['tension']
        cache={}
        def residual(rn):
            sol,row=radial_state(rn,3,tau,extra_radius=40,initial_dx=.06,tol=1e-8)
            cache[rn]=(sol,row)
            return row['omega']-w
        rn=brentq(residual,8.,64.,xtol=2e-8)
        seed_bg=FourFields(cache[rn][0]);seed_bg.frequency=w
        # Never extrapolate the polynomial tail beyond its solved box.
        def safe_seed(x):
            xx=np.minimum(x,seed_bg.x[-1]);y=seed_bg.sol(xx)
            y[:,x>seed_bg.x[-1]]=0
            return y
        bg=solve_state(omega=w,previous=safe_seed,radius=radius,n=n,tol=tol)
        return bg,measures(bg,w)
    if bg is not None and hasattr(bg,'frequency') and abs(w-bg.frequency)>.00031:
        for subw in np.linspace(bg.frequency,w,int(np.ceil(abs(w-bg.frequency)/.0003))+1)[1:-1]:
            bg=solve_state(omega=float(subw),previous=bg,radius=radius,n=n,tol=max(tol,1e-8))
    bg=solve_state(omega=w,previous=seed() if bg is None else bg,radius=radius,n=n,tol=tol)
    return bg,measures(bg,w)

def slope(w,delta=1e-4,previous=None):
    bg,_=compute(w,previous)
    am=compute(w-delta,bg)[1];ap=compute(w+delta,bg)[1]
    return (ap['Q']-am['Q'])/(2*delta),(ap['E']-am['E'])/(ap['Q']-am['Q'])

def run():
    cfg=json.loads((R/'datos/campana_4_2.json').read_text())['reserve_branch']
    points=np.array(cfg['frequencies']); backgrounds={}; rows=[];bg=None
    # Continue away from 0.9 in both directions to avoid selecting the zero branch.
    order=sorted([w for w in points if w<=.9000001],reverse=True)+sorted([w for w in points if w>.9000001])
    for w in order:
        if w>.9000001 and bg is not None and w==min(q for q in points if q>.9000001):bg=backgrounds[min(points,key=lambda q:abs(q-.9))]
        bg,row=compute(float(w),bg);backgrounds[w]=bg
        spectral=[]
        for step in cfg['spectral_dx']:
            n=int(round(cfg['spectral_radius']/step))-1
            spec=spectrum(bg,n,cfg['spectral_radius'],0,omega=w,dynamics=False)
            spectral.append(spec)
        angular=spectrum(bg,int(round(cfg['spectral_radius']/cfg['spectral_dx'][-1]))-1,cfg['spectral_radius'],2,omega=w,dynamics=True)
        row['spectral_radial']=spectral;row['angular_ell2']=angular
        row['omega_threshold_vacuum']=1-w
        eig=angular['selected_generator_eigenvalues']
        low=min((v['imag'] for v in eig if v['imag']>1e-7),default=None)
        row['selected_quadrupole_frequency']=low
        row['quadrupole_below_vacuum_continuum']=bool(low is not None and low<1-w)
        sample=np.linspace(.001,45,9001);f,fp,z,zp=bg.sol(sample)
        active=f>1e-9
        row['resolved_monotone_f']=bool(np.all(fp[active]<0))
        row['resolved_monotone_z']=bool(np.all(zp[active]>0))
        row['radial_morse_count_in_low_four']=sum(v<0 for v in spectral[-1]['H_amplitude'])
        row['fixed_charge_min']=spectral[-1]['H_fixed_charge'][0]
        row['finite_grid_stable_candidate']=bool(row['fixed_charge_min']>0 and row['radial_morse_count_in_low_four']==1 and angular['H_amplitude'][0]>0)
        rows.append(row)
        (O/'partial.json').write_text(json.dumps(dict(status='EN_PROGRESO',rows=rows),ensure_ascii=False,indent=2)+'\n')
        x=np.linspace(0,bg.x[-1],10001)
        np.savetxt(O/f'perfil_w{w:.5f}.csv',np.c_[x,bg.sol(x).T],delimiter=',',header='r,f,fp,z,zp',comments='')
        print('BRANCH',w,row['Q'],row['fixed_charge_min'],low,flush=True)
    rows.sort(key=lambda x:x['omega'])
    differences=[]
    for row in rows:
        w=row['omega'];dq,de=slope(w,previous=backgrounds[w]);differences.append(dict(omega=w,dQ_domega=dq,dE_dQ=de,first_law_error=abs(de-w),E_second_derivative_at_Q=1/dq))
    # Locate a turning point only if there is an actual bracket.
    root=None
    for a,b in zip(differences,differences[1:]):
        if a['dQ_domega']*b['dQ_domega']<0:
            wa,wb=a['omega'],b['omega']
            w0=brentq(lambda w:slope(w,previous=backgrounds[wa])[0],wa,wb,xtol=2e-8)
            bg0,rr=compute(w0,backgrounds[wa]);d1=slope(w0,delta=1e-4,previous=bg0)[0];d2=slope(w0,delta=5e-5,previous=bg0)[0]
            root=dict(state=rr,bracket=[wa,wb],delta1=1e-4,delta2=5e-5,slope1=d1,slope2=d2,
                      meaning='Turning point estimate, not a certified stability boundary.')
            break
    # Refine the candidate and one negative control independently in box and mesh.
    checks=[]
    for w in cfg['refinement_frequencies']:
        old=next(x for x in rows if abs(x['omega']-w)<1e-10);bg,row=compute(w,backgrounds[old['omega']],radius=120,n=2200,tol=5e-10)
        sp=spectrum(bg,3999,100,0,omega=w,dynamics=False)
        checks.append(dict(omega=w,state=row,spectrum=sp,E_relative=abs(row['E']/old['E']-1),Q_relative=abs(row['Q']/old['Q']-1)))
    branch=json.loads((R/'validacion/cierre_m2.json').read_text())['field_convergence'][-1]
    energetic=dict(reference_Q=branch['Qhat'],reference_E=branch['Ehat'],
                   minimum_external_work_to_free_all_charge=branch['Qhat']-branch['Ehat'],
                   incremental_free_wave_work_per_charge=1-.9,
                   fixed_Q_equilibrium_is_not_extractable_excitation=True,
                   scope='Free small-amplitude outgoing charge has E>=m|Q|. A receiver with its own binding energy is a different problem.')
    passed=all(r['virial_relative']<1e-7 for r in rows) and all(r['E_relative']<1e-7 and r['Q_relative']<1e-7 for r in checks)
    out=dict(schema_version='1.0.0',stage='E03/RES0',configuration=cfg,rows=rows,derivatives=differences,turning_point=root,refinements=checks,
             energy_access=energetic,passed=bool(passed),continuum_certified=False,full_3D_nonlinear_stability=False,
             preparation_demonstrated=False,complete_reserve=False,
             angular_coverage='Conditional ground-state transformation of 14.4 plus positive ell>=2 centrifugal increment; numeric monotonicity is not an interval proof.',
             spectrum_scope='Radial constrained Hessian and low-mode count; all angular sectors conditionally controlled for exact positive monotone backgrounds; selected dynamic roots are not a complete root count.')
    (O/'resultados.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    if not passed:raise SystemExit(1)
if __name__=='__main__':run()
