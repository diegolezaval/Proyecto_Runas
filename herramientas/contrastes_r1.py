"""Consecuencias cuantitativas, sin completar coeficientes físicos desconocidos.
Los contrastes de grafo, SI y Landauer declaran sus hipótesis por separado.
"""
import json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from m2_comun import ROOT,RATIO,M,G,H,THETA,up,upp

def main():
    d=json.loads((ROOT/'validacion/cierre_m2.json').read_text())
    kb=1.380649e-23;hp=6.62607015e-34;hbar=hp/(2*np.pi);ev=1.602176634e-19;c=299792458.
    geo=d['geometry']['P-04'];Lu=geo['segments'][1]['length_graphic_units']*.01;L=geo['R1_planar_length_m']
    desired_loss=1-np.exp(-1e-4*L)
    reflect=lambda x:np.sin(x)**2/(1+3*np.cos(x)**2)
    halfwidth=brentq(lambda x:reflect(x)-desired_loss,0,.1)*1e7/(2*np.pi*Lu)
    # Dimensionless G with a gap x0=Egap/kBT. The stable integrand avoids overflow.
    T=300.;gap=ev/(kb*T)
    integrand=lambda x:x*x*np.exp(-x)/(1-np.exp(-x))**2
    thermal_integral=quad(integrand,gap,np.inf,epsabs=1e-27,epsrel=1e-10)[0]
    gq=np.pi**2*kb*kb*T/(3*hp);g_gap=kb*kb*T/hp*thermal_integral
    fine=d['field_convergence'][-1];s_center=fine['f0']**2
    dz=lambda s:2*s*(G*M*M/(M*M+H*s)**2)**2
    amplitude_limit=brentq(lambda s:dz(s)-.01,.01,1)
    # One specified slow amplitude direction, at the homogeneous zero-pressure state.
    s0=d['homogeneous']['zero_pressure']['s'];z0=-G*s0/(M*M+H*s0);f0=np.sqrt(s0);w2=up(s0)
    u0=np.sqrt(2)*f0;C=np.sqrt(2)*f0*(G+H*z0)
    jac=np.array([[4*RATIO*s0,C],[C,M*M+H*s0]])
    eig,vec=np.linalg.eigh(jac);v=vec[:,0];v*=1 if v[0]>0 else -1
    def force(y):
        u,z=y;s=.5*u*u
        return np.array([(1+2*RATIO*s+G*z+.5*H*z*z-w2)*u,M*M*z+G*s+H*z*s])
    y0=np.array([u0,z0]);force0=force(y0)
    def err(eps):
        perturb=eps*u0*v;linear=jac@perturb
        return np.linalg.norm(force(y0+perturb)-force0-linear)/np.linalg.norm(linear)
    eps_limit=brentq(lambda e:err(e)-.01,1e-6,.1)
    # Scalar illustrative SI scale, kept separate from the old M1 density matching.
    lam=THETA['SI_illustration']['lambda'];mass_eV=THETA['SI_illustration']['m_energy_eV']
    mass_energy=mass_eV*ev;scale_energy=mass_energy/lam;scale_density=mass_energy**4/(lam*(hbar*c)**3)
    report={
      'schema_version':'4.0.0','complete_device_derived':False,
      'P04':{'length_main_m_planar':L,'stub_length_m_planar':Lu,'R1_bulk_loss_fraction':desired_loss,
             'matched_neumann_stub':{'center_T':1.0,'half_band_Hz_at_R1_speed_and_zero_bulk_loss':halfwidth,
                 'reflection_at_plus_minus_500kHz':reflect(2*np.pi*500000*Lu/1e7),
                 'group_delay_s_at_R1_speed':(L+Lu/2)/1e7,'bare_main_delay_s_at_R1_speed':L/1e7},
             'scope':'Grafo ideal, v impuesto, extremo U perfectamente reflectante y sin absorcion; no derivacion M2 de paredes ni velocidad.'},
      'P11':{'phase_encoding_barrier_J_exact_U1':0.,'R1_requested_barrier_J':60*kb*T,
             'R1_requested_barrier_eV':60*kb*T/ev,'R1_arrhenius_lifetime_s_if_postulated':1e-12*np.exp(60),
             'landauer_reset_lower_bound_J_at_300K':kb*T*np.log(2),
             'density_kernel_quartic_sign_change_k_over_m':M/np.sqrt(RATIO),
             'scope':'Barrera nula solo para codificacion en fase de una orbita U(1) aislada; no excluye memoria alimentada o con otras variables.'},
      'P18':{'T_K':T,'gapless_conductance_quantum_W_K':gq,'minimum_gapless_channels_for_100_W_K':100/gq,
             'vacuum_gap_example_eV':1.,'gap_over_kBT':gap,'one_gapped_ballistic_channel_W_K':g_gap,
             'minimum_gapped_channels_for_100_W_K':100/g_gap,
             'scope':'Transporte pasivo lineal entre dos banos ideales, transmision <=1 por canal; no cota universal de una bomba activa ni de todo material.'},
      'P01':{'energy_only_minimum_seconds':5/(2-.05),'energy_plus_assumed_settle_seconds':5/(2-.05)+.25,
             'exact_zero_classical_field_remains_zero':True,'net_charge_created_by_U1_invariant_closed_drive':0.,
             'scope':'Cota energetica condicionada a potencia realmente transferida. No es un protocolo de preparacion.'},
      'validity':{'sextic_term_relative_error_1pct_max_s':100/99,
             'no_induced_kinetic_term_1pct_max_s_near_vacuum':amplitude_limit,
             'induced_kinetic_correction_at_Qball_center':dz(s_center),
             'adiabatic_linear_response_sufficient_1pct_condition':'Omega^2+k^2 <= 0.01*(M^2+h*s)',
             'local_slow_direction_force_linearization_1pct_epsilon':eps_limit,
             'local_test_background_s':s0,'local_test_definition':'delta( sqrt(2)f,z ) = epsilon*sqrt(2)*f0*v_min; un unico sentido, no cota universal.',
             'physical_EFT_cutoff_identified':False,'universal_long_time_error_bound_identified':False},
      'scalar_SI_example':{'m_energy_eV':mass_eV,'lambda':lam,'length_unit_m':hbar*c/mass_energy,'time_unit_s':hbar/mass_energy,
             'field_energy_unit_eV':mass_eV/np.sqrt(lam),'energy_unit_J':scale_energy,'density_unit_J_m3':scale_density,
             'lambda0':RATIO*lam,'M_energy_eV':M*mass_eV,'g_energy_eV':G*mass_eV*np.sqrt(lam),'h':H*lam,
             'Qball_E_J':fine['Ehat']*scale_energy,'Qball_Q':fine['Qhat']/lam,
             'zero_pressure_density_J_m3':d['homogeneous']['zero_pressure']['rho']*scale_density,
             'scope':'Una unica escala ilustrativa: m=1 eV, lambda=0.001. No identifica portales ni alcanza R1. No se mezcla con el ajuste de densidad M1.'}
    }
    report['passed']=bool(0<halfwidth and reflect(2*np.pi*500000*Lu/1e7)<desired_loss and 0<g_gap<gq and eps_limit>0)
    (ROOT/'validacion/contrastes_r1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
