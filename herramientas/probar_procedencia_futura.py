from pathlib import Path
import sys,tempfile,subprocess,os,json,shutil,hashlib,fcntl
import numpy as np
PROJECT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

worker='''from pathlib import Path
import argparse,json,os,numpy as np
p=argparse.ArgumentParser();p.add_argument('--config',type=Path);p.add_argument('--output-dir',type=Path);p.add_argument('--stop-at',type=float);a=p.parse_args()
out=a.output_dir;r=json.loads((out/'procedencia.json').read_text());assert r['status']=='EN_PROGRESO' and r['segments'][-1]['status']=='EN_PROGRESO'
assert all(os.environ.get(k)=='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'])
cfg=json.loads(a.config.read_text())['case']['configuration'];state=out/'control_estado.npz'
start=0.0
if state.exists():
 with np.load(state,allow_pickle=False) as z:start=float(z['time'])
target=min(cfg['tmax'],a.stop_at) if a.stop_at is not None else cfg['tmax']
assert start<=target
print('REUSED' if start==target else 'CONTINUED_FROM '+str(start))
q=np.zeros((3,2,2));rows=np.array([[0.,0.],[target,target]])
np.savez_compressed(state,q=q,v=q,initial_q=q,initial_v=q,rows=rows,time=target,config=json.dumps(cfg))
progress=dict(time=target,status='EN_PROGRESO' if target<cfg['tmax'] else 'CALCULO_TERMINADO')
if target==cfg['tmax']:
 (out/'control.json').write_text(json.dumps(dict(configuration=cfg,scope='CONTROL_DE_PROCEDENCIA_NO_EVIDENCIA_M2')))
 np.savetxt(out/'control_tiempo.csv',rows,delimiter=',',header='time,control',comments='')
(out/'control_progreso.json').write_text(json.dumps(progress))
'''


def run_tests():
    tests={};commands=[]
    with tempfile.TemporaryDirectory(prefix='runica_procedencia_futura_') as temporary:
     root=Path(temporary)/'Proyecto_Runas'
     for d in ['herramientas','datos','validacion/P06/no_radial']: (root/d).mkdir(parents=True,exist_ok=True)
     for name in ['ejecutar_con_procedencia.py','ejecutar_protocolo.py']:shutil.copyfile(PROJECT/'herramientas'/name,root/'herramientas'/name)
     (root/'herramientas/caso_control.py').write_text(worker)
     (root/'datos/theta_comun.json').write_text('{}')
     np.savez(root/'validacion/origen.npz',control=np.zeros(1))
     protocol=dict(model='M2',initial_state='validacion/origen.npz',campaign_directory='validacion/control_aislado',scope='CONTROL_DE_PROCEDENCIA_NO_EVIDENCIA_M2',cases={'demo':dict(entrypoint='herramientas/caso_control.py',configuration=dict(tmax=2.0),inputs=['datos/theta_comun.json'],extra_code=['herramientas/ejecutar_protocolo.py'])})
     path=root/'datos/protocolo_demo.json';path.write_text(json.dumps(protocol))
     env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1')
     def call(*args,expected=0):
      r=subprocess.run([sys.executable,str(root/'herramientas/ejecutar_protocolo.py'),'--protocolo','datos/protocolo_demo.json','--caso','demo',*args],cwd=temporary,env=env,text=True,capture_output=True,timeout=20)
      commands.append(dict(args=list(args),returncode=r.returncode,expected=expected))
      if r.returncode!=expected:raise AssertionError(r.stdout+r.stderr)
      return r
     call('--stop-at','1')
     receipt=next((root/'validacion/control_aislado').glob('*/procedencia.json'));run=receipt.parent;state=run/'control_estado.npz'
     r=json.loads(receipt.read_text())
     tests['receipt_and_sources_exist_before_worker_and_threads_applied']=r['status']=='PAUSADA_REANUDABLE' and 'herramientas/ejecutar_protocolo.py' in r['identity']['code_hashes'] and len(r['run_id'])==64
     tests['campaign_directory_relative_to_corpus']=run.parent==root/'validacion/control_aislado'
     saved=state.read_bytes();before=receipt.read_bytes()
     with (root/('validacion/P06/no_radial/ejecucion_prov_'+r['run_id']+'.lock')).open('a+') as lock:
      fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
      blocked=call('--reanudar',expected=1)
      tests['second_live_writer_refused_without_mutation']=receipt.read_bytes()==before and state.read_bytes()==saved and 'BlockingIOError' in blocked.stderr
     (root/'herramientas/caso_control.py').write_text(worker+'\n# altered code fixture\n')
     refused=call('--reanudar',expected=1)
     tests['changed_code_resume_refused_without_new_run']=len(list(run.parent.iterdir()))==1 and receipt.read_bytes()==before and state.read_bytes()==saved and 'No existe esta identidad' in refused.stderr
     (root/'herramientas/caso_control.py').write_text(worker)
     # Emulate an orphaned segment with a valid last state, never a physics run.
     r['status']='EN_PROGRESO';r['segments'].append(dict(status='EN_PROGRESO',started_at='CONTROL_AISLADO',command=[],resumed_from_hashes={'control_estado.npz':sha(state)}));receipt.write_text(json.dumps(r))
     with np.load(state,allow_pickle=False) as z:bad={k:z[k].copy() for k in z.files}
     bad['q'][0,0,0]=np.nan;np.savez_compressed(state,**bad)
     orphan_bytes=receipt.read_bytes();refused=call('--reanudar',expected=1)
     tests['nonfinite_orphan_state_refused_without_receipt_mutation']=receipt.read_bytes()==orphan_bytes and 'Estado no finito' in refused.stderr
     state.write_bytes(saved)
     continued=call('--reanudar')
     r=json.loads(receipt.read_text());lost=r['segments'][-2]
     tests['orphan_segment_preserved_and_recovered']=lost['status']=='INTERRUMPIDA' and lost['recovered_time']==1 and lost['recovered_state_sha256']==r['segments'][-1]['resumed_from_hashes']['control_estado.npz'] and 'CONTINUED_FROM 1.0' in continued.stdout and r['status']=='COMPLETADA'
     call('--verificar')
     before=receipt.read_bytes();saved=state.read_bytes();reused=call('--reanudar')
     tests['closed_case_reused_without_output_or_receipt_changes']=receipt.read_bytes()==before and state.read_bytes()==saved and 'REUTILIZADO' in reused.stdout
     # Worker finished, parent died before closing receipt; no integration repeated.
     r['status']='EN_PROGRESO';r['segments'].append(dict(status='EN_PROGRESO',started_at='CONTROL_AISLADO_CIERRE',command=[],resumed_from_hashes={'control_estado.npz':sha(state)}));receipt.write_text(json.dumps(r))
     completed=call('--reanudar');r=json.loads(receipt.read_text())
     tests['finished_worker_orphan_closed_without_advancing_state']=r['status']=='COMPLETADA' and r['segments'][-2]['recovered_time']==2 and state.read_bytes()==saved and 'REUSED' in completed.stdout
     call('--verificar')
     protocol['cases']['demo']['extra_code']=[];path.write_text(json.dumps(protocol))
     refused=call(expected=1)
     tests['undeclared_launcher_refused']=len(list(run.parent.iterdir()))==1 and 'Declarar este adaptador' in refused.stderr
    report=dict(passed=all(tests.values()),tests=tests,commands=commands,adapter_sha256=sha(PROJECT/'herramientas/ejecutar_protocolo.py'),numerical_campaigns_executed=False,scope='Controles aislados de orquestación con arrays sintéticos; no evidencia física ni integración M2. Corpus científico no modificado.')
    return report


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Controles aislados del adaptador; no campañas científicas.')
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    report = run_tests()
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
