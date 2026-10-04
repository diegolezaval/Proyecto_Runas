"""Descomposición de diferencias guardadas; no reitera evoluciones."""
from pathlib import Path
import argparse
import json
import numpy as np
from scipy.fft import dst
from scipy.interpolate import CubicSpline
from modelo_m2 import BENCHMARK as model

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'validacion/P06/no_radial'


def load(path):
    with np.load(path, allow_pickle=False) as saved:
        data = {k: saved[k].copy() for k in ['q', 'v', 'initial_q', 'initial_v', 'rows']}
        data['configuration'] = json.loads(str(saved['config']))
        data['time'] = float(saved['time'])
        data['labels'] = saved['labels'].copy()
    return data


def compare(left, right):
    c, f = load(left), load(right)
    if c['time'] != 160 or f['time'] != 160:
        raise ValueError('Tiempo final incorrecto')
    rc = (np.arange(c['q'].shape[1]) + .5) * c['configuration']['dx']
    rf = (np.arange(f['q'].shape[1]) + .5) * f['configuration']['dx']
    use = rf < 40
    rr = rf[use]
    weights = (np.diff((np.arange(len(rf)+1)*f['configuration']['dx'])**3)/3)[use]
    ac = CubicSpline(rc, c['q'], axis=1)(rr)
    bc = CubicSpline(rc, c['v'], axis=1)(rr)
    af, bf = f['q'][:, use], f['v'][:, use]
    pc, pf = ac[0] + 1j*ac[1], af[0] + 1j*af[1]
    phase = np.angle(np.sum(weights*np.conj(pf[:, 0])*pc[:, 0]))
    pc *= np.exp(-1j*phase)
    pvc = (bc[0]+1j*bc[1])*np.exp(-1j*phase)
    pvf = bf[0]+1j*bf[1]
    initial = f['initial_q'][:, use]
    iv = f['initial_v'][:, use]
    pi, pvi = initial[0]+1j*initial[1], iv[0]+1j*iv[1]
    phi_scale = np.sum(weights[:, None]*abs(pi[:, 1:])**2)
    phi_pscale = np.sum(weights[:, None]*(abs(pi[:, 1:])**2+abs(pvi[:, 1:])**2/model.mass2))
    chi_scale = np.sum(weights[:, None]*initial[2, :, 1:]**2)
    chi_pscale = np.sum(weights[:, None]*(initial[2, :, 1:]**2+iv[2, :, 1:]**2/model.mediator**2))
    phi_error = float(np.sqrt(np.sum(weights[:, None]*abs(pc[:, 1:]-pf[:, 1:])**2)/phi_scale))
    phi_phase_error = float(np.sqrt(np.sum(weights[:, None]*(abs(pc[:, 1:]-pf[:, 1:])**2+abs(pvc[:, 1:]-pvf[:, 1:])**2/model.mass2))/phi_pscale))
    dq = ac[2, :, 1:]-af[2, :, 1:]
    dv = (bc[2, :, 1:]-bf[2, :, 1:])/model.mediator
    chi_error = float(np.sqrt(np.sum(weights[:, None]*dq**2)/chi_scale))
    chi_phase_error = float(np.sqrt(np.sum(weights[:, None]*(dq**2+dv**2))/chi_pscale))
    total = np.sum(weights[:, None]*(dq**2+dv**2))
    bands = []
    for lower, upper in [(0, 2), (2, 5), (5, 10), (10, 20), (20, 40)]:
        sel = (rr >= lower) & (rr < upper)
        bands.append(dict(r_min=lower, r_max=upper, fraction_of_chi_squared_difference=float(np.sum(weights[sel, None]*(dq[sel]**2+dv[sel]**2))/total)))
    ell = f['labels'][1:, 0].astype(int)
    modes = {str(l): float(np.sum(weights[:, None]*(dq[:, ell == l]**2+dv[:, ell == l]**2))/total) for l in range(1, 5)}
    zc, zf = ac[2, :, 1:]+1j*bc[2, :, 1:]/model.mediator, af[2, :, 1:]+1j*bf[2, :, 1:]/model.mediator
    chi_phase = np.angle(np.sum(weights[:, None]*np.conj(zf)*zc))
    rotation_error = float(np.sqrt(np.sum(weights[:, None]*abs(zc*np.exp(-1j*chi_phase)-zf)**2)/chi_pscale))
    return dict(norm_relative_sup_error=float(np.max(abs(c['rows'][:, 5]-f['rows'][:, 5]))/np.max(f['rows'][:, 5])),
                final_complex_nonradial_field_error_over_initial_norm=phi_error,
                final_phi_phase_space_error_over_initial_norm=phi_phase_error,
                final_mediator_nonradial_error_over_initial_norm=chi_error,
                final_mediator_phase_space_error_over_initial_norm=chi_phase_error,
                global_phi_phase_removed=float(phase), chi_radial_bands=bands, chi_multipole_fractions=modes,
                descriptive_chi_rotation=dict(angle=float(chi_phase), rotated_error=rotation_error,
                    used_for_acceptance=False, warning='χ es real: esta rotación del espacio de fases es sólo un diagnóstico; no es una simetría que permita alinear la puerta.'))


def spectrum(data, initial=False):
    q, v = (data['initial_q'], data['initial_v']) if initial else (data['q'], data['v'])
    h = data['configuration']['dx']
    n = int(round(40/h))
    r = (np.arange(n)+.5)*h
    u = r[:, None]*q[2, :n, 1:]
    uv = r[:, None]*v[2, :n, 1:]/model.mediator
    amplitude = np.sum(dst(u, type=2, axis=0, norm='ortho')**2 + dst(uv, type=2, axis=0, norm='ortho')**2, axis=1)
    k = np.pi*np.arange(1, n+1)/40
    return dict(fractions_above_k={str(cut): float(amplitude[k > cut].sum()/amplitude.sum()) for cut in [2, 4, 8, 12, 20]},
                k_at_max=float(k[np.argmax(amplitude)]),
                interpretation='Transformada seno de rχ en el núcleo finito, sin diagonalizar el operador acoplado; localizador descriptivo, no espectro físico certificado.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    names = [f'dop853e9_L4_h{h:.3f}_dt0.0200_R220_eps0.020_T160_estado.npz' for h in [.5, .25, .125]]
    comparisons = [compare(OLD/names[0], OLD/names[1]), compare(OLD/names[1], OLD/names[2])]
    stored = json.loads((OLD/'resultados.json').read_text())
    for calculated, control in zip(comparisons, ['radial_mediador_grueso', 'radial_mediador_refinado']):
        reference = next(x for x in stored['comparisons'] if x['control'] == control)
        for key in ['norm_relative_sup_error', 'final_complex_nonradial_field_error_over_initial_norm', 'final_phi_phase_space_error_over_initial_norm', 'final_mediator_nonradial_error_over_initial_norm', 'final_mediator_phase_space_error_over_initial_norm']:
            if not np.isclose(calculated[key], reference[key], rtol=1e-11, atol=1e-13):
                raise ValueError('Diagnóstico no reproduce definición previa: '+key)
    spectra = {name: dict(initial=spectrum(load(OLD/name), True), final=spectrum(load(OLD/name))) for name in names}
    phases = []
    for k in [2, 4, 8, 12, 20]:
        frequency = lambda h: np.sqrt(model.mediator**2 + (2*np.sin(k*h/2)/h)**2)
        phases.append(dict(k=k, coarse_pair_phase_difference=float(160*(frequency(.25)-frequency(.125))),
                           fine_pair_phase_difference=float(160*(frequency(.125)-frequency(.0625)))))
    result = dict(checkpoint='CP10_MEDIADOR_ESPACIOTEMPORAL', comparisons=comparisons, spectra=spectra,
                  free_cartesian_dispersion_illustration=phases,
                  illustration_limit='ω_h²=M²+4 sin²(kh/2)/h² es la dispersión libre cartesiana; no reemplaza el operador radial/centrífugo ni demuestra la causa en M2 acoplado.',
                  historical_metric_reproduction_passed=True, evolutions_repeated=False,
                  cause_certified=False, continuum_error_certified=False,
                  next_test='Control temporal en h=.125 y comparación h=.125/.0625 con tolerancia común fina; no ajustar fase χ ni relajar el 2%.')
    (args.output_dir/'diagnostico.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
