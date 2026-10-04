"""Respuestas pasivas de la identidad de diferencias; ningún paso físico M2."""
import copy
import numpy as np
from scipy.integrate import DOP853
from scipy.interpolate import CubicSpline
from scipy.linalg import solve_banded, eigh_tridiagonal
from numpy.polynomial import Polynomial
from continuar_no_radial_m2 import Evolution
from modelo_m2 import BENCHMARK as model
from diagnosticar_chi_CP11 import tridiagonal

BARE = ['inicial_libre', 'operador_chi', 'transferencia_chi', 'densidad_rho', 'reaccion_chi']
COUPLED = ['inicial', 'operador_Phi', 'operador_chi', 'transferencia_Phi', 'transferencia_chi']


def interpolate(sim, q, target):
    return CubicSpline(sim.r, q, axis=-2)(target.r)


def lap(sim, q):
    flux = sim.c * np.diff(q, axis=-2).swapaxes(-1, -2)
    flux = flux.swapaxes(-1, -2)
    result = np.zeros_like(q)
    result[..., :-1, :] += flux
    result[..., 1:, :] -= flux
    result[..., -1, :] -= 2 * sim.radius**2 / sim.dx * q[..., -1, :]
    return result / sim.w[:, None] - sim.cent * q


def nonlinear(sim, physical):
    a, b, z = physical
    rho = a*a + b*b
    fac = 2*model.quartic*rho + model.trilinear*z + .5*model.mixed*z*z
    return np.array([-fac*a, -fac*b, -(model.trilinear+model.mixed*z)*rho]) @ sim.YW


def terms(sc, sf, qc, qf):
    qi = interpolate(sc, qc, sf)
    xc, xi, xf = qc @ sc.Y, qi @ sf.Y, qf @ sf.Y
    nc, ni, nf = nonlinear(sc, xc), nonlinear(sf, xi), nonlinear(sf, xf)
    comm = interpolate(sc, lap(sc, qc), sf) - lap(sf, qi)
    transfer = interpolate(sc, nc, sf) - ni
    rc, rf = xi[0]**2 + xi[1]**2, xf[0]**2 + xf[1]**2
    rho = -((model.trilinear + model.mixed*(xi[2]+xf[2])/2)*(rc-rf)) @ sf.YW
    feedback = -(model.mixed*(rc+rf)/2*(xi[2]-xf[2])) @ sf.YW
    bare = np.zeros((5, 1, sf.n, sf.nm))
    bare[1, 0] = comm[2]; bare[2, 0] = transfer[2]
    bare[3, 0] = rho; bare[4, 0] = feedback
    coupled = np.zeros((5, 3, sf.n, sf.nm))
    coupled[1, :2] = comm[:2]; coupled[2, 2] = comm[2]
    coupled[3, :2] = transfer[:2]; coupled[4, 2] = transfer[2]
    mu, delta = (xi+xf)/2, xi-xf
    a, b, z = mu; da, db, dz = delta
    a2, b2, z2 = a*a+da*da/12, b*b+db*db/12, z*z+dz*dz/12
    fac = 2*model.quartic*(a2+b2) + model.trilinear*z + .5*model.mixed*z2
    jac = np.array([-fac-4*model.quartic*a2, -fac-4*model.quartic*b2,
                    -4*model.quartic*(a*b+da*db/12),
                    -model.trilinear*a-model.mixed*(z*a+dz*da/12),
                    -model.trilinear*b-model.mixed*(z*b+dz*db/12),
                    -model.mixed*(a2+b2)])
    return bare, coupled, jac


def apply_jac(sim, jac, q):
    x = q @ sim.Y
    aa, bb, ab, az, bz, zz = jac
    a, b, z = x[:, 0], x[:, 1], x[:, 2]
    value = np.stack([aa*a+ab*b+az*z, ab*a+bb*b+bz*z,
                      2*az*a+2*bz*b+zz*z], axis=1)
    return value @ sim.YW


def passive_dense(solver):
    """Las etapas extra viven en una copia; RHS puro, sin contar en solver.nfev."""
    shadow = copy.copy(solver)
    shadow.K_extended = solver.K_extended.copy()
    shadow.K = shadow.K_extended[:solver.n_stages+1]
    shadow.fun = solver.fun_single
    return DOP853._dense_output_impl(shadow)


def gauss_table(stages):
    x, b = np.polynomial.legendre.leggauss(stages)
    c, b = (x+1)/2, b/2
    A = np.empty((stages, stages))
    for j in range(stages):
        p = Polynomial([1.])
        for k in range(stages):
            if k != j: p *= Polynomial([-c[k], 1.]) / (c[j]-c[k])
        ip = p.integ(); A[:, j] = ip(c)-ip(0)
    ev, S = np.linalg.eig(A)
    return c, b, A, ev, S, np.linalg.inv(S)


class GaussResponse:
    """Colocación GL; masas/lap exactos, Jacobiano prescrito de la historia."""
    def __init__(self, sim, fields, stages, initial_q, initial_v):
        self.sim = sim; self.fields = fields; self.stages = stages
        self.c, self.b, self.A, self.ev, self.S, self.Si = gauss_table(stages)
        self.A2 = self.A @ self.A; self.A1 = self.A @ np.ones(stages)
        self.masses = np.array([model.mediator**2] if fields == 1 else [model.mass2, model.mass2, model.mediator**2])
        self.q = np.zeros((5, fields, sim.n, sim.nm)); self.v = np.zeros_like(self.q)
        self.q[0] = initial_q; self.v[0] = initial_v
        self.last_iterations = 0; self.max_iterations = 0; self.max_iteration_residual = 0.
        self.matrices = {}
        for ell in range(int(sim.ell.max())+1):
            diag, off = tridiagonal(sim, ell)
            # tridiagonal() is the W-symmetric representative; return physical coefficients.
            self.matrices[ell] = (diag, off*np.sqrt(sim.w[1:]/sim.w[:-1]), off*np.sqrt(sim.w[:-1]/sim.w[1:]))

    def action(self, q):
        return self.masses[:, None, None]*q - lap(self.sim, q)

    def stage_solve(self, h, forcing):
        rhs = self.q[None] + h*self.A1[:, None, None, None, None]*self.v[None]
        rhs = rhs + h*h*np.tensordot(self.A2, forcing, axes=(1, 0))
        transformed = np.tensordot(self.Si, rhs, axes=(1, 0))
        solved = np.empty_like(transformed)
        for j, ev in enumerate(self.ev):
            if ev.imag < -1e-12: continue
            for f in range(self.fields):
                for ell, (di, upper, lower) in self.matrices.items():
                    sel = np.flatnonzero(self.sim.ell == ell)
                    band = np.zeros((3, self.sim.n), dtype=complex)
                    factor = (h*ev)**2
                    band[1] = 1+factor*(self.masses[f]+di)
                    band[0, 1:] = factor*upper; band[2, :-1] = factor*lower
                    plane = transformed[j, :, f]
                    values = plane[:, :, sel].transpose(1, 0, 2).reshape(self.sim.n, -1).copy()
                    answer = solve_banded((1, 1), band, values, overwrite_ab=True, overwrite_b=True, check_finite=False)
                    solved[j, :, f, :, sel] = answer.reshape(self.sim.n, 5, len(sel)).transpose(2, 1, 0)
            if ev.imag > 1e-12:
                other = int(np.argmin(abs(self.ev-ev.conjugate())))
                solved[other] = solved[j].conjugate()
        return np.tensordot(self.S, solved, axes=(1, 0)).real

    def advance(self, h, forcing, jac=None):
        if jac is None:
            Q = self.stage_solve(h, forcing); G = forcing; iterations = 0; residual = 0.
        else:
            Q = self.q[None] + self.c[:, None, None, None, None]*h*self.v[None]
            for iterations in range(1, 13):
                G = forcing + np.array([apply_jac(self.sim, jac[s], Q[s]) for s in range(self.stages)])
                updated = self.stage_solve(h, G)
                residual = float(np.max(abs(updated-Q))/max(float(np.max(abs(updated))), 1e-14))
                Q = updated
                if residual <= 1e-12: break
            else: raise ValueError('Etapas pasivas no convergen; no interpretar ni cambiar integración M2')
            G = forcing + np.array([apply_jac(self.sim, jac[s], Q[s]) for s in range(self.stages)])
        acceleration = G-self.action(Q)
        V = self.v[None]+h*np.tensordot(self.A, acceleration, axes=(1, 0))
        self.q = self.q+h*np.tensordot(self.b, V, axes=(0, 0))
        self.v = self.v+h*np.tensordot(self.b, acceleration, axes=(0, 0))
        self.last_iterations = iterations; self.max_iterations = max(self.max_iterations, iterations)
        self.max_iteration_residual = max(self.max_iteration_residual, residual)


def chi_inner(sim, aq, av, bq, bv):
    use = sim.r < 40
    return float(np.sum(sim.w[use, None]*(aq[use, 1:]*bq[use, 1:]+av[use, 1:]*bv[use, 1:]/model.mediator**2)))


class Budget:
    def __init__(self, sc, sf, qc0, vc0, qf0, vf0, config):
        self.sc, self.sf = sc, sf; self.config = config
        d0 = interpolate(sc, qc0, sf)-qf0; v0 = interpolate(sc, vc0, sf)-vf0
        self.orders = config.get('observer_stages', [5, 4])
        self.raw = [GaussResponse(sf, 1, s, d0[2:3], v0[2:3]) for s in self.orders]
        self.coupled = [GaussResponse(sf, 3, s, d0, v0) for s in self.orders]
        self.scale = chi_inner(sf, qf0[2], vf0[2], qf0[2], vf0[2])
        self.phi_scale = float(np.sum(sf.w[None, :, None]*(qf0[:2]**2+vf0[:2]**2/model.mass2)))
        self.rows = []; self.algebra = []; self.max_step_phase = 0.; self.maximum_errors = {}
        self.modal = {}
        if config.get('modal_diagnostics', True):
            for ell in [1, 2, 3, 4]:
                diag, off = tridiagonal(sf, ell)
                lam, U = eigh_tridiagonal(diag, off, lapack_driver='stemr')
                self.modal[ell] = (lam, U)
        self.max_frequency = float(max(np.sqrt(model.mediator**2+np.max(tridiagonal(sf, e)[0])+2*np.max(abs(tridiagonal(sf, e)[1]))) for e in range(5)))
        self.window = np.ones(sf.n)
        transition=(sf.r>=32)&(sf.r<40)
        self.window[transition]=.5*(1+np.cos(np.pi*(sf.r[transition]-32)/8))
        self.window[sf.r>=40]=0

    def advance(self, start, end, coarse_dense, fine_dense, shape_c, shape_f):
        h = end-start; self.max_step_phase = max(self.max_step_phase, h*self.max_frequency)
        for index, s in enumerate(self.orders):
            data = []
            for node in self.raw[index].c:
                time = start+h*node
                qc = coarse_dense(time).reshape(shape_c)[0]
                qf = fine_dense(time).reshape(shape_f)[0]
                data.append(terms(self.sc, self.sf, qc, qf))
            self.raw[index].advance(h, np.array([x[0] for x in data]))
            self.coupled[index].advance(h, np.array([x[1] for x in data]), np.array([x[2] for x in data]))

    def metrics(self, q, v, names, dq, dv):
        norm = chi_inner(self.sf, dq, dv, dq, dv)
        den = max(norm, self.scale*1e-10)
        rows = []
        for name, a, b in zip(names, q, v):
            power = chi_inner(self.sf, a, b, a, b)
            dot = chi_inner(self.sf, a, b, dq, dv)
            rows.append(dict(name=name,relative_error=float(np.sqrt(max(0,power)/self.scale)),
                             signed_projection=dot/den,cosine=dot/np.sqrt(max(1e-300,power*norm)),
                             removal_squared_reduction=1-chi_inner(self.sf,dq-a,dv-b,dq-a,dv-b)/den))
        return rows

    def record(self, time, qc, vc, qf, vf):
        dq = interpolate(self.sc, qc, self.sf)-qf; dv = interpolate(self.sc, vc, self.sf)-vf
        actual = chi_inner(self.sf,dq[2],dv[2],dq[2],dv[2]); den=max(actual,self.scale*1e-10)
        item=dict(time=float(time),observed_relative_error=float(np.sqrt(actual/self.scale)),
                  raw=self.metrics(self.raw[0].q[:,0],self.raw[0].v[:,0],BARE,dq[2],dv[2]),
                  coupled=self.metrics(self.coupled[0].q[:,2],self.coupled[0].v[:,2],COUPLED,dq[2],dv[2]))
        errors={}
        for name, family, field in [('raw',self.raw,0),('coupled',self.coupled,2)]:
            q=family[0].q[:,field];v=family[0].v[:,field]
            errors[name+'_closure']=float(np.sqrt(chi_inner(self.sf,dq[2]-q.sum(0),dv[2]-v.sum(0),dq[2]-q.sum(0),dv[2]-v.sum(0))/den))
            errors[name+'_order_difference']=float(np.sqrt(chi_inner(self.sf,(family[0].q[:,field]-family[1].q[:,field]).sum(0),(family[0].v[:,field]-family[1].v[:,field]).sum(0),(family[0].q[:,field]-family[1].q[:,field]).sum(0),(family[0].v[:,field]-family[1].v[:,field]).sum(0))/den))
            individual=[]
            for k in range(5):
                a=family[0].q[k,field]-family[1].q[k,field];b=family[0].v[k,field]-family[1].v[k,field]
                n=max(chi_inner(self.sf,q[k],v[k],q[k],v[k]),self.scale*1e-10)
                individual.append(float(np.sqrt(chi_inner(self.sf,a,b,a,b)/n)))
            errors[name+'_individual_order_difference']=max(individual)
        item['verification']=errors
        cq=self.coupled[0].q[:,:2];cv=self.coupled[0].v[:,:2]
        phi_norm=lambda a,b:float(np.sum(self.sf.w[None,:,None]*(a*a+b*b/model.mass2)))
        pden=max(phi_norm(dq[:2],dv[:2]),self.phi_scale*1e-10)
        errors['coupled_Phi_closure']=float(np.sqrt(phi_norm(dq[:2]-cq.sum(0),dv[:2]-cv.sum(0))/pden))
        errors['coupled_Phi_order_difference']=float(np.sqrt(phi_norm((cq-self.coupled[1].q[:,:2]).sum(0),(cv-self.coupled[1].v[:,:2]).sum(0))/pden))
        if self.modal:
            item['short_modes']=self.modal_metrics(dq[2],dv[2])
            errors['modal_parseval']=item['short_modes']['parseval_relative_residual']
            for window in ['core','smooth']:
                for key,value in item['short_modes'][window]['verification'].items():errors['short_'+window+'_'+key]=value
        for k,value in errors.items():self.maximum_errors[k]=max(self.maximum_errors.get(k,0.),value)
        item['coupled_Phi_response_from_chi_operator']=float(np.sqrt(np.sum(self.sf.w[:,None]*(self.coupled[0].q[2,:2]**2+self.coupled[0].v[2,:2]**2))))
        self.rows.append(item)
        return item

    def modal_metrics(self,dq,dv):
        # Todas las respuestas y ambos órdenes comparten exactamente la misma ventana/base.
        q=np.concatenate([dq[None],self.raw[0].q[:,0],self.coupled[0].q[:,2],self.raw[1].q[:,0],self.coupled[1].q[:,2]])
        v=np.concatenate([dv[None],self.raw[0].v[:,0],self.coupled[0].v[:,2],self.raw[1].v[:,0],self.coupled[1].v[:,2]])
        use=self.sf.r<40;w=self.sf.w[use];powers={};dots={};parseval=0.
        for label,window in [('core',np.ones(use.sum())),('smooth',self.window[use])]:
            allpower=np.zeros(len(q));cutpower={str(c):np.zeros(len(q)) for c in [2,4,8,12,20]}
            cutdot={str(c):np.zeros(len(q)) for c in [2,4,8,12,20]}
            cross=np.zeros((len(q),len(q)))
            for ell,(lam,U) in self.modal.items():
                sel=self.sf.ell==ell;nm=int(sel.sum())
                sw=np.sqrt(w)*window
                xq=(q[:,use][:,:,sel]*sw[None,:,None]).transpose(1,0,2).reshape(use.sum(),-1)
                xv=(v[:,use][:,:,sel]*sw[None,:,None]/model.mediator).transpose(1,0,2).reshape(use.sum(),-1)
                coeff=U[use].T@np.concatenate([xq,xv],axis=1)
                aq,av=np.split(coeff,2,axis=1);aq=aq.reshape(self.sf.n,len(q),nm);av=av.reshape(aq.shape)
                allpower+=np.sum(aq*aq+av*av,axis=(0,2))
                for cut in [2,4,8,12,20]:
                    selected=np.sqrt(lam)>cut;a,b=aq[selected],av[selected]
                    cutpower[str(cut)]+=np.sum(a*a+b*b,axis=(0,2))
                    cutdot[str(cut)]+=np.sum(a*a[:,0:1]+b*b[:,0:1],axis=(0,2))
                    if cut==4:
                        cross+=np.einsum('ikm,ilm->kl',a,a)+np.einsum('ikm,ilm->kl',b,b)
            expected=np.sum((q[:,use,1:]*window[None,:,None])**2*w[None,:,None]+(v[:,use,1:]*window[None,:,None]/model.mediator)**2*w[None,:,None],axis=(1,2))
            # Canal nulo: medir residuo absoluto respecto a escala inicial, no dividir por cero.
            parseval=max(parseval,float(np.max(abs(allpower-expected)/np.maximum(expected,self.scale*1e-20))))
            metrics=[];norm=cutpower['4'][0];den=max(norm,self.scale*1e-10)
            for k,name in enumerate(BARE+COUPLED,1):
                power=cutpower['4'][k];dot=cutdot['4'][k]
                metrics.append(dict(name=name,family='raw' if k<=5 else 'coupled',relative_error=float(np.sqrt(power/self.scale)),
                                    signed_projection=float(dot/den),cosine=float(dot/np.sqrt(max(1e-300,power*norm))),
                                    removal_squared_reduction=float((2*dot-power)/den)))
            errors={}
            for name,indices,controls in [('raw',np.arange(1,6),np.arange(11,16)),('coupled',np.arange(6,11),np.arange(16,21))]:
                e=np.zeros(len(q));e[0]=1;e[indices]=-1
                diff=np.zeros(len(q));diff[indices]=1;diff[controls]=-1
                errors[name+'_closure']=float(np.sqrt(max(0,float(e@cross@e))/den))
                errors[name+'_order_difference']=float(np.sqrt(max(0,float(diff@cross@diff))/den))
            powers[label]=dict(observed_error_fraction_above_k={c:float(p[0]/max(allpower[0],1e-300)) for c,p in cutpower.items()},
                               short_relative_error=float(np.sqrt(norm/self.scale)),metrics=metrics,verification=errors,
                               short_response_gram_matrix=cross[:11,:11].tolist())
        return dict(**powers,parseval_relative_residual=parseval)
