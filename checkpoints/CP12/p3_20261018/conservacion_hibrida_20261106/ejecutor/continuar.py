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


def validate(reg,home,helpers,auditor):
    p.validate_hybrid_registry(reg)
    if sys.flags.optimize or os.environ.get('OPENBLAS_CORETYPE'):raise ValueError('Comprobaciones deshabilitadas o arquitectura forzada')
    if reg.get('schema')!='CP12_P3_FORWARD_SEGMENT_V2' or reg.get('registered_before_M2') is not True or reg.get('replay96_to112_authorized') is not False:raise ValueError('Registro inválido o repetición consumida')
    if reg['kind'] not in ('transport','boundary'):raise ValueError('Origen no reanudable')
    if reg['target']!=reg['closed_boundary']+8 or reg['target']>=160:raise ValueError('Sólo la siguiente frontera; lectura final160 requiere registro propio')
    if not reg['closed_boundary']<=reg['clock']<reg['target'] or reg['clock']<11.2:raise ValueError('No retroceder el estado vigente')
    if p.sha(home/'outputs/MIXTO_par_estado.npz')!=reg['closed_state_sha256'] or p.sha(home/'outputs/procedencia.json')!=reg['receipt_sha256'] or p.sha(home/'configuration.json')!=reg['configuration_sha256']:raise ValueError('Estado, recibo o configuración distintos')
    if reg['kind']=='transport' and p.sha(home/'transport/current.npz')!=reg['transport_sha256']:raise ValueError('Transporte distinto')
    for name,h in reg['administrative_sources'].items():
        if p.sha(Path(__file__).parent/name)!=h:raise ValueError('Adaptador cambiado: '+name)
    for name,h in reg['helper_sha256'].items():
        if p.sha(helpers/name)!=h:raise ValueError('Ayudante cambiado: '+name)
    if p.sha(auditor)!=reg['original_auditor_sha256']:raise ValueError('Auditor original cambiado')


def restore(home,reg):
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
        TMPDIR=str(home/'runtime/tmp'),PYTHONPYCACHEPREFIX=str(home/'runtime/pycache'))
    sys.pycache_prefix=str(home/'runtime/pycache');sys.path.insert(0,str(home))
    import controlador_transporte as controller
    legacy=controller.legacy_module(home);tr=controller.tr
    with legacy.zero_m2_audit() as attempts:
        if reg['kind']=='transport':
            modules,streams,budget,dense,payload=tr.restore(home,legacy,home/'transport/current.npz')
            tr.assert_equal(payload,tr.capture(home,streams,budget,dense,payload['observer_clock'],payload['next_record'],payload['target']))
            if payload['observer_clock']!=reg['clock'] or payload['target']!=reg['target'] or not all(s.solver.t_bound==reg['target'] for s in streams):raise ValueError('Relojes o límite interno distintos')
            clock,next_record=payload['observer_clock'],payload['next_record']
        else:
            modules,streams,budget=legacy.streams_and_budget(home);dense=None
            clock=streams[0].t;next_record=round(clock/.4+1)*.4
            if clock!=reg['clock'] or not all(s.solver is None and s.t==clock for s in streams):raise ValueError('No es una frontera cerrada')
        if attempts:raise ValueError('Construcción o paso durante restauración')
    return controller,legacy,modules,streams,budget,dense,clock,next_record


def activate(path,registration_sha,capacity_sha):
    value=p.read(path)
    if value.get('schema')!='CP12_P3_FORWARD_ACTIVATION_V2' or value.get('registry_sha256')!=registration_sha or value.get('capacity_acceptance_sha256')!=capacity_sha or value.get('single_worker_reserved') is not True or not value.get('registered_commit'):raise ValueError('Activación sin reserva, capacidad o registro coincidente')


def metrics(saved,output,target):
    recovered=saved['github']['recovery'];home=Path(recovered['recovered_home']);a=recovered['original_audits']['boundary']
    proof=dict(schema='CP12_P3_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED',passed=True,time=target,
        all_payload_hashes_verified=True,independent_extracted_audit=a,state_sha256=a['state_sha256'],
        configuration_sha256=a['configuration_sha256'],receipt_sha256=a['receipt_sha256'])
    p.write(output/'CERTIFICADO_FRONTERA.json',proof)
    script=home/'preregistration/administration/leer_metricas_prefijo.py'
    registration=home/'preregistration/administration/REGISTRO_LECTURA_PREFIJOS_CONTINUACION_20261016.json'
    raw=p.logged([sys.executable,str(script),'--home',str(home),'--certificate',str(output/'CERTIFICADO_FRONTERA.json'),
        '--registration',str(registration),'--output',str(output/'metricas')],output/'lector_original')
    result=json.loads(raw)
    if result['M2_steps_executed']!=0 or not result['physical_state_and_receipt_unchanged']:raise ValueError('Lectura no conservadora')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('home','registro','helpers','auditor','salida'):parser.add_argument('--'+name,type=Path,required=True)
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
        label='CONTROL_'+reg['allocation_id'].upper()
        p.preserve(home,output/'control',label,reg['kind'],reg['clock'],reg['closed_boundary'],helpers,auditor,capacity=True)
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
