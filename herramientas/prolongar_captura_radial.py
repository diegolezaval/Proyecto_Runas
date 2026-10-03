"""Prolonga un estado radial válido en una caja mayor, sin repetir su evolución.

Sólo conserva dx, dt y el dato inicial. Rechaza la transferencia si la energía
del anillo exterior no es despreciable. No permite reemplazar un destino.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from modelo_m2 import BENCHMARK as model

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--radius',type=float,required=True);p.add_argument('--tmax',type=float,required=True)
    args=p.parse_args();source=args.source
    with np.load(source,allow_pickle=False) as z:state={k:z[k] for k in z.files}
    old=json.loads(str(state['config']));new=dict(old,radius=args.radius,tmax=args.tmax,n=int(round(args.radius/old['dx'])))
    assert args.radius>old['radius'] and args.tmax>old['tmax']
    assert abs(new['n']*old['dx']-args.radius)<1e-10
    dx=old['dx'];n=old['n'];edges=np.linspace(0,old['radius'],n+1);weight=np.diff(edges**3)/3
    phi,vel,chi,vchi=(state[k] for k in ['phi','vel','chi','vchi'])
    density=weight*(abs(vel)**2+.5*vchi*vchi+model.potential(abs(phi),chi))
    faces=edges[1:-1]**2/dx*(abs(np.diff(phi))**2+.5*np.diff(chi)**2)
    boundary=2*old['radius']**2/dx*(abs(phi[-1])**2+.5*chi[-1]**2)
    total=4*np.pi*(density.sum()+faces.sum()+boundary)
    start=int(round((old['radius']-20)/dx))
    outer=4*np.pi*(density[start:].sum()+faces[start-1:].sum()+boundary)
    bound=float(outer/total)
    assert bound<1e-12,('El borde antiguo no es despreciable',bound)
    extra=new['n']-n
    for k in ['phi','vel','chi','vchi']:state[k]=np.pad(state[k],(0,extra))
    r=(np.arange(new['n'])+.5)*dx
    initial=np.zeros((new['n'],7));initial[:,0]=r;initial[:n,1:]=state['initial'][:,1:];state['initial']=initial
    state['late']=np.empty((0,int(round(30/dx))))
    state['config']=json.dumps(new)
    tag=f"w{new['width']:.2f}_h{dx:.3f}_dt{new['dt']:.4f}_R{new['radius']:.0f}_T{new['tmax']:.0f}"
    target=source.parent/f'{tag}_estado.npz'
    assert not target.exists(),'El destino ya existe: reanudarlo, no reemplazarlo'
    np.savez_compressed(target,**state)
    report=dict(schema_version='1.0.0',source=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        target=target.name,configuration_old=old,configuration_new=new,continued_from_time=float(state['step'])*new['dt'],
        outer_annulus_width=20,outer_annulus_energy_fraction=bound,energy_change_from_outer_face_relative=float(-2*np.pi*boundary/total),
        prior_steps_repeated=False,scope='Misma malla interior, relleno nulo exterior con energía de borde comprobada; no extiende la validez física del modelo.')
    (source.parent/f'{tag}_transferencia.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
