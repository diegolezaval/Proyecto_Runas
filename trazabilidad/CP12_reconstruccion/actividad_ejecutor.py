"""Publish observed executor activity, without touching physics or checkpoints.

A recent record prevents duplicate workers across workspaces. An old record or
an inaccessible host never proves that a worker has stopped.
"""
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = 'a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
MONITOR_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def write(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(path)


def process_identity(pid):
    try:
        raw = Path(f'/proc/{pid}/stat').read_text()
        fields = raw[raw.rfind(')')+2:].split()
        return dict(start_ticks=fields[19], parent_pid=int(fields[1]),
                    command=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode())
    except (FileNotFoundError, ProcessLookupError):
        return None


def observe(pid, start_ticks, instance, continuation_log):
    identity = process_identity(pid)
    coordinator = bool(identity and identity['start_ticks'] == start_ticks and
                       'continuacion_raiz_20261010.py' in identity['command'])
    # procps cannot reliably resolve its own PID under the executor's nested
    # PID namespace. Read the mounted procfs directly, retaining uncertainty
    # on permission/read errors and allowing processes that disappear to race.
    pipeline, query_errors = [], []
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():
            continue
        try:
            process = process_identity(int(path.name))
        except OSError as error:
            query_errors.append(dict(pid=int(path.name), error=type(error).__name__))
            continue
        if process is None:
            continue
        command = process['command']
        if str(ROOT) not in command:
            continue
        names = ['herramientas/reproducir_par_CP12.py', 'orquestador_respaldos.py',
                 'lectura_final_automatica.py']
        if any(name in command for name in names) or (
                'gestionar_respaldo_CP12.py' in command and '--avanzar' in command):
            pipeline.append(dict(pid=int(path.name), parent_pid=process['parent_pid'], command=command))
    proofs = []
    for path in sorted((ROOT/'trazabilidad/CP12_reconstruccion/respaldos').glob('tau????.json')):
        value = json.loads(path.read_text())
        if value.get('passed') and value.get('download_verification', {}).get('passed'):
            proofs.append((path, value))
    if not proofs:
        raise ValueError('No verified boundary: do not publish activity without context')
    path, proof = max(proofs, key=lambda item: item[1]['time'])
    events = []
    for line in continuation_log.read_text().splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get('event'):
            events.append(value)
    active = coordinator or bool(pipeline)
    activity_known = active or not query_errors
    status = 'ACTIVE' if active else (
        'INACTIVE_OBSERVED_ON_ORIGINAL_EXECUTOR' if activity_known else 'UNKNOWN_ACTIVITY')
    return dict(schema='CP12_OBSERVED_EXECUTOR_ACTIVITY_NOT_A_CHECKPOINT',
                observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                monitor_source_sha256=MONITOR_SHA256,
                executor_instance=instance,
                executor_boot_sha256=hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes()).hexdigest(),
                original_workspace=str(ROOT), coordinator_pid=pid,
                coordinator_start_ticks=start_ticks, coordinator_identity_matches=coordinator,
                pipeline_processes=pipeline, active=active if activity_known else None,
                status=status, activity_known=activity_known,
                process_query_method='mounted_procfs', process_query_errors=query_errors,
                last_verified_boundary=dict(time=proof['time'], zip_sha256=proof['zip_sha256'],
                    state_sha256=proof['state_sha256'], proof_path=path.relative_to(ROOT).as_posix()),
                last_coordinator_event=events[-1] if events else None,
                science_run_id=RUN_ID, scientific_closure=False, M2_steps_by_this_monitor=0,
                interpretation='A recent active record blocks another worker. Staleness, a missing file or another host cannot establish inactivity. Independently recover and verify the complete scientific backup before resuming.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helpers', type=Path, required=True)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--start-ticks', required=True)
    parser.add_argument('--instance', required=True)
    parser.add_argument('--state-file', type=Path, required=True)
    parser.add_argument('--metadata-file', type=Path, required=True)
    parser.add_argument('--continuation-log', type=Path, required=True)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    args.state_file.parent.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    with args.state_file.with_suffix('.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            state = observe(args.pid, args.start_ticks, args.instance, args.continuation_log)
            write(args.state_file, state)
            upload = dict(local_path=str(args.state_file.resolve()), purpose='create_library_file',
                          library_artifact_type='other')
            if args.metadata_file.exists():
                owned = json.loads(args.metadata_file.read_text())
                upload = dict(local_path=str(args.state_file.resolve()), purpose='replace_library_file',
                              library_file_id=owned['library_file_id'],
                              version_reason='Observed original CP12 executor activity; zero physics steps')
            result = subprocess.run([sys.executable, str(args.helpers.resolve()/'library_upload.py')],
                input=json.dumps({'uploads': [upload]}), text=True, capture_output=True, timeout=55)
            if result.returncode:
                raise RuntimeError('Activity publication failed: '+result.stderr[-2000:])
            outcomes = json.loads(result.stdout)['results']
            if len(outcomes) != 1 or outcomes[0].get('status') != 'succeeded':
                raise RuntimeError('Activity not saved: '+str(outcomes))
            if args.metadata_file.exists() and outcomes[0]['library_file_id'] != owned['library_file_id']:
                raise RuntimeError('Activity record identity changed')
            write(args.metadata_file, outcomes[0])
            print(json.dumps(dict(event='EXECUTOR_ACTIVITY_SAVED', observed_at=state['observed_at'],
                active=state['active'], verified_time=state['last_verified_boundary']['time'],
                library_file_id=outcomes[0]['library_file_id'], file_id=outcomes[0]['file_id'])), flush=True)
            if args.once or state['active'] is False:
                return
            time.sleep(60)


if __name__ == '__main__':
    main()
