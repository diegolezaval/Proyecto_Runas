"""Exploratory linear two-field M2 scattering on an already saved background.

Three coupled radial amplitudes; chi is retained as a closed channel. Fluxes,
not shell energy densities, define amplification. No background or spectrum is
recomputed and no finite power, backreaction, receiver or cycle is claimed.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from modelo_m2 import BENCHMARK as m
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/acceso_lineal';O.mkdir(parents=True,exist_ok=True)


def solve(Omega,dx=.05,radius=60.,omega=.9,vacuum=False):
    source=R/f'validacion/P06/rama/perfil_w{omega:.5f}.csv'
    tag=f'w{omega:.5f}_Om{Omega:.4f}_h{dx:.4f}_R{radius:.0f}'+('_vacio' if vacuum else '')
    rp=O/(tag+'.json');sp=O/(tag+'_estado.npz')
    config=dict(Omega=Omega,dx=dx,radius=radius,omega=omega,vacuum=vacuum,ell=0)
    if rp.exists():
        d=json.loads(rp.read_text());assert d['configuration']==config and sp.exists();return d
    n=round(radius/dx);assert abs(n*dx-radius)<1e-12
    r=np.arange(1,n+1)*dx;raw=np.loadtxt(source,delimiter=',',skiprows=1);assert radius<=raw[-1,0]
    f=CubicHermiteSpline(raw[:,0],raw[:,1],raw[:,2])(r)
    z=CubicHermiteSpline(raw[:,0],raw[:,3],raw[:,4])(r)
    if vacuum:f*=0;z*=0
    U=m.mass2+4*m.quartic*f*f+m.trilinear*z+.5*m.mixed*z*z
    V=2*m.quartic*f*f;Z=(m.trilinear+m.mixed*z)*f;C=m.mediator**2+m.mixed*f*f
    nu=np.array([omega+Omega,omega-Omega,Omega]);mass2=np.array([m.mass2,m.mass2,m.mediator**2]);k2=nu**2-mass2
    opened=np.flatnonzero(k2>0);assert 2 not in opened, 'This campaign keeps the mediator closed'
    wave=np.zeros(3);flux=np.zeros(3);ghost=np.zeros(3,dtype=complex)
    for j in range(3):
        if k2[j]>0:
            assert np.sqrt(k2[j])*dx<2
            wave[j]=2/dx*np.arcsin(np.sqrt(k2[j])*dx/2)
            flux[j]=np.sin(wave[j]*dx)/dx;ghost[j]=np.exp(-1j*wave[j]*dx)
        else:ghost[j]=np.exp(-2*np.arcsinh(np.sqrt(-k2[j])*dx/2))
    idx=np.arange(3*n).reshape(n,3)
    diag=np.c_[U-nu[0]**2,U-nu[1]**2,C-nu[2]**2].astype(complex)+2/dx**2
    diag[-1]-=ghost/dx**2
    rows=[idx.ravel()];cols=[idx.ravel()];vals=[diag.ravel()]
    for i,j,c in [(0,1,V),(0,2,Z),(1,2,Z)]:
        rows.extend([idx[:,i],idx[:,j]]);cols.extend([idx[:,j],idx[:,i]]);vals.extend([c,c])
    rows.extend([idx[:-1].ravel(),idx[1:].ravel()]);cols.extend([idx[1:].ravel(),idx[:-1].ravel()])
    vals.extend([np.full(3*(n-1),-1/dx**2),np.full(3*(n-1),-1/dx**2)])
    matrix=coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(3*n,3*n)).tocsc()
    rhs=np.zeros((3*n,len(opened)),complex)
    for col,j in enumerate(opened):
        rhs[idx[-1,j],col]=2j*np.sin(wave[j]*dx)/np.sqrt(flux[j])*np.exp(1j*wave[j]*radius)/dx**2
    solution=splu(matrix).solve(rhs);outgoing=np.zeros((len(opened),len(opened)),complex)
    for col,inc in enumerate(opened):
        for row,j in enumerate(opened):
            incident=1/np.sqrt(flux[j]) if j==inc else 0
            amplitude=(solution[idx[-1,j],col]-incident*np.exp(1j*wave[j]*radius))*np.exp(1j*wave[j]*radius)
            outgoing[row,col]=np.sqrt(flux[j])*amplitude
    probs=abs(outgoing)**2;unitary=float(np.max(abs(outgoing.conj().T@outgoing-np.eye(len(opened)))))
    residual=float(np.max(abs(matrix@solution-rhs))/max(1,np.max(abs(rhs))))
    cases=[]
    for col,j in enumerate(opened):
        Eout=float(np.dot(abs(nu[opened]),probs[:,col]));Ein=abs(nu[j]);sgn=np.sign(nu[opened])
        deltaQ=float(2*(np.dot(sgn,probs[:,col])-np.sign(nu[j])))
        deltaE=float(2*(Eout-Ein))
        cases.append(dict(incoming_channel=int(j),incoming_frequency=float(nu[j]),outgoing_probabilities=probs[:,col].tolist(),
            energy_flux_gain=Eout/Ein,net_outward_charge_flux=deltaQ,net_outward_energy_flux=deltaE,
            energy_charge_relation_error=abs(deltaE-omega*deltaQ),
            predicted_background_charge_rate=-deltaQ,predicted_background_energy_rate=-deltaE,
            background_rates_are_second_order_bookkeeping=True))
    result=dict(configuration=config,source=str(source.relative_to(R)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        full_two_field_linearization=True,closed_mediator_eliminated_algebraically=False,open_channels=opened.tolist(),
        discrete_flux_velocities=flux.tolist(),S_real=outgoing.real.tolist(),S_imag=outgoing.imag.tolist(),
        unitary_error=unitary,linear_residual_relative=residual,cases=cases,
        balance_passed=unitary<1e-8 and residual<1e-9 and all(x['energy_charge_relation_error']<1e-7 for x in cases),
        background_recomputed=False,finite_amplitude_backreaction_simulated=False,complete_RES2=False)
    np.savez_compressed(sp,r=r,radial_amplitudes=solution.reshape(n,3,len(opened)),S=outgoing,config=json.dumps(config))
    rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(tag,'unitary',unitary,'gains',[x['energy_flux_gain'] for x in cases],flush=True)
    assert result['balance_passed'];return result


def run():
    cfg=json.loads((R/'datos/ensayo_acceso_lineal_CP07.json').read_text());records=[]
    for Om in cfg['frequencies']:
        steps=cfg['radial_steps']+cfg.get('per_frequency_refinements',{}).get(str(Om),[])
        for h in steps:records.append(solve(Om,h,cfg['radius']))
        (O/'parcial.json').write_text(json.dumps(dict(status='EN_PROGRESO',records=records),indent=2)+'\n')
    controls=[solve(Om,.025,80.) for Om in cfg['box_controls']]
    controls+=[solve(Om,.05,60.,vacuum=True) for Om in cfg['vacuum_controls']]
    controls+=[solve(Om,.025,60.) for Om in cfg['one_open_channel_controls']]
    checks=[]
    for Om in cfg['frequencies']:
        steps=cfg['radial_steps']+cfg.get('per_frequency_refinements',{}).get(str(Om),[])
        xs=[next(r for r in records if r['configuration']['Omega']==Om and r['configuration']['dx']==h) for h in steps]
        gains=[next(v for v in x['cases'] if v['incoming_channel']==1)['energy_flux_gain'] for x in xs]
        probs=[next(v for v in x['cases'] if v['incoming_channel']==1)['outgoing_probabilities'][0] for x in xs]
        checks.append(dict(Omega=Om,gains=gains,conversion_probabilities=probs,last_absolute_gain_difference=abs(gains[-1]-gains[-2]),
            last_relative_conversion_difference=abs(probs[-1]-probs[-2])/max(1e-12,probs[-1]),
            observed_error_ratio=abs((probs[-3]-probs[-2])/(probs[-2]-probs[-1])) if abs(probs[-2]-probs[-1])>1e-16 else None))
    box=[]
    for c in controls:
        conf=c['configuration']
        if conf['radius']==80:
            old=next(x for x in records if x['configuration']['Omega']==conf['Omega'] and x['configuration']['dx']==.025)
            box.append(dict(Omega=conf['Omega'],max_gain_difference=max(abs(a['energy_flux_gain']-b['energy_flux_gain']) for a,b in zip(old['cases'],c['cases']))))
    passed=all(x['last_relative_conversion_difference']<.02 and x['last_absolute_gain_difference']<1e-4 for x in checks) and all(x['max_gain_difference']<1e-7 for x in box)
    result=dict(status='SUBCALCULO_LINEAL_SUPERADO' if passed else 'REFINAMIENTO_PENDIENTE',records=records,controls=controls,convergence=checks,box_comparisons=box,
        numerical_campaign_passed=passed,complete_RES0=False,complete_RES2=False,complete_device=False,
        scope='Monochromatic ell=0 infinitesimal scattering at omega=0.9 on saved M2 profile; mediator closed and dynamic in linear equations.',
        limitations=['No prepared incident packet or material source','No time-domain backreaction','No demonstrated absorption/storage or cycle','No continuum interval certificate or finite power'])
    (O/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],convergence=checks,box=box),indent=2),flush=True)


if __name__=='__main__':run()
