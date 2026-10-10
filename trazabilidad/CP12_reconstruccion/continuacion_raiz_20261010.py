"""Continue verified original boundaries, then the registered offline reader."""
from pathlib import Path
import argparse
import fcntl
import json
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helpers', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--from-time', type=int, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    support = root/'trazabilidad/CP12_reconstruccion'
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    sys.path.insert(0, str(root/'herramientas'))
    import ejecutar_con_procedencia as prov

    def emit(event, **values):
        print(json.dumps(dict(event=event, at=prov.now(), **values)), flush=True)

    with (support/'coordinador_raiz.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        emit('BEGIN_VERIFIED_ORIGINAL_CONTINUATION', from_time=args.from_time,
             science_run_id='a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d')
        subprocess.run([sys.executable, str(support/'orquestador_respaldos.py'),
            '--root', str(root), '--helpers', str(args.helpers.resolve()),
            '--from-time', str(args.from_time), '--to-time', '160'], cwd=root, check=True)
        emit('EVOLUTION_AND_BACKUPS_FINISHED', time=160, interpretation_pending=True)
        subprocess.run([sys.executable, str(support/'lectura_final_automatica.py'),
            '--helpers', str(args.helpers.resolve()), '--continuation-log', str(args.log.resolve())],
            cwd=root, check=True)
        emit('REGISTERED_CAUSAL_READING_COMPLETE', scientific_review_pending=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps(dict(event='STOP_AND_DIAGNOSE', error=repr(error))), flush=True)
        raise
