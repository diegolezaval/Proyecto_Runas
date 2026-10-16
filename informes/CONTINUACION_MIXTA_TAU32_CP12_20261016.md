# CP12 · Frontera mixta τ32 verificada

La evolución autoconsistente Φ-FV / χ-K4 alcanzó τ32. Su cápsula fue guardada, recuperada íntegramente y auditada con las 28 comprobaciones sin pasos M2; las cinco métricas espaciales del prefijo también pasan .02 mediante la lectura registrada. Se mantiene el mismo ensayo en 32→40. CP11 sigue aceptado y CP12 abierto.

| Magnitud | h=.125 | h=.0625 | Límite original |
|---|---:|---:|---:|
| Deriva FV | 1.228083301718641e-08 | 3.642155022021143e-09 | 2e-4 |
| Deriva mixta | 1.0159695307265793e-10 | 1.0141298911747754e-10 | 2e-4 |
| Deriva de carga | 8.881784197001252e-16 | 6.661338147750939e-16 | 1e-9 |

Hay 81 observaciones por malla; 5889/5887 pasos aceptados y 71360/71336 evaluaciones cerradas, con cero evaluaciones vivas en la frontera. El máximo de observadores es 1.4311332843839691e-6; Parseval 2.038210442465316e-14; identidad instantánea 4.911526548694804e-13 y simetría ponderada 8.5495188351436525e-16. Los cuatro límites originales permanecen 1e-3, 2e-11, 2e-12 y 2e-12 respectivamente.

| Métrica del prefijo | Error (%) |
|---|---:|
| Norma temporal suprema | 0.00846743841325 |
| Campo Φ | 0.047298928114 |
| Espacio de fases Φ | 0.0791833273816 |
| Campo χ | 0.101278025087 |
| Espacio de fases χ | 0.143215175703 |

La lectura conserva fórmulas, spline, pesos, núcleo, normas iniciales y fase global permitida de Φ; no alinea χ para aceptación. La extensión fue publicada en `b805708d3faedc37118164f574325d3a6ebb3d2b` antes de adquirir esta frontera. Se usa una extracción independiente, sin trabajador ni pasos M2 y con estado/recibo inmutados. El acuerdo de dos mallas no determina un orden de convergencia.

La cápsula completa contiene 221 archivos de carga útil y 230481444 bytes; SHA256 `330c5e3d89b4025649e086719630a8758cf9c239e99b96cc29b893753ad12df3`. Estado `12a8c0d4efc1068137fc71fa52b4d8f91aec9b23b2d439af6cb201e99b137768`; recibo `bcdc40675df4bd4726de5f5b2f8ffc7104b1cf5ad55741943bf0f35c7c702266`; configuración `0719d82ab2187b6076fa2baf6d010495bdffd59622b9ca8f56345beb19e7f182`. Los certificados públicos de frontera, lectura y decisión están en `checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015`.

Se conservan el negativo de K4 de tres campos, los incidentes administrativos y los prefijos certificados sin repetirlos. Los auxiliares de respaldo se actualizaron con hashes científicos protegidos intactos. El registro de continuidad cuenta ahora una frontera completa como punto recuperable al publicarse; esta corrección administrativa no toca el integrador.

La puerta final de τ160, la reducción necesaria del canal acoplado operador_chi en cada una de las tres ventanas y las pruebas adicionales justificadas de referencia, conservación, estabilidad y robustez siguen pendientes. No se valida todavía la corrección ni se confunde esta verificación numérica con evidencia experimental. Main, PR #2 y las 33 etapas permanecen intactos.
