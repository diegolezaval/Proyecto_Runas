"""Integridad editorial, antecedentes y estados; no ejecuta física histórica."""
from pathlib import Path
import ast, json, re, hashlib, zipfile, argparse
from rutas_documentales import local_target, document_links
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
issues=[]; counts=dict(json=0,python=0,svg=0,local_links=0)
for p in R.rglob('*'):
    if not p.is_file() or '__pycache__' in p.parts:continue
    try:
        if p.suffix=='.json':json.loads(p.read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)));counts['json']+=1
        elif p.suffix=='.py':ast.parse(p.read_text());counts['python']+=1
        elif p.suffix=='.svg':ET.parse(p);counts['svg']+=1
        elif p.suffix=='.md':
            for link in document_links(p):
                if re.match(r'\w+://',link) or link.startswith('#'):continue
                target=link.split('#')[0]
                if not target or ' ' in target or '`' in target:continue
                counts['local_links']+=1
                resolved=local_target(p,link,R)
                if resolved is not None and not resolved.exists():issues.append(f'{p.relative_to(R)}: {link}')
    except Exception as e:issues.append(f'{p.relative_to(R)}: {e}')
state=json.loads((R/'estado_progreso.json').read_text())
base=json.loads((R/'trazabilidad/reanudacion_CP02/estado_progreso.json').read_text())
for name in ['E00','E01']:
    if next(x for x in state['stages'] if x['id']==name)!=next(x for x in base['stages'] if x['id']==name):issues.append(f'{name} modificado sin reapertura')
for stage in state['stages']:
    if stage['status']=='COMPLETADA':
        if not all(stage[k] for k in ['evidence','checkpoint','reopen_conditions']):issues.append(f"Puerta incompleta: {stage['id']}")
    for e in stage['evidence']:
        if not (R/e).exists():issues.append(f'Evidencia ausente: {e}')
source=R/'trazabilidad/fuente_M2_4_1.zip'
if hashlib.sha256(source.read_bytes()).hexdigest()!=state['baseline_sha256']:issues.append('Fuente modificada')
with zipfile.ZipFile(source) as z:
    if z.testzip():issues.append('CRC fuente')
report=dict(schema_version='1.0.0',checkpoint=state['checkpoint'],passed=not issues,counts=counts,issues=issues,
    E00_E01_recalculated=False,scope='Integridad y continuidad editorial; no certificación científica automática.')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--salida',type=Path,help='Guardar informe sólo en una ruta explícita')
parser.add_argument('--solo-lectura',action='store_true',help='Compatibilidad: el modo predeterminado ya es de lectura')
args=parser.parse_args()
if args.salida:
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    args.salida.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if issues:raise SystemExit(1)
