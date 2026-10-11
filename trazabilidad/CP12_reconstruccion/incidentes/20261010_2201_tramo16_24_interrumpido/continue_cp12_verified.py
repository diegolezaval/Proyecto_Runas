"""Continue the existing CP12 segment, preserving every original boundary."""
from pathlib import Path
import datetime
import fcntl
import importlib.util
import json
import os
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'Proyecto_Runas'
HELPERS = BASE / '.library_helpers'
PAIR = ROOT / 'validacion/P06/no_radial/CP12/par_instrumentado__a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
LOCK = ROOT / 'validacion/P06/no_radial/ejecucion_prov_a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d.lock'
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
sys.path.insert(0, str(HELPERS))
from library_hosted_apps import HostedAppsClient

def emit(event, **values):
    print(json.dumps(dict(event=event, at=datetime.datetime.now(datetime.timezone.utc).isoformat(), **values)), flush=True)

def locked():
    with LOCK.open('a+') as held:
        try:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False

def main():
    emit('WAIT_EXISTING_SEGMENT', target=16)
    while locked():
        time.sleep(5)
    receipt = json.loads((PAIR/'procedencia.json').read_text())
    progress = json.loads((PAIR/'CP12_par_progreso.json').read_text())
    if receipt['status'] != 'PAUSADA_REANUDABLE' or progress['time'] != 16:
        raise RuntimeError('Existing segment did not finish at tau=16; preserve and diagnose, do not relaunch')
    path = ROOT/'trazabilidad/CP12_reconstruccion/orquestador_respaldos.py'
    spec = importlib.util.spec_from_file_location('cp12_original_orchestrator', path)
    orchestration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(orchestration)
    client = HostedAppsClient()
    orchestration.preserve(ROOT, HELPERS, 16.0, client)
    for target in range(24, 161, 8):
        emit('BEGIN_REGISTERED_SEGMENT', from_time=target-8, to_time=target)
        orchestration.run([sys.executable, str(ROOT/'herramientas/gestionar_respaldo_CP12.py'), '--avanzar', str(target)], cwd=ROOT)
        orchestration.preserve(ROOT, HELPERS, float(target), client)
    emit('EVOLUTION_AND_BACKUPS_FINISHED', time=160, interpretation_pending=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        emit('STOP_AND_DIAGNOSE', error=repr(error))
        raise
