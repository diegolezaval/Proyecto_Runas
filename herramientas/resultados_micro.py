"""Tablas de resultados de la edición microscópica; biblioteca estándar."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(n):return json.loads((R/'validacion'/n).read_text())
a=read('correspondencia_micro.json');b=read('complecion_escalar.json');c=read('preparacion_motor.json')
s='# Resultados de la correspondencia microscópica\n\n'
s+=f'Se superaron {sum(x["passed"] for x in a["checks"])}/{len(a["checks"])} comprobaciones de correspondencia, además de los ensayos de compleción escalar y preparación/motor. Cada prueba tiene un dominio; su suma no demuestra la realización conjunta de las 24 runas.\n\n'
s+='## Dos campos y potencial efectivo\n\n![Perfiles radiales](../graficos/microscopia/perfiles_M1_M2.svg)\n\n| Magnitud M2 | Valor |\n|---|---:|\n'
for k in ['f0','mediator0_rescaled','Ehat','Qhat','E_over_Q','virial_relative','max_residual']:s+=f'| {k} | {b["fine"][k]:.12g} |\n'
s+=f'| Cambio de energía entre dominios | {b["relative_energy_refinement"]:.12g} |\n\nComparación a la misma frecuencia, no a la misma carga. El perfil radial no representa los glifos del atlas.\n\n'
s+='## Modos del condensado\n\n![Dispersión](../graficos/microscopia/dispersion.svg)\n\n'
s+='En M1 sin presión, la velocidad acústica es c/2 y el módulo cortante estático es cero. Las curvas son las ramas exactas de la linealización homogénea, no las velocidades asignadas en R1.\n\n'
s+='| Comprobación radial M1 | Resultado |\n|---|---:|\n'
for k in ['dQ_domega','dE_dQ']:s+=f'| {k} | {a["radial_extended"][k]:.12g} |\n'
s+='\n## Dispersión en las 24 geometrías\n\n![Matrices de tres grafos](../graficos/microscopia/dispersion_grafos.svg)\n\nLas sondas numeran todos los extremos libres del grafo en el orden registrado en JSON. No son una asignación automática de terminales físicos de energía o control. Las guías y uniones ideales son hipótesis del cálculo.\n\n| Glifo | Longitud del eje (u) | Vértices | Sondas | Máximo residuo unitario |\n|---|---:|---:|---:|---:|\n'
for g in a['graphs']:s+=f'| {g["id"]} | {g["length_u"]:.8g} | {g["vertices"]} | {len(g["free_end_order"])} | {max(x["unitarity_error"] for x in g["samples"]):.3g} |\n'
s+='\nP-20 tiene cero sondas de extremos: se calcula el espectro del grafo cerrado mediante elementos finitos. Su matriz vacía de dispersión no cuenta como prueba de funcionamiento. Los terminales funcionales requieren otro problema de acoplamiento. P-04 y P-08 presentan las mismas fracciones de potencia en este ensayo ideal; la diferencia entre sus responsabilidades requiere estados, modos y controles adicionales.\n\n'
s+='## Memoria modal alimentada\n\n![Conmutación de memoria](../graficos/microscopia/memoria_alimentada.svg)\n\n| Estado | Ocupación | Estabilidad lineal |\n|---|---:|---|\n'
for i,x in enumerate(a['memory_kerr']['fixed_points']):s+=f'| {i+1} | {x["occupation_normalized"]:.10g} | '+('Estable' if x['linearly_stable'] else 'Inestable')+' |\n'
s+=f'\nResiduo del balance de ocupación: {a["memory_kerr"]["occupation_balance_residual"]:.3g}. No se ha calculado una tasa de error estocástica ni se afirma memoria pasiva.\n\n'
s+='## Preparación y motor\n\n| Modulación h | Exponente de Floquet | Estimación resonante |\n|---|---:|---:|\n'
for x in c['parametric_pump']['cases']:s+=f'| {x["h"]} | {x["growth_per_time_unit"]:.10g} | {x["resonant_small_h_estimate"]:.10g} |\n'
s+='\nEl bombeo está prescrito; no se deduce del movimiento de una mano.\n\n| Motor de tres niveles | Resultado |\n|---|---:|\n'
for k in ['heat_hot_eV_per_time_unit','heat_cold_eV_per_time_unit','work_eV_per_time_unit','cycle_efficiency','entropy_production_eV_K_per_time_unit','energy_residual']:s+=f'| {k} | {c["three_level_engine"][k]:.12g} |\n'
qc=c['three_level_engine']['quantum_stationary_check']
s+=f'| Diferencia de poblaciones: tasas frente a Lindblad | {qc["population_difference_from_rate_model"]:.3g} |\n'
s+=f'| Autovalor mínimo de la matriz de densidad | {qc["minimum_density_eigenvalue"]:.12g} |\n'
s+=f'| Potencia desde el Hamiltoniano coherente | {qc["coherent_work_output_eV_per_time_unit"]:.12g} |\n'
s+='\nLa eficiencia es del ciclo idealizado y las tasas utilizan una unidad temporal adoptada. No mide rendimiento solar por área ni prueba que M2 tenga los niveles elegidos.\n\n'
s+='## Comprobaciones adicionales\n\n| Prueba | Resultado | Alcance |\n|---|---|---|\n'
for x in a['checks']:s+='| '+x['test']+' | '+('Correcta' if x['passed'] else 'Fallida')+' | '+x['scope']+' |\n'
s+='\n## Datos completos\n\nLos JSON de `validacion/` incluyen matrices, frecuencias, coeficientes, resultados y alcances. Los CSV conservan perfiles y trayectorias. La biblioteca científica utilizada y las pruebas de formato se registran en `validacion/informe.json`.\n'
(R/'tratado/11_resultados_micro.md').write_text(s)
print('Informe microscópico generado.')
