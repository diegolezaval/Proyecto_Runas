"""Dos mecanismos condicionados: bombeo paramétrico y motor de tres niveles."""
from pathlib import Path
import json,math
import numpy as np
from scipy.integrate import solve_ivp
R=Path(__file__).resolve().parents[1];floq=[];cfg=json.loads((R/'datos/microscopia.json').read_text())
for h in cfg['pump']['modulations']:
 gamma=cfg['pump']['gamma'];period=math.pi
 def f(t,y):
  A=np.array([[0.,1.],[-(1+h*math.cos(2*t)),-2*gamma]])
  return (A@y.reshape(2,2)).ravel()
 sol=solve_ivp(f,(0,period),np.eye(2).ravel(),rtol=1e-11,atol=1e-13,max_step=.01)
 multipliers=np.linalg.eigvals(sol.y[:,-1].reshape(2,2));growth=math.log(max(abs(multipliers)))/period
 floq.append({'h':h,'gamma':gamma,'growth_per_time_unit':growth,'resonant_small_h_estimate':h/4-gamma,'multipliers':[[float(z.real),float(z.imag)] for z in multipliers]})
# Rate model after elimination of coherences for a driven transition; rates in a common arbitrary unit.
ec=cfg['engine'];kB=8.617333262145e-5;Th=ec['hot_temperature_K'];Tc=ec['cold_temperature_K'];Eh=ec['hot_transition_eV'];Ec=ec['cold_transition_eV'];Ew=Eh-Ec;nh=1/math.expm1(Eh/(kB*Th));nc=1/math.expm1(Ec/(kB*Tc));gh=ec['gamma_hot'];gc=ec['gamma_cold'];kw=ec['stimulated_rate']
W=np.zeros((3,3))
def rate(src,dst,k):W[dst,src]+=k;W[src,src]-=k
rate(0,2,gh*nh);rate(2,0,gh*(nh+1));rate(0,1,gc*nc);rate(1,0,gc*(nc+1));rate(2,1,kw);rate(1,2,kw)
A=W.copy();b=np.zeros(3);A[-1,:]=1;b[-1]=1;p=np.linalg.solve(A,b)
Jh=gh*(nh*p[0]-(nh+1)*p[2]);Jc=gc*((nc+1)*p[1]-nc*p[0]);Jw=kw*(p[2]-p[1]);Qh=Eh*Jh;Qc=Ec*Jc;Pw=Ew*Jw;S=Qc/Tc-Qh/Th
res={'parametric_pump':{'equation':'q_ddot+2 gamma q_dot+[1+h cos(2t)]q=0','cases':floq,'scope':'Coeficiente de modulación prescrito. No demuestra su obtención manual desde el portal.'},'three_level_engine':{'hot_temperature_K':Th,'cold_temperature_K':Tc,'hot_transition_eV':Eh,'cold_transition_eV':Ec,'work_transition_eV':Ew,'occupation_hot':nh,'occupation_cold':nc,'stationary_populations':p.tolist(),'cycle_fluxes':[Jh,Jc,Jw],'heat_hot_eV_per_time_unit':Qh,'heat_cold_eV_per_time_unit':Qc,'work_eV_per_time_unit':Pw,'cycle_efficiency':Pw/Qh,'entropy_production_eV_K_per_time_unit':S,'energy_residual':Qh-Qc-Pw,'scope':'Niveles y tasas adoptados; transición de trabajo inducida coherentemente, aproximación de eliminación de coherencias. No deriva esos niveles de M2 ni incorpora toda banda, geometría solar o pérdidas de instalación.'}}
# Independent stationary Lindblad solution with a coherent work Hamiltonian.
Gamma12=.5*(gh*(nh+1)+gc*(nc+1));Omega=math.sqrt(kw*Gamma12/2)
Hw=np.zeros((3,3),complex);Hw[1,2]=Hw[2,1]=Omega
Id=np.eye(3);Li=-1j*(np.kron(Id,Hw)-np.kron(Hw.T,Id))
for src,dst,k in [(0,2,gh*nh),(2,0,gh*(nh+1)),(0,1,gc*nc),(1,0,gc*(nc+1))]:
 L=np.zeros((3,3),complex);L[dst,src]=math.sqrt(k);D=L.conj().T@L
 Li+=np.kron(L.conj(),L)-.5*np.kron(Id,D)-.5*np.kron(D.T,Id)
Eq=Li.copy();rhs=np.zeros(9,complex);Eq[-1,:]=np.eye(3).ravel(order='F');rhs[-1]=1
rho=np.linalg.solve(Eq,rhs).reshape((3,3),order='F');drive=-1j*(Hw@rho-rho@Hw);power_exact=-np.trace(np.diag([0,Ec,Eh])@drive).real
lindblad_error=float(max(abs(np.diag(rho).real-p)));stationary_error=float(max(abs(Li@rho.ravel(order='F'))));rho_min=float(min(np.linalg.eigvalsh(rho)))
res['three_level_engine']['quantum_stationary_check']={'coherence_decay_rate':Gamma12,'coherent_coupling_Omega':Omega,'density_matrix_real':rho.real.tolist(),'density_matrix_imag':rho.imag.tolist(),'population_difference_from_rate_model':lindblad_error,'stationary_residual':stationary_error,'minimum_density_eigenvalue':rho_min,'coherent_work_output_eV_per_time_unit':float(power_exact)}
res['passed']=bool(lindblad_error<1e-12 and stationary_error<1e-12 and rho_min>=-1e-12 and abs(power_exact-Pw)<1e-12 and floq[0]['growth_per_time_unit']<0 and floq[1]['growth_per_time_unit']>0 and min(p)>=0 and max(abs(W@p))<1e-12 and Pw>0 and S>0 and abs(Qh-Qc-Pw)<1e-12 and abs(Pw/Qh-.8)<1e-12)
(R/'validacion/preparacion_motor.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False,indent=2))
if not res['passed']:raise SystemExit(1)
