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
            assert tests[1] < .32*tests[0]+1e-13
            assert tests[1] < 1e-4*max(abs(adjoint[:,column]))+1e-10
            errors.append(tests)
    return errors
