"""Manufactured bulk symbols and exact free Duhamel; no physical integration."""
from pathlib import Path
from types import SimpleNamespace
import argparse, hashlib, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import numpy as np

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kappa(k,h,order):
    a=4*np.sin(k*h/2)**2/h**2
    return a if order==2 else a+h*h*a*a/12
def transfer(theta):
    eta=(1-np.cos(theta))/(2+np.cos(theta))
    a=.75+21*eta/64;b=.25+15*eta/64
    return float(a*np.cos(theta/4)+b*np.cos(3*theta/4)),float(a*np.sin(theta/4)-b*np.sin(3*theta/4))
def propagator(w,t,mass):
    return np.cos(w*t)-1j*mass/w*np.sin(w*t),-w*np.sin(w*t)-1j*mass*np.cos(w*t)
def power(q,v,mass):return float(abs(q)**2+abs(v/mass)**2)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--home',type=Path,required=True);ap.add_argument('--prereg-commit',required=True)
    args=ap.parse_args();home=args.home.resolve();folder=Path(__file__).parent
    assert len(args.prereg_commit)==40 and all(c in '0123456789abcdef' for c in args.prereg_commit)
    out=folder/'resultados.json';assert not out.exists()
    root=home/'science';identity=json.loads((home/'preregistration/identidad_cientifica.json').read_text())
    assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    sys.path.insert(0,str(root/'herramientas'))
    from observador_causal_CP12 import interpolate, model
    mass=model.mediator;assert mass==100
    cuts=[2,4,8,12,20];hc=.125;hf=.0625;times=[24,48,160];steps=[hc,hf,.03125,.015625]
    rc=(np.arange(1760)+.5)*hc;rf=(np.arange(3520)+.5)*hf
    interior=(rf>=32*hc)&(rf<=220-32*hc)
    checks=[];dispersion=[];duhamel=[];max_residual=0.
    for k in cuts:
        A,B=transfer(k*hc);ka=k+2*np.pi/hc
        actual=interpolate(SimpleNamespace(r=rc),np.exp(1j*k*rc)[:,None],SimpleNamespace(r=rf))[:,0]
        predicted=A*np.exp(1j*k*rf)+B*np.exp(1j*ka*rf)
        residual=float(np.max(abs(actual[interior]-predicted[interior])))
        assert residual<=2e-11
        checks.append(dict(k=k,low_amplitude=A,image_amplitude=B,image_wave_number=ka,original_CubicSpline_interior_absolute_residual=residual))
        wc=np.sqrt(mass**2+kappa(k,hc,2));wf=[np.sqrt(mass**2+kappa(kj,hf,2)) for kj in [k,ka]]
        source=[a*(w*w-wc*wc) for a,w in zip([A,B],wf)]
        source_power=[float(abs(s)**2) for s in source]
        for t in times:
            qc,vc=propagator(wc,t,mass)
            qf,vf=propagator(wf[0],t,mass)
            exact=[(A*qc-qf,A*vc-vf),(B*qc,B*vc)]
            parts=[]
            for j,(amplitude,w) in enumerate(zip([A,B],wf)):
                qj,vj=propagator(w,t,mass)
                initial_amplitude=amplitude-1 if j==0 else amplitude
                initial=(initial_amplitude*qj,initial_amplitude*vj)
                response=(amplitude*(qc-qj),amplitude*(vc-vj))
                error=max(abs(initial[0]+response[0]-exact[j][0]),abs((initial[1]+response[1]-exact[j][1])/mass))
                max_residual=max(max_residual,float(error));assert error<=2e-11
                p0=power(*initial,mass);p1=power(*response,mass);pt=power(*exact[j],mass)
                parts.append(dict(component='low' if j==0 else 'image',frequency=float(w),initial_phase_power=p0,operator_response_phase_power=p1,total_phase_power=pt,cross_term=pt-p0-p1))
            duhamel.append(dict(k=k,time=t,coarse_frequency=float(wc),source_squared_norm=sum(source_power),source_image_power_fraction=source_power[1]/sum(source_power),components=parts,relative_unit_phase_contrast=float(np.sqrt(sum(x['total_phase_power'] for x in parts)/2))))
        continuum=np.sqrt(mass**2+k*k)
        records={}
        for order in [2,4]:
            frequencies=[float(np.sqrt(mass**2+kappa(k,h,order))) for h in steps]
            errors=[abs(w-continuum) for w in frequencies]
            records[str(order)]=dict(steps=steps,frequencies=frequencies,absolute_frequency_errors=errors,refinement_orders=[float(np.log2(a/b)) for a,b in zip(errors[:-1],errors[1:])],coarse_fine_phase_mismatch={str(t):abs(frequencies[0]-frequencies[1])*t for t in times})
        dispersion.append(dict(k=k,continuous_frequency=float(continuum),symbols=records,phase_ratio_candidate_to_original=records['4']['coarse_fine_phase_mismatch']['160']/records['2']['coarse_fine_phase_mismatch']['160']))
    assert all(sha(root/n)==h for n,h in identity['code_hashes'].items())
    meta=json.loads((home/'preregistration/nueva_identidad.json').read_text())
    result=dict(schema='CP12_PASSIVE_MANUFACTURED_BULK_SYMBOL_AND_INTERPOLATION',execution_uuid=meta['execution_uuid'],execution_run_id=meta['execution_run_id'],preregistration_git_commit=args.prereg_commit,preregistration_sha256=sha(folder/'PRERREGISTRO.md'),source_sha256=sha(Path(__file__)),original_interpolator_source_sha256=sha(root/'herramientas/observador_causal_CP12.py'),M2_steps=0,physical_observers_changed=False,physical_gate_evaluated=False,physical_correction_tested=False,CP12_closed=False,mass=mass,wave_number_cuts=cuts,transfer_checks=checks,exact_free_Duhamel_max_absolute_residual=max_residual,dispersion=dispersion,duhamel=duhamel,limits='Manufactured interior/free-wave reference; not a reconstruction of radial interacting CP12 histories. The full candidate has only demonstrated global spectral order two and some modes worsen.')
    temp=out.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');temp.replace(out)
    print(json.dumps(dict(M2_steps=0,interpolation_max_residual=max(x['original_CubicSpline_interior_absolute_residual'] for x in checks),Duhamel_max_residual=max_residual,phase_mismatch_at_160=[{'k':x['k'],'original':x['symbols']['2']['coarse_fine_phase_mismatch']['160'],'candidate':x['symbols']['4']['coarse_fine_phase_mismatch']['160']} for x in dispersion],CP12_closed=False)))

if __name__=='__main__':main()
