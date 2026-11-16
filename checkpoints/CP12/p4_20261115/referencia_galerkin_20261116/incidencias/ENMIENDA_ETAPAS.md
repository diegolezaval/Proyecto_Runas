# CP12/P4 Galerkin · Enmienda sobre el cálculo de etapas

EPS guardó su último paso aceptado, el 830 en τ6,64. En el intento siguiente el incremento normalizado de las etapas se estancó en 1.486251. El diagnóstico congelado reprodujo el estancamiento. La corrección de residuo llegó a 0.748562 en cinco iteraciones, con el mismo ancho de elemento, paso y tolerancias. El diagnóstico dejó el NPZ intacto y ejecutó cero pasos nuevos de M2.

El camino Gauss–Legendre original se usa en los cinco brazos. Si agota sus iteraciones, el ejecutor resuelve el mismo sistema de etapas por incrementos del residuo y exige el mismo límite de convergencia. El resultado se integra con las mismas ponderaciones. El recibo conserva cuántos pasos requirieron esa corrección. La Cauchy, los casos, las cinco métricas, los presupuestos de error y las puertas físicas siguen el prerregistro.

Al recuperar EPS, verificar el manifiesto y el SHA-256 del respaldo archivado, el contador, el prefijo de observaciones, la Cauchy y los balances del último paso aceptado. Acreditar ese estado como transporte de τ6,64 con cero pasos de recuperación. La frontera completa sigue en τ0 hasta que τ8 pase sus puertas. Reservar la reanudación tras constatar la terminación del intento anterior. R0, R1, R2 y T conservan sus cierres acreditados.

[Diagnóstico congelado](EPS_ETAPAS_CONGELADAS.json) · [Puertas y fallo observado](eps_43973602565/PUERTAS.json) · [Recuperación de la evidencia](eps_43973602565/RECUPERACION_PUBLICA.json)
