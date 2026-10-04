"""Vistas CP11 desde resultados registrados; no cálculos ni evoluciones nuevas."""
from pathlib import Path
import argparse
import io
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
SUMMARY=ROOT/'informes/RESUMEN_NUMERICO_CP11.md'
FIGURE=ROOT/'graficos/CP11_diagnostico_chi.svg'


def sources():
    registry=json.loads((ROOT/'datos/registro_calculos.json').read_text())
    paths=registry['authoritative_results']
    names=['chi_radial_diagnostic','chi_frozen_source_contrast','chi_forced_response']
    return paths,{name:json.loads((ROOT/paths[name]).read_text()) for name in names},registry


def render():
    paths,d,registry=sources();a=d['chi_radial_diagnostic'];b=d['chi_frozen_source_contrast']['source'];f=d['chi_forced_response'];m=a['metric'];r=a['radial']
    link=lambda p:f'[{p}](../{p})'
    lines=['# Resumen numérico · CP11','',
      '> Vista generada por herramientas/generar_resumen_CP11.py. Resultados y recibos son las autoridades; no editar cifras manualmente.','',
      '**Unidad finita: diagnóstico radial cerrado. Causa acoplada abierta por historia de fuente no guardada.**','',
      '**Puerta física original: REFINAMIENTO_PENDIENTE, umbral 2 %. Cero pasos nuevos de evolución M2.**','',
      '## Interpolación y métrica','',
      'Normas sobre r<40 y τ=160, relativas a la perturbación inicial de χ; velocidades divididas por M. Ninguna fase de χ se ajusta para aceptación. Ambos denominadores y la sensibilidad lineal permanecen en el resultado fuente.','',
      '| Comparación | Campo (%) | Campo y velocidad (%) |','|---|---:|---:|']
    rows=[('CP10 unilateral',m['original']),('Inversa: fina→gruesa',m['reverse']),('Spline simétrico, Gauss 12',m['continuous_union_knots_Gauss']['12']),('Spline con paridad en origen',m['parity_at_origin']),('Control lineal, orden inferior',m['lower_order_linear_sensitivity'])]
    for name,row in rows:
        lines.append(f"| {name} | {100*row['field_error_fine_denominator']:.9g} | {100*row['phase_space_error_fine_denominator']:.9g} |")
    lines += ['',f"Error inicial spline: {100*m['original']['initial_phase_space_difference']:.9g} %. Error fina→gruesa→fina de representación: {100*m['fine_coarse_fine_roundtrip']['phase_space_error_fine_denominator']:.9g} %.",'',
      'La explicación de un cruce artificial del umbral queda descartada en las comparaciones spline declaradas; no se certifica el continuo.','',
      '## Operador y componentes cortas','',
      '| Control algebraico | Error relativo máximo |','|---|---:|',
      f"| Acción frente a Evolution.lap | {max(x['action_relative_error'] for x in r['operator_audits']):.9g} |",
      f"| Simetría ponderada | {max(x['weighted_symmetry_relative_error'] for x in r['operator_audits']):.9g} |",
      f"| Residuo modal | {r['max_eigenmode_relative_residual']:.9g} |",
      f"| Parseval | {r['max_parseval_relative_error']:.9g} |",'',
      'K es la forma positiva de la acción FV en R=220. La autobase libre no es el generador dinámico acoplado.','',
      '| Corte k=√λ | Fracción de diferencia cuadrática por encima (%) | Recorte suave (%) |','|---|---:|---:|']
    for k,v in r['actual_core_error_fractions_above_k'].items():
        lines.append(f"| {k} | {100*v:.9g} | {100*r['actual_smooth_core_error_fractions_above_k'][k]:.9g} |")
    lines += ['',f"El recorte suave conserva {100*r['smooth_core_power_retained']:.9g} % de la diferencia cuadrática. Son fracciones de la norma de error, no de energía física.",'',
      '| ℓ=2: k continuo aproximado | Δω·τ, gruesa−fina (rad) |','|---|---:|']
    for row in r['eigenvalue_phase_examples']:
        if row['ell']==2 and row['continuum_k']>1:
            lines.append(f"| {row['continuum_k']:.6g} | {row['phase_coarse_minus_fine']:.9g} |")
    lines += ['','## Hipótesis negativas y respuesta forzada','',
      f"Propagador libre de χ inicial: diferencia {100*r['free_initial_propagator']['phase_space_error_fine_denominator']:.9g} %; su diferencia cuadrática representa {100*r['free_initial_squared_difference_over_actual']:.9g} % de la observada. No basta.",'',
      f"Residuo frente al equilibrio congelado: {100*b['fast_residual_difference']['phase_space_error_fine_denominator']:.9g} %. Diferencia del equilibrio: {100*b['instantaneous_equilibrium_difference']['phase_space_error_fine_denominator']:.9g} %.",'',
      f"La corrección modal fijada antes del resultado deja {100*b['predetermined_modal_correction']['phase_space_error_fine_denominator']:.9g} % y reduce {100*b['squared_error_reduction']:.9g} % la diferencia cuadrática. Falla el criterio explicativo prerregistrado de reducción ≥50 %. No se utiliza para la puerta física.",'',
      f"Diferencia de respuesta forzada por Duhamel: {100*f['forced_response_phase_space_difference']:.9g} %. Cota inferior de su amplitud respecto de la diferencia observada: {100*f['forced_difference_lower_bound_amplitude_ratio']:.9g} %. El cierre de la descomposición tiene residuo {f['decomposition_closure_relative_residual']:.9g}.",'',
      'Los extremos determinan dos momentos por modo, no la historia de fuente. No separan el presupuesto integrado del conmutador radial y el de la fuente acoplada. Se detiene antes de nuevas campañas.','',
      '## Intento aritmético conservado y referencia','',
      'El intento doble inicial es FALLIDA y no evidencia aceptada. Su código, salidas y recibo permanecen incluidos. La referencia longdouble conserva las mismas ecuaciones, estados, coeficientes y spline, y la tolerancia algebraica 2e−12.','',
      '| Extremo | Residuo de identidad extendida | Equivalencia de spline |','|---|---:|---:|']
    for row in f['instantaneous_defect_terms']:
        lines.append(f"| {row['frame']} | {row['identity_relative_residual']:.9g} | {row['spline_matrix_equivalence_relative_error']:.9g} |")
    lines += ['','## Fuentes y recibos','']
    for name in ['chi_radial_diagnostic','chi_frozen_source_contrast','chi_forced_response']:
        p=paths[name];lines.append(f'- {name}: {link(p)}; recibo {link(str(Path(p).with_name("procedencia.json")))}.')
    for failure in registry['failed_CP11_controls_preserved']:
        lines.append(f'- Intento fallido: {link(failure["result"])}; recibo {link(failure["receipt"])}.')
    lines += ['',f'Figura generada: {link(FIGURE.relative_to(ROOT).as_posix())}.',
      '', 'La definición, hipótesis, derivación y puerta están en [el capítulo 31](../tratado/31_diagnostico_radial_del_mediador.md) y los prerregistros. E03/E04/RES0/RES1 siguen PARCIALES; no se afirma estabilidad orbital, convergencia continua/conjunta, inestabilidad física ni agotamiento de M2.','']
    return '\n'.join(lines)


def figure_bytes(preview=None):
    _,d,_=sources();m=d['chi_radial_diagnostic']['metric'];r=d['chi_radial_diagnostic']['radial']
    plt.rcParams.update({'svg.hashsalt':'Runas-CP11','font.size':10,'font.family':'DejaVu Sans'})
    fig,ax=plt.subplots(1,2,figsize=(11.4,4.7),layout='constrained')
    names=['CP10','Inversa','Cuadratura','Paridad'];data=[m['original'],m['reverse'],m['continuous_union_knots_Gauss']['12'],m['parity_at_origin']]
    errors=[100*x['phase_space_error_fine_denominator'] for x in data]
    ax[0].barh(names,errors,color='#24659c',height=.6);ax[0].invert_yaxis()
    ax[0].axvline(2,color='#a33e35',linestyle='--',label='Puerta original: 2 %')
    for i,x in enumerate(errors):ax[0].text(x+.07,i,f'{x:.4f} %',va='center',fontsize=9)
    ax[0].set_xlim(0,6.35);ax[0].set_xlabel('Diferencia de χ en espacio de fases (%)');ax[0].set_title('El fallo persiste entre métricas');ax[0].legend(loc='lower right')
    cuts=list(map(float,r['actual_core_error_fractions_above_k']));values=[100*x for x in r['actual_core_error_fractions_above_k'].values()]
    ax[1].plot(cuts,values,'o-',color='#24659c',linewidth=2)
    ax[1].set_ylim(-2,104);ax[1].set_xlim(0,21);ax[1].set_xticks(cuts)
    ax[1].set_xlabel('Corte radial k = √λ');ax[1].set_ylabel('Fracción de diferencia cuadrática por encima (%)')
    ax[1].set_title('Diferencia dominada por modos cortos');ax[1].grid(alpha=.2)
    fig.suptitle('CP11 · Diagnóstico sobre estados guardados de CP10',fontsize=14)
    fig.supxlabel('R = 220 · L = 4 · τ = 160 · r < 40 · sin ajuste de fase χ',fontsize=10)
    stream=io.BytesIO();fig.savefig(stream,format='svg',metadata={'Date':None,'Creator':'herramientas/generar_resumen_CP11.py'})
    if preview:
        if preview.resolve().is_relative_to(ROOT):raise ValueError('Vista previa fuera del payload')
        preview.parent.mkdir(parents=True,exist_ok=True);fig.savefig(preview,dpi=140)
    plt.close(fig);return stream.getvalue()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--comprobar',action='store_true');parser.add_argument('--vista-previa',type=Path)
    args=parser.parse_args();summary=render();figure=figure_bytes(args.vista_previa)
    if args.comprobar:
        passed=SUMMARY.is_file() and SUMMARY.read_text()==summary and FIGURE.is_file() and FIGURE.read_bytes()==figure
    else:
        SUMMARY.write_text(summary);FIGURE.write_bytes(figure);passed=True
    print(json.dumps(dict(passed=passed,generated_views=[SUMMARY.relative_to(ROOT).as_posix(),FIGURE.relative_to(ROOT).as_posix()],new_M2_evolution_steps=0)))
    raise SystemExit(0 if passed else 1)
