"""Guía autosostenida M2: Q-tubo, sin paredes ni parámetros fundamentales nuevos.
Resuelve el perfil cilíndrico, el espectro longitudinal y la respuesta de un
semiespacio exterior de vacío. Esta última no sustituye a una solución del capuchón.
"""
import json
import numpy as np
from scipy.integrate import solve_bvp,simpson
from scipy.sparse import diags,bmat,eye,csc_matrix
from scipy.sparse.linalg import eigsh,eigs
from m2_comun import ROOT,RATIO,M,G,H,potential,up

def tube(omega=.9,radius=40,n=1000,tol=1e-8,previous=None):
    x=np.linspace(0,radius,n)
    if previous is None:
        base=np.loadtxt(ROOT/'validacion/m2_perfil_convergente.csv',delimiter=',',skiprows=1)
        f=np.interp(x,base[:,0],base[:,1],right=0)
        fp=np.interp(x,base[:,0],base[:,2],right=0)
        seed=np.vstack([f,fp])
        # El potencial adiabático sólo inicializa Newton. Todos los resultados
        # publicados usan después las DOS ecuaciones completas, sin eliminar chi.
        for dimension in np.linspace(3,2,11):
            reduced=solve_bvp(lambda x,y:np.vstack([y[1],(up(y[0]**2)-omega*omega)*y[0]]),
                     lambda a,b:np.array([a[1],b[0]]),x,seed,
                     S=np.diag([0.,1-dimension]),tol=1e-7,max_nodes=20000)
            if not reduced.success:raise RuntimeError('Fallo del inicializador: '+reduced.message)
            seed=reduced.sol(x)
        f,fp=seed
        z=-G*f*f/(M*M+H*f*f);zp=-2*G*M*M*f/(M*M+H*f*f)**2*fp
        y=np.vstack([f,fp,z,zp])
    else:y=previous.sol(x)
    def fun(x,y):
        f,fp,z,zp=y
        return np.vstack([fp,(1-omega*omega+2*RATIO*f*f+G*z+.5*H*z*z)*f,zp,M*M*z+G*f*f+H*z*f*f])
    def jac(x,y):
        f,fp,z,zp=y;j=np.zeros((4,4,x.size));j[0,1]=1;j[2,3]=1
        j[1,0]=1-omega*omega+6*RATIO*f*f+G*z+.5*H*z*z
        j[1,2]=(G+H*z)*f;j[3,0]=2*f*(G+H*z);j[3,2]=M*M+H*f*f
        return j
    dimensions=[2.0]
    for dimension in dimensions:
        out=solve_bvp(fun,lambda a,b:np.array([a[1],a[3],b[0],b[2]]),x,y,
                      S=np.diag([0.,1-dimension,0.,1-dimension]),fun_jac=jac,
                      tol=tol if dimension==2 else max(tol,1e-6),max_nodes=50000)
        if not out.success:raise RuntimeError(f'd={dimension}: '+out.message)
        y=out.sol(x)
    if out.y[0,0]<.1:raise RuntimeError('Convergencia a la solucion trivial')
    return out

def tube_measures(bg,w):
    x=np.linspace(0,bg.x[-1],20001);f,fp,z,zp=bg.sol(x)
    integ=lambda y:float(2*np.pi*simpson(x*y,x=x))
    I=integ(f*f);T=integ(fp*fp+.5*zp*zp);U=integ(potential(f,z))
    return dict(radius=float(x[-1]),nodes=int(bg.x.size),omega=w,f0=float(f[0]),z0=float(z[0]),
                I=I,T=T,U=U,energy_per_length=w*w*I+T+U,charge_per_length=2*w*I,
                transverse_virial_relative=abs(U-w*w*I)/(w*w*I+T+U),
                collocation_residual=float(max(bg.rms_residuals)))

def operators(bg,n=800,radius=30.,omega=.9):
    dx=radius/n;edges=np.linspace(0,radius,n+1);r=(edges[1:]+edges[:-1])/2
    weights=np.diff(edges**2)/2
    # W^(1/2) (-Laplacian_cylindrical) W^(-1/2), regular origin.
    conduct=edges[1:-1]/dx
    diag=np.zeros(n);diag[:-1]+=conduct;diag[1:]+=conduct;diag[-1]+=2*radius/dx
    off=-conduct/np.sqrt(weights[:-1]*weights[1:])
    lap=diags([off,diag/weights,off],[-1,0,1],format='csc')
    f,fp,z,zp=bg.sol(r)
    vv=1+2*RATIO*f*f+G*z+.5*H*z*z-omega*omega
    lv=lap+diags(vv);lu=lv+diags(4*RATIO*f*f);lc=lap+diags(M*M+H*f*f)
    cc=diags(np.sqrt(2)*f*(G+H*z))
    return lu,lv,lc,cc,dx

def growth(ops,k,omega=.9):
    lu,lv,lc,cc,dx=ops;n=lu.shape[0];I=eye(n,format='csc');Z=csc_matrix((n,n))
    hess=bmat([[lu+k*k*I,Z,cc],[Z,lv+k*k*I,Z],[cc,Z,lc+k*k*I]],format='csc')
    gyro=bmat([[Z,-2*omega*I,Z],[2*omega*I,Z,Z],[Z,Z,Z]],format='csc')
    A=bmat([[csc_matrix((3*n,3*n)),eye(3*n)],[-hess,-gyro]],format='csc').astype(complex)
    # Real shift close to unstable branch, requesting both nearby branches.
    eig,vec=eigs(A,k=10,sigma=.035+0j,which='LM',tol=2e-10,maxiter=5000,
                 v0=np.cos(np.arange(6*n)+.33).astype(complex))
    j=int(np.argmax(eig.real));v=eig[j]
    residual=float(np.linalg.norm(A@vec[:,j]-v*vec[:,j]))
    return dict(k=float(k),growth=float(v.real),imaginary=float(v.imag),residual=residual,
                selected_eigenvalues=[[float(a.real),float(a.imag)] for a in eig])

def main():
    backgrounds=[];bg=None
    for radius,n,tol in [(30,700,1e-6),(40,1200,1e-8),(50,1800,1e-9)]:
        bg=tube(radius=radius,n=n,tol=tol,previous=bg);row=tube_measures(bg,.9);backgrounds.append(row)
        print('TUBE',row,flush=True)
    x=np.linspace(0,50,5001);np.savetxt(ROOT/'validacion/m2_guia_perfil.csv',np.column_stack([x,bg.sol(x).T]),delimiter=',',header='rho,f,df_drho,z,dz_drho',comments='')
    deriv=[]
    for delta in [.0004,.0002]:
        a=tube_measures(tube(omega=.9-delta,previous=bg),.9-delta)
        b=tube_measures(tube(omega=.9+delta,previous=bg),.9+delta)
        dq=(b['charge_per_length']-a['charge_per_length'])/(2*delta)
        deriv.append({'delta':delta,'dq_domega':dq,'long_wave_cL_squared':backgrounds[-1]['charge_per_length']/(.9*dq)})
    spectra=[]
    for radius,n in [(30,400),(30,800),(30,1600),(40,2133)]:
        ops=operators(bg,n,radius)
        lu,lv,lc,cc,dx=ops;A=bmat([[lu,cc],[cc,lc]],format='csc')
        vals=eigsh(A,k=3,sigma=-1,which='LM',return_eigenvectors=False,tol=1e-11,v0=np.sin(np.arange(2*n)+.7))
        vals=np.sort(vals);lvs=np.sort(eigsh(lv,k=2,sigma=-1,which='LM',return_eigenvectors=False,tol=1e-11))
        row={'radius':radius,'n':n,'dx':dx,'H_low':vals.tolist(),'Lphase_low':lvs.tolist(),
             'kcrit_from_H':float(np.sqrt(-vals[0])),'growth_samples':[growth(ops,k) for k in [.025,.075,.15,.225,.30]]}
        spectra.append(row);print('SPECTRUM',radius,n,row['H_low'],[(v['k'],v['growth']) for v in row['growth_samples']],flush=True)
    ops=operators(bg,1600,30)
    band=[growth(ops,k) for k in np.linspace(.005,1.04*spectra[-2]['kcrit_from_H'],31)]
    maxrow=max(band,key=lambda x:x['growth'])
    # Exterior vacuum channels, longitudinal momentum only. Sidebands have different cutoffs.
    vacuum=[]
    for Om in [0.,.025,.05,.075,.099,.1,.125,.2]:
        kappas=[1-(.9+Om)**2,1-(.9-Om)**2,M*M-Om**2]
        vacuum.append({'Omega':Om,'kappa_squared_phi_plus_minus_chi':kappas})
    report={'model':'M2 comun, Q-tubo recto autosostenido sin paredes externas',
       'same_fundamental_parameters_as_Qball':True,'background_convergence':backgrounds,
       'charge_derivative':deriv,'spectral_convergence':spectra,'growth_band':band,
       'largest_sampled_growth':maxrow,'exterior_vacuum':vacuum,
       'stable_free_guide_demonstrated':False,'exact_Neumann_terminal_demonstrated':False,
       'complete_P04_derived':False,
       'conclusion':'Existe un perfil transversal convergente, pero el Q-tubo presenta inestabilidad longitudinal. No realiza una guia operacional estable.',
       'scope':'Fondo de energia finita por longitud y perturbaciones Bloch axiales. No demuestra inexistencia de guias sostenidas por materia o bombeo.',
       'passed':bool(backgrounds[-1]['transverse_virial_relative']<1e-7 and deriv[-1]['long_wave_cL_squared']<0 and maxrow['growth']>.001)}
    (ROOT/'validacion/guia_m2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('GUIDE_RESULT',report['conclusion'])
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
