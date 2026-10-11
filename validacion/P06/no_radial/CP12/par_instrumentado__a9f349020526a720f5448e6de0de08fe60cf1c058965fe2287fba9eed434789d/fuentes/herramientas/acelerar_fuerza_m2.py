"""Optional fused C potential; the numerical action and projection are unchanged."""
from pathlib import Path
import ctypes,subprocess,hashlib,json,time
import numpy as np
from modelo_m2 import BENCHMARK as m
from continuar_no_radial_m2 import Evolution,OUT,save_json
SOURCE=Path(__file__).with_name('fuerza_potencial_m2.c')


def install(sim):
    cache=OUT/'cache';cache.mkdir(exist_ok=True)
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    target=cache/f'force_{digest[:16]}.so'
    if not target.exists():
        subprocess.run(['cc','-O3','-fPIC','-shared','-fno-fast-math',str(SOURCE),'-o',str(target)],check=True,capture_output=True)
    lib=ctypes.CDLL(str(target));f=lib.m2_potential_force
    ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
    f.argtypes=[ctypes.c_size_t,ptr,ptr]+[ctypes.c_double]*5;f.restype=None
    def force(q):
        values=np.ascontiguousarray(q@sim.Y);out=np.empty_like(values)
        f(values.shape[1]*values.shape[2],values,out,m.mass2,m.quartic,m.mediator**2,m.trilinear,m.mixed)
        return sim.lap(q)+out@sim.YW
    sim.force=force
    return dict(method='numpy_projection_fused_C_potential',source_sha256=digest,fast_math=False,action_changed=False)


if __name__=='__main__':
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        sim=Evolution(.125,220.,4);standard=sim.force
        sp=OUT/'dop853e9_L4_h0.125_dt0.0200_R220_eps0.020_T160_estado.npz'
        with np.load(sp) as d:q=d['q'].copy();restart_time=float(d['time'])
        ref=standard(q);start=time.perf_counter()
        for _ in range(24):standard(q)
        slow=(time.perf_counter()-start)/24
        meta=install(sim);test=sim.force(q);start=time.perf_counter()
        for _ in range(24):sim.force(q)
        fast=(time.perf_counter()-start)/24
        rng=np.random.default_rng(280920268);errors=[float(np.max(abs(ref-test))/max(1,float(np.max(abs(ref)))))]
        for _ in range(4):
            trial=q+rng.normal(size=q.shape)*.00001;a=standard(trial);b=sim.force(trial)
            errors.append(float(np.max(abs(a-b))/max(1,float(np.max(abs(a))))))
        rec=dict(**meta,comparison_relative_errors=errors,numpy_force_seconds=slow,fused_force_seconds=fast,
            speedup=slow/fast,read_only_restart_time=restart_time,passed=max(errors)<2e-12,
            scope='Implementation equivalence only; no evolution repeated and no new physical approximation')
        save_json(OUT/'auditoria_fuerza_fusionada.json',rec);print(json.dumps(rec,indent=2));assert rec['passed']
