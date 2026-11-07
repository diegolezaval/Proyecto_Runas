"""Capacidad propia de un reinicio nativo con una referencia pública separada."""
import importlib.util
import json
import time

import preservar as p


MODE = 'CP12_P3_HYBRID_SPLIT_CAPACITY_V1'


def prepare_public_reference(archive, output, label, reg, auditor):
    reference = reg['public_capacity_reference']
    boundary = reg['closed_boundary']
    if (archive.name != reference['file_name'] or reference['observer_clock'] != boundary or
            reference['kind'] != 'boundary' or reference['github_asset_id'] <= 0):
        raise ValueError('Referencia pública distinta de la frontera registrada')

    spec = importlib.util.spec_from_file_location('original_P3_unpack', auditor)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    home = output / 'referencia_extraida'
    manifest = driver.unpack(archive, home, reference['sha256'], reference['bytes'])
    if (manifest['kind'] != 'boundary' or manifest['observer_clock'] != boundary or
            manifest['closed_boundary'] != boundary or manifest['capacity_probe'] is not False):
        raise ValueError('La referencia exige una cápsula pública de frontera completa')

    request = p.prepare(home, output / 'publico', 'CONTROL_PUBLICO_' + label,
                        'boundary', boundary, boundary, capacity=True)
    audit = request['local_audits']['boundary']
    if (request['source_inventory'] != manifest['files'] or
            audit['state_sha256'] != reg['closed_state_sha256'] or
            audit['configuration_sha256'] != reg['configuration_sha256'] or
            audit['receipt_sha256'] != reg['receipt_sha256']):
        raise ValueError('Referencia pública ajena a la frontera del transporte')
    return request


def preserve_capacity(home, output, reg, registration, reference_archive, helpers, auditor):
    if reg.get('capacity_mode') != MODE or reg['kind'] != 'transport':
        raise ValueError('Capacidad separada sin registro de origen nativo')
    output.mkdir()
    label = reg['allocation_id'].upper()
    boundary, clock = reg['closed_boundary'], reg['clock']
    public_request = prepare_public_reference(reference_archive, output, label, reg, auditor)

    private = output / 'nativo'
    native_request = p.prepare(home, private, 'CONTROL_NATIVO_' + label,
                               'transport', clock, boundary, capacity=True)
    native = p.native(native_request, private / 'transito', helpers, auditor)
    p.validate_native(native, clock)
    transport = native['recovery']['original_audits']['transport']
    if transport['state_sha256'] != reg['transport_sha256']:
        raise ValueError('La capacidad nativa recuperó un transporte distinto')

    public_dir = output / 'publico'
    print(json.dumps(dict(stage='PUBLICACION_GITHUB_REQUERIDA', capacity_mode=MODE,
        request=str(public_dir / 'SOLICITUD.json'), archive=public_request['archive_path'],
        bytes=public_request['bytes'], sha256=public_request['sha256'], observer_clock=boundary)), flush=True)
    metadata_path = public_dir / 'ASSET_GITHUB.json'
    deadline = time.monotonic() + 3600
    while not metadata_path.exists():
        if time.monotonic() > deadline:
            raise TimeoutError('Publicación de referencia pendiente, sin física nueva')
        time.sleep(.5)
    public = p.public(public_request, p.read(metadata_path), public_dir / 'github', auditor)
    if public['github_asset_id'] == reg['public_capacity_reference']['github_asset_id']:
        raise ValueError('La capacidad pública exige un adjunto nuevo')
    public_audit = public['recovery']['original_audits']['boundary']
    if len(public_audit['tests']) != 30 or not all(public_audit['tests'].values()):
        raise ValueError('Faltan controles originales en la referencia pública')
    p.unchanged(native_request)
    result = dict(schema=MODE, passed=True, registry_sha256=p.sha(registration),
        observer_clock=clock, closed_boundary=boundary, kind='transport', capacity_probe=True,
        native=native, github=public, public_capacity_reference=reg['public_capacity_reference'],
        public_contains_only_previously_public_frontier_and_capacity_metadata=True,
        source_archive_and_payload_unchanged=True, M2_steps_executed_during_preservation=0,
        CP12_closed=False)
    p.write(output / 'ACEPTACION_COMBINADA.json', result)
    return result
