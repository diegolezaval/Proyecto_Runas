"""Balance cinemático del contacto. Ejecutar desde cualquier directorio."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicHermiteSpline, CubicSpline
from scipy.special import roots_legendre

HERE = Path(__file__).resolve().parent
RES = HERE.parent
ROOT = RES.parents[1]
W = .9
A = 40.


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Profile:
    def __init__(self, path, w, manifest=None):
        self.w = w
        self.sha = digest(path)
        if manifest is None:
            r,f,df,_,_ = np.loadtxt(path, delimiter=",", skiprows=1).T
            self.f = CubicHermiteSpline(r,f,df)
            self.v = None
            self.edge = r[-1]
        else:
            if self.sha != manifest:
                raise ValueError(path)
            with np.load(path, allow_pickle=False) as data:
                dx = float(data["dx"])
                q,v = data["q"], data["v"]
            r = (np.arange(q.shape[1])+.5)*dx
            self.edge = r[-1]+dx/2
            axis = np.r_[-r[2::-1],r,self.edge]
            def spline(x):
                return CubicSpline(axis,np.r_[x[2::-1],x,0])
            self.f = spline(q[0]+1j*q[1])
            self.v = spline(v[0]+1j*v[1])
        self.rotation = np.exp(-1j*np.angle(self.f(0)))
        self.peak = np.max(abs(self.f(r)))

    def field(self,r,der=0):
        rr = np.minimum(r,self.edge)
        return np.where(r<=self.edge,self.rotation*self.f(rr,der),0.)

    def velocity(self,r):
        if self.v is None:
            return 1j*self.w*self.field(r)
        return np.where(r<=self.edge,self.rotation*self.v(np.minimum(r,self.edge)),0.)


def measure(donor, rec, sep, n):
    u,g = roots_legendre(n)
    # u se mide desde el centro receptor a lo largo del eje donante → receptor.
    distance = np.sqrt(sep**2+A**2+2*sep*A*u)
    D,R = donor.field(distance),rec.field(A)
    Dn = -donor.field(distance,1)*(A+sep*u)/distance
    Rn = -rec.field(A,1)
    Vd,Vr = donor.velocity(distance),rec.velocity(A)
    area = 2*np.pi*A**2*g
    # Coeficientes complejos para fase relativa multiplicativa exp(i theta).
    # jQ = -2 Im[Cq exp(i theta)], jE = -2 Re[Ce exp(i theta)].
    cq = area @ (D.conjugate()*Rn-R*Dn.conjugate())
    ce0 = area @ (Vd.conjugate()*Rn+Vr*Dn.conjugate())
    ce = area @ (-1j*W*D.conjugate()*Rn+1j*rec.w*R*Dn.conjugate())
    r = (.5*A*(1+u))[:,None]
    rd = np.sqrt(sep**2+r*r+2*sep*r*u)
    vol = np.pi*A*r*r*g[:,None]*g
    # rhoQ cruzada de la rotación rígida = 2(wD+wR) Re[e^{i theta} D*R].
    iq = 2*(W+rec.w)*np.sum(vol*donor.field(rd).conjugate()*rec.field(r))
    # Interpolación de las colas muestreada sobre todo el intervalo radial relevante.
    radius = np.linspace(sep-A,sep+A,8001)
    weak = max(max(abs(donor.field(radius)))/donor.peak,max(abs(rec.field(radius)))/rec.peak)
    rows = []
    for t in (40,80,240):
        angle = (rec.w-W)*t
        kernel = t*np.exp(.5j*angle)*np.sinc(angle/(2*np.pi))
        # Media diferencia entre +pi/2 y -pi/2. Sin contacto desaparece el cruzado.
        flow_q = -2*(1j*cq*kernel).imag
        gain_q = (1j*iq*np.expm1(1j*angle)).real
        rows.append(dict(T=t,cola_rel=weak,flujo_Q=flow_q,delta_inventario_Q=gain_q,
                         defecto_Q=flow_q-gain_q,flujo_E=-2*(1j*ce*kernel).real,
                         inicial_Q_impar=-2*cq.real,inicial_E_impar=2*ce0.imag,
                         inicial_E_rigida=2*ce.imag,inicial_Q_fase0=-2*cq.imag,
                         inicial_E_fase0=-2*ce0.real,inventario_Q_inicial_impar=-iq.imag))
    return rows


def run():
    p2,p3 = RES/"paso2_20261117", RES/"paso3_20261118"
    def read(path):
        return json.loads(path.read_text())
    m2 = read(p2/"MANIFIESTO.json")["archivos"]
    m3 = read(p3/"MANIFIESTO_RETENCION.json")
    h = {}
    def prepared(base,key,manifest):
        obj = Profile(base/key,W,manifest[key]["sha256"])
        h[str((base/key).relative_to(ROOT))] = obj.sha
        return obj
    recs = {"preparada":prepared(p2,"datos/preparacion.npz",m2)}
    branch = ROOT/"validacion/P06/rama"
    frequencies = {x["omega"] for x in read(branch/"resultados.json")["rows"]}
    for w in (.895,.900,.905):
        if w not in frequencies:
            raise ValueError(w)
        path = branch/f"perfil_w{w:.5f}.csv"
        obj = Profile(path,w)
        recs[f"rama_{w:.3f}"] = obj
        h[str(path.relative_to(ROOT))] = obj.sha
    rows = []
    for step in ("dt0005","dt001"):
        for case in ("gota_a010","gemelo"):
            donor = prepared(p3,f"datos/{step}/{case}/tau300.npz",m3)
            for recname,rec in recs.items():
                for d in (80,100,120):
                    for n in (96,192):
                        for row in measure(donor,rec,d,n):
                            rows.append(dict(dt=step,donante=case,receptora=recname,d=d,n=n,**row))
    with (HERE/"medidas.csv").open("w",newline="") as f:
        writer = csv.DictWriter(f,fieldnames=rows[0],lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    idx = {(r["dt"],r["donante"],r["receptora"],r["d"],r["n"],r["T"]):r for r in rows}
    summaries = []
    for rec in recs:
        for d in (80,100,120):
            for t in (40,80,240):
                def pair(step,n,col):
                    return [idx[step,c,rec,d,n,t][col] for c in ("gota_a010","gemelo")]
                def contrast(step,n,col):
                    a,b = pair(step,n,col)
                    return a-b
                s = dict(receptora=rec,d=d,T=t,cola=max(pair("dt0005",192,"cola_rel")))
                for col in ("flujo_Q","flujo_E","delta_inventario_Q","defecto_Q"):
                    v = contrast("dt0005",192,col)
                    s[col] = v
                    s["error_cuadratura_"+col] = abs(v-contrast("dt0005",96,col))
                    s["error_dt_"+col] = abs(v-contrast("dt001",192,col))
                s["diferencia_velocidad_inicial_E_por_tiempo"] = t*abs(
                    contrast("dt0005",192,"inicial_E_impar")-contrast("dt0005",192,"inicial_E_rigida"))
                summaries.append(s)
    result = dict(insumos=h,contrastes=summaries,filas=len(rows),
                  sha256_csv=digest(HERE/"medidas.csv"),decision="Indeterminado en M2. Piloto sin habilitar.")
    (HERE/"resultado.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n")


if __name__ == "__main__":
    run()
