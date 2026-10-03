"""Audit the variable translation of 14.4 used in chapter 28; no old spectra are recomputed."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from modelo_m2 import BENCHMARK as m

R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/no_radial';O.mkdir(exist_ok=True,parents=True)
rng=np.random.default_rng(28092026);n=20000
r=rng.uniform(.1,20,n);f=rng.uniform(.01,1,n);u=rng.uniform(.001,m.trilinear/m.mixed*.99,n)
fp=-rng.uniform(.001,1,n);up=-rng.uniform(.001,1,n);omega=.9;a=m.mass2-omega**2
D=a+2*m.quartic*f*f-m.trilinear*u+.5*m.mixed*u*u
A=a+6*m.quartic*f*f-m.trilinear*u+.5*m.mixed*u*u
B=np.sqrt(2)*f*(-m.trilinear+m.mixed*u);C=m.mediator**2+m.mixed*f*f
fpp=D*f-2/r*fp;upp=C*u-m.trilinear*f*f-2/r*up
fppp=A*fp+B/np.sqrt(2)*up+2/r**2*fp-2/r*fpp
uppp=np.sqrt(2)*B*fp+C*up+2/r**2*up-2/r*upp
w=np.array([-np.sqrt(2)*fp,-up]);wp=np.array([-np.sqrt(2)*fpp,-upp]);wpp=np.array([-np.sqrt(2)*fppp,-uppp])
rest=np.array([A*w[0]+B*w[1],B*w[0]+C*w[1]])
res=-wpp-2/r*wp+2/r**2*w+rest
scale=abs(wpp)+abs(2/r*wp)+abs(2/r**2*w)+abs(rest)+1
jet_error=float(np.max(abs(res)/scale))

# Independent integration of the ground-state transform. Test coefficients
# are constructed with a known positive vector, not claimed to solve M2.
left,right=.2,4.
def terms(t):
    w=np.array([t*np.exp(-t),t*np.exp(-2*t)]);ks=np.array([1.,2.])
    wp=w*(1/t-ks);W=.3*np.exp(-t)
    bump=(t-left)**2*(right-t)**2
    bp=2*(t-left)*(right-t)*(right+left-2*t)
    s=bump*np.array([np.cos(2*t),np.sin(1.3*t)])
    sp=bp*np.array([np.cos(2*t),np.sin(1.3*t)])+bump*np.array([-2*np.sin(2*t),1.3*np.cos(1.3*t)])
    eta=w*s;etap=wp*s+w*sp
    diag=ks**2-4*ks/t+2/t**2+W*w[::-1]/w
    lhs=t*t*(np.sum(etap**2+diag*eta**2)-2*W*eta[0]*eta[1])
    rhs=t*t*(np.sum(w*w*sp*sp)+W*w[0]*w[1]*(s[0]-s[1])**2)
    return lhs,rhs
ql=quad(lambda t:terms(t)[0],left,right,epsabs=1e-11,epsrel=1e-11)
qr=quad(lambda t:terms(t)[1],left,right,epsabs=1e-11,epsrel=1e-11)
quad_error=abs(ql[0]-qr[0])/abs(qr[0])
result=dict(samples=n,translation_identity_scaled_error=jet_error,cooperative_W_positive=bool(np.all(B<0)),
    quadratic_form_lhs=ql[0],quadratic_form_rhs=qr[0],quadratic_form_relative_error=quad_error,
    passed=bool(jet_error<1e-12 and np.all(B<0) and quad_error<1e-10 and qr[0]>0),
    scope='Numerical algebra audit of the variable translation of existing 14.4 identities; functional proof and assumptions are in chapter 28; no existence certificate')
(O/'auditoria_positividad_angular.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));assert result['passed']
