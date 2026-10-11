"""Backup only: wait for the already active original segment to close."""
from pathlib import Path
import argparse
import fcntl
import json
import sys
import time

p=argparse.ArgumentParser();p.add_argument('--time',type=int,required=True);p.add_argument('--helpers',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[2]
pair=root/'validacion/P06/no_radial/CP12/par_instrumentado__a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d'
runlock=root/'validacion/P06/no_radial/ejecucion_prov_a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d.lock'
backup_lock=root.parent/('CP12_preservar_tau'+str(a.time).zfill(4)+'.lock')
with backup_lock.open('a+') as exclusive:
    fcntl.flock(exclusive,fcntl.LOCK_EX|fcntl.LOCK_NB)
    proof=root/'trazabilidad/CP12_reconstruccion/respaldos'/('tau'+str(a.time).zfill(4)+'.json')
    if proof.exists():raise ValueError('Boundary already preserved; do not duplicate backup')
    while True:
        receipt=json.loads((pair/'procedencia.json').read_text())
        if receipt['status'] in ['FALLIDA','INTERRUMPIDA']:
            raise ValueError('Original execution failed; diagnose before backing up')
        progress=json.loads((pair/'CP12_par_progreso.json').read_text())
        if receipt['status'] in ['PAUSADA_REANUDABLE','COMPLETADA'] and progress['time']==a.time:
            with runlock.open('a+') as guard:
                try:fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:time.sleep(2);continue
            break
        if progress['time']>a.time:raise ValueError('Original execution passed requested boundary unexpectedly')
        time.sleep(5)
    print(json.dumps(dict(event='ORIGINAL_SEGMENT_CLOSED_BACKUP_ONLY',time=a.time)),flush=True)
    sys.path.insert(0,str(a.helpers.resolve()))
    from library_hosted_apps import HostedAppsClient
    from orquestador_respaldos import preserve
    preserve(root,a.helpers.resolve(),float(a.time),HostedAppsClient())
