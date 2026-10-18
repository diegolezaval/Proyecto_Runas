"""New discriminants on conserved tau80 data; no integration is authorized."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import sys
from fractions import Fraction

os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import DOP853
from scipy.integrate._ivp.base import OdeSolver
from numpy.polynomial import Polynomial as Poly

BLOCKED = []
def forbidden(*args, **kwargs):
    BLOCKED.append('integration_attempt')
    raise RuntimeError('No DOP853 construction or step authorized in passive diagnosis')
DOP853.__init__ = DOP853._step_impl = OdeSolver.step = forbidden


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def run(home, output):
    assert not output.exists()
    state = home / 'outputs/MIXTO_par_estado.npz'
    assert sha(state) == 'abfae6d6b88a1f5b6a58df1657ea3f860a81b02835fe6598b97315da3c1f3ba4'
    sources = json.loads((home / 'preregistration/identidad_cientifica_original.json').read_text())
    captured = json.loads((home / 'preregistration/nueva_identidad.json').read_text())['captured_sources']
    watched = {str(home / 'science' / p): h for p, h in {**sources['code_hashes'], **sources['input_hashes']}.items()}
    watched.update({str(home / p): h for p, h in captured.items()})
    watched.update({str(state): sha(state), str(home / 'outputs/procedencia.json'): sha(home / 'outputs/procedencia.json')})
    assert all(sha(Path(p)) == h for p, h in watched.items())
    sys.path.insert(0, str(home / 'science/herramientas'))
    sys.path.insert(0, str(home / 'candidate'))
    from continuar_no_radial_m2 import Evolution, harmonics, SOURCE
    from mixed_backend import Mixed
    from observador_causal_CP12 import nonlinear
    from modelo_m2 import BENCHMARK as model
    with np.load(state, allow_pickle=False) as data:
        saved = {k: data[k].copy() for k in data.files}
    assert float(saved['time']) == 80
    n = int(saved['coarse_n'])
    sc, sf = [Mixed(h, 220., 4) for h in (.125, .0625)]
    qc, qf = saved['q'][:, :n], saved['q'][:, n:]
    vc, vf = saved['v'][:, :n], saved['v'][:, n:]
    qi, vi = [CubicSpline(sc.r, a, axis=1)(sf.r) for a in (qc, vc)]
    initial = saved['initial_q'][2, n:]
    initial_v = saved['initial_v'][2, n:]
    mask = sf.r < 40
    weight = sf.w[mask, None]
    def inner(a, b, c, d):
        return float(np.sum(weight * (a[mask, 1:] * c[mask, 1:] + b[mask, 1:] * d[mask, 1:] / model.mediator**2)))
    scale = inner(initial, initial_v, initial, initial_v)
    dq, dv = qi[2] - qf[2], vi[2] - vf[2]
    actual = inner(dq, dv, dq, dv)
    S = saved['coupled_angular_basis']
    cq, cv = [saved['coupled_0_' + key][:, 2] @ S.T for key in ('q', 'v')]
    rq, rv = [saved['raw_0_' + key][:, 0] for key in ('q', 'v')]
    vectors_q = np.concatenate([dq[None], rq, cq])
    vectors_v = np.concatenate([dv[None], rv, cv])
    gram = [[inner(a, b, c, d) for c, d in zip(vectors_q, vectors_v)] for a, b in zip(vectors_q, vectors_v)]
    deltaq, deltav = cq[2] - rq[1], cv[2] - rv[1]
    coupling = dict(raw_norm=np.sqrt(inner(rq[1], rv[1], rq[1], rv[1]) / scale),
        coupled_norm=np.sqrt(inner(cq[2], cv[2], cq[2], cv[2]) / scale),
        coupled_minus_raw_norm=np.sqrt(inner(deltaq, deltav, deltaq, deltav) / scale),
        coupled_minus_raw_signed_projection=inner(deltaq, deltav, dq, dv) / actual,
        raw_delta_cross_over_observed_squared=2*inner(rq[1], rv[1], deltaq, deltav)/actual,
        scope='Same saved operator-chi forcing, two registered propagators; conditional Jacobian effect, no pure return-loop fraction')
    bands = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 40), (40, 220)]
    def distribution(q, v=None):
        power = q*q if v is None else q*q + v*v/model.mediator**2
        radial = np.sum(power[:, 1:], axis=1)*sf.w
        total = float(radial.sum())
        return dict(squared_norm=total, bands=[dict(r_min=a, r_max=b, fraction=float(radial[(sf.r>=a)&(sf.r<b)].sum()/max(total,1e-300))) for a,b in bands],
            multipoles={str(ell): float(np.sum(sf.w[:,None]*power[:,sf.ell==ell])/max(total,1e-300)) for ell in range(1,5)})
    comm = CubicSpline(sc.r, sc.lap(qc), axis=1)(sf.r) - sf.lap(qi)
    transfer = CubicSpline(sc.r, nonlinear(sc, qc@sc.Y), axis=1)(sf.r) - nonlinear(sf, qi@sf.Y)
    spatial = {'observed_difference': distribution(dq,dv), 'operator_chi_coupled_response': distribution(cq[2],cv[2]),
        'operator_chi_raw_response': distribution(rq[1],rv[1]), 'instantaneous_chi_commutator': distribution(comm[2]),
        'instantaneous_chi_nonlinear_transfer': distribution(transfer[2])}
    parity = (-1.)**sc.ell
    parity_arrays = [CubicSpline(np.r_[-sc.r[::-1],sc.r],np.concatenate([a[::-1]*parity,a]),axis=0)(sf.r) for a in (qc[2],vc[2])]
    parity_error = np.sqrt(inner(parity_arrays[0]-qf[2],parity_arrays[1]-vf[2],parity_arrays[0]-qf[2],parity_arrays[1]-vf[2])/scale)
    reverse = [CubicSpline(sf.r,a,axis=0)(sc.r) for a in (qf[2],vf[2],initial,initial_v)]
    use = sc.r<40
    norm_c = lambda a,b: float(np.sum(sc.w[use,None]*(a[use,1:]**2+b[use,1:]**2/model.mediator**2)))
    metrics = dict(original=np.sqrt(actual/scale),parity=parity_error,
        reverse_fine_to_coarse=np.sqrt(norm_c(qc[2]-reverse[0],vc[2]-reverse[1])/norm_c(reverse[2],reverse[3])),used_for_acceptance=False)
    timeline = []
    for row in json.loads(str(saved['budget_rows'])):
        op = next(m for m in row['coupled'] if m['name']=='operador_chi')
        timeline.append(dict(time=row['time'],observed_error=row['observed_relative_error'],operator_chi=op,
            all_channels={family:row[family] for family in ('raw','coupled')},
            short_observed_fractions={label:row['short_modes'][label]['observed_error_fraction_above_k'] for label in ('core','smooth')},
            verification=row['verification']))
    assert len(timeline)==201 and timeline[-1]['time']==80
    preparation = {}
    with np.load(SOURCE,allow_pickle=False) as data:
        config=json.loads(str(data['config']));sr=(np.arange(config['n'])+.5)*config['dx']
        for label,key in [('chi','chi'),('vchi','vchi')]:
            arr=data[key];spline=CubicSpline(np.r_[-sr[::-1],sr],np.r_[arr[::-1],arr])
            knots=spline.x[1:-1];jumps=6*np.diff(spline.c[0]);selected=(knots>0)&(knots<40)
            r=knots[selected];delta=jumps[selected]
            quadrupole_second_jump=-.02*r*np.exp(-(r/20)**4)*delta
            preparation[label]=dict(source_third_derivative_jump_max=float(np.max(abs(delta))),
                quadrupole_second_derivative_jump_max=float(np.max(abs(quadrupole_second_jump))),
                largest_jump_radius=float(r[np.argmax(abs(quadrupole_second_jump))]),
                radial_band_jump_squared={str((a,b)):float(np.sum(quadrupole_second_jump[(r>=a)&(r<b)]**2)) for a,b in bands},
                exact_regularity='CubicSpline background C2; derivative-based quadrupole C1 wherever third derivative jumps; centre even extension retained')
    angular = []
    labels,Y,wa=harmonics(12);ells=np.array([label[0] for label in labels]);YW=(Y*wa).T
    for clock,states in [(0,(saved['initial_q'][:,:n],saved['initial_q'][:,n:])),(80,(qc,qf))]:
        for sim,q in zip((sc,sf),states):
            use=sim.r<40;x,y,z=q[:,use]@Y[:25];rho=x*x+y*y
            f=2*model.quartic*rho+model.trilinear*z+.5*model.mixed*z*z
            values=np.array([-f*x,-f*y,-(model.trilinear+model.mixed*z)*rho])@YW
            powers=np.sum(sim.w[use][None,:,None]*values*values,axis=1)
            angular.append(dict(time=clock,h=sim.dx,by_field_and_ell=[{str(l):float(p[ells==l].sum()) for l in range(13)} for p in powers],
                omitted_squared_fraction_by_field=[float(p[ells>4].sum()/max(p.sum(),1e-300)) for p in powers],
                scope='Instantaneous nonlinear-source leakage only; no evolved L comparison'))
    manufactured=[]
    for ell in range(5):
        a=2*ell+2;c=(a+1)*(Fraction(-a,24)+Fraction(1,12*(a-1)))
        b2=Fraction(a*(a-1),8)+c-Fraction(1,12)-Fraction(a*(a-2),12)
        b1=Fraction(a*(a-1)*(a-2),24)+c*(a-2)-Fraction(a,12)-Fraction(a*(2-a),12)
        assert b2==Fraction(1,6*(a-1)) and b1==-b2
        for shape,g in [('centre',Poly([0,0,-1/64])),('shell',-(Poly([-225,0,1])/60)**2)]:
            p=(Poly([1,0,-1/1600]))**6;polys=[p]
            for order in range(4):polys.append(polys[-1].deriv()+polys[-1]*g.deriv())
            for h in (.25,.125,.0625,.03125,.015625):
                sim=Mixed(h,40.,4);r=sim.r;u,u1,u2=[p(r)*np.exp(g(r)) for p in polys[:3]]
                q=r**ell*u;exact=r**ell*(u2+a/r*u1)
                leading=r**ell*float(b2)*(u2/r**2-u1/r**3)
                index=int(np.flatnonzero(sim.ell==ell)[0]);field=np.zeros((3,sim.n,sim.nm));field[2,:,index]=q
                result=sim.lap(field)[2,:,index];inside=r<32
                norm=lambda x:float(np.sqrt(np.dot(sim.w[inside],x[inside]**2)))
                manufactured.append(dict(ell=ell,shape=shape,h=h,error_over_field_norm=norm(result-exact)/norm(q),
                    after_subtracting_derived_h2=norm(result-exact-h*h*leading)/norm(q),
                    first_cell_error=float(result[0]-exact[0]),outer_band_error_norm=float(np.sqrt(np.sum(sim.w[~inside]*(result-exact)[~inside]**2)))))
    assert not BLOCKED and all(sha(Path(p))==h for p,h in watched.items())
    output.mkdir(parents=True)
    result=dict(schema='CP12_TAU80_NEW_PASSIVE_DISCRIMINANTS',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        input_state_sha256=sha(state),source_hashes=watched,source_hashes_unchanged=True,new_M2_steps=0,DOP853_attempts=len(BLOCKED),
        source_code_sha256=sha(Path(__file__)),core_full_Gram=gram,Gram_order=['observed']+['raw:'+str(i) for i in range(5)]+['coupled:'+str(i) for i in range(5)],
        initial_chi_phase_squared_scale=scale,coupling_contrast=coupling,spatial_distributions=spatial,metric_sensitivity=metrics,
        timeline=timeline,preparation=preparation,angular_source_leakage=angular,manufactured_geometry=manufactured,
        limitations=['No new M2 or observer propagation','Instantaneous force/modal leakage is not propagated causality',
                    'No angular or box trajectory convergence proven','No altered acceptance metric or phase fitting'],CP12_closed=False)
    dump(output/'RESULTADO.json',result)
    print(json.dumps({k:result[k] for k in ['new_M2_steps','DOP853_attempts','metric_sensitivity','coupling_contrast','preparation']},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--home',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.home.resolve(),args.output.resolve())
