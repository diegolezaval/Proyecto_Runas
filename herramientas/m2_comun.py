"""Sector escalar M2: una configuración común, sin parámetros por primordial.
Unidades x=m r, tau=m t, f=sqrt(lambda)*Phi/m, z=sqrt(lambda)*chi/m.
No incluye un Hamiltoniano de materia ni convierte una curva SVG en una pared.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_bvp, simpson
from modelo_m2 import BENCHMARK, require_reference_benchmark
require_reference_benchmark()

ROOT=Path(__file__).resolve().parents[1]
THETA=json.loads((ROOT/'datos/theta_comun.json').read_text())
CFG=THETA['scalar_benchmark']['dimensionless']
RATIO=BENCHMARK.quartic
M=BENCHMARK.mediator
G=BENCHMARK.trilinear
H=BENCHMARK.mixed

def potential(f,z):
    return BENCHMARK.potential(f,z)

def ueff(s):
    return BENCHMARK.effective(s)

def up(s):
    return BENCHMARK.effective_prime(s)

def upp(s):
    return BENCHMARK.effective_second(s)

def solve(omega=.9,radius=60,n=1600,tol=1e-9,previous=None):
    x=np.linspace(0,radius,n)
    if previous is None:
        seed=np.loadtxt(ROOT/'validacion/perfil_radial.csv',delimiter=',',skiprows=1)
        f=np.interp(x,seed[:,0],seed[:,1],right=0)
        fp=np.interp(x,seed[:,0],seed[:,2],right=0)
        z=-G*f*f/(M*M+H*f*f)
        zp=-2*G*M*M*f/(M*M+H*f*f)**2*fp
        y=np.vstack([f,fp,z,zp])
    else:y=previous.sol(x)
    def fun(x,y):
        f,fp,z,zp=y
        return np.vstack([fp,(1-omega*omega+2*RATIO*f*f+G*z+.5*H*z*z)*f,
                          zp,M*M*z+G*f*f+H*z*f*f])
    def jac(x,y):
        f,fp,z,zp=y
        j=np.zeros((4,4,x.size))
        j[0,1]=1;j[2,3]=1
        j[1,0]=1-omega*omega+6*RATIO*f*f+G*z+.5*H*z*z
        j[1,2]=(G+H*z)*f
        j[3,0]=2*f*(G+H*z);j[3,2]=M*M+H*f*f
        return j
    result=solve_bvp(fun,lambda a,b:np.array([a[1],a[3],b[0],b[2]]),x,y,
                     S=np.diag([0.,-2.,0.,-2.]),fun_jac=jac,tol=tol,max_nodes=80000)
    if not result.success:raise RuntimeError(result.message)
    return result

def measures(result,omega=.9):
    x=np.linspace(0,result.x[-1],32001)
    f,fp,z,zp=result.sol(x)
    integ=lambda a:float(4*np.pi*simpson(x*x*a,x=x))
    I=integ(f*f);gradient=integ(fp*fp+.5*zp*zp);U=integ(potential(f,z))
    energy=omega*omega*I+gradient+U;charge=2*omega*I
    return dict(radius=float(x[-1]),nodes=int(result.x.size),omega=omega,
                f0=float(f[0]),z0=float(z[0]),Ehat=energy,Qhat=charge,
                E_over_Q=energy/charge,virial_relative=abs(gradient+3*U-3*omega*omega*I)/energy,
                max_collocation_residual=float(max(result.rms_residuals)),gradient=gradient,
                potential_integral=U,static_scaling_derivative=gradient+3*U,
                min_f=float(f.min()),max_z=float(z.max()),
                monotone_f_to_x30=bool(np.max(fp[(x>1e-3)&(x<30)])<0),
                monotone_z_to_x30=bool(np.min(zp[(x>1e-3)&(x<30)])>0))

if __name__=='__main__':
    print(json.dumps(measures(solve()),indent=2))
