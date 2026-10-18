"""Occupied radial spectra and fixed positive-composition alternatives; no M2."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import math
import os
import sys

os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq
from scipy.special import spherical_jn
from scipy.integrate import DOP853
from scipy.integrate._ivp.base import OdeSolver

ATTEMPTS=[]
def forbidden(*args,**kwargs):
    ATTEMPTS.append(True)
    raise RuntimeError('No physical construction or steps in spectrum diagnosis')
DOP853.__init__=DOP853._step_impl=OdeSolver.step=forbidden

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def run(home,output):
    assert not output.exists()
    state=home/'outputs/MIXTO_par_estado.npz';expected='abfae6d6b88a1f5b6a58df1657ea3f860a81b02835fe6598b97315da3c1f3ba4'
    assert sha(state)==expected
    sys.path.insert(0,str(home/'science/herramientas'));sys.path.insert(0,str(home/'candidate'))
    from mixed_backend import Mixed
    from modelo_m2 import BENCHMARK as model
    with np.load(state,allow_pickle=False) as data:saved={k:data[k].copy() for k in data.files}
    assert float(saved['time'])==80
    n=int(saved['coarse_n']);store={};summary=[];coefficients=[2/(j*j*math.comb(2*j,j)) for j in range(1,5)]
    for ell in (2,4):
        grid=[]
        for index,h in enumerate((.125,.0625)):
            sim=Mixed(h,220.,4);selection=slice(0,n) if index==0 else slice(n,None)
            d,e=sim.weighted_tridiagonal2(ell);lam,U=eigh_tridiagonal(d,e,lapack_driver='stemr')
            assert np.min(lam)>0
            mode=sim.ell==ell;window=np.ones(sim.n);transition=(sim.r>=32)&(sim.r<40)
            window[transition]=.5*(1+np.cos(np.pi*(sim.r[transition]-32)/8));window[sim.r>=40]=0
            norms={};errors={}
            for label,window_array in [('full_box',np.ones(sim.n)),('smooth_core',window)]:
                for clock,key_q,key_v in [(0,'initial_q','initial_v'),(80,'q','v')]:
                    q=saved[key_q][2,selection][:,mode];v=saved[key_v][2,selection][:,mode]
                    weight=np.sqrt(sim.w)*window_array
                    aq=U.T@(weight[:,None]*q);av=U.T@(weight[:,None]*v)/model.mediator
                    power=np.sum(aq*aq+av*av,axis=1);direct=np.sum((weight[:,None]*q)**2+(weight[:,None]*v/model.mediator)**2)
                    residual=abs(power.sum()-direct)/max(direct,1e-300);assert residual<=2e-11
                    name=f'{label}_{clock}';norms[name]=power;errors[name]=float(residual)
                    store[f'ell{ell}_grid{index}_{name}']=power
            store[f'ell{ell}_grid{index}_lambda2']=lam
            eigen_residual=np.max(abs(d[:,None]*U[:,:3]+np.r_[e[:,None]*U[1:,:3],np.zeros((1,3))]+np.r_[np.zeros((1,3)),e[:,None]*U[:-1,:3]]-U[:,:3]*lam[:3]))
            grid.append((lam,norms))
            summary.append(dict(ell=ell,h=h,Parseval_residuals=errors,first_three_eigenpair_max_absolute_residual=float(eigen_residual),
                full_vs_smooth_squared_norm_ratio={str(t):float(norms[f'smooth_core_{t}'].sum()/norms[f'full_box_{t}'].sum()) for t in (0,80)}))
        count=len(grid[0][0]);roots=[]
        for j in range(1,count+1):
            centre=(j+ell/2)*np.pi
            roots.append(brentq(lambda z:spherical_jn(ell,z),centre-np.pi*.499999,centre+np.pi*.499999,xtol=1e-12))
        k=np.array(roots)/220;store[f'ell{ell}_continuum_k']=k
        weights=grid[1][1]['smooth_core_0'][:count];total=grid[1][1]['smooth_core_0'].sum()
        quantiles={str(q):float(k[min(np.searchsorted(np.cumsum(weights),q*total),count-1)]) for q in (.5,.9,.99,.999)}
        alternatives=[]
        for degree in range(1,5):
            omega=[]
            for h,(lam,_) in zip((.125,.0625),grid):
                eigenvalues=sum(coefficients[j-1]*h**(2*j-2)*lam[:count]**j for j in range(1,degree+1))
                omega.append(np.sqrt(model.mediator**2+eigenvalues))
            difference=omega[0]-omega[1];store[f'ell{ell}_P{degree}_frequency_grid_difference']=difference
            exact=np.sqrt(model.mediator**2+k*k)
            alternatives.append(dict(degree=degree,coefficients=coefficients[:degree],
                occupied_phase_proxy80=float(np.sqrt(np.dot(weights,4*np.sin(40*difference)**2)/total)),
                occupied_rms_frequency_difference=float(np.sqrt(np.dot(weights,difference*difference)/total)),
                occupied_rms_coarse_frequency_error=float(np.sqrt(np.dot(weights,(omega[0]-exact)**2)/total)),
                occupied_rms_fine_frequency_error=float(np.sqrt(np.dot(weights,(omega[1]-exact)**2)/total)),
                positive_polynomial=True,global_radial_high_order_claim=False))
        summary.append(dict(ell=ell,occupied_k_quantiles_initial=quantiles,
            fine_initial_power_above_coarse_mode_count=float(1-weights.sum()/total),alternatives=alternatives))
    assert sha(state)==expected and not ATTEMPTS
    output.mkdir(parents=True);np.savez_compressed(output/'ESPECTROS.npz',**store)
    result=dict(schema='CP12_OCCUPIED_RADIAL_FREQUENCY_DISCRIMINANT_NO_M2',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        state_sha256=expected,code_sha256=sha(Path(__file__)),spectra_sha256=sha(output/'ESPECTROS.npz'),summary=summary,
        M2_steps_executed=0,DOP853_attempts=0,state_unchanged=True,coefficients_not_fitted=True,
        phase_proxy_definition='sqrt(sum initial fine smooth-core powers *4sin²(80*(omega_coarse-omega_fine)/2)/sum powers)',
        limitations=['Free occupation-weighted phase proxy is not actual coupled evolution or a physical gate',
                    'Mode indices matched by radial Sturm ordering; basis and shape errors not included in phase proxy',
                    'Finite positive compositions retain the derived radial h² residual',
                    'No candidate chosen or CP12 closed by this calculation'],CP12_closed=False)
    (output/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps([row for row in summary if 'alternatives' in row],ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--home',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.home.resolve(),args.output.resolve())
