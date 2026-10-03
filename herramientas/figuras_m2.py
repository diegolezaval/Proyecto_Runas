"""Figuras científicas SVG a partir de resultados, sin datos ilustrativos añadidos."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none',
 'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold',
 'axes.labelcolor':'#243547','text.color':'#243547','axes.edgecolor':'#adb8c1',
 'figure.facecolor':'white','axes.grid':True,'grid.alpha':.2})
q=json.loads((R/'validacion/cierre_m2.json').read_text());t=json.loads((R/'validacion/guia_m2.json').read_text())
d=json.loads((R/'validacion/contrastes_r1.json').read_text())
fig,ax=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
f=np.loadtxt(R/'validacion/m2_guia_perfil.csv',delimiter=',',skiprows=1)
ax[0].plot(f[:,0],f[:,1],color='#246f92',label=r'$f(\rho)$')
ax[0].plot(f[:,0],-f[:,3],color='#ba672d',label=r'$-z_s(\rho)$')
ax[0].set(xlim=(0,18),xlabel=r'Radio transversal $\rho/\ell_0$',ylabel='Amplitud adimensional',title='Perfil autosostenido de dos campos')
ax[0].legend(frameon=False)
band=t['growth_band'];k=np.array([x['k'] for x in band]);growth=np.array([max(0,x['growth']) for x in band]);kc=t['spectral_convergence'][-2]['kcrit_from_H']
ax[1].plot(k,growth,'o-',markersize=3,color='#b94338',label='Generador completo M2')
ax[1].plot(k[k<.1],np.sqrt(-t['charge_derivative'][-1]['long_wave_cL_squared'])*k[k<.1],ls='--',color='#246f92',label='Límite de onda larga')
ax[1].axvline(kc,color='#687c8b',ls=':',label=r'$k_c\simeq0.22656$')
ax[1].set(xlabel=r'Número de onda axial $k\ell_0$',ylabel=r'Tasa de crecimiento $\sigma t_0$',title='Inestabilidad longitudinal convergente',ylim=(-.0005,.019))
ax[1].legend(frameon=False,fontsize=9,loc='lower center')
fig.suptitle('M2 sostiene el tubo, pero no lo estabiliza como guía',fontsize=16,fontweight='bold')
fig.savefig(R/'graficos/M2_guia_inestable.svg');plt.close(fig)

fig,ax=plt.subplots(2,2,figsize=(12,8),layout='constrained')
f=np.loadtxt(R/'validacion/m2_perfil_convergente.csv',delimiter=',',skiprows=1)
ax[0,0].plot(f[:,0],f[:,1],label='Campo complejo',color='#246f92');ax[0,0].plot(f[:,0],-f[:,3],label='− mediador',color='#ba672d')
ax[0,0].set(xlim=(0,25),xlabel=r'$r/\ell_0$',ylabel='Amplitud',title='Q-ball: perfil de referencia');ax[0,0].legend(frameon=False)
rows=[r for r in q['spectra'] if r['ell']==1 and r['radius']==40]
h=np.array([r['dx'] for r in rows]);lam=np.abs([r['H_amplitude'][0] for r in rows])
ax[0,1].loglog(h,lam,'o-',color='#246f92',label='Error del modo de traslación')
ax[0,1].loglog(h,lam[-1]*(h/h[-1])**2,'--',color='#ba672d',label=r'Referencia $h^2$')
ax[0,1].set(xlabel='Paso radial h',ylabel=r'$|\lambda_{min}(H_1)|$',title='El falso modo negativo tiende a cero');ax[0,1].legend(frameon=False,fontsize=9)
for n,color in [(800,'#ba672d'),(1600,'#246f92')]:
    ts=np.loadtxt(R/f'validacion/m2_dinamica_{n}.csv',delimiter=',',skiprows=1)
    ax[1,0].plot(ts[:,0],(ts[:,1]/ts[0,1]-1)*1e8,label=f'{n} celdas',color=color)
ax[1,0].set(xlabel=r'Tiempo $\tau=t/t_0$',ylabel=r'$(E/E_0-1)\times10^8$',title='Dinámica no lineal: conservación de energía');ax[1,0].legend(frameon=False)
rows=[r for r in q['spectra'] if r['ell']==2 and r['radius']==40]
hs=np.array([r['dx'] for r in rows]);om=np.array([min(abs(v['imag']) for v in r['selected_generator_eigenvalues']) for r in rows])
ax[1,1].plot(hs**2,om,'o-',color='#246f92')
ax[1,1].ticklabel_format(useOffset=False,axis='y')
ax[1,1].set(xlabel=r'$h^2$',ylabel=r'Frecuencia $\Omega t_0$',title='Modo cuadrupolar ligado: convergencia')
fig.suptitle('M2: evidencia de campo, espectro y evolución',fontsize=16,fontweight='bold')
fig.savefig(R/'graficos/M2_evidencia_numerica.svg');plt.close(fig)

fig,ax=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
nu=np.linspace(-1.2e6,1.2e6,1601);length=d['P04']['stub_length_m_planar'];xx=2*np.pi*nu*length/1e7
refl=np.sin(xx)**2/(1+3*np.cos(xx)**2)
ax[0].plot(nu/1e6,refl*1e6,color='#246f92',label='Reflexión del grafo')
ax[0].axhline(d['P04']['R1_bulk_loss_fraction']*1e6,color='#ba672d',ls='--',label='Presupuesto de referencia')
ax[0].axvspan(-.5,.5,color='#246f92',alpha=.08,label='Banda total 1 MHz')
ax[0].set(xlabel='Desintonía (MHz)',ylabel='Fracción reflejada (ppm)',title='Canal ideal con U cerrado: cálculo condicionado');ax[0].legend(frameon=False,fontsize=9)
Om=np.linspace(0,.12,300)
ax[1].plot(Om,np.where(Om<=.1,np.sqrt(np.maximum(0,1-(.9+Om)**2)),np.nan),color='#246f92',label=r'$\kappa_+$ (evanescente)')
ax[1].plot(Om,np.sqrt(1-(.9-Om)**2),color='#ba672d',label=r'$\kappa_-$')
ax[1].axvspan(.1,.12,color='#b94338',alpha=.12,label='Canal + propagante')
ax[1].set(xlabel=r'Frecuencia relativa $\Omega t_0$',ylabel=r'Decaimiento exterior $\kappa\ell_0$',title='Exterior M2: condición distinta de Neumann');ax[1].legend(frameon=False,fontsize=9)
fig.suptitle('Respuesta del grafo y condición del exterior son problemas distintos',fontsize=15,fontweight='bold')
fig.savefig(R/'graficos/M2_terminal_y_canal.svg');plt.close(fig)
print('Tres figuras SVG científicas generadas desde los resultados.')
