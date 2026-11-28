"""Comparación conjunta con un único estado entrante por candidato."""
import json
import sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"caja_componentes_20261127"))
import evaluar as prev
d,core,o,cont=prev.d,prev.core,prev.o,prev.cont
ARCH=json.loads((prev.HERE/"resultado.json").read_text())["continuacion"]["filas"]
FIRST=len(ARCH)-1


class Transition(prev.Components):
    def __init__(self):
        super().__init__(False)
        sl=d.bands[1]
        self.local,self.res_transition=core.evaluation(True,(sl.start,sl.stop))
        ka,kz=np.split(o.kap,2)
        self.k1=np.column_stack([abs(ka[sl]),0*ka[sl],abs(kz[sl])])/o.sw[sl,None]
        self.u1=np.column_stack([0*ka[sl],abs(o.u[sl]),0*ka[sl]])/o.sw[sl,None]
        self.enable=False

    def transition_box(self,cell,D,Q,b):
        if self.enable:
            sl=d.bands[1]
            w=core.w[sl,None]
            old=cell[sl].copy()
            cut=(self.local*D+self.k1*Q+self.u1*b)/np.array([np.sqrt(2),np.sqrt(2),1.])
            cell[sl]=np.minimum(old,np.divide(cut,w,out=old.copy(),where=w>0))
            assert np.all(cell[sl]<=old) and np.array_equal(cell[sl][w[:,0]==0],old[w[:,0]==0])
        return cell


class Policy:
    def __init__(self,model,mode):
        self.model=model
        self.mode=mode
        self.tests=[]

    def start(self,j,ladder,idx,log):
        self.model.enable=self.mode=="desde_cero" or (j==FIRST and self.mode=="traslado")
        if j<FIRST and self.mode!="desde_cero":
            return np.searchsorted(ladder,ARCH[j]["radios"])
        if j==FIRST and self.mode!="desde_cero":
            start=np.searchsorted(ladder,ARCH[j-1]["radios"])
            start[0]=len(ladder)-1
            if self.mode=="techos": start[:]=len(ladder)-1
            return start
        return idx

    def test(self,j,ladder,idx,entry,pt,cr,e,x):
        radius=ladder[idx]
        need=np.maximum(entry,pt)
        higher=np.maximum(idx,np.minimum(len(ladder)-1,np.searchsorted(ladder,need)))
        done=np.array_equal(idx,higher)
        if self.mode!="desde_cero" and j<FIRST:
            assert done and np.all(need<=radius)
        if j==FIRST or (self.mode=="desde_cero" and max(pt)>o.tube and done):
            self.tests.append(dict(t=(j+1)*d.h,entrada=entry.tolist(),radios=radius.tolist(),
                envolventes=pt.tolist(),gradiente=self.model.s*e[1],curvatura=self.model.c*x[1],
                fase_restaurada=max(self.model.phase)*cr["beta"],carga_restaurada=max(self.model.kap)*cr["Q"],
                defecto_fase=o.eps*(self.model.uw@x),nucleo=cr))
        return done,higher


def study(step,march,table):
    adj=prev.kernels()
    model=Transition()
    result=dict(residuo_transicion=model.res_transition)
    for mode in ("techos","bandas","traslado","desde_cero"):
        if mode=="desde_cero" and min(result[k]["pruebas"][-1]["envolventes"][0] for k in ("bandas","traslado"))>=ARCH[-1]["punto"][0]:
            break
        model.D=model.Q=model.beta=0.
        policy=Policy(model,mode)
        out=cont.solve(step,march,table,adj=adj,
            core_model=model,box_observer=model.reference,radii_policy=policy,limit=None if mode=="desde_cero" else FIRST+1)
        rows=out["filas"]
        if mode!="desde_cero":
            assert rows[:FIRST]==ARCH[:FIRST]
        if mode=="techos": assert rows[-1]==ARCH[-1]
        result[mode]=dict(prefijo=out["prefijo"],ultima=rows[-1],pruebas=policy.tests)
        if mode=="desde_cero": result[mode]["filas"]=rows
    return result

if __name__=="__main__":
    cont.main(study,HERE/"resultado.json")
