"""Referencia radial tangente; el operador evolutivo nunca evalúa fuerzas no lineales."""
import csv
import ctypes
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from scipy.interpolate import CubicHermiteSpline

HERE=Path(__file__).resolve().parent
RES=HERE.parent
sys.path.insert(0,str(RES/"paso2_20261117"))
from ensayo import Grid, OMEGA as om, PROFILE, model as m, sha

P3=RES/"paso3_20261118"
PK=RES/"mision_paquete_negativo_20261125"
NAMES=("E40","Q40","E60","Q60")
PROBES=("40i","40e","60i","60e")
THRESHOLDS={"E":1.66414371e-6,"Q":1.84762579e-6}


def read(p):
    return json.loads(p.read_text())


def operator(g):
    raw=np.loadtxt(PROFILE,delimiter=",",skiprows=1)
    f,z=[np.where(g.r<raw[-1,0],CubicHermiteSpline(raw[:,0],raw[:,j],raw[:,j+1])(
        np.minimum(g.r,raw[-1,0])),0.) for j in (1,3)]
    K=m.mass2+2*m.quartic*f*f+m.trilinear*z+.5*m.mixed*z*z
    B=(m.trilinear+m.mixed*z)*f
    V=m.mediator**2+m.mixed*f*f
    offset_f=-g.A@f+(om**2-K)*f
    offset_z=-g.A@z-V*z-m.trilinear*f*f
    c=np.column_stack((g.lo,g.hi,om**2-K-4*m.quartic*f*f,om**2-K,-V,-B,-2*B,offset_f,offset_z))
    # Hessiano canónico de la interacción respecto de las masas de vacío.
    hess=np.zeros((len(f),3,3))
    hess[:,0,0]=K-m.mass2+4*m.quartic*f*f
    hess[:,1,1]=K-m.mass2
    hess[:,2,2]=V-m.mediator**2
    hess[:,0,2]=hess[:,2,0]=np.sqrt(2)*B
    L=np.max(np.linalg.svd(hess/[np.sqrt(m.mass2),np.sqrt(m.mass2),m.mediator],compute_uv=False))
    return f,z,c,float(L)


def load_reference(case):
    label="cargada_sin" if case=="gota_a010" else "gemela_sin"
    table=read(PK/"datos/EJECUCION.json")["series"]
    entry=next(t for t in table if t["caso"]==label and t["replica"]=="principal")
    def load(kind):
        p=PK/"datos/principal"/label/(kind+".csv")
        assert sha(p)==entry["sha256_"+kind]
        return np.genfromtxt(p,delimiter=",",names=True)
    return load("serie"),load("sondas")


def trajectory(advance,g,f,z,c,prep,case,dt):
    p=P3/"datos"/prep/case/"tau300.npz"
    assert sha(p)==read(P3/"MANIFIESTO_RETENCION.json")[str(p.relative_to(P3))]["sha256"]
    with np.load(p) as s:
        assert s["dx"]==g.dx and s["tau"]==300
        q0,v0=s["q"],s["v"]
    phase=np.exp(1j*np.angle(q0[0,0]+1j*q0[1,0]))
    F=(q0[0]+1j*q0[1])/phase
    P=(v0[0]+1j*v0[1])/phase-1j*om*F
    x=np.column_stack((F.real-f,F.imag,q0[2]-z))
    v=np.column_stack((P.real,P.imag,v0[2]))
    series,probes=load_reference(case)
    idx=[g.core-1,g.core,g.port-1,g.port]
    rows=[]
    weight=4*np.pi*g.w
    initial={}
    for i in range(161):
        if i:
            advance(g.n,round(.25/dt),dt,om,c,x,v)
        s=i*.25
        a,b,y=x.T
        F=f+a+1j*b
        rot=phase*np.exp(1j*om*s)
        field=rot*F
        vel=rot*(v[:,0]+1j*v[:,1]+1j*om*F)
        q=np.array([field.real,field.imag,z+y])
        vv=np.array([vel.real,vel.imag,v[:,2]])
        u=a*a+b*b
        deltaK=2*m.quartic*(2*f*a+u)+(m.trilinear+m.mixed*z)*y+.5*m.mixed*y*y
        rem_phi=f*(2*m.quartic*u+.5*m.mixed*y*y)+deltaK*(a+1j*b)
        rem_chi=(m.trilinear+m.mixed*z)*u+m.mixed*(2*f*a+u)*y
        squared=2*abs(rem_phi)**2+rem_chi**2
        row=dict(preparacion=prep,caso=case,dt=dt,s=s,
            residuo_L2=np.sqrt(weight@squared),residuo_r160=np.sqrt(weight[g.r<160]@squared[g.r<160]),
            max_delta_phi=max(abs(a+1j*b)),max_delta_chi=max(abs(y)),
            max_delta_vel_phi=max(abs(v[:,0]+1j*v[:,1]+1j*om*(a+1j*b))),
            max_delta_vel_chi=max(abs(v[:,2])))
        # Fuentes espurias de los balances de la referencia semidiscreta;
        # corresponden solo a la fuerza omitida, antes del error de paso temporal.
        for radius in (40,60):
            cut=round(radius/g.dx)
            rhoQ=2*(F.conj()*rem_phi).imag
            rhoE=2*((v[:,0]+1j*v[:,1]+1j*om*F).conj()*rem_phi).real+v[:,2]*rem_chi
            row["fuente_Q"+str(radius)] = weight[:cut]@rhoQ[:cut]
            row["fuente_E"+str(radius)] = weight[:cut]@rhoE[:cut]
        if i in (0,80,160):
            qrot=np.array([F.real,F.imag,z+y])
            actual=g.acceleration(qrot)
            linear=np.array([-g.A@a+(c[:,2]-om**2)*a+c[:,5]*y+c[:,7]-om**2*f,
                             -g.A@b+(c[:,3]-om**2)*b,
                             -g.A@y+c[:,4]*y+c[:,6]*a+c[:,8]])
            err=max(np.max(abs((linear-actual)[0]+1j*(linear-actual)[1]-rem_phi)),
                    np.max(abs((linear-actual)[2]-rem_chi)))
            if err>2e-9: raise ArithmeticError(("Taylor",err))
            row["control_taylor"]=err
        if prep=="dt0005":
            assert probes["s"][i]==s
            obs=np.array([probes["Re"+n][i]+1j*probes["Im"+n][i] for n in PROBES])
            row["error_sondas"]=max(abs(field[idx]-obs))
        if i%4==0:
            inv=g.measure(np.pad(q,((0,0),(1,1))),np.pad(vv,((0,0),(1,1))),f)[2:6]
            if not i:
                initial=dict(zip(NAMES,inv))
                assert max(np.max(abs(q-q0)),np.max(abs(vv-v0)))<1e-13
                if prep=="dt0005":
                    assert row["error_sondas"]<1e-12
                    assert max(abs(initial[k]-series[k][0]) for k in NAMES)<1e-8
            for k,val in zip(NAMES,inv):
                row["perdida_"+k]=initial[k]-val
                if prep=="dt0005":
                    row["archivo_"+k]=series[k][0]-series[k][int(s)]
        rows.append(row)
    return rows


def run():
    g=Grid(.025)
    f,z,c,L=operator(g)
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        lib=Path(tmp)/"tangente.so"
        subprocess.run(["cc","-std=c11","-O3","-ffp-contract=off","-shared","-fPIC",str(HERE/"tangente.c"),"-lm","-o",str(lib)],check=True)
        fn=ctypes.CDLL(str(lib)).advance
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
        fn.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_double,ptr,ptr,ptr]
        fn.restype=None
        for prep in ("dt0005","dt001"):
            for case in ("gota_a010","gemelo"):
                for dt in (.005,.0025):
                    rows.extend(trajectory(fn,g,f,z,c,prep,case,dt))
    columns=list(dict.fromkeys(k for r in rows for k in r))
    with (HERE/"series.csv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=columns,lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (HERE/"series.csv.gz").write_bytes(gzip.compress((HERE/"series.csv").read_bytes(), compresslevel=9, mtime=0))
    lookup={(r["preparacion"],r["caso"],r["dt"],r["s"]):r for r in rows}
    controls={}
    for k in NAMES:
        def delta(prep,dt,t,field):
            return lookup[prep,"gota_a010",dt,t][field+k]-lookup[prep,"gemelo",dt,t][field+k]
        ref=np.array([delta("dt0005",.0025,t,"perdida_") for t in range(41)])
        physical=np.array([delta("dt0005",.0025,t,"archivo_") for t in range(41)])
        coarse=np.array([delta("dt0005",.005,t,"perdida_") for t in range(41)])
        prep=np.array([delta("dt001",.0025,t,"perdida_") for t in range(41)])
        i=int(np.argmax(abs(ref-physical)))
        controls[k]=dict(max_error=abs(ref[i]-physical[i]),s_max=i,
            error_en_umbrales=abs(ref[i]-physical[i])/THRESHOLDS[k[0]],
            cambio_dt_ref=max(abs(ref-coarse)),cambio_dt_preparacion=max(abs(ref-prep)),
            ref_s40=ref[-1],archivo_s40=physical[-1])
    for k in NAMES:
        times=np.arange(161)*.25
        rates=[delta("dt0005",.0025,t,"fuente_") for t in times]
        controls[k]["integral_firma_residuo_T40"]=np.trapezoid(rates,times)
    stats=dict(controles=controls,coeficiente_norma_vacio=L,
        log10_factor_energia_s40=20*L/np.log(10),max_defecto_estacionario=list(np.max(abs(c[:,7:9]),axis=0)),
        sha256_perfil=sha(PROFILE),sha256_series=sha(HERE/"series.csv"))
    (HERE/"resultado.json").write_text(json.dumps(stats,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    run()
