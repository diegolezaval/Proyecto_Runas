"""Continue CP04 with all real spherical harmonics through L and full M2 fields.

Variational radial finite volumes, exact angular quadrature of the quartic
potential, and velocity Verlet. No damping, fixed background or mediator
elimination. A finite angular truncation is not a continuum 3-D certificate.
"""
from pathlib import Path
import argparse, hashlib, json, time
import numpy as np
from scipy.special import lpmv, gammaln
from scipy.interpolate import CubicSpline
from threadpoolctl import threadpool_limits
from modelo_m2 import BENCHMARK as model

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'validacion/P06/no_radial'
SOURCE = ROOT/'validacion/P06/preparacion/w7.20_h0.100_dt0.0020_R1300_T1200_estado.npz'


def save_json(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    tmp.replace(path)


def harmonics(L, extra=0):
    nt, np_ = max(1, 2*L+1+extra), max(1, 4*L+4+2*extra)
    z, wz = np.polynomial.legendre.leggauss(nt)
    az = 2*np.pi*np.arange(np_)/np_
    labels, ys = [], []
    for l in range(L+1):
        for m in range(l+1):
            norm = np.sqrt((2*l+1)/(4*np.pi)*np.exp(gammaln(l-m+1)-gammaln(l+m+1)))
            p = norm*lpmv(m,l,z)
            if m == 0:
                labels.append((l,0,'0')); ys.append(np.repeat(p,np_))
            else:
                for tag, fun in [('c',np.cos),('s',np.sin)]:
                    labels.append((l,m,tag)); ys.append((np.sqrt(2)*p[:,None]*fun(m*az)).ravel())
    Y = np.asarray(ys); weights = np.repeat(wz,np_)*(2*np.pi/np_)
    return labels, Y, weights


class Evolution:
    def __init__(self, dx, radius, L):
        self.n = int(round(radius/dx)); self.dx = radius/self.n; self.radius = radius
        self.edges = np.linspace(0,radius,self.n+1)
        self.r = (self.edges[1:]+self.edges[:-1])/2
        self.w = np.diff(self.edges**3)/3
        self.c = self.edges[1:-1]**2/self.dx
        self.labels,self.Y,self.wa = harmonics(L)
        self.YW = (self.Y*self.wa).T.copy()
        self.nm = len(self.labels)
        self.ell = np.array([x[0] for x in self.labels])
        self.angular = self.ell*(self.ell+1)
        self.cent = self.dx/self.w[:,None]*self.angular
        self.core = int(round(40/self.dx))

    def lap(self,q):
        flux = self.c[None,:,None]*np.diff(q,axis=1)
        result = np.zeros_like(q)
        result[:,:-1] += flux; result[:,1:] -= flux
        result[:,-1] -= 2*self.radius**2/self.dx*q[:,-1]
        return result/self.w[None,:,None]-self.cent[None,:,:]*q

    def force(self,q,without_mass=False):
        a,b,z = q@self.Y
        s = a*a+b*b
        fac = (0 if without_mass else model.mass2)+2*model.quartic*s+model.trilinear*z+.5*model.mixed*z*z
        values = np.array([-fac*a,-fac*b,-((0 if without_mass else model.mediator**2)+model.mixed*s)*z-model.trilinear*s])
        return self.lap(q)+values@self.YW

    def components(self,q,v):
        a,b,z = q@self.Y; s = a*a+b*b
        pot = model.mass2*s+model.quartic*s*s+.5*model.mediator**2*z*z+model.trilinear*z*s+.5*model.mixed*z*z*s
        bulk = self.w*(np.sum(v[0]**2+v[1]**2+.5*v[2]**2,axis=1)+pot@self.wa)
        dq = np.diff(q,axis=1)
        faces = self.c*np.sum(dq[0]**2+dq[1]**2+.5*dq[2]**2,axis=1)
        ang = self.dx*np.sum(self.angular*(q[0]**2+q[1]**2+.5*q[2]**2),axis=1)
        boundary = 2*self.radius**2/self.dx*np.sum(q[0,-1]**2+q[1,-1]**2+.5*q[2,-1]**2)
        charge = 2*self.w*np.sum(q[0]*v[1]-q[1]*v[0],axis=1)
        return bulk,faces,ang,boundary,charge

    def measure(self,t,q,v):
        bulk,faces,ang,boundary,charge = self.components(q,v)
        c = self.core
        energy = bulk.sum()+faces.sum()+ang.sum()+boundary
        ec = bulk[:c].sum()+faces[:c-1].sum()+.5*faces[c-1]+ang[:c].sum()
        norms = np.sum(self.w[:c,None]*(q[0,:c]**2+q[1,:c]**2),axis=0)
        den = norms[0]
        by_l = [float(np.sqrt(norms[self.ell==l].sum()/den)) for l in range(1,int(self.ell.max())+1)]
        return [t,float(energy),float(charge.sum()),float(ec),float(charge[:c].sum()),
                float(np.sqrt(norms[1:].sum()/den)),*by_l]


def seed(sim,eps):
    with np.load(SOURCE,allow_pickle=False) as d:
        cfg = json.loads(str(d['config'])); assert int(d['step'])*cfg['dt']==1200
        sr = (np.arange(cfg['n'])+.5)*cfg['dx']
        source_q = np.array([d['phi'].real,d['phi'].imag,d['chi']])
        source_v = np.array([d['vel'].real,d['vel'].imag,d['vchi']])
        source_last = d['rows'][-1].tolist()
    # Even extension enforces the same regular centre. All six Cauchy fields
    # come from the saved final state, including its residual radial motion.
    def interp(arr):
        return [CubicSpline(np.r_[-sr[::-1],sr],np.r_[a[::-1],a]) for a in arr]
    sq,sv = interp(source_q),interp(source_v)
    q = np.zeros((3,sim.n,sim.nm)); v = np.zeros_like(q)
    for k in range(3):
        q[k,:,0]=np.sqrt(4*np.pi)*sq[k](sim.r)
        v[k,:,0]=np.sqrt(4*np.pi)*sv[k](sim.r)
    base_q,base_v=q.copy(),v.copy()
    if eps:
        assert sim.nm>=9
        # A triaxial quadrupole with <H^2>_Omega=1. All five real m components
        # are retained by the solver, not an axisymmetric restriction.
        coeff=np.array([1.,.3,-.2,.7,.4]); coeff*=np.sqrt(4*np.pi)/np.linalg.norm(coeff)
        inds=np.flatnonzero(sim.ell==2)
        window=np.exp(-(sim.r/20)**4)
        for k in range(3):
            q[k,:,inds] += (-eps*sim.r*window*sq[k](sim.r,1))[:,None].T*coeff[:,None]
            v[k,:,inds] += (-eps*sim.r*window*sv[k](sim.r,1))[:,None].T*coeff[:,None]
    # Account separately for the exterior omitted from this finite causal
    # experiment, regridding, and the physical initial deformation.
    se=np.linspace(0,cfg['radius'],cfg['n']+1); sw=np.diff(se**3)/3; sc=se[1:-1]**2/cfg['dx']
    a,b,z=source_q; s=a*a+b*b
    sbulk=4*np.pi*sw*(source_v[0]**2+source_v[1]**2+.5*source_v[2]**2+model.potential(np.sqrt(s),z))
    dq=np.diff(source_q,axis=1)
    sf=4*np.pi*sc*(dq[0]**2+dq[1]**2+.5*dq[2]**2)
    scharge=8*np.pi*sw*(source_q[0]*source_v[1]-source_q[1]*source_v[0])
    cut=int(round(sim.radius/cfg['dx']))
    sin=float(sbulk[:cut].sum()+sf[:cut-1].sum()+.5*sf[cut-1]); sqin=float(scharge[:cut].sum())
    bm=sim.measure(0,base_q,base_v); pm=sim.measure(0,q,v)
    transfer=dict(source=str(SOURCE.relative_to(ROOT)),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        source_time=1200.,source_full_energy=source_last[1],source_full_charge=source_last[2],
        source_energy_inside_new_radius=sin,source_charge_inside_new_radius=sqin,
        omitted_exterior_energy=source_last[1]-sin,omitted_exterior_charge=source_last[2]-sqin,
        regridding_and_new_boundary_energy_change=bm[1]-sin,regridding_charge_change=bm[2]-sqin,
        seed_energy_change=pm[1]-bm[1],seed_charge_change=pm[2]-bm[2],
        core_energy_regridding_relative=bm[3]/source_last[3]-1,core_charge_regridding_relative=bm[4]/source_last[4]-1,
        causal_margin=sim.radius-40.,full_original_domain_evolved=False,discarded_exterior_state_preserved=True,
        initial_perturbation='delta q=-epsilon*r*exp(-(r/20)^4)*q_radial_prime*H2; same for all velocities',
        primary_source_derived=False)
    return q,v,transfer


def audit():
    OUT.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(28092026); results=[]
    for L in [0,2,4,6]:
        labels,Y,w=harmonics(L); _,Yh,wh=harmonics(L,extra=4)
        gram=np.max(abs((Y*w)@Y.T-np.eye(len(labels))))
        coeff=rng.normal(size=(3,len(labels)))*.03
        def integral(Z,W):
            a,b,z=coeff@Z; return float(model.potential(np.sqrt(a*a+b*b),z)@W)
        integ=integral(Y,w); ih=integral(Yh,wh)
        results.append(dict(L=L,modes=len(labels),angles=len(w),gram_error=float(gram),quartic_quadrature_relative=abs(integ-ih)/max(1,abs(ih))))
    sim=Evolution(.5,4.,2); q=rng.normal(size=(3,sim.n,sim.nm))*.01; v=rng.normal(size=q.shape)*.01
    direction=rng.normal(size=q.shape); force=sim.force(q)
    def energy(x):
        b,f,a,bnd,_=sim.components(x,v); return float(b.sum()+f.sum()+a.sum()+bnd)
    step=1e-6; numerical=(energy(q+step*direction)-energy(q-step*direction))/(2*step)
    analytical=-np.sum(sim.w[None,:,None]*np.array([2,2,1])[:,None,None]*force*direction)
    gradient_error=float(abs(numerical-analytical)/max(1,abs(analytical)))
    charge_acc=float(abs(2*np.sum(sim.w[:,None]*(q[0]*force[1]-q[1]*force[0]))))
    result=dict(angular=results,variational_force_relative=gradient_error,charge_acceleration_absolute=charge_acc,
        passed=bool(all(x['gram_error']<1e-12 and x['quartic_quadrature_relative']<1e-12 for x in results) and gradient_error<2e-7 and charge_acc<1e-10),
        scope='Discrete variational and quadrature audit, not a continuum proof')
    save_json(OUT/'auditoria_operador.json',result); print(json.dumps(result,indent=2),flush=True)
    assert result['passed']


def run(dx=.5,dt=.004,radius=220.,L=2,eps=.02,tmax=160.,stop_at=None,scheme='vv'):
    OUT.mkdir(parents=True,exist_ok=True)
    assert json.loads((OUT/'auditoria_operador.json').read_text())['passed']
    assert radius-40>tmax, 'Window must end before the continuum boundary can reach the core'
    config=dict(dx=dx,dt=dt,radius=radius,L=L,eps=eps,tmax=tmax,source_time=1200.,core_radius=40.)
    if scheme=='split4b':config['numerical_phase_reference']=.90132601261449
    tag=f'L{L}_h{dx:.3f}_dt{dt:.4f}_R{radius:.0f}_eps{eps:.3f}_T{tmax:.0f}'
    if scheme!='vv':config['scheme']=scheme;tag=scheme+'_'+tag
    sp=OUT/f'{tag}_estado.npz'; rp=OUT/f'{tag}.json'; pp=OUT/f'{tag}_progreso.json'
    if (OUT/f'{tag}_puerta_fallida.json').exists():
        raise RuntimeError('Puerta numérica fallida registrada; no reanudar automáticamente este intento')
    if rp.exists():
        result=json.loads(rp.read_text()); assert result['configuration']==config
        with np.load(sp,allow_pickle=False) as d:
            assert int(d['step'])==round(tmax/dt) and np.isfinite(d['q']).all() and np.isfinite(d['v']).all()
        print('REUTILIZADO',tag,flush=True); return
    sim=Evolution(dx,radius,L); steps=int(round(tmax/dt)); start=0; elapsed0=0.
    stride=int(round(.4/dt)); cps=int(round(8/dt))
    if sp.exists():
        with np.load(sp,allow_pickle=False) as d:
            assert json.loads(str(d['config']))==config
            q=d['q'];v=d['v'];rows=d['rows'].tolist();start=int(d['step']);elapsed0=float(d['elapsed'])
            transfer=json.loads(str(d['transfer'])); initial_q=d['initial_q'];initial_v=d['initial_v']
        print('REANUDADO',tag,'paso',start,flush=True)
    else:
        q,v,transfer=seed(sim,eps);rows=[sim.measure(0,q,v)];initial_q=q.copy();initial_v=v.copy()
        save_json(OUT/f'{tag}_transferencia.json',transfer)
    clock=time.perf_counter()
    def checkpoint(step):
        tmp=sp.with_suffix('.tmp')
        with tmp.open('wb') as f:
            np.savez_compressed(f,q=q,v=v,initial_q=initial_q,initial_v=initial_v,rows=np.asarray(rows),step=step,
                elapsed=elapsed0+time.perf_counter()-clock,config=json.dumps(config),transfer=json.dumps(transfer),
                labels=np.asarray(sim.labels,dtype=str))
        tmp.replace(sp)
        save_json(pp,dict(status='EN_PROGRESO' if step<steps else 'EVOLUCION_TERMINADA_DIAGNOSTICO_PENDIENTE',
            step=step,total_steps=steps,source_time=1200.,elapsed_physical_time=step*dt,restart_file=sp.name,stage_complete=False))
    if start==0: checkpoint(0)
    split=scheme in ['split4','split4c','split4b']
    # Symmetric fourth-order composition: 2*b1+b0=1 and 2*b1^3+b0^3=0.
    # The middle substep is negative; no dissipation or new physical term.
    b1=1/(2-2**(1/3));b0=-2**(1/3)/(2-2**(1/3))
    frequencies=np.array([np.sqrt(model.mass2),np.sqrt(model.mass2),model.mediator])[:,None,None]
    if scheme=='split4b':frequencies[:2]=config['numerical_phase_reference']
    bare_mass2=np.array([model.mass2,model.mass2,model.mediator**2])[:,None,None]
    centre=np.zeros_like(q)
    if scheme in ['split4c','split4b']:centre[2]=initial_q[2]
    # This reference occurs with cancelling signs in A and B. It is solely
    # an integrator coordinate shift, NOT a physical background or source.
    correction=frequencies**2*centre
    def acceleration(x):
        return sim.force(x,without_mass=True)+(frequencies**2-bare_mass2)*x-correction if split else sim.force(x)
    acc=acceleration(q);end=steps if stop_at is None else min(steps,round(stop_at/dt))
    rotations=[]
    for b in [b1,b0,b1]:
        h=b*dt;rotations.append((h,np.cos(frequencies*h),np.sin(frequencies*h)/frequencies,frequencies*np.sin(frequencies*h)))
    for k in range(start,end):
        if split:
            for h,co,si,msi in rotations:
                v+=.5*h*acc
                old=q-centre;q=centre+co*old+si*v;v=co*v-msi*old
                acc=acceleration(q);v+=.5*h*acc
        else:
            v+=.5*dt*acc; q+=dt*v; acc=sim.force(q);v+=.5*dt*acc
        if (k+1)%stride==0:
            rows.append(sim.measure((k+1)*dt,q,v))
            if not np.isfinite(rows[-1]).all():
                save_json(OUT/f'{tag}_fallo.json',dict(step=k+1,reason='Nonfinite observables',last_valid_restart=sp.name))
                raise FloatingPointError(tag)
            if abs(rows[-1][1]/rows[0][1]-1)>2e-4 or abs(rows[-1][2]/rows[0][2]-1)>1e-9:
                # Keep the previous restart intact, and preserve the failed
                # observation separately. Never overwrite the last valid NPZ.
                failed=OUT/f'{tag}_estado_fallido.npz'
                np.savez_compressed(failed,q=q,v=v,rows=np.asarray(rows),step=k+1,config=json.dumps(config))
                save_json(OUT/f'{tag}_puerta_fallida.json',dict(status='PUERTA_NUMERICA_FALLIDA',step=k+1,time=(k+1)*dt,
                    energy_drift=abs(rows[-1][1]/rows[0][1]-1),charge_drift=abs(rows[-1][2]/rows[0][2]-1),
                    last_valid_restart=sp.name,failed_state=failed.name,physical_instability_inferred=False))
                save_json(pp,dict(status='PARCIAL',failed_time=(k+1)*dt,restart_file=sp.name,
                    resume_policy='Do not resume this failed configuration automatically',stage_complete=False))
                raise SystemExit(2)
        if (k+1)%cps==0:
            checkpoint(k+1);print('EVOLUCION',tag,'tau',(k+1)*dt,'s',round(elapsed0+time.perf_counter()-clock,1),flush=True)
    if rows[-1][0]<end*dt: rows.append(sim.measure(end*dt,q,v))
    checkpoint(end)
    if end<steps: print('PAUSA_REANUDABLE',tag,end*dt,flush=True);return
    a=np.asarray(rows); edrift=float(np.max(abs(a[:,1]/a[0,1]-1))); qdrift=float(np.max(abs(a[:,2]/a[0,2]-1)))
    result=dict(configuration=config,initial_energy=float(a[0,1]),initial_charge=float(a[0,2]),final_core_energy=float(a[-1,3]),
        final_core_charge=float(a[-1,4]),relative_energy_drift=edrift,relative_charge_drift=qdrift,
        relative_core_charge_change=float(np.max(abs(a[:,4]/a[0,4]-1))),initial_nonradial_norm=float(a[0,5]),
        max_nonradial_norm=float(a[:,5].max()),max_amplification=float(a[:,5].max()/a[0,5]) if eps else None,
        mode_maxima={str(l):float(a[:,5+l].max()) for l in range(1,L+1)},
        elapsed_seconds=elapsed0+time.perf_counter()-clock,balance_passed=edrift<2e-4 and qdrift<1e-9,
        bounded_window_passed=bool(a[:,5].max()<=3*a[0,5]) if eps else bool(a[:,5].max()<1e-10),
        stage_complete=False,orbital_stability_proven=False,full_angular_continuum=False,
        interpretation='Finite conservative nonradial continuation of CP04 with all m through L; no claim outside this window or truncation')
    save_json(rp,result)
    np.savetxt(OUT/f'{tag}_tiempo.csv',a,delimiter=',',header='tau,E_box,Q_box,E_core40,Q_core40,nonradial_norm'+''.join(f',norm_l{l}' for l in range(1,L+1)),comments='')
    save_json(pp,dict(status='CALCULO_TERMINADO',step=steps,time=tmax,source_time=1200.,result=rp.name,restart_file=sp.name,stage_complete=False))
    print(json.dumps(result,indent=2),flush=True)
    if not result['balance_passed']: raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audit',action='store_true');p.add_argument('--dx',type=float,default=.5)
    p.add_argument('--dt',type=float,default=.004);p.add_argument('--radius',type=float,default=220);p.add_argument('--L',type=int,default=2)
    p.add_argument('--eps',type=float,default=.02);p.add_argument('--tmax',type=float,default=160);p.add_argument('--stop-at',type=float)
    p.add_argument('--scheme',choices=['vv','split4','split4c','split4b'],default='vv')
    args=vars(p.parse_args());do_audit=args.pop('audit')
    with threadpool_limits(limits=1):
        if do_audit:audit()
        else:run(**args)
