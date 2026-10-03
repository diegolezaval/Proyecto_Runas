"""Check local current identity by finite differences; not a theorem prover."""
from pathlib import Path
import json
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'validacion/P04/C7'
rng=np.random.default_rng(30092026);n=10000
f=rng.uniform(.2,2,n);theta=rng.uniform(-100,100,n)
gf=rng.normal(size=(n,3));gt=rng.normal(size=(n,3))
hf=rng.normal(size=(n,3));ht=rng.normal(size=(n,3))
psi=f*np.exp(1j*theta);lap=np.zeros(n,complex);step=2e-4
for j in range(3):
    plus=(f+step*gf[:,j]+.5*step**2*hf[:,j])*np.exp(1j*(theta+step*gt[:,j]+.5*step**2*ht[:,j]))
    minus=(f-step*gf[:,j]+.5*step**2*hf[:,j])*np.exp(1j*(theta-step*gt[:,j]+.5*step**2*ht[:,j]))
    lap+=(plus-2*psi+minus)/step**2
num=np.imag(np.conj(psi)*lap);pred=2*f*np.sum(gf*gt,axis=1)+f*f*ht.sum(axis=1)
error=float(max(abs(num-pred))/max(abs(pred)))
# The nodal Gaussian has nonzero current but zero divergence: its phase
# cannot be lifted globally. This checks why the positivity assumption matters.
x=rng.normal(size=(n,3));envelope=np.exp(-2*np.sum(x*x,axis=1))
div=4*x[:,0]*x[:,1]*envelope-4*x[:,0]*x[:,1]*envelope
out=dict(samples=n,seed=30092026,current_identity_relative_error=error,nodal_control_divergence_max=float(max(abs(div))),
    passed=error<2e-6,scope='Local algebra and nodal scope control only; global proof is chapter 30, not numerically certified',
    nodal_control_is_M2_solution=False,formal_proof_checker=False)
(O/'auditoria_fase_sin_nodos.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2));assert out['passed']
