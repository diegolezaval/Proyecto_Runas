"""Convergencia del fondo, Hessianos y modos del MISMO M2.
Los autovalores en coma flotante no son una certificación por intervalos.
Ejecutar OPENBLAS_NUM_THREADS=1 python herramientas/cierre_m2.py
"""
import json,sys,platform
import numpy as np
import scipy
from scipy.sparse import diags,bmat,eye,csc_matrix
from scipy.sparse.linalg import eigsh,eigs,splu,LinearOperator
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq
from scipy.integrate import quad
from m2_comun import ROOT,RATIO,M,G,H,solve,measures,ueff,up,upp
from geometria import segments

def low(operator,k=4,lower=-2,inv=None):
    n=operator.shape[0]
    vals,vec=eigsh(operator,k=k,sigma=lower,which='LM',tol=2e-11,
                   v0=np.sin(np.arange(n)+.2),OPinv=inv)
    order=np.argsort(vals);vals=vals[order];vec=vec[:,order]
    residual=[np.linalg.norm(operator@vec[:,j]-vals[j]*vec[:,j]) for j in range(k)]
    return vals,residual

def spectrum(background,n,radius,ell,omega=.9,dynamics=True):
    dx=radius/(n+1);x=dx*np.arange(1,n+1)
    f,fp,z,zp=background.sol(x)
    off=-np.ones(n-1)/dx**2
    lap=diags([off,2*np.ones(n)/dx**2+ell*(ell+1)/x**2,off],[-1,0,1],format='csc')
    vv=1+2*RATIO*f*f+G*z+.5*H*z*z-omega*omega
    uu=vv+4*RATIO*f*f;zz=M*M+H*f*f;coupling=np.sqrt(2)*f*(G+H*z)
    lv=lap+diags(vv);lu=lap+diags(uu);lc=lap+diags(zz);c=diags(coupling)
    amp=bmat([[lu,c],[c,lc]],format='csc')
    # Pointwise 2x2 potential minimum is a lower bound for the Dirichlet operator.
    lower=float(np.min(.5*(uu+zz-np.sqrt((uu-zz)**2+4*coupling**2))))-1
    av,ares=low(amp,lower=lower)
    pv=eigh_tridiagonal(lv.diagonal(),off,select='i',select_range=(0,3))[0]
    result=dict(n=n,radius=radius,dx=dx,ell=ell,H_amplitude=av.tolist(),
                H_phase=pv.tolist(),amplitude_eigen_residual_max=float(max(ares)),
                analytic_lower_bound=lower+1)
    if ell==0:
        v=np.r_[x*f,np.zeros(n)];v/=np.linalg.norm(v)
        beta=4*omega**2
        def matvec(a):return amp@a+beta*v*np.dot(v,a)
        def matmat(a):return amp@a+beta*v[:,None]*(v@a)[None,:]
        constrained=LinearOperator(amp.shape,matvec=matvec,matmat=matmat,dtype=float)
        lu_shift=splu(amp-lower*eye(2*n,format='csc'));ainvv=lu_shift.solve(v)
        den=1+beta*np.dot(v,ainvv)
        def invvec(a):
            t=lu_shift.solve(a)
            return t-beta*ainvv*np.dot(v,t)/den
        inverse=LinearOperator(amp.shape,matvec=invvec,dtype=float)
        kv,kres=low(constrained,lower=lower,inv=inverse)
        result['H_fixed_charge']=kv.tolist();result['constrained_residual_max']=float(max(kres))
    if dynamics:
        ident=eye(n,format='csc');zero=csc_matrix((n,n))
        hess=bmat([[lu,zero,c],[zero,lv,zero],[c,zero,lc]],format='csc')
        gyro=bmat([[zero,-2*omega*ident,zero],[2*omega*ident,zero,zero],[zero,zero,zero]],format='csc')
        dynam=bmat([[csc_matrix((3*n,3*n)),eye(3*n)],[-hess,-gyro]],format='csc').astype(complex)
        vals,vec=eigs(dynam,k=18,sigma=.055j,which='LM',tol=2e-10,
                      v0=np.cos(np.arange(6*n)+.17).astype(complex),maxiter=8000)
        order=np.argsort(np.abs(vals));vals=vals[order];vec=vec[:,order]
        residuals=[float(np.linalg.norm(dynam@vec[:,j]-vals[j]*vec[:,j])) for j in range(len(vals))]
        result['selected_generator_eigenvalues']=[{'real':float(v.real),'imag':float(v.imag)} for v in vals]
        result['dynamic_residual_max']=max(residuals)
        result['dynamic_scope']='18 autovalores proximos al desplazamiento 0.055i; no barrido exhaustivo del generador.'
    return result

def homogeneous():
    s0=(RATIO+1)*(np.sqrt((RATIO+1)/RATIO)-1)
    spinodal=brentq(upp,.1,.5)
    cs=lambda s:s*upp(s)/(s*upp(s)+2*up(s))
    ss=brentq(lambda s:cs(s)-(1e7/299792458.)**2,spinodal+1e-9,s0)
    def entry(s):
        pressure=s*up(s)-ueff(s);rho=s*up(s)+ueff(s)
        return dict(s=float(s),f=float(np.sqrt(s)),z=float(-G*s/(M*M+H*s)),
                    omega=float(np.sqrt(up(s))),pressure=float(pressure),rho=float(rho),
                    pressure_over_rho=float(pressure/rho),cs_over_c=float(np.sqrt(max(0,cs(s)))),
                    cs_m_s=float(299792458.*np.sqrt(max(0,cs(s)))))
    # All three homogeneous branches: x=Omega^2 from the exact cubic.
    dispersion=[]
    s=s0;omega=np.sqrt(up(s));z=-G*s/(M*M+H*s);cc=2*s*(G+H*z)**2
    for k in np.r_[0,np.geomspace(1e-4,1000,160)]:
        a=k*k+4*RATIO*s;b=k*k+M*M+H*s
        p=np.polymul([1,-(a+k*k+4*omega*omega),a*k*k],[-1,b])
        p[-2]+=cc;p[-1]-=cc*k*k
        raw_roots=np.roots(p)
        if np.max(abs(raw_roots.imag))>1e-8:raise ArithmeticError('Ramas homogeneas complejas no esperadas en este fondo')
        roots=np.sort(raw_roots.real)
        dispersion.append([float(k)]+[float(v) for v in roots])
    return {'zero_pressure':entry(s0),'spinodal_s':float(spinodal),
            'state_matching_R1_speed_only':entry(ss),'dispersion_columns':['k','Omega2_1','Omega2_2','Omega2_3'],
            'dispersion':dispersion}

def geometry_lengths():
    geo=json.loads((ROOT/'datos/geometria.json').read_text())
    out={}
    for r in geo['runes']:
        ls=[]
        for name,seg in segments(geo,r):
            p=np.array([[float(y) for y in x] for x in seg])
            if len(p)==2:length=float(np.linalg.norm(p[1]-p[0]))
            else:
                length=quad(lambda t:np.linalg.norm(3*(1-t)**2*(p[1]-p[0])+6*t*(1-t)*(p[2]-p[1])+3*t*t*(p[3]-p[2])),0,1,epsabs=1e-12)[0]
            ls.append({'piece':name,'length_graphic_units':length})
        out[r['id']]={'projected_total_length_graphic_units':sum(x['length_graphic_units'] for x in ls),'segments':ls}
    # P04 main path excludes the N control branch 0 -> endpoint 2.
    r=next(x for x in geo['runes'] if x['id']=='P-04')
    out['P-04']['main_path_A_B_graphic_units']=sum(x['length_graphic_units'] for j,x in enumerate(out['P-04']['segments']) if j!=1)
    L=out['P-04']['main_path_A_B_graphic_units']*.01
    out['P-04']['R1_planar_length_m']=L
    out['P-04']['R1_desired_bulk_transmission']=float(np.exp(-1e-4*L))
    out['P-04']['open_equal_lead_graph_power_AB']=4/9
    out['P-04']['open_equal_lead_graph_reflection_AA']=1/9
    out['P-04']['open_equal_lead_graph_power_AU']=4/9
    out['P-04']['graph_scope']='Contraste exacto condicionado al grafo ideal de tres terminales adaptados, sin paredes M2 derivadas.'
    return out

def main():
    data={'schema_version':'4.0.0','environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
          'sector':'M2 escalar clasico aislado, mismo benchmark que 3.0',
          'fundamental_dimensionless':{'lambda0_over_lambda':RATIO,'M_over_m':M,'g_over_m_sqrtlambda':G,'h_over_lambda':H},
          'new_device_specific_fundamental_parameters':[],'certified_continuum_spectral_proof':False,
          'complete_device_derived':False}
    refinements=[];bg=None
    for radius,n,tol in [(40,700,1e-6),(50,1100,1e-8),(60,1800,1e-9)]:
        bg=solve(radius=radius,n=n,tol=tol,previous=bg);d=measures(bg);d['requested_tolerance']=tol;refinements.append(d)
        print('BVP',json.dumps(d),flush=True)
    data['field_convergence']=refinements
    x=np.linspace(0,60,6001);np.savetxt(ROOT/'validacion/m2_perfil_convergente.csv',np.column_stack([x,bg.sol(x).T]),delimiter=',',header='x,f,df_dx,z,dz_dx',comments='')
    derivative=[]
    for delta in [.0004,.0002]:
        aa=measures(solve(omega=.9-delta,previous=bg),.9-delta)
        bb=measures(solve(omega=.9+delta,previous=bg),.9+delta)
        derivative.append({'delta':delta,'dQ_dw':(bb['Qhat']-aa['Qhat'])/(2*delta),'dE_dQ':(bb['Ehat']-aa['Ehat'])/(bb['Qhat']-aa['Qhat'])})
    data['branch_derivatives']=derivative
    data['spectra']=[]
    for radius,n in [(40,500),(40,1000),(40,2000),(60,3000)]:
        for ell in [0,1,2,3]:
            row=spectrum(bg,n,radius,ell,dynamics=ell<=2)
            data['spectra'].append(row)
            print('SPEC',radius,n,ell,'H',row['H_amplitude'][:2],'K',row.get('H_fixed_charge',[])[:2],flush=True)
    data['homogeneous']=homogeneous();data['geometry']=geometry_lengths()
    b=refinements[-1]
    data['numerical_checks_passed']=bool(b['virial_relative']<1e-7 and b['f0']>.1 and
        abs(refinements[-2]['Ehat']-b['Ehat'])/b['Ehat']<1e-6 and
        all(x['dQ_dw']<0 for x in derivative) and
        all(row.get('H_fixed_charge',[1])[0]>0 for row in data['spectra']) and
        all(row['H_amplitude'][0]>0 for row in data['spectra'] if row['ell']>=2))
    (ROOT/'validacion/cierre_m2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('NUMERICAL_CHECKS',data['numerical_checks_passed'])
    if not data['numerical_checks_passed']:sys.exit(1)

if __name__=='__main__':main()
