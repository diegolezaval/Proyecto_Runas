"""Revisión de integridad CP12 tras pérdida local; cero pasos científicos M2."""
from pathlib import Path
import argparse
import json
from ejecutar_con_procedencia import digest, prepare, verify_receipt, write

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def review():
    archive = ROOT / 'trazabilidad/CP11_entrada'
    inventory = read(archive / 'archivos_sha256.json')
    missing = [name for name, wanted in inventory.items() if not any(
        path.is_file() and digest(path) == wanted for path in [archive/name, ROOT/name])]
    previous = read(archive/'estado_progreso.json')
    current = read(ROOT/'estado_progreso.json')
    protocol = read(ROOT/'datos/ensayo_causal_chi_CP12.json')
    reports = [verify_receipt(path) for path in sorted(
        (ROOT/'validacion/P06/no_radial/CP12').glob('control_instrumentacion__*/procedencia.json'))]
    _, _, identity, run_id = prepare(ROOT/'datos/ensayo_causal_chi_CP12.json', 'par_instrumentado')
    run = ROOT/'validacion/P06/no_radial/CP12'/('par_instrumentado__'+run_id)
    preserved_science = [name for name in inventory if name.startswith(
        ('validacion/', 'tratado/', 'graficos/', 'fichas/', 'hoja_ruta_original/'))]
    fixed = ['datos/theta_comun.json', 'herramientas/modelo_m2.py',
             'herramientas/fuerza_potencial_m2.c', 'datos/ensayo_no_radial_CP06.json',
             'datos/ensayo_mediador_CP10.json', 'datos/estado_evidencia.json', 'ENMIENDAS_HOJA_RUTA.md']
    pause = current['automatic_continuation_paused']
    controls = list((ROOT/'validacion/P06/no_radial/CP12').glob('control_instrumentacion__*/procedencia.json'))
    matching = [path for path in controls if read(path)['status'] == 'COMPLETADA' and all(
        digest(ROOT/name) == wanted for name, wanted in read(path)['identity']['code_hashes'].items())]
    tests = dict(all_1047_CP11_files_recoverable=len(inventory)==1047 and not missing,
                 all_original_paths_exist=all((ROOT/name).is_file() for name in inventory),
                 original_scientific_evidence_unchanged=all(digest(ROOT/name)==inventory[name] for name in preserved_science),
                 M2_Theta_original_protocols_evidence_and_amendments_unchanged=all(digest(ROOT/name)==inventory[name] for name in fixed),
                 all_33_stage_records_identical=current['stages']==previous['stages'] and len(current['stages'])==33,
                 all_six_control_receipts_intact=len(reports)==6 and all(r['passed'] for r in reports),
                 three_failed_technical_controls_preserved=sum(r['status']=='FALLIDA' for r in reports)==3,
                 one_positive_control_matches_current_instrumentation=len(matching)==1,
                 same_instrumented_pair_identity=run_id=='a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d',
                 physical_gate_still_two_percent=protocol['criteria']['field_and_phase_space_relative_error_max']==.02,
                 last_closed_checkpoint_still_CP11=current['checkpoint']==current['scientific_checkpoint']=='CP11_DIAGNOSTICO_RADIAL_CHI',
                 latest_valid_state_still_CP10=current['latest_completed_nonradial_state']==previous['latest_completed_nonradial_state'],
                 no_nonexistent_run_announced_as_active=not current['numerical_runs_in_progress'] and not current['research_in_progress'],
                 missing_restart_explicitly_blocks_continuation=pause['reason']=='ESTADO_CP12_NO_DISPONIBLE_TRAS_LIMPIEZA' and pause['resume_ready'] is False,
                 no_fundamental_change_or_exhaustion_claim=pause['fundamental_model_change_authorized'] is False and pause['M2_exhaustion_claimed'] is False)
    return dict(passed=all(tests.values()), tests=tests, checkpoint=current['checkpoint'],
                original_files_recovered=len(inventory)-len(missing), missing_original_CP11_paths=missing,
                control_receipts=reports, instrumented_pair_run_id=run_id,
                physical_code_hashes=identity['code_hashes'],
                restart_files_present=[p.name for p in run.glob('*_estado.npz')],
                original_pair_receipt_present=(run/'procedencia.json').is_file(),
                resume_ready=False, cause_certified=False, correction_tested=False,
                physical_gate='REFINAMIENTO_PENDIENTE', physical_gate_threshold=.02,
                M2_steps_executed=0, original_CP10_evolutions_repeated=False,
                missing_CP12_data_is_a_scientific_negative=False,
                scope='Integridad de material recuperado y registro explícito del bloqueo; no certificación de un estado CP12 ausente.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if read(args.config)['case']['operation'] != 'revision_recuperacion_sin_evolucion':
        raise ValueError('Operación no admitida')
    result = review()
    write(args.output_dir/'resultados.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
