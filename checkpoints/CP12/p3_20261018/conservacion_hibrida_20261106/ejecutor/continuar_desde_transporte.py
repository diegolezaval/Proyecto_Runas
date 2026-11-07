"""Un segmento P3 original; conservación previa, restauración exacta y bloqueo."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time
import traceback
import preservar as p
from capacidad_separada import preserve_capacity
from continuar import activate, metrics, restore, validate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('home','registro','helpers','auditor','salida'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--referencia-publica', type=Path, required=True)
    parser.add_argument('--solo-auditar',action='store_true');args=parser.parse_args()
    home,output,helpers,auditor=[getattr(args,n).resolve() for n in ('home','salida','helpers','auditor')]
    reg=p.read(args.registro);validate(reg,home,helpers,auditor)
    output.mkdir(parents=True,exist_ok=False)
    for n in ('runtime/tmp','runtime/pycache'):(home/n).mkdir(parents=True,exist_ok=True)
    with (args.registro.resolve().parent/'P3_WORKER.lock').open('a+') as global_lock,(home/'runtime/worker.lock').open('a+') as instance_lock:
        fcntl.flock(global_lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(instance_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        p.initialize_rotation(home,reg)
        controller,legacy,modules,streams,budget,dense,clock,next_record=restore(home,reg);tr=controller.tr
        p.write(output/'RESTAURACION_EXACTA.json',dict(passed=True,clock=clock,target=reg['target'],
            physical_metadata=[s.metadata() for s in streams],M2_steps_executed=0,DOP853_construction_or_step_attempts=0,CP12_closed=False))
        if args.solo_auditar:
            print(json.dumps(dict(passed=True,clock=clock,M2_steps_executed=0,DOP853_construction_or_step_attempts=0)));return 0
        p.write(home/'runtime/worker_started.json',dict(at=p.now(),registry_sha256=p.sha(args.registro),pid=os.getpid(),physical_steps_observed=False))
        admin=home/'administracion_continuacion_20261030'/reg['allocation_id'];admin.mkdir(parents=True,exist_ok=False)
        for name in reg['administrative_sources']:shutil.copyfile(Path(__file__).parent/name,admin/name)
        shutil.copyfile(args.registro,admin/'REGISTRO.json')
        preserve_capacity(home, output / 'control', reg, args.registro,
                          args.referencia_publica.resolve(), helpers, auditor)
        capacity_sha=p.sha(output/'control/ACEPTACION_COMBINADA.json');activation=output/'ACTIVACION.json'
        print(json.dumps(dict(stage='ACTIVACION_REGISTRADA_REQUERIDA',registry_sha256=p.sha(args.registro),capacity_acceptance_sha256=capacity_sha,activation_file=str(activation))),flush=True)
        deadline=time.monotonic()+3600
        while not activation.exists():
            if time.monotonic()>deadline:raise TimeoutError('Sin activación; cero pasos nuevos')
            time.sleep(.5)
        activate(activation,p.sha(args.registro),capacity_sha)
        controller,legacy,modules,streams,budget,dense,clock,next_record=restore(home,reg)
        target=reg['target'];before=[s.accepted for s in streams];done=threading.Event();progress=dict(clock=clock,phase='evolution')
        def heartbeat():
            while not done.wait(30):tr.write(output/'HEARTBEAT.json',dict(at=p.now(),**progress,physical_streams=[s.metadata() for s in streams],not_a_restart_certificate=True))
        threading.Thread(target=heartbeat,daemon=True).start()
        try:
            if dense is None:dense=[s.advance(target) for s in streams]
            while clock<target-1e-12:
                clock,next_record,dense,recorded=controller.interval(modules,streams,budget,dense,clock,next_record,target);progress['clock']=clock
                if not (output/'INICIO_FISICO.json').exists() and any(s.accepted>b for s,b in zip(streams,before)):
                    p.write(output/'INICIO_FISICO.json',dict(at=p.now(),clock=clock,accepted_steps_since_restore=[s.accepted-b for s,b in zip(streams,before)],replay96_to112_executed=False,CP12_closed=False))
                if recorded and clock<target-1e-12:
                    tr.save(home/'transport/current.npz',tr.capture(home,streams,budget,dense,clock,next_record,target))
                    checked=controller.audit_transport(home,legacy);tr.write(home/'proofs'/('auditoria_forward_%06d.json'%round(clock*10)),checked)
                    if round(clock/.4)%4==0:
                        progress['phase']='conservation'
                        saved=p.preserve(home,output/('transporte_%06d'%round(clock*10)),
                            'TRANSPORTE_%06d_'%round(clock*10)+reg['allocation_id'].upper(),'transport',clock,reg['closed_boundary'],helpers,auditor)
                        tr.write(home/'proofs'/('forward_%06d_permanent.json'%round(clock*10)),saved);progress['phase']='evolution'
            for s in streams:s.close_segment()
            check=modules['native'].reference(streams[1].sim,(streams[0].sim,streams[1].sim,streams[0].q,streams[1].q))
            budget.algebra.append(dict(time=clock,**check));legacy.save_state(home,streams,budget)
            progress['phase']='frontier_conservation'
            frontier=output/('frontera_%04d'%target)
            saved=p.preserve(home,frontier,'FRONTERA_%04d_'%target+reg['allocation_id'].upper(),'boundary',clock,target,helpers,auditor)
            decision=metrics(saved,frontier,target)
            positive=decision['prefix_pair_limits_met'] and decision['prefix_physical_controls_met']
            result=dict(passed=positive,time=target,comparison=decision['comparison'],all_original_prefix_gates_passed=positive,
                physical_metadata=[s.metadata() for s in streams],public_capsule_asset=saved['github']['github_asset_id'],
                CP12_closed=False,correction_validated=False,next_physical_interval_executed=False)
            p.write(output/'RESULTADO.json',result)
            if not positive:
                negative=home/'negative'/('PUERTA_FORWARD_%04d'%target);negative.mkdir()
                shutil.copyfile(frontier/'metricas/RESULTADO.json',negative/'METRICAS_ORIGINALES.json')
                progress['phase']='negative_preservation'
                p.preserve(home,output/'negativo','NEGATIVO_%04d_'%target+reg['allocation_id'].upper(),'negative',clock,target,helpers,auditor)
                p.write(output/'SUSPENSION.json',dict(time=target,scientific_gate_failed=True,automatic_new_candidate_authorized=False,CP12_closed=False))
                return 2
            p.retire_at_boundary(home,saved,decision,helpers)
            print(json.dumps(dict(stage='FRONTERA_POSITIVA_RECUPERADA',time=target,next_interval_executed=False)),flush=True);return 0
        except BaseException as error:
            failed=home/'negative'/('INCIDENTE_'+reg['allocation_id']);failed.mkdir()
            arrays={f'grid_{i}_{k}':getattr(s,k) for i,s in enumerate(streams) for k in ('q','v','initial_q','initial_v')}
            for family in ('raw','coupled'):
                for i,o in enumerate(getattr(budget,family)):arrays[f'{family}_{i}_q']=o.q;arrays[f'{family}_{i}_v']=o.v
            modules['np'].savez_compressed(failed/'ESTADO_NO_CERTIFICADO.npz',**arrays)
            p.write(failed/'FALLO.json',dict(error_type=type(error).__name__,traceback=traceback.format_exc(),phase=progress['phase'],clock=clock,
                physical_metadata=[s.metadata() for s in streams],classification='REQUIRES_REVIEW_NO_AUTOMATIC_REPLAY',CP12_closed=False))
            pending=[]
            for request in output.rglob('SOLICITUD.json'):
                if (request.parent/'transito/RESULTADO_TRANSITO.json').exists() and not (request.parent/'ACEPTACION_COMBINADA.json').exists():
                    pending.append(str(request))
            if pending:
                p.write(output/'REQUIERE_RECONCILIACION.json',dict(pending_requests=pending,
                    automatic_publication_retry_permitted=False,next_physical_interval_executed=False,CP12_closed=False))
            else:
                p.preserve(home,output/'fallo_conservado','FALLO_'+reg['allocation_id'].upper(),'negative',clock,reg['closed_boundary'],helpers,auditor)
            raise
        finally:done.set()


if __name__=='__main__':raise SystemExit(main())
