"""Soluciones radiales de M2 sin imponer las relaciones del benchmark.

Las cinco coordenadas fisicas pertenecen a ScalarModel. omega, dimension,
norma y caja son estados o controles numericos, nunca constantes nuevas.
"""
import numpy as np
from scipy.integrate import solve_bvp, simpson
from modelo_m2 import BENCHMARK

def solve_state(omega=.9,dimension=3,radius=60.,n=1200,tol=1e-8,previous=None,model=BENCHMARK):
    x=np.linspace(0,radius,n)
    if previous is None:
        raise ValueError('Provide an explicit seed profile/callable or a previous BVP; no hidden branch choice')
    y=previous.sol(x) if hasattr(previous,'sol') else previous(x)
    def fun(x,y):
        f,fp,z,zp=y; af,az=model.forces(f,z,omega)
        return np.vstack([fp,af,zp,az])
    def jac(x,y):
        f,fp,z,zp=y;j=np.zeros((4,4,x.size));b=model.amplitude_jacobian(f,z,omega)
        j[0,1]=1;j[2,3]=1;j[1,0]=b[0,0];j[1,2]=b[0,1];j[3,0]=b[1,0];j[3,2]=b[1,1]
        return j
    s=solve_bvp(fun,lambda a,b:np.array([a[1],a[3],b[0],b[2]]),x,y,
                S=np.diag([0.,1-dimension,0.,1-dimension]),fun_jac=jac,tol=tol,max_nodes=60000)
    if not s.success:raise RuntimeError(s.message)
    if np.max(abs(s.y[0]))<.01:raise RuntimeError('Trivial solution, not evidence of nonexistence')
    s.frequency=float(omega)
    return s

def measures(bg,omega,dimension=3,model=BENCHMARK):
    r=np.linspace(0,bg.x[-1],24001);f,fp,z,zp=bg.sol(r)
    surface=4*np.pi if dimension==3 else 2*np.pi
    integ=lambda value:float(surface*simpson(r**(dimension-1)*value,x=r))
    I=integ(f*f);T=integ(fp*fp+.5*zp*zp);U=integ(model.potential(f,z));E=omega**2*I+T+U
    return dict(omega=omega,dimension=dimension,radius=float(bg.x[-1]),f0=float(f[0]),z0=float(z[0]),
                E=E,Q=2*omega*I,I=I,gradient=T,potential=U,E_over_Q=E/(2*omega*I),
                virial_relative=abs((dimension-2)*T+dimension*(U-omega**2*I))/E,
                max_residual=float(max(bg.rms_residuals)),nodes=int(bg.x.size))
