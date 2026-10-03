"""Figuras vectoriales de datos calculados, sin ajuste para acercarlos a la teoria."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
a=json.loads((R/'validacion/capilaridad/resultados.json').read_text())
plt.rcParams.update({'font.size':10,'svg.fonttype':'none','svg.hashsalt':'M2-4.1-capilaridad'})
fig,ax=plt.subplots(2,2,figsize=(12,8.4),constrained_layout=True)
colors={2:'#b35423',3:'#1b6b8a'}; names={2:'Tubo',3:'Esfera'}
p=np.loadtxt(R/'validacion/capilaridad/pared.csv',delimiter=',',skiprows=1)
x,f,fp,z,zp=p.T
ax[0,0].plot(x,f/np.sqrt(a['coexistence']['s']),label=r'$f/\sqrt{s_0}$',color=colors[3])
ax[0,0].plot(x,z/a['coexistence']['z'],label=r'$\chi/\chi_0$',color=colors[2],ls='--')
ax[0,0].set(xlim=(-10,10),xlabel='Coordenada de interfaz',ylabel='Campo normalizado',title='Interfaz de los dos campos')
ax[0,0].legend(frameon=False)
for d in [2,3]:
 rows=[v for v in a['radial_family'] if v['dimension']==d]
 ax[0,1].loglog([v['equimolar_radius'] for v in rows],[abs(v['laplace_ratio']-1) for v in rows],'-o',color=colors[d],label=names[d])
 rows=[v for v in a['spectra'] if v['dimension']==d]
 ax[1,0].loglog([v['equimolar_radius'] for v in rows],[abs(v['relative_prediction_error']) for v in rows],'-o',color=colors[d],label=names[d])
 row=rows[-1]; rate=row['rate_extrapolation']['value']
 ax[1,1].plot([v['dx'] for v in row['samples']],[v['rate']/rate for v in row['samples']],'-o',color=colors[d],label=names[d])
ax[0,1].set(xlabel='Radio equimolar',ylabel=r'$|pR/[(d-1)\tau]-1|$',title='Equilibrio de Laplace')
ax[1,0].set(xlabel='Radio equimolar',ylabel='Error relativo de tasa o frecuencia',title='Predicción capilar frente al espectro M2')
ax[1,1].set(xlabel='Paso espacial h',ylabel='Tasa / extrapolación',title=r'Error de malla: $R_N=128$')
ax[1,1].axhline(1,color='#64748b',lw=.8,ls=':')
for axes in ax.flat:
 axes.grid(alpha=.22); axes.spines[['top','right']].set_visible(False)
for axes in [ax[0,1],ax[1,0],ax[1,1]]: axes.legend(frameon=False)
fig.suptitle('M2 · Un mismo coeficiente de interfaz para dos geometrías',fontsize=16)
fig.savefig(R/'graficos/M2_capilaridad.svg',metadata={'Date':None})
plt.close(fig)
