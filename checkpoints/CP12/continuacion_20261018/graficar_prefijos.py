"""Render the five already certified spatial comparisons; no integration."""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run(repo, output, preview=None):
    base = repo / 'checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015'
    sources = sorted(base.glob('METRICAS_ESPACIALES_PREFIJO_TAU*.json'))
    records = []
    for path in sources:
        data = json.loads(path.read_text())
        assert data['M2_steps_executed'] == 0
        assert data['original_spatial_threshold'] == .02
        records.append((data['time'], data['comparison'], str(path.relative_to(repo)),
                        hashlib.sha256(path.read_bytes()).hexdigest()))
    assert records
    records.sort()
    metrics = [
        ('norm_relative_sup_error', 'Norma temporal suprema', '#707070'),
        ('final_complex_nonradial_field_error_over_initial_norm', r'Campo $\Phi$', '#628a32'),
        ('final_phi_phase_space_error_over_initial_norm', r'Fases $\Phi$', '#2a9d8f'),
        ('final_mediator_nonradial_error_over_initial_norm', r'Campo $\chi$', '#0072b2'),
        ('final_mediator_phase_space_error_over_initial_norm', r'Fases $\chi$', '#9b51a4'),
    ]
    with plt.rc_context({'font.size': 10, 'svg.hashsalt': 'CP12-certified-prefixes'}):
        fig, ax = plt.subplots(figsize=(9.2, 5.4), constrained_layout=True)
        for key, label, color in metrics:
            ax.plot([r[0] for r in records], [100*r[1][key] for r in records],
                    marker='o', markersize=4, linewidth=1.7, color=color, label=label)
        ax.axhline(2, color='#b3261e', linestyle='--', linewidth=1.5, label='Límite original: 2 %')
        ax.set(xlabel=r'Tiempo $\tau$', ylabel='Error relativo (%)',
               xlim=(0, max(r[0] for r in records)+2),
               ylim=(0, max(2.2, 110*max(r[1][key] for r in records for key, _, _ in metrics))))
        ax.set_title('CP12 mixto: cinco métricas espaciales auditadas', loc='left', pad=14, weight='bold')
        ax.grid(axis='y', alpha=.22)
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(loc='upper left', fontsize=9, frameon=True, facecolor='white',
                  edgecolor='none', framealpha=1, ncol=2)
        fig.supxlabel('h = 0,125 / 0,0625 · χ sin ajuste de fase · evidencia numérica de dos mallas', fontsize=9)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, metadata={'Date': None, 'Description': 'Derived only from authenticated saved prefix comparisons. No M2 steps.'})
        if preview:
            fig.savefig(preview, dpi=150)
        plt.close(fig)
    provenance = dict(schema='CP12_DERIVED_FIVE_SPATIAL_METRICS_FIGURE',
        source_certificates=[dict(time=t, path=p, sha256=s) for t, _, p, s in records],
        original_threshold=.02, final_time=max(r[0] for r in records),
        derived_from_saved_comparisons_only=True, M2_steps_executed=0,
        figure_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        continuum_or_experimental_validation=False, CP12_closed=False)
    output.with_suffix('.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(provenance))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--preview', type=Path)
    args = parser.parse_args()
    run(args.repo.resolve(), args.output.resolve(), args.preview.resolve() if args.preview else None)
