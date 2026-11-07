"""Clasifica todos los bytes del control contra material público; no importa física."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    for name in ('control', 'publico', 'repositorio', 'salida'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    assert digest(args.control.read_bytes()) == '4e0f5733635d3ab049e67a958bea4429e5b496bf541bf53d923171fe37b6c3c0'
    assert digest(args.publico.read_bytes()) == '13660aae72467ccb2eda738d773103c8b14cb1950f4ed84a959cfb6f3f10fed6'
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.repositorio, text=True).strip()
    assert commit == 'a975d0328daaea41ebeb6f91cef802c01714af5a'
    seed = b'RUNICA_P3_FORWARD_CAPACITY_20261030'
    filler = b''.join(hashlib.sha256(seed + i.to_bytes(8, 'big')).digest() for i in range(32768))
    metadata = json.dumps(dict(scientific_data=False, bytes=1048576, seed=seed.decode(),
        algorithm='Concatenate SHA256(seed + uint64_be(i)), i=0..32767', M2_steps_executed=0)).encode()
    admin = 'administracion_continuacion_20261030/p3_24_a32_hibrido_20261106/'
    repo_base = 'checkpoints/CP12/p3_20261018/'
    counts = Counter()
    additions = []
    with zipfile.ZipFile(args.publico) as public, zipfile.ZipFile(args.control) as control:
        names = control.namelist()
        assert len(names) == len(set(names))
        public_names = set(public.namelist())
        manifest = json.loads(control.read('MANIFIESTO_NEGATIVO.json'))
        assert set(names) == set(manifest['files']) | {'MANIFIESTO_NEGATIVO.json'}
        assert {k: v for k, v in manifest.items() if k != 'files'} == dict(
            schema='CP12_P3_FORWARD_CAPSULE_V2', kind='boundary', observer_clock=24,
            closed_boundary=24, capacity_probe=True, CP12_closed=False,
            correction_validated=False, stale_internal_transport_forensic_only=True)
        for name in names:
            data = control.read(name)
            if name == 'MANIFIESTO_NEGATIVO.json':
                counts['derived_inventory_only'] += 1
                continue
            expected = manifest['files'][name]
            assert len(data) == expected['bytes'] and digest(data) == expected['sha256']
            if name in public_names:
                assert data == public.read(name)
                counts['exact_public_frontier_payload'] += 1
            elif name.startswith(admin):
                short = name[len(admin):]
                assert '/' not in short
                relative = (repo_base + 'reanudacion_hibrida_t24_20261106/REGISTRO.json' if short == 'REGISTRO.json'
                    else repo_base + 'conservacion_hibrida_20261106/ejecutor/' + short)
                existing = subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=args.repositorio)
                assert data == existing
                counts['exact_public_git_payload'] += 1
                additions.append(dict(path=name, public_git_path=relative, sha256=digest(data)))
            elif name == 'ancestor/continuidad_20261030/CONTROL_P3_24_A32_HIBRIDO_20261106_MANIFIESTO_ORIGEN.json':
                assert data == public.read('MANIFIESTO_NEGATIVO.json')
                counts['exact_public_frontier_inventory'] += 1
            elif name == 'administracion_continuacion_20261030/CAPACIDAD.bin':
                assert data == filler
                counts['deterministic_public_algorithm_filler'] += 1
            elif name == 'administracion_continuacion_20261030/CAPACIDAD.json':
                assert data == metadata
                counts['deterministic_filler_description'] += 1
            else:
                raise ValueError('Unclassified bytes: ' + name)
        assert public_names - {'MANIFIESTO_NEGATIVO.json'} <= set(names)
    result = dict(schema='CP12_P3_CAPACITY_CONTROL_PUBLIC_CONTENT_COMPARISON_V1', passed=True,
        control_bytes=args.control.stat().st_size, control_sha256=digest(args.control.read_bytes()),
        public_frontier_asset_id=718257706, public_frontier_sha256=digest(args.publico.read_bytes()),
        compared_public_git_commit=commit, classification_counts=dict(counts),
        exact_public_git_additions=additions, unclassified_entries=0,
        private_runtime_directories_or_logs_included=False, M2_steps_executed=0,
        purpose='Evidence for review of the same unchanged capacity archive; not a scientific frontier.',
        approval_inferred_from_this_comparison=False)
    args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'exact_public_git_additions'}))


if __name__ == '__main__':
    main()
