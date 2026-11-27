"""Reciprocidad a s=32 con el avance homogéneo del proyecto en toda la malla."""
import ctypes
from pathlib import Path
import subprocess
import tempfile

import numpy as np


def pulses(loc):
    sources = []
    for left in [39.,60.,160.]:
        coordinate = (loc.g.r-left)/1.5
        pulse = np.zeros_like(coordinate)
        inside = (coordinate>0) & (coordinate<1)
        pulse[inside] = np.sin(np.pi*coordinate[inside])**4
        field = pulse[:,None]*np.array([[1.,.5,-.25]])
        sources.append(field/np.linalg.norm(field))
    return sources


def verify(loc, adjoint, index):
    ptr = np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
    c = loc.c.copy()
    c[:,7:] = 0.
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        lib = Path(tmp)/"paso.so"
        subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",
                        str(loc.ref.HERE/"tangente.c"),"-lm","-o",str(lib)],check=True)
        step = ctypes.CDLL(str(lib)).advance
        step.argtypes = [ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_double,ptr,ptr,ptr]
        step.restype = None
        for column, field in enumerate(pulses(loc)):
            tests = []
            for dt in [.005,.0025]:
                v = np.ascontiguousarray(field/loc.old.canon)
                x = np.zeros_like(v)
                step(loc.g.n,round(32/dt),dt,loc.om,c,x,v)
                physical = np.r_[x[index],v[index]]*np.tile([np.sqrt(2),np.sqrt(2),1.],2)
                tests.append(np.max(abs(physical-adjoint[:,column])))
            errors.append(tests)
    return errors

def exponential(loc, adjoint, index, K, O):
    from scipy.sparse import bmat, eye
    from scipy.sparse.linalg import expm_multiply
    # Similarity on velocity limits the number of products in the exponential.
    scale = 100.
    G = bmat([[None, scale*eye(K.shape[0])], [-K/scale,O]], format="csr")
    force = np.column_stack([field.ravel() for field in pulses(loc)])
    initial = np.vstack([np.zeros_like(force),force/scale])
    forward = expm_multiply(32*G,initial,traceA=0.)
    x, v = np.split(forward,2)
    sl = slice(3*index,3*index+3)
    observed = np.vstack([x[sl],scale*v[sl]])/loc.old.sw[index]
    error = np.max(abs(observed-adjoint),axis=0)
    assert max(error)<1e-10
    return error.tolist()
