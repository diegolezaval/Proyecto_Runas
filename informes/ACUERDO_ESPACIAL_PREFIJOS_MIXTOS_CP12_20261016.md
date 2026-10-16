# CP12 · Acuerdo espacial de prefijos mixtos guardados

Las cinco métricas originales se leen en extracciones independientes de fronteras completas; no se ejecutan pasos M2. Todos los porcentajes usan sus normalizaciones iniciales originales, spline y tratamiento de fase. El límite original es 2 % por métrica.

| Tiempo real | Norma suprema (%) | Campo Φ (%) | Fase Φ (%) | Campo χ (%) | Fase χ (%) |
|---|---:|---:|---:|---:|---:|
| 8 | 0.005123319496 | 0.02748172374 | 0.03455549764 | 0.0334983078 | 0.03399386198 |
| 16 | 0.005123319496 | 0.02996336856 | 0.04530523815 | 0.02467040493 | 0.02486276969 |
| 24 | 0.008467438413 | 0.03970588972 | 0.06493368245 | 0.02883749257 | 0.03753995687 |

τ8/16 reutilizan sus certificados sin repetir la lectura. τ24 y las futuras fronteras hasta τ152 siguen la extensión registrada en `b805708d3faedc37118164f574325d3a6ebb3d2b`, anterior a su análisis; τ24 ya estaba adquirido al registrar esa extensión. El lector mantiene exactamente su SHA256 `3043d3f58bb0a28cac20a528d3680408191a75c18a0c36505884e0cd9eac330b`. Sólo se parametriza la comprobación de tiempo del lector original, con identidad AST de las demás instrucciones.

El mayor error de τ24 es 0.06493368245324747 %, correspondiente al espacio de fases de Φ. Las cinco comparaciones están bajo 2 %. La rotación descriptiva de χ no interviene en la aceptación. Todos los diagnósticos, bandas y multipolos están en los JSON públicos individuales.

Este acuerdo de dos mallas en prefijos no demuestra orden de convergencia ni acepta la corrección o el horizonte original de τ160. Siguen pendientes la reducción del mecanismo en las tres ventanas y las pruebas adicionales justificadas de referencia, conservación, estabilidad y robustez. CP12 permanece abierto; CP11 es el último checkpoint científico aceptado. Main, PR #2 y las 33 etapas permanecen intactos.
