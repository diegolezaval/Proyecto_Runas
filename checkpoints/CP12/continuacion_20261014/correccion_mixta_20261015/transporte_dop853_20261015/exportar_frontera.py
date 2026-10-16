"""Publishable summary of an already recovered mixed boundary; no M2 calls."""
from pathlib import Path
import argparse
import datetime
import json


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def export(home, repo):
    candidates = []
    for path in (home / 'proofs').glob('tau*_permanent.json'):
        proof = read(path)
        if proof.get('schema') != 'CP12_MIXTO_TRIAL_BOUNDARY_PERMANENTLY_RECOVERED_AND_AUDITED':
            continue
        assert proof['passed'] and proof['all_payload_hashes_verified']
        audit = proof['independent_extracted_audit']
        assert audit['passed'] and audit['M2_steps_executed'] == 0 and all(audit['tests'].values())
        assert proof['time'] == audit['time'] and proof['state_sha256'] == audit['state_sha256']
        assert proof['configuration_sha256'] == audit['configuration_sha256']
        assert proof['receipt_sha256'] == audit['receipt_sha256']
        candidates.append(proof)
    assert candidates
    proof = max(candidates, key=lambda item: item['time'])
    time = proof['time']
    state = read(repo / 'estado_progreso.json')
    previous = state['latest_verified_cp12_mixed_restart']['time']
    if previous >= time:
        return dict(written=False, latest_boundary=time, already_published_boundary=previous)
    initial = read(home / 'proofs/tau0000_permanent.json')
    assert state['mixed_transport_initial_capsule_sha256'] == initial['zip_sha256']
    assert proof['execution_run_id'] == initial['execution_run_id']
    assert time > 0 and time % 8 == 0 and proof['configuration_sha256'] == initial['configuration_sha256']
    stages = json.dumps(state['stages'], sort_keys=True)
    prefix = Path('checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015')
    relative = prefix / 'transporte_dop853_20261015' / ('FRONTERA_MIXTA_TAU%04d.json' % time)
    report = Path('informes/FRONTERAS_MIXTAS_CP12_20261016.md')
    keys = ('schema', 'time', 'passed', 'execution_run_id', 'zip_sha256', 'zip_bytes',
            'state_sha256', 'configuration_sha256', 'receipt_sha256',
            'all_payload_hashes_verified', 'independent_extracted_audit',
            'local_source_archive_unchanged_after_upload', 'CP12_closed')
    public = {key: proof[key] for key in keys}
    public.update(numerical_trial_boundary=True, correction_validated=False,
                  project_scientific_checkpoint_unchanged='CP11',
                  final_spatial_and_mechanism_gates_not_accepted_by_this_export=True)
    write(repo / relative, public)
    lines = ['# CP12 · Fronteras numéricas mixtas recuperadas', '',
             f'Última frontera completa recuperada y auditada: **τ={time}**. '
             'CP11 sigue siendo el último checkpoint científico aceptado; CP12 permanece abierto.', '',
             '| Frontera | Bytes del ZIP | SHA256 |', '|---|---:|---|']
    for item in sorted(candidates, key=lambda value: value['time']):
        lines.append(f"| {item['time']} | {item['zip_bytes']} | `{item['zip_sha256']}` |")
    lines += ['', 'Cada frontera conserva ambas mallas, entradas, fuentes, campos y observadores, '
              'configuración, contadores y recibo. Sus recuperaciones pasan las auditorías '
              'independientes con cero pasos M2. Un transporte intermedio anterior conserva su '
              'alcance como evidencia del tramo abierto y no sustituye una frontera posterior.', '',
              'Las puertas de conservación e integridad del prefijo están verificadas. '
              'La comparación espacial original del 2 % en τ160, la eliminación del mecanismo '
              'en las tres ventanas y las pruebas justificadas de convergencia, estabilidad y '
              'robustez conservan sus dependencias; esta exportación no las acepta.', '',
              'Consultar primero cápsulas posteriores y actividad propia antes de recuperar. '
              'Usar RECUPERAR_FRONTERA.md para una frontera completa y RECUPERAR.md para un '
              'transporte interno posterior. Conservar todos los negativos; main, PR #2 y las '
              '33 etapas permanecen intactos.', '']
    (repo / report).write_text('\n'.join(lines))
    state['latest_verified_cp12_mixed_restart'] = dict(time=time, proof=str(relative),
        state_sha256=proof['state_sha256'], configuration_sha256=proof['configuration_sha256'],
        receipt_sha256=proof['receipt_sha256'], zip_sha256=proof['zip_sha256'],
        zip_bytes=proof['zip_bytes'], full_capsule_recovered_and_audited=True,
        correction_validated=False, CP12_closed=False)
    state['execution_activity']['mixed_candidate_latest_certified_time'] = time
    for item in state['numerical_runs_in_progress']:
        if item.get('campaign') == 'CP12_PILOTO_MIXTO_PHI_FV_CHI_K4':
            item.update(latest_certified_time=time, evidence=str(relative))
    action = (f'Última frontera numérica mixta guardada, recuperada y auditada: τ={time}. '
              'Consultar primero estados posteriores y actividad propia; continuar sólo desde '
              'evidencia válida, sin repetir el prefijo. Mantener ambas energías, carga, '
              'observadores, comparación espacial original del 2 % y dependencias causales, '
              'de convergencia, estabilidad y robustez. CP12 abierto.')
    state['next_actions'][0] = state['next_calculation'] = action
    state['history'].append(dict(event='CP12_FRONTERA_NUMERICA_MIXTA_RECUPERADA',
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), time=time,
        evidence=str(relative), report=str(report), closed_stages=[], reopened_stages=[],
        project_scientific_checkpoint_unchanged=True, correction_validated=False, CP12_closed=False))
    assert json.dumps(state['stages'], sort_keys=True) == stages
    write(repo / 'estado_progreso.json', state)
    recovery = repo / 'RECUPERACION_CP12_ACTUAL.md'
    recovery.write_text(recovery.read_text() + f'\nÚltima frontera numérica del ensayo mixto '
        f'guardada/recuperada/auditada: τ={time}, comprobante `{relative}`, estado SHA256 '
        f'`{proof["state_sha256"]}`. No valida la corrección ni cierra CP12. Buscar primero '
        'cápsulas posteriores; no repetir este prefijo.\n')
    return dict(written=True, time=time, certificate=str(relative))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.home.resolve(), args.repo.resolve())))
