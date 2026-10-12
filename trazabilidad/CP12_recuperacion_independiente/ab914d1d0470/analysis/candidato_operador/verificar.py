"""Preregistered static candidate checks. No physical integration or observer modification."""
from pathlib import Path
import hashlib, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;HOME=HERE.parents[1];ROOT=HOME/'science';sys.path.insert(0,str(ROOT/'herramientas'))
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq
from scipy.special import spherical_jn
from operador import Candidate
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
identity=json.loads((HOME/'preregistration/identidad_cientifica.json').read_text());before={n:sha(ROOT/n) for n in identity['code_hashes']};assert before==identity['code_hashes']
def roots(ell):
    grid=np.arange(.1,40.,np.pi/20);zeros=[]
    for a,b in zip(grid[:-1],grid[1:]):
        if spherical_jn(ell,a)*spherical_jn(ell,b)<0:
            zeros.append(brentq(lambda x:spherical_jn(ell,x),a,b,xtol=5e-14))
            if len(zeros)==3:return np.array(zeros)
    raise ValueError(ell)
polynomials=[];spectra=[]
for N in [32,64,128,256,512]:
    sim=Candidate(1/N,1.,4)
    for ell in range(5):
        index=int(np.flatnonzero(sim.ell==ell)[0]);q=np.zeros((1,N,sim.nm));q[0,:,index]=sim.r**ell
        r0=sim.lap(q)[0,:,index];q[0,:,index]=sim.r**(ell+2);r2=sim.lap(q)[0,:,index]-(4*ell+6)*sim.r**ell
        errors=[float(np.max(abs(r0[:-2]))),float(np.max(abs(r2[:-2])))];assert max(errors)<5e-8*(N/512)**2+5e-10
        polynomials.append({'N':N,'ell':ell,'solid_harmonic_residual':errors[0],'next_regular_moment_residual':errors[1]})
        d,e=sim.weighted_tridiagonal2(ell);values=eigh_tridiagonal(d,e,select='i',select_range=(0,2),eigvals_only=True,lapack_driver='stebz')
        values4=values+sim.dx**2/12*values**2;exact=roots(ell)**2;assert np.all(values4>0)
        spectra.append({'N':N,'h':sim.dx,'ell':ell,'exact':exact.tolist(),'K2_eigenvalues':values.tolist(),'K_eigenvalues':values4.tolist(),'relative_errors_K2':abs(values/exact-1).tolist(),'relative_errors_K':abs(values4/exact-1).tolist()})
rng=np.random.default_rng(28092026);sim=Candidate(1/64,1.,4);q=rng.normal(size=(3,sim.n,sim.nm))*.01;v=rng.normal(size=q.shape)*.01;direction=rng.normal(size=q.shape)
def energy(x):
    b,f,a,bnd,unused=sim.components(x,v);return float(b.sum()+f.sum()+a.sum()+bnd)
force=sim.force(q);step=1e-6;numerical=(energy(q+step*direction)-energy(q-step*direction))/(2*step)
analytical=-np.sum(sim.w[None,:,None]*np.array([2,2,1])[:,None,None]*force*direction)
variation=float(abs(numerical-analytical)/max(1,abs(analytical)));charge=float(abs(2*np.sum(sim.w[:,None]*(q[0]*force[1]-q[1]*force[0]))))
assert variation<2e-7 and charge<1e-10
after={n:sha(ROOT/n) for n in identity['code_hashes']};assert before==after
orders=[]
for ell in range(5):
    rows=[r for r in spectra if r['ell']==ell]
    for a,b in zip(rows[:-1],rows[1:]):orders.append({'ell':ell,'coarse_N':a['N'],'fine_N':b['N'],'observed_order_K':(np.log(np.array(a['relative_errors_K'])/np.array(b['relative_errors_K']))/np.log(2)).tolist()})
result={'schema':'CP12_STATIC_ACTION_CANDIDATE_WITH_ORIGINAL_MASS','M2_steps':0,'original_sources_unchanged':before==after,'regular_polynomials_verified':True,'positive_quadratic_form':True,
    'variational_force_relative_residual':variation,'original_charge_acceleration_absolute':charge,'mass_and_potential_unchanged':True,'physical_correction_tested':False,'observer_backend_for_candidate_implemented':False,
    'global_fourth_order_claimed':False,'CP12_closed':False,'polynomials':polynomials,'spectra':spectra,'orders':orders,'source_sha256':sha(Path(__file__)),'operator_sha256':sha(HERE/'operador.py'),'preregistration_sha256':sha(HERE/'PRERREGISTRO.md')}
out=HERE/'resultados.json';assert not out.exists();out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({'M2_steps':0,'regular_polynomials_verified':True,'variational_force_relative_residual':variation,'charge_acceleration':charge,'physical_correction_tested':False,'CP12_closed':False}))
