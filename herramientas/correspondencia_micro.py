"""Derivaciones comprobadas: condensado, espectro radial, grafos, cavidades y difusión.
Requiere numpy/scipy. Un resultado condicional no valida el dispositivo completo.
"""
from pathlib import Path
import json, math
import numpy as np
from scipy.integrate import solve_bvp, simpson, quad, solve_ivp
from scipy.linalg import eigh_tridiagonal, eigh
from scipy.optimize import brentq
from geometria import transform,ends
R=Path(__file__).resolve().parents[1];out={};tests=[];cfg=json.loads((R/'datos/microscopia.json').read_text())
def check(name,ok,scope):tests.append({'test':name,'passed':bool(ok),'scope':scope})
def U(s):return s-s*s+s**3
def Up(s):return 1-2*s+3*s*s
def Upp(s):return -2+6*s
# Homogeneous condensate: exact tree-level algebra, no material portal.
s=.5;om2=Up(s);c2=s*Upp(s)/(2*om2+s*Upp(s));p=s*Up(s)-U(s);rho=s*Up(s)+U(s)
ks=np.array([1e-4,.01,.1,1.,3.]);disp=[]
for k in ks:
 D=s*Upp(s)+2*om2
 ylo=k*k+D-math.sqrt(D*D+4*om2*k*k);yhi=k*k+D+math.sqrt(D*D+4*om2*k*k)
 # u_ddot=2w v_dot -(k2+2sU'')u; v_ddot=-2w u_dot-k2 v.
 w=math.sqrt(om2);A=np.array([[0,0,1,0],[0,0,0,1],[-(k*k+2*s*Upp(s)),0,0,2*w],[0,-k*k,-2*w,0]])
 eig=np.linalg.eigvals(A);freqs=sorted(abs(x.imag) for x in eig)[::2]
 err=max(abs(freqs[0]-math.sqrt(max(ylo,0))),abs(freqs[1]-math.sqrt(yhi)))
 disp.append({'k':float(k),'omega_minus':math.sqrt(max(ylo,0)),'omega_plus':math.sqrt(yhi),'matrix_error':err})
check('Dispersión: matriz de perturbación frente a fórmula exacta',max(x['matrix_error'] for x in disp)<1e-7,'Fondo homogéneo aislado, orden clásico.')
cs_goal=1e7/299792458.;sg=brentq(lambda z:z*Upp(z)/(2*Up(z)+z*Upp(z))-cs_goal**2,1/3+1e-12,.5)
eVJ=1.602176634e-19;hc=1.973269804593025e-7;sc=cfg['SI_density_example'];mr=sc['mass_energy_eV'];densscale=mr**4*eVJ/hc**3;lam=rho*densscale/sc['target_density_J_m3'];Lam=sc['cutoff_eV'];kappa=lam**2*Lam**2/mr**2
out['homogeneous']={'s_zero_pressure':s,'rho_hat':rho,'pressure_hat':p,'sound_speed_over_c':math.sqrt(c2),'bulk_modulus_over_energy_density':c2*(rho+p)/rho,'shear_modulus':0,'slow_R1_density_s':sg,'slow_R1_pressure_over_energy_density':(sg*Up(sg)-U(sg))/(sg*Up(sg)+U(sg)),'dispersion':disp,'illustrative_SI_matching':{'mass_energy_eV':mr,'lambda':lam,'cutoff_eV':Lam,'kappa':kappa,'length_unit_m':hc/mr,'energy_density_J_m3':1e9,'field_amplitude_over_cutoff':mr*math.sqrt(s/lam)/Lam,'status':'Una densidad fijada por ajuste. No prueba acoplamientos, vacío ambiental ni R1 completo.'}}
check('Estado sin presión: velocidad c/2 y ausencia de rigidez cortante',abs(c2-.25)<1e-12 and p==0,'Propiedades de fluido; no certifica un sólido ni toda perturbación no lineal.')
# Refine existing radial profile and neighbouring frequencies; no import side effects from older solver.
old=np.loadtxt(R/'validacion/perfil_radial.csv',delimiter=',',skiprows=1)
def radial(w):
 x=np.linspace(0,60,900);f=np.interp(x,old[:,0],old[:,1],right=0);fp=np.interp(x,old[:,0],old[:,2],right=0)
 sol=solve_bvp(lambda x,y:np.vstack((y[1],(1-w*w)*y[0]-2*y[0]**3+3*y[0]**5)),lambda a,b:np.array([a[1],b[0]]),x,np.vstack([f,fp]),S=np.array([[0.,0.],[0.,-2.]]),tol=1e-8,max_nodes=30000)
 if not sol.success:raise RuntimeError(sol.message)
 z=np.linspace(0,60,15001);ff,df=sol.sol(z);I=4*np.pi*simpson(z*z*ff*ff,x=z);grad=4*np.pi*simpson(z*z*df*df,x=z);pot=4*np.pi*simpson(z*z*U(ff*ff),x=z)
 return sol,2*w*I,w*w*I+grad+pot
sol,Q,E=radial(.9);minus,qm,em=radial(.899);plus,qp,ep=radial(.901)
# Radial Hessians on u=r*delta f, Dirichlet at r=0,R. Negative L+ alone does not imply instability at fixed Q.
spectra=[]
for n in [1200,2400]:
 rad=40.;h=rad/(n+1);rr=h*np.arange(1,n+1);ff=sol.sol(rr)[0];a=ff*ff;vp=Up(a)-.9**2+2*a*Upp(a);vm=Up(a)-.9**2
 eigp=eigh_tridiagonal(2/h**2+vp,np.full(n-1,-1/h**2),select='i',select_range=(0,3),eigvals_only=True)
 eigm=eigh_tridiagonal(2/h**2+vm,np.full(n-1,-1/h**2),select='i',select_range=(0,3),eigvals_only=True)
 spectra.append({'N':n,'R':rad,'Lplus_lowest':eigp.tolist(),'Lminus_lowest':eigm.tolist()})
dEdQ=(ep-em)/(qp-qm);slope=(qp-qm)/.002
check('Rama radial: dE/dQ coincide con omega',abs(dEdQ-.9)<5e-4,'Diferencia centrada local; no prueba todas las ramas.')
check('Modo de fase: autovalor de L- converge a cero',abs(spectra[-1]['Lminus_lowest'][0])<abs(spectra[0]['Lminus_lowest'][0]) and abs(spectra[-1]['Lminus_lowest'][0])<1e-5,'Hessiano radial discretizado; no es análisis 3D completo.')
out['radial_extended']={'omega':.9,'Qhat':Q,'Ehat':E,'dQ_domega':slope,'dE_dQ':dEdQ,'hessians':spectra,'scope':'Identidad de rama y modo de fase. La estabilidad física exige restricción de carga y espectro acoplado, además de sectores no radiales.'}
# Compile exact topology into a metric graph. Interior crossings never become vertices.
g=json.loads((R/'datos/geometria.json').read_text());metric=[]
def graph(r):
 vertices={};parents={};edges=[]
 def get(key):
  if key not in vertices:
   i=len(vertices);vertices[key]=i;parents[i]=i
  return vertices[key]
 def find(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 def unite(i,j):parents[find(i)]=find(j)
 endmap={}
 for ins in r['instances']:
  src=g['source_pieces'][ins['piece']]
  for en,xy in src['ends'].items():endmap[ins['id']+'.'+en]=get((ins['id'],tuple(map(str,xy))))
  for seg in src['segments']:
   u=get((ins['id'],tuple(map(str,seg[0]))));v=get((ins['id'],tuple(map(str,seg[-1]))));pp=np.array([[float(v) for v in transform(ins,xy)] for xy in seg])
   if len(pp)==2:L=float(np.linalg.norm(pp[1]-pp[0]))
   else:
    def sp(t):return float(np.linalg.norm(3*((1-t)**2*(pp[1]-pp[0])+2*t*(1-t)*(pp[2]-pp[1])+t*t*(pp[3]-pp[2]))))
    L=quad(sp,0,1,epsabs=1e-11)[0]
   edges.append([u,v,L])
 for join in r['joins']:
  for e in join[1:]:unite(endmap[join[0]],endmap[e])
 roots=sorted({find(i) for i in parents});idx={u:k for k,u in enumerate(roots)}
 edges=[[idx[find(u)],idx[find(v)],L] for u,v,L in edges];leads=[idx[find(endmap[e])] for e in r['free_ends']]
 return edges,leads,len(roots)
def scattering(edges,leads,N,k):
 # Vertex Dirichlet-to-Neumann matrix plus matched semi-infinite leads.
 D=np.zeros((N,N),complex)
 for u,v,L in edges:
  a=k/math.tan(k*L);b=k/math.sin(k*L);D[u,u]-=a;D[v,v]-=a;D[u,v]+=b;D[v,u]+=b
 B=np.zeros((N,len(leads)))
 for j,v in enumerate(leads):B[v,j]+=1;D[v,v]+=1j*k
 if not leads:return np.zeros((0,0),complex),0.
 cond=float(np.linalg.cond(D));X=np.linalg.solve(D,2j*k*B);S=B.T@X-np.eye(len(leads));return S,cond
for r in g['runes']:
 edges,leads,N=graph(r);freqs=[]
 for k in cfg['graph']['wave_numbers_per_graphic_unit']:
  S,cond=scattering(edges,leads,N,k)
  err=float(np.linalg.norm(S.conj().T@S-np.eye(len(leads))))
  freqs.append({'k_per_u':k,'power_matrix':(abs(S)**2).tolist(),'unitarity_error':err,'condition_number':cond})
 closed_spectrum=None
 if not leads:
  mesh=[];nverts=N
  for u,v,L in edges:
   steps=max(2,math.ceil(L/.1));nodes=[u]+list(range(nverts,nverts+steps-1))+[v];nverts+=steps-1
   mesh.extend((nodes[j],nodes[j+1],L/steps) for j in range(steps))
  stiff=np.zeros((nverts,nverts));massmat=np.zeros_like(stiff)
  for u,v,step in mesh:
   stiff[u,u]+=1/step;stiff[v,v]+=1/step;stiff[u,v]-=1/step;stiff[v,u]-=1/step
   massmat[u,u]+=step/3;massmat[v,v]+=step/3;massmat[u,v]+=step/6;massmat[v,u]+=step/6
  ev=eigh(stiff,massmat,subset_by_index=[0,5],eigvals_only=True)
  closed_spectrum={'finite_element_nodes':nverts,'eigenvalues_k_squared_per_u_squared':ev.tolist(),'scope':'Espectro FEM del grafo cerrado ideal, no de los campos 3D.'}
  check(r['id']+' grafo cerrado: modo constante y espectro no negativo',abs(ev[0])<1e-8 and ev[1]>0,'Laplaciano sobre grafo cerrado; no prueba sus terminales funcionales.')
 else:
  check(r['id']+' dispersión conserva flujo',all(x['unitarity_error']<1e-9 for x in freqs),'Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa.')
 metric.append({'id':r['id'],'vertices':N,'edges':edges,'free_end_order':r['free_ends'],'lead_vertices':leads,'length_u':sum(x[2] for x in edges),'samples':freqs,'closed_spectrum':closed_spectrum,'scope':'Modelo métrico condicionado a guías preparadas; no demuestra que la acción produzca ese confinamiento.'})
# degree-three junction: intrinsic reflection, not a perfect automatic splitter.
Sstar=2/3*np.ones((3,3))-np.eye(3);out['nexo_ideal']={'scattering_amplitude':Sstar.tolist(),'power':(Sstar*Sstar).tolist(),'reflected_power_fraction':1/9,'each_other_branch_power_fraction':4/9}
check('Nexo: potencia 1/9+4/9+4/9',abs(sum(Sstar[:,0]**2)-1)<1e-12,'Tres impedancias iguales; una adaptación adicional cambia el reparto.')
out['graphs']=metric
# Two-mode converter, input and all losses accounted. All rates are dimensionless in a common time unit.
cc=cfg['converter'];k_e=cc['kappa_external'];k_i=cc['kappa_intrinsic'];gam_e=cc['gamma_external'];gam_i=cc['gamma_intrinsic'];kap=k_e+k_i;gam=gam_e+gam_i;gc=math.sqrt(cc['cooperativity']*kap*gam)/2
Aa=2*gam*math.sqrt(k_e)/(kap*gam+4*gc*gc);Bb=-4j*gc*math.sqrt(k_e)/(kap*gam+4*gc*gc)
Rrefl=abs(1-math.sqrt(k_e)*Aa)**2;conv=gam_e*abs(Bb)**2;loss_a=k_i*abs(Aa)**2;loss_b=gam_i*abs(Bb)**2
out['converter']={'kappa_external':k_e,'kappa_intrinsic':k_i,'gamma_external':gam_e,'gamma_intrinsic':gam_i,'g':gc,'cooperativity':1.,'transferred_energy_fraction':conv,'reflected_fraction':Rrefl,'loss_mode_a':loss_a,'loss_mode_b':loss_b,'scope':'Conversión resonante monocromática en el modelo de dos modos. No representa rendimiento solar de trabajo ni ancho de banda integral.'}
check('Convertidor: reflexión+salida+pérdidas=entrada',abs(Rrefl+conv+loss_a+loss_b-1)<1e-12,'Respuesta de dos modos resonantes con acoplamientos elegidos.')
# Driven Kerr oscillator, deterministic classical envelope.
kc=cfg['kerr'];Delta=kc['Delta_over_kappa'];K=kc['K_normalized'];kap=kc['kappa_normalized'];drive2=kc['drive_squared']
roots=np.roots([K*K,-2*Delta*K,Delta*Delta+(kap/2)**2,-drive2]);roots=sorted(float(v.real) for v in roots if abs(v.imag)<1e-10 and v.real>=0);states=[]
for n in roots:
 discr=(K*n)**2-(Delta-2*K*n)**2;eig=np.array([-kap/2+np.lib.scimath.sqrt(discr),-kap/2-np.lib.scimath.sqrt(discr)])
 states.append({'occupation_normalized':n,'eigenvalues_real':eig.real.tolist(),'eigenvalues_imag':eig.imag.tolist(),'linearly_stable':bool(max(eig.real)<0)})
def drv(t):
 if 20<=t<30:return kc['write_drive']
 if 60<=t<70:return kc['erase_drive']
 return math.sqrt(drive2)
def ode(t,y):
 x,z,integ=y;n=x*x+z*z;F=drv(t);return [-kap*x-(Delta-K*n)*z+F+kap*x/2,(Delta-K*n)*x-kap*z/2,2*F*x-kap*n]
# Integrate in separate intervals: discontinuities are explicit, no step jumps over a pulse.
y=np.array([0.,0.,0.]);tra=[]
for start,end in [(0,20),(20,30),(30,60),(60,70),(70,110)]:
 F=drv((start+end)/2)
 def f(t,y):
  x,z,integ=y;n=x*x+z*z;return [-kap*x/2-(Delta-K*n)*z+F,(Delta-K*n)*x-kap*z/2,2*F*x-kap*n]
 soln=solve_ivp(f,(start,end),y,rtol=1e-9,atol=1e-11,max_step=.05,dense_output=True)
 tt=np.linspace(start,end,401);yy=soln.sol(tt);tra.extend(zip(tt,yy[0]**2+yy[1]**2));y=soln.y[:,-1]
 if end==60:high=y[0]**2+y[1]**2
 if end==110:low=y[0]**2+y[1]**2
numerr=abs(y[0]**2+y[1]**2-y[2]);out['memory_kerr']={'Delta_over_kappa':2,'nonlinearity_normalized':1,'drive_squared':.9,'fixed_points':states,'after_high_pulse':high,'after_low_pulse':low,'occupation_balance_residual':numerr,'scope':'Memoria alimentada en un modelo modal; no calcula tasa de error térmico, túnel ni coeficiente K desde un glifo 3D.'}
check('Memoria: dos ramas estables y conmutación por pulsos',sum(s['linearly_stable'] for s in states)==2 and abs(high-roots[-1])<1e-4 and abs(low-roots[0])<1e-4,'Biestabilidad clásica determinista de una cavidad reducida.')
check('Memoria: balance temporal de ocupación',numerr<1e-7,'Ocupación normalizada; energía aproximadamente hbar*omega_carrier*N en banda estrecha.')
(R/'validacion/memoria_kerr.csv').write_text('tiempo_kappa,ocupacion_normalizada\n'+'\n'.join(f'{a:.12g},{b:.12g}' for a,b in tra)+'\n')
# Chemistry: detailed balance and equilibrium from microscopic energies and barriers.
chem=cfg['chemical_case'];kBT=chem['kBT_eV'];GA=chem['state_A_eV'];GB=chem['state_B_eV'];TS=chem['transition_eV'];nu=chem['attempt_s_inv'];kf=nu*math.exp(-(TS-GA)/kBT);kr=nu*math.exp(-(TS-GB)/kBT);eq=math.exp(-(GB-GA)/kBT)
check('Química: cociente cinético satisface balance detallado',abs(kf/kr-eq)<1e-12,'Dos estados con igual prefactor y misma transición; ejemplo explícito, no reacción CO2 real.')
# Force and reciprocity from shared potential: central difference vs analytic derivative.
fc=cfg['force_case'];am=fc['a'];sA=fc['sA'];Lm=fc['gaussian_length_m'];mass=fc['mass_kg'];c=299792458.
def Sx(x):return math.exp(-x*x/(2*Lm*Lm))
def Afield(x):z=Sx(x);return math.exp(am*z/(z+sA))
# Avoid cancellation of huge rest energy: interaction energy evaluated with expm1.
x=fc['evaluation_x_m']
def pot(x):z=Sx(x);return mass*c*c*math.expm1(am*z/(z+sA))
z=Sx(x);analytic=mass*c*c*Afield(x)*am*sA*z*x/(Lm*Lm*(z+sA)**2);dx=1e-7;fd=-(pot(x+dx)-pot(x-dx))/(2*dx)
check('Fuerza de portal: gradiente de energía y reacción',abs(fd-analytic)/max(abs(analytic),1e-30)<1e-6,'Perfil impuesto y prueba diferencial; no incluye solución de retroacción.')
out['chemical_example']={'delta_G_eV':GB-GA,'barrier_forward_eV':TS-GA,'temperature_kBT_eV':kBT,'forward_s_inv':kf,'reverse_s_inv':kr,'equilibrium_B_over_A':eq,'scope':'Ejemplo químico abstracto, no predicción de una especie concreta.'}
out['portal_force_example']={'force_N':analytic,'finite_difference_N':fd,'profile':'s(x)=exp(-x^2/(2 L^2)); L=0.02 m; a=1e-10; s_A=1; masa 1 g','scope':'Perfil de campo impuesto para comprobar la fuerza; no evidencia de que sea accesible.'}
out['checks']=tests;out['passed']=all(v['passed'] for v in tests);out['scope']='Pruebas diferenciadas de sectores y aproximaciones. No constituye una teoría microscópica completa validada ni una demostración conjunta de las 24 funciones.'
(R/'validacion/correspondencia_micro.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'checks':len(tests),'failed':[x for x in tests if not x['passed']],'homogeneous':out['homogeneous'],'radial':out['radial_extended'],'memory':out['memory_kerr']},ensure_ascii=False,indent=2))
if not out['passed']:raise SystemExit(1)
