"""Prepare immutable public boundary evidence and bounded Git tree payloads."""
from pathlib import Path
import argparse, json, hashlib

def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--home',type=Path,required=True);ap.add_argument('--boundary',type=int,required=True)
    args=ap.parse_args();home=args.home.resolve();t=args.boundary
    meta=read(home/'preregistration/nueva_identidad.json');proof=read(home/'proofs'/('tau%04d_permanent.json'%t))
    assert proof['time']==t and proof['passed'] and proof['all_payload_hashes_verified'] and proof['independent_extracted_audit']['passed']
    assert proof['execution_uuid']==meta['execution_uuid'] and proof['execution_run_id']==meta['execution_run_id']
    public={k:v for k,v in proof.items() if k not in ['library_file_id','file_id']}
    p=home/'proofs'/('tau%04d_publica.json'%t)
    if p.exists():assert read(p)==public
    else:
        temp=p.with_suffix('.tmp');temp.write_text(json.dumps(public,indent=2,ensure_ascii=False)+'\n');temp.replace(p)
    prefix='trazabilidad/CP12_recuperacion_independiente/'+meta['execution_uuid'][:12]+'/'
    files=[p,home/'publish_boundary.py',home/'analysis/ADAPTACION_RECUPERACION.md']
    for f in [home/'analysis/prefix'/('tau%04d.json'%t),home/'analysis/condicional'/('tau%04d'%t)/'resultados.json',home/'analysis/jacobiano_local'/('tau%04d.json'%t)]:
        if f.exists():files.append(f)
    if t==48:
        for directory in ['causal','prefix','condicional','jacobiano_local']:
            files.extend(sorted((home/'analysis'/directory).glob('*.py')))
            files.extend(sorted((home/'analysis'/directory).glob('*.md')))
    if t==160:
        for d in sorted((home/'analysis/causal').glob('lectura__*')):
            files.extend(sorted(d.glob('*.json')))
    for directory in ['dispersion_candidato','referencia_CP10','backend_candidato']:
        if (home/'analysis'/directory).exists():
            for pattern in ['*.py','*.md','*.json']:
                files.extend(sorted((home/'analysis'/directory).glob(pattern)))
    entries=[dict(path=prefix+f.relative_to(home).as_posix(),mode='100644',type='blob',content=f.read_text()) for f in dict.fromkeys(files)]
    reading=home/'analysis/prefix'/('tau%04d.json'%t)
    text=f'''# CP12: recuperación independiente {meta['execution_uuid'][:12]}

Última frontera recuperada y auditada permanentemente: **τ{t}**. Rama `{meta['branch']}`; identidad `{meta['execution_run_id']}`. Estado SHA256 `{proof['state_sha256']}`; configuración `{proof['configuration_sha256']}`; cápsula `{proof['zip_sha256']}`, {proof['zip_bytes']} bytes. Pasan hashes completos, controles, balances, observadores y auditor original. Los prefijos CP10 son exactos.

Esta instancia parte de la cápsula independiente τ48 de ab914d1d0470, cuya ascendencia es el τ24 original. No repite los segmentos certificados hasta τ48 y no atribuye la ascendencia a su propio trabajador. Los ejecutores anteriores se consideran potencialmente activos y no autoritativos; no se consultan ni controlan. Rutas de escritura, bloqueos, identidad, recibos y cápsulas son distintos. Main, PR #2, ramas y evidencias anteriores quedan intactos; el PR #2 sigue en borrador. No se usa Actions.

M2, Θ, las catorce fuentes, DOP853, tolerancias, mallas, observadores y puerta original del 2 % permanecen idénticos. Cada frontera se guarda, descarga y audita antes de avanzar. Un latido no certifica un reinicio.
'''
    if reading.exists():
        r=read(reading);text+=f"\nLectura pasiva provisional de τ{t}: error de fases del núcleo χ {r['observed_core_phase_relative_error']:.12g}, cierres en toda la caja {r['full_box_chi_closure']}. No decide la aceptación final ni el inicio causal, que requieren τ160.\n"
    if t<160:text+=f'\nLa continuación autorizada es τ{t}→160. Siguen pendientes reproducción CP10 final exacta, lectura causal final y pruebas de una corrección.\n'
    else:text+='\nLa evolución original ha alcanzado τ160 y se ha auditado CP10 final exacto. La interpretación causal y su revisión se documentan separadamente; alcanzar τ160 no cierra CP12.\n'
    text+='\nLos diagnósticos pasivos conservan resultados negativos. El residuo de r²Y₂m es una pista; su suficiencia global no está probada. El candidato variacional no se ha aplicado a estas trayectorias y algunos errores espectrales empeoran. **CP12 permanece abierto.**\n'
    entries.append(dict(path='RECUPERACION_CP12_ACTUAL.md',mode='100644',type='blob',content=text))
    batches=[];batch=[];size=0
    for e in entries:
        n=len(json.dumps(e,ensure_ascii=False).encode())
        if batch and size+n>45000:batches.append(batch);batch=[];size=0
        batch.append(e);size+=n
    if batch:batches.append(batch)
    paths=[]
    for i,b in enumerate(batches):
        out=home/'runtime'/('publish_tau%04d_batch%02d.json'%(t,i));out.write_text(json.dumps(b,ensure_ascii=False));paths.append(str(out))
    print(json.dumps(dict(time=t,entries=len(entries),entries_paths=paths,state_sha256=proof['state_sha256'],CP12_closed=False)))

if __name__=='__main__':main()
