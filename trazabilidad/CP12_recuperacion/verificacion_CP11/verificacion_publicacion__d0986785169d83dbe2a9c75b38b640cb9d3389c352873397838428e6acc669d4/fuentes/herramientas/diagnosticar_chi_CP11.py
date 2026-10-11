"""Diagnósticos prerregistrados CP11 sobre estados CP10; cero pasos M2 nuevos.

Entrar mediante ejecutar_protocolo.py. Los controles libres/congelados son
contrafactuales analíticos, nunca estados físicos ni criterios de aceptación.
"""
from pathlib import Path
import argparse
import csv
import json
import numpy as np
from scipy.interpolate import CubicSpline, interp1d
from scipy.linalg import eigh_tridiagonal, solve_banded
from scipy.optimize import brentq
from scipy.special import spherical_jn
from scipy.sparse.linalg import LinearOperator, cg
from threadpoolctl import threadpool_limits, threadpool_info
from modelo_m2 import BENCHMARK as model
from continuar_no_radial_m2 import Evolution
from diagnosticar_mediador_CP10 import load, compare

ROOT = Path(__file__).resolve().parents[1]


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def grid(data):
    h = data['configuration']['dx']
    n = data['q'].shape[1]
    r = (np.arange(n)+.5)*h
    w = np.diff((np.arange(n+1)*h)**3)/3
    return r, w


def chi_metrics(cq, cv, fq, fv, ci, cvi, fi, fvi, w):
    """Todos los modos no radiales; ambos denominadores se conservan."""
    def norm(q, v=None):
        a = q[:, 1:]**2
        if v is not None:
            a = a+v[:, 1:]**2/model.mediator**2
        return float(np.sum(w[:, None]*a))
    dq, dv = cq-fq, cv-fv
    values = {'field_numerator':norm(dq), 'phase_space_numerator':norm(dq,dv),
              'fine_initial_field_squared':norm(fi), 'coarse_initial_field_squared':norm(ci),
              'fine_initial_phase_space_squared':norm(fi,fvi),
              'coarse_initial_phase_space_squared':norm(ci,cvi)}
    for den in ['fine','coarse']:
        values['field_error_'+den+'_denominator'] = float(np.sqrt(values['field_numerator']/values[den+'_initial_field_squared']))
        values['phase_space_error_'+den+'_denominator'] = float(np.sqrt(values['phase_space_numerator']/values[den+'_initial_phase_space_squared']))
    values['initial_phase_space_difference'] = float(np.sqrt(norm(ci-fi,cvi-fvi)/values['fine_initial_phase_space_squared']))
    return values


def interpolate(r, values, target, method='cubic', labels=None):
    if method == 'linear':
        return interp1d(r,values,axis=0,kind='linear',fill_value='extrapolate')(target)
    if method == 'parity':
        parity = (-1.0)**labels[:,0].astype(int)
        return CubicSpline(np.r_[-r[::-1],r],np.concatenate([values[::-1]*parity,values]),axis=0)(target)
    return CubicSpline(r,values,axis=0)(target)


def metric_audit(coarse, fine, cfg):
    rc,wc = grid(coarse); rf,wf = grid(fine); core = cfg['core_radius']
    def sample(data,r,target,method='cubic'):
        return [interpolate(r,data[key][2],target,method,data['labels'])
                for key in ['q','v','initial_q','initial_v']]
    def measure(target,w,method='cubic'):
        c = sample(coarse,rc,target,method); f = sample(fine,rf,target,method)
        return chi_metrics(c[0],c[1],f[0],f[1],c[2],c[3],f[2],f[3],w)
    use = rf<core
    original = measure(rf[use],wf[use])
    cp10 = compare(ROOT/cfg['states']['coarse'],ROOT/cfg['states']['fine'])
    assert np.isclose(original['phase_space_error_fine_denominator'],cp10['final_mediator_phase_space_error_over_initial_norm'],rtol=1e-13,atol=1e-15)
    reverse = measure(rc[rc<core],wc[rc<core])
    knots = np.unique(np.r_[0,rc[rc<core],rf[rf<core],core])
    continuous = {}
    for order in cfg['quadrature_orders']:
        x, wg = np.polynomial.legendre.leggauss(order)
        a,b = knots[:-1,None],knots[1:,None]
        target = ((a+b)/2+(b-a)/2*x).ravel()
        weights = (((b-a)/2*wg).ravel())*target**2
        continuous[str(order)] = measure(target,weights)
        if order == cfg['quadrature_orders'][-1]:
            parity = measure(target,weights,'parity')
    linear = measure(rf[use],wf[use],'linear')
    # Fine -> coarse -> fine: isolate information lost by this representation.
    fq,fv,fi,fvi = sample(fine,rf,rf[use])
    qc = interpolate(rf,fine['q'][2],rc)
    vc = interpolate(rf,fine['v'][2],rc)
    roundtrip = chi_metrics(interpolate(rc,qc,rf[use]),interpolate(rc,vc,rf[use]),fq,fv,fi,fvi,fi,fvi,wf[use])
    manufactured = {}
    for ell in [2,4]:
        func = lambda r: r**ell*np.exp(-(r/8)**2)*(1+.2*np.cos(2*r))
        exact = func(rf[use]); got = CubicSpline(rc,func(rc))(rf[use])
        manufactured[str(ell)] = float(np.sqrt(np.sum(wf[use]*(got-exact)**2)/np.sum(wf[use]*exact**2)))
    independent = [reverse,continuous[str(cfg['quadrature_orders'][-1])],parity]
    rejected = all(row['phase_space_error_'+den+'_denominator']>.02 for row in independent for den in ['fine','coarse'])
    return dict(CP10_metric_reproduced=True, original=original, reverse=reverse,
                continuous_union_knots_Gauss=continuous, parity_at_origin=parity,
                lower_order_linear_sensitivity=linear, fine_coarse_fine_roundtrip=roundtrip,
                manufactured_regular_fields_errors=manufactured,
                artificial_threshold_crossing_explanation_rejected=rejected,
                used_to_change_acceptance=False)


def tridiagonal(sim, ell):
    """Independent weighted matrix of the SAME FV quadratic form."""
    k = np.full(sim.n,sim.dx*ell*(ell+1),dtype=float)
    k[:-1] += sim.c; k[1:] += sim.c
    k[-1] += 2*sim.radius**2/sim.dx
    return k/sim.w,-sim.c/np.sqrt(sim.w[:-1]*sim.w[1:])


def apply_tri(d,e,x):
    out = d[:,None]*x
    out[:-1] += e[:,None]*x[1:]
    out[1:] += e[:,None]*x[:-1]
    return out


def operator_audit(sim,cfg):
    rng = np.random.default_rng(cfg['manufactured_seed'])
    q = rng.normal(size=(3,sim.n,sim.nm))
    expected = -sim.lap(q)[2]*np.sqrt(sim.w[:,None])
    x = q[2]*np.sqrt(sim.w[:,None]); actual = np.empty_like(x)
    for ell in range(sim.ell.max()+1):
        sel = sim.ell==ell; d,e = tridiagonal(sim,ell)
        actual[:,sel] = apply_tri(d,e,x[:,sel])
    action = float(np.linalg.norm(actual-expected)/np.linalg.norm(expected))
    y = rng.normal(size=x.shape); ay = np.empty_like(y)
    for ell in range(sim.ell.max()+1):
        sel = sim.ell==ell; d,e = tridiagonal(sim,ell)
        ay[:,sel] = apply_tri(d,e,y[:,sel])
    symmetry = float(abs(np.sum(x*ay)-np.sum(actual*y))/(np.linalg.norm(x)*np.linalg.norm(ay)+np.linalg.norm(y)*np.linalg.norm(actual)))
    form = float(np.sum(x*actual))
    return dict(action_relative_error=action,weighted_symmetry_relative_error=symmetry,
                random_quadratic_form=form,passed=action<cfg['algebra_relative_tolerance'] and symmetry<cfg['algebra_relative_tolerance'] and form>0,
                central_boundary='flujo cero',outer_boundary='Dirichlet en R, media celda',
                proof='K=D^T c D + dr ell(ell+1) I + 2 R^2/dr e_N e_N^T; forma positiva.')


def continuum_roots(ell,n):
    # Sign scanning resolves every root for ell<=4, including the first one.
    x = np.arange(.01,(n+ell+3)*np.pi,np.pi/4)
    y = spherical_jn(ell,x)
    idx = np.flatnonzero(y[:-1]*y[1:]<0)
    roots = [brentq(lambda z:spherical_jn(ell,z),x[j],x[j+1],xtol=1e-12,rtol=1e-14) for j in idx[:n]]
    if len(roots)!=n:
        raise ValueError('No se aislaron todas las raíces continuas')
    return np.asarray(roots)


def modal_power(U,w,q,v):
    a,b = U.T@(np.sqrt(w[:,None])*q),U.T@(np.sqrt(w[:,None])*v/model.mediator)
    return np.sum(a*a+b*b,axis=1)


def fractions(power,k,cuts):
    total = float(power.sum())
    return {str(cut):float(power[k>cut].sum()/total) if total else 0.0 for cut in cuts}


def radial_diagnostics(c,f,cfg,out):
    rc,wc=grid(c);rf,wf=grid(f); core=cfg['core_radius']
    sims = [Evolution(data['configuration']['dx'],cfg['radius'],cfg['L']) for data in [c,f]]
    audits = [operator_audit(s,cfg) for s in sims]
    cq=interpolate(rc,c['q'][2],rf);cv=interpolate(rc,c['v'][2],rf)
    dq,dv = cq-f['q'][2],cv-f['v'][2]
    sharp = (rf<core).astype(float)
    smooth = np.ones_like(rf)
    transition = (rf>=cfg['smooth_core_start']) & (rf<core)
    smooth[transition] = .5*(1+np.cos(np.pi*(rf[transition]-cfg['smooth_core_start'])/(core-cfg['smooth_core_start'])))
    smooth[rf>=core]=0
    free = [dict(q=np.zeros_like(data['q'][2]),v=np.zeros_like(data['v'][2])) for data in [c,f]]
    total_error = np.zeros(len(rf));smooth_error=np.zeros(len(rf))
    summaries=[];rows=[];samples=[];parseval=[];residuals=[];conservation=[]
    for ell in cfg['ell']:
        bases=[]
        for s in sims:
            d,e=tridiagonal(s,ell)
            lam,U=eigh_tridiagonal(d,e,lapack_driver='stemr')
            if lam.min()<=0:
                raise ValueError('Modo espacial no positivo')
            idx=np.unique(np.r_[0,1,4,len(lam)//2,len(lam)-1])
            mode_error = np.linalg.norm(apply_tri(d,e,U[:,idx])-U[:,idx]*lam[idx])/(np.linalg.norm(d)*np.linalg.norm(U[:,idx]))
            residuals.append(float(mode_error));bases.append((lam,U))
        lc,Uc=bases[0];lf,Uf=bases[1];k=np.sqrt(lf)
        pc=[];pf=[]
        for data,s,(lam,U),dest in zip([c,f],sims,bases,free):
            sel=s.ell==ell
            pi=modal_power(U,s.w,data['initial_q'][2][:,sel],data['initial_v'][2][:,sel])
            final=modal_power(U,s.w,data['q'][2][:,sel],data['v'][2][:,sel])
            a=U.T@(np.sqrt(s.w[:,None])*data['initial_q'][2][:,sel])
            b=U.T@(np.sqrt(s.w[:,None])*data['initial_v'][2][:,sel])
            om=np.sqrt(model.mediator**2+lam); angle=om*cfg['time']
            aq=a*np.cos(angle[:,None])+b/om[:,None]*np.sin(angle[:,None])
            av=-a*om[:,None]*np.sin(angle[:,None])+b*np.cos(angle[:,None])
            dest['q'][:,sel]=(U@aq)/np.sqrt(s.w[:,None]);dest['v'][:,sel]=(U@av)/np.sqrt(s.w[:,None])
            en0=float(np.sum((om[:,None]*a)**2+b*b));en1=float(np.sum((om[:,None]*aq)**2+av*av))
            conservation.append(abs(en1-en0)/en0 if en0 else 0.)
            expected=np.sum(s.w[:,None]*(data['q'][2][:,sel]**2+data['v'][2][:,sel]**2/model.mediator**2))
            parseval.append(float(abs(final.sum()-expected)/max(expected,1e-300)))
            summaries.append(dict(ell=ell,dx=s.dx,initial_squared_norm=float(pi.sum()),final_squared_norm=float(final.sum()),
                                  initial_fractions_above_k=fractions(pi,np.sqrt(lam),cfg['wave_number_cuts']),
                                  final_fractions_above_k=fractions(final,np.sqrt(lam),cfg['wave_number_cuts'])))
            if data is c:pc=pi
            else:pf=pi
        sel=sims[1].ell==ell
        err=modal_power(Uf,wf,dq[:,sel]*sharp[:,None],dv[:,sel]*sharp[:,None])
        errsmooth=modal_power(Uf,wf,dq[:,sel]*smooth[:,None],dv[:,sel]*smooth[:,None])
        total_error+=err;smooth_error+=errsmooth
        continuum=(continuum_roots(ell,len(lf))/cfg['radius'])**2
        delta=cfg['time']*(np.sqrt(model.mediator**2+lc)-np.sqrt(model.mediator**2+lf[:len(lc)]))
        selected=np.unique(np.r_[0,1,4,[np.argmin(abs(np.sqrt(continuum)-cut)) for cut in cfg['wave_number_cuts']]])
        for i in selected:
            if i>=len(lc):continue
            samples.append(dict(ell=ell,mode_index=int(i+1),continuum_k=float(np.sqrt(continuum[i])),
                                lambda_coarse=float(lc[i]),lambda_fine=float(lf[i]),lambda_continuum=float(continuum[i]),
                                phase_coarse_minus_fine=float(delta[i])))
        for i in range(len(lf)):
            rows.append([ell,i+1,float(lf[i]),float(continuum[i]),float(lc[i]) if i<len(lc) else '',
                         float(delta[i]) if i<len(lc) else '',float(err[i]),float(errsmooth[i]),
                         float(pc[i]) if i<len(pc) else '',float(pf[i])])
    # Group modes by physical eigenvalue, not by a Cartesian surrogate.
    error_fractions={};smooth_fractions={}
    for cut in cfg['wave_number_cuts']:
        error_fractions[str(cut)]=float(sum(row[6] for row in rows if np.sqrt(row[2])>cut)/total_error.sum())
        smooth_fractions[str(cut)]=float(sum(row[7] for row in rows if np.sqrt(row[2])>cut)/smooth_error.sum())
    with (out/'modos_radiales.csv').open('w') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['ell','index','lambda_fine','lambda_continuum','lambda_coarse','phase_coarse_minus_fine','core_error_power','smooth_core_error_power','initial_coarse_power','initial_fine_power']);writer.writerows(rows)
    use=rf<core
    ci=interpolate(rc,c['initial_q'][2],rf[use]);cvi=interpolate(rc,c['initial_v'][2],rf[use])
    fq=interpolate(rc,free[0]['q'],rf[use]);fv=interpolate(rc,free[0]['v'],rf[use])
    free_metric=chi_metrics(fq,fv,free[1]['q'][use],free[1]['v'][use],ci,cvi,f['initial_q'][2,use],f['initial_v'][2,use],wf[use])
    zd=(dq[use]+1j*dv[use]/model.mediator)[:,1:]
    zfree=(fq-free[1]['q'][use]+1j*(fv-free[1]['v'][use])/model.mediator)[:,1:]
    dot=float(np.real(np.sum(wf[use,None]*np.conj(zd)*zfree)))
    actual_power=float(np.sum(wf[use,None]*abs(zd)**2));free_power=float(np.sum(wf[use,None]*abs(zfree)**2))
    cosine=dot/np.sqrt(actual_power*free_power) if free_power else 0.
    sufficient=free_power/actual_power>=cfg['free_prediction_squared_fraction_min'] and cosine>=cfg['free_prediction_vector_cosine_min']
    passed=all(a['passed'] for a in audits) and max(parseval)<cfg['parseval_relative_tolerance'] and max(residuals)<cfg['algebra_relative_tolerance'] and max(conservation)<cfg['algebra_relative_tolerance']
    return dict(operator_audits=audits,algebra_passed=passed,max_parseval_relative_error=max(parseval),
                max_eigenmode_relative_residual=max(residuals),max_free_energy_relative_drift=max(conservation),
                spectra=summaries,actual_core_error_fractions_above_k=error_fractions,
                actual_smooth_core_error_fractions_above_k=smooth_fractions,
                smooth_core_power_retained=float(smooth_error.sum()/total_error.sum()),
                eigenvalue_phase_examples=samples,free_initial_propagator=free_metric,
                free_initial_squared_difference_over_actual=free_power/actual_power,
                free_initial_difference_vector_cosine=float(cosine),free_initial_explanation_sufficient=bool(sufficient),
                short_components_predominate=error_fractions['4']>cfg['short_component_predominance_min'],
                interpretation='Autobase del operador radial FV de R=220; no espectro del generador M2 acoplado. El corte del núcleo no cambia el operador.')


def frozen_equilibrium(data,sim,q,v,cfg):
    """Diagnostic elliptic solve, projected full rho, in mass-weighted variables."""
    sqrtw=np.sqrt(sim.w[:,None]);a,b=q[:2]@sim.Y
    av,bv=v[:2]@sim.Y;rho=a*a+b*b;drho=2*(a*av+b*bv)
    triangles={ell:tridiagonal(sim,ell) for ell in range(cfg['L']+1)}
    bands={}
    for ell,(d,e) in triangles.items():
        ab=np.zeros((3,sim.n));ab[1]=d+model.mediator**2;ab[0,1:]=e;ab[2,:-1]=e;bands[ell]=ab
    def bare(x):
        ans=np.empty_like(x)
        for ell,(d,e) in triangles.items():
            sel=sim.ell==ell;ans[:,sel]=apply_tri(d+model.mediator**2,e,x[:,sel])
        return ans
    def apply(flat):
        x=flat.reshape(sim.n,sim.nm)
        return (bare(x)+model.mixed*((rho*(x@sim.Y))@sim.YW)).ravel()
    def precondition(flat):
        x=flat.reshape(sim.n,sim.nm);ans=np.empty_like(x)
        for ell,ab in bands.items():
            sel=sim.ell==ell;ans[:,sel]=solve_banded((1,1),ab,x[:,sel],check_finite=False)
        return ans.ravel()
    op=LinearOperator((sim.n*sim.nm,)*2,matvec=apply,dtype=float)
    pre=LinearOperator(op.shape,matvec=precondition,dtype=float)
    def solve(rhs):
        count=[0]
        def called(x):count[0]+=1
        sol,info=cg(op,rhs.ravel(),M=pre,rtol=1e-12,atol=0,maxiter=300,callback=called)
        residual=float(np.linalg.norm(apply(sol)-rhs.ravel())/np.linalg.norm(rhs))
        if info or residual>=cfg['elliptic_relative_tolerance']:
            raise ValueError('Problema elíptico no resuelto: '+str((info,residual)))
        return sol.reshape(sim.n,sim.nm)/sqrtw,dict(relative_residual=residual,iterations=count[0])
    rhs=-model.trilinear*sqrtw*(rho@sim.YW)
    equilibrium,reportq=solve(rhs)
    veq,reportv=solve(-sqrtw*(((model.trilinear+model.mixed*(equilibrium@sim.Y))*drho)@sim.YW))
    source=(model.trilinear*rho+model.mixed*rho*(q[2]@sim.Y))@sim.YW
    lap=np.empty_like(q[2])
    for ell,(d,e) in triangles.items():
        sel=sim.ell==ell
        lap[:,sel]=-apply_tri(d,e,(sqrtw*q[2])[:,sel])/sqrtw
    acceleration=lap-model.mediator**2*q[2]-source
    original=sim.force(q)[2]
    force_error=float(np.linalg.norm(sqrtw*(acceleration-original))/max(np.linalg.norm(sqrtw*source),1e-300))
    if force_error>cfg['algebra_relative_tolerance']:
        raise ValueError('La fuente congelada no traduce la fuerza M2')
    return equilibrium,veq,source,dict(field=reportq,velocity=reportv,force_translation_relative_error=force_error,
                                     positivity_bound='A>=M^2 I; rho>=0 y proyección con cuadratura positiva.')


def source_diagnostics(c,f,cfg,out):
    paths=list((ROOT/'validacion/P06/no_radial/CP11').glob('diagnostico_radial__*/resultados.json'))
    if len(paths)!=1:raise ValueError('Diagnóstico previo ausente o ambiguo')
    previous=json.loads(paths[0].read_text())
    if not previous['radial']['algebra_passed'] or previous['radial']['free_initial_explanation_sufficient']:
        raise ValueError('No se satisface la puerta prerregistrada del contraste fuente')
    sims=[Evolution(d['configuration']['dx'],cfg['radius'],cfg['L']) for d in [c,f]]
    frames=[];audits=[]
    for data,s in zip([c,f],sims):
        frame={}
        for name,qkey,vkey in [('initial','initial_q','initial_v'),('final','q','v')]:
            eq,ev,src,report=frozen_equilibrium(data,s,data[qkey],data[vkey],cfg)
            frame[name]=dict(eq=eq,ev=ev,xi=data[qkey][2]-eq,nu=data[vkey][2]-ev,source=src)
            audits.append(dict(dx=s.dx,frame=name,**report))
        frames.append(frame)
    rc,wc=grid(c);rf,wf=grid(f);use=rf<cfg['core_radius']
    ci=interpolate(rc,c['initial_q'][2],rf[use]);cvi=interpolate(rc,c['initial_v'][2],rf[use])
    fi=f['initial_q'][2,use];fvi=f['initial_v'][2,use]
    def metric(cq,cv,fq,fv):
        return chi_metrics(interpolate(rc,cq,rf[use]),interpolate(rc,cv,rf[use]),fq[use],fv[use],ci,cvi,fi,fvi,wf[use])
    raw=metric(c['q'][2],c['v'][2],f['q'][2],f['v'][2])
    residual=metric(frames[0]['final']['xi'],frames[0]['final']['nu'],frames[1]['final']['xi'],frames[1]['final']['nu'])
    equilibrium_difference=metric(frames[0]['final']['eq'],frames[0]['final']['ev'],frames[1]['final']['eq'],frames[1]['final']['ev'])
    corrected_q=frames[0]['final']['eq'].copy();corrected_v=frames[0]['final']['ev'].copy()
    spectra=[]
    for ell in cfg['ell']:
        dc,ec=tridiagonal(sims[0],ell);df,ef=tridiagonal(sims[1],ell)
        lc,Uc=eigh_tridiagonal(dc,ec,lapack_driver='stemr');lf,Uf=eigh_tridiagonal(df,ef,lapack_driver='stemr')
        wc_freq=np.sqrt(model.mediator**2+lc);wf_freq=np.sqrt(model.mediator**2+lf[:len(lc)])
        delta=(wf_freq-wc_freq)*cfg['time'];sel=sims[0].ell==ell
        aq=Uc.T@(np.sqrt(wc[:,None])*frames[0]['final']['xi'][:,sel])
        av=Uc.T@(np.sqrt(wc[:,None])*frames[0]['final']['nu'][:,sel])
        qcorr=aq*np.cos(delta[:,None])+av/wc_freq[:,None]*np.sin(delta[:,None])
        vcorr=wf_freq[:,None]*(-aq*np.sin(delta[:,None])+av/wc_freq[:,None]*np.cos(delta[:,None]))
        corrected_q[:,sel]+=(Uc@qcorr)/np.sqrt(wc[:,None]);corrected_v[:,sel]+=(Uc@vcorr)/np.sqrt(wc[:,None])
        for data,s,U,lam,frame in zip([c,f],sims,[Uc,Uf],[lc,lf],frames):
            sel=s.ell==ell
            for name in ['initial','final']:
                power=modal_power(U,s.w,frame[name]['xi'][:,sel],frame[name]['nu'][:,sel])
                source_power=modal_power(U,s.w,frame[name]['source'][:,sel]/model.mediator**2,np.zeros_like(frame[name]['source'][:,sel]))
                spectra.append(dict(ell=ell,dx=s.dx,frame=name,residual_squared_norm=float(power.sum()),
                                    residual_fractions_above_k=fractions(power,np.sqrt(lam),cfg['wave_number_cuts']),
                                    source_fractions_above_k=fractions(source_power,np.sqrt(lam),cfg['wave_number_cuts'])))
    corrected=metric(corrected_q,corrected_v,f['q'][2],f['v'][2])
    reduction=1-corrected['phase_space_numerator']/raw['phase_space_numerator']
    return dict(elliptic_audits=audits,raw=raw,fast_residual_difference=residual,
                instantaneous_equilibrium_difference=equilibrium_difference,
                spectral_frozen_source_and_fast_residual=spectra,
                predetermined_modal_correction=corrected,squared_error_reduction=float(reduction),
                supports_delimited_dispersive_explanation=bool(reduction>=cfg['modal_correction_squared_reduction_min']),
                correction_fitted_to_data=False,correction_used_for_acceptance=False,
                coupled_causal_attribution_certified=False,
                missing_evidence='Historia temporal de rho y de sus coeficientes/fuentes modales: los NPZ conservan extremos, no esta trayectoria.',
                next_campaign_authorized_by_this_result=False,
                stop_reason='La respuesta forzada entre extremos no se reconstruye desde norma, E y Q. No escoger otra corrección o malla para aprobar.')


def run(configuration,output):
    case=configuration['case'];cfg=case['configuration']
    c,f=[load(ROOT/cfg['states'][key]) for key in ['coarse','fine']]
    if not np.array_equal(c['labels'],f['labels']) or any(d['time']!=cfg['time'] for d in [c,f]):
        raise ValueError('Estados o modos incompatibles')
    result=dict(checkpoint='CP11_DIAGNOSTICO_RADIAL_CHI',operation=case['operation'],
                observed_threadpools=threadpool_info(),physical_gate_threshold=.02,
                physical_gate='REFINAMIENTO_PENDIENTE',cause_certified=False,
                continuum_error_certified=False,new_M2_evolution_steps=0,
                old_evolutions_repeated=False,fundamental_model_changed=False)
    if not result['observed_threadpools'] or any(p['num_threads']!=1 for p in result['observed_threadpools']):
        raise ValueError('Política de un hilo no observada')
    if case['operation']=='operador_metricas_modos_y_propagador_libre':
        result['metric']=metric_audit(c,f,cfg)
        result['radial']=radial_diagnostics(c,f,cfg,output)
        result['status']='DIAGNOSTICO_RADIAL_COMPLETADO' if result['radial']['algebra_passed'] else 'DEFECTO_ALGEBRAICO_PENDIENTE'
        result['decisions']=[dict(hypothesis='H-METRICA',decision='DESCARTADA_COMO_EXPLICACION_DEL_CRUCE' if result['metric']['artificial_threshold_crossing_explanation_rejected'] else 'NO_DESCARTADA',scope='Métricas spline declaradas; no certificado de continuo.'),
                             dict(hypothesis='H-OPERADOR',decision='DEFECTO_ALGEBRAICO_NO_DETECTADO' if result['radial']['algebra_passed'] else 'DETENER',scope='Acción FV, simetría, positividad y modos; no precisión de fase M2.'),
                             dict(hypothesis='H-LIBRE-INICIAL',decision='INSUFICIENTE' if not result['radial']['free_initial_explanation_sufficient'] else 'COMPATIBLE',scope='Propagador libre de chi inicial completo; no respuesta acoplada.')]
    else:
        result['source']=source_diagnostics(c,f,cfg,output)
        result['status']='DIAGNOSTICO_CAUSAL_LIMITADO_POR_HISTORIA_DE_FUENTE'
        result['decisions']=[dict(hypothesis='H-FASE-MODAL-LIBRE-DE-RESIDUO',decision='APOYO_DELIMITADO' if result['source']['supports_delimited_dispersive_explanation'] else 'INSUFICIENTE_DESCARTADA_COMO_EXPLICACION_MAYORITARIA',scope='Cambio sin ajuste de frecuencias radiales libres; no espectro ni propagador acoplado.'),
                             dict(hypothesis='ATRIBUCION_CAUSAL_M2',decision='ABIERTA_POR_EVIDENCIA_FALTANTE',scope=result['source']['missing_evidence'])]
    write(output/'resultados.json',result)
    print(json.dumps({k:result[k] for k in ['checkpoint','operation','status','physical_gate','new_M2_evolution_steps','decisions']},ensure_ascii=False),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    with threadpool_limits(limits=1):
        run(json.loads(args.config.read_text()),args.output_dir)
