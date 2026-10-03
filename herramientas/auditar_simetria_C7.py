"""Auditor de identidades de la prueba C7; NO sustituye la demostración funcional."""
from pathlib import Path
import json
import numpy as np
from modelo_m2 import BENCHMARK as m
R=Path(__file__).resolve().parents[1];O=R/'validacion/P04/C7';O.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(27092026);n=20000;w=.9;a=m.mass2-w*w;g=m.trilinear;h=m.mixed;M=m.mediator;lam=m.quartic
f,fr=rng.uniform(1e-9,1.5,(2,n));u,ur=rng.uniform(1e-9,.999*g/h,(2,n))
F=lambda f,u:-a*f-2*lam*f**3+g*u*f-.5*h*u*u*f
G=lambda f,u:-M*M*u+g*f*f-h*f*f*u
A=-a-2*lam*(fr*fr+fr*f+f*f)+g*u-.5*h*u*u
B=fr*(g-.5*h*(ur+u));C=(g-h*ur)*(fr+f);D=-M*M-h*f*f
one=F(fr,ur)-F(f,u);two=G(fr,ur)-G(f,u)
err1=float(np.max(abs(one-A*(fr-f)-B*(ur-u)))/np.max(abs(one)))
err2=float(np.max(abs(two-C*(fr-f)-D*(ur-u)))/np.max(abs(two)))
p=np.maximum(f-fr,0);q=np.maximum(u-ur,0)
cross=(B+C)*p*q;upper=3*g*f*p*q
ext_f=rng.uniform(0,M*np.sqrt(a)/(6*g),n);ext_u=rng.uniform(0,a/(2*g),n)
pp,qq=rng.random((2,n));lhs=3*g*ext_f*pp*qq;bound=a/4*pp*pp+M*M/4*qq*qq
checks=dict(reflected_F_identity=err1<1e-12,reflected_G_identity=err2<1e-12,positive_cross_derivatives=bool(np.all(B>0)&np.all(C>0)),
    negative_mediator_diagonal=bool(np.all(D<0)),cross_bound_on_negative_support=bool(np.all(cross<=upper+1e-8)),exterior_young_bound=bool(np.all(lhs<=bound+1e-12)))
result=dict(schema_version='1.0.0',samples=n,seed=27092026,checks=checks,passed=all(checks.values()),F_identity_relative=err1,G_identity_relative=err2,
    benchmark_tail_thresholds=dict(f=float(M*np.sqrt(a)/(6*g)),u=float(a/(2*g))),
    mathematical_proof='tratado/27_simetria_estacionaria_y_cadenas_finitas.md',proof_by_numeric_samples=False,complete_C7=False)
(O/'auditoria_algebra.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
if not result['passed']:raise SystemExit(1)
