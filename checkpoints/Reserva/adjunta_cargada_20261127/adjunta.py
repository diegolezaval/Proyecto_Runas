"""Seis observables del adjunto FV y presupuestos de Duhamel."""
import csv
import gzip
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import bmat, diags, eye, kron
from scipy.sparse.linalg import expm_multiply

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/"defecto_localizado_20261127"))
import localizar as loc
import pulsos

o, g = loc.old, loc.g
i = loc.i40-1
h = 1/32
degree = 48
n = round(104/g.dx)
sw = o.sw[i]
gyro = np.array([[0, 2*o.om, 0], [-2*o.om, 0, 0], [0, 0, 0]])
sign = np.array([1., -1., 1.])


def matrices(n):
    V = np.zeros((n, 3, 3))
    V[:, range(3), range(3)] = -loc.c[:n, 2:5]
    V[:, 0, 2] = V[:, 2, 0] = -np.sqrt(2)*loc.c[:n, 5]
    K = kron(o.T[:n, :n], eye(3)) + diags(V[:, range(3), range(3)].ravel())
    b = np.zeros(3*n-2)
    b[::3] = V[:, 0, 2]
    K = (K+diags([b, b], [-2, 2])).tocsr()
    O = kron(eye(n), gyro).tocsr()
    return K, O


def norms(a):
    # Frobenius simultáneo de tres observables; cada grupo acota la norma 2.
    return np.sqrt(np.einsum("ij,ij->j", a, a).reshape(2, 3).sum(axis=1))


def run():
    K, O = matrices(n)
    Kfull, Ofull = matrices(g.n)
    S = diags(np.tile(sign, n))
    assert (S@K@S-K).nnz == 0 and (S@O@S+O).nnz == 0
    # Rw and Rw' obey the original homogeneous generator.
    R = np.tile(sign, n)[:, None]
    seed = np.zeros((3*n, 6))
    seed[3*i:3*i+3, :3] = np.eye(3)/sw
    w = np.roll(seed, 3, axis=1)
    v = R*(seed-O@w)
    w = R*w
    # Shifted wave energy controls error globally as well as on the crop.
    m = 1-.410
    mu = 1/(2*np.sqrt(m))
    kmax = abs(Kfull).sum(axis=1).max()
    gen = np.sqrt(kmax+1)+1/np.sqrt(m)+2*o.om
    local_factor = np.exp(gen*h)*(gen*h)**(degree+1)/math.factorial(degree+1)
    # Uniform theoretical bound on all truncated Taylor states via recurrence.
    E0 = np.sqrt(np.sum(v*v)+np.sum(w*(K@w+w)))
    boundE = E0*(np.exp(mu*h)+local_factor)**1280
    defect = 1280*local_factor*boundE*np.exp(mu*40)
    # Band 2 is outside the crop. Extension by zero is checked via its face force.
    coupling = abs(o.T[n,n-1])
    bins = np.zeros((320, 5, 2))
    wall = np.zeros(2)
    Ktest, Otest = Kfull, Ofull
    I = eye(3*g.n)
    G = bmat([[None,I],[-Ktest,Otest]], format="csr")
    def packed():
        u = R*w
        return np.vstack((R*v+O@u, u))
    def embed(p):
        a,b = np.split(p, 2)
        return np.vstack([np.pad(t, ((0,3*(g.n-n)),(0,0))) for t in (a,b)])
    p0 = embed(packed())
    ptest = expm_multiply(G.T*(4*h),p0)
    # Three smooth field-space impulses, one per source band, acceleration channel.
    pulses = np.zeros((6*g.n,3))
    for k,center in enumerate((40.,60.1,160.1)):
        idx = np.where(abs(g.r-center)<.09)[0]
        pulses[3*g.n+3*idx+k,k] = 1/np.sqrt(len(idx))
    pulse_end = expm_multiply(G*(4*h),pulses)
    for step in range(1280):
        a, b = w, v
        envelope = np.zeros((5,2))
        edge = np.zeros(2)
        W, V = w.copy(), v.copy()
        for order in range(degree+1):
            projected = b-O@a  # R p_x
            for k,group in enumerate((a[:3*loc.cuts[1]], a[3*loc.cuts[1]:])):
                envelope[k] += norms(group)
            envelope[3] += norms(projected)
            envelope[4] += norms(a)
            edge += norms(a[-3:])
            if order < degree:
                f = h/(order+1)
                a,b = f*b, f*(-K@a+O@b)
                W += a
                V += b
        w,v = W,V
        bins[step//4] = np.maximum(bins[step//4], envelope)
        wall = np.maximum(wall, edge)
        if step==1023:
            kernels_v = (R*w).reshape(n, 3, 6)
            long_pulses = np.column_stack([
                np.einsum("ijk,ij->k", kernels_v, field[:n]) for field in pulsos.pulses(loc)
            ])
        if step==3:
            num = embed(packed())
            exp_err = np.linalg.norm(num-ptest)/np.linalg.norm(ptest)
            differences = num.T@pulses-p0.T@pulse_end
            pulse_err = np.max(abs(differences),axis=0)
            assert exp_err < 1e-10 and max(pulse_err)<1e-11
    remainder = defect + 40*np.exp(40*mu)*coupling*max(wall)
    # Continuous polynomial on each step: add its own exponential-series tail
    # to the propagated nodal error, including the truncation-face estimate.
    remainder += local_factor*boundE*(1+40*np.exp(40*mu)*coupling/np.sqrt(m))
    coarse_remainder = remainder
    # A local defect generated at j has only 40-j*h of subsequent growth.
    # The crop discrepancy at time s enters the full-space Duhamel integral
    # with growth exp(mu*(40-s)); both time factors share the same horizon.
    amplitude = E0*(np.exp(mu*h)+local_factor)**1282
    defect = 1281*local_factor*amplitude
    remainder = defect*(1+40*coupling/np.sqrt(m)) + 40*np.exp(40*mu)*coupling*max(wall)
    bins[:,[0,1,2,4]] += remainder/np.sqrt(m)
    bins[:,3] += remainder*(1+2*o.om/np.sqrt(m))
    source = HERE.parent/"energia_fisica_corregida_20261127/bandas.csv.gz"
    with gzip.open(source,"rt") as stream:
        rows = [r for r in csv.DictReader(stream) if r["caso"]=="gota_a010"]
    assert len(rows)==320
    F = np.array([[float(row[k]) for k in ("ajustada0","ajustada1","ajustada2","pos","vel")] for row in rows])
    # For t in slab j and source in slab i, lag crosses at most two bins.
    kernels = np.maximum(bins, np.concatenate([bins[:1], bins[:-1]]))
    all_terms = np.array([.125*(kernels[:j+1]*F[j::-1,:,None]).sum(axis=0) for j in range(320)])
    dz = all_terms[:,:,1].sum(axis=1)+F[:,3]/sw
    z = all_terms[:,:,0].sum(axis=1)
    weighted = np.exp(.051*(40-np.arange(320)/8))
    old = json.loads((HERE.parent/"interfaz_cargada_20261127/resultado.json").read_text())
    lift = old["interfaz"]["levantamiento_energia"]
    result = dict(paso=h,orden=degree,limite_generador=gen,mu=mu,error_local_rel=local_factor,
        resto_doble_crecimiento=coarse_remainder,error_nodos=defect,envolvente_pared=wall.tolist(),resto_total_energia=remainder,
        exp_rel=exp_err,pulsos_abs=pulse_err.tolist(),pulsos_respuesta=(p0.T@pulse_end).tolist(),
        bandas_truncacion_pos_vel=all_terms[-1].tolist(), z_terminal=z[-1],
        integral_z=.125*sum(z), integral_dz=.125*sum(dz), cinematica_directa=.125*sum(F[:,3])/sw,
        integral_dz_propagada=.125*sum(weighted*dz),
        directa=old["interfaz"]["directa"]*.125*sum(weighted*z),
        restitucion=lift*z[-1],levantada=lift*(z[-1]+.125*sum(weighted*dz)))
    result["pulsos_s32"] = long_pulses.tolist()
    result["errores_s32"] = pulsos.verify(loc, long_pulses, i)
    result["exponencial_directa_s32"] = pulsos.exponential(loc, long_pulses, i, Kfull, Ofull)
    (HERE/"resultado.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    run()
