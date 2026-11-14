"""Repeat only the registered P3 segment (30, 32] from its exact saved state."""

import argparse
import fcntl
import json
from pathlib import Path
import shutil
import sys
import time
import traceback

from base_preservar import now, prepare, native, read, sha, write, logged
from continuar import restore, validate
from preservar import validate_native


def persist(home, output, label, kind, clock, boundary, helpers, auditor, *, capacity=False):
    request = prepare(home, output, label, kind, clock, boundary, capacity=capacity)
    receipt = native(request, output / 'transito', helpers, auditor)
    if kind == 'transport':
        validate_native(receipt, clock)
    write(output / 'RECUPERACION_INDEPENDIENTE.json', receipt)
    return receipt


def measure(receipt, output, target):
    recovery = receipt['recovery']
    audit = recovery['original_audits']['boundary']
    if not (recovery['exact_manifest_coverage'] and recovery['all_payload_hashes_verified_before_and_after']):
        raise ValueError('Cápsula incompleta')
    home = Path(recovery['recovered_home'])
    certificate = output / 'CERTIFICADO_FRONTERA.json'
    write(certificate, dict(
        schema='CP12_P3_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED',
        passed=True, time=target, independent_extracted_audit=audit,
        all_payload_hashes_verified=True, state_sha256=audit['state_sha256'],
        receipt_sha256=audit['receipt_sha256'], configuration_sha256=audit['configuration_sha256'],
        recovery_medium='Biblioteca', scientific_branch_advanced=False,
    ))
    folder = home / 'preregistration/administration'
    command = [
        sys.executable, str(folder / 'leer_metricas_prefijo.py'),
        '--home', str(home), '--certificate', str(certificate),
        '--registration', str(folder / 'REGISTRO_LECTURA_PREFIJOS_CONTINUACION_20261016.json'),
        '--output', str(output / 'metricas'),
    ]
    return json.loads(logged(command, output / 'lector_original'))


def repeat(args, reg):
    home, output, helpers, auditor = args.home, args.salida, args.helpers, args.auditor
    controller, legacy, modules, streams, budget, dense, clock, next_record = restore(home, reg)
    initial_clock = clock
    initial_steps = [s.accepted for s in streams]
    target = reg['target']
    label = reg['allocation_id'].upper()
    provenance = home / 'administracion_continuacion_20261030' / reg['allocation_id']
    provenance.mkdir(exist_ok=False)
    shutil.copyfile(args.registro, provenance / 'REGISTRO.json')
    shutil.copyfile(Path(__file__), provenance / Path(__file__).name)
    for name in reg['administrative_sources']:
        shutil.copyfile(args.adaptadores / name, provenance / name)
    control = persist(home, output / 'control_nativo', 'CONTROL_NATIVO_' + label, 'transport',
                      clock, reg['closed_boundary'], helpers, auditor, capacity=True)
    if control['recovery']['original_audits']['transport']['state_sha256'] != reg['transport_sha256']:
        raise ValueError('La prueba recuperó otro estado interno')
    write(output / 'CAPACIDAD_NATIVA.json', dict(
        allocation=reg['allocation_id'], registry_sha256=sha(args.registro),
        library_file_id=control['library_file_id'], archive_sha256=control['sha256'],
        bytes=control['bytes'], passed=True,
    ))
    write(output / 'INICIO.json', dict(
        at=now(), start=clock, target=target, allocation=reg['allocation_id'],
        registry_sha256=sha(args.registro), physical_metadata=[s.metadata() for s in streams],
    ))
    started = time.monotonic()
    phase = 'evolution'
    try:
        while clock < target - 1e-12:
            clock, next_record, dense, recorded = controller.interval(
                modules, streams, budget, dense, clock, next_record, target)
            if not (output / 'PRIMER_PASO.json').exists() and any(
                    s.accepted > n for s, n in zip(streams, initial_steps)):
                write(output / 'PRIMER_PASO.json', dict(
                    at=now(), clock=clock,
                    new_accepted_steps=[s.accepted - n for s, n in zip(streams, initial_steps)],
                ))
            if recorded and clock < target - 1e-12:
                phase = 'transport'
                tr = controller.tr
                tr.save(home / 'transport/current.npz',
                        tr.capture(home, streams, budget, dense, clock, next_record, target))
                checked = controller.audit_transport(home, legacy)
                tr.write(home / 'proofs' / ('auditoria_forward_%06d.json' % round(clock * 10)), checked)
                print(json.dumps(dict(clock=clock, accepted=[s.accepted for s in streams])), flush=True)
                if round(clock / .4) % 4 == 0:
                    tag = f'transporte_{round(clock * 10):06d}'
                    saved = persist(home, output / tag, f'{label}_{tag.upper()}', 'transport',
                                    clock, reg['closed_boundary'], helpers, auditor)
                    tr.write(home / 'proofs' / ('forward_%06d_permanent.json' % round(clock * 10)), saved)
                    print(json.dumps(dict(stage='transporte_recuperado', clock=clock,
                                          library_file_id=saved['library_file_id'])), flush=True)
                phase = 'evolution'
        for stream in streams:
            stream.close_segment()
        check = modules['native'].reference(streams[1].sim, (streams[0].sim, streams[1].sim, streams[0].q, streams[1].q))
        budget.algebra.append(dict(time=clock, **check))
        legacy.save_state(home, streams, budget)
        phase = 'boundary'
        print(json.dumps(dict(stage='estado_cerrado', clock=clock, steps=[s.accepted for s in streams])), flush=True)
        frontier = output / 'frontera_0032'
        saved = persist(home, frontier, label + '_FRONTERA_0032', 'boundary',
                        clock, target, helpers, auditor)
        phase = 'metrics'
        measured = measure(saved, frontier, target)
        passed = measured['prefix_pair_limits_met'] and measured['prefix_physical_controls_met']
        result = dict(
            scope='Repetición aislada del segmento P3', allocation=reg['allocation_id'],
            source_archive_sha256=reg['source_archive_sha256'], start=initial_clock,
            end=clock, registry_sha256=sha(args.registro), passed=passed,
            new_accepted_steps=[s.accepted - n for s, n in zip(streams, initial_steps)],
            physical_metadata=[s.metadata() for s in streams], persisted_boundary=saved['file_name'],
            library_file_id=saved['library_file_id'], archive_sha256=saved['sha256'],
            elapsed_seconds=round(time.monotonic() - started, 3),
            scientific_branch_advanced=False, CP12_closed=False, correction_validated=False,
            next_interval_executed=False,
        )
        write(output / 'RESULTADO.json', result)
        print(json.dumps(result), flush=True)
        return 0 if passed else 2
    except Exception:
        failed = home / 'negative' / ('INCIDENTE_' + reg['allocation_id'])
        failed.mkdir(parents=True, exist_ok=False)
        arrays = {f'grid_{i}_{key}': getattr(stream, key)
                  for i, stream in enumerate(streams) for key in ('q', 'v', 'initial_q', 'initial_v')}
        for name, family in [('raw', budget.raw), ('coupled', budget.coupled)]:
            for i, observer in enumerate(family):
                arrays[f'{name}_{i}_q'] = observer.q
                arrays[f'{name}_{i}_v'] = observer.v
        modules['np'].savez_compressed(failed / 'ESTADO_NO_CERTIFICADO.npz', **arrays)
        failure = dict(
            at=now(), phase=phase, clock=clock, traceback=traceback.format_exc(),
            physical_metadata=[s.metadata() for s in streams], correction_validated=False,
        )
        write(failed / 'FALLO.json', failure)
        write(output / 'INTERRUPCION.json', failure)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('home', 'registro', 'helpers', 'auditor', 'adaptadores', 'salida'):
        parser.add_argument('--' + name, type=lambda path: Path(path).resolve(), required=True)
    args = parser.parse_args()
    expected = args.adaptadores
    reg = read(args.registro)
    if (reg.get('run_scope') != 'independent_repeat_pending_reconciliation' or
            reg['clock'] != 30 or reg['target'] != 32 or reg['kind'] != 'transport' or
            sha(Path(__file__)) != reg['replay_driver_sha256']):
        raise ValueError('Registro de repetición inválido')
    if any(Path(sys.modules[name].__file__).resolve().parent != expected
           for name in ('base_preservar', 'continuar', 'preservar')):
        raise ValueError('La recuperación debe usar los adaptadores registrados')
    validate(reg, args.home, args.helpers, args.auditor)
    args.salida.mkdir(mode=0o700, exist_ok=False, parents=True)
    for directory in ('runtime/tmp', 'runtime/pycache'):
        (args.home / directory).mkdir(exist_ok=True, parents=True)
    with (args.registro.parent / 'P3_WORKER.lock').open('a+') as registry_lock, (
            args.home / 'runtime/worker.lock').open('a+') as state_lock:
        fcntl.flock(registry_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(state_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return repeat(args, reg)


if __name__ == '__main__':
    raise SystemExit(main())
