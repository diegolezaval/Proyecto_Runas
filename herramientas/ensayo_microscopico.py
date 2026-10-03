"""Sector escalar radial aislado. Requiere numpy y scipy; no valida redes rúnicas."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_bvp, simpson
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'datos/parametros.json').read_text())['microscopic_benchmark'];w=p['omega']
def initial_branch():
 x=np.linspace(0,60,600);f=.5/np.cosh(x/4);y=np.vstack([f,-f*np.tanh(x/4)/4])
 def rhs(x,y,p):return np.vstack([y[1],(1-p[0]**2)*y[0]-2*y[0]**3+3*y[0]**5])
 s=solve_bvp(rhs,lambda a,b,p:np.array([a[1],b[0],a[0]-.5]),x,y,p=[.93],S=np.array([[0.,0.],[0.,-2.]]),tol=1e-7,max_nodes=20000)
 if not s.success:raise RuntimeError(s.message)
 for wi in np.linspace(s.p[0],w,40):
  x=np.linspace(0,60,800);y=s.sol(x)
  s=solve_bvp(lambda x,y:np.vstack([y[1],(1-wi*wi)*y[0]-2*y[0]**3+3*y[0]**5]),lambda a,b:np.array([a[1],b[0]]),x,y,S=np.array([[0.,0.],[0.,-2.]]),tol=1e-7,max_nodes=30000)
  if not s.success:raise RuntimeError(s.message)
 return s

def solve(R,n,tol,old=None):
 x=np.linspace(0,R,n)
 if old is None:
  f=.74/(1+np.exp((x-8)*.8));y=np.vstack([f,-.8*f*(1-f/.74)])
 else:y=old.sol(x)
 def rhs(x,y):return np.vstack((y[1],(1-w*w)*y[0]-2*y[0]**3+3*y[0]**5))
 def bc(a,b):return np.array([a[1],b[0]])
 sol=solve_bvp(rhs,bc,x,y,S=np.array([[0.,0.],[0.,-2.]]),tol=tol,max_nodes=40000)
 z=np.linspace(0,R,20001);f,fp=sol.sol(z);I=4*np.pi*simpson(z*z*f*f,x=z);G=4*np.pi*simpson(z*z*fp*fp,x=z);U=4*np.pi*simpson(z*z*(f*f-f**4+f**6),x=z);Q=2*w*I;E=w*w*I+G+U
 return sol,{'radius_domain':R,'nodes':sol.x.size,'success':bool(sol.success),'message':sol.message,'f0':float(f[0]),'Qhat':float(Q),'Ehat':float(E),'E_over_Q':float(E/Q) if Q else None,'virial_relative':float(abs(G+3*U-3*w*w*I)/max(E,1e-30)),'solver_max_rms_residual':float(max(sol.rms_residuals)),'nonnegative_profile':bool(min(f)>-1e-8),'tail_absolute':float(abs(f[-1]))}
seed=initial_branch();a,ra=solve(60,600,1e-6,seed);b,rb=solve(80,1000,1e-8,a)
res={'model':p,'coarse':ra,'fine':rb,'relative_change_E':abs(rb['Ehat']-ra['Ehat'])/rb['Ehat'],'relative_change_Q':abs(rb['Qhat']-ra['Qhat'])/rb['Qhat'],'scope':'Solucion radial estacionaria hasta rotacion de fase. E/Q<1 compara con cuantos libres del sector aislado. No prueba estabilidad completa, otras geometrias, bombeo ni compatibilidad operacional.'}
res['passed']=bool(ra['success'] and rb['success'] and rb['f0']>.1 and rb['nonnegative_profile'] and rb['virial_relative']<1e-5 and res['relative_change_E']<1e-4 and rb['E_over_Q']<1)
(ROOT/'validacion/microscopia.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
z=np.linspace(0,40,1001);y=b.sol(z)
(ROOT/'validacion/perfil_radial.csv').write_text('radio_adimensional,amplitud,derivada\n'+'\n'.join(','.join(f'{v:.12g}' for v in row) for row in zip(z,y[0],y[1]))+'\n')
print(json.dumps(res,ensure_ascii=False,indent=2))
if not res['passed']:raise SystemExit(1)
