"""Manifiesto, diferencias respecto de la fuente y ZIP reproducible de la entrega.
Ejemplos: python herramientas/empaquetar.py --verificar
          python herramientas/empaquetar.py --salida ../Proyecto_Runas_M2_4_1.zip
No ejecuta ni declara validados los calculos: deben verificarse antes.
"""
from pathlib import Path
import argparse, hashlib, json, zipfile
R=Path(__file__).resolve().parents[1]
MANIFEST=R/'MANIFIESTO_SHA256.json'
DIFF=R/'trazabilidad/cambios_archivos.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def files():
 return sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def verify():
 data=json.loads(MANIFEST.read_text())
 expected=data['files']; actual={str(p.relative_to(R)):sha(p) for p in files() if p!=MANIFEST}
 failures=[key for key in sorted(set(actual)|set(expected)) if actual.get(key)!=expected.get(key)]
 print(json.dumps({'manifest_passed':not failures,'files':len(actual),'failures':failures},ensure_ascii=False,indent=2))
 if failures:raise SystemExit(1)
p=argparse.ArgumentParser(description=__doc__)
g=p.add_mutually_exclusive_group(required=True)
g.add_argument('--verificar',action='store_true');g.add_argument('--salida',type=Path)
a=p.parse_args()
if a.verificar:verify();raise SystemExit(0)
destination=a.salida.resolve()
if destination.is_relative_to(R):raise SystemExit('El ZIP debe quedar fuera de la carpeta que se empaqueta.')
# Refuse to package a known failed validation or a stale scientific benchmark.
for name in ['validacion/informe.json','validacion/verificacion_m2.json','validacion/capilaridad/verificacion.json','validacion/reproduccion_completa.json']:
 if not json.loads((R/name).read_text())['passed']:raise SystemExit('Validacion fallida: '+name)
science=json.loads((R/'validacion/capilaridad/resultados.json').read_text())
if science['theta_sha256']!=sha(R/'datos/theta_comun.json'):raise SystemExit('Theta cambio despues del calculo capilar.')
audit=json.loads((R/'trazabilidad/auditoria_entrada.json').read_text())
if sha(R/'trazabilidad/fuente_M2_4_0.zip')!=audit['source_sha256']:raise SystemExit('Fuente archivada alterada.')
original={r['path']:r['sha256'] for r in audit['files']}
excluded={'MANIFIESTO_SHA256.json','trazabilidad/cambios_archivos.json'}
current={str(q.relative_to(R)):sha(q) for q in files() if str(q.relative_to(R)) not in excluded}
rows=[]
for key in sorted((set(original)|set(current))-excluded):
 before=original.get(key); after=current.get(key)
 rows.append(dict(path=key,status='added' if before is None else 'removed' if after is None else 'unchanged' if before==after else 'modified',source_sha256=before,current_sha256=after))
write(DIFF,dict(schema_version='4.1.0',source_zip_sha256=audit['source_sha256'],excluded_to_avoid_circular_hashes=sorted(excluded),
                counts={k:sum(r['status']==k for r in rows) for k in ['added','removed','modified','unchanged']},files=rows))
write(MANIFEST,dict(algorithm='SHA256',edition='4.1.0',excluded=['MANIFIESTO_SHA256.json','**/__pycache__/**','**/*.pyc'],
                   files={str(q.relative_to(R)):sha(q) for q in files() if q!=MANIFEST}))
verify()
destination.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as out:
 for q in files():
  info=zipfile.ZipInfo('Proyecto_Runas/'+str(q.relative_to(R)),date_time=(2026,9,27,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
  out.writestr(info,q.read_bytes(),compresslevel=9)
with zipfile.ZipFile(destination) as z:
 bad=z.testzip()
 if bad:raise SystemExit('CRC fallido: '+bad)
print(json.dumps({'zip':str(destination),'bytes':destination.stat().st_size,'sha256':sha(destination),'entries':len(files())},ensure_ascii=False,indent=2))
