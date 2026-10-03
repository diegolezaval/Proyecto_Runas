"""Regenera SVG, fichas, tablas e integrado a partir de datos y capítulos fuente."""
from pathlib import Path
import json, html, math, re
from geometria import bounds,ends,topology
R=Path(__file__).resolve().parents[1]
def load(n):return json.loads((R/'datos'/n).read_text())
g=load('geometria.json');p=load('parametros.json');models=load('modelos.json')['models'];mods=load('modulos.json')['modules'];matching={x['id']:x for x in load('correspondencia.json')['runes']}
acceptance={x['id']:x for x in load('aceptacion_m2.json')['runes']}
esc=html.escape
colors={'T':'#256d85','R':'#a35d25','N':'#624ba0'}
def paths(r,technical=False):
 out=[]
 ep=ends(g,r)
 joined_points={ep[e] for j in r['joins'] for e in j}
 mask_id='joinmask-'+r['id']
 if joined_points:
  bx0,by0,bx1,by1=bounds(g,r)
  holes=''.join(f'<circle cx="{float(x)}" cy="{float(y)}" r=".18" fill="black"/>' for x,y in joined_points)
  out.append(f'<defs><mask id="{mask_id}" maskUnits="userSpaceOnUse" x="{bx0-1}" y="{by0-1}" width="{bx1-bx0+2}" height="{by1-by0+2}"><rect x="{bx0-1}" y="{by0-1}" width="{bx1-bx0+2}" height="{by1-by0+2}" fill="white"/>{holes}</mask></defs>')
 for i in r['instances']:
  from fractions import Fraction
  a,b,tx,ty=[float(Fraction(v)) for v in i['transform_fraction']];scale=math.hypot(a,b);stroke=.085/scale
  d=g['source_pieces'][i['piece']]['path'];tr=f'matrix({a:.12g} {b:.12g} {-b:.12g} {a:.12g} {tx:.12g} {ty:.12g})'
  under=f'<path d="{d}" transform="{tr}" fill="none" stroke="white" stroke-width="{stroke*2.5:.8g}" stroke-linejoin="round" stroke-linecap="round"/>'
  out.append(f'<g mask="url(#{mask_id})">{under}</g>' if joined_points else under)
  color=colors[i['piece']] if technical else '#182634'
  out.append(f'<path d="{d}" transform="{tr}" fill="none" stroke="{color}" stroke-width="{stroke:.8g}" stroke-linejoin="round" stroke-linecap="round"/>')
 if technical:
  ep=ends(g,r);joined=set(e for j in r['joins'] for e in j)
  seen=set()
  for e,xy in ep.items():
   x,y=map(float,xy)
   if xy not in seen:
    out.append(f'<circle cx="{x}" cy="{y}" r=".09" fill="{("#23384c" if e in joined else "#c02e3c")}" stroke="white" stroke-width=".025"/>');seen.add(xy)
  for pt in r['ports']:
   if pt['end'] in ep:
    x,y=map(float,ep[pt['end']]);out.append(f'<text x="{x+.14}" y="{y-.14}" font-size=".3" font-family="sans-serif" fill="#c02e3c">{esc(pt["name"])}</text>')
 return '\n'.join(out)

def svg(r,technical=False):
 x0,y0,x1,y1=bounds(g,r);pad=.7;w=x1-x0+2*pad;h=y1-y0+2*pad
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-pad} {y0-pad} {w} {h}" width="640" height="640" role="img"><title>{esc(r["id"]+" "+r["name"])}</title><desc>Proyección canónica. Uniones declaradas en JSON; los cruces interiores no unen.</desc><rect x="{x0-pad}" y="{y0-pad}" width="{w}" height="{h}" fill="white"/>{paths(r,technical)}</svg>'

for r,m,c in zip(g['runes'],mods,models):
 rid=r['id'];(R/f'graficos/runas/{rid}.svg').write_text(svg(r));(R/f'graficos/tecnicos/{rid}.svg').write_text(svg(r,True))
 top=topology(g,r);bb=bounds(g,r)
 s=f'# {rid} · {r["name"]}\n\n{m["function"]}\n\n![Geometría de {r["name"]}](../graficos/tecnicos/{rid}.svg)\n\n## Registro geométrico\n\nLa escala física se declara en O.2; la figura representa una proyección. T: azul, R: ocre, N: violeta. Los puntos oscuros son uniones declaradas; los rojos, extremos libres.\n\n'
 a=acceptance[rid]
 notice='**Estado M2: '+('tubo libre refutado por inestabilidad' if a['current_realization_status']=='refutada_por_inestabilidad' else 'realización completa no demostrada')+'.** '+a['reason']+' La función y los valores siguientes son objetivos revisables. Véanse las secciones '+a['evidence_sections']+'.\n\n'
 s=s.replace('\n\n','\n\n'+notice,1)
 s+='| Pieza | a | b | tₓ | tᵧ | Capa de cruce |\n|---|---:|---:|---:|---:|---:|\n'
 for i in r['instances']:s+='| '+i['id']+' | '+' | '.join(i['transform_fraction'])+' | '+str(i['crossing_lane'])+' |\n'
 s+='\nTransformación: \\(x_g=ax-by+t_x,\\ y_g=bx+ay+t_y\\). Las fracciones son los valores canónicos, no redondeos de calibración física.\n\n'
 s+='Uniones: '+('; '.join(' ↔ '.join(j) for j in r['joins']) or 'ninguna')+'.\n\n'
 s+=f'{top["pieces"]} piezas; {top["connected_components"]} componente(s) conexa(s); {top["independent_cycles"]} ciclo(s) independiente(s); {top["free_ends"]} extremo(s) libre(s). Caja del eje: {bb[2]-bb[0]:.6f} × {bb[3]-bb[1]:.6f} u, sin espesor de trazo.\n\n'
 if rid=='P-20':s+='**Corrección de esta edición:** R₂ se reorienta para eliminar la coincidencia de un tramo con N₂; se conservan las cinco piezas y los dos ciclos.\n\n'
 s+='## Puertos y terminales\n\n'
 if r['ports']:
  s+='| Puerto | Extremo | Intercambio | Función |\n|---|---|---|---|\n'
  for q in r['ports']:s+='| '+' | '.join(q[k].replace('|','/') for k in ['name','end','exchange','role'])+' |\n'
 else:s+='No hay extremos libres asignados a puertos. La alimentación, el control y la interacción usan terminales del estado desplegado; su localización debe declararse en el montaje.\n'
 if c.get('field_regions'):
  s+='\n| Región funcional | Localización | Intercambio |\n|---|---|---|\n'
  for region in c['field_regions']:s+='| '+' | '.join(region[k] for k in ['name','location','exchange'])+' |\n'
 s+='\nLos puertos mixtos se descomponen en subcanales tipados. La región de aplicación y los intercambios distribuidos forman parte del montaje aunque no sean extremos de la plantilla.\n\n'
 s+='## Contrato dinámico de referencia\n\n'
 s+='- Estados: '+', '.join(c['states'])+'.\n- Entradas: '+', '.join(c['inputs'])+'.\n- Salidas: '+', '.join(c['outputs'])+'.\n- Dominio: '+c['domain']+'.\n\n'
 s+='`'+c['equation']+'`\n\n'+c['limitation']+'\n\n'
 s+='Grupos de parámetros: '+', '.join('`'+x+'`' for x in c['parameter_groups'])+' en `datos/parametros.json`. El contrato reducido no constituye una realización microscópica demostrada.\n\n'
 for title,body in m['sections'].items():s+='## '+title+'\n\n'+body+'\n\n'
 e=matching[rid]
 s+='## Correspondencia microscópica\n\n'+e['mechanism']+'.\n\n'
 s+='**Estado físico:** '+e['microscopic_state']+'.\n\n**Coeficientes:** '+e['matching_coefficients']+'.\n\n'
 s+='**Comportamiento resultante:** '+e['macroscopic_behavior']+'\n\n'
 s+='**Comprobación disponible:** '+e['checked_sector']+'. Véase '+e['derivation']+'.\n\n'
 s+='**Requisito de realización:** '+e['remaining_requirement']+'\n\n'
 s+='## Aceptación\n\nComprobar geometría y puertos, respuesta a baja potencia, balance de recursos y transición de retirada. El montaje debe satisfacer las magnitudes del contrato y el dominio de su receta. La precisión del SVG no demuestra estabilidad ni rendimiento del estado físico.\n'
 (R/f'fichas/{rid}.md').write_text(s)

for piece,src in g['source_pieces'].items():
 rr={'id':piece,'name':{'T':'Tránsito','R':'Repliegue','N':'Nexo'}[piece],'instances':[{'id':piece,'piece':piece,'transform_fraction':['1','0','0','0'],'crossing_lane':0}],'joins':[],'ports':[],'free_ends':[]}
 (R/f'graficos/elementales/{piece}.svg').write_text(svg(rr,True))
# Full atlas is vector and readable at arbitrary zoom.
W,H=1200,1620;out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><title>Atlas de las 24 primordiales</title><rect width="100%" height="100%" fill="#f4f6f8"/><text x="32" y="44" font-size="28" font-family="sans-serif" fill="#182634">RÚNICA · Atlas canónico 4.1</text><text x="32" y="72" font-size="14" font-family="sans-serif" fill="#516272">Geometría derivada de datos racionales · Cruces interiores separados</text>']
for k,r in enumerate(g['runes']):
 col,row=k%4,k//4;x=col*300;y=100+row*250;bb=bounds(g,r);scale=min(240/(bb[2]-bb[0]+1),175/(bb[3]-bb[1]+1));tx=x+150-scale*(bb[0]+bb[2])/2;ty=y+105-scale*(bb[1]+bb[3])/2
 out.append(f'<rect x="{x+10}" y="{y}" width="280" height="235" rx="12" fill="white"/><g transform="translate({tx},{ty}) scale({scale})">{paths(r)}</g><text x="{x+150}" y="{y+219}" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#182634">{esc(r["id"]+" · "+r["name"])}</text>')
out.append('</svg>');(R/'graficos/atlas.svg').write_text('\n'.join(out))
# All scalar parameters get a human-readable table generated from canonical JSON.
s='# Parámetros de referencia\n\nPerfil R1. Los valores adoptados son objetivos de diseño. Las constantes conservan su clasificación propia; no se infiere calibración por tener muchas cifras.\n\n'
for group,vals in p.items():
 if not isinstance(vals,dict) or group=='microscopic_benchmark':continue
 s+='## '+group+'\n\n| Parámetro | Valor | Unidad | Significado | Estado |\n|---|---:|---|---|---|\n'
 for key,v in vals.items():
  if isinstance(v,dict) and 'value' in v:s+=f'| {key} | {v["value"]:g} | {v["unit"]} | {v["meaning"]} | {v["status"]} |\n'
 s+='\n'
(R/'tratado/05_parametros.md').write_text(s)
s='# Revisión de los 50 hallazgos\n\nOrden de prioridad conservado desde la revisión. «Corregido» se refiere al documento; «verificado reducido» a un cálculo bajo sus hipótesis. Los estados abiertos no se convierten en resultados físicos por adoptar un parámetro.\n\n| Prioridad | Hallazgo | Acción | Estado | Evidencia |\n|---:|---|---|---|---|\n'
for v in load('revision.json')['findings']:s+='| '+' | '.join(str(v[k]).replace('|','/') for k in ['priority','issue','action','status','evidence'])+' |\n'
(R/'tratado/06_revision.md').write_text(s)
# The integrated document is a generated convenience copy.
parts=['# Rúnica · Documento integrado\n\nEdición de referencia 4.1, ampliada por los checkpoints 4.2. Estado vigente en ESTADO_ACTUAL.md. Archivo generado: editar capítulos y JSON fuente y ejecutar `herramientas/generar.py`.\n\n**Resultado vigente:** no hay un dispositivo M2/R1 completamente derivado. Los capítulos 20–21 derivan la interfaz y el límite capilar del mismo M2. El tubo libre continúa siendo longitudinalmente inestable; no hay un terminal físico ni una preparación completa demostrados. Empieza por [M2_RESULTADO.md](M2_RESULTADO.md) para conocer la evidencia y sus límites.\n\n![Atlas canónico](graficos/atlas.svg)\n\n']
for file in sorted((R/'tratado').glob('*.md')):parts.append(re.sub(r'\]\(([^)]+)\)', lambda m: ']('+str((file.parent/m.group(1)).relative_to(R))+')' if not re.match(r'https?://|#|mailto:',m.group(1)) and not m.group(1).startswith('../') else m.group(0).replace('(../','('), file.read_text()))
parts.append('# Repertorio de primordiales\n\n')
for file in sorted((R/'fichas').glob('*.md')):parts.append(re.sub(r'\]\(([^)]+)\)', lambda m: ']('+str((file.parent/m.group(1)).relative_to(R))+')' if not re.match(r'https?://|#|mailto:',m.group(1)) and not m.group(1).startswith('../') else m.group(0).replace('(../','('), file.read_text()))
(R/'Runica_Tratado_integrado.md').write_text('\n\n---\n\n'.join(parts))
print('Generados: 24 fichas, 52 SVG de geometría, tablas y tratado integrado.')
