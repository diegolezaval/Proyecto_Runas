"""Respuesta elíptica y compatibilidad dinámica instantánea del contacto."""
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent
sys.path.insert(0,str(RES/"tangente_contacto_20261126"))
from proyectar import State, m, ROOT, digest


class Cylinder:
    def __init__(self,R,L,dx):
        self.dx = dx
        self.r = ((np.arange(round(R/dx))+.5)*dx)[:,None]
        self.z = (np.arange(round(2*L/dx))+.5)*dx-L
        self.weight = 2*np.pi*self.r*dx**2

    def inner(self,a,b):
        return float(np.sum((a.conj()*b).real*self.weight))

    def lap(self,x):
        # Volúmenes anulares, flujo axial nulo en r=0, Dirichlet en caras exteriores.
        h = self.dx
        lap = np.zeros_like(x)
        diff = (self.r[:-1]+h/2)*np.diff(x,axis=0)/h**2
        lap[:-1] += diff/self.r[:-1]
        lap[1:] -= diff/self.r[1:]
        lap[-1] -= 2*(self.r[-1]+h/2)*x[-1]/(self.r[-1]*h**2)
        diff = np.diff(x,axis=1)/h**2
        lap[:,:-1] += diff
        lap[:,1:] -= diff
        lap[:,0] -= 2*x[:,0]/h**2
        lap[:,-1] -= 2*x[:,-1]/h**2
        return lap

    def gradient(self,x,y):
        # Forma bilineal independiente del operador por celdas.
        h = self.dx
        radial = 2*np.pi*(self.r[:-1]+h/2)*np.diff(x,axis=0)*np.diff(y,axis=0)
        axial = self.weight*np.diff(x,axis=1)*np.diff(y,axis=1)/h**2
        wall = 4*np.pi*(self.r[-1,0]+h/2)*np.sum(x[-1]*y[-1])
        ends = 2*np.sum(self.weight[:,0]*(x[:,0]*y[:,0]+x[:,-1]*y[:,-1]))/h**2
        return float(radial.sum()+axial.sum()+wall+ends)

    def solve(self,V,src):
        w = src/V
        norm = self.inner(src,src)**.5
        for _ in range(20):
            error = src-V*w+self.lap(w)
            relative = self.inner(error,error)**.5/max(norm,1e-300)
            if relative < 1e-12:
                return w,relative
            w += error/V
        raise ArithmeticError(relative)


def isolated(profile,r):
    a,v,da,z,p = profile.sample(r)
    support = r<profile.edge
    rz = np.minimum(r,profile.edge)
    lap_a = profile.field(r,2)+2*da/r
    lap_z = np.where(support,profile.neutral(rz,2)[0]+2*profile.neutral(rz,1)[0]/r,0.)
    density = abs(a)**2
    acc = lap_a-(m.mass2+2*m.quartic*density+m.trilinear*z+.5*m.mixed*z*z)*a
    az = lap_z-(m.mediator**2+m.mixed*density)*z-m.trilinear*density
    return (a,v,acc),(z,p,az)


def density_jet(a,v,acc):
    return abs(a)**2,2*(a.conj()*v).real,2*(abs(v)**2+(a.conj()*acc).real)


def product(a,b):
    return (a[0]*b[0],a[1]*b[0]+a[0]*b[1],a[2]*b[0]+2*a[1]*b[1]+a[0]*b[2])


def measure(grid,donor,receiver,d):
    D,Z = isolated(donor,np.hypot(grid.r,grid.z+d/2))
    R,Y = isolated(receiver,np.hypot(grid.r,grid.z-d/2))
    sd,sr = density_jet(*D),density_jet(*R)
    z,y = Z[0],Y[0]
    chi = tuple(a+b for a,b in zip(Z,Y))
    norm = lambda a: np.sqrt(grid.inner(a,a))
    rows=[]
    for phase,rot in ((0,1),(1,1j),(-1,-1j)):
        B = tuple(rot*a for a in R)
        A = tuple(a+b for a,b in zip(D,B))
        I = tuple(2*a.real for a in product(tuple(x.conj() for x in D),B))
        density = density_jet(*A)
        S = tuple(-m.trilinear*i-m.mixed*(j+k+l)
                  for i,j,k,l in zip(I,product(sd,Y),product(sr,Z),product(I,chi)))
        V = m.mediator**2+m.mixed*density[0]
        w,e0 = grid.solve(V,S[0])
        wt,e1 = grid.solve(V,S[1]-m.mixed*density[1]*w)
        wtt,e2 = grid.solve(V,S[2]-m.mixed*(density[2]*w+2*density[1]*wt))
        def cross(s,other,selfz):
            return 2*m.quartic*(s+I[0])+m.trilinear*other+m.mixed*other*(selfz+.5*other)
        raw = -cross(sr[0],y,z)*D[0]-cross(sd[0],z,y)*B[0]
        corrected = raw-(m.trilinear+m.mixed*chi[0]+.5*m.mixed*w)*w*A[0]
        pos = .5*(grid.gradient(w,w)+grid.inner(w,V*w))
        linear = grid.gradient(chi[0],w)+grid.inner(V*chi[0]+m.trilinear*density[0],w)
        kinetic = grid.inner(chi[1],wt)+.5*grid.inner(wt,wt)
        work = .5*grid.inner(w,S[0])
        if abs(pos-work)>1e-9*max(abs(pos),1e-30):
            raise ArithmeticError("Identidad de caras")
        rows.append(dict(fase=phase,norma_phi_original=norm(raw),norma_phi_corregida=norm(corrected),
            razon_phi=norm(corrected)/norm(raw),norma_S=norm(S[0]),norma_wtt=norm(wtt),
            razon_dinamica=norm(wtt)/norm(S[0]),max_w=float(np.max(abs(w))),
            max_rel_eliptico=max(e0,e1,e2),energia_cuadratica=pos,media_fuente_w=work,
            energia_lineal=linear,energia_estatica=linear+pos,energia_cinetica_seguimiento=kinetic,
            energia_montaje_incremental=linear+pos+kinetic,norma_w=norm(w),norma_wt=norm(wt),
            cota_norma_w=norm(S[0])/m.mediator**2))
    return rows


def run():
    prior = json.loads((RES/"contacto_interno_20261126/resultado.json").read_text())["insumos"]
    def state(key):
        return State(ROOT/key,prior[key])
    rec = state("checkpoints/Reserva/paso2_20261117/datos/preparacion.npz")
    rows=[]
    for dt in ("dt0005","dt001"):
        for case in ("gota_a010","gemelo"):
            donor=state(f"checkpoints/Reserva/paso3_20261118/datos/{dt}/{case}/tau300.npz")
            for d in (80,100,120):
                for name,R,L,h in (("gruesa",160,224,1.),("fina",160,224,.5),("amplia",192,256,.5)):
                    for row in measure(Cylinder(R,L,h),donor,rec,d):
                        rows.append(dict(dt=dt,donante=case,d=d,malla=name,**row))
    with (HERE/"medidas.csv").open("w",newline="") as out:
        writer=csv.DictWriter(out,fieldnames=rows[0],lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lookup={(r["dt"],r["donante"],r["d"],r["malla"],r["fase"]):r for r in rows}
    combinations=[]
    for dt in ("dt0005","dt001"):
        for d in (80,100,120):
            for grid in ("gruesa","fina","amplia"):
                def odd(case,k):
                    return (lookup[dt,case,d,grid,1][k]-lookup[dt,case,d,grid,-1][k])/2
                for k in ("energia_cuadratica","energia_estatica","energia_cinetica_seguimiento","energia_montaje_incremental"):
                    a,b=(odd(c,k) for c in ("gota_a010","gemelo"))
                    combinations.append(dict(dt=dt,d=d,malla=grid,magnitud=k,impar_cargada=a,impar_gemela=b,diferencia=a-b))
    prev=json.loads((RES/"tangente_contacto_20261126/resultado.json").read_text())
    checks=[]
    for p in prev["registros"]:
        r=lookup[p["dt"],p["donante"],p["d"],"fina",p["fase"]]
        force=np.hypot(r["norma_phi_original"],r["norma_S"]/np.sqrt(2))
        checks.append(abs(force/p["fina"]["norma_fuerza"]-1))
    result=dict(filas=len(rows),sha256_csv=digest(HERE/"medidas.csv"),contrastes_energia=combinations,
                diferencia_rel_max_fuerza_base=max(checks),theta_sha256=digest(ROOT/"datos/theta_comun.json"))
    (HERE/"resultado.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n")


if __name__=="__main__":
    run()
