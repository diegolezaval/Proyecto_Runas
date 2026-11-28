"""Contabilidad de las normas positivas que entran en la banda 10–40."""
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"proyeccion_qdot_20261127"))
import medir_qdot as q
base,d=q.base,q.d
archive=q.archive[:108]+json.loads((q.HERE/"resultado.json").read_text())["doce"]["filas"]
labels=["prescrita","desplazamiento_S","realimentacion","defecto_pos","defecto_vel"]


def matches(actual,reference):
    assert np.allclose(actual,reference,rtol=2e-12,atol=1e-25)


class History:
    def __init__(self,model):
        self.model=model
        self.raw=[]
        self.jumps=[]
        self.rows=[]
        self.details=[]

    def capture(self,state,best,remainder,jump,op,row,cr,accepted):
        j=len(self.raw)
        current=state.rows[-1]
        x=np.array(current["volumen"])
        band=1
        prescribed=np.linalg.norm(state.shapes[band]*best)
        shifted=state.shift[band]*x
        local=state.mask[band]*remainder*x
        global_cap=max(remainder)*x[band]
        feedback=min(np.linalg.norm(local),global_cap)
        source=[prescribed,np.linalg.norm(shifted),feedback,
                np.sqrt(state.op**2+op)*row["pos"],row["vel"]]
        matches(source[1],current["cota_Sx"][band])
        matches(source[2],current["fuerza_resto"][band])
        self.raw.append(source)
        self.jumps.append(jump)
        # Sources born in interval i receive jumps i+1,...,j only.
        jumps=np.r_[np.cumprod(np.array(self.jumps[:0:-1]))[::-1],1.]
        weights=state.E[:j+1,band][::-1]*jumps
        by_time=weights[:,None]*np.array(self.raw)
        lags=j-np.arange(j+1)
        grouped=np.array([by_time[mask].sum(axis=0) for mask in
                         (lags==0,(lags>=1)&(lags<8),(lags>=8)&(lags<32),lags>=32)])
        energy=by_time.sum()
        matches(energy,current["energia"][band])
        matches(grouped.sum(axis=0),by_time.sum(axis=0))
        old=self.model.s*energy+self.model.c*x[band]
        spectral=self.model.gamma*energy
        use_spectral=self.model.active_face and spectral<=old
        face=spectral if use_spectral else old
        matches(face,cr["cara"])
        self.rows.append(dict(t=row["t"],aceptada=bool(accepted),energia=energy,
            coste_caras=face,coste_previo=old,coste_espectral=spectral,
            usa_espectral=bool(use_spectral),por_fuente=by_time.sum(axis=0).tolist(),
            por_retardo_y_fuente=grouped.tolist(),error_energia=abs(energy-current["energia"][band]),
            error_caras=abs(face-cr["cara"]),S_por_banda_cuadrado=(shifted**2).tolist(),
            realim_local_por_banda_cuadrado=(local**2).tolist(),usa_realim_local=bool(np.linalg.norm(local)<=global_cap),
            realim_global=global_cap))
        if j>=len(archive)-2:
            self.details.append(dict(t=row["t"],emisiones=np.column_stack([
                [z["t"] for z in self.rows],lags,jumps,weights,by_time]).tolist()))


def study(step,march,table):
    model=q.Project(q.wj.prior["metrica"]["gamma"])
    hist=History(model)
    out=base.cont.solve(step,march,table,adj=base.prev.kernels(),core_model=model,
        box_observer=model.reference,radii_policy=q.Policy(model,"doce",108),budget_observer=hist.capture)
    assert out["filas"]==archive
    return dict(prefijo=out["prefijo"],fuentes=labels,retardos=["0","1–7","8–31","32+"],
        columnas_emision=["extremo_fuente","retardo_pasos","producto_saltos","E_por_saltos"]+labels,
        filas=hist.rows,extremos=hist.details)


if __name__=="__main__":
    base.cont.main(study,HERE/"resultado.json")
