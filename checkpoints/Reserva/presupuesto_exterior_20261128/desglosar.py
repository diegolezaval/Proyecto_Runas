"""Contabilidad exacta de los mayorantes, sin alterar el comparador ni su marcha."""
from pathlib import Path
import json,sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cota_exterior_20261128"))
import reproducir as rep
from formas import coefficient
d,cont=rep.d,rep.cont
base=json.loads((rep.HERE/"marcha.json").read_text())
tfinal=base["filas"][-1]["t"]
keys=["prescrita","realimentacion","desplazamiento_positivo","defecto_posicion","defecto_velocidad"]

def close(a,b):
    np.testing.assert_allclose(a,b,rtol=4e-12,atol=1e-29)

def rowsums(arr):
    total=arr.sum(axis=0)
    windows=[arr[-8:].sum(axis=0),arr[-32:-8].sum(axis=0),arr[:-32].sum(axis=0)]
    close(np.asarray(windows).sum(axis=0),total)
    return dict(total=total.tolist(),retardos=[[0,.875],[1.,3.875],[4.,tfinal-d.h]],
                por_retardo=np.stack(windows).tolist())

def ledger(raw,state,pres,shx,fbx):
    hist=np.stack([r[0] for r in raw])
    pos,vel=np.stack([r[1] for r in raw]),np.stack([r[2] for r in raw])
    jumps=np.array([r[3] for r in raw])
    n=len(jumps)
    multipliers=np.r_[np.cumprod(jumps[:0:-1])[::-1],1.]
    weighted=hist*multipliers[:,None,None]
    eK=state.E[:n][::-1]
    xK=state.K[:n][::-1]
    E=np.empty((n,5,5));X=np.empty_like(E)
    E[:,:,:3]=weighted*eK[:,:,None]
    X[:,:,:3]=weighted*xK[:,:,None]
    X[-1,:,1]=fbx*state.K[0]
    X[-1,:,2]=shx*state.K[0]
    for i,v in enumerate([pos,vel],3):
        E[:,:,i]=(multipliers*v)[:,None]*eK
        X[:,:,i]=E[:,:,i]/np.sqrt(state.floor)
    row=state.rows[-1]
    close(E.sum(axis=(0,2)),row["energia"])
    close(X.sum(axis=(0,2)),row["volumen"])
    plain=E/multipliers[:,None,None]
    close(plain[-1],E[-1])
    radial=np.stack([r[4] for r in raw])*multipliers[:,None,None]
    radialE=(radial*eK[:,:,None]).sum(axis=0)
    radialX=(radial*xK[:,:,None]).sum(axis=0)
    close(radialE.sum(axis=1),E[:,:,0].sum(axis=0))
    close(radialX.sum(axis=1),X[:,:,0].sum(axis=0))
    return dict(X=rowsums(X),E=rowsums(E),grupos=keys,
        asignacion_cuadratica_prescrita_E=radialE.tolist(),asignacion_cuadratica_prescrita_X=radialX.tolist(),
        E_sin_multiplicadores_de_salto=plain.sum(axis=0).tolist(),
        salto_acumulado_max=float(multipliers.max()),salto_final=float(jumps[-1]),
        saltos=jumps.tolist(),X_fila=row["volumen"],E_fila=row["energia"])

def estimate(result):
    X=np.array(result["X"]["total"])
    E=np.array(result["E"]["total"])
    profiles={b:[(p,coefficient(b,*p)[0]) for p in rep.params[b]] for b in (3,4)}
    def values(cut,group):
        e=E.sum(axis=1)-cut*E[:,group]
        x=X.sum(axis=1)-cut*X[:,group]
        return [float(np.min([coeff*np.sqrt(e[b]**2+p[1]*x[b]**2+p[2]*e[7-b]**2)*(1+2e-12)
                             for p,coeff in profiles[b]],axis=0).max()) for b in (3,4)]
    close(values(0,0),base["filas"][-1]["punto"][3:])
    out={}
    for i,key in enumerate(keys):
        end=values(1,i)
        needed=[]
        for b in range(2):
            left,right=0.,1.
            if end[b]>d.tube:
                needed.append(None)
                continue
            for _ in range(45):
                mid=(left+right)/2
                if values(mid,i)[b]>d.tube:left=mid
                else:right=mid
            needed.append(right)
        out[key]=dict(cota_sin_este_aporte=end,fraccion_necesaria=needed)
    return out

def study(step,march,table):
    C=d.Comparison
    initial=cont.solve
    advance=C.advance
    final={}
    def solve(*args,**kw):
        raw=[]
        def instrument(self,best,J,row,adj,linear,remainder,jump,op_extra,shift_cap=None,feedback_cap=None):
            k=len(self.rows)
            F=np.linalg.norm(self.shapes*best,axis=1)
            advance(self,best,J,row,adj,linear,remainder,jump,op_extra,shift_cap,feedback_cap)
            r=self.rows[-1]
            shp=np.asarray(r["cota_Sx"])
            fb=np.asarray(r["fuerza_resto"])
            radial=np.stack([np.sum((self.shapes[:,s]*best[s])**2,axis=1) for s in d.bands],axis=1)
            # This is a positive allocation of the weighted norm, not independent force norms.
            radial/=np.maximum(F[:,None],np.finfo(float).tiny)
            op=np.sqrt(self.op**2+op_extra)
            record=(np.stack([F,fb,shp],axis=1),op*row["pos"],row["vel"],jump,radial)
            if k==len(raw):
                raw.append(record)
            else:
                assert k==len(raw)-1
                raw[k]=record
            if row["t"]==tfinal:
                ne=np.sum(self.E[:k+1]*np.array(self.numeric[::-1])[:,None],axis=0)
                rhs=ne/np.sqrt(self.floor)+self.K[0]*F
                if k: rhs+=np.sum(self.K[1:k+1]*self.history[-2::-1],axis=0)
                M=self.K[0,:,None]*(self.shift+np.eye(5)*max(remainder))
                inverse=np.linalg.solve(np.eye(5)-M,np.eye(5))
                x=np.maximum(inverse,0)@rhs
                for _ in range(3):
                    shifted=np.linalg.norm(self.shift*x,axis=1)
                    if shift_cap is not None:shifted=np.minimum(shifted,shift_cap)
                    f=np.minimum(max(remainder)*x,np.linalg.norm(self.mask*(remainder*x),axis=1))
                    if feedback_cap is not None:f=np.minimum(f,feedback_cap)
                    x=rhs+self.K[0]*(shifted+f)
                close(x,r["volumen"])
                self.final_x_groups=shifted,f
        def observer(state,best,rem,jump,op,row,cr,ok):
            if row["t"]==tfinal:
                assert not ok and len(raw)==len(state.rows)
                final.update(ledger(raw,state,best,*state.final_x_groups))
        kw["budget_observer"]=observer
        C.advance=instrument
        try:return initial(*args,**kw)
        finally:C.advance=advance
    cont.solve=solve
    try:
        run=rep.study(step,march,table)
    finally:cont.solve=initial
    assert run==base and final
    return dict(t=tfinal,radios=base["filas"][-1]["radios"],
        entrada=base["evaluacion"]["184"]["entrada"],cotas=base["filas"][-1]["punto"],
        desglose=final,sensibilidad_solo_diagnostica=estimate(final))

if __name__=="__main__":
    cont.main(study,HERE/"resultado.json")
