"""Prueba de contacto instantánea en el espacio de fases M2."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.special import roots_legendre

HERE = Path(__file__).resolve().parent
RES = HERE.parent
ROOT = RES.parents[1]
sys.path.insert(0, str(RES/"contacto_interno_20261126"))
sys.path.insert(0, str(ROOT/"herramientas"))
from medir import Profile, digest
from modelo_m2 import BENCHMARK as m


class State(Profile):
    def __init__(self,path,sha):
        super().__init__(path,.9,sha)
        with np.load(path,allow_pickle=False) as archive:
            q,v,dx = archive["q"],archive["v"],float(archive["dx"])
        r = (np.arange(q.shape[1])+.5)*dx
        self.neutral = CubicSpline(np.r_[-r[2::-1],r,self.edge],
            np.vstack([np.r_[a[2::-1],a,0.] for a in (q[2],v[2])]),axis=1)

    def sample(self,r):
        z,p = self.neutral(np.minimum(r,self.edge))
        return self.field(r),self.velocity(r),self.field(r,1),np.where(r<self.edge,z,0.),np.where(r<self.edge,p,0.)


def domain(d,edges,order):
    x,wx = roots_legendre(order)
    y,wy = roots_legendre(6*order)
    cuts = np.unique(np.r_[np.arange(0,max(edges),2.),40.,d/2,edges])
    widths = np.diff(cuts)
    r = (cuts[:-1,None]+widths[:,None]*(1+x)/2).ravel()[:,None]
    wr = (widths[:,None]*wx/2).ravel()[:,None]
    hi = np.minimum(1.,d/(2*r))
    u = -1+(1+y)*(hi+1)/2
    other = np.sqrt(r*r+d*d-2*r*d*u)
    w = 2*np.pi*r*r*wr*(hi+1)/2*wy
    cosine = (r-d*u)/other
    radius = np.broadcast_to(r,other.shape).ravel()
    rd = np.r_[radius,other.ravel()]
    rr = np.r_[other.ravel(),radius]
    return rd,rr,np.tile(w.ravel(),2),np.tile(cosine.ravel(),2)


def inward_flux(center, other, d, center_rotation, other_rotation, order):
    u,g = roots_legendre(6*order)
    r = np.sqrt(40**2+d*d-80*d*u)
    f,v,df,_,p = center.sample(np.full_like(u,40.))
    b,t,db,_,h = other.sample(r)
    normal = -(40-d*u)/r
    grad = -center_rotation*df+normal*other_rotation*db
    dz = -center.neutral(40.,1)[0]+normal*other.neutral(r,1)[0]
    phi = center_rotation*f+other_rotation*b
    vel = center_rotation*v+other_rotation*t
    area = 2*np.pi*40**2*g
    return [float(area @ (-2*(phi.conj()*grad).imag)),
            float(area @ (-2*(vel.conj()*grad).real-(p+h)*dz))]


def analyse(D,R,d,n):
    rd,rr,w,cosine = domain(d,[D.edge,R.edge],n)
    a,v,da,z,p = D.sample(rd)
    b0,u0,db0,y,h = R.sample(rr)
    weights = np.vstack((w*(rd<40),w*(rr<40),w))
    out = []
    for phase in (0,1,-1):
        rot = (1,1j,-1j)[{0:0,1:1,-1:2}[phase]]
        b,u,db = rot*b0,rot*u0,rot*db0
        field,vel,chi = a+b,v+u,z+y
        sa,sb = abs(a)**2,abs(b)**2
        interference = 2*(a.conj()*b).real
        density = abs(field)**2
        # Aceleración conjunta menos la suma de las aceleraciones aisladas.
        def coupling(other,other_z,self_z):
            return 2*m.quartic*(other+interference)+m.trilinear*other_z+m.mixed*other_z*(self_z+.5*other_z)
        accel = -coupling(sb,y,z)*a-coupling(sa,z,y)*b
        neutral = -m.trilinear*interference-m.mixed*(sa*y+sb*z+interference*chi)
        force2 = w @ (abs(accel)**2+.5*neutral**2)
        phi_gradient = (m.mass2+2*m.quartic*density+m.trilinear*chi+.5*m.mixed*chi**2)*field
        # Jacobiano real de Q,E en las dos esferas y en la unión completa de los soportes.
        basis = [(a,v,da,db*cosine+da),(1j*a,1j*v,1j*da,db*cosine+da),
                 (b,u,db,da*cosine+db),(1j*b,1j*u,1j*db,da*cosine+db)]
        gram = np.empty((4,4))
        rhs = np.empty(4)
        jac = np.empty((3,2,4))
        for i,(s,t,ds,fullgrad) in enumerate(basis):
            rhs[i] = w @ (t.conj()*accel).real
            for j,(sj,tj,_,_) in enumerate(basis):
                gram[i,j] = w @ (s.conj()*sj+t.conj()*tj).real
            jac[:,0,i] = weights @ (2*(s.conj()*vel+field.conj()*t).imag)
            jac[:,1,i] = weights @ (2*(vel.conj()*t+phi_gradient.conj()*s+fullgrad.conj()*ds).real)
        # Diferencial aplicado al vector de interacción M2 exacto.
        target = np.column_stack((weights @ (2*(field.conj()*accel).imag),
            weights @ (2*(vel.conj()*accel).real+(p+h)*neutral)))
        rates = np.linalg.solve(gram,rhs)
        normres = np.sqrt(max(0.,force2-rhs@rates)/force2)
        diff = jac @ rates-target
        # Normalización euclídea de cada fila; la columna de fase común debe anularse.
        matrix = jac.reshape(6,4)
        scaled = matrix/np.linalg.norm(matrix,axis=1)[:,None]
        singular = np.linalg.svd(scaled,compute_uv=False)
        flux = np.array([inward_flux(D,R,d,1,rot,n),inward_flux(R,D,d,rot,1,n),[0.,0.]])
        out.append(dict(fase=phase,flujo_entrante_exacto=flux.tolist(),
            tasa_reducida=(flux+diff).tolist(),gram_cond=float(np.linalg.cond(gram)),gram=gram.tolist(),
            tasas=rates.tolist(),jac=matrix.tolist(),jac_escalado=scaled.tolist(),singulares=singular.tolist(),
            defecto_fase_comun=float(np.linalg.norm(scaled[:,1]+scaled[:,3])),
            norma_fuerza=float(np.sqrt(force2)),residuo_rel=float(normres),
            fraccion_norma2_chi=float(.5*(w@neutral**2)/force2),
            tasa_contacto_exacta=target.tolist(),error_tasa_balance=diff.tolist()))
    return out


def run():
    prior = json.loads((RES/"contacto_interno_20261126/resultado.json").read_text())["insumos"]
    def state(path):
        return State(ROOT/path,prior[path])
    rec = state("checkpoints/Reserva/paso2_20261117/datos/preparacion.npz")
    rows = []
    for step in ("dt0005","dt001"):
        for case in ("gota_a010","gemelo"):
            donor = state(f"checkpoints/Reserva/paso3_20261118/datos/{step}/{case}/tau300.npz")
            for d in (80,100,120):
                coarse = analyse(donor,rec,d,4)
                fine = analyse(donor,rec,d,8)
                for l,h in zip(coarse,fine):
                    eps = float(np.linalg.norm(np.array(h["jac_escalado"])-l["jac_escalado"],2))
                    rank = sum(s>max(eps,np.finfo(float).eps*6*h["singulares"][0]) for s in h["singulares"])
                    rows.append(dict(dt=step,donante=case,d=d,fase=h["fase"],rango_resuelto=rank,
                        cambio_jac=eps,gruesa=l,fina=h))
    result = dict(orden_columnas=["log_amplitud_D","fase_D","log_amplitud_R","fase_R"],
        orden_filas=["QD","ED","QR","ER","Qglobal","Eglobal"],registros=rows,
        theta_sha256=digest(ROOT/"datos/theta_comun.json"))
    (HERE/"resultado.json").write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,separators=(",",":"))+"\n")


if __name__ == "__main__":
    run()
