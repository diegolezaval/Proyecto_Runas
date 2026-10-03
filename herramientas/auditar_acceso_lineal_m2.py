"""Independent finite-difference linearization and physical plane-wave fluxes."""
from pathlib import Path
import json
import numpy as np
from modelo_m2 import BENCHMARK as m
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/acceso_lineal'
rng=np.random.default_rng(29092026);n=10000
f=rng.uniform(.001,.12,n);z=rng.uniform(-.004,0,n)
a,b,c=(rng.normal(size=(3,n))+1j*rng.normal(size=(3,n)))*.01
phase=np.exp(1j*rng.uniform(0,2*np.pi,n));dp=a*phase+b.conj()*phase.conj();dz=2*(c*phase).real
U=m.mass2+4*m.quartic*f*f+m.trilinear*z+.5*m.mixed*z*z
V=2*m.quartic*f*f;Z=(m.trilinear+m.mixed*z)*f;C=m.mediator**2+m.mixed*f*f
def force(p,zz):
    s=abs(p)**2
    return -(m.mass2+2*m.quartic*s+m.trilinear*zz+.5*m.mixed*zz*zz)*p,-(m.mediator**2+m.mixed*s)*zz-m.trilinear*s
step=1e-6;fp,fz=force(f+step*dp,z+step*dz);fm,zm=force(f-step*dp,z-step*dz)
numphi=(fp-fm)/(2*step);numchi=(fz-zm)/(2*step)
predphi=-(U*a+V*b+Z*c)*phase-(U*b+V*a+Z*c).conj()*phase.conj()
predchi=-2*((C*c+Z*(a+b))*phase).real
errorphi=float(max(abs(numphi-predphi))/max(abs(predphi)))
errorchi=float(max(abs(numchi-predchi))/max(abs(predchi)))
# Calculate stress-energy and U(1) currents directly from plane-wave jets,
# independently of the energy weighting used by the scattering solver.
omega=.9;Om=rng.uniform(1.901,10,n);P=rng.uniform(0,1,n)
def currents(nu,k,amp):
    p=amp.astype(complex);pt=1j*nu*p;pr=1j*k*p
    energy=-2*np.real(np.conj(pt)*pr)
    charge=-2*np.imag(np.conj(p)*pr)
    return energy,charge
nuplus=omega+Om;numinus=omega-Om;kp=np.sqrt(nuplus**2-m.mass2);km=np.sqrt(numinus**2-m.mass2)
# Negative-frequency incident wave, two outgoing channels; unit Wronskian.
ei,qi=currents(numinus,-km,1/np.sqrt(km))
ep,qp=currents(nuplus,-kp,np.sqrt(P/kp))
em,qm=currents(numinus,km,np.sqrt((1-P)/km))
de=ei+ep+em;dq=qi+qp+qm
flux_error=float(max(abs(de-omega*dq)))
gain_error=float(max(abs((ep+em)/(-ei)-(1+2*omega*P/(Om-omega)))))
out=dict(samples=n,seed=29092026,linearization_phi_relative_error=errorphi,linearization_chi_relative_error=errorchi,
    physical_flux_energy_charge_error=flux_error,physical_flux_gain_error=gain_error,
    passed=errorphi<2e-7 and errorchi<2e-7 and flux_error<1e-11 and gain_error<1e-12,
    scope='Algebra and flux normalizations only; not stability, finite-amplitude dynamics or a physical receiver')
(O/'auditoria_linealizacion_y_flujos.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2));assert out['passed']
