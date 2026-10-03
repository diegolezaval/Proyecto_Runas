"""Figuras de datos guardados: no recalcula ninguna campaña física."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
b=json.loads((R/'validacion/P06/rama/resultados.json').read_text())['rows']
v=json.loads((R/'validacion/validez/resultados.json').read_text())
fig,ax=plt.subplots(1,3,figsize=(13,4.1),layout='constrained')
w=np.array([r['omega'] for r in b])
ax[0].semilogy(w,[r['Q'] for r in b],'o-',color='#245e89',ms=4)
ax[0].set(xlabel='Frecuencia ω',ylabel='Carga Q',title='23 soluciones de la rama')
ax[1].plot(w,[r['fixed_charge_min'] for r in b],'o-',color='#245e89',ms=4)
ax[1].axhline(0,color='#b44131',lw=1);ax[1].set(xlabel='Frecuencia ω',ylabel='Mínimo del Hessiano a Q fija',title='Malla finita: control negativo')
ax[2].plot(w,[r['E_over_Q'] for r in b],'o-',color='#245e89',ms=4)
ax[2].axhline(1,color='#b44131',lw=1,label='Carga libre: E/Q = m = 1')
ax[2].set(xlabel='Frecuencia ω',ylabel='E/Q',title='Ligadura ≠ energía recuperable');ax[2].legend(fontsize=8)
for a in ax:a.grid(alpha=.18)
fig.suptitle('M2 · Rama de Reserva — evidencia numérica, sin cierre de estabilidad 3D',fontsize=12)
fig.savefig(R/'graficos/CP03_rama_reserva.svg');fig.savefig(R/'validacion/CP03_rama_reserva.png',dpi=140);plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(10.5,4.1),layout='constrained')
names=['m','M','lambda0','g','h'];y=np.arange(5)
for sign,dy,color,label in [(-1,-.16,'#245e89','−0.01 %'),(1,.16,'#d28b2d','+0.01 %')]:
 vals=[next(r for r in v['independent_sensitivity'] if r['parameter']==p and np.sign(r['relative_offset'])==sign)['susceptibility_logQ'] for p in names]
 ax[0].barh(y+dy,vals,height=.3,color=color,label=label)
ax[0].set_yticks(y,['m','M','λ₀','g','h']);ax[0].set(xlabel='Δln Q / Δln p (secante)',title='Sensibilidad: ω = 0.9');ax[0].legend(fontsize=8)
for mode,color in [(.2,'#245e89'),(.6,'#d28b2d'),(.9,'#b44131')]:
 rr=[r for r in v['capillary_extension'] if r['dimension']==2 and r['kR']==mode]
 ax[1].plot([r['norm_radius'] for r in rr],[100*r['relative_capillary_error'] for r in rr],'o-',label=f'kR = {mode}',color=color)
ax[1].axhline(10,color='#666',ls=':',label='Nivel 10 %');ax[1].set(xlabel='Radio de norma',ylabel='Error capilar (%)',title='Tubo: error de la aproximación');ax[1].legend(fontsize=8)
for a in ax:a.grid(alpha=.18)
fig.suptitle('M2 · Carta muestreada — no certifica los puntos intermedios',fontsize=12)
fig.savefig(R/'graficos/CP03_validez.svg');fig.savefig(R/'validacion/CP03_validez.png',dpi=140);plt.close(fig)
print('Dos SVG y dos PNG generados desde los resultados existentes.')
