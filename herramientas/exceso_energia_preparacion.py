"""Resta el equilibrio de la MISMA acción discreta antes de estimar excitación.

El continuo sustraído a una energía FV introduce un sesgo de orden h² que
puede dominar la pequeña diferencia. Conserva ambos diagnósticos.
"""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import diags,bmat,csc_matrix
from scipy.sparse.linalg import spsolve
from scipy.interpolate import CubicSpline
from modelo_m2 import BENCHMARK as m
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/preparacion'

def equilibrium(record,radius):
    dx=record['configuration']['dx'];n=int(round(radius/dx));edges=np.arange(n+1)*dx;r=(edges[1:]+edges[:-1])/2
    weight=np.diff(edges**3)/3;conduct=edges[1:-1]**2/dx;dg=np.zeros(n);dg[:-1]+=conduct;dg[1:]+=conduct;dg[-1]+=2*radius**2/dx
    L=diags([-conduct/weight[1:],dg/weight,-conduct/weight[:-1]],[-1,0,1],format='csc')
    seed=np.loadtxt(O/f"{record['run']}_perfil_referencia.csv",delimiter=',',skiprows=1)
    # The equilibrium seed is tabulated to r=30; a decaying tail is only an
    # initial guess, then every cell must satisfy the full two-field equations.
    w=record['equilibrium_omega'];target=record['mean_late_core_charge'];kap=np.sqrt(m.mass2-w*w)
    f=np.where(r<=seed[-1,0],CubicSpline(seed[:,0],seed[:,1])(np.minimum(r,seed[-1,0])),seed[-1,1]*seed[-1,0]/r*np.exp(-kap*(r-seed[-1,0])))
    z=np.where(r<=seed[-1,0],CubicSpline(seed[:,0],seed[:,2])(np.minimum(r,seed[-1,0])),seed[-1,2]*(seed[-1,0]/r)**2*np.exp(-2*kap*(r-seed[-1,0])))
    for iteration in range(12):
        F=L@f+(m.mass2-w*w+2*m.quartic*f*f+m.trilinear*z+.5*m.mixed*z*z)*f
        Z=L@z+(m.mediator**2+m.mixed*f*f)*z+m.trilinear*f*f
        Q=8*np.pi*w*np.dot(weight,f*f);res=np.r_[F,Z,Q/target-1]
        if max(abs(F))<1e-10 and max(abs(Z))<1e-8 and abs(Q/target-1)<1e-12:break
        A=L+diags(m.mass2-w*w+6*m.quartic*f*f+m.trilinear*z+.5*m.mixed*z*z)
        B=diags(f*(m.trilinear+m.mixed*z));D=L+diags(m.mediator**2+m.mixed*f*f)
        J=bmat([[A,B,csc_matrix((-2*w*f)[:,None])],[2*B,D,csc_matrix((n,1))],
            [csc_matrix((16*np.pi*w*weight*f/target)[None,:]),csc_matrix((1,n)),csc_matrix([[Q/w/target]])]],format='csc')
        step=spsolve(J,-res);f+=step[:n];z+=step[n:2*n];w+=step[-1]
    else:raise RuntimeError('Equilibrio FV no convergió')
    bulk=weight*(w*w*f*f+m.potential(f,z));faces=conduct*(np.diff(f)**2+.5*np.diff(z)**2)
    E=4*np.pi*(bulk.sum()+faces.sum()+2*radius**2/dx*(f[-1]**2+.5*z[-1]**2))
    return dict(radius=radius,dx=dx,omega=float(w),Q=float(Q),E=float(E),amplitude_residual=float(max(abs(F))),mediator_residual=float(max(abs(Z))),
        charge_relative=abs(Q/target-1),iterations=iteration+1,
        excitation_mean_core_minus_discrete_equilibrium=record['mean_late_core_energy']-float(E))

def run():
    data=json.loads((O/'resultados.json').read_text());rows=[]
    for r in data['records']:
        if r['configuration']['tmax']!=1200:continue
        a=equilibrium(r,60);b=equilibrium(r,80)
        rows.append(dict(run=r['run'],continuum_subtraction_diagnostic=r['mean_core_energy_excess_over_matched_stationary'],
            discrete_equilibria=[a,b],box_energy_difference=abs(a['E']-b['E']),
            estimated_excitation=b['excitation_mean_core_minus_discrete_equilibrium']))
    coarse=next(x for x in rows if 'h0.200' in x['run']);fine=next(x for x in rows if 'h0.100' in x['run'])
    difference=abs(coarse['estimated_excitation']/fine['estimated_excitation']-1)
    passed=bool(difference<.02 and all(x['box_energy_difference']<1e-7 for x in rows))
    result=dict(schema_version='1.0.0',method='Equilibrio a carga fija de la misma acción FV; Newton de dos campos y frecuencia, cajas 60 y 80.',
        rows=rows,relative_mesh_difference=difference,excitation_convergence_passed=passed,
        receiver_solved=False,extractable_energy_demonstrated=False,stage_complete=False,
        caution='Estimación de exceso energético radial, no energía útil demostrada ni eficiencia de un ciclo.')
    (O/'exceso_energia.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not passed:raise SystemExit(1)

if __name__=='__main__':run()
