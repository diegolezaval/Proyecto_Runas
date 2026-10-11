"""Verifica CP11; reproducción con recibo previo, sin repetir evoluciones M2."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from threadpoolctl import threadpool_limits
from checkpoint import digest
from ejecutar_con_procedencia import verify_receipt
import ejecutar_con_procedencia as provenance
from ejecutar_protocolo import configure

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'validacion/P06/no_radial/CP11'
EXPECTED={'diagnostico_radial':'COMPLETADA','contraste_fuente':'COMPLETADA','respuesta_forzada':'FALLIDA','respuesta_forzada_precisa':'COMPLETADA'}


def read(path):return json.loads(path.read_text())


def verify(reproduce=False):
    tests={};snapshot=ROOT/'trazabilidad/CP10_entrada';baseline=read(snapshot/'archivos_sha256.json')
    sources={};missing=[]
    for path,expected in baseline.items():
        current=ROOT/path;old=snapshot/path
        if old.is_file() and digest(old)==expected:sources[path]=old
        elif current.is_file() and digest(current)==expected:sources[path]=current
        else:missing.append(path)
    tests['all_938_CP10_files_recoverable']=len(baseline)==938 and not missing
    tests['no_original_file_removed_or_renamed']=all((ROOT/p).is_file() for p in baseline)
    original_science=[p for p in baseline if p.startswith(('validacion/','tratado/','graficos/','fichas/','hoja_ruta_original/'))]
    tests['all_original_scientific_evidence_and_chapters_unchanged']=all(digest(ROOT/p)==baseline[p] for p in original_science)
    for p in ['herramientas/modelo_m2.py','herramientas/continuar_no_radial_m2.py','herramientas/continuar_no_radial_adaptativo.py','herramientas/fuerza_potencial_m2.c','datos/theta_comun.json','datos/ensayo_no_radial_CP06.json','datos/ensayo_mediador_CP10.json']:
        tests['unchanged:'+p]=digest(ROOT/p)==baseline[p]
    old=read(snapshot/'estado_progreso.json');current=read(ROOT/'estado_progreso.json')
    old_stages={s['id']:s for s in old['stages']};stages={s['id']:s for s in current['stages']}
    tests['all_33_stage_identities_and_gates_preserved']=len(stages)==33 and stages.keys()==old_stages.keys() and all(stages[k]['gate_original']==old_stages[k]['gate_original'] and stages[k]['dependencies']==old_stages[k]['dependencies'] for k in stages)
    tests['other_32_stage_records_identical']=all(stages[k]==old_stages[k] for k in stages if k!='E03')
    tests['E00_E01_C0_not_reopened']=all(stages[k]==old_stages[k] for k in ['E00','E01','C0'])
    tests['general_research_stages_remain_partial']=all(stages[k]['status']=='PARCIAL' for k in ['E03','E04','RES0','RES1'])
    tests['no_active_runs_no_primordial_declared']=not current['numerical_runs_in_progress'] and not current['research_in_progress'] and current['complete_primordials']==0
    tests['latest_valid_M2_state_is_still_CP10']=current['latest_completed_nonradial_state']==old['latest_completed_nonradial_state'] and current['latest_completed_nonradial_time']==160 and current['restart_state']==old['restart_state']
    runs={};reports=[]
    for name,status in EXPECTED.items():
        paths=list(BASE.glob(name+'__*/procedencia.json'))
        if len(paths)!=1:raise ValueError('Recibo ausente o ambiguo: '+name)
        path=paths[0];r=read(path);check=verify_receipt(path);reports.append(check);runs[name]=(path.parent,r)
        tests[name+':receipt_integrity_and_expected_status']=check['passed'] and r['status']==status and all(seg['status']!= 'EN_PROGRESO' for seg in r['segments'])
        result=read(path.parent/'resultados.json')
        tests[name+':unchanged_physical_gate_and_no_evolution']=result['physical_gate_threshold']==.02 and result['physical_gate']=='REFINAMIENTO_PENDIENTE' and result['new_M2_evolution_steps']==0 and result['old_evolutions_repeated'] is False and result['cause_certified'] is False
    a=read(runs['diagnostico_radial'][0]/'resultados.json');b=read(runs['contraste_fuente'][0]/'resultados.json');failed=read(runs['respuesta_forzada'][0]/'resultados.json');f=read(runs['respuesta_forzada_precisa'][0]/'resultados.json')
    tests['metric_and_algebra_decisions_match_data']=a['metric']['artificial_threshold_crossing_explanation_rejected'] and a['radial']['algebra_passed'] and a['radial']['short_components_predominate'] and not a['radial']['free_initial_explanation_sufficient']
    tests['negative_frozen_phase_gate_preserved']=b['source']['squared_error_reduction']<.5 and b['source']['supports_delimited_dispersive_explanation'] is False and b['source']['correction_used_for_acceptance'] is False
    tests['arithmetic_failure_preserved_without_physical_inference']=failed['algebra_passed'] is False and any(x['identity_relative_residual']>=2e-12 for x in failed['instantaneous_defect_terms']) and runs['respuesta_forzada'][1]['segments'][-1]['returncode']!=0
    tests['extended_reference_meets_same_tolerance']=f['algebra_passed'] and all(x['identity_relative_residual']<2e-12 and x['spline_matrix_equivalence_relative_error']<2e-12 and x['reference_epsilon']<x['float64_epsilon'] for x in f['instantaneous_defect_terms'])
    tests['forced_response_bound_and_stop_delimited']=f['main_free_initial_explanation_rejected'] and f['forced_difference_lower_bound_amplitude_ratio']>.5 and f['source_history_reconstructible_from_endpoints'] is False and f['fundamental_model_Cauchy_uniqueness_questioned'] is False and current['automatic_continuation_paused']['M2_exhaustion_claimed'] is False
    reproductions=[]
    with tempfile.TemporaryDirectory(prefix='runas_CP11_verificacion_') as temporary:
        temp=Path(temporary);recovered=temp/'CP10'
        for name,p in sources.items():
            target=recovered/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        cp10=subprocess.run([sys.executable,str(recovered/'herramientas/checkpoint.py'),'--verificar'],text=True,capture_output=True,timeout=30)
        tests['CP10_original_checkpoint_reconstructed_and_verified']=not missing and cp10.returncode==0
        if reproduce:
            env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
            for name in ['diagnostico_radial','contraste_fuente','respuesta_forzada_precisa']:
                folder,r=runs[name];out=temp/name;out.mkdir()
                entry=r['identity']['case']['entrypoint']
                run=subprocess.run([sys.executable,str(ROOT/entry),'--config',str(folder/'configuration.json'),'--output-dir',str(out)],cwd=ROOT,env=env,text=True,capture_output=True,timeout=60)
                emitted=sorted(p.name for p in out.iterdir() if p.is_file())
                identical=bool(emitted) and all((folder/p).is_file() and digest(out/p)==digest(folder/p) for p in emitted)
                tests[name+':reproduction_byte_identical']=run.returncode==0 and identical
                reproductions.append(dict(case=name,returncode=run.returncode,outputs=emitted,byte_identical=identical,new_M2_evolution_steps=0,
                                          error=run.stderr[-2000:] if run.returncode else None))
    # This is read-only validation. Publication receipts may live outside the payload.
    result=dict(passed=all(tests.values()),checkpoint=current['checkpoint'],tests={k:bool(v) for k,v in tests.items()},
                original_files_recoverable=len(sources),missing_originals=missing,receipts=reports,reproductions=reproductions,
                new_M2_evolution_steps=0,physical_gate='REFINAMIENTO_PENDIENTE',physical_gate_threshold=.02,
                scope='Identidad, antecedentes, puertas y reproducción de diagnósticos en temporales; no evolución, aceptación física ni certificación del continuo.')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path);parser.add_argument('--output-dir',type=Path);parser.add_argument('--salida',type=Path)
    parser.add_argument('--protocolo',type=Path);parser.add_argument('--caso');parser.add_argument('--recibo-externo',type=Path)
    args=parser.parse_args()
    if args.recibo_externo:
        if not args.protocolo or not args.caso:parser.error('Recibo externo requiere protocolo y caso')
        protocol=args.protocolo.resolve() if args.protocolo.is_absolute() else ROOT/args.protocolo
        data=configure(protocol,args.caso);case=data['cases'][args.caso]
        if case['operation']!='verificacion_diagnosticos_guardados' or case['entrypoint']!='herramientas/verificar_CP11.py':raise ValueError('Modo externo limitado a verificación CP11 sin evolución')
        if args.recibo_externo.resolve().is_relative_to(ROOT):raise ValueError('El recibo externo debe estar fuera del payload')
        provenance.CAMPAIGN=args.recibo_externo.resolve();provenance.execute(protocol,args.caso);raise SystemExit(0)
    if args.config:
        cfg=read(args.config)
        if cfg['case']['operation']!='verificacion_diagnosticos_guardados':raise ValueError('Operación no admitida')
        if not args.output_dir:parser.error('Trabajador requiere output-dir')
        with threadpool_limits(limits=1):report=verify(reproduce=True)
        destination=args.output_dir/'verificacion.json'
    else:
        with threadpool_limits(limits=1):report=verify()
        destination=args.salida
    if destination:
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['passed'] else 1)
