"""Adaptador de procedencia para siguientes protocolos M2, sin mover CP10.

El protocolo debe declarar campaign_directory y este archivo en extra_code
de cada caso. Las ecuaciones y los trabajadores siguen siendo propios del
protocolo; este adaptador controla ubicación, hilos y recuperación de estados.
"""
from pathlib import Path
import argparse
import fcntl
import json
import os
import re
import ejecutar_con_procedencia as provenance

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()
THREADS = {'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}


def configure(protocol, case_name=None):
    data = json.loads(protocol.read_text())
    if data['model'] != 'M2':
        raise ValueError('Este adaptador captura Θ común M2; otro modelo requiere su adaptador explícito')
    location = Path(data['campaign_directory'])
    if location.is_absolute() or '..' in location.parts or not location.parts or location.parts[0] != 'validacion':
        raise ValueError('campaign_directory debe ser relativo y estar bajo validacion/')
    campaign = (ROOT / location).resolve()
    if not campaign.is_relative_to(ROOT / 'validacion'):
        raise ValueError('Campaña fuera del corpus')
    if case_name is not None:
        if not re.fullmatch(r'[A-Za-z0-9_]+', case_name):
            raise ValueError('Nombre de caso ambiguo')
        if SELF not in data['cases'][case_name].get('extra_code', []):
            raise ValueError('Declarar este adaptador en extra_code antes de ejecutar')
    provenance.CAMPAIGN = campaign
    os.environ.update(THREADS)  # applied before the child imports numerical libraries
    return data


def recover_if_needed(protocol, case_name):
    _, case, identity, run_id = provenance.prepare(protocol, case_name)
    folder = provenance.CAMPAIGN / (case_name + '__' + run_id)
    path = folder / 'procedencia.json'
    if not path.is_file():
        raise ValueError('No existe esta identidad: --reanudar no inicia una ejecución nueva')
    receipt = json.loads(path.read_text())
    if receipt['status'] not in ['EN_PROGRESO', 'INTERRUMPIDA', 'PAUSADA_REANUDABLE']:
        return
    lock_path = ROOT / ('validacion/P06/no_radial/ejecucion_prov_' + run_id + '.lock')
    with lock_path.open('a+') as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if receipt['identity'] != identity:
            raise ValueError('Identidad de reinicio incompatible')
        verified = provenance.verify_receipt(path)
        if any(not item.startswith('output:') for item in verified['issues']):
            raise ValueError('Fuente, configuración o identidad de reinicio alterada')
        if receipt['status'] == 'PAUSADA_REANUDABLE' and not verified['passed']:
            raise ValueError('Piloto cerrado alterado')
        states = list(folder.glob('*_estado.npz'))
        progresses = list(folder.glob('*_progreso.json'))
        if len(states) != 1 or len(progresses) != 1:
            raise ValueError('Reinicio requiere un estado y un progreso inequívocos')
        import numpy as np
        with np.load(states[0], allow_pickle=False) as saved:
            time = float(saved['time'])
            config = json.loads(str(saved['config']))
            if not all(np.isfinite(saved[k]).all() for k in ['q', 'v', 'initial_q', 'initial_v', 'rows']):
                raise ValueError('Estado no finito')
            if any(config[k] != v for k, v in case['configuration'].items()):
                raise ValueError('Configuración interna de reinicio incompatible')
            rows = saved['rows']
            if rows[-1, 0] != time or rows[0, 0] != 0 or not np.all(np.diff(rows[:, 0]) > 0):
                raise ValueError('Tiempos de observación incompatibles')
        progress = json.loads(progresses[0].read_text())
        target = case['configuration']['tmax']
        valid_phase = (progress['status'] == 'EN_PROGRESO' and time < target or
                       progress['status'] in ['EVOLUCION_TERMINADA_DIAGNOSTICO_PENDIENTE', 'CALCULO_TERMINADO'] and time == target)
        if progress['time'] != time or not valid_phase or not 0 <= time <= target:
            raise ValueError('Estado/progreso no válido para continuación')
        result_path = folder / states[0].name.replace('_estado.npz', '.json')
        if progress['status'] == 'EVOLUCION_TERMINADA_DIAGNOSTICO_PENDIENTE' and result_path.exists():
            raise ValueError('Diagnóstico parcial existente: conservarlo y cerrar sus vistas en copia antes de reutilizar el trabajador')
        if progress['status'] == 'CALCULO_TERMINADO':
            csv_path = folder / states[0].name.replace('_estado.npz', '_tiempo.csv')
            if not result_path.is_file() or not csv_path.is_file() or json.loads(result_path.read_text())['configuration'] != config or not np.array_equal(np.loadtxt(csv_path, delimiter=',', skiprows=1, ndmin=2), rows):
                raise ValueError('Salidas de cálculo terminado incompletas o incompatibles')
        if receipt['status'] == 'PAUSADA_REANUDABLE':
            return
        stamp = provenance.now()
        last = receipt['segments'][-1]
        last.update(status='INTERRUMPIDA', interruption_detected_at=last.get('interruption_detected_at', stamp),
                    recovered_time=time, recovered_state=states[0].name,
                    recovered_state_sha256=provenance.digest(states[0]))
        if 'reason' not in last:
            last['reason'] = 'Segmento sin cierre, sin escritor activo; instante de terminación desconocido.'
        receipt['status'] = 'INTERRUMPIDA'
        receipt.setdefault('recoveries', []).append(dict(detected_at=stamp, saved_time=time,
            state_sha256=last['recovered_state_sha256'], configuration_and_identity_verified=True,
            finite_arrays_verified=True, exclusive_kernel_lock_available=True,
            recovery_tool=SELF, recovery_tool_sha256=provenance.digest(Path(__file__).resolve())))
        provenance.write(path, receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocolo', type=Path, required=True)
    parser.add_argument('--caso')
    parser.add_argument('--stop-at', type=float)
    parser.add_argument('--reanudar', action='store_true')
    parser.add_argument('--verificar', action='store_true')
    args = parser.parse_args()
    protocol = args.protocolo.resolve() if args.protocolo.is_absolute() else ROOT / args.protocolo
    configure(protocol, None if args.verificar else args.caso)
    if args.verificar:
        reports = [provenance.verify_receipt(p) for p in sorted(provenance.CAMPAIGN.glob('*/procedencia.json'))]
        passed = bool(reports) and all(r['passed'] for r in reports)
        print(json.dumps(dict(passed=passed, receipts=reports), ensure_ascii=False, indent=2))
        raise SystemExit(0 if passed else 1)
    if args.caso is None:
        parser.error('--caso requerido')
    if args.reanudar:
        recover_if_needed(protocol, args.caso)
    provenance.execute(protocol, args.caso, args.stop_at, args.reanudar)
