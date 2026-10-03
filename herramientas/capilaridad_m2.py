"""Interfaz y limite capilar derivados de los dos campos M2 comunes.
No ajusta tension, masa efectiva, radio ni parametros para cada geometria.
Las mallas gruesas y sus discrepancias se conservan en el resultado.
"""
from pathlib import Path
import json, platform, hashlib
import numpy as np
import scipy
from scipy.integrate import solve_bvp, simpson, quad, cumulative_trapezoid
from scipy.optimize import brentq
from scipy.sparse import diags, bmat, eye, csc_matrix
from scipy.sparse.linalg import eigsh, eigs
from scipy.special import iv
from m2_comun import ROOT, RATIO, M, G, H, potential, ueff, up, upp
from guia_m2 import operators as tube_operators

CFG=json.loads((ROOT/'datos/ensayo_capilaridad.json').read_text())
OUT=ROOT/'validacion/capilaridad'
S0=brentq(lambda s:s*up(s)-ueff(s),.4,.6,xtol=1e-14)
MU0=np.sqrt(up(S0)); F0=np.sqrt(S0); Z0=-G*S0/(M*M+H*S0)
ENTHALPY0=2*MU0*MU0*S0

def dump(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def wall(L,n,tol,old=None):
    x=np.linspace(-L,L,n); decay=np.sqrt(1-MU0*MU0)
    f=F0/np.sqrt(1+np.exp(2*decay*x)); fp=-decay*f*(1-f*f/S0)
    z=-G*f*f/(M*M+H*f*f); zp=-2*G*M*M*f*fp/(M*M+H*f*f)**2
    y=np.array([f,fp,z,zp,np.zeros_like(x)]) if old is None else old.sol(x)
    def fun(x,y,p):
        f,fp,z,zp,phase=y
        ref=F0/np.sqrt(1+np.exp(2*decay*x)); refp=-decay*ref*(1-ref*ref/S0)
        return np.array([fp,(1-p[0]+2*RATIO*f*f+G*z+.5*H*z*z)*f,
                         zp,M*M*z+G*f*f+H*z*f*f,(f-ref)*refp])
    bg=solve_bvp(fun,lambda a,b,p:np.array([a[0]-F0,a[2]-Z0,b[0],b[2],a[4],b[4]]),
                 x,y,p=[MU0*MU0],tol=tol,max_nodes=50000)
    if not bg.success: raise RuntimeError(bg.message)
    x=np.linspace(-L,L,20001); f,fp,z,zp,j=bg.sol(x)
    W=potential(f,z)-MU0*MU0*f*f; T=fp*fp+.5*zp*zp
    row=dict(L=L,initial_n=n,tolerance=tol,nodes=int(bg.x.size),
             tension=float(simpson(T+W,x=x)),tension_from_stress=float(simpson(2*T,x=x)),
             first_integral_max=float(np.max(abs(T-W))),mu_squared_shift=float(bg.p[0]-MU0*MU0),
             phase_condition_residual=float(max(abs(j[0]),abs(j[-1]))),
             collocation_residual=float(max(bg.rms_residuals)))
    return bg,row

def wall_bounds():
    # Exact factorisation for the benchmark; verified numerically in the report.
    A=RATIO*H/(M*M)
    W=lambda f:A*f*f*(f*f-S0)**2/(1+H*f*f/(M*M))
    Z=lambda f:1+2*f*f*(G*M*M/(M*M+H*f*f)**2)**2
    lo=quad(lambda f:2*np.sqrt(W(f)),0,F0,epsabs=1e-13)[0]
    hi=quad(lambda f:2*np.sqrt(Z(f)*W(f)),0,F0,epsabs=1e-13)[0]
    grid=np.linspace(0,F0,1001)
    return dict(lower=float(lo),adiabatic_trial_upper=float(hi),
                factorisation_error=float(np.max(abs(ueff(grid**2)-MU0**2*grid**2-W(grid)))),
                scope='Cotas del infimo global de tension. El perfil estacionario numerico no certifica por si solo ese infimo.')

def radial_state(norm_radius,dimension,tension,extra_radius=30,initial_dx=.1,tol=1e-8):
    d=dimension; RN=norm_radius; L=RN+extra_radius
    x=np.linspace(0,L,max(600,int(np.ceil(L/initial_dx))))
    p0=MU0*MU0+(d-1)*tension/(S0*RN)
    s=brentq(lambda s:up(s)-p0,S0,1.5)
    radius=RN*(S0/s)**(1/d); decay=np.sqrt(1-MU0*MU0)
    f=np.sqrt(s)/np.sqrt(1+np.exp(2*decay*(x-radius))); fp=-decay*f*(1-f*f/s)
    z=-G*f*f/(M*M+H*f*f); zp=-2*G*M*M*f*fp/(M*M+H*f*f)**2
    nf=d/(S0*RN**d); j=cumulative_trapezoid(nf*x**(d-1)*f*f,x,initial=0)
    def fun(x,y,p):
        f,fp,z,zp,j=y
        return np.array([fp,(1-p[0]+2*RATIO*f*f+G*z+.5*H*z*z)*f,
                         zp,M*M*z+G*f*f+H*z*f*f,nf*x**(d-1)*f*f])
    def jac(x,y,p):
        f,fp,z,zp,j=y; a=np.zeros((5,5,x.size)); b=np.zeros((5,1,x.size))
        a[0,1]=1; a[2,3]=1
        a[1,0]=1-p[0]+6*RATIO*f*f+G*z+.5*H*z*z; a[1,2]=(G+H*z)*f
        a[3,0]=2*f*(G+H*z); a[3,2]=M*M+H*f*f
        a[4,0]=2*nf*x**(d-1)*f; b[1,0]=-f
        return a,b
    bg=solve_bvp(fun,lambda a,b,p:np.array([a[1],a[3],b[0],b[2],a[4],b[4]-1]),
                 x,np.array([f,fp,z,zp,j]),p=[p0],S=np.diag([0.,1-d,0.,1-d,0.]),
                 fun_jac=jac,tol=tol,max_nodes=50000)
    if not bg.success: raise RuntimeError((RN,d,bg.message))
    if bg.y[0,0]<.1: raise RuntimeError('Convergencia trivial')
    w=np.sqrt(bg.p[0]); s=brentq(lambda s:up(s)-w*w,S0,1.5)
    pressure=w*w*s-ueff(s)
    x=np.linspace(0,L,32001); f,fp,z,zp,j=bg.sol(x); sd=2*np.pi if d==2 else 4*np.pi
    integ=lambda v:float(sd*simpson(x**(d-1)*v,x=x))
    I=integ(f*f); Q=2*w*I; T=integ(fp*fp+.5*zp*zp); U=integ(potential(f,z)); E=w*w*I+T+U
    Req=(d*I/(sd*s))**(1/d); Rq=(d*Q/(sd*2*MU0*S0))**(1/d)
    # Exact curved-interface stress balance; origin limit is zero by regularity.
    W=potential(f,z)-w*w*f*f; Trr=fp*fp+.5*zp*zp-W
    anisotropy=2*fp*fp+zp*zp
    rhs=(d-1)*simpson(np.divide(anisotropy,x,out=np.zeros_like(x),where=x!=0),x=x)
    row=dict(dimension=d,norm_radius=RN,domain=L,initial_dx=initial_dx,tolerance=tol,
             nodes=int(bg.x.size),omega=float(w),bulk_s=float(s),bulk_pressure=float(pressure),
             equimolar_radius=float(Req),charge_radius=float(Rq),I=I,Q=float(Q),E=float(E),
             virial_relative=float(abs((d-2)*T+d*(U-w*w*I))/E),
             norm_relative=float(abs(I/(sd*S0*RN**d/d)-1)),
             stress_balance_relative=float(abs(Trr[0]-Trr[-1]-rhs)/max(abs(Trr[0]),1e-12)),
             center_pressure=float(Trr[0]),boundary_stress=float(Trr[-1]),
             laplace_ratio=float(pressure*Req/((d-1)*tension)),
             energy_excess_ratio=float((E-MU0*Q)/(sd*tension*Rq**(d-1))),
             collocation_residual=float(max(bg.rms_residuals)))
    return bg,row

class FourFields:
    def __init__(self,bg): self.bg=bg; self.x=bg.x
    def sol(self,x): return self.bg.sol(x)[:4]

def operators(bg,dimension,dx,omega,ell=2):
    L=bg.x[-1]; n=int(np.ceil(L/dx))
    if dimension==2: return tube_operators(FourFields(bg),n=n,radius=L,omega=omega)
    h=L/(n+1); r=h*np.arange(1,n+1); f,fp,z,zp=bg.sol(r)[:4]
    off=-np.ones(n-1)/h**2
    lap=diags([off,2/h**2+ell*(ell+1)/r**2,off],[-1,0,1],format='csc')
    lv=lap+diags(1+2*RATIO*f*f+G*z+.5*H*z*z-omega*omega)
    return lv+diags(4*RATIO*f*f),lv,lap+diags(M*M+H*f*f),diags(np.sqrt(2)*f*(G+H*z)),h

def spectrum(bg,dimension,dx,omega,k=0,ell=2):
    lu,lv,lc,cc,h=operators(bg,dimension,dx,omega,ell); n=lu.shape[0]
    I=eye(n,format='csc'); Z=csc_matrix((n,n))
    hess=bmat([[lu+k*k*I,Z,cc],[Z,lv+k*k*I,Z],[cc,Z,lc+k*k*I]],format='csc')
    gyro=bmat([[Z,-2*omega*I,Z],[2*omega*I,Z,Z],[Z,Z,Z]],format='csc')
    gen=bmat([[csc_matrix((3*n,3*n)),eye(3*n)],[-hess,-gyro]],format='csc')
    vals,vec=eigs(gen,k=6,sigma=0,which='LM',tol=1e-10,
                  v0=np.sin(np.arange(6*n)+.21),maxiter=5000)
    j=int(np.argmax(vals.real) if dimension==2 else np.argmin(np.where(vals.imag>0,abs(vals),np.inf)))
    v=vals[j]; rate=float(v.real if dimension==2 else v.imag)
    row=dict(dx=float(h),requested_dx=dx,n=n,k=float(k),ell=0 if dimension==2 else ell,
             eigenvalue=[float(v.real),float(v.imag)],rate=rate,
             residual=float(np.linalg.norm(gen@vec[:,j]-v*vec[:,j])),
             selected_eigenvalues=[[float(q.real),float(q.imag)] for q in vals])
    if dimension==2:
        # Laplacian is nonnegative. Bound pointwise potential BEFORE shift-invert
        # so the eigenvalues requested really are the bottom of the amplitude Hessian.
        r=(np.arange(n)+.5)*h; f,fp,z,zp=bg.sol(r)[:4]
        a=1+6*RATIO*f*f+G*z+.5*H*z*z-omega*omega
        b=M*M+H*f*f; c=np.sqrt(2)*f*(G+H*z)
        bound=float(np.min(.5*(a+b-np.sqrt((a-b)**2+4*c*c))))
        amp=bmat([[lu,cc],[cc,lc]],format='csc')
        av,ae=eigsh(amp,k=2,sigma=bound-1,which='LM',tol=1e-11,
                     v0=np.sin(np.arange(2*n)+.4))
        index=int(np.argmin(av)); amin=float(av[index])
        row.update(amplitude_lowest=amin,amplitude_lower_bound=bound,
                   amplitude_residual=float(np.linalg.norm(amp@ae[:,index]-amin*ae[:,index])),
                   kcrit=float(np.sqrt(-amin)) if amin<0 else 0.)
    return row

def extrapolate(rows,key,squared=True):
    def extrap(a,b):
        va=a[key]**2 if squared else a[key]; vb=b[key]**2 if squared else b[key]
        return (a['dx']**2*vb-b['dx']**2*va)/(a['dx']**2-b['dx']**2)
    x=extrap(rows[-2],rows[-1]); previous=extrap(rows[-3],rows[-2])
    val=float(np.sqrt(x)) if squared else float(x)
    prev=float(np.sqrt(previous)) if squared else float(previous)
    return dict(value=val,previous=prev,relative_sequence_difference=abs(val/prev-1),
                method='Richardson lineal en dx^2 del autovalor cuadrado; error estimado, no cota certificada')

def run():
    OUT.mkdir(exist_ok=True)
    walls=[]; bg=None
    for case in CFG['wall_runs']:
        bg,row=wall(**case,old=bg); walls.append(row); print('WALL',row,flush=True)
    x=np.linspace(-CFG['wall_runs'][-1]['L'],CFG['wall_runs'][-1]['L'],7201)
    np.savetxt(OUT/'pared.csv',np.column_stack([x,bg.sol(x)[:4].T]),delimiter=',',
               header='x,f,df_dx,z,dz_dx',comments='')
    tension=walls[-1]['tension']; states=[]; spectra=[]; backgrounds={}
    for d in CFG['dimensions']:
        for RN in CFG['norm_radii']:
            bg,row=radial_state(RN,d,tension,**CFG['background'])
            states.append(row); backgrounds[(d,RN)]=(bg,row)
            x=np.linspace(0,bg.x[-1],int(bg.x[-1]*100)+1)
            np.savetxt(OUT/f'perfil_d{d}_RN{RN}.csv',np.column_stack([x,bg.sol(x)[:4].T]),delimiter=',',
                       header='r,f,df_dr,z,dz_dr',comments='')
            print('STATE',row,flush=True)
            if RN not in CFG['spectrum_radii']: continue
            radius=row['equimolar_radius']; xk=CFG['tube_kR']; ell=CFG['sphere_ell']
            coefficient=ell*(ell-1)*(ell+2) if d==3 else xk*(1-xk*xk)*iv(1,xk)/iv(0,xk)
            predicted=np.sqrt(tension/(ENTHALPY0*radius**3)*coefficient)
            samples=[]
            for dx in CFG['spectrum_dx']:
                sample=spectrum(bg,d,dx,row['omega'],k=xk/radius if d==2 else 0,ell=ell)
                samples.append(sample); print('SPECTRUM',d,RN,dx,sample['rate'],flush=True)
            extra=extrapolate(samples,'rate'); kr=extrapolate(samples,'kcrit') if d==2 else None
            spectra.append(dict(dimension=d,norm_radius=RN,equimolar_radius=radius,
                prediction=float(predicted),samples=samples,rate_extrapolation=extra,
                relative_prediction_error=float(extra['value']/predicted-1),
                kcrit_extrapolation=kr,kcrit_R=None if kr is None else kr['value']*radius))
    domain=[]; dc=CFG['domain_check']
    for d in CFG['dimensions']:
        bg,row=radial_state(dc['norm_radius'],d,tension,extra_radius=dc['extra_radius'],
                           initial_dx=dc['initial_dx'],tol=dc['tol'])
        reference=backgrounds[(d,dc['norm_radius'])][1]
        # Compare at the SAME physical k and omega solved in each box.
        sample=spectrum(bg,d,dc['spectral_dx'],row['omega'],
                        k=CFG['tube_kR']/reference['equimolar_radius'] if d==2 else 0,
                        ell=CFG['sphere_ell'])
        original=next(r for r in spectra if r['dimension']==d and r['norm_radius']==dc['norm_radius'])
        previous=next(r for r in original['samples'] if r['requested_dx']==dc['spectral_dx'])
        # For spheres h=L/(n+1) differs slightly: correct only the measured O(h^2) bias.
        slope=(original['samples'][-2]['rate']**2-original['samples'][-1]['rate']**2)/(original['samples'][-2]['dx']**2-original['samples'][-1]['dx']**2)
        expected2=previous['rate']**2+slope*(sample['dx']**2-previous['dx']**2)
        domain.append(dict(dimension=d,background=row,spectrum=sample,
              E_relative_difference=abs(row['E']/reference['E']-1),
              omega_relative_difference=abs(row['omega']/reference['omega']-1),
              spectral_relative_difference=abs(sample['rate']/previous['rate']-1),
              spectral_relative_difference_same_h_estimate=abs(sample['rate']/np.sqrt(expected2)-1)))
    first_laws=[]
    for d in CFG['dimensions']:
        RN=CFG['domain_check']['norm_radius']; reference=backgrounds[(d,RN)][1]
        for delta in [.016,.008]:
            minus=radial_state(RN-delta,d,tension,**CFG['background'])[1]
            plus=radial_state(RN+delta,d,tension,**CFG['background'])[1]
            slope=(plus['E']-minus['E'])/(plus['Q']-minus['Q'])
            dq_dw=(plus['Q']-minus['Q'])/(plus['omega']-minus['omega'])
            first_laws.append(dict(dimension=d,norm_radius=RN,delta=delta,
                dE_dQ=slope,omega=reference['omega'],relative_error=abs(slope/reference['omega']-1),
                dQ_domega=dq_dw,
                cL_squared=None if d==3 else reference['Q']/(reference['omega']*dq_dw),
                capillary_cL_squared=None if d==3 else -tension/(2*ENTHALPY0*reference['equimolar_radius'])))
    bounds=wall_bounds()
    report=dict(schema_version='4.1.0',environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        theta_sha256=hashlib.sha256((ROOT/'datos/theta_comun.json').read_bytes()).hexdigest(),
        configuration=CFG,coexistence=dict(s=S0,omega=MU0,z=Z0,number_density=2*MU0*S0,
             enthalpy_density=ENTHALPY0,sound_speed_squared=S0*upp(S0)/(2*MU0*MU0+S0*upp(S0))),
        wall_convergence=walls,variational_bounds=bounds,tension=tension,radial_family=states,
        spectra=spectra,domain_check=domain,first_laws=first_laws,
        new_fundamental_parameters=[],fitted_macroscopic_parameters=[],
        capillary_limit_numerically_supported=True,continuum_error_certified=False,
        full_nonlinear_shape_stability_proved=False,preparation_demonstrated=False,
        complete_device_derived=False,
        scope='Contraste de soluciones y modos lineales del sector clasico aislado. No medida experimental ni realizacion de R1.')
    dump(OUT/'resultados.json',report)
    print('CAPILLARITY_DONE',tension,flush=True)

if __name__=='__main__': run()
