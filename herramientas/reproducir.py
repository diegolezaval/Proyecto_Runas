"""Reproduce los calculos o comprueba la entrega; no controla dispositivos fisicos."""
from pathlib import Path
import argparse, json, os, subprocess, sys, time, platform
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--solo-verificar',action='store_true',help='Comprueba resultados incluidos sin repetir solucionadores.')
a=p.parse_args()
env=os.environ.copy(); env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
if a.solo_verificar:
 scripts=['verificar.py','verificar_m2.py','verificar_capilaridad.py']
else:
 scripts=['ensayo_microscopico.py','correspondencia_micro.py','complecion_escalar.py',
          'preparacion_y_motor.py','graficos_micro.py','resultados_micro.py',
          'cierre_m2.py','dinamica_m2.py','contrastes_r1.py','guia_m2.py',
          'capilaridad_m2.py','catalogo_aceptacion_m2.py','figuras_m2.py',
          'figuras_capilaridad.py','generar.py','verificar.py','verificar_m2.py',
          'verificar_capilaridad.py','generar.py']
mode='verificacion' if a.solo_verificar else 'completa'
logs=R/'validacion/reproduccion'/mode; logs.mkdir(parents=True,exist_ok=True)
runs=[]; okay=True
for i,script in enumerate(scripts):
 print(f'[{i+1}/{len(scripts)}] {script}',flush=True)
 start=time.perf_counter()
 with (logs/f'{i+1:02d}_{script[:-3]}.log').open('w') as out:
  result=subprocess.run([sys.executable,str(R/'herramientas'/script)],cwd=R,env=env,stdout=out,stderr=subprocess.STDOUT)
 runs.append(dict(script=script,returncode=result.returncode,elapsed_seconds=time.perf_counter()-start,
                  log=str((logs/f'{i+1:02d}_{script[:-3]}.log').relative_to(R))))
 if result.returncode:
  okay=False; print('FALLO: revisar '+runs[-1]['log'],flush=True);break
report=dict(schema_version='4.1.0',mode=mode,passed=okay,python=platform.python_version(),runs=runs,
            meaning='Ejecucion y verificacion interna. No implica dispositivo aceptado. El manifiesto de entrega no se regenera automaticamente.')
(R/f'validacion/reproduccion_{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('REPRODUCCION_CORRECTA' if okay else 'REPRODUCCION_CON_FALLO')
if not okay: raise SystemExit(1)
