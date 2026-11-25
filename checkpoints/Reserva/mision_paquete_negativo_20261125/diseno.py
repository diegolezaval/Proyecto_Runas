"""Diseño previo desde el espectro de la pareja (rΦ, rΦ̇) y la dispersión de M2."""
import json
from pathlib import Path
import sys

import numpy as np

AQUI=Path(__file__).resolve().parent
PASO2=AQUI.parent/"paso2_20261117"
PASO3=AQUI.parent/"paso3_20261118"
ANTERIOR=AQUI.parent/"mision_extraccion_radial_20261124"
sys.path.insert(0,str(PASO2))
import ensayo
from ensayo import OMEGA, dump, envelope, model, sha

OMEGA_P=2.3
NU=OMEGA-OMEGA_P
K0=np.sqrt(NU**2-model.mass2)
VG=K0/abs(NU)
CENTRO=120.
BNEG=(1.02,1.85)
BPOS=(BNEG[0]+2*OMEGA,BNEG[1]+2*OMEGA)


def forma(x):
    b,bp=envelope(x)
    f=np.exp(-1j*K0*x)
    return f*b, f*(1j*NU*b+VG*bp)


def paquete(r,a):
    f,v=forma(r-CENTRO)
    f=f*a/r
    v=v*a/r
    return (np.array([f.real,f.imag,np.zeros_like(r)]),
            np.array([v.real,v.imag,np.zeros_like(r)]))


def espectro(L=4096.,h=.025):
    # FFT de la onda radial reducida en la recta, rellenada con ceros fuera del soporte.
    x=(np.arange(round(L/h))+.5)*h-L/2
    k=2*np.pi*np.fft.fftfreq(len(x),h)
    q,v=map(np.fft.fft,forma(x))
    nu=np.sqrt(model.mass2+k*k)
    ep=nu**2*abs((q+v/(1j*nu))/2)**2
    em=nu**2*abs((q-v/(1j*nu))/2)**2
    et=ep.sum()+em.sum()
    sel=k<0
    orden=np.argsort(nu[sel])
    f=nu[sel][orden]; w=em[sel][orden]/et
    return f,w,dict(negativa_entrante=float(w.sum()),negativa_saliente=float(em[k>0].sum()/et),
        positiva_entrante=float(ep[k>0].sum()/et),positiva_saliente=float(ep[k<0].sum()/et))


def predecir():
    nodos=json.loads((PASO2/"BANDA.json").read_text())
    disp=np.array(nodos["dispersion"])
    g=ensayo.Grid(.025)
    seed=.001
    def recursos(a):
        q,v=paquete(g.r,a)
        q,v=(np.pad(x,((0,0),(1,1))) for x in (q,v))
        # La referencia sólo afecta al indicador opcional de perfil; usar 1 evita dividir por cero en vacío.
        return list(map(float,g.measure(q,v,np.ones(g.n))[:2]))
    e0,_=recursos(seed)
    ret=json.loads((PASO3/"RETENCION.json").read_text())["paso_temporal"]["dt0005"]
    st={k:ret[k]["por_radio"]["40"]["inventario_300"] for k in ("E","Q")}
    est={}
    for L in (2048.,4096.):
        f,w,ramas=espectro(L)
        om=f+OMEGA
        for hr in (.0125,.00625):
            a=disp[disp[:,0]==hr]
            nodes=np.r_[1.9,a[:,1]]
            pr=np.r_[0.,a[:,2]]
            for paso in (1,2):
                prob=np.interp(om,nodes[::paso],pr[::paso],left=0.,right=0.)
                K=float(np.sum(w*prob/f))
                est[f"L{L:g}_h{hr}_paso{paso}"]=dict(ganancia_energetica=2*OMEGA*K,
                    carga_neta_por_E=2*K,Q_positiva_por_E=K,
                    E_positiva_por_E=float(np.sum(w*prob*(f+2*OMEGA)/f)))
    principal=est["L4096_h0.00625_paso1"]
    alpha=round(seed*np.sqrt(.10*max(st["E"],OMEGA*st["Q"])/(e0*principal["ganancia_energetica"])),5)
    e,q=recursos(alpha)
    bandas={}
    wp=w/w.sum()
    for nombre,a in (("nu_neg_abs",f),("Omega",om),("modulo_v_grupo",np.sqrt(1-1/f**2))):
        bandas[nombre]=[float(a[np.searchsorted(np.cumsum(wp),u)]) for u in (.0005,.025,.5,.975,.9995)]
    frac_omitida=float(w[om>2.8].sum())
    return dict(A=alpha,Omega=OMEGA_P,nu_incidente=NU,k_portadora=-K0,rapidez_grupo=VG,
        stock=st,umbral={k:.01*v for k,v in st.items()},E_paquete_vacio=e,Q_paquete_vacio=q,
        objetivo_diseno="Saldo lineal de fondo cercano a 10 veces el umbral del 1 % en ambos canales.",
        recurso_referencia=dict(a=seed,E=e0),prediccion=dict(delta_E=e*principal["ganancia_energetica"],
        delta_Q=e*principal["carga_neta_por_E"],Q_positiva=e*principal["Q_positiva_por_E"],
        E_positiva=e*principal["E_positiva_por_E"]),fracciones_E_inicial=ramas,
        cuantiles_acumulados_E=[.0005,.025,.5,.975,.9995],bandas=bandas,
        fraccion_E_incidente_en_banda_fijada=float(wp[(f>=BNEG[0])&(f<=BNEG[1])].sum()),
        fraccion_E_negativa_mas_alla_tabla=frac_omitida,
        max_ganancia_no_contada_por_unidad_E=2*OMEGA*frac_omitida/(2.8-OMEGA),
        ponderaciones=est,sha256_dispersion=sha(PASO2/"BANDA.json"))


if __name__=="__main__":
    dump(AQUI/"DISENO_ESPECTRAL.json",predecir())
