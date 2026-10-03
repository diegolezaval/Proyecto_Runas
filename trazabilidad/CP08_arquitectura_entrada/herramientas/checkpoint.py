"""Empaqueta sin alterar las fuentes archivadas; hashes deterministas, CRC y estado."""
from pathlib import Path
import argparse, hashlib, json, zipfile
R=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files():return sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.lock'] and p.parent!=R/'validacion/P06/no_radial/cache')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path)
    parser.add_argument('--estados-salida',type=Path,help='ZIP complementario para los estados de acceso lineal; extraer ambos en la misma carpeta')
    parser.add_argument('--verificar',action='store_true')
    args=parser.parse_args(); manifest=R/'MANIFIESTO_SHA256.json'
    state=json.loads((R/'estado_progreso.json').read_text())
    if args.verificar:
        expected=json.loads(manifest.read_text())['files']
        actual={str(p.relative_to(R)):digest(p) for p in files() if p!=manifest}
        bad=[k for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k)]
        print(json.dumps(dict(passed=not bad,files=len(actual),failures=bad)))
        if bad:raise SystemExit(1)
        return
    if not args.salida:parser.error('--salida o --verificar requerido')
    if args.salida.resolve().is_relative_to(R):raise ValueError('ZIP debe quedar fuera del proyecto')
    if args.estados_salida:
        if args.estados_salida.resolve().is_relative_to(R):raise ValueError('ZIP de estados debe quedar fuera del proyecto')
        if args.estados_salida.resolve()==args.salida.resolve():raise ValueError('Los ZIP deben tener rutas distintas')
    assert digest(R/'trazabilidad/fuente_M2_4_1.zip')==state['baseline_sha256']
    original=json.loads((R/'hoja_ruta_original/MANIFIESTO_SHA256.json').read_text())['files']
    assert all(digest(R/'hoja_ruta_original'/k)==v for k,v in original.items())
    for stage in state['stages']:
        if stage['status']=='COMPLETADA':
            assert stage['evidence'] and stage['checkpoint'] and stage['reopen_conditions'],stage['id']
            assert all((R/e).exists() for e in stage['evidence']),stage['id']
    manifest.write_text(json.dumps(dict(algorithm='SHA256',edition=state['project_version'],checkpoint=state['checkpoint'],
        excluded=['MANIFIESTO_SHA256.json','**/__pycache__/**','**/*.pyc','**/*.lock','validacion/P06/no_radial/cache/**'],
        files={str(p.relative_to(R)):digest(p) for p in files() if p!=manifest}),ensure_ascii=False,indent=2)+'\n')
    payload=files()
    def separate(p):
        return args.estados_salida and p.parent==R/'validacion/P06/acceso_lineal' and p.name.endswith('_estado.npz')
    groups=[(args.salida,[p for p in payload if not separate(p)])]
    if args.estados_salida:groups.append((args.estados_salida,[p for p in payload if separate(p)]))
    seen=set();receipts=[]
    for output,entries in groups:
        output.parent.mkdir(exist_ok=True,parents=True)
        with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in entries:
                info=zipfile.ZipInfo('Proyecto_Runas/'+str(p.relative_to(R)),date_time=(2026,9,28,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,p.read_bytes(),compresslevel=9)
        with zipfile.ZipFile(output) as z:
            assert z.testzip() is None
            for name in z.namelist():
                assert name not in seen,name
                seen.add(name)
                p=R/name.removeprefix('Proyecto_Runas/')
                assert hashlib.sha256(z.read(name)).hexdigest()==digest(p),name
        receipts.append(dict(path=str(output.resolve()),bytes=output.stat().st_size,sha256=digest(output),files=len(entries)))
    assert seen=={'Proyecto_Runas/'+str(p.relative_to(R)) for p in payload}
    print(json.dumps(dict(archives=receipts,checkpoint=state['checkpoint'],combined_files=len(seen),
        combined_integrity_passed=True,extraction='Extraer todos los ZIP en la misma carpeta; la union reconstruye Proyecto_Runas completo.'),ensure_ascii=False))
if __name__=='__main__':main()
