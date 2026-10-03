"""Comprueba un clon CP10 sin nuevas campañas; recibo fuera del repositorio."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,tempfile,zipfile

EXPECTED_ZIP='c1b8b472f8d1f89c466fd5cb89470f63993ec73dedc9dac3896a88ffc2add4c1'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()


def verify(root,archive,origin_kind):
 assert sha(archive)==EXPECTED_ZIP,'ZIP distinto del CP10 autorizado'
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  expected={n.removeprefix('Proyecto_Runas/'):hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
 assert len(expected)==938
 for n,h in expected.items():assert (root/n).is_file() and sha(root/n)==h,n
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg')
 def git(*args):
  r=subprocess.run(['git','-C',str(root),*args],env=env,text=True,capture_output=True,timeout=60)
  assert r.returncode==0,r.stderr
  return r.stdout.strip()
 assert git('branch','--show-current')=='main'
 if origin_kind == 'github':
  assert git('remote','get-url','origin') in [
   'https://github.com/diegolezaval/Proyecto_Runas.git',
   'git@github.com:diegolezaval/Proyecto_Runas.git'
  ], 'El origen no corresponde al repositorio GitHub privado previsto'
 commit=git('rev-parse','HEAD');assert commit==git('rev-parse','CP10^{commit}')
 assert set(git('ls-files','-z').split('\0'))-{''}==set(expected)
 assert not git('status','--porcelain')
 git('fsck','--full')
 runs=[]
 with tempfile.TemporaryDirectory(prefix='cp10_clon_comprobacion_') as temp:
  work=Path(temp)
  def run(args,label=None,timeout=180):
   r=subprocess.run([sys.executable,str(root/'herramientas'/args[0]),*args[1:]],cwd=work,env=env,text=True,capture_output=True,timeout=timeout)
   row={'command':args,'passed':r.returncode==0,'returncode':r.returncode,'output':r.stdout.replace(str(root),'<clon_CP10>').replace(str(work),'<temporal>')};runs.append(row)
   print(json.dumps({'check':label or args[0],'passed':row['passed']}),flush=True)
   assert r.returncode==0,r.stdout+r.stderr
   return r
  for args in [['checkpoint.py','--verificar'],['verificar_entorno.py','--cp10'],['generar_continuidad.py','--comprobar'],['generar_resumen_CP10.py','--comprobar'],['verificar_continuidad.py','--solo-lectura'],['auditar_arquitectura.py'],['ejecutar_con_procedencia.py','--verificar'],['verificar_CP10.py'],['probar_procedencia_futura.py'],['regresion_estructural.py']]:run(args)
  # El comprobador histórico de preparación presupone deliberadamente ausencia de .git.
  # Se ejecuta sobre los bytes exportados del índice del clon, sin modificar ese comprobador.
  export=work/'exportacion_CP10';export.mkdir()
  git('checkout-index','--all','--prefix='+str(export)+'/')
  assert all(sha(export/n)==h for n,h in expected.items())
  r=subprocess.run([sys.executable,str(export/'herramientas/verificar_preparacion_git.py')],cwd=work,env=env,text=True,capture_output=True,timeout=90)
  assert r.returncode==0,r.stdout+r.stderr
  preparation=json.loads(r.stdout)
  runs.append({'command':['verificar_preparacion_git.py','(exportación exacta del índice)'],'passed':True,'returncode':0,'output':r.stdout})
  force_code='''import sys,json,tempfile,pathlib,numpy as np
sys.path.insert(0,sys.argv[1])
from continuar_no_radial_m2 import Evolution
from diagnosticar_mediador_CP10 import load
import acelerar_fuerza_m2 as acceleration
from threadpoolctl import threadpool_limits
root=pathlib.Path(sys.argv[1]).parent
errors=[]
with threadpool_limits(limits=1),tempfile.TemporaryDirectory(prefix="cp10_fuerza_fria_") as temp:
 acceleration.OUT=pathlib.Path(temp)
 for name in ["temporal_h0125","espacial_h00625"]:
  p=next(root.glob("validacion/P06/no_radial/CP10/"+name+"__*/*_estado.npz"));d=load(p);c=d["configuration"];sim=Evolution(c["dx"],c["radius"],c["L"]);original=sim.force;acceleration.install(sim)
  for key in ["initial_q","q"]:
   a=original(d[key]);b=sim.force(d[key]);errors.append(float(np.max(abs(a-b))/max(1,float(np.max(abs(a))))))
 passed=max(errors)<2e-12
 print(json.dumps(dict(passed=passed,relative_errors=errors,cache_in_checkpoint_required=False,integration_steps=0)))
 assert passed
'''
  r=subprocess.run([sys.executable,'-c',force_code,str(root/'herramientas')],cwd=work,env=env,text=True,capture_output=True,timeout=60)
  assert r.returncode==0,r.stdout+r.stderr;force=json.loads(r.stdout)
  config=next(root.glob('validacion/P06/no_radial/CP10/comparacion_final__*/configuration.json'));views=work/'vistas';views.mkdir()
  run(['comparar_mediador_CP10.py','--config',str(config),'--output-dir',str(views)],'regeneración del resultado, CSV y SVG')
  regenerated={n:(views/n).read_bytes()==(config.parent/n).read_bytes() for n in ['resultados.json','comparaciones.csv','CP10_errores_mediador.svg']};assert all(regenerated.values())
  newzip=work/'CP10_reproducido.zip';run(['checkpoint.py','--salida',str(newzip)],'reproducción del ZIP')
  assert sha(newzip)==EXPECTED_ZIP,'El ZIP reproducido no coincide byte a byte'
 assert all(sha(root/n)==h for n,h in expected.items());assert not git('status','--porcelain')
 outcome=json.loads(next(root.glob('validacion/P06/no_radial/CP10/comparacion_final__*/resultados.json')).read_text())
 return {'passed':True,'origin_kind':origin_kind,'remote_clone_verified':origin_kind=='github','commit':commit,'branch':'main','tag':'CP10','payload_files':938,'all_payload_bytes_preserved':True,'deterministic_checkpoint_zip_reproduced':True,'checkpoint_zip_sha256':EXPECTED_ZIP,'CP10_checks':runs,'preparation_checker_context':'Exportación exacta del índice; respeta su condición histórica de no contener .git.','fresh_C_force':force,'views_regenerated_identically':regenerated,'scientific_gate':outcome['status'],'finite_campaign_passed':outcome['finite_campaign_passed'],'scientific_campaigns_executed':False,'CP11_started':False}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clon',type=Path,required=True);p.add_argument('--zip',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--origen',choices=['local','bundle','github'],default='local');a=p.parse_args()
 assert not a.salida.resolve().is_relative_to(a.clon.resolve()),'Guardar la comprobación fuera del corpus'
 report=verify(a.clon.resolve(),a.zip.resolve(),a.origen);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='CP10_checks'},ensure_ascii=False,indent=2))
