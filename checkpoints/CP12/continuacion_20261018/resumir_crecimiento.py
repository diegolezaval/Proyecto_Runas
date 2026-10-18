"""Tabulate exact arithmetic between saved spatial prefix certificates."""
from pathlib import Path
import argparse
import hashlib
import json


def run(repo):
    base=repo/'checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015'
    rows=[]
    for p in sorted(base.glob('METRICAS_ESPACIALES_PREFIJO_TAU*.json')):
        j=json.loads(p.read_text())
        assert j['M2_steps_executed']==0 and j['original_spatial_threshold']==.02
        value=100*j['comparison']['final_mediator_phase_space_error_over_initial_norm']
        previous=rows[-1]['chi_phase_percent'] if rows else None
        rows.append(dict(time=j['time'],chi_phase_percent=value,
            change_percentage_points=None if previous is None else value-previous,
            factor=None if previous is None else value/previous,
            five_spatial_gates_passed=j['prefix_pair_limits_met'],
            source=str(p.relative_to(repo)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    output=repo/'informes/CRECIMIENTO_ERROR_CHI_MIXTO_CP12_20261018.md'
    lines=['# CP12 mixto: crecimiento medido del error de fases χ','',
        'Aritmética de las comparaciones guardadas y auditadas; cero pasos M2. '
        'Los factores comparan tiempos sucesivos con las mismas dos mallas. '
        'No son órdenes de convergencia espacial ni certifican una ley exponencial o una predicción hasta τ160.','',
        '| τ | Error χ (%) | Cambio (puntos porcentuales) | Factor frente a anterior | Cinco puertas ≤2 % |',
        '|---|---:|---:|---:|---|']
    for r in rows:
        delta='—' if r['change_percentage_points'] is None else f'{r["change_percentage_points"]:.10f}'
        factor='—' if r['factor'] is None else f'{r["factor"]:.8f}'
        status='Pasan' if r['five_spatial_gates_passed'] else 'NEGATIVO'
        lines.append(f'| {r["time"]} | {r["chi_phase_percent"]:.10f} | {delta} | {factor} | {status} |')
    lines += ['', 'Un factor que disminuye puede acompañar a un error que sigue aumentando. '
        'Cada frontera conserva su propia decisión con el límite original del 2 %. '
        'Superar ese límite suspende la continuación correspondiente, aunque el crecimiento relativo se reduzca. '
        'El acuerdo entre mallas y estos incrementos son evidencia numérica de M2; no validación experimental.','',
        'Fuentes exactas y hashes: `CRECIMIENTO_ERROR_CHI_MIXTO_CP12_20261018.json`.','']
    output.write_text('\n'.join(lines))
    output.with_suffix('.json').write_text(json.dumps(dict(rows=rows,threshold_percent=2,
        M2_steps_executed=0,temporal_model_fitted=False,extrapolation_used=False,CP12_closed=False),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows[-3:],ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    run(parser.parse_args().repo.resolve())
