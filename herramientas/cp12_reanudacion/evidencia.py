"""Resolver el respaldo y las puertas a partir de un HEAD científico fijado."""

from dataclasses import dataclass
from pathlib import PurePosixPath
import re

from .infra import BRANCH, CLAIM, PREFIX, RELEASE, ROOT, STATE, UID, Stop, digest, require


def zero(audit, count=None):
    require(audit['passed'] is True and audit['M2_steps_executed'] == 0 and
            audit['DOP853_construction_or_step_attempts'] == 0, 'Auditoría distinta de cero evolución')
    if count is not None:
        require(len(audit['tests']) == count and all(x is True for x in audit['tests'].values()),
                'Controles originales incompletos')


def checked_audits(audits, spec):
    boundary = audits['boundary']
    zero(boundary, 30)
    require(boundary['execution_uuid'] == UID and boundary['time'] == spec['closed_boundary'] and
            boundary['state_sha256'] == spec.get('closed_state_sha256', spec.get('state_sha256')) and
            boundary['receipt_sha256'] == spec['receipt_sha256'] and
            boundary['configuration_sha256'] == spec['configuration_sha256'],
            'La frontera auditada no coincide con el respaldo')
    if spec['kind'] == 'transport':
        transport = audits['transport']
        zero(transport, 14)
        require(transport['observer_clock'] == spec['observer_clock'] and
                transport['target'] == spec['target'] and
                transport['state_sha256'] == spec['transport_state_sha256'],
                'El transporte auditado no coincide con el respaldo')


def recovery(value, spec):
    value = value.get('native', value)
    require(value['passed'] is True and all(value[key] == spec[key] for key in ('sha256', 'bytes')),
            'El recibo recuperado no coincide con el archivo')
    if 'library_file_id' in value:
        require(all(value[key] == spec[key] for key in ('library_file_id', 'file_id', 'file_name')),
                'Identidad nativa distinta en el recibo')
    if 'github_asset_id' in spec:
        require(value['github_asset_id'] == spec['github_asset_id'], 'Adjunto distinto en el recibo')
    content = value.get('recovery', value)
    require(content['passed'] is True and content['exact_manifest_coverage'] is True and
            content['all_payload_hashes_verified_before_and_after'] is True and
            content['payload_files'] == spec['payload_files'], 'Recuperación independiente incompleta')
    checked_audits(content['original_audits'], spec)
    return content


@dataclass
class Plan:
    head: str
    state: dict
    origin: dict
    frontier: dict
    registry_path: str
    registry_bytes: bytes
    registry: dict
    receipt: dict
    frontier_receipt: dict
    claim: dict | None
    blocked: dict | None

    @property
    def registry_sha(self):
        return digest(self.registry_bytes)

    @property
    def directory(self):
        return str(PurePosixPath(self.registry_path).parent)

    @property
    def allocation(self):
        return self.registry['allocation_id']

    def files(self, git, name, *, missing=False):
        return git.json(self.head, f'{self.directory}/{name}', missing=missing)

    def assignment_matches(self):
        reg, source = self.registry, self.origin
        return (reg['kind'] == source['kind'] and reg['clock'] == source['observer_clock'] and
                reg['target'] == self.state['current_target'] == source.get('target', source.get('next_target')) and
                reg['closed_boundary'] == source['closed_boundary'] == self.frontier['observer_clock'] and
                reg['source_archive_sha256'] == source['sha256'] and
                reg['closed_state_sha256'] == source.get('closed_state_sha256', source.get('state_sha256')) and
                reg['receipt_sha256'] == source['receipt_sha256'] and
                reg['configuration_sha256'] == source['configuration_sha256'] and
                (reg['kind'] != 'transport' or
                 (reg['source_recovery_evidence'] == source['recovery_receipt'] and
                  reg['source_library_file_id'] == source['library_file_id'] and
                  reg['source_file_id'] == source['file_id'] and
                  reg['transport_sha256'] == source['transport_state_sha256'])))


def resolve(git, head):
    state = git.json(head, STATE)
    require(state['schema'] == 'CP12_P3_CANONICAL_RECOVERY_REGISTER' and state['branch'] == BRANCH and
            state['execution_uuid'] == UID and state['CP12_closed'] is False and
            state['correction_validated'] is False, 'Registro vigente fuera de la línea CP12/P3 abierta')
    frontier = state['latest_full_frontier_proof']
    require(frontier['kind'] == 'boundary' and frontier['passed'] is True and
            frontier['all_five_spatial_and_physical_gates_passed'] is True and
            frontier['observer_clock'] == state['latest_full_trial_frontier_recovered_and_audited'],
            'Frontera pública sin acreditación científica completa')
    certificate = git.json(head, frontier['certificate'])
    metrics = git.json(head, frontier['original_spatial_and_physical_metrics'])
    require(certificate['passed'] is True and certificate['time'] == frontier['observer_clock'] and
            certificate['state_sha256'] == frontier['state_sha256'] and
            metrics['prefix_pair_limits_met'] is True and metrics['prefix_physical_controls_met'] is True and
            metrics['M2_steps_executed'] == 0, 'Certificado o métricas originales de frontera distintos')
    frontier_path = str(PurePosixPath(frontier['certificate']).with_name('RECUPERACION_PUBLICA.json'))
    frontier_receipt = recovery(git.json(head, frontier_path), frontier)
    options = [frontier]
    for field in ('latest_intermediate_transport', 'latest_protected_administrative_transport'):
        candidate = state.get(field)
        if candidate and candidate['observer_clock'] > frontier['observer_clock']:
            require(candidate['kind'] == 'transport' and candidate['passed'] is True and
                    candidate['scientific_frontier'] is False and
                    candidate['closed_boundary'] == frontier['observer_clock'],
                    'Transporte registrado sin respaldo de su frontera')
            options.append(candidate)
    options.sort(key=lambda item: item['observer_clock'], reverse=True)
    origin = options[0]
    require(not any(x['observer_clock'] == origin['observer_clock'] and x['sha256'] != origin['sha256']
                    for x in options[1:]), 'Dos orígenes distintos declaran el mismo reloj')
    require(origin['observer_clock'] >= state['latest_recoverable_observer_clock'],
            'Reloj recuperable anunciado sin prueba canónica')
    receipt = recovery(git.json(head, origin['recovery_receipt']), origin) if origin is not frontier else frontier_receipt
    registry_path = state.get('current_assignment')
    if not registry_path:
        raise Stop('ASIGNACION_PENDIENTE', 'Falta una asignación registrada para el siguiente segmento',
                   f'Registrar la asignación desde τ{origin["observer_clock"]:g}', destination=BRANCH)
    require(registry_path.startswith(ROOT + '/') and registry_path.endswith('/REGISTRO.json'),
            'Asignación fuera de CP12/P3')
    registry_bytes = git.get(head, registry_path)
    registry = git.json(head, registry_path)
    require(re.fullmatch('[a-z0-9_]+', registry['allocation_id']), 'Identidad de asignación inválida')
    claim = git.json(head, CLAIM, missing=True)
    block_path = state.get('active_publication_block')
    blocked = git.json(head, block_path) if block_path else None
    if blocked:
        require(blocked['allocation_id'] == registry['allocation_id'] and
                blocked['github_release_id'] == RELEASE, 'Bloqueo de otra asignación o Release')
    return Plan(head, state, origin, frontier, registry_path, registry_bytes, registry,
                receipt, frontier_receipt, claim, blocked)


def unpublished(plan, assets, items):
    """Un nombre aporta una pista para reconciliar, nunca un certificado."""
    clock = plan.origin['observer_clock']
    known_names = {plan.origin['file_name'], plan.frontier['file_name']}
    known_names.update(x['file_name'] for x in
                       plan.state.get('native_verified_transport_retention', {}).get('retained', []))
    for destination, candidates in (('GitHub Releases', assets), ('Biblioteca', items)):
        for item in candidates:
            name = item['name']
            if not name.startswith(PREFIX) or name in known_names:
                continue
            match = re.match(r'(TRANSPORTE_(\d{6})|RESCATE_ADMIN_(\d{6})|FRONTERA_(\d{4}))_', name[len(PREFIX):])
            if match:
                observed = float(match[4]) if match[4] else int(match[2] or match[3]) / 10
                if observed >= clock:
                    return dict(file=name, destination=destination, identity=item.get('id'), observer_clock=observed)
            suffix = name[len(PREFIX):]
            if suffix.startswith(('NEGATIVO_', 'FALLO_')) and (
                    name.endswith('_' + plan.allocation.upper() + '.zip') or
                    suffix == f'NEGATIVO_{plan.registry["target"]:04d}.zip'):
                return dict(file=name, destination=destination, identity=item.get('id'), negative_or_incident=True)
    return None


def first_step(value, reg):
    steps = value['accepted_steps_since_restore']
    require(reg['clock'] < value['clock'] <= reg['target'] and len(steps) == 2 and
            all(type(n) is int and n >= 0 for n in steps) and any(steps) and
            value['replay96_to112_executed'] is False and value['CP12_closed'] is False,
            'Inicio sin un nuevo paso físico aceptado')


def historical_chain(git, plan):
    """Releer los mismos bytes que precedieron a la entrega, sin repetir el tramo."""
    if not plan.state.get('own_observed_start'):
        return None
    start = plan.files(git, 'RECEPCION_ACREDITADA_POR_INICIO.json')
    delivery = plan.files(git, 'ACTIVACION_RECUPERADA_Y_ENTREGADA.json')
    activation = plan.files(git, 'ACTIVACION.json')
    reserved = plan.files(git, 'RESERVA_RECUPERADA.json')
    old_boundary = plan.registry['kind'] == 'boundary' and 'public_path' not in reserved
    if old_boundary:
        require(reserved['passed'] is True and reserved['capacity_receipt_public_bytes_exact'] is True and
                reserved['M2_steps_executed'] == 0 and delivery['passed'] is True and
                start['passed'] is True and activation['public_reservation_recovered_exactly'] is True,
                'Expediente original de frontera incompleto')
        reservation_path = f'{plan.directory}/ASIGNACION_{plan.registry["clock"]:g}_A{plan.registry["target"]:g}.json'
        reservation_commit = reserved['commit']
        reservation_readback = reserved['reservation_bytes_exact']
        exact_delivery = delivery['activation_bytes_exact'] and delivery['both_locks_observed_held']
        delivered_session = delivery['delivered_to_tool_session']
        observed = start['observed_start']
        proved_start = start['activation_receipt_accredited_by_observed_new_steps']
    else:
        reservation_path, reservation_commit = reserved['public_path'], reserved['registered_commit']
        reservation_readback = reserved['exact_bytes_recovered']
        exact_delivery = (delivery['delivered_atomically'] and delivery['exact_public_bytes_recovered'] and
                          delivery['both_worker_locks_held'])
        delivered_session = delivery['tool_session_id']
        observed = start['first_observed']
        proved_start = start['physical_start_observed']
    acceptance_path = f'{plan.directory}/capacidad/ACEPTACION_COMBINADA.json'
    activation_commit = git.pin(delivery['activation_commit'])
    reservation_commit = git.pin(reservation_commit)
    a = git.get(activation_commit, f'{plan.directory}/ACTIVACION.json')
    r = git.get(reservation_commit, reservation_path)
    c = git.get(reservation_commit, acceptance_path)
    acceptance = git.json(reservation_commit, acceptance_path)
    reservation = git.json(reservation_commit, reservation_path)
    require(proved_start is True and observed == plan.state['own_observed_start'] and
            exact_delivery is True and digest(a) == delivery['activation_sha256'] and
            a == git.get(plan.head, f'{plan.directory}/ACTIVACION.json') and
            reservation_readback is True and digest(r) == reserved['reservation_sha256'] and
            digest(c) == activation['capacity_acceptance_sha256'] == reservation['capacity_acceptance_sha256'] and
            acceptance['passed'] is True and
            plan.registry_sha == reservation['registry_sha256'] == activation['registry_sha256'] and
            start['tool_session_id'] == delivered_session == activation['tool_session_id'] ==
            reservation['tool_session_id'] and activation['registered_commit'] == reservation_commit and
            start['activation_commit'] == delivery['activation_commit'],
            'Los recibos históricos de reserva, activación e inicio no forman una cadena')
    if not old_boundary:
        require(activation['recovered_reservation_sha256'] == digest(r) and
                delivery['capacity_acceptance_sha256'] == digest(c) and
                delivery['registry_sha256'] == plan.registry_sha and
                (plan.registry['kind'] == 'boundary' or acceptance['registry_sha256'] == plan.registry_sha),
                'Las huellas de la entrega no coinciden con la reserva y capacidad')
    require(start.get('worker_id') == delivery.get('worker_id') == activation.get('worker_id') ==
            reservation.get('worker_id'), 'Trabajador distinto en la cadena de recibos')
    checked_audits(acceptance['native']['recovery']['original_audits'], plan.origin)
    checked_audits(acceptance['github']['recovery']['original_audits'], plan.frontier)
    first_step(observed, plan.registry)
    return dict(archive_sha256=plan.origin['sha256'], native_capacity=acceptance['native']['library_file_id'],
                public_capacity=acceptance['github']['github_asset_id'], reserved=reservation_commit,
                activation=delivery['activation_commit'], first=observed)
