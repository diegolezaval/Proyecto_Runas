# Resumen numérico · CP11

> Vista generada por herramientas/generar_resumen_CP11.py. Resultados y recibos son las autoridades; no editar cifras manualmente.

**Unidad finita: diagnóstico radial cerrado. Causa acoplada abierta por historia de fuente no guardada.**

**Puerta física original: REFINAMIENTO_PENDIENTE, umbral 2 %. Cero pasos nuevos de evolución M2.**

## Interpolación y métrica

Normas sobre r<40 y τ=160, relativas a la perturbación inicial de χ; velocidades divididas por M. Ninguna fase de χ se ajusta para aceptación. Ambos denominadores y la sensibilidad lineal permanecen en el resultado fuente.

| Comparación | Campo (%) | Campo y velocidad (%) |
|---|---:|---:|
| CP10 unilateral | 3.61743537 | 5.12639096 |
| Inversa: fina→gruesa | 3.63108591 | 5.14576911 |
| Spline simétrico, Gauss 12 | 3.61755315 | 5.12655809 |
| Spline con paridad en origen | 3.61755315 | 5.12655809 |
| Control lineal, orden inferior | 3.39534213 | 4.81116208 |

Error inicial spline: 0.00112231493 %. Error fina→gruesa→fina de representación: 0.0371210362 %.

La explicación de un cruce artificial del umbral queda descartada en las comparaciones spline declaradas; no se certifica el continuo.

## Operador y componentes cortas

| Control algebraico | Error relativo máximo |
|---|---:|
| Acción frente a Evolution.lap | 1.68780823e-16 |
| Simetría ponderada | 5.03778507e-19 |
| Residuo modal | 1.05496066e-16 |
| Parseval | 6.49143856e-15 |

K es la forma positiva de la acción FV en R=220. La autobase libre no es el generador dinámico acoplado.

| Corte k=√λ | Fracción de diferencia cuadrática por encima (%) | Recorte suave (%) |
|---|---:|---:|
| 2 | 99.9830359 | 99.9830359 |
| 4 | 99.9724962 | 99.9724964 |
| 8 | 74.6838795 | 74.6838825 |
| 12 | 11.3694477 | 11.3694311 |
| 20 | 0.0183191066 | 0.0183193526 |

El recorte suave conserva 99.9999759 % de la diferencia cuadrática. Son fracciones de la norma de error, no de energía física.

| ℓ=2: k continuo aproximado | Δω·τ, gruesa−fina (rad) |
|---|---:|
| 1.99916 | -0.0122830828 |
| 3.99838 | -0.196192418 |
| 7.99677 | -3.04597819 |
| 11.9952 | -14.6026512 |
| 20.0062 | -94.7020371 |

## Hipótesis negativas y respuesta forzada

Propagador libre de χ inicial: diferencia 0.0718833927 %; su diferencia cuadrática representa 0.0196622713 % de la observada. No basta.

Residuo frente al equilibrio congelado: 5.12595655 %. Diferencia del equilibrio: 0.0668259023 %.

La corrección modal fijada antes del resultado deja 4.43602575 % y reduce 25.1202015 % la diferencia cuadrática. Falla el criterio explicativo prerregistrado de reducción ≥50 %. No se utiliza para la puerta física.

Diferencia de respuesta forzada por Duhamel: 5.12714037 %. Cota inferior de su amplitud respecto de la diferencia observada: 98.5977778 %. El cierre de la descomposición tiene residuo 3.45908983e-15.

Los extremos determinan dos momentos por modo, no la historia de fuente. No separan el presupuesto integrado del conmutador radial y el de la fuente acoplada. Se detiene antes de nuevas campañas.

## Intento aritmético conservado y referencia

El intento doble inicial es FALLIDA y no evidencia aceptada. Su código, salidas y recibo permanecen incluidos. La referencia longdouble conserva las mismas ecuaciones, estados, coeficientes y spline, y la tolerancia algebraica 2e−12.

| Extremo | Residuo de identidad extendida | Equivalencia de spline |
|---|---:|---:|
| initial | 4.01085953e-13 | 1.11172624e-16 |
| final | 1.18492487e-16 | 1.03508987e-16 |

## Fuentes y recibos

- chi_radial_diagnostic: [validacion/P06/no_radial/CP11/diagnostico_radial__95e3e493841d55db9dad877564e70192975ff410333cac478376d81e16b33faa/resultados.json](../validacion/P06/no_radial/CP11/diagnostico_radial__95e3e493841d55db9dad877564e70192975ff410333cac478376d81e16b33faa/resultados.json); recibo [validacion/P06/no_radial/CP11/diagnostico_radial__95e3e493841d55db9dad877564e70192975ff410333cac478376d81e16b33faa/procedencia.json](../validacion/P06/no_radial/CP11/diagnostico_radial__95e3e493841d55db9dad877564e70192975ff410333cac478376d81e16b33faa/procedencia.json).
- chi_frozen_source_contrast: [validacion/P06/no_radial/CP11/contraste_fuente__f02556d29606ee7c48dbe63bfeadd289bd5f821d175dcae1324daecb54161df9/resultados.json](../validacion/P06/no_radial/CP11/contraste_fuente__f02556d29606ee7c48dbe63bfeadd289bd5f821d175dcae1324daecb54161df9/resultados.json); recibo [validacion/P06/no_radial/CP11/contraste_fuente__f02556d29606ee7c48dbe63bfeadd289bd5f821d175dcae1324daecb54161df9/procedencia.json](../validacion/P06/no_radial/CP11/contraste_fuente__f02556d29606ee7c48dbe63bfeadd289bd5f821d175dcae1324daecb54161df9/procedencia.json).
- chi_forced_response: [validacion/P06/no_radial/CP11/respuesta_forzada_precisa__74359dfc9526f7d4de8e7f2da369de2c2349308518a8933b0bb54d41a98606ed/resultados.json](../validacion/P06/no_radial/CP11/respuesta_forzada_precisa__74359dfc9526f7d4de8e7f2da369de2c2349308518a8933b0bb54d41a98606ed/resultados.json); recibo [validacion/P06/no_radial/CP11/respuesta_forzada_precisa__74359dfc9526f7d4de8e7f2da369de2c2349308518a8933b0bb54d41a98606ed/procedencia.json](../validacion/P06/no_radial/CP11/respuesta_forzada_precisa__74359dfc9526f7d4de8e7f2da369de2c2349308518a8933b0bb54d41a98606ed/procedencia.json).
- Intento fallido: [validacion/P06/no_radial/CP11/respuesta_forzada__9360199db9cdc238ab2e4c8d75512db5f81d85a225088ad27f8ab8e67d9b0817/resultados.json](../validacion/P06/no_radial/CP11/respuesta_forzada__9360199db9cdc238ab2e4c8d75512db5f81d85a225088ad27f8ab8e67d9b0817/resultados.json); recibo [validacion/P06/no_radial/CP11/respuesta_forzada__9360199db9cdc238ab2e4c8d75512db5f81d85a225088ad27f8ab8e67d9b0817/procedencia.json](../validacion/P06/no_radial/CP11/respuesta_forzada__9360199db9cdc238ab2e4c8d75512db5f81d85a225088ad27f8ab8e67d9b0817/procedencia.json).

Figura generada: [graficos/CP11_diagnostico_chi.svg](../graficos/CP11_diagnostico_chi.svg).

La definición, hipótesis, derivación y puerta están en [el capítulo 31](../tratado/31_diagnostico_radial_del_mediador.md) y los prerregistros. E03/E04/RES0/RES1 siguen PARCIALES; no se afirma estabilidad orbital, convergencia continua/conjunta, inestabilidad física ni agotamiento de M2.
