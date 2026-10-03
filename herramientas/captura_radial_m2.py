"""E04/RES1: asentamiento conservativo desde un paquete gaussiano cargado.

La fuente primaria del paquete NO se deriva. El dato inicial no es una Q-ball
final ni usa amortiguamiento. Se cuentan energia y carga de ambos campos.
"""
from pathlib import Path
import argparse,json,time,traceback
import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from modelo_m2 import BENCHMARK as model
from soluciones_m2 import solve_state,measures
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/preparacion';O.mkdir(parents=True,exist_ok=True)

def run(width=8.,dx=.2,dt=.004,tmax=240.,radius=260.):
    n=int(round(radius/dx));dx=radius/n;edges=np.linspace(0,radius,n+1);r=(edges[1:]+edges[:-1])/2
    config=dict(width=width,dx=dx,dt=dt,radius=radius,tmax=tmax,n=n,core_radius=40)
    tag=f'w{width:.2f}_h{dx:.3f}_dt{dt:.4f}_R{radius:.0f}_T{tmax:.0f}'
    result_path=O/f'{tag}.json';state_path=O/f'{tag}_estado.npz'
    if result_path.exists():
        saved=json.loads(result_path.read_text())
        assert saved['configuration']==config,'Configuración distinta del resultado existente'
        with np.load(state_path,allow_pickle=False) as state:
            assert abs(int(state['step'])*dt-tmax)<1e-10,'Resultado final sin estado terminado'
            assert all(np.isfinite(state[k]).all() for k in ['phi','vel','chi','vchi','rows'])
        (O/f'{tag}_progreso.json').write_text(json.dumps(dict(status='CALCULO_TERMINADO',step=int(round(tmax/dt)),time=tmax,
            result=result_path.name,restart_file=state_path.name,stage_complete=False,existing_result_verified_without_evolution=True),indent=2)+'\n')
        print('REUTILIZADO',result_path.name,flush=True)
        if not saved['balance_passed']:raise SystemExit(1)
        return saved
    weight=np.diff(edges**3)/3;conduct=edges[1:-1]**2/dx
    diag=np.zeros(n);diag[:-1]+=conduct;diag[1:]+=conduct;diag[-1]+=2*radius**2/dx
    lap_matrix=diags([-conduct/weight[1:],diag/weight,-conduct/weight[:-1]],[-1,0,1],format='csc')
    reference=json.loads((R/'validacion/cierre_m2.json').read_text())['field_convergence'][-1]
    target_q=reference['Qhat'];omega=.9
    f=np.exp(-r*r/(2*width**2));f*=np.sqrt(target_q/(8*np.pi*omega*np.dot(weight,f*f)))
    phi=f.astype(complex);vel=1j*omega*phi
    # Minimize mediator energy for the specified packet, using the same discrete action.
    chi=spsolve(lap_matrix+diags(model.mediator**2+model.mixed*f*f),-model.trilinear*f*f)
    vchi=np.zeros(n)
    initial=np.c_[r,phi.real,phi.imag,vel.real,vel.imag,chi,vchi]
    def lap(q):
        flux=np.zeros(n+1,dtype=q.dtype);flux[1:-1]=conduct*np.diff(q)
        flux[-1]=-2*radius**2*q[-1]/dx
        return np.diff(flux)/weight
    def forces(phi,chi):
        s=abs(phi)**2
        return lap(phi)-(model.mass2+2*model.quartic*s+model.trilinear*chi+.5*model.mixed*chi**2)*phi,lap(chi)-(model.mediator**2+model.mixed*s)*chi-model.trilinear*s
    core=int(round(40/dx));near=int(round(30/dx))
    def measure(t):
        bulk=weight*(abs(vel)**2+.5*vchi*vchi+model.potential(abs(phi),chi))
        faces=conduct*(abs(np.diff(phi))**2+.5*np.diff(chi)**2)
        boundary=2*radius**2/dx*(abs(phi[-1])**2+.5*chi[-1]**2)
        energy=4*np.pi*(bulk.sum()+faces.sum()+boundary)
        core_energy=4*np.pi*(bulk[:core].sum()+faces[:core-1].sum()+.5*faces[core-1])
        qcells=8*np.pi*weight*np.imag(np.conj(phi)*vel);charge=qcells.sum();core_q=qcells[:core].sum()
        return [t,float(energy),float(charge),float(core_energy),float(core_q),float(abs(phi[0]))]
    steps=int(round(tmax/dt));stride=max(1,steps//600);rows=[measure(0)];start=time.perf_counter()
    late=[];start_step=0;previous_elapsed=0.
    if state_path.exists():
        with np.load(state_path,allow_pickle=False) as state:
            assert json.loads(str(state['config']))==config,'Configuración distinta del checkpoint'
            phi=state['phi'];vel=state['vel'];chi=state['chi'];vchi=state['vchi'];initial=state['initial']
            rows=state['rows'].tolist();late=list(state['late']);start_step=int(state['step']);previous_elapsed=float(state['elapsed'])
        print('REANUDADO',tag,'paso',start_step,flush=True)
    def checkpoint(step):
        temp=state_path.with_suffix('.tmp')
        with temp.open('wb') as f:
            np.savez_compressed(f,phi=phi,vel=vel,chi=chi,vchi=vchi,initial=initial,rows=np.asarray(rows),late=np.asarray(late),
                step=step,elapsed=previous_elapsed+time.perf_counter()-start,config=json.dumps(config))
        temp.replace(state_path)
        (O/f'{tag}_progreso.json').write_text(json.dumps(dict(status='EN_PROGRESO' if step<steps else 'EVOLUCION_TERMINADA_DIAGNOSTICO_PENDIENTE',
            step=step,total_steps=steps,time=step*dt,restart_file=state_path.name,configuration=config),indent=2)+'\n')
    if start_step==0:checkpoint(0)
    acc,acc_chi=forces(phi,chi)
    for k in range(start_step,steps):
        vel+=dt/2*acc;vchi+=dt/2*acc_chi;phi+=dt*vel;chi+=dt*vchi
        acc,acc_chi=forces(phi,chi);vel+=dt/2*acc;vchi+=dt/2*acc_chi
        if (k+1)%stride==0:
            rows.append(measure((k+1)*dt))
            if (k+1)*dt>=.8*tmax:late.append(abs(phi[:near]).copy())
        if (k+1)%max(1,steps//24)==0:
            checkpoint(k+1);print('EVOLUCION',tag,(k+1)*dt,flush=True)
    if rows[-1][0]<steps*dt:rows.append(measure(steps*dt))
    checkpoint(steps);a=np.asarray(rows)
    np.savetxt(O/f'{tag}_tiempo.csv',a,delimiter=',',header='t,E_total,Q_total,E_core_r40,Q_core_r40,abs_Phi_center',comments='')
    np.savetxt(O/f'{tag}_inicial.csv',initial,delimiter=',',header='r,RePhi,ImPhi,ReVel,ImVel,chi,chi_vel',comments='')
    np.savetxt(O/f'{tag}_final.csv',np.c_[r,phi.real,phi.imag,vel.real,vel.imag,chi,vchi],delimiter=',',header='r,RePhi,ImPhi,ReVel,ImVel,chi,chi_vel',comments='')
    # Equilibrium comparison at the MEASURED retained charge, with interpolation
    # only as a first seed. This is a diagnostic, not a fitted dynamical source.
    branch=json.loads((R/'validacion/P06/rama/resultados.json').read_text())['rows']
    stable=sorted([b for b in branch if b['omega']<=.98],key=lambda b:b['Q'])
    coreq=float(np.mean(a[a[:,0]>=.8*tmax,4]));ws=float(PchipInterpolator([b['Q'] for b in stable],[b['omega'] for b in stable],extrapolate=False)(coreq))
    fit=None
    fit_error=None
    if np.isfinite(ws):
        nearest=min(stable,key=lambda b:abs(b['omega']-ws));raw=np.loadtxt(R/f"validacion/P06/rama/perfil_w{nearest['omega']:.5f}.csv",delimiter=',',skiprows=1)
        fs=CubicHermiteSpline(raw[:,0],raw[:,1],raw[:,2]);zs=CubicHermiteSpline(raw[:,0],raw[:,3],raw[:,4])
        bg=solve_state(omega=nearest['omega'],previous=lambda x:np.array([fs(x),fs(x,1),zs(x),zs(x,1)]),n=1800)
        for wi in np.linspace(nearest['omega'],ws,int(np.ceil(abs(ws-nearest['omega'])/.0002))+1)[1:]:bg=solve_state(omega=float(wi),previous=bg,n=1800)
        ref=bg.sol(r[:near])[0];den=np.dot(weight[:near],ref*ref)
        deviations=[float(np.sqrt(np.dot(weight[:near],(q-ref)**2)/den)) for q in late]
        eq=measures(bg,ws)
        fit=dict(omega_estimate=ws,equilibrium_charge=eq['Q'],mean_retained_charge=coreq,charge_matching_relative=abs(eq['Q']/coreq-1),
                 max_late_profile_deviation=max(deviations),min_late_profile_deviation=min(deviations),equilibrium_energy=eq['E'],
                 method='omega(Q) PCHIP seed, then full two-field stationary solve; residual charge mismatch explicitly reported')
    energy_drift=float(np.max(abs(a[:,1]/a[0,1]-1)));charge_drift=float(np.max(abs(a[:,2]/a[0,2]-1)))
    result=dict(schema_version='1.1.0',configuration=config,
                initial_energy=float(a[0,1]),initial_charge=float(a[0,2]),initial_E_over_Q=float(a[0,1]/a[0,2]),
                initial_energy_above_reference=float(a[0,1]-reference['Ehat']),final_core_energy=float(a[-1,3]),final_core_charge=float(a[-1,4]),
                final_energy_outside_core=float(a[-1,1]-a[-1,3]),final_charge_outside_core=float(a[-1,2]-a[-1,4]),
                mean_late_charge_fraction=coreq/a[0,2],relative_energy_drift=energy_drift,relative_charge_drift=charge_drift,
                equilibrium_diagnostic=fit,elapsed_seconds=previous_elapsed+time.perf_counter()-start,
                balance_passed=bool(energy_drift<2e-4 and charge_drift<1e-9),
                primary_source_derived=False,shutdown_derived=False,full_3D_test=False,complete_RES1=False,
                interpretation='Conditional radial relaxation from a pre-existing dressed charged packet. No vacuum start, no source construction, no artificial damping. Exterior retains emitted energy and charge.')
    result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (O/f'{tag}_progreso.json').write_text(json.dumps(dict(status='CALCULO_TERMINADO',step=steps,time=steps*dt,result=result_path.name,
        restart_file=state_path.name,stage_complete=False),indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    if not result['balance_passed']:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--width',type=float,default=8);p.add_argument('--dx',type=float,default=.2);p.add_argument('--dt',type=float,default=.004);p.add_argument('--tmax',type=float,default=240);p.add_argument('--radius',type=float,default=260)
    run(**vars(p.parse_args()))
