"""Independent continuous-boundary collocation for selected scattering cases."""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicSpline,CubicHermiteSpline
from scipy.integrate import solve_bvp
from modelo_m2 import BENCHMARK as m
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/acceso_lineal'
raw=np.loadtxt(R/'validacion/P06/rama/perfil_w0.90000.csv',delimiter=',',skiprows=1)
fs=CubicHermiteSpline(raw[:,0],raw[:,1],raw[:,2]);zs=CubicHermiteSpline(raw[:,0],raw[:,3],raw[:,4])
records=[]
for Om in [1.95,2.3,5.]:
    # Attempt 1 is retained verbatim. A real/imaginary formulation and exact
    # boundary Jacobian avoid the unconverged complex Newton iterations.
    path=O/f'colocacion_real_Om{Om:.4f}.json'
    if path.exists():records.append(json.loads(path.read_text()));continue
    omega=.9;radius=60.;nu=np.array([omega+Om,omega-Om,Om]);k=np.sqrt(nu[:2]**2-m.mass2);kap=np.sqrt(m.mediator**2-Om**2)
    def matrix(x):
        f=fs(x);z=zs(x);U=m.mass2+4*m.quartic*f*f+m.trilinear*z+.5*m.mixed*z*z;V=2*m.quartic*f*f;Z=(m.trilinear+m.mixed*z)*f
        mat=np.zeros((3,3,len(x)));mat[0,0]=U-nu[0]**2;mat[1,1]=U-nu[1]**2;mat[2,2]=m.mediator**2+m.mixed*f*f-Om**2
        mat[0,1]=mat[1,0]=V;mat[0,2]=mat[2,0]=mat[1,2]=mat[2,1]=Z;return mat
    def fun(x,y):return np.vstack([y[3:],np.einsum('ijk,jk->ik',matrix(x),y[:3])])
    def jac(x,y):
        mat=np.zeros((6,6,len(x)),complex);mat[:3,3:]=np.eye(3)[:,:,None];mat[3:,:3]=matrix(x);return mat
    def bc(ya,yb):
        end=yb[3:].copy();end[:2]+=1j*k*yb[:2];end[2]+=kap*yb[2]
        end[1]-=2j*k[1]/np.sqrt(k[1])*np.exp(1j*k[1]*radius)
        return np.r_[ya[:3],end]
    def unpack(y):return y[:6]+1j*y[6:]
    def realfun(x,y):
        out=fun(x,unpack(y));return np.vstack([out.real,out.imag])
    def realjac(x,y):
        a=jac(x,unpack(y)).real;out=np.zeros((12,12,len(x)))
        out[:6,:6]=a;out[6:,6:]=a;return out
    def realbc(ya,yb):
        out=bc(unpack(ya),unpack(yb));return np.r_[out.real,out.imag]
    ba=np.zeros((6,6),complex);bb=np.zeros((6,6),complex)
    ba[:3,:3]=np.eye(3);bb[3:,3:]=np.eye(3)
    bb[3:,:3]=np.diag(np.r_[1j*k,kap])
    def block(z):return np.block([[z.real,-z.imag],[z.imag,z.real]])
    def realbcjac(ya,yb):return block(ba),block(bb)
    # Saved coarse FD solution is only an initial guess. Both the ODE and
    # continuous radiation boundary are imposed independently by collocation.
    source=O/f'w0.90000_Om{Om:.4f}_h0.0250_R60_estado.npz'
    with np.load(source) as d:r=np.r_[0,d['r']];u=np.vstack([np.zeros((1,3)),d['radial_amplitudes'][:,:,1]])
    spl=CubicSpline(r,u,axis=0);x=np.linspace(0,radius,2401);y=np.vstack([spl(x).T,spl(x,1).T])
    sol=solve_bvp(realfun,realbc,x,np.vstack([y.real,y.imag]),tol=2e-8,bc_tol=1e-10,max_nodes=120000,fun_jac=realjac,bc_jac=realbcjac)
    sy=unpack(sol.y)
    end=sy[:3,-1];amps=(end[:2]-np.array([0,np.exp(1j*k[1]*radius)/np.sqrt(k[1])]))*np.exp(1j*k*radius)
    prob=k*abs(amps)**2;gain=float(np.dot(abs(nu[:2]),prob)/abs(nu[1]))
    candidates=[r for r in json.loads((O/'resultados.json').read_text())['records'] if r['configuration']['Omega']==Om]
    ref=min(candidates,key=lambda v:v['configuration']['dx']);fd=next(v for v in ref['cases'] if v['incoming_channel']==1)
    rec=dict(Omega=Om,success=bool(sol.success),message=sol.message,nodes=len(sol.x),max_rms_residual=float(max(sol.rms_residuals)),
        boundary_residual=float(max(abs(bc(sy[:,0],sy[:,-1])))),probabilities=prob.tolist(),unitarity_error=float(abs(sum(prob)-1)),
        energy_flux_gain=gain,relative_conversion_difference_vs_fd=abs(float(prob[0])-fd['outgoing_probabilities'][0])/float(prob[0]),
        gain_difference_vs_fd=abs(gain-fd['energy_flux_gain']),fd_dx=ref['configuration']['dx'])
    rec['passed']=bool(rec['success'] and rec['unitarity_error']<1e-7 and rec['relative_conversion_difference_vs_fd']<.02 and rec['gain_difference_vs_fd']<1e-5)
    rec['method']='Continuous ODE, real/imaginary collocation, exact boundary Jacobian; original failed complex attempt preserved'
    path.write_text(json.dumps(rec,indent=2)+'\n');np.savez_compressed(O/f'colocacion_real_Om{Om:.4f}_estado.npz',r=sol.x,y=sy)
    records.append(rec);print(json.dumps(rec,indent=2),flush=True)
(O/'verificacion_colocacion_real.json').write_text(json.dumps(dict(records=records,passed=all(x['passed'] for x in records)),indent=2)+'\n')
assert all(x['passed'] for x in records)
