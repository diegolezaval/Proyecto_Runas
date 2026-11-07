"""Ruta administrativa híbrida; reutiliza íntegros los auditores y transportes."""
from base_preservar import *
import base_preservar as original

POLICY = 'CP12_P3_HYBRID_20261106_V1'


def validate_hybrid_registry(reg):
    policy = Path(__file__).resolve().parent / 'POLITICA.json'
    if (reg.get('hybrid_policy_sha256') != sha(policy) or
            reg.get('closed_boundary', 0) < 24 or reg.get('clock', 0) < 24):
        raise ValueError('Enmienda no registrada o segmento anterior a24')


def atomic_record(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('x') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def validate_native(receipt, clock):
    if receipt.get('passed') is not True or receipt.get('observer_clock') != clock:
        raise ValueError('Transporte nativo no verificado')
    recovery = receipt.get('recovery', {})
    if (recovery.get('passed') is not True or
            recovery.get('exact_manifest_coverage') is not True or
            recovery.get('all_payload_hashes_verified_before_and_after') is not True):
        raise ValueError('Recuperación independiente incompleta')
    audits = recovery.get('original_audits', {})
    for name, count in [('boundary', 30), ('transport', 14)]:
        audit = audits.get(name, {})
        if (audit.get('passed') is not True or len(audit.get('tests', {})) != count or
                not all(audit['tests'].values()) or audit.get('M2_steps_executed') != 0 or
                audit.get('DOP853_construction_or_step_attempts') != 0):
            raise ValueError('Auditor original incompleto')
    if audits['transport']['observer_clock'] != clock:
        raise ValueError('Auditor de otro reloj')
    if not receipt.get('library_file_id') or not receipt.get('file_id'):
        raise ValueError('Identidad permanente ausente')


def rotation_plan(entries, keep=2):
    if keep not in (0, 2):
        raise ValueError('Retención no autorizada')
    ids = [item['library_file_id'] for item in entries]
    clocks = [item['observer_clock'] for item in entries]
    if len(ids) != len(set(ids)) or clocks != sorted(set(clocks)):
        raise ValueError('Registro ambiguo')
    for item in entries:
        if (item.get('execution_uuid') != UID or item.get('kind') != 'transport' or
                item.get('verified') is not True or item.get('protected') is not False):
            raise ValueError('Objeto no autorizado para rotación')
    return entries[:-keep] if keep else entries[:]


def validate_protected_origin(home, reg, incident, inherited):
    record = Path(incident['embedded_record'])
    if (len(record.parts) != 2 or record.parts[0] != 'administracion_continuacion_20261030' or
            not re.fullmatch(r'INCIDENTE_SESION_[0-9]+\.json', record.name)):
        raise ValueError('Recibo de incidente fuera de la administración canónica')
    if (reg['kind'] != 'transport' or incident.get('protected') is not True or
            incident.get('observer_clock') != reg['clock'] or
            incident.get('library_file_id') != reg['source_library_file_id'] or
            incident.get('sha256') != reg['source_archive_sha256'] or
            any(item['observer_clock'] >= reg['clock'] or
                item['library_file_id'] == incident['library_file_id'] for item in inherited)):
        raise ValueError('El rescate de incidente debe quedar fuera de la rotación')
    proof = read(home / record)
    if (sha(home / record) != incident['embedded_record_sha256'] or
            proof.get('recovery_kind') != 'protected_administrative_transport' or
            proof.get('latest_exact_local_observer_clock') != reg['clock'] or
            proof.get('exact_state_sha256') != reg['transport_sha256']):
        raise ValueError('El recibo no acredita el estado exacto del incidente')


def initialize_rotation(home, reg):
    inherited = reg.get('inherited_verified_transports', [])
    incident = reg.get('protected_incident_recovery')
    if incident is not None:
        validate_protected_origin(home, reg, incident, inherited)
    path = home / 'runtime/HIBRIDO_ROTACION.json'
    if path.exists():
        ring = read(path)
        if ring.get('schema') != POLICY or ring.get('execution_uuid') != UID:
            raise ValueError('Diario de otra política')
        rotation_plan(ring['retained'])
        if incident is not None and ring['retained'] != inherited:
            raise ValueError('La rotación previa al rescate no coincide con el registro')
        if len(ring['retained']) > 2:
            raise ValueError('Rotación incompleta: reconciliar antes de física')
        if any(x['status'] not in ('trashed',) for x in ring['retirements']):
            raise ValueError('Retirada pendiente: reconciliar antes de física')
        return
    rotation_plan(inherited)
    if len(inherited) > 2:
        raise ValueError('Reconciliar transportes anteriores antes de física')
    if (reg['kind'] == 'transport' and incident is None and
            (not inherited or inherited[-1]['observer_clock'] != reg['clock'])):
        raise ValueError('Falta identidad del transporte restaurado en la rotación')
    atomic_record(path, dict(schema=POLICY, execution_uuid=UID,
                            retained=inherited, retirements=[]))


def unwrap_management(response):
    for _ in range(8):
        if isinstance(response, dict) and isinstance(response.get('results'), list):
            return response['results']
        if isinstance(response, dict) and isinstance(response.get('structuredContent'), dict):
            response = response['structuredContent']
        elif isinstance(response, dict) and isinstance(response.get('result'), dict):
            response = response['result']
        elif isinstance(response, dict) and isinstance(response.get('content'), list):
            response = json.loads(''.join(x['text'] for x in response['content'] if x.get('type') == 'text'))
        else:
            raise ValueError('Resultado de retirada no reconocido; no repetir automáticamente')
    raise ValueError('Resultado demasiado anidado')


def retire(ring_path, ring, candidates, replacement, helpers, client_factory=None):
    """Papelera por identidad, sólo después de guardar el reemplazo verificado."""
    if not candidates:
        return
    if client_factory is None:
        sys.path.insert(0, str(helpers))
        from library_hosted_apps import HostedAppsClient
        client_factory = HostedAppsClient
    client = client_factory()
    for item in candidates:
        intent = dict(at=now(), library_file_id=item['library_file_id'], file_id=item['file_id'],
                      observer_clock=item['observer_clock'], sha256=item['sha256'],
                      replacement=replacement, status='pending_no_automatic_retry')
        ring['retirements'].append(intent)
        atomic_record(ring_path, ring)
        response = client.call_tool('connector_openai_library', 'manage_library', dict(operations=[dict(
            operation='delete', target=dict(kind='file', library_file_id=item['library_file_id']))]))
        results = unwrap_management(response)
        if len(results) != 1 or results[0].get('status') != 'succeeded':
            intent.update(status='failed_no_automatic_retry', result=results)
            atomic_record(ring_path, ring)
            raise RuntimeError('Retirada no acreditada; conservar registro y reconciliar')
        intent['status'] = 'trashed'
        ring['retained'] = [x for x in ring['retained'] if x['library_file_id'] != item['library_file_id']]
        atomic_record(ring_path, ring)


def record_transport(home, receipt, helpers, client_factory=None):
    clock = receipt['observer_clock']
    validate_native(receipt, clock)
    ring_path = home / 'runtime/HIBRIDO_ROTACION.json'
    ring = read(ring_path) if ring_path.exists() else dict(
        schema=POLICY, execution_uuid=UID, retained=[], retirements=[])
    if ring.get('schema') != POLICY or ring.get('execution_uuid') != UID:
        raise ValueError('Registro de otra política o ejecución')
    item = dict(execution_uuid=UID, kind='transport', protected=False, verified=True,
                observer_clock=clock, library_file_id=receipt['library_file_id'],
                file_id=receipt['file_id'], file_name=receipt['file_name'],
                sha256=receipt['sha256'], bytes=receipt['bytes'])
    ring['retained'].append(item)
    candidates = rotation_plan(ring['retained'])
    atomic_record(ring_path, ring)
    retire(ring_path, ring, candidates, dict(kind='newer_verified_transports',
        identities=[x['library_file_id'] for x in ring['retained'][-2:]]), helpers, client_factory)
    write(home / 'administracion_continuacion_20261030' / ('ROTACION_HIBRIDA_%06d.json' % round(clock * 10)), ring)
    return ring


def retire_at_boundary(home, saved, decision, helpers):
    """Limpia sólo transportes de esta ruta tras frontera pública y puertas."""
    if not (decision['prefix_pair_limits_met'] and decision['prefix_physical_controls_met'] and
            decision['M2_steps_executed'] == 0 and decision['physical_state_and_receipt_unchanged']):
        raise ValueError('Frontera sin puertas completas; no retirar nada')
    recovery = saved['github']['recovery']
    audit = recovery['original_audits']['boundary']
    if not (saved['passed'] and recovery['passed'] and recovery['exact_manifest_coverage'] and
            recovery['all_payload_hashes_verified_before_and_after'] and audit['passed'] and
            audit['M2_steps_executed'] == 0 and audit['DOP853_construction_or_step_attempts'] == 0):
        raise ValueError('Recuperación pública incompleta')
    if audit['state_sha256'] != sha(home / 'outputs/MIXTO_par_estado.npz'):
        raise ValueError('La cápsula no conserva la frontera actual')
    ring_path = home / 'runtime/HIBRIDO_ROTACION.json'
    if ring_path.exists():
        ring = read(ring_path)
        candidates = rotation_plan(ring['retained'], keep=0)
        if any(item['observer_clock'] >= audit['time'] for item in candidates):
            raise ValueError('El checkpoint no sustituye esos transportes')
        retire(ring_path, ring, candidates, dict(kind='full_public_boundary', time=audit['time'],
            github_asset_id=saved['github']['github_asset_id'], state_sha256=audit['state_sha256'],
            archive_sha256=saved['github']['sha256']), helpers)


def preserve(home, output, label, kind, clock, boundary, helpers, auditor, capacity=False):
    if boundary < 24:
        raise ValueError('La enmienda se aplica sólo en segmentos desde la frontera24')
    if kind != 'transport' or capacity:
        return original.preserve(home, output, label, kind, clock, boundary, helpers, auditor, capacity)
    request = prepare(home, output, label, kind, clock, boundary, capacity=False)
    temporary = native(request, output / 'transito', helpers, auditor)
    validate_native(temporary, clock)
    result = dict(schema=POLICY, passed=True, observer_clock=clock, closed_boundary=boundary,
        kind=kind, capacity_probe=False, native=temporary, github_required=False,
        scientific_frontier=False, source_archive_and_payload_unchanged=True,
        M2_steps_executed_during_preservation=0, CP12_closed=False)
    write(output / 'ACEPTACION_COMBINADA.json', result)
    ring = record_transport(home, temporary, helpers)
    write(output / 'ROTACION.json', ring)
    print(json.dumps(dict(stage='TRANSPORTE_HIBRIDO_RECUPERADO', observer_clock=clock,
        library_file_id=temporary['library_file_id'], retained=len(ring['retained']),
        github_required=False, scientific_frontier=False)), flush=True)
    return result
