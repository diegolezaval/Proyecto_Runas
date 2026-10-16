# CP12 · Frontera mixta τ40 verificada

La cápsula autoconsistente Φ-FV / χ-K4 de τ40 pasó recuperación íntegra y las 28 comprobaciones sin pasos M2. Las cinco métricas espaciales del prefijo también pasan .02 mediante la lectura registrada. Se continúa el mismo ensayo en 40→48; CP11 sigue siendo el último checkpoint científico aceptado y CP12 permanece abierto.

| Máximo del prefijo | h=.125 | h=.0625 | Límite original |
|---|---:|---:|---:|
| Deriva FV | 1.8142904845142027e-08 | 5.502209909913347e-09 | 2e-4 |
| Deriva mixta | 1.1940171074087402e-10 | 1.193691812062525e-10 | 2e-4 |
| Deriva de carga | 8.881784197001252e-16 | 6.661338147750939e-16 | 1e-9 |

Hay 101 observaciones por malla; 7328/7324 pasos aceptados y 88702/88654 evaluaciones cerradas, con cero evaluaciones vivas. El máximo error de observadores es 1.4311332843839691e-06, bajo 1e-3; Parseval 2.038210442465316e-14, bajo 2e-11. La identidad instantánea es 4.967105544026367e-13 y la simetría ponderada 2.109202680584824e-16, ambas bajo 2e-12.

| Métrica original del prefijo | Error (%) |
|---|---:|
| Norma temporal suprema | 0.0140120481408 |
| Campo Φ | 0.0512110302783 |
| Espacio de fases Φ | 0.0927308734274 |
| Campo χ | 0.270988714497 |
| Espacio de fases χ | 0.384127731583 |

El mayor error es 0.384127731583 %, en el espacio de fases de χ, frente a 0.143215175703 % en τ32. Esta comparación entre tiempos no mide un orden de convergencia ni permite extrapolar el error final. Se mantienen el umbral del 2 %, las normas iniciales, el spline y el tratamiento original de fases. La rotación descriptiva de χ no se usa para aceptación. La lectura conserva estado y recibo y ejecuta cero pasos M2.

El ZIP íntegro tiene 253 archivos de carga útil y 230737013 bytes; SHA256 `a01caf2e8ced46cca4edfeddbb5add78c3c21ba0794e6ba80633f6961dc7e24d`. Estado `0e52bfd1b1f78fbed48cf8b0b97e46a0da454fc2c695f0886594e631e4ab47e4`; recibo `533cd7dfed4d592eeed85daad1f9cdbd6ac105f266e8ee70f9c1616cd1776ae4`; configuración `0719d82ab2187b6076fa2baf6d010495bdffd59622b9ca8f56345beb19e7f182`. Frontera, métricas y decisión se conservan como JSON públicos bajo `checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015`.

La conservación del prefijo está verificada. Siguen pendientes la comparación original de τ160, la reducción necesaria del canal operador_chi acoplado en las tres ventanas y las pruebas adicionales justificadas de referencia, conservación, estabilidad y robustez. No se valida todavía la corrección ni se declara evidencia experimental.

La continuación conserva los negativos y los controles A–D ya certificados, sin repetirlos. El método para suspender tras una lectura espacial negativa exige un checkpoint previo recuperado y evidencia separada de la parada propia. Main, PR #2 y las 33 etapas permanecen intactos. Recuperar primero cualquier transporte o frontera posterior y conservar la identidad de cada sesión.
