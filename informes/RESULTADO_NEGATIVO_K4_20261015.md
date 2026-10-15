# CP12 · Resultado negativo del primer piloto K4

La prueba prerregistrada en `b6fafdcec6906291f411c8bdc8a33c3da815a80b` se detuvo por la **puerta energética FV original**, que conserva el límite **2×10⁻⁴**. No se completó τ8. CP12 sigue abierto y K4 no está validado.

Antes de M2 se guardó, recuperó y auditó τ0: sus 23 comprobaciones pasan y los seis datos de Cauchy coinciden exactamente con CP10. El coeficiente de composición sigue fijo en 1/12, las dos mallas, M2, Θ, DOP853, tolerancias y observadores siguen registrados. Se reutilizaron los controles estáticos y lineales cerrados.

| Malla | Tiempo físico al detenerse | Pasos aceptados | Deriva máxima de energía FV original | Deriva máxima del Hamiltoniano K4 | Deriva máxima de carga |
|---|---:|---:|---:|---:|---:|
| 0.125 | 0.022873976998663583 | 3 | 0.00006610612050739206 | 4.3231196400483896e-11 | 3.3306690738754696e-16 |
| 0.0625 | 0.017672153921661566 | 2 | 0.00029807341459231473 | 4.322864288752726e-11 | 2.220446049250313e-16 |

La malla fina excedió la puerta en τ=0.017672153921661566. La conservación del Hamiltoniano K4 permanece como un dato separado; el criterio de energía FV original falla. El guardián observó la salida 1 del trabajador propio. No se deduce el estado de otros ejecutores.

El reloj del observador era τ=0.01. Los dos estados físicos guardados tienen los tiempos individuales de la tabla; no forman una frontera común τ8 ni un estado reiniciable certificado del piloto. Se guardaron sus campos y respuestas de observadores, el error y el último τ0 certificado. Los contadores nfev de segmentos cerrados son cero; los contadores abiertos de evaluaciones no fueron capturados y no se reconstruyen por conjetura.

Cápsula inicial: 10974539 bytes, SHA-256 `218b4a7a5956d4db990128fae5fa7e56ab74dbd62456615c23dcc115e0fb647b`. Estado inicial SHA-256 `3a8386d3fc4d304d8db81b185ca5d5f77f01024c97f35a005cfbf4047c6a6a0c`. Cápsula negativa completa: 39126835 bytes, SHA-256 `f4176ec466647faa5a48a427403db3a865f3eef8fda21ea0f837520adfc5bf0b`. Ambas se guardaron y recuperaron independientemente con todos los hashes comprobados. El negativo y sus fuentes permanecen sin sobrescritura.

La evolución original τ160, su comparación CP10 exacta y sus tres ventanas causales conservan sus certificados. La recuperación numérica pública τ80 sigue completa. Las 33 etapas, main y PR #2 permanecen intactos. La siguiente tarea es una lectura pasiva de las dos formas energéticas y del trabajo del cambio de operador sobre los estados guardados. Este resultado no autoriza un reintento K4, otra tolerancia ni K6/K8 por inercia.
