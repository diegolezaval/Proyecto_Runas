# CP12 · Acuerdo espacial de prefijos mixtos guardados

Las cinco métricas originales se leen en extracciones independientes de fronteras completas, sin pasos M2 ni mutación del estado o recibo. Los porcentajes conservan normalizaciones iniciales, spline y tratamiento de fase originales. El límite es 2 % por métrica.

| Tiempo real | Norma suprema (%) | Campo Φ (%) | Fase Φ (%) | Campo χ (%) | Fase χ (%) |
|---|---:|---:|---:|---:|---:|
| 8 | 0.005123319496 | 0.02748172374 | 0.03455549764 | 0.0334983078 | 0.03399386198 |
| 16 | 0.005123319496 | 0.02996336856 | 0.04530523815 | 0.02467040493 | 0.02486276969 |
| 24 | 0.008467438413 | 0.03970588972 | 0.06493368245 | 0.02883749257 | 0.03753995687 |
| 32 | 0.008467438413 | 0.04729892811 | 0.07918332738 | 0.1012780251 | 0.1432151757 |
| 40 | 0.01401204814 | 0.05121103028 | 0.09273087343 | 0.2709887145 | 0.3841277316 |
| 48 | 0.01850100307 | 0.05759187898 | 0.1143372769 | 0.5293110703 | 0.7508082788 |
| 56 | 0.0208614924 | 0.05757757447 | 0.1128965814 | 0.833489937 | 1.182721018 |
| 64 | 0.0208614924 | 0.05140544279 | 0.09523351109 | 1.135839791 | 1.61212291 |
| 72 | 0.0208614924 | 0.04083355557 | 0.07493546039 | 1.40500533 | 1.994270312 |
| 80 | 0.0208614924 | 0.0347184016 | 0.05807697051 | 1.628819676 | 2.311907991 |

En el prefijo más reciente, τ80, el mayor error es 2.31190799095 %. Las cinco comparaciones no pasan todas el límite original.

τ8/16 reutilizan sus certificados sin repetir la lectura. Las nuevas fronteras siguen la extensión registrada en `b805708d3faedc37118164f574325d3a6ebb3d2b` antes de su análisis; τ24 ya estaba adquirido al registrar esa extensión. Sólo se parametriza la comprobación temporal, con identidad AST del resto. La rotación descriptiva de χ no interviene en aceptación. Los JSON conservan todos los diagnósticos.

El acuerdo de dos mallas en prefijos no demuestra orden de convergencia ni acepta el horizonte original τ160. Siguen pendientes reducción del mecanismo en las tres ventanas y pruebas adicionales justificadas de referencia, conservación, estabilidad y robustez. Una lectura negativa se conserva y exige suspender la continuación para investigar sin relajar las puertas.

CP12 permanece abierto; CP11 sigue aceptado. Main, PR #2 y las 33 etapas permanecen intactos.
