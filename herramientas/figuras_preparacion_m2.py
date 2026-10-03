"""Figuras del ensayo radial; sólo usa CSV y JSON guardados."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'validacion/P06/preparacion'
d=json.loads((O/'resultados.json').read_text())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,ax=plt.subplots(1,3,figsize=(13,4.1),layout='constrained')
for h,col in [(.2,'#d28b2d'),(.1,'#245e89')]:
 r=next(x for x in d['records'] if x['configuration']['tmax']==1200 and x['configuration']['dx']==h)
 a=np.loadtxt(O/f"{r['run']}_tiempo.csv",delimiter=',',skiprows=1)
 ax[0].plot(a[:,0],a[:,4]/a[0,2],color=col,label=f'h = {h}')
 ax[2].semilogy(a[:,0],np.maximum(abs(a[:,1]/a[0,1]-1),1e-16),color=col,label=f'h = {h}')
ax[0].axhline(.9,color='#b44131',ls=':',label='Umbral del ensayo: 90 %');ax[0].set(xlabel='Tiempo t',ylabel='Q dentro de r = 40 / Q inicial',title='Carga localizada');ax[0].legend(fontsize=8)
best=next(x for x in d['records'] if x['configuration']['tmax']==1200 and x['configuration']['dx']==.1)
init=np.loadtxt(O/f"{best['run']}_inicial.csv",delimiter=',',skiprows=1);end=np.loadtxt(O/f"{best['run']}_final.csv",delimiter=',',skiprows=1);ref=np.loadtxt(O/f"{best['run']}_perfil_referencia.csv",delimiter=',',skiprows=1)
sel=end[:,0]<25
ax[1].plot(init[sel,0],abs(init[sel,1]+1j*init[sel,2]),color='#999',ls=':',label='Gaussiana inicial')
ax[1].plot(end[sel,0],abs(end[sel,1]+1j*end[sel,2]),color='#245e89',label='Evolución a t = 1200')
ax[1].plot(ref[:,0],ref[:,1],color='#d28b2d',ls='--',label='Equilibrio a igual Q media')
ax[1].set(xlim=(0,25),xlabel='Radio r',ylabel='Amplitud |Φ|',title='Perfil final y referencia');ax[1].legend(fontsize=8)
ax[2].set(xlabel='Tiempo t',ylabel='|E(t) / E(0) − 1|',title='Deriva energética muestreada');ax[2].legend(fontsize=8)
for a in ax:a.grid(alpha=.18)
fig.suptitle('M2 · Asentamiento radial desde un paquete cargado — E04 / RES1 parciales',fontsize=12)
fig.savefig(R/'graficos/CP04_preparacion_radial.svg');fig.savefig(R/'validacion/CP04_preparacion_radial.png',dpi=140)
print('SVG y PNG de preparación generados.')
