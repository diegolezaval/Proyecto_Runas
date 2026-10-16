"""Export verified transport evidence; never advance or certify a new M2 gate."""
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
    for path in (home / 'proofs').glob('TRANSPORTE_TAU_*_permanent.json'):
        proof = read(path)
        if proof.get('schema') != 'CP12_PERMANENTLY_RECOVERED_INTERNAL_TRANSPORT_NOT_SCIENTIFIC_FRONTIER':
            continue
        assert proof['passed'] and proof['all_payload_hashes_verified']
        audit = proof['independent_zero_step_audit']
        assert audit['passed'] and audit['M2_steps_executed'] == 0 and all(audit['tests'].values())
        candidates.append(proof)
    assert candidates
    proof = max(candidates, key=lambda item: item['observer_clock'])
    clock = proof['observer_clock']
    state_path = repo / 'estado_progreso.json'
    state = read(state_path)
    previous = state.get('latest_verified_cp12_mixed_transport', {}).get('observer_clock', -1)
    if previous >= clock:
        return dict(written=False, latest_permanent_clock=clock, already_published_clock=previous)
    initial_hash = read(home / 'proofs/tau0000_permanent.json')['zip_sha256']
    anchor = state.get('mixed_transport_initial_capsule_sha256', state['latest_verified_cp12_mixed_restart']['zip_sha256'])
    assert anchor == initial_hash, 'Public progress belongs to another attempt; do not overwrite it'
    control = read(home / 'proofs/CONTROL_TRANSPORTE_M2_UN_INTERVALO.json')
    assert control['passed'] and control['physical_and_passive_states_solver_memory_dense_and_counters_bitwise_exact']
    stages = json.dumps(state['stages'], sort_keys=True)
    prefix = Path('checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015')
    relative = prefix / ('TRANSPORTE_TAU_%06d.json' % round(clock * 10))
    keys = ('schema', 'passed', 'observer_clock', 'payload_files', 'zip_sha256', 'zip_bytes',
            'all_payload_hashes_verified', 'transport_state_sha256', 'independent_zero_step_audit',
            'scientific_frontier', 'correction_validated', 'CP12_closed')
    public = {key: proof[key] for key in keys}
    public['registration_commit'] = read(home / 'preregistration/registro_transporte.json')['registration_commit']
    public['original_transport_registration_commit'] = 'e080cec73d44fe099d6de40715732ef7d11f7d9a'
    write(repo / relative, public)
    report = Path('informes/TRANSPORTES_MIXTOS_CP12_20261015.md')
    previous_report = (repo / report).read_text() if (repo / report).exists() else ''
    incident_marker = '## Incidentes administrativos conservados'
    incident_tail = previous_report[previous_report.index(incident_marker):] if incident_marker in previous_report else ''
    lines = ['# CP12 · Transportes mixtos recuperados', '',
             f'Último reloj del observador recuperado y rehidratado: **τ={clock:g}**. '
             'Los tiempos físicos reales, balances y contadores están en cada certificado. '
             'Estos estados internos permiten continuar DOP853 sin resembrar ni partir un paso adaptativo.', '',
             '| Reloj | Bytes del ZIP | SHA256 |', '|---|---:|---|']
    for item in sorted(candidates, key=lambda value: value['observer_clock']):
        lines.append(f"| {item['observer_clock']:g} | {item['zip_bytes']} | `{item['zip_sha256']}` |")
    lines += ['', 'Cada cápsula completa supera cobertura/tamaños/hashes y la auditoría independiente '
              'de rehidratación con cero pasos M2. El contraste preregistrado .4→.41 coincide bit a bit; '
              'su trabajo diagnóstico se registra separadamente. No se repiten A–D ni campañas certificadas.', '',
              'Las fronteras científicas siguen cada ocho unidades. Se mantienen ambas energías ≤2e-4, '
              'carga ≤1e-9, identidades, observadores, cinco métricas espaciales ≤2 %, eliminación del mecanismo '
              'y pruebas adicionales de convergencia/estabilidad/robustez. Un transporte no las sustituye.', '',
              'CP12 permanece abierto y CP11 sigue aceptado. La producción conserva sus paradas y negativos. '
              'Main, PR #2 y las 33 etapas permanecen intactos. Recuperar primero el transporte o frontera '
              'válido más avanzado usando RECUPERAR.md; no volver a τ0 si existe un estado posterior.', '']
    (repo / report).write_text('\n'.join(lines) + ('\n' + incident_tail if incident_tail else ''))
    state['mixed_transport_initial_capsule_sha256'] = initial_hash
    state['latest_verified_cp12_mixed_transport'] = dict(observer_clock=clock, proof=str(relative),
        state_sha256=proof['transport_state_sha256'], zip_sha256=proof['zip_sha256'], zip_bytes=proof['zip_bytes'],
        full_capsule_recovered_and_rehydrated=True, scientific_frontier=False, CP12_closed=False)
    state['execution_activity']['mixed_candidate_latest_recoverable_observer_clock'] = clock
    for item in state['numerical_runs_in_progress']:
        if item.get('campaign') == 'CP12_PILOTO_MIXTO_PHI_FV_CHI_K4':
            item.update(latest_recoverable_observer_clock=clock, evidence=str(relative))
    action = (f'Continuar/supervisar el piloto mixto con transporte DOP853 verificado; último respaldo '
              f'completo recuperado/auditado: reloj {clock:g}. Recuperar primero cualquier estado posterior, '
              'sin volver a τ0 ni reiniciar el integrador. Mantener fronteras científicas cada 8 y todas '
              'las puertas originales; conservar y analizar cualquier fallo. CP12 abierto.')
    state['next_actions'][0] = action
    state['next_calculation'] = action
    state['history'].append(dict(event='CP12_TRANSPORTE_INTERNO_RECUPERADO',
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), scientific_checkpoint_unchanged=True,
        closed_stages=[], reopened_stages=[], report=str(report), recoverable_observer_clock=clock,
        independent_zero_step_checks=len(proof['independent_zero_step_audit']['tests']),
        scientific_frontier=False, correction_validated=False, CP12_closed=False))
    assert json.dumps(state['stages'], sort_keys=True) == stages
    write(state_path, state)
    recovery = repo / 'RECUPERACION_CP12_ACTUAL.md'
    recovery.write_text(recovery.read_text() + f'\nÚltimo transporte permanente recuperado/rehidratado: '
        f'reloj observador τ={clock:g}. Comprobante `{relative}`; estado interno SHA256 '
        f'`{proof["transport_state_sha256"]}`. No es una frontera científica ni cierre CP12. '
        'Recuperar primero cualquier transporte o frontera posterior; no volver a τ0.\n')
    return dict(written=True, observer_clock=clock, certificate=str(relative), report=str(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.home.resolve(), args.repo.resolve())))
