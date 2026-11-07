"""Compara controles P3 con frontera y registro públicos ya recuperados; cero M2."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('control', 'publico', 'repositorio', 'salida'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('sha-control', 'sha-publico', 'commit-publico', 'registro-publico', 'ejecutor-publico'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--publico-asset-id', type=int, required=True)
    args = parser.parse_args()
    if not all(re.fullmatch('[0-9a-f]{64}', x) for x in (args.sha_control, args.sha_publico)):
        raise ValueError('Se exigen hashes SHA256 completos')
    if not re.fullmatch('[0-9a-f]{40}', args.commit_publico):
        raise ValueError('Se exige un commit completo ya recuperado públicamente')
    for value in (args.registro_publico, args.ejecutor_publico):
        path = PurePosixPath(value)
        if path.is_absolute() or '..' in path.parts or '\\' in value or not value.startswith('checkpoints/CP12/p3_20261018/'):
            raise ValueError('Referencia fuera de la línea P3')
    def git_bytes(relative):
        return subprocess.check_output(['git', 'show', args.commit_publico + ':' + relative], cwd=args.repositorio)
    registry_bytes = git_bytes(args.registro_publico)
    registry = json.loads(registry_bytes)
    clock = registry['closed_boundary']
    separate = registry.get('capacity_mode') == 'CP12_P3_HYBRID_SPLIT_CAPACITY_V1'
    if separate:
        reference = registry['public_capacity_reference']
        if (registry['kind'] != 'transport' or reference['kind'] != 'boundary' or
                reference['observer_clock'] != clock or reference['sha256'] != args.sha_publico or
                reference['github_asset_id'] != args.publico_asset_id or
                reference['bytes'] != args.publico.stat().st_size or reference['file_name'] != args.publico.name):
            raise ValueError('Referencia separada distinta del registro')
    elif (registry['kind'] != 'boundary' or registry['clock'] != clock or
            registry['source_archive_sha256'] != args.sha_publico):
        raise ValueError('El registro no continúa esa frontera pública')
    if clock % 8 or clock < 24:
        raise ValueError('Control ajeno a una frontera cerrada habilitada')
    if file_sha(args.control) != args.sha_control or file_sha(args.publico) != args.sha_publico:
        raise ValueError('Las referencias no coinciden con las identidades declaradas')
    allocation = registry['allocation_id']
    if not re.fullmatch('[a-z0-9_]+', allocation):
        raise ValueError('Asignación no canónica')
    admin = 'administracion_continuacion_20261030/' + allocation + '/'
    label = 'CONTROL_PUBLICO_' if separate else 'CONTROL_'
    ancestor = 'ancestor/continuidad_20261030/' + label + allocation.upper() + '_MANIFIESTO_ORIGEN.json'
    filler_path = 'administracion_continuacion_20261030/CAPACIDAD.bin'
    filler_description = 'administracion_continuacion_20261030/CAPACIDAD.json'
    seed = b'RUNICA_P3_FORWARD_CAPACITY_20261030'
    filler = b''.join(hashlib.sha256(seed + i.to_bytes(8, 'big')).digest() for i in range(32768))
    filler_meta = json.dumps(dict(scientific_data=False, bytes=1048576, seed=seed.decode(),
        algorithm='Concatenate SHA256(seed + uint64_be(i)), i=0..32767', M2_steps_executed=0)).encode()
    counts = Counter()
    with zipfile.ZipFile(args.publico) as public, zipfile.ZipFile(args.control) as control:
        names = control.namelist()
        public_names = set(public.namelist())
        manifest = json.loads(control.read('MANIFIESTO_NEGATIVO.json'))
        if len(names) != len(set(names)) or set(names) != set(manifest['files']) | {'MANIFIESTO_NEGATIVO.json'}:
            raise ValueError('Cobertura no canónica')
        expected = dict(schema='CP12_P3_FORWARD_CAPSULE_V2', kind='boundary', observer_clock=clock,
            closed_boundary=clock, capacity_probe=True, CP12_closed=False, correction_validated=False,
            stale_internal_transport_forensic_only=True)
        if {k: v for k, v in manifest.items() if k != 'files'} != expected:
            raise ValueError('Metadatos del control distintos del protocolo')
        for name in names:
            data = control.read(name)
            if name == 'MANIFIESTO_NEGATIVO.json':
                counts['derived_inventory_only'] += 1
                continue
            entry = manifest['files'][name]
            if len(data) != entry['bytes'] or sha(data) != entry['sha256']:
                raise ValueError('Carga no íntegra: ' + name)
            if name in public_names:
                valid, category = data == public.read(name), 'exact_public_frontier_payload'
            elif not separate and name.startswith(admin):
                short = name[len(admin):]
                if '/' in short or short.startswith('.'):
                    raise ValueError('Ruta administrativa no canónica')
                if short == 'REGISTRO.json':
                    valid = data == registry_bytes
                else:
                    expected_hash = registry['administrative_sources'].get(short)
                    valid = bool(expected_hash) and sha(data) == expected_hash and data == git_bytes(args.ejecutor_publico + '/' + short)
                category = 'exact_public_git_payload'
            elif name == ancestor:
                valid, category = data == public.read('MANIFIESTO_NEGATIVO.json'), 'exact_public_frontier_inventory'
            elif name == filler_path:
                valid, category = data == filler, 'deterministic_public_algorithm_filler'
            elif name == filler_description:
                valid, category = data == filler_meta, 'deterministic_filler_description'
            else:
                raise ValueError('Entrada sin clasificar: ' + name)
            if not valid:
                raise ValueError('Bytes distintos de la referencia: ' + name)
            counts[category] += 1
        if not public_names - {'MANIFIESTO_NEGATIVO.json'} <= set(names):
            raise ValueError('Faltan cargas originales')
        if separate and set(names) != public_names | {ancestor, filler_path, filler_description}:
            raise ValueError('Inventario de la capacidad separada distinto')
    result = dict(schema='CP12_P3_REUSABLE_PUBLIC_CONTROL_COMPARISON_V1', passed=True,
        control_bytes=args.control.stat().st_size, control_sha256=args.sha_control,
        public_frontier_asset_id=args.publico_asset_id, public_frontier_sha256=args.sha_publico,
        compared_public_git_commit=args.commit_publico, registry_public_path=args.registro_publico,
        allocation_id=allocation, separate_public_capacity=separate,
        classification_counts=dict(counts), unclassified_entries=0,
        M2_steps_executed=0, approval_inferred_from_this_comparison=False,
        scope='Igualdad de bytes;el operador debe haber recuperado las referencias públicas previamente. No concede permisos.')
    args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
