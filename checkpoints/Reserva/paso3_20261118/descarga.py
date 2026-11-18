"""Primera descarga de Reserva, acción axisimétrica en anillos de volumen finito."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import ctypes as ct
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import time

import numpy as np
from scipy.interpolate import CubicSpline
from calibrar import envolvente, soporte
from retencion import DX, Grid, HERE, PASO2, dump, sha

MALLAS = {"espacial": (.40, .01), "intermedia": (.30, .01), "fina": (.30, .005)}
RAMAS = ("cargada", "gemelo", "directa")
COLUMNAS = "s E Q E_d Q_d E_r Q_r E_ext Q_ext trabajo".split()
PTR = ct.POINTER(ct.c_double)
IPTR = ct.POINTER(ct.c_int)


class MallaC(ct.Structure):
    _fields_ = ([("nr", ct.c_int), ("nz", ct.c_int)]
                + [(k, PTR) for k in ("rm", "rp", "zm", "zp", "vr", "vz", "wd", "wr", "theta")]
                + [("ns", ct.c_int), ("ind", IPTR), ("forma", PTR), ("dVsrc", PTR)])


def eje(largo, fino, h, transicion, ancho, lejano):
    def suave(x):
        u = min(1., max(0., x))
        return u*u*(3-2*u)
    e = [0.]
    while e[-1] < largo:
        x = e[-1]
        dh = h*(1 + .35*suave((x-fino)/ancho) + 1.75*suave((x-transicion)/lejano))
        if largo-x < 1.5*dh:
            e.append(largo)
        else:
            e.append(x+dh)
    return np.array(e)


def fraccion_esfera(re, ze, centro):
    u = ze - centro
    def primitivo(c):
        t = np.maximum(40.**2-c*c, 0.)[:, None]
        b = np.clip(u, -np.sqrt(t), np.sqrt(t))
        return t*b - b**3/3
    casquete = np.diff(primitivo(re[:-1])-primitivo(re[1:]), axis=1)
    return np.ascontiguousarray(np.clip(casquete/(np.diff(re**2)[:,None]*np.diff(ze)), 0., 1.))


class Malla:
    def __init__(self, h):
        self.re = eje(320., 45., h, 200., 70., 100.)
        medio = eje(384., 100., h, 230., 70., 100.)
        self.ze = np.r_[-medio[:0:-1], medio]
        self.r = (self.re[1:]+self.re[:-1])/2
        self.z = (self.ze[1:]+self.ze[:-1])/2
        nr, nz = len(self.r), len(self.z)
        self.shape = (3, nr+2, nz+2)
        vr, vz = np.pi*np.diff(self.re**2), np.diff(self.ze)
        cr = 2*np.pi*self.re[1:]/np.diff(np.r_[self.r, self.re[-1]])
        cz = 1/np.diff(np.r_[self.ze[0], self.z, self.ze[-1]])
        wd, wr = (fraccion_esfera(self.re, self.ze, c) for c in (-60., 60.))
        v_esfera = 4*np.pi*40**3/3
        for fr in (wd, wr):
            if abs(np.sum(vr[:,None]*vz*fr)/v_esfera-1) > 1e-11:
                raise ArithmeticError("Volumen del núcleo")
        self.rd = np.hypot(self.r[:,None], self.z+60.)
        self.rr = np.hypot(self.r[:,None], self.z-60.)
        si, sj = np.nonzero(self.rd < 6)
        ind = np.ascontiguousarray((si+1)*(nz+2)+sj+1, dtype=np.int32)
        valores = [np.r_[0., cr[:-1]]/vr, cr/vr, cz[:-1]/vz, cz[1:]/vz,
                   vr, vz, wd, wr, Grid(DX).theta, soporte(self.rd[si,sj]), vr[si]*vz[sj]]
        self.arrays = [np.ascontiguousarray(v, dtype=float) for v in valores]
        self.ind = ind
        ptrs = [v.ctypes.data_as(PTR) for v in self.arrays]
        self.c = MallaC(nr,nz,*ptrs[:9],len(ind),ind.ctypes.data_as(IPTR),*ptrs[9:])


def preparado(path, dist):
    """Spline par en el origen y valor del campo nulo en la pared radial original."""
    with np.load(path, allow_pickle=False) as estado:
        qv = np.r_[estado["q"],estado["v"]].copy()
        dx = float(estado["dx"])
    r = (np.arange(qv.shape[1])+.5)*dx
    extendido = np.c_[qv[:,2::-1], qv, np.zeros(6)]
    spline = CubicSpline(np.r_[-r[2::-1], r, r[-1]+dx/2], extendido, axis=1)
    centro = spline(0.)
    fase = -np.angle(centro[0]+1j*centro[1])
    v = np.zeros((6,*dist.shape))
    dentro = dist < r[-1]+dx/2
    v[:,dentro] = spline(dist[dentro])
    for k in (0,3):
        rotado = np.exp(1j*fase)*(v[k]+1j*v[k+1])
        v[k],v[k+1] = rotado.real,rotado.imag
    return v, fase


def compilar(temp):
    lib = Path(temp)/"axis.so"
    subprocess.run(["cc","-std=c11","-O3","-march=native","-ffp-contract=off","-fopenmp-simd",
                    "-shared","-fPIC",str(HERE/"axisimetrico.c"),"-lm","-o",str(lib)],check=True)
    native = ct.CDLL(str(lib))
    ptrm = ct.POINTER(MallaC)
    vec = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    native.avanzar.argtypes = [ptrm,vec,vec,ct.c_int,ct.c_int,ct.c_double,ct.c_double,vec]
    native.observar.argtypes = [ptrm,vec,vec,vec,ct.c_double,ct.c_double,ct.c_int,vec]
    native.avanzar.restype = native.observar.restype = None
    return native


def insumos(base):
    ret = json.loads((base/"RETENCION.json").read_text())
    cal = json.loads((base/"calibracion/CALIBRACION.json").read_text())
    if not ret["aprobada"] or cal["error_rel"] > .02:
        raise ValueError("Puertas anteriores")
    prep = PASO2/"datos/preparacion.npz"
    huella = sha(prep)
    for f in ("MANIFIESTO.json","REPRODUCCION_INDEPENDIENTE.json"):
        if json.loads((PASO2/f).read_text())["archivos"]["datos/preparacion.npz"]["sha256"] != huella:
            raise ValueError("Huella de preparación del receptor")
    paths = dict(receptor=prep, cargada=base/"datos/dt0005/gota_a010/tau300.npz",
                 gemelo=base/"datos/dt0005/gemelo/tau300.npz")
    if sha(paths["gemelo"]) != cal["sha256_gemelo_300"]:
        raise ValueError("Gemelo distinto del calibrado")
    return paths, cal["A"]


def rama(native, mesh, nombre, caso, dt, paths, amplitud, dest, hasta):
    d = dest/nombre/caso
    d.mkdir(parents=True)
    q = np.zeros(mesh.shape)
    v = np.zeros_like(q)
    p = np.zeros_like(q)
    receptor, fr = preparado(paths["receptor"], mesh.rr)
    q[:,1:-1,1:-1] = receptor[:3]
    v[:,1:-1,1:-1] = receptor[3:]
    del receptor
    fases = {"receptor":fr}
    if caso != "directa":
        donante, fd = preparado(paths[caso], mesh.rd)
        q[:,1:-1,1:-1] += donante[:3]
        v[:,1:-1,1:-1] += donante[3:]
        del donante
        fases["donante"] = fd
    obs, trabajo = np.zeros(8), np.zeros(1)
    m = ct.byref(mesh.c)
    n = round(1/dt)
    if n%2 or n*dt != 1:
        raise ValueError("Se necesitan pares de pasos por muestra")
    native.observar(m,q,p,v,dt,0.,0,obs)
    native.observar(m,q,p,v,dt,0.,2,obs)
    dump(d/"origen.json",dict(sha256={k:sha(paths[k]) for k in
        (("receptor",) if caso=="directa" else ("receptor",caso))},
        rotacion_rad=fases,dt=dt,h=MALLAS[nombre][0],nr=mesh.c.nr,nz=mesh.c.nz,A=amplitud))
    inicio=time.monotonic()
    with (d/"serie.csv").open("w", buffering=1) as csv:
        csv.write(",".join(COLUMNAS)+"\n")
        for s in range(hasta+1):
            if s:
                native.avanzar(m,q,p,n,(s-1)*n,dt,amplitud,trabajo)
                native.observar(m,q,p,v,dt,amplitud*envolvente(s),1,obs)
            if not np.isfinite(obs).all() or not np.isfinite(trabajo[0]):
                raise FloatingPointError(f"{nombre} {caso} s={s}")
            csv.write(",".join(format(a,".17g") for a in [s,*obs,*trabajo])+"\n")
            if s in (8,60,120,180,240):
                print(nombre,caso,"s",s,"seg",round(time.monotonic()-inicio,1),flush=True)
    np.savez_compressed(d/f"s{hasta}.npz",q=q[:,1:-1,1:-1],v=v[:,1:-1,1:-1],
                        rho_caras=mesh.re,z_caras=mesh.ze,s=hasta,dt=dt,trabajo=trabajo[0],A=amplitud)


def ejecutar(root, dest, nombres, casos, hasta, jobs):
    paths, amplitud = insumos(root)
    with TemporaryDirectory() as tmp, ThreadPoolExecutor(max_workers=jobs) as pool:
        native = compilar(tmp)
        mallas = {h:Malla(h) for h in {MALLAS[k][0] for k in nombres}}
        tareas = [pool.submit(rama,native,mallas[MALLAS[k][0]],k,c,MALLAS[k][1],paths,
                              amplitud,dest,hasta) for k in nombres for c in casos]
        for tarea in tareas:
            tarea.result()


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("destino",type=Path)
    p.add_argument("--mallas",nargs="+",choices=MALLAS,default=list(MALLAS))
    p.add_argument("--ramas",nargs="+",choices=RAMAS,default=list(RAMAS))
    p.add_argument("--hasta",type=int,default=240)
    p.add_argument("--procesos",type=int,default=3)
    args=p.parse_args()
    ejecutar(HERE,args.destino,args.mallas,args.ramas,args.hasta,args.procesos)
