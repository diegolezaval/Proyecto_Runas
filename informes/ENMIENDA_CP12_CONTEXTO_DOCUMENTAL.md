# CP12 · Contexto de instantáneas y ecuaciones en la comprobación documental

La regresión de la recuperación detectó dos defectos administrativos de la preparación CP12. Su recibo inicial negativo se conserva en `trazabilidad/CP12_recuperacion/regresion_inicial_fallida.json`. No detectó una regresión de las ecuaciones, estados o resultados físicos.

`trazabilidad/CP11_entrada/` conservaba documentos completos del checkpoint original, pero faltaba en `snapshot_document_roots` de `datos/arquitectura.json`. Se declara esa raíz como las instantáneas CP08–CP10. El resolutor verifica los destinos relativos al documento original dentro del corpus, sin modificar sus bytes ni omitir la comprobación de los destinos. Esto conserva la interpretación histórica y la recuperación por hash.

En el protocolo causal, el producto matemático `[g+h(…)/2](\tilde\rho-\rho_f)` dentro de un bloque de ecuación se confundía con un enlace Markdown. El resolutor común reconoce ahora los bloques de ecuaciones delimitados por `\[` y `\]` en líneas propias y el texto literal delimitado por comillas invertidas. Los enlaces documentales fuera de esos contextos mantienen las comprobaciones originales, incluido el control negativo que introduce un enlace realmente roto.

Se preservaron las versiones originales de los dos verificadores modificados en las instantáneas CP09, CP10 y CP11, exclusivamente donde sus inventarios acreditan los mismos bytes. Esto mantiene también los verificadores históricos que consultan su propia instantánea. La primera iteración de la corrección y su regresión negativa se conservan en `trazabilidad/CP12_recuperacion/regresion_intermedia_fallida.json`.

No se modifica el prerregistro causal, la clausura de catorce archivos de la instrumentación física, sus identidades de ejecución, M2, Θ, la puerta del 2 %, las ecuaciones ni las conclusiones científicas. No hay movimientos ni renombrados.

El índice se regenera después de registrar las ejecuciones, porque incluye sus recibos y salidas. El éxito de estas regresiones no recupera el estado CP12 ausente ni autoriza certificar su causa.
