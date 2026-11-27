"""Comparación exterior FV de la donante. No evoluciona los campos."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import bmat, diags
from scipy.sparse.linalg import splu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "defecto_localizado_20261127"))
import localizar as loc

g, o = loc.g, loc.old
cut = loc.i40
r = g.r[cut:]
w = g.w[cut:]
sw = o.sw[cut:]
n = len(r)
alpha = .2
duration = 40.
source = HERE.parent / "energia_fisica_corregida_20261127/bandas.csv.gz"


def stiffness():
    lap = o.T[cut:, cut:]
    coeff = loc.c[cut:]
    mix = diags(-np.sqrt(2) * coeff[:, 5])
    return bmat([[lap-diags(coeff[:, 2]), None, mix],
                 [None, lap-diags(coeff[:, 3]), None],
                 [mix, None, lap-diags(coeff[:, 4])]], format="csc")


def face_gram(lift):
    fields = lift.reshape(3, n, 3).transpose(1, 0, 2) / sw[:, None, None]
    jump = np.diff(fields, axis=0, prepend=np.zeros((1, 3, 3)),
                   append=np.zeros((1, 3, 3)))
    grad = 4*np.pi*np.einsum("n,nij,nik->jk", loc.face[cut-1:], jump, jump)
    pot = np.zeros((n, 3, 3))
    pot[:, 0, 0], pot[:, 1, 1], pot[:, 2, 2] = -loc.c[cut:, 2:5].T
    pot[:, 0, 2] = pot[:, 2, 0] = -np.sqrt(2)*loc.c[cut:, 5]
    return grad + np.einsum("n,nij,nik,nkl->jl", sw**2, fields, pot, fields)


def static_lift(K):
    B = np.zeros((3*n, 3))
    B[np.arange(3)*n, np.arange(3)] = sw[0]*g.lo[cut]
    L = splu(K).solve(B)
    gram = L.T @ B
    residual = np.linalg.norm(K @ L-B)/np.linalg.norm(B)
    check = np.linalg.norm(face_gram(L)-gram)/np.linalg.norm(gram)
    # Test with distinct trace and derivative, including a gyro term.
    z = np.array([.13, -.21, .17])
    dz = np.array([-.09, .31, -.12])
    y = L @ np.array([.36, .18, -.23])
    v = L @ np.array([-.18, .07, .25])
    x = y + L @ z
    va, vb, vc = v.reshape(3, n)
    gyro = 2*o.om*np.r_[vb, -va, 0*vc]
    dv = -(K @ x) + gyro + B @ z
    dy = v - L @ dz
    rhs_error = np.linalg.norm(dv + K @ y-gyro)/np.linalg.norm(B @ z)
    work = -(y @ (B @ dz))
    work_error = abs(dv @ v + (K @ y) @ dy-work)/abs(work)
    assert max(residual, check, rhs_error, work_error) < 1e-8
    return dict(directa=np.linalg.norm(B, 2), levantamiento_energia=np.sqrt(np.linalg.eigvalsh(gram)[-1]),
                levantamiento_L2=np.linalg.norm(L, 2), energia_por_columna=np.sqrt(np.diag(gram)).tolist(),
                gram=gram.tolist(), residuo=residual, contraste_caras=check,
                identidad_rhs=rhs_error, identidad_trabajo=work_error)


def moving_budget():
    # c_face/w for either endpoint of any internal face touched by the taper.
    face = loc.face[cut:-1]
    active = r[1:] >= 60.
    max_rate = max(max((face/w[:-1])[active]), max((face/w[1:])[active]))
    ratio = np.exp(alpha*g.dx)
    C = max_rate * np.expm1(alpha*g.dx)**2 * ratio
    # gamma multiplies E, hence gamma/2 multiplies sqrt(2E).
    gamma = .102
    mixed = C/(alpha+2*gamma)
    tail = C/(2*(alpha+gamma))
    margins = [gamma-mixed, alpha+gamma-mixed-tail, alpha+gamma-2*tail]
    assert min(margins) > 1e-4
    # Independent test at s=20. Only v at the last flat center and b at
    # the first tapered center. b is the imaginary canonical component.
    k = np.exp(-alpha*np.maximum(r-80., 0))
    d = alpha*k*(r>80)
    i = np.searchsorted(r, 80.)-1
    cross = face[i]*(k[i]-k[i+1])/2
    penalty = (face[i]*(d[i]+d[i+1])+face[i+1]*(d[i+1]+d[i+2]))/4
    potential = -loc.c[cut+i+1, 3]
    penalty += .5*w[i+1]*potential*d[i+1]
    displacement = cross/(2*penalty)
    derivative = cross*displacement - penalty*displacement**2
    energy = .5*w[i]+displacement**2*(.5*w[i+1]*potential*k[i+1] +
        (face[i]*(k[i]+k[i+1])+face[i+1]*(k[i+1]+k[i+2]))/4)
    assert 0 < derivative/energy < gamma
    return dict(gamma=gamma, gamma_fijo=loc.growth, C=C, margenes=margins,
                potencial_minimo=loc.potential_min, test_s20_dE_sobre_E=derivative/energy,
                test_desplazamiento=displacement)


def slab_bounds(gamma, moving, op):
    totals = np.zeros(5)
    with gzip.open(source, "rt") as stream:
        rows = [row for row in csv.DictReader(stream) if row["caso"] == "gota_a010"]
    assert len(rows) == 320
    for i, row in enumerate(rows):
        s = i/8
        assert float(row["t"]) == s+.125
        front = 100-s if moving else 60.
        attenuation = np.exp(-alpha/2*np.maximum(np.array([40., 60., 160.])-front, 0))
        bands = np.array([float(row[f"ajustada{k}"]) for k in range(3)])
        numerical = [op*float(row["pos"]), float(row["vel"])]
        totals += .125*np.exp(gamma*(duration-s)/2)*np.r_[attenuation*bands, numerical]
    return dict(zip(["r40_60_desde_banda0", "r60_160", "r160_256", "posicion", "velocidad"], totals))


def linear_trace(interface, gamma):
    index = cut-1
    archived = json.loads((source.parent/"traza.json").read_text())
    resistance = 1/(4*np.pi*loc.face)
    assert abs(sum(resistance)-archived["resistencia"]) < 1e-12
    local = sum(resistance[index:])
    gradient_ratio = 1+max(0., -archived["min_potencial"])/o.gap
    ka, kz = np.split(o.kap, 2)
    position = np.array([np.sqrt(local*gradient_ratio),
                         np.hypot(ka[index], kz[index])/o.sw[index],
                         abs(o.u[index])/o.sw[index]])
    speed = np.array([1+abs(o.u[index])*2*o.om/np.sqrt(o.gap),
                      abs(o.u[index]*o.gamma), 0.])/o.sw[index]
    integrals = np.zeros(4)
    previous = np.zeros(3)
    with gzip.open(source, "rt") as stream:
        rows = [row for row in csv.DictReader(stream) if row["caso"] == "gota_a010"]
    for row in rows:
        state = np.array([float(row[k]) for k in ("D", "q", "fase")])
        assert np.all(state >= previous)
        previous = state
        z = position @ state
        dz = speed @ state + float(row["pos"])/o.sw[index]
        factor = np.exp(gamma*(duration-float(row["t"])+.125)/2)
        integrals += .125*np.array([z, dz, factor*z, factor*dz])
    restore = interface["levantamiento_energia"]*z
    return dict(r=g.r[index], coef_z=position.tolist(), coef_velocidad=speed.tolist(),
                z40=z, dz_ultimo_intervalo=dz, integral_z=integrals[0],
                integral_dz=integrals[1], integral_propagada_z=integrals[2],
                integral_propagada_dz=integrals[3], inicial=0.,
                directa=interface["directa"]*integrals[2], restitucion=restore,
                levantada=interface["levantamiento_energia"]*integrals[3]+restore)


def main():
    K = stiffness()
    control = moving_budget()
    op = np.sqrt(np.asarray(abs(K).sum(axis=1)).max())
    tail = g.r > 60
    # Uniform for 60 <= front <= 100; bounds for the conversion to physical q,beta
    # and extra S'/S when differentiating variables transformed by S=sqrt(k).
    S = np.exp(-alpha/2*np.maximum(g.r-60, 0))
    projections = dict(cambio_u=np.linalg.norm((1/S-1)*o.u),
                       velocidad_peso_u=alpha/2*np.linalg.norm(o.u[tail]),
                       defecto_fase=o.eps)
    interface = static_lift(K)
    result = dict(traza_lineal=linear_trace(interface, control["gamma"]), sha256_bandas=hashlib.sha256(source.read_bytes()).hexdigest(),
                  operador_posicion=op, interfaz=interface, movil=control,
                  proyecciones=projections,
                  propagacion_movil=slab_bounds(control["gamma"], True, op),
                  propagacion_fija=slab_bounds(loc.growth, False, op))
    (HERE/"resultado.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
