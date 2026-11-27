"""Espectro radial FV en coordenadas canónicas; no evoluciona los campos."""
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.sparse import bmat, diags, eye
from scipy.sparse.linalg import LinearOperator, eigsh, splu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/"referencia_radial_contacto_20261127"))
# El módulo de la referencia también se llama medir; cargarlo con nombre propio.
import importlib.util
spec = importlib.util.spec_from_file_location("referencia", Path(sys.path[0])/"medir.py")
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)


def counts(shift, lap, off, a, z, coupling, amp, v, beta):
    """Inercia LDL por bloques 2x2 y complemento escalar de la ampliación."""
    nnegative = 0
    pa = pz = pc = 0.
    for i in range(len(a)):
        d = lap[i]-shift
        x, y, c = a[i]+d, z[i]+d, coupling[i]
        if i:
            factor = off[i-1]**2/det
            x, y, c = x-factor*pz, y-factor*pa, c+factor*pc
        det = x*y-c*c
        if abs(det) < 1e-14:
            raise ArithmeticError("Pivote singular")
        nnegative += 1 if det < 0 else 2*int(x+y < 0)
        pa, pz, pc = x, y, c
    lu = splu(amp-shift*eye(amp.shape[0], format="csc"))
    schur = -1/beta-v@lu.solve(v)
    return [nnegative, nnegative+int(schur < 0)-1]


def minimum(mat, v, beta, shift):
    dim = len(v)
    lu = splu(mat-shift*eye(dim, format="csc"))
    w = lu.solve(v)
    def invert(x):
        t = lu.solve(x)
        return t-beta*w*(v@t)/(1+beta*(v@w))
    def apply(x):
        return mat@x+beta*v*(v@x)
    op = LinearOperator((dim, dim), matvec=apply)
    val, vec = eigsh(op, k=1, sigma=shift, OPinv=LinearOperator(op.shape, matvec=invert),
                     v0=np.cos(np.arange(dim)*.0123), tol=1e-12)
    return float(val[0]), float(np.linalg.norm(apply(vec[:,0])-val[0]*vec[:,0]))


def evaluate(dx, corrected):
    grid = ref.Grid(dx)
    f,z = grid.equilibrium()[:2] if corrected else ref.operator(grid)[:2]
    m, omega = ref.m, ref.om
    phase = m.mass2+2*m.quartic*f*f+m.trilinear*z+.5*m.mixed*z*z-omega**2
    a = phase+4*m.quartic*f*f
    heavy = m.mediator**2+m.mixed*f*f
    coupling = np.sqrt(2)*f*(m.trilinear+m.mixed*z)
    lap = grid.A.diagonal()
    off = -np.sqrt(grid.lo[1:]*grid.hi[:-1])
    T = diags([off,lap,off],[-1,0,1],format="csc")
    amp = bmat([[T+diags(a),diags(coupling)],[diags(coupling),T+diags(heavy)]],format="csc")
    u = np.sqrt(grid.w)*f
    u /= np.linalg.norm(u)
    v = np.r_[u,np.zeros(grid.n)]
    beta = 4*omega**2
    free,rf = minimum(amp,v,0,-.05)
    fixed,rc = minimum(amp,v,beta,.17)
    def inertia(t):
        return counts(t,lap,off,a,heavy,coupling,amp,v,beta)
    checks = [inertia(t) for t in (-.05,0,.17)]
    edges = [[inertia(l-1e-7)[i],inertia(l+1e-7)[i]] for i,l in enumerate((free,fixed))]
    phase_op = T+diags(phase)
    eig,vec = eigh_tridiagonal(lap+phase,off,select="i",select_range=(0,1))
    pres = np.linalg.norm(phase_op@vec-vec*eig,axis=0)
    defect = np.linalg.norm(phase_op@u)
    overlap = abs(vec[:,0]@u)
    # min Rayleigh on u-perp bounded using the angle with the true lowest vector.
    perp = eig[1]-(eig[1]-eig[0])*np.linalg.norm(vec[:,0]-(u@vec[:,0])*u)**2
    passed = (checks[0]==[0,0] and checks[1]==[1,0] and checks[2][1]==0
              and edges==[[0,1],[0,1]] and perp>.17 and max(rf,rc,*pres)<1e-7)
    return dict(dx=dx,Newton=corrected,libre=free,fijo=fixed,fase=eig.tolist(),
                residuos=[rf,rc,*pres],defecto_fase=defect,alineacion=overlap,
                fase_perp_inferior=perp,inercia=checks,intervalos=edges,puerta=bool(passed))


if __name__=="__main__":
    rows=[evaluate(h,corrected) for h in (.05,.025) for corrected in (False,True)]
    path=HERE.parents[2]/"validacion/P06/rama/resultados.json"
    def spectra(node):
        if isinstance(node, dict):
            if node.get("n")==1999 and node.get("radius")==80 and node.get("ell")==0 and "H_fixed_charge" in node:
                yield node
            for child in node.values():
                yield from spectra(child)
        elif isinstance(node,list):
            for child in node:
                yield from spectra(child)
    target=[s for s in spectra(json.loads(path.read_text())) if abs(s["H_amplitude"][0]+.022815)<1e-6]
    assert len(target)==1
    nodal=target[0]
    out=dict(filas=rows,nodal=[nodal["H_amplitude"][0],nodal["H_fixed_charge"][0],nodal["H_phase"][1]],
             candidata=all(r["puerta"] for r in rows) and all(rows[i+1]["defecto_fase"]<rows[i]["defecto_fase"] for i in (0,2)))
    (HERE/"resultado.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
