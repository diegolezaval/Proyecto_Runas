"""Prueba radial de Reserva. Python prepara la acción y mide inventarios; C integra las trayectorias."""
import argparse
import ctypes
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.sparse import bmat, diags
from scipy.sparse.linalg import spsolve

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "herramientas"))
from modelo_m2 import BENCHMARK as model

PROFILE = ROOT / "validacion/P06/rama/perfil_w0.90000.csv"
THETA = ROOT / "datos/theta_comun.json"
OMEGA, TMAX, RADIUS = .9, 240, 256.
GRIDS = {"espacial": (.05, .002), "temporal": (.025, .002), "fina": (.025, .001)}
KICKS = {"menos": -.005, "libre": 0., "mas": .005}
AMPLITUDES = {"a010": .01, "a020": .02}
NAMES = ("tau E Q E40 Q40 E60 Q60 perfil40 phi_c chi_c "
         "flujoE40 flujoQ40 salidaE40 flujoE60 flujoQ60 salidaE60").split()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)+"\n")


class Grid:
    def __init__(self, dx):
        self.dx = dx
        self.n = round(RADIUS/dx)
        edges = np.arange(self.n+1)*dx
        self.r = .5*(edges[1:]+edges[:-1])
        self.w = np.diff(edges**3)/3
        self.c = edges[1:-1]**2/dx
        self.wall = 2*RADIUS**2/dx
        self.lo = np.r_[0., self.c]/self.w
        self.hi = np.r_[self.c, self.wall]/self.w
        self.A = diags((-self.lo[1:],self.lo+self.hi,-self.hi[:-1]),(-1,0,1),format="csc")
        self.theta = np.array([model.mass2, model.mediator**2, model.quartic,
                               model.trilinear, model.mixed])
        self.core = round(40/dx)
        self.port = round(60/dx)

    def equilibrium(self):
        raw = np.loadtxt(PROFILE, delimiter=",", skiprows=1)
        f,z = [np.where(self.r<raw[-1,0],
                        CubicHermiteSpline(raw[:,0],raw[:,j],raw[:,j+1])(np.minimum(self.r,raw[-1,0])),0.)
               for j in (1,3)]
        initial = f.copy()
        for iteration in range(10):
            ff, zz = model.forces(f,z,OMEGA)
            residual = np.r_[self.A@f+ff, self.A@z+zz]
            if max(abs(residual)) < 2e-9:
                break
            jac = model.amplitude_jacobian(f,z,OMEGA)
            matrix = bmat([[self.A+diags(jac[0,0]),diags(jac[0,1])],
                           [diags(jac[1,0]),self.A+diags(jac[1,1])]],format="csc")
            correction = spsolve(matrix, -residual)
            f += correction[:self.n]
            z += correction[self.n:]
        else:
            raise ArithmeticError("Equilibrio sin convergencia")
        return f,z,dict(residuo_inf=float(max(abs(residual))),correcciones=iteration,
                        cambio_rel_f=float(np.sqrt(self.w@(f-initial)**2/(self.w@(initial**2)))))

    def measure(self, q, v, reference):
        a,b,z = q[:,1:-1]
        va,vb,vz = v[:,1:-1]
        mod = np.hypot(a,b)
        bulk = self.w*(va*va+vb*vb+.5*vz*vz+model.potential(mod,z))
        charge = 8*np.pi*self.w*(a*vb-b*va)
        faces = self.c*(np.diff(a)**2+np.diff(b)**2+.5*np.diff(z)**2)
        boundary = self.wall*(a[-1]**2+b[-1]**2+.5*z[-1]**2)
        out = [4*np.pi*(bulk.sum()+faces.sum()+boundary), charge.sum()]
        for cut in (self.core,self.port):
            out += [4*np.pi*(bulk[:cut].sum()+faces[:cut-1].sum()+.5*faces[cut-1]),charge[:cut].sum()]
        c = self.core
        err = np.sqrt(self.w[:c]@(mod[:c]-reference[:c])**2/(self.w[:c]@reference[:c]**2))
        return [*out,err,mod[0],z[0]]

    def acceleration(self,q):
        a,b,z = q
        density = a*a+b*b
        fac = model.mass2+2*model.quartic*density+model.trilinear*z+.5*model.mixed*z*z
        return np.array([-self.A@a-fac*a, -self.A@b-fac*b,
                         -self.A@z-(model.mediator**2+model.mixed*density)*z-model.trilinear*density])


def initial_background(f,z,kick,r):
    q = np.array([f,np.zeros_like(f),z])
    v = np.array([kick*f*np.exp(-(r/12)**2),OMEGA*f,np.zeros_like(f)])
    return q,v


def native(work):
    libpath = work/"radial.so"
    subprocess.run(["cc","-O3","-std=c11","-ffp-contract=off","-shared","-fPIC",
                    str(HERE/"radial.c"),"-lm","-o",str(libpath)],check=True)
    fun = ctypes.CDLL(str(libpath)).advance
    ptr = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    fun.argtypes = [ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_double]+[ptr]*6
    fun.restype = None
    return fun


def evolve(grid, dt, q, v, f, fun, directory):
    directory.mkdir(parents=True,exist_ok=True)
    q,v = (np.pad(x,((0,0),(1,1))) for x in (q,v))
    sums = np.zeros(6)
    rows = []
    for clock in range(2*TMAX+1):
        if clock:
            fun(grid.n,round(.5/dt),dt,grid.dx,grid.lo,grid.hi,grid.theta,q,v,sums)
        rows.append([clock/2,*grid.measure(q,v,f),*sums])
    values=np.asarray(rows)
    if not np.isfinite(values).all():
        raise FloatingPointError(directory)
    np.savetxt(directory/"serie.csv",values,delimiter=",",header=",".join(NAMES),comments="",fmt="%.16g")
    np.savez_compressed(directory/"estado.npz",tau=TMAX,dx=grid.dx,dt=dt,q=q[:,1:-1],v=v[:,1:-1])


def series(folder):
    return np.genfromtxt(folder/"serie.csv",delimiter=",",names=True)


def stability(work,fun,jobs):
    def one_mesh(item):
        name,(dx,dt)=item
        grid=Grid(dx)
        f,z,fit=grid.equilibrium()
        rows={}
        for label,kick in KICKS.items():
            folder=work/name/label
            q,v=initial_background(f,z,kick,grid.r)
            evolve(grid,dt,q,v,f,fun,folder)
            s=series(folder)
            excess=(s["E"]-s["E40"])-(s["E"][0]-s["E40"][0])
            rows[label]=dict(eta=kick,E0=s["E"][0],Q0=s["Q"][0],Q40_0=s["Q40"][0],
                Q40_final=s["Q40"][-1],min_fraccion_Q40=min(s["Q40"]/s["Q40"][0]),
                error_perfil_max=max(s["perfil40"]),deriva_E=max(abs(s["E"]/s["E"][0]-1)),
                deriva_Q=max(abs(s["Q"]/s["Q"][0]-1)),incremento_ext_max=max(excess),
                Eext_final=s["E"][-1]-s["E40"][-1],flujo_E40_neto=s["flujoE40"][-1],
                flujo_E40_saliente=s["salidaE40"][-1],flujo_Q40_neto=s["flujoQ40"][-1],
                cierre_flujo_E40=max(abs(s["E40"]-s["E40"][0]+s["flujoE40"])))
            print("estabilidad",name,label,flush=True)
        return name,dict(equilibrio=fit,casos=rows)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        grids=dict(pool.map(one_mesh,GRIDS.items()))
    drifts=[abs(grids[g]["casos"][k]["min_fraccion_Q40"]-grids["temporal"]["casos"][k]["min_fraccion_Q40"])
            for k in KICKS for g in ("fina","espacial")]
    ok=all(r["min_fraccion_Q40"]>.99 and r["deriva_E"]<2e-4 and r["deriva_Q"]<1e-9
           and r["error_perfil_max"]<.05 and r["incremento_ext_max"]<1e-3*r["E0"]
           for rec in grids.values() for r in rec["casos"].values()) and max(drifts)<.002
    dump(work/"ESTABILIDAD.json",dict(aprobada=bool(ok),mallas=grids,
                                      mayor_cambio_retencion=max(drifts),muestreo_tau=.5))
    return ok


def prepare(grid,dt,f,z,folder):
    """Resuelve con fuentes prescritas en el tiempo. La potencia usa el estado realmente obtenido."""
    folder.mkdir(parents=True,exist_ok=True)
    q=np.zeros((3,grid.n))
    v=np.zeros_like(q)
    lap_f,lap_z=-grid.A@f,-grid.A@z
    def drive(t):
        x=t/8
        b=x**3*(10-15*x+6*x*x)
        bp=30*x*x*(1-x)**2/8
        bpp=60*x*(1-x)*(1-2*x)/64
        density=(b*f)**2
        zb=b*b*z
        residual=(bpp-OMEGA**2*b)*f-b*lap_f + b*f*(
            model.mass2+2*model.quartic*density+model.trilinear*zb+.5*model.mixed*zb**2)
        imag=2*OMEGA*bp*f
        c,s=np.cos(OMEGA*t),np.sin(OMEGA*t)
        return np.array([c*residual-s*imag,s*residual+c*imag,
            2*(bp*bp+b*bpp)*z-b*b*lap_z+(model.mediator**2+model.mixed*density)*zb+
            model.trilinear*density])
    def rates(source):
        p=8*np.pi*(grid.w@(v[0]*source[0]+v[1]*source[1]))
        pz=4*np.pi*(grid.w@(v[2]*source[2]))
        dq=8*np.pi*(grid.w@(q[0]*source[1]-q[1]*source[0]))
        return np.array([p,pz,dq,max(p,0.),max(pz,0.)])
    acc=grid.acceleration(q)+drive(0.)
    prev=np.zeros(5)
    ledger=np.zeros(5)
    for step in range(1,round(8/dt)+1):
        v+=.5*dt*acc
        q+=dt*v
        source=drive(step*dt)
        acc=grid.acceleration(q)+source
        v+=.5*dt*acc
        curr=rates(source)
        ledger+=.5*dt*(prev+curr)
        prev=curr
    phase=np.exp(-1j*OMEGA*8)
    for fields in (q,v):
        rotated=phase*(fields[0]+1j*fields[1])
        fields[0],fields[1]=rotated.real,rotated.imag
    p,m=grid.measure(np.pad(q,((0,0),(1,1))),np.pad(v,((0,0),(1,1))),f),ledger
    info=dict(E=p[0],Q=p[1],trabajo_Phi=m[0],trabajo_chi=m[1],carga_fuente=m[2],
        entrada_positiva_Phi=m[3],entrada_positiva_chi=m[4],trabajo_devuelto=m[3]+m[4]-m[0]-m[1],
        error_balance_E=abs((m[0]+m[1])/p[0]-1),error_balance_Q=abs(m[2]/p[1]-1),
        error_perfil=p[6],error_chi_rel=float(np.sqrt(grid.w@(q[2]-z)**2/(grid.w@(z*z)))),
        error_E_objetivo=abs(p[0]/2525.658909869193-1),error_Q_objetivo=abs(p[1]/2745.7739206251663-1))
    info["aprobada"]=bool(max(info[k] for k in ("error_balance_E","error_balance_Q","error_perfil"))<3e-4)
    np.savez_compressed(folder/"estado.npz",tau=0.,t_preparacion=8.,dx=grid.dx,dt=dt,q=q,v=v)
    dump(folder/"presupuesto.json",info)
    return q,v,info


def envelope(s):
    support=abs(s)<24
    angle=np.pi*s/48
    b=np.where(support,np.cos(angle)**4,0.)
    derivative=np.where(support,-np.pi/12*np.sin(angle)*np.cos(angle)**3,0.)
    return b,derivative


def packet(r,amplitude):
    nu=3.2
    k=np.sqrt(nu*nu-model.mass2)
    s=r-120
    b,bp=envelope(s)
    phase=amplitude*np.exp(1j*k*s)/r
    phi,vel=phase*b,phase*(1j*nu*b+(k/nu)*bp)
    return np.array([phi.real,phi.imag,np.zeros_like(r)]),np.array([vel.real,vel.imag,np.zeros_like(r)])


def contact(work,fun,jobs):
    if not json.loads((work/"ESTABILIDAD.json").read_text())["aprobada"]:
        raise ValueError("El contraste de estabilidad exige detenerse")
    def one_mesh(item):
        name,(dx,dt)=item
        grid=Grid(dx)
        f,z,_=grid.equilibrium()
        q,v,prep=prepare(grid,dt,f,z,work/name/"preparacion")
        if not prep["aprobada"]:
            raise ValueError(f"Preparación fallida en {name}")
        evolve(grid,dt,q,v,f,fun,work/name/"gemelo")
        for label,a in AMPLITUDES.items():
            dq,dv=packet(grid.r,a)
            for medium,baseq,basev in (("gota",q,v),("vacio",0.,0.)):
                folder=work/name/(medium+"_"+label)
                evolve(grid,dt,baseq+dq,basev+dv,f,fun,folder)
                print("pulso",name,medium,label,flush=True)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(one_mesh,GRIDS.items()))


def cut(s,time):
    return int(np.flatnonzero(s["tau"]==time)[0])


def response(work,name,label):
    folder=work/name
    bg=series(folder/"gemelo")
    got=series(folder/("gota_"+label))
    vac=series(folder/("vacio_"+label))
    last,early=cut(got,240),cut(got,220)
    mid=cut(got,105)
    out={}
    for x in ("E","Q"):
        net=got["flujo"+x+"60"]-bg["flujo"+x+"60"]
        inside=got[x+"60"]-bg[x+"60"]
        core=got[x+"40"]-bg[x+"40"]
        # Retirar también la diferencia inicial si una cola toca el núcleo.
        inside-=inside[0]
        core-=core[0]
        inc=-net[mid]
        reflected=net[last]-net[mid]
        invac=-vac["flujo"+x+"60"][mid]
        packet0=got[x][0]-bg[x][0]
        shifts=[abs(net[cut(got,t)]-net[mid]) for t in (100,110)]
        out[x]=dict(fuente_inicial=packet0,entrada=inc,reflejada=reflected,
            absorbida=inc-reflected,nucleo=core[last],puerto=inside[last],anillo=inside[last]-core[last],
            cambio_220_a_240=abs(net[last]-net[early]),corte_100_110=max(shifts),
            cierre_final=abs(net[last]+inside[last]),cierre_max=max(abs(net+inside)),
            vacio_saldo=abs(vac["flujo"+x+"60"][last]),vacio_entrada=invac,
            vacio_inventario=vac[x][0],vacio_reflejada=vac["flujo"+x+"60"][last]+invac)
    dif=out["E"]["nucleo"]-OMEGA*out["Q"]["nucleo"]
    with (np.load(folder/("gota_"+label)/"estado.npz",allow_pickle=False) as on,
          np.load(folder/"gemelo"/"estado.npz",allow_pickle=False) as off):
        grid=Grid(GRIDS[name][0])
        c=grid.core
        a=np.hypot(*on["q"][:2,:c]);b=np.hypot(*off["q"][:2,:c])
        change=np.sqrt(grid.w[:c]@(a-b)**2/(grid.w[:c]@(b*b)))
        dz=on["q"][2,:c]-off["q"][2,:c]
        chi_change=np.sqrt(grid.w[:c]@(dz*dz)/(grid.w[:c]@(off["q"][2,:c]**2)))
    out.update(exceso_sobre_omega_delta_Q=dif,cambio_rel_modulo_Phi=change,cambio_rel_chi=chi_change,
               cambio_fi_centro=got["phi_c"][-1]-bg["phi_c"][-1],
               fraccion_absorbida=out["E"]["absorbida"]/out["E"]["entrada"])
    for key,s in (("gota",got),("vacio",vac),("gemelo",bg)):
        out["derivas_"+key]={x:max(abs(s[x]/s[x][0]-1)) for x in ("E","Q")}
    return out


def decide(work):
    rows={g:{label:response(work,g,label) for label in AMPLITUDES} for g in GRIDS}
    gates={}
    for label in AMPLITUDES:
        gates[label]={}
        for x in ("E","Q"):
            f,t,c=(rows[g][label][x] for g in ("fina","temporal","espacial"))
            terms=dict(espacio=abs(c["absorbida"]-t["absorbida"]),
                       tiempo=abs(t["absorbida"]-f["absorbida"]),
                       vacio=f["vacio_saldo"],flujo_inventario=f["cierre_max"],
                       espera=f["cambio_220_a_240"],separacion=f["corte_100_110"])
            u=max(terms.values())
            gates[label][x]=dict(U=u,componentes=terms,senal_sobre_U=f["absorbida"]/u,
                 signo_y_resolucion=bool(f["absorbida"]>3*u),
                 nucleo_puerto=bool(abs(f["anillo"])<=max(3*u,1e-8)))
    scaling=abs(rows["fina"]["a010"]["fraccion_absorbida"]/rows["fina"]["a020"]["fraccion_absorbida"]-1)
    balances=all(r["derivas_"+s]["E"]<2e-4 and r["derivas_"+s]["Q"]<1e-9 for g in rows.values()
                 for r in g.values() for s in ("gota","vacio","gemelo"))
    ok=balances and scaling<.25 and all(v["signo_y_resolucion"] and v["nucleo_puerto"]
                        for case in gates.values() for v in case.values())
    result=dict(status="CONTACTO_FINITO_RESUELTO" if ok else "CONTACTO_FINITO_NO_SUPERA_LA_PUERTA",
        mediciones=rows,incertidumbre_empirica=gates,discrepancia_escalado=scaling,
        balances_aprobados=bool(balances),habilita_disenar_paso3=bool(ok),ciclo_realizado=False,
        preparacion={g:json.loads((work/g/"preparacion/presupuesto.json").read_text()) for g in GRIDS})
    dump(work/"CONTACTO.json",result)
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fase",choices=["estabilidad","contacto","medidas"])
    parser.add_argument("salida",type=Path)
    parser.add_argument("--procesos",type=int,choices=[1,2,3],default=3)
    args=parser.parse_args()
    args.salida=args.salida.resolve()
    args.salida.mkdir(parents=True,exist_ok=True)
    if sha(PROFILE)!="9037fb7f1fa691fe5d8712efee3092d26cc2303b95853694cb7a2539ec1f5574" or sha(THETA)!="ccba93368f572cae3ba1727ecb454a08491c508ee93d207528b8c5527c0e0cc3":
        raise ValueError("Revisar la identidad de los insumos")
    if args.fase=="estabilidad":
        stability(args.salida,native(args.salida),args.procesos)
    if args.fase=="contacto":
        contact(args.salida,native(args.salida),args.procesos)
    if args.fase in ("contacto","medidas"):
        print(decide(args.salida)["status"])
