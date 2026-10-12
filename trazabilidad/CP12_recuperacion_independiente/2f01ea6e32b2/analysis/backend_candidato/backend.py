"""Independent five-band Gauss prototype; original numerical files unchanged."""
import time
import numpy as np
from scipy.linalg import solve_banded
from observador_causal_CP12 import GaussResponse, POOL

def lap2_general(sim,q):
    ell=tuple(int(x) for x in sim.ell)
    key=(sim.n,ell)
    if getattr(sim,'_candidate_cache_key',None)!=key:
        powers=sim.r[:,None]**sim.ell[None,:]
        mass=sim.w[:,None]*powers**2
        cumulative=np.cumsum(mass,axis=0);factor=2*sim.ell+3
        conductance=factor[None,:]*cumulative[:-1]/(sim.edges[1:-1,None]*sim.dx)
        boundary=2*factor*cumulative[-1]/(sim.radius*sim.dx)
        sim._candidate_cache_key=key;sim._candidate_cache=(powers,conductance,boundary)
    powers,conductance,boundary=sim._candidate_cache
    u=q/powers;flux=conductance*np.diff(u,axis=-2);force=np.zeros_like(q)
    force[...,:-1,:]+=flux;force[...,1:,:]-=flux;force[...,-1,:]-=boundary*u[...,-1,:]
    return force/(sim.w[:,None]*powers)

def lap_general(sim,q):
    second=lap2_general(sim,q)
    return second-sim.dx**2/12*lap2_general(sim,second)

def weighted_bands(sim,ell):
    if hasattr(sim,'weighted_tridiagonal2') and len(sim.ell)==len(sim.powers[0]):d,e=sim.weighted_tridiagonal2(ell)
    else:
        power=sim.r**ell;mass=sim.w*power**2;c=(2*ell+3)*np.cumsum(mass)[:-1]/(sim.edges[1:-1]*sim.dx)
        d=(np.r_[c,0.]+np.r_[0.,c]);d[-1]+=2*(2*ell+3)*mass.sum()/(sim.radius*sim.dx)
        d/=power**2*sim.w;e=-c/(power[:-1]*power[1:]*np.sqrt(sim.w[:-1]*sim.w[1:]))
    alpha=sim.dx**2/12
    main=d+alpha*(d*d+np.r_[e*e,0.]+np.r_[0.,e*e])
    first=e*(1+alpha*(d[:-1]+d[1:]));second=alpha*e[:-1]*e[1:]
    return main,first,second

class CandidateGauss(GaussResponse):
    def __init__(self,sim,fields,stages,initial_q,initial_v):
        super().__init__(sim,fields,stages,initial_q,initial_v)
        self.penta={}
        for ell in np.unique(sim.ell):
            d,e,f=weighted_bands(sim,ell)
            self.penta[ell]=(d,e*np.sqrt(sim.w[1:]/sim.w[:-1]),e*np.sqrt(sim.w[:-1]/sim.w[1:]),f*np.sqrt(sim.w[2:]/sim.w[:-2]),f*np.sqrt(sim.w[:-2]/sim.w[2:]))
    def action(self,q):return self.masses[:,None,None]*q-lap_general(self.sim,q)
    def stage_solve(self,h,forcing):
        clock=time.perf_counter()
        rhs=self.q[None]+h*self.A1[:,None,None,None,None]*self.v[None]
        rhs+=h*h*np.tensordot(self.A2,forcing,axes=(1,0))
        self.timings['rhs']+=time.perf_counter()-clock;clock=time.perf_counter()
        transformed=np.tensordot(self.Si,rhs,axes=(1,0));self.timings['transform']+=time.perf_counter()-clock;clock=time.perf_counter()
        solved=np.empty_like(transformed)
        tasks=[(j,f,ell) for j,ev in enumerate(self.ev) if ev.imag>=-1e-12 for f in range(self.fields) for ell in self.penta]
        def solve(task):
            j,f,ell=task;ev=self.ev[j];di,upper,lower,upper2,lower2=self.penta[ell]
            sel=np.flatnonzero(self.sim.ell==ell);band=np.zeros((5,self.sim.n),dtype=complex);factor=(h*ev)**2
            band[2]=1+factor*(self.masses[f]+di);band[1,1:]=factor*upper;band[3,:-1]=factor*lower
            band[0,2:]=factor*upper2;band[4,:-2]=factor*lower2
            plane=transformed[j,:,f];values=plane[:,:,sel].transpose(1,0,2).reshape(self.sim.n,-1).copy()
            answer=solve_banded((2,2),band,values,overwrite_ab=True,overwrite_b=True,check_finite=False)
            return j,f,sel,answer.reshape(self.sim.n,5,len(sel)).transpose(2,1,0)
        for j,f,sel,answer in POOL.map(solve,tasks):solved[j,:,f,:,sel]=answer
        for j,ev in enumerate(self.ev):
            if ev.imag>1e-12:solved[int(np.argmin(abs(self.ev-ev.conjugate())))]=solved[j].conjugate()
        self.timings['tridiagonal']+=time.perf_counter()-clock;clock=time.perf_counter()
        result=np.tensordot(self.S,solved,axes=(1,0)).real;self.timings['back_transform']+=time.perf_counter()-clock
        return result
