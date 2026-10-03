"""Audita referencias, estados y conservación sin evolucionar campos.

Los NPZ fallidos siguen incluidos. Sólo una excepción documentada por ruta y
hash puede conservarse como ilegible; nunca cuenta como estado reanudable.
"""
from pathlib import Path
import argparse
import ast
import json
import re
import xml.etree.ElementTree as ET
import numpy as np
from generar_continuidad import read, sha, build_index, render_state, INDEX
from rutas_documentales import missing_links
from checkpoint import files, validate_context

ROOT = Path(__file__).resolve().parents[1]


def walk(value, pointer=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, pointer + '/' + str(key))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, pointer + '/' + str(i))
    elif isinstance(value, str):
        yield pointer, value


def inspect_states(root=ROOT):
    config = read('datos/arquitectura.json', root)
    known = {x['path']: x for x in config['known_unreadable_artifacts']}
    rows, issues = [], []
    for path in sorted((root / 'validacion').rglob('*.npz')):
        relative = str(path.relative_to(root))
        item = dict(path=relative, bytes=path.stat().st_size, snapshot_sha256=sha(path),
                    runtime_code_theta_hashes_not_uniformly_recorded=True)
        try:
            with np.load(path, allow_pickle=False) as data:
                item['keys'] = data.files
                item['arrays'] = {}
                item['metadata'] = {}
                for key in data.files:
                    value = data[key]
                    array = dict(shape=list(value.shape), dtype=str(value.dtype))
                    if value.dtype.kind in 'biufc':
                        array['finite'] = bool(np.isfinite(value).all())
                        if not array['finite']:
                            issues.append(relative + ':' + key + ':nonfinite')
                    item['arrays'][key] = array
                    if value.shape == () and key in ['time', 'step', 'config', 'transfer', 'implementations']:
                        decoded = value.item()
                        if isinstance(decoded, str):
                            decoded = json.loads(decoded)
                        item['metadata'][key] = decoded
                metadata = item['metadata']
                failed_observation = path.name.endswith('_estado_fallido.npz')
                suffix = '_estado_fallido.npz' if failed_observation else '_estado.npz'
                tag = path.name.removesuffix(suffix)
                companion = path.with_name(tag + ('_puerta_fallida.json' if failed_observation else '.json'))
                progress = path.with_name(tag + '_progreso.json')
                item['companion_result'] = str(companion.relative_to(root)) if companion.is_file() else None
                if companion.is_file():
                    result = json.loads(companion.read_text())
                    if 'configuration' in result and 'config' in metadata and result['configuration'] != metadata['config']:
                        issues.append(relative + ':configuration_mismatch')
                    item['result_passed_if_recorded'] = result.get('passed')
                if failed_observation:
                    item['role'] = 'FALLO_NUMERICO_NO_REANUDAR'
                elif progress.is_file():
                    progress_data = json.loads(progress.read_text())
                    item['progress'] = progress_data
                    if progress_data['status'] == 'CALCULO_TERMINADO':
                        item['role'] = 'CALCULO_TERMINADO_NO_REPETIR'
                        cfg = metadata['config']
                        final_time = metadata.get('time', metadata.get('step', 0) * cfg.get('dt', 0))
                        item['saved_time'] = final_time
                        if abs(final_time - cfg['tmax']) > 1e-9:
                            issues.append(relative + ':incomplete_completed_state')
                    else:
                        item['role'] = 'PILOTO_O_ESTADO_PARCIAL_ARCHIVADO'
                elif companion.is_file() and result.get('success') is False:
                    item['role'] = 'INTENTO_FALLIDO_NO_REANUDAR'
                else:
                    item['role'] = 'SOLUCION_GUARDADA_CON_JSON_COMPANERO'
                transfer = metadata.get('transfer', {})
                if transfer.get('source') and transfer.get('source_sha256'):
                    source = root / transfer['source']
                    item['recorded_source_hash_verified'] = source.is_file() and sha(source) == transfer['source_sha256']
                    if not item['recorded_source_hash_verified']:
                        issues.append(relative + ':source_hash_mismatch')
                item['readable'] = True
        except Exception as error:
            item.update(readable=False, error=str(error), role='ILEGIBLE_NO_REANUDABLE')
            exception = known.get(relative)
            result = read(exception['result'], root) if exception else {}
            documented = bool(exception and exception['sha256'] == item['snapshot_sha256']
                              and result.get('success') is False and result.get('passed') is False)
            item['documented_historical_failure'] = documented
            if not documented:
                issues.append(relative + ':unexpected_unreadable_state')
        rows.append(item)
    return rows, issues


def preservation(root=ROOT):
    baseline = read('trazabilidad/arquitectura/archivos_CP08.json', root)
    archive = root / 'trazabilidad/CP08_arquitectura_entrada'
    changed, missing, unrecoverable = [], [], []
    for relative, expected in baseline.items():
        current = root / relative
        if not current.is_file():
            missing.append(relative)
        elif sha(current) != expected:
            changed.append(relative)
            old = archive / relative
            if not old.is_file() or sha(old) != expected:
                unrecoverable.append(relative)
    historical_state = read('trazabilidad/CP08_arquitectura_entrada/estado_progreso.json', root)
    state = read('estado_progreso.json', root)
    scientific_prefixes = ['validacion/', 'tratado/', 'graficos/', 'fichas/', 'hoja_ruta_original/']
    science_changed = [x for x in changed if x.startswith(tuple(scientific_prefixes)) or x.startswith('datos/')]
    return dict(passed=not missing and not unrecoverable and not science_changed and state['stages'] == historical_state['stages'],
                original_files=len(baseline), modified_existing=changed, missing=missing,
                unrecoverable_originals=unrecoverable, scientific_files_changed=science_changed,
                stage_records_identical=state['stages'] == historical_state['stages'],
                archived_files_recover_original_CP08=True if not missing and not unrecoverable else False)


def audit(root=ROOT, conserve=False):
    issues = []
    counts = dict(json=0, python=0, svg=0)
    payload = files(root)
    for path in payload:
        try:
            if path.suffix == '.json':
                json.loads(path.read_text(encoding='utf-8'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
                counts['json'] += 1
            elif path.suffix == '.py':
                ast.parse(path.read_text(encoding='utf-8'))
                counts['python'] += 1
            elif path.suffix == '.svg':
                ET.parse(path)
                counts['svg'] += 1
        except Exception as error:
            issues.append(str(path.relative_to(root)) + ':' + str(error))
    issues += missing_links(root)
    validate_context()
    state = read('estado_progreso.json', root)
    science = read('datos/estado_evidencia.json', root)
    registry = read('datos/registro_calculos.json', root)
    scientific_checkpoint = state.get('scientific_checkpoint', state['checkpoint'])
    if science['current_checkpoint'] != scientific_checkpoint or registry['checkpoint'] != scientific_checkpoint:
        issues.append('scientific_checkpoint_mismatch')
    for key in ['numerical_runs_in_progress', 'latest_completed_nonradial_state', 'latest_completed_nonradial_time']:
        if state.get(key) != registry.get(key):
            issues.append('progress_registry_mismatch:' + key)
    for field in ['restart_state', 'latest_completed_nonradial_state', 'diagnostic_after_gate']:
        if state.get(field) and not (root / state[field]).is_file():
            issues.append('missing_continuation:' + field)
    for stage in state['stages']:
        if not isinstance(stage['dependencies'], list) or not stage['gate_original']:
            issues.append('missing_stage_contract:' + stage['id'])
    initial_state = read('trazabilidad/reanudacion_CP02/estado_progreso.json', root)
    cp08 = read('trazabilidad/CP08_arquitectura_entrada/estado_progreso.json', root)
    for name, context in [('E00', initial_state), ('E01', initial_state), ('C0', cp08)]:
        old = next(x for x in context['stages'] if x['id'] == name)
        now = next(x for x in state['stages'] if x['id'] == name)
        if old != now and not now.get('reopening_reason'):
            issues.append(name + ':changed_without_reopening_reason')
    index = build_index(root)
    if (root / 'ESTADO_ACTUAL.md').read_text(encoding='utf-8') != render_state(root):
        issues.append('stale_generated_state')
    if read(INDEX, root) != index:
        issues.append('stale_generated_trace_index')
    states, state_issues = inspect_states(root)
    issues += state_issues
    report = dict(checkpoint=state['checkpoint'], passed=not issues, issues=issues, counts=counts,
                  claims_indexed=len(index['claims']), states_inspected=len(states),
                  readable_states=sum(x['readable'] for x in states),
                  preserved_unreadable_states=[x['path'] for x in states if not x['readable']],
                  numerical_campaigns_executed=False, state_details=states,
                  scope='Integridad documental, metadatos y diagnóstico de estados incluidos; no certificación científica.')
    if conserve:
        report['conservation_CP08'] = preservation(root)
        report['passed'] = report['passed'] and report['conservation_CP08']['passed']
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, help='Guardar el informe en una ruta explícita')
    parser.add_argument('--conservacion-cp08', action='store_true', help='Exigir conservación científica en la entrega administrativa CP09')
    args = parser.parse_args()
    try:
        result = audit(conserve=args.conservacion_cp08)
    except Exception as error:
        result = dict(passed=False, error=str(error))
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'state_details'}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
