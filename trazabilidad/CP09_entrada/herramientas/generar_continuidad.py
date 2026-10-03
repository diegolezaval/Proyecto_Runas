"""Genera vistas de continuidad y trazabilidad sin ejecutar ciencia.

El progreso y las conclusiones se leen de sus autoridades. Los hashes nuevos
identifican el snapshot presente; no se atribuyen al momento de ejecución.
"""
from pathlib import Path
import argparse
import fnmatch
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX = 'trazabilidad/arquitectura/indice_trazabilidad.json'


def read(path, root=ROOT):
    return json.loads((root / path).read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def role(path, config):
    if path.startswith(('trazabilidad/', 'hoja_ruta_original/')):
        return 'antecedente_o_instantanea'
    if path in config.get('historical_notes', {}) or path == 'tratado/19_resultados_edicion4.md':
        return 'documento_historico_contextualizado'
    for view in config['generated_views']:
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in view['outputs']):
            return 'vista_o_informe_generado'
    if path == 'datos/linaje_afirmaciones.json':
        return 'linaje_inicial_E00_conservado'
    if path.startswith('herramientas/'):
        return 'codigo_o_herramienta'
    if path.startswith('validacion/'):
        if path.endswith('.npz'):
            return 'estado_numerico_o_intento'
        if path.endswith('.log'):
            return 'registro_de_ejecucion'
        return 'resultado_o_diagnostico'
    if path.startswith('datos/'):
        return 'fuente_o_protocolo_JSON'
    if path.startswith('tratado/'):
        return 'capitulo_fuente'
    if path.startswith('graficos/'):
        return 'figura_generada'
    if path.startswith('informes/'):
        return 'informe_de_entrega'
    return 'documentacion_o_continuidad'


def render_state(root=ROOT):
    state = read('estado_progreso.json', root)
    registry = read('datos/registro_calculos.json', root)
    current = state.get('scientific_checkpoint', state['checkpoint'])
    completed = ', '.join(s['id'] for s in state['stages'] if s['status'] == 'COMPLETADA') or 'Ninguna'
    partial = ', '.join(s['id'] for s in state['stages'] if s['status'] == 'PARCIAL') or 'Ninguna'
    latest_nonradial = read(registry['authoritative_results']['nonradial'], root)
    lines = [f"# Estado actual · {state['checkpoint']}", '',
             '> Vista generada por herramientas/generar_continuidad.py. Editar las fuentes JSON; no este archivo.', '',
             f"Proyecto: **{state['project_version']}**. Modelo: **{state['model_version']}**. Último checkpoint científico: **{current}**.", '',
             f"**Completadas:** {completed}. **Parciales:** {partial}.", '',
             f"**Puerta no radial vigente:** {latest_nonradial['status']}. **Cálculos numéricos activos:** {len(state.get('numerical_runs_in_progress', []))}. **Primordiales/dispositivos completos:** {state['complete_primordials']}.", '',
             'La auditoría administrativa no cambia las etapas ni sus puertas. La evidencia reproducible prevalece ante una discrepancia documental.', '',
             '## Siguiente trabajo científico', '']
    lines += ['- ' + action for action in state['next_actions']]
    lines += ['', '## Estados de origen y continuación', '']
    labels = {'restart_state': 'Estado CP04 terminado de origen para nuevas perturbaciones',
              'latest_completed_nonradial_state': 'Último estado no radial terminado; no repetir ni prolongar sin protocolo nuevo',
              'diagnostic_after_gate': 'Diagnóstico guardado después de la puerta'}
    for name, label in labels.items():
        if state.get(name):
            path = state[name]
            lines.append(f'- {label}: [{path}]({path}).')
    if 'latest_completed_nonradial_time' in state:
        lines.append(f"- Tiempo no radial final registrado: {state['latest_completed_nonradial_time']}.")
    lines += ['', '## Qué no repetir', '']
    lines += ['- ' + item for item in state['do_not_repeat']]
    lines += ['', '## Resultados vigentes y límites', '']
    shown = set()
    for name, path in registry['authoritative_results'].items():
        if path in shown:
            continue
        shown.add(path)
        result = read(path, root)
        status = result.get('status', result.get('gate_decision', 'Alcance en el archivo fuente'))
        if isinstance(status, (dict, list)):
            status = 'Consultar resultado fuente'
        lines.append(f'- {name}: [{path}]({path}) — {status}.')
    lines += ['', '## Etapas y puertas', '', '| Etapa | Estado | Puerta registrada |', '|---|---|---|']
    for stage in state['stages']:
        gate = stage.get('gate_decision', 'Cierre histórico conservado' if stage['status'] == 'COMPLETADA' else 'Consultar expediente')
        lines.append(f"| {stage['id']} | {stage['status']} | {gate.replace('|', '/')} |")
    latest = state['history'][-1]['report']
    lines += ['', f'Informe de esta entrega: [{latest}]({latest}).', '',
              f'Índice derivado de trazabilidad: [{INDEX}]({INDEX}).', '',
              'Entrada y comandos: [LEEME.md](LEEME.md). Autoridad y límites: [ARQUITECTURA.md](ARQUITECTURA.md).', '']
    return '\n'.join(lines)


def build_index(root=ROOT):
    config = read('datos/arquitectura.json', root)
    state = read('estado_progreso.json', root)
    science = read('datos/estado_evidencia.json', root)
    registry = read('datos/registro_calculos.json', root)
    initial = {x['claim']: x for x in read('datos/linaje_afirmaciones.json', root)['claims']}
    claims = []
    all_paths = set()
    for claim in science['claims']:
        old = initial.get(claim['id'], {})
        extra = config['claim_links'].get(claim['id'], {})
        groups = {
            'equations': extra.get('equations', [old['action']] if old.get('action') else [x for x in claim['evidence'] if x.endswith('.md')]),
            'parameters': extra.get('parameters', ['datos/parametros.json'] if claim['id'] == 'R1' else ['datos/theta_comun.json']),
            'scripts': sorted(set(old.get('scripts', []) + extra.get('scripts', []))),
            'evidence': claim['evidence'],
            'configurations': extra.get('configurations', []),
            'data': extra.get('data', []),
            'figures': extra.get('figures', []),
            'gates': extra.get('gates', [])
        }
        expanded = {}
        for category, patterns in groups.items():
            expanded[category] = sorted(set(str(p.relative_to(root)) for pattern in patterns
                                            for p in root.glob(pattern) if p.is_file()))
            for pattern in patterns:
                if not any(p.is_file() for p in root.glob(pattern)):
                    raise ValueError(f"Enlace ausente para {claim['id']} / {category}: {pattern}")
            all_paths.update(expanded[category])
        stages = [s['id'] for s in state['stages'] if set(s['evidence']) & set(claim['evidence'])]
        claims.append(dict(id=claim['id'], assertion=claim['assertion'], classification=claim['classification'],
                           scope=claim['scope'], not_established=claim['not_established'],
                           historical_status=claim.get('historical_status'), links=expanded, stages=stages,
                           links_basis=extra.get('basis', 'Linaje inicial E00 y evidencia vigente; sin nuevo recibo de ejecución.')))
    for prefix in ['datos', 'tratado', 'herramientas', 'validacion', 'graficos', 'fichas']:
        all_paths.update(str(p.relative_to(root)) for p in (root / prefix).rglob('*')
                         if p.is_file() and '__pycache__' not in p.parts and 'cache' not in p.parts
                         and not p.is_relative_to(root / 'validacion/arquitectura')
                         and p.suffix not in ['.pyc', '.lock', '.tmp'])
    artifacts = []
    for path in sorted(all_paths):
        f = root / path
        users = [c['id'] for c in claims if any(path in values for values in c['links'].values())]
        generators = [v['generator'] for v in config['generated_views']
                      if any(fnmatch.fnmatchcase(path, x) for x in v['outputs'])]
        claim_categories = {c['id']: [category for category, values in c['links'].items() if path in values]
                            for c in claims if c['id'] in users}
        campaigns = []
        for name, result_path in registry['authoritative_results'].items():
            folder = Path(result_path).parent
            if folder != Path('validacion') and Path(path).is_relative_to(folder):
                campaigns.append(dict(registry_role=name, authoritative_result=result_path))
        readers = [v['generator'] for v in config['generated_views']
                   if any(fnmatch.fnmatchcase(path, pattern) for pattern in v['inputs'])]
        stage_users = [s['id'] for s in state['stages'] if path in s['evidence']]
        artifacts.append(dict(path=path, role=role(path, config), bytes=f.stat().st_size,
                              snapshot_sha256=sha(f), used_by_claims=users,
                              claim_link_categories=claim_categories,
                              stage_evidence_for=stage_users,
                              stored_with_campaign_results=campaigns,
                              read_by_declared_generators=readers,
                              declared_generators=generators))
    return dict(schema_version=config['schema_version'], checkpoint=state['checkpoint'],
                scientific_checkpoint=state.get('scientific_checkpoint', state['checkpoint']),
                authority='Vista derivada; fuentes: evidencia, progreso, linaje inicial y metadatos de arquitectura.',
                provenance_limit='snapshot_sha256 identifica bytes actuales, no Θ/código capturados durante corridas antiguas. Los enlaces por familia no certifican causalidad de ejecución.',
                relationship_limit='stored_with_campaign_results agrupa por carpeta de un resultado vigente; no declara que cada archivo respalde su conclusión. Las categorías de enlaces distinguen evidencia explícita de asociación documental/familiar.',
                generators=config['generated_views'], claims=claims, artifacts=artifacts,
                artifacts_without_direct_claim=[x['path'] for x in artifacts if not x['used_by_claims']],
                known_unreadable_artifacts=config['known_unreadable_artifacts'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comprobar', action='store_true', help='Comprobar vistas sin escribir')
    args = parser.parse_args()
    outputs = {'ESTADO_ACTUAL.md': render_state(), INDEX: json.dumps(build_index(), ensure_ascii=False, indent=2) + '\n'}
    stale = []
    for path, content in outputs.items():
        target = ROOT / path
        if args.comprobar:
            if not target.exists() or target.read_text(encoding='utf-8') != content:
                stale.append(path)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
    print(json.dumps(dict(passed=not stale, stale=stale, written=[] if args.comprobar else list(outputs)), ensure_ascii=False))
    if stale:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
