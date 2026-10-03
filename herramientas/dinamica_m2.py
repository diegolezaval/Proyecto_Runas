"""Evolución NO LINEAL radial de M2; volúmenes finitos + Verlet.
Datos iniciales cargados prescritos: este ensayo NO prepara el estado desde materia.
La condición exterior es Dirichlet. No se añade amortiguamiento ni ruido.
"""
import json
import numpy as np
from scipy.interpolate import CubicSpline
from m2_comun import ROOT,RATIO,M,G,H,potential

def evolve(n,dt,tmax=24.,radius=40.,eps=.001):
    dx=radius/n;edges=np.linspace(0,radius,n+1);x=(edges[1:]+edges[:-1])/2
    weights=np.diff(edges**3)/3
    p=np.loadtxt(ROOT/'validacion/m2_perfil_convergente.csv',delimiter=',',skiprows=1)
    interp=CubicSpline(p[:,0],p[:,1:]);f,fp,z,zp=interp(x).T
    phi=(f*(1+eps*np.exp(-x*x/25))).astype(complex);chi=z.copy()
    omega=.9*np.dot(weights,f*f)/np.dot(weights,abs(phi)**2)
    vel=1j*omega*phi;vchi=np.zeros(n)
    def lap(q):
        flux=np.zeros(n+1,dtype=q.dtype)
        flux[1:-1]=edges[1:-1]**2*np.diff(q)/dx
        flux[-1]=-2*radius**2*q[-1]/dx
        return np.diff(flux)/weights
    def acceleration(phi,chi):
        s=abs(phi)**2
        return lap(phi)-(1+2*RATIO*s+G*chi+.5*H*chi**2)*phi,lap(chi)-M*M*chi-G*s-H*chi*s
    def gradient(q):
        return np.sum(edges[1:-1]**2*abs(np.diff(q))**2/dx)+2*radius**2*abs(q[-1])**2/dx
    def sample(t):
        energy=4*np.pi*(np.dot(weights,abs(vel)**2+.5*vchi*vchi+potential(abs(phi),chi))+gradient(phi)+.5*gradient(chi))
        charge=8*np.pi*np.dot(weights,np.imag(np.conj(phi)*vel))
        deviation=np.sqrt(np.dot(weights,(abs(phi)-f)**2)/np.dot(weights,f*f))
        return [t,float(energy),float(charge),float(deviation)]
    rows=[sample(0)];a,b=acceleration(phi,chi);steps=int(round(tmax/dt))
    for j in range(steps):
        vel+=.5*dt*a;vchi+=.5*dt*b;phi+=dt*vel;chi+=dt*vchi
        a,b=acceleration(phi,chi);vel+=.5*dt*a;vchi+=.5*dt*b
        if (j+1)%max(1,steps//240)==0:rows.append(sample((j+1)*dt))
    arr=np.array(rows)
    result=dict(n=n,dt=dt,tmax=tmax,radius=radius,initial_relative_amplitude=eps,
                E0=float(arr[0,1]),Q0=float(arr[0,2]),
                max_relative_energy_drift=float(np.max(abs(arr[:,1]/arr[0,1]-1))),
                max_relative_charge_drift=float(np.max(abs(arr[:,2]/arr[0,2]-1))),
                max_amplitude_deviation=float(arr[:,3].max()),final_amplitude_deviation=float(arr[-1,3]))
    np.savetxt(ROOT/f'validacion/m2_dinamica_{n}.csv',arr,delimiter=',',header='tau,Ehat,Qhat,relative_amplitude_deviation',comments='')
    return result

if __name__=='__main__':
    runs=[evolve(800,.002),evolve(1600,.001)]
    report={'model':'M2 escalar comun','runs':runs,'preparation_demonstrated':False,
            'scope':'24 unidades de tiempo; perturbacion radial de amplitud 0.001; no certifica estabilidad global ni tiempos R1.',
            'passed':all(r['max_relative_energy_drift']<1e-5 and r['max_relative_charge_drift']<1e-10 and r['max_amplitude_deviation']<.02 for r in runs)}
    (ROOT/'validacion/dinamica_m2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if not report['passed']:raise SystemExit(1)
