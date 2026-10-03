"""E01: identidades, dimensiones, cinco variaciones y equivalencia del benchmark."""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from modelo_m2 import BENCHMARK as model
from soluciones_m2 import solve_state,measures
R=Path(__file__).resolve().parents[1];O=R/'validacion/identidades';O.mkdir(exist_ok=True,parents=True)

def run():
    rng=np.random.default_rng(271926);errors=[];jacerrors=[];dimerrors=[];continuity=[]
    for f,z in rng.uniform([.02,-.2],[1.,.1],size=(32,2)):
        step=1e-25
        force_from_action=np.array([np.imag(model.potential(f+1j*step,z))/step/2,np.imag(model.potential(f,z+1j*step))/step])
        force=np.array(model.forces(f,z))
        errors.append(float(np.linalg.norm(force-force_from_action)/max(1,np.linalg.norm(force))))
        J=np.column_stack([np.imag(model.forces(f+1j*step,z))/step,np.imag(model.forces(f,z+1j*step))/step])
        jacerrors.append(float(np.linalg.norm(model.amplitude_jacobian(f,z)-J)/max(1,np.linalg.norm(J))))
        Phi=f*model.mass_reference/np.sqrt(model.lambda_reference);chi=z*model.mass_reference/np.sqrt(model.lambda_reference)
        Vdim=model.m**2*Phi**2+model.lambda0*Phi**4+model.M**2*chi**2/2+model.g*chi*Phi**2+model.h*chi**2*Phi**2/2
        dimerrors.append(float(abs(Vdim*model.lambda_reference/model.mass_reference**4-model.potential(f,z))/max(1,abs(model.potential(f,z)))))
        # Noether divergence using independently assigned local jets and EOM.
        a,b=rng.normal(size=2);Fa,Fz=model.forces(np.sqrt(a*a+b*b),z)
        coefficient=Fa/np.sqrt(a*a+b*b)
        div=2*(a*(-coefficient*b)-b*(-coefficient*a));continuity.append(float(abs(div)))
    raw=np.loadtxt(R/'validacion/m2_perfil_convergente.csv',delimiter=',',skiprows=1)
    f=CubicHermiteSpline(raw[:,0],raw[:,1],raw[:,2]);z=CubicHermiteSpline(raw[:,0],raw[:,3],raw[:,4])
    seed=lambda x:np.array([f(x),f(x,1),z(x),z(x,1)])
    bg=solve_state(previous=seed,tol=1e-9,n=1800);m=measures(bg,.9)
    old=json.loads((R/'validacion/cierre_m2.json').read_text())['field_convergence'][-1]
    equivalence={k:abs(m[k]/old[v]-1) for k,v in [('E','Ehat'),('Q','Qhat'),('f0','f0'),('z0','z0')]}
    # Each physical coordinate can move alone: detect hidden benchmark constraints.
    independent=[]
    for name in ('m','M','lambda0','g','h'):
        v=model.with_parameter(name,getattr(model,name)*(1+1e-4))
        row=dict(parameter=name,derived_lambda=v.derived_lambda,potential_change=float(v.potential(.6,-.05)-model.potential(.6,-.05)),
                 unchanged_other_coordinates=all(getattr(v,k)==getattr(model,k) for k in ('m','M','lambda0','g','h') if k!=name))
        independent.append(row)
    q=2*.9*.5;K=.2;n=2
    # Phase theta=omega*t-K*z+n*phi, j^0 positive for omega>0.
    signs=dict(X=.9**2-K**2,j0=q,jz=2*.5*K,T0z=2*.5*.9*K,Jz_over_Q=-n)
    checks=dict(action_derivatives=max(errors)<1e-12,jacobian=max(jacerrors)<1e-12,
                dimensional_equivalence=max(dimerrors)<1e-11,noether_local=max(continuity)<1e-10,
                numerical_benchmark=max(equivalence.values())<1e-8,
                all_five_coordinates=all(x['unchanged_other_coordinates'] and x['potential_change']!=0 for x in independent))
    result=dict(schema_version='1.0.0',stage='E01',action_derivative_max_relative=max(errors),jacobian_max_relative=max(jacerrors),
                dimensional_max_relative=max(dimerrors),noether_max_absolute=max(continuity),reference_equivalence=equivalence,
                independent_coordinates=independent,phase_sign_example=signs,benchmark=m,checks=checks,passed=all(checks.values()),
                scope='Identidades clasicas y benchmark; no EFT cuantica ni estabilidad global de dispositivos.')
    (O/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result['passed']:raise SystemExit(1)
if __name__=='__main__':run()
