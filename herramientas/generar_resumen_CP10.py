"""Vista numérica CP10 desde su resultado vigente y recibos, sin evolución."""
from pathlib import Path
import argparse
import json
import os

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'informes/RESUMEN_NUMERICO_CP10.md'
METRICS = [
    ('norm_relative_sup_error', 'Norma temporal Φ'),
    ('final_complex_nonradial_field_error_over_initial_norm', 'Φ: campo final'),
    ('final_phi_phase_space_error_over_initial_norm', 'Φ: campo y velocidad'),
    ('final_mediator_nonradial_error_over_initial_norm', 'χ: campo final'),
    ('final_mediator_phase_space_error_over_initial_norm', 'χ: campo y velocidad'),
]


def read(path):
    return json.loads(path.read_text())


def link(path, label=None):
    path = ROOT / path
    return f'[{label or path.name}]({Path(os.path.relpath(path, OUTPUT.parent)).as_posix()})'


def render():
    registry = read(ROOT / 'datos/registro_calculos.json')
    result_path = registry['authoritative_results']['nonradial']
    result = read(ROOT / result_path)
    if result.get('checkpoint') != 'CP10_MEDIADOR_ESPACIOTEMPORAL':
        raise ValueError('El registro todavía no identifica el resultado cerrado CP10')
    comparisons = {row['control']: row for row in result['comparisons']}
    temporal = comparisons['temporal_fino_h0125']
    spatial = comparisons['radial_fino_h0125_h00625']
    verdict = result['status']
    lines = ['# Resumen numérico · CP10', '',
             '> Vista generada por herramientas/generar_resumen_CP10.py. Las cifras y puertas proceden del resultado registrado; no editar esta tabla manualmente.', '',
             f'**Decisión finita: {verdict}.** Resultado fuente: {link(result_path)}.', '',
             '## Comparaciones', '',
             'En las etiquetas, h=Δr=config.dx es el paso radial; el parámetro h del potencial M2 permanece fijo.', '',
             'Núcleo r<40 y τ=160. Errores relativos a la perturbación inicial; el espacio de fases incluye la velocidad dividida por la masa del campo. Sólo se elimina la fase U(1) de Φ. χ no se alinea ni se ajusta para aceptar el ensayo.', '',
             '| Magnitud | Temporal h=.125, rtol 1e-9→1e-10 (%) | Espacial h=.125→.0625, rtol=1e-10 (%) | Puerta (%) |',
             '|---|---:|---:|---:|']
    for key, name in METRICS:
        lines.append(f"| {name} | {100*temporal[key]:.9g} | {100*spatial[key]:.9g} | {100*spatial['threshold']:.9g} |")
    lines += ['', f"Control temporal: **{'SUPERADO' if temporal['passed'] else 'NO SUPERADO'}**. Control espacial: **{'SUPERADO' if spatial['passed'] else 'NO SUPERADO'}**.", '',
              f"CSV derivado: {link(str(Path(result_path).with_name('comparaciones.csv')))}. Figura derivada: {link(str(Path(result_path).with_name('CP10_errores_mediador.svg')))}.", '',
              '## Balances de las dos evoluciones nuevas', '',
              '| Caso | Deriva relativa E | Deriva relativa Q | Cambio relativo Q del núcleo | Amplificación máxima | Balance/retención |',
              '|---|---:|---:|---:|---:|---|']
    for gate in result['run_gates']:
        record = result['records'][gate['case']]
        lines.append(f"| {gate['case']} | {record['relative_energy_drift']:.9g} | {record['relative_charge_drift']:.9g} | {record['relative_core_charge_change']:.9g} | {record['max_amplification']:.9g} | {'SUPERADO' if gate['passed'] else 'NO SUPERADO'} |")
    lines += ['', 'Los umbrales completos están en el protocolo capturado. Conservar balances no sustituye superar las comparaciones de campo.', '',
              '## Segmentos y estados recuperados', '',
              '| Caso/segmento | Estado del segmento | Inicio UTC | Cierre o detección UTC | τ final guardado/recuperado |',
              '|---|---|---|---|---:|']
    receipt_links = []
    for gate in result['run_gates']:
        receipt = read(ROOT / gate['receipt'])
        if receipt['status'] != 'COMPLETADA':
            raise ValueError('Recibo no cerrado')
        for number, segment in enumerate(receipt['segments'], 1):
            stop = segment.get('ended_at', segment.get('interruption_detected_at', ''))
            tau = segment.get('final_time', segment.get('recovered_time', ''))
            lines.append(f"| {gate['case']}/{number} | {segment['status']} | {segment['started_at']} | {stop} | {tau} |")
        receipt_links.append(f"Recibo {gate['case']}: {link(gate['receipt'])}. Estado final: {link(next(row['right'] for row in result['comparisons'] if row['right'].startswith(str(Path(gate['receipt']).parent))))}.")
    lines += ['', *receipt_links, '', 'La detección de una interrupción no fija su instante exacto. Los recibos conservan los hashes del piloto y de los estados válidos desde los que se reanudó; no se repitió la preparación ni se inició otra vez desde τ=0.', '',
              '## Distribución del error de χ en el nuevo control espacial', '',
              'Fracciones de la diferencia cuadrática en espacio de fases; no son fracciones de energía física.', '',
              '| Banda radial | Fracción (%) |', '|---|---:|']
    for band in spatial['chi_radial_bands']:
        lines.append(f"| {band['r_min']}≤r<{band['r_max']} | {100*band['fraction_of_chi_squared_difference']:.9g} |")
    lines += ['', '| ℓ | Fracción (%) |', '|---|---:|']
    for ell, fraction in spatial['chi_multipole_fractions'].items():
        lines.append(f'| {ell} | {100*fraction:.9g} |')
    lines += ['', '## Alcance de la decisión', '', result['scope'], '',
              'Los controles de caja, truncación angular y otras perturbaciones heredados conservan sus resoluciones históricas. No son una prueba conjunta en las nuevas mallas. La fuente de Cauchy procede de la preparación radial h=.1 de CP04; interpolarla a una malla más fina no certifica la resolución del estado fuente.', '',
              'E03/E04/RES0/RES1 siguen PARCIALES. No se establece estabilidad orbital o continua, causa certificada del error, preparación primaria, apagado, retroacción, ciclo ni dispositivo. Los resultados negativos CP06–CP08 y el fallo de la nueva puerta, cuando corresponda, permanecen conservados.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comprobar', action='store_true')
    args = parser.parse_args()
    content = render()
    if args.comprobar:
        passed = OUTPUT.is_file() and OUTPUT.read_text() == content
    else:
        OUTPUT.write_text(content)
        passed = True
    print(json.dumps(dict(passed=passed, generated_view=OUTPUT.relative_to(ROOT).as_posix(), integrations_executed=False)))
    raise SystemExit(0 if passed else 1)
