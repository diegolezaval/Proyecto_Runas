"""Complecion clasica polinomica del potencial escalar con un mediador real.
No completa los portales A,B ni valida todas las runas. Requiere numpy/scipy.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_bvp,simpson
R=Path(__file__).resolve().parents[1];old=np.loadtxt(R/'validacion/perfil_radial.csv',delimiter=',',skiprows=1)
cfg=json.loads((R/'datos/microscopia.json').read_text())['M2']
from m2_comun import RATIO as ratio, M, G as g, H as h
N=ratio+1;w=cfg['omega_over_m']

def V(f,z):return f*f+ratio*f**4+.5*M*M*z*z+g*z*f*f+.5*h*z*z*f*f

def ueff(s):return s-s*s+s**3/(1+s/N)
def ueffp(s):return 1-2*s+(3*s*s+2*s**3/N)/(1+s/N)**2

def solve_full(Rbox,n,tol,previous=None):
 x=np.linspace(0,Rbox,n)
 if previous is None:
  f=np.interp(x,old[:,0],old[:,1],right=0);fp=np.interp(x,old[:,0],old[:,2],right=0);z=-g*f*f/(M*M+h*f*f);zp=-2*g*M*M*f/(M*M+h*f*f)**2*fp;y=np.vstack([f,fp,z,zp])
 else:y=previous.sol(x)
 def fun(x,y):
  f,fp,z,zp=y
  return np.vstack([fp,(1-w*w+2*ratio*f*f+g*z+.5*h*z*z)*f,zp,M*M*z+g*f*f+h*z*f*f])
 s=solve_bvp(fun,lambda a,b:np.array([a[1],a[3],b[0],b[2]]),x,y,S=np.diag([0.,-2.,0.,-2.]),tol=tol,max_nodes=40000)
 zz=np.linspace(0,Rbox,24001);f,fp,z,zp=s.sol(zz);I=4*np.pi*simpson(zz*zz*f*f,x=zz);G=4*np.pi*simpson(zz*zz*(fp*fp+.5*zp*zp),x=zz);U=4*np.pi*simpson(zz*zz*V(f,z),x=zz);E=w*w*I+G+U;Q=2*w*I
 return s,{'domain':Rbox,'success':bool(s.success),'nodes':s.x.size,'f0':float(f[0]),'mediator0_rescaled':float(z[0]),'Ehat':float(E),'Qhat':float(Q),'E_over_Q':float(E/Q),'virial_relative':float(abs(G+3*U-3*w*w*I)/E),'max_residual':float(max(s.rms_residuals))}
a,aa=solve_full(50,1000,1e-6);b,bb=solve_full(60,1600,1e-8,a)
xx=np.linspace(0,60,1000);yf=b.sol(xx)[:2]
c=solve_bvp(lambda x,y:np.vstack([y[1],(ueffp(y[0]**2)-w*w)*y[0]]),lambda a,b:np.array([a[1],b[0]]),xx,yf,S=np.diag([0.,-2.]),tol=1e-8,max_nodes=20000)
zz=np.linspace(0,60,24001);f,fp=c.sol(zz);I=4*np.pi*simpson(zz*zz*f*f,x=zz);Ead=4*np.pi*simpson(zz*zz*(w*w*f*f+fp*fp+ueff(f*f)),x=zz);Qad=2*w*I
vmin=1-N*(np.sqrt(N)-np.sqrt(ratio))**2;smin=N*(np.sqrt(N/ratio)-1)
report={'model':'M2: un escalar complejo Phi y un mediador real chi; portales conservados como EFT','parameters_dimensionless':{'omega':w,'lambda0_over_lambda':ratio,'M_over_m':M,'g_over_m_sqrtlambda':float(g),'h_over_lambda':h},'exact_effective_potential':f'Uhat(s)=s-s^2+s^3/(1+s/{N:g})','minimum_U_over_s':float(vmin),'s_at_minimum':float(smin),'coarse':aa,'fine':bb,'relative_energy_refinement':abs(aa['Ehat']-bb['Ehat'])/bb['Ehat'],'adiabatic_no_gradient':{'success':bool(c.success),'Ehat':float(Ead),'Qhat':float(Qad),'energy_difference_relative_to_full':float((Ead-bb['Ehat'])/bb['Ehat'])},'scope':'Existencia numérica radial en dos campos, virial y convergencia. No prueba estabilidad no radial, portales ni arquitectura de las 24 runas.'}
report['passed']=bool(aa['success'] and bb['success'] and c.success and vmin>0 and bb['f0']>.1 and bb['virial_relative']<1e-5 and report['relative_energy_refinement']<1e-4)
(R/'validacion/complecion_escalar.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
z=np.linspace(0,30,1201);f,fp,chi,chip=b.sol(z)
(R/'validacion/perfil_dos_campos.csv').write_text('radio,phi_amplitud,chi_reescalado\n'+'\n'.join(f'{a:.12g},{b:.12g},{c:.12g}' for a,b,c in zip(z,f,chi))+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
