"""Figuras vectoriales de los cálculos; requiere numpy y matplotlib."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'graficos/microscopia';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','figure.facecolor':'white','axes.titleweight':'bold'})
d=json.loads((R/'validacion/correspondencia_micro.json').read_text())
a=np.loadtxt(R/'validacion/perfil_radial.csv',delimiter=',',skiprows=1);b=np.loadtxt(R/'validacion/perfil_dos_campos.csv',delimiter=',',skiprows=1)
fig,ax=plt.subplots(1,2,figsize=(10,4),layout='constrained');ax[0].plot(a[:,0],a[:,1],label='M1: potencial sextico',color='#346a9a');ax[0].plot(b[:,0],b[:,1],label='M2: dos campos',color='#9a5130',ls='--');ax[0].set(xlim=(0,25),xlabel='Radio adimensional',ylabel='Amplitud f',title='Condensado radial');ax[0].legend(frameon=False,fontsize=9);ax[1].plot(b[:,0],b[:,2],color='#6f4ca5');ax[1].set(xlim=(0,25),xlabel='Radio adimensional',ylabel='Mediador reescalado z',title='Mediador de M2');fig.suptitle('Soluciones a la misma frecuencia: ω/m = 0.9',fontsize=13);fig.savefig(O/'perfiles_M1_M2.svg');plt.close(fig)
a=np.loadtxt(R/'validacion/memoria_kerr.csv',delimiter=',',skiprows=1);fig,ax=plt.subplots(figsize=(9,4),layout='constrained');ax.plot(a[:,0],a[:,1],lw=1.8,color='#256d85');ax.axvspan(20,30,color='#c1dede',alpha=.6,label='Pulso de escritura');ax.axvspan(60,70,color='#ead7c3',alpha=.65,label='Pulso de borrado');ax.set(xlabel='Tiempo en unidades de 1/κ',ylabel='Ocupación normalizada',title='Memoria modal: escritura, conservación y borrado');ax.legend(frameon=False,fontsize=9);fig.savefig(O/'memoria_alimentada.svg');plt.close(fig)
k=np.linspace(0,3,401);D=2.;w2=.75;lo=np.sqrt(np.maximum(0,k*k+D-np.sqrt(D*D+4*w2*k*k)));hi=np.sqrt(k*k+D+np.sqrt(D*D+4*w2*k*k));fig,ax=plt.subplots(figsize=(8,4),layout='constrained');ax.plot(k,lo,label='Rama de fase',color='#256d85');ax.plot(k,hi,label='Rama con brecha',color='#985128');ax.plot(k,.5*k,ls=':',color='#89949e',label='Límite acústico: Ω = k/2');ax.set(xlabel='Número de onda k / m',ylabel='Frecuencia Ω / m',title='Dispersión sobre fondo M1 sin presión');ax.legend(frameon=False,fontsize=9);fig.savefig(O/'dispersion.svg');plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for ax,rid in zip(axs,['P-04','P-08','P-16']):
 r=next(x for x in d['graphs'] if x['id']==rid);p=np.array(r['samples'][1]['power_matrix']);im=ax.imshow(p,vmin=0,vmax=1,cmap='Blues');n=len(p);ax.set_xticks(range(n),[str(i+1) for i in range(n)]);ax.set_yticks(range(n),[str(i+1) for i in range(n)]);ax.set(xlabel='Sonda de entrada',ylabel='Sonda de salida',title=rid)
 for i in range(n):
  for j in range(n):ax.text(j,i,f'{p[i,j]:.2f}',ha='center',va='center',fontsize=9,color='white' if p[i,j]>.5 else '#18304b')
fig.suptitle('Fracción de potencia en grafos ideales · k = 1.137/u',fontsize=13);fig.colorbar(im,ax=axs,shrink=.7,label='Potencia / entrada');fig.savefig(O/'dispersion_grafos.svg');plt.close(fig)
print('Cuatro SVG científicos generados.')
