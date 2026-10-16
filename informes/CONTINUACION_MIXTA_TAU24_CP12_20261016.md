# CP12 · Frontera mixta τ24 conservada y auditada

La evolución autoconsistente Φ-FV / χ-K4 alcanzó τ24 y su cápsula completa pasó recuperación independiente y las 28 comprobaciones originales adaptadas al ensayo mixto. Quedan 61 observaciones por malla. La decisión positiva de conservación e integridad permite continuar 24→32 conforme al prerregistro; CP11 sigue aceptado y CP12 abierto.

| Magnitud máxima del prefijo | h=.125 | h=.0625 | Límite original |
|---|---:|---:|---:|
| Deriva de energía FV | 5.356187493532616e-9 | 1.5675596376496514e-9 | 2e-4 |
| Deriva de energía mixta | 8.549638774724144e-11 | 8.531364503738814e-11 | 2e-4 |
| Deriva de carga | 6.661338147750939e-16 | 6.661338147750939e-16 | 1e-9 |
| Pasos físicos aceptados | 4434 | 4433 | Contadores conservados |
| Evaluaciones cerradas | 53826 | 53814 | Cero evaluaciones vivas en la frontera |

El máximo error de observadores es 1.4311332843839691e-6 frente a 1e-3; Parseval 2.038210442465316e-14 frente a 2e-11. La identidad instantánea mixta da 6.281425210987864e-13 y la simetría ponderada 1.0532497067253383e-16, ambas bajo 2e-12. El cierre χ de toda la caja es 2.3269041765008575e-7 en la familia cruda y 2.3321625687106268e-7 en la acoplada. El error de fase χ observado en el núcleo en este tiempo es 0.03753995687408938 %; esta observación no reemplaza la comparación final de cinco métricas en τ160.

La cápsula tiene 230147547 bytes y SHA256 `b807568f3523440c2358120365901a4dd2a13a982d1a64548f0f3e19ef3e9abd`. Estado: `b65f3886a004c6b05c13f2bcea10d6de2631785a2af947fcaea992f59c7a9180`; configuración: `0719d82ab2187b6076fa2baf6d010495bdffd59622b9ca8f56345beb19e7f182`; recibo: `77e70344cec5fc1d03957e2fafe1d88293b69270778a75e97f28b51959244b3e`. El certificado público completo es `checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015/FRONTERA_MIXTA_TAU0024.json`.

Se reanudó desde el transporte τ22.4 con memoria DOP853 y observadores exactos, sin repetir prefijos, controles A–D ni campañas originales. El reinicio del integrador en τ24 es la política original entre segmentos de ocho unidades. La actividad anterior permanece desconocida; la sesión actual conserva su propia identidad y salida observada.

La lectura de las cinco métricas en τ8/16 ya está certificada y no se repite. Se registra una extensión de la misma lectura sin pasos M2 para nuevas fronteras, empezando por τ24. Se mantienen fórmulas, tiempos reales, spline, norma inicial, fase permitida de Φ y ausencia de alineación de χ. El acuerdo de dos mallas no mide por sí solo un orden de convergencia. Siguen pendientes el horizonte τ160, la reducción del mecanismo en las tres ventanas y las pruebas adicionales justificadas de referencia, estabilidad y robustez; no hay validación experimental ni cierre de CP12.

Main, PR #2 y las 33 etapas siguen intactos. Para recuperar, buscar primero cápsulas posteriores y usar el transporte o frontera positivo más avanzado con su herramienta pública, auxiliares vigentes y auditoría sin pasos M2.
