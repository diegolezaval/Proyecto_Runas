"""Prospective Phi-FV/chi-K4 operators. No evolution entrypoint."""
import numpy as np
from continuar_no_radial_m2 import Evolution
from operador import Candidate
from backend import CandidateGauss,lap_general as lap_k4
from observador_causal_CP12 import GaussResponse,lap as lap_fv

def lap_mixed(sim,q):
    """Field axis is -3; all other leading axes are passive channels."""
    if q.shape[-3]!=3:raise ValueError('Mixed vector requires three fields')
    out=lap_fv(sim,q)
    out[...,2:3,:,:]=lap_k4(sim,q[...,2:3,:,:])
    return out

class Mixed(Candidate):
    def lap(self,q):
        out=Evolution.lap(self,q)
        out[2:3]=Candidate.lap(self,q[2:3])
        return out

    def components(self,q,v):
        bulk,_,_,_,charge=Evolution.components(self,q,v)
        d=np.diff(q[:2],axis=1)
        faces=self.c*np.sum(d[0]**2+d[1]**2,axis=1)
        u=q[2]/self.powers
        faces+=np.sum(.5*self.conductance_u*np.diff(u,axis=0)**2,axis=1)
        second=self.lap2(q[2:3])[0]
        bulk=bulk+self.dx**2/24*self.w*np.sum(second**2,axis=1)
        angular=self.dx*np.sum(self.angular*(q[0]**2+q[1]**2),axis=1)
        boundary=2*self.radius**2/self.dx*np.sum(q[0,-1]**2+q[1,-1]**2)
        boundary+=.5*np.sum(self.boundary_u*u[-1]**2)
        return bulk,faces,angular,boundary,charge

class MixedGauss(GaussResponse):
    """Delegate scalar resolvents, retaining the original Gauss coefficients."""
    def __init__(self,sim,fields,stages,initial_q,initial_v):
        super().__init__(sim,fields,stages,initial_q,initial_v)
        if fields not in (1,3):raise ValueError('Only original bare/coupled spaces')
        self.scalar=[]
        for f in range(fields):
            cls=CandidateGauss if fields==1 or f==2 else GaussResponse
            sub=cls(sim,1,stages,initial_q[f:f+1],initial_v[f:f+1])
            sub.masses=self.masses[f:f+1].copy()
            self.scalar.append(sub)

    def action(self,q):
        l=lap_k4(self.sim,q) if self.fields==1 else lap_mixed(self.sim,q)
        return self.masses[:,None,None]*q-l

    def stage_solve(self,h,forcing):
        out=np.empty((self.stages,*self.q.shape))
        for f,sub in enumerate(self.scalar):
            sub.q=self.q[:,f:f+1];sub.v=self.v[:,f:f+1]
            out[:,:,f:f+1]=sub.stage_solve(h,forcing[:,:,f:f+1])
        return out
