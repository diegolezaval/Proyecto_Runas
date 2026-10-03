# Resultados de la correspondencia microscópica

Se superaron 34/34 comprobaciones de correspondencia, además de los ensayos de compleción escalar y preparación/motor. Cada prueba tiene un dominio; su suma no demuestra la realización conjunta de las 24 runas.

## Dos campos y potencial efectivo

![Perfiles radiales](../graficos/microscopia/perfiles_M1_M2.svg)

| Magnitud M2 | Valor |
|---|---:|
| f0 | 0.746019205344 |
| mediator0_rescaled | -0.0782716722348 |
| Ehat | 2525.6589095 |
| Qhat | 2745.77392021 |
| E_over_Q | 0.91983498383 |
| virial_relative | 1.09067679027e-11 |
| max_residual | 9.77619216078e-09 |
| Cambio de energía entre dominios | 1.98020909291e-09 |

Comparación a la misma frecuencia, no a la misma carga. El perfil radial no representa los glifos del atlas.

## Modos del condensado

![Dispersión](../graficos/microscopia/dispersion.svg)

En M1 sin presión, la velocidad acústica es c/2 y el módulo cortante estático es cero. Las curvas son las ramas exactas de la linealización homogénea, no las velocidades asignadas en R1.

| Comprobación radial M1 | Resultado |
|---|---:|
| dQ_domega | -232934.050889 |
| dE_dQ | 0.899962253434 |

## Dispersión en las 24 geometrías

![Matrices de tres grafos](../graficos/microscopia/dispersion_grafos.svg)

Las sondas numeran todos los extremos libres del grafo en el orden registrado en JSON. No son una asignación automática de terminales físicos de energía o control. Las guías y uniones ideales son hipótesis del cálculo.

| Glifo | Longitud del eje (u) | Vértices | Sondas | Máximo residuo unitario |
|---|---:|---:|---:|---:|
| P-01 | 9.7743071 | 7 | 1 | 2.22e-16 |
| P-02 | 12.533676 | 10 | 3 | 1.59e-15 |
| P-03 | 10.942215 | 7 | 1 | 1.11e-15 |
| P-04 | 9.7706417 | 8 | 3 | 1.05e-15 |
| P-05 | 26.252258 | 13 | 1 | 5.55e-16 |
| P-06 | 18.255923 | 14 | 3 | 2.35e-15 |
| P-07 | 11.288544 | 8 | 3 | 1.09e-15 |
| P-08 | 12.704792 | 10 | 3 | 1.46e-15 |
| P-09 | 9.7706417 | 7 | 1 | 1.22e-15 |
| P-10 | 12.599069 | 10 | 3 | 3.31e-15 |
| P-11 | 12.599069 | 9 | 1 | 3.33e-16 |
| P-12 | 12.599069 | 10 | 3 | 2.04e-15 |
| P-13 | 18.361646 | 12 | 3 | 3.44e-15 |
| P-14 | 13.397451 | 9 | 1 | 4.44e-16 |
| P-15 | 13.778706 | 11 | 4 | 1.64e-15 |
| P-16 | 18.361646 | 9 | 5 | 1.79e-15 |
| P-17 | 12.704792 | 10 | 3 | 3.87e-15 |
| P-18 | 15.533219 | 11 | 1 | 1.33e-15 |
| P-19 | 11.184855 | 8 | 3 | 1.74e-15 |
| P-20 | 19.43556 | 11 | 0 | 0 |
| P-21 | 16.225878 | 12 | 3 | 1.28e-15 |
| P-22 | 15.19292 | 13 | 4 | 1.09e-15 |
| P-23 | 13.778706 | 10 | 2 | 1.13e-15 |
| P-24 | 16.919313 | 12 | 2 | 7.83e-16 |

P-20 tiene cero sondas de extremos: se calcula el espectro del grafo cerrado mediante elementos finitos. Su matriz vacía de dispersión no cuenta como prueba de funcionamiento. Los terminales funcionales requieren otro problema de acoplamiento. P-04 y P-08 presentan las mismas fracciones de potencia en este ensayo ideal; la diferencia entre sus responsabilidades requiere estados, modos y controles adicionales.

## Memoria modal alimentada

![Conmutación de memoria](../graficos/microscopia/memoria_alimentada.svg)

| Estado | Ocupación | Estabilidad lineal |
|---|---:|---|
| 1 | 0.28073477 | Estable |
| 2 | 1.357277629 | Inestable |
| 3 | 2.361987601 | Estable |

Residuo del balance de ocupación: 3.65e-09. No se ha calculado una tasa de error estocástica ni se afirma memoria pasiva.

## Preparación y motor

| Modulación h | Exponente de Floquet | Estimación resonante |
|---|---:|---:|
| 0.04 | -0.01000096889 | -0.01 |
| 0.12 | 0.009991185718 | 0.01 |

El bombeo está prescrito; no se deduce del movimiento de una mano.

| Motor de tres niveles | Resultado |
|---|---:|
| heat_hot_eV_per_time_unit | 0.0118644888942 |
| heat_cold_eV_per_time_unit | 0.00237289777883 |
| work_eV_per_time_unit | 0.00949159111534 |
| cycle_efficiency | 0.8 |
| entropy_production_eV_K_per_time_unit | 5.85626900765e-06 |
| energy_residual | -8.67361737988e-18 |
| Diferencia de poblaciones: tasas frente a Lindblad | 1.11e-16 |
| Autovalor mínimo de la matriz de densidad | 0.00377666387804 |
| Potencia desde el Hamiltoniano coherente | 0.00949159111534 |

La eficiencia es del ciclo idealizado y las tasas utilizan una unidad temporal adoptada. No mide rendimiento solar por área ni prueba que M2 tenga los niveles elegidos.

## Comprobaciones adicionales

| Prueba | Resultado | Alcance |
|---|---|---|
| Dispersión: matriz de perturbación frente a fórmula exacta | Correcta | Fondo homogéneo aislado, orden clásico. |
| Estado sin presión: velocidad c/2 y ausencia de rigidez cortante | Correcta | Propiedades de fluido; no certifica un sólido ni toda perturbación no lineal. |
| Rama radial: dE/dQ coincide con omega | Correcta | Diferencia centrada local; no prueba todas las ramas. |
| Modo de fase: autovalor de L- converge a cero | Correcta | Hessiano radial discretizado; no es análisis 3D completo. |
| P-01 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-02 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-03 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-04 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-05 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-06 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-07 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-08 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-09 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-10 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-11 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-12 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-13 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-14 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-15 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-16 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-17 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-18 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-19 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-20 grafo cerrado: modo constante y espectro no negativo | Correcta | Laplaciano sobre grafo cerrado; no prueba sus terminales funcionales. |
| P-21 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-22 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-23 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| P-24 dispersión conserva flujo | Correcta | Grafo ideal sin pérdidas y un modo escalar por arista; no valida la función completa. |
| Nexo: potencia 1/9+4/9+4/9 | Correcta | Tres impedancias iguales; una adaptación adicional cambia el reparto. |
| Convertidor: reflexión+salida+pérdidas=entrada | Correcta | Respuesta de dos modos resonantes con acoplamientos elegidos. |
| Memoria: dos ramas estables y conmutación por pulsos | Correcta | Biestabilidad clásica determinista de una cavidad reducida. |
| Memoria: balance temporal de ocupación | Correcta | Ocupación normalizada; energía aproximadamente hbar*omega_carrier*N en banda estrecha. |
| Química: cociente cinético satisface balance detallado | Correcta | Dos estados con igual prefactor y misma transición; ejemplo explícito, no reacción CO2 real. |
| Fuerza de portal: gradiente de energía y reacción | Correcta | Perfil impuesto y prueba diferencial; no incluye solución de retroacción. |

## Datos completos

Los JSON de `validacion/` incluyen matrices, frecuencias, coeficientes, resultados y alcances. Los CSV conservan perfiles y trayectorias. La biblioteca científica utilizada y las pruebas de formato se registran en `validacion/informe.json`.
