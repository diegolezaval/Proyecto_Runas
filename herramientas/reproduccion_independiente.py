"""E00: derivacion numerica independiente de energia, tension y dos modos.

No importa ningun operador, potencial, solucionador o medida del proyecto.
Los perfiles CSV 4.1 son datos de entrada para E,Q y los modos; la pared se
vuelve a resolver por Newton en diferencias finitas, no por colocacion.
Los modos usan elementos finitos P1 con masa consistente y cuadratura Gauss.
"""
from pathlib import Path
import json, platform, hashlib
import numpy as np
import scipy
from scipy.interpolate import CubicHermiteSpline
from scipy.sparse import coo_matrix, bmat, eye, diags, csc_matrix
from scipy.sparse.linalg import spsolve, eigs, eigsh
from numpy.polynomial.legendre import leggauss

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validacion/reproduccion_independiente'
OUT.mkdir(exist_ok=True, parents=True)
cfg = json.loads((ROOT / 'datos/theta_comun.json').read_text())
# Independently translated from the documented benchmark, not m2_comun.py.
a = float(cfg['scalar_benchmark']['dimensionless']['lambda0_over_lambda'])
mass = float(cfg['scalar_benchmark']['dimensionless']['M_over_m'])
g = mass * np.sqrt(2 * (a + 1))
h = mass**2 / (a + 1)

def potential(f, z):
    s = f*f
    # Completed square avoids cancellation of the large mediator terms.
    d = mass*mass+h*s
    return s+a*s*s-g*g*s*s/(2*d)+d/2*(z+g*s/d)**2

def profile(path):
    raw = np.loadtxt(ROOT / path, delimiter=',', skiprows=1)
    return raw, CubicHermiteSpline(raw[:, 0], raw[:, 1], raw[:, 2]), CubicHermiteSpline(raw[:, 0], raw[:, 3], raw[:, 4])

def integrals(path, dimension, frequency=.9, order=6):
    raw, f, z = profile(path)
    nodes, weights = leggauss(order)
    left, right = raw[:-1, 0], raw[1:, 0]
    x = (left[:, None]+right[:, None])/2+(right-left)[:, None]*nodes/2
    w = (right-left)[:, None]*weights/2 * x**(dimension-1)
    surface = 4*np.pi if dimension == 3 else 2*np.pi
    norm = surface*np.sum(w*f(x)**2)
    grad = surface*np.sum(w*(f(x, 1)**2+z(x, 1)**2/2))
    pot = surface*np.sum(w*potential(f(x), z(x)))
    energy = frequency**2*norm+grad+pot
    return dict(E=float(energy), Q=float(2*frequency*norm),
                virial_relative=float(abs((dimension-2)*grad+dimension*(pot-frequency**2*norm))/energy),
                quadrature_order=order, input_sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest())

def independent_wall(dx, length=24):
    """Fix translation at f(0)=sqrt(s0/2); retain and test the omitted residual."""
    s0=(a+1)*(np.sqrt((a+1)/a)-1)
    mu2=1+a*s0-g*g*s0/(2*(mass*mass+h*s0))
    n=int(round(2*length/dx)); n += n % 2
    x=np.linspace(-length,length,n+1); dx=x[1]-x[0]
    f=np.sqrt(s0/(1+np.exp(2*np.sqrt(1-mu2)*x)))
    z=-g*f*f/(mass*mass+h*f*f)
    ends=np.array([np.sqrt(s0),0.,-g*s0/(mass*mass+h*s0),0.])
    f[0],f[-1],z[0],z[-1]=ends
    size=n-1; mid=n//2-1
    lap=diags([-np.ones(size-1),2*np.ones(size),-np.ones(size-1)],[-1,0,1],format='csc')/dx**2
    boundary_f=np.zeros(size); boundary_z=np.zeros(size)
    boundary_f[0]=ends[0]/dx**2; boundary_z[0]=ends[2]/dx**2
    def residual(u,v,pin=True):
        rf=lap@u-boundary_f+(1-mu2+2*a*u*u+g*v+h*v*v/2)*u
        rz=lap@v-boundary_z+(mass*mass+h*u*u)*v+g*u*u
        if pin: rf[mid]=u[mid]-np.sqrt(s0/2)
        return np.r_[rf,rz]
    last_step=0
    for it in range(35):
        u,v=f[1:-1],z[1:-1]; res=residual(u,v)
        if np.linalg.norm(res,np.inf)<2e-10: break
        j=bmat([[lap+diags(1-mu2+6*a*u*u+g*v+h*v*v/2),diags(u*(g+h*v))],
                [diags(2*u*(g+h*v)),lap+diags(mass*mass+h*u*u)]],format='lil')
        j[mid,:]=0; j[mid,mid]=1
        step=spsolve(j.tocsc(),-res); scale=1.
        while scale>1/1024:
            test=residual(u+scale*step[:size],v+scale*step[size:])
            if np.linalg.norm(test)<np.linalg.norm(res): break
            scale/=2
        f[1:-1]+=scale*step[:size]; z[1:-1]+=scale*step[size:]
        last_step=float(np.max(abs(scale*step)))
    else: raise RuntimeError('Newton de pared no converge')
    W=potential(f,z)-mu2*f*f
    gradient=np.sum(np.diff(f)**2+.5*np.diff(z)**2)/dx
    tension=gradient+np.trapezoid(W,x=x)
    full=residual(f[1:-1],z[1:-1],False)
    row=dict(dx=float(dx),length=length,iterations=it,last_step=last_step,tension=float(tension),
             nonlinear_residual=float(np.max(abs(res))),pin_equation_residual=float(full[mid]),
             translation_condition='f(0)=sqrt(s0/2); omit one f equation and report its residual',
             mu2=float(mu2))
    np.savetxt(OUT/f'pared_FD_h{dx:.4f}_L{length}.csv',np.c_[x,f,z],delimiter=',',header='x,f,z',comments='')
    return row

def finite_elements(path,dimension,n,radius,ell=0,axial_k=0,omega=.9):
    """Weak form in original radial amplitudes, no r*q transformation."""
    _,f,z=profile(path)
    nodes=np.linspace(0,radius,n+1); dx=radius/n
    gauss,wg=leggauss(5); basis=np.array([(1-gauss)/2,(1+gauss)/2])
    rows=[];cols=[];data=[[] for _ in range(6)]
    for cell in range(n):
        r=nodes[cell]+dx*(gauss+1)/2
        weight=wg*dx/2*r**(dimension-1)
        s=f(r)**2; mediator=z(r)
        phase=1-omega*omega+2*a*s+g*mediator+h*mediator**2/2
        vals=[np.ones_like(r),phase+4*a*s+axial_k**2,phase+axial_k**2,
              mass*mass+h*s+axial_k**2,np.sqrt(2)*f(r)*(g+h*mediator)]
        cent=ell*(ell+1)/r**2 if dimension==3 else np.zeros_like(r)
        for i in range(2):
            for j in range(2):
                rows.append(cell+i);cols.append(cell+j)
                prod=basis[i]*basis[j]
                for k in range(5):data[k].append(float(np.dot(weight,prod*vals[k])))
                deriv=(1 if i==j else -1)/dx**2
                data[5].append(float(np.dot(weight,np.full_like(r,deriv)+cent*prod)))
    # Outer Dirichlet. For spherical ell=2 regularity imposes q(0)=0.
    keep=np.arange(1 if dimension==3 and ell>0 else 0,n)
    mat=[]
    for values in data:
        mat.append(coo_matrix((values,(rows,cols)),shape=(n+1,n+1)).tocsc()[keep,:][:,keep])
    mass_matrix,pu,pv,pc,coupling,stiff=mat
    lu,lv,lc=stiff+pu,stiff+pv,stiff+pc
    N=len(keep); zero=csc_matrix((N,N))
    hessian=bmat([[lu,zero,coupling],[zero,lv,zero],[coupling,zero,lc]],format='csc')
    inertia=bmat([[mass_matrix,zero,zero],[zero,mass_matrix,zero],[zero,zero,mass_matrix]],format='csc')
    gyro=bmat([[zero,-2*omega*mass_matrix,zero],[2*omega*mass_matrix,zero,zero],[zero,zero,zero]],format='csc')
    A=bmat([[csc_matrix((3*N,3*N)),eye(3*N)],[-hessian,-gyro]],format='csc').astype(complex)
    B=bmat([[eye(3*N),None],[None,inertia]],format='csc').astype(complex)
    shift=.044j if dimension==3 else .016+0j
    eigenvectors_count=6
    ev,vec=eigs(A,M=B,k=eigenvectors_count,sigma=shift,tol=1e-11,
                v0=np.cos(np.arange(6*N)*.23).astype(complex),maxiter=5000)
    j=int(np.argmin(abs(ev-.044j))) if dimension==3 else int(np.argmax(ev.real))
    v=vec[:,j]; residual=np.linalg.norm(A@v-ev[j]*(B@v))/(np.linalg.norm(A@v)+abs(ev[j])*np.linalg.norm(B@v))
    return dict(n=n,radius=radius,h=dx,ell=ell,k=axial_k,eigenvalue=[float(ev[j].real),float(ev[j].imag)],
                rate=float(ev[j].imag if dimension==3 else ev[j].real),relative_algebraic_residual=float(residual),
                selected_eigenvalues=[[float(q.real),float(q.imag)] for q in ev])

def extrapolate(rows,key,step_key):
    a1,b1=rows[-2:]; factor=(a1[step_key]/b1[step_key])**2
    return float((factor*b1[key]-a1[key])/(factor-1))

def run():
    measures={}
    for label,path,d in [('sphere','validacion/m2_perfil_convergente.csv',3),('tube','validacion/m2_guia_perfil.csv',2)]:
        measures[label]=[integrals(path,d,order=q) for q in [4,8]]
    walls=[independent_wall(dx) for dx in [.12,.06,.03]]
    wall_domain=independent_wall(.06,length=32)
    spectra={}
    for label,path,d,ell,k in [('sphere','validacion/m2_perfil_convergente.csv',3,2,0),('tube','validacion/m2_guia_perfil.csv',2,0,.15)]:
        spectra[label]=[finite_elements(path,d,n,40.,ell,k) for n in [250,500,1000]]
        spectra[label].append(finite_elements(path,d,1250,50.,ell,k))
    original_sphere=json.loads((ROOT/'validacion/cierre_m2.json').read_text())
    original_tube=json.loads((ROOT/'validacion/guia_m2.json').read_text())
    original_wall=json.loads((ROOT/'validacion/capilaridad/resultados.json').read_text())
    reference_sphere=[s for s in original_sphere['spectra'] if s['ell']==2 and s['radius']==40]
    old_s=[dict(h=s['dx'],rate=min(abs(v['imag']) for v in s['selected_generator_eigenvalues'])) for s in reference_sphere]
    old_t=[dict(h=s['dx'],rate=next(v['growth'] for v in s['growth_samples'] if abs(v['k']-.15)<1e-12)) for s in original_tube['spectral_convergence'] if s['radius']==30]
    comparison={
        'sphere_E_relative':abs(measures['sphere'][-1]['E']/original_sphere['field_convergence'][-1]['Ehat']-1),
        'sphere_Q_relative':abs(measures['sphere'][-1]['Q']/original_sphere['field_convergence'][-1]['Qhat']-1),
        'tube_E_relative':abs(measures['tube'][-1]['E']/original_tube['background_convergence'][-1]['energy_per_length']-1),
        'tube_Q_relative':abs(measures['tube'][-1]['Q']/original_tube['background_convergence'][-1]['charge_per_length']-1),
        'wall_relative':abs(extrapolate(walls,'tension','dx')/original_wall['tension']-1),
        'wall_domain_relative':abs(wall_domain['tension']/walls[1]['tension']-1),
        'sphere_mode_relative':abs(extrapolate(spectra['sphere'][:3],'rate','h')/extrapolate(old_s,'rate','h')-1),
        'tube_growth_relative':abs(extrapolate(spectra['tube'][:3],'rate','h')/extrapolate(old_t,'rate','h')-1)}
    # Registered before execution: much smaller than the physical margins.
    limits={k:1e-8 for k in comparison}
    limits.update(wall_relative=2e-7,wall_domain_relative=2e-7,sphere_mode_relative=2e-5,tube_growth_relative=2e-5)
    checks={k:comparison[k]<limits[k] for k in comparison}
    for label in spectra:
        rows=spectra[label]
        checks[label+'_h2_convergence']=2.8<abs((rows[0]['rate']-rows[1]['rate'])/(rows[1]['rate']-rows[2]['rate']))<5.2
        checks[label+'_box_convergence']=abs(rows[3]['rate']/rows[2]['rate']-1)<2e-6
        checks[label+'_relative_residual']=max(s['relative_algebraic_residual'] for s in rows)<2e-6
    result=dict(schema_version='1.0.0',model_version='M2',stage='E00',
                environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                independence='No project imports; P1 finite elements with consistent mass vs historical FD/FV; FD Newton wall vs collocation; independent integrals on shared profile data.',
                measures=measures,walls=walls,wall_domain=wall_domain,spectra=spectra,
                comparison=comparison,limits=limits,checks=checks,passed=all(checks.values()),
                continuum_certified=False,device_validated=False)
    (OUT/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(comparison=comparison,checks=checks,passed=result['passed']),indent=2),flush=True)
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':run()
