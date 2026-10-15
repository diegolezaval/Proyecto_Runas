# CP12 · Estado intermedio recuperable verificado en M2

El nuevo transporte pasa el contraste preregistrado sobre la trayectoria mixta: restaurar τ=.4 y avanzar un intervalo original .01 reproduce τ=.41 **bit a bit** en campos, estados pasivos, internos DOP853, interpolaciones y contadores. La rama diagnóstica ejecutó dos pasos aceptados y 24 evaluaciones del solver por malla, contabilizados separadamente. No se repitió una campaña certificada ni A–D.

La cápsula completa τ=.4 tiene 204098285 bytes y SHA256 `fc7e044658650e8c3fbb731c942192b387bcc31f0455b5731368f675f38ac21c`. Se verificaron los 102 archivos y la rehidratación independiente superó 14 controles con cero pasos M2. La herramienta de recuperación pública también se ejecutó sobre otra extracción y pasa sin reescribir el recibo ni reiniciar el integrador. Estado interno NPZ SHA256 `3a1332db0b5ae4d259bab692cd8a384a7012e251a2628e5e0c425c07888cbce8`.

El reloj del observador es .4 y los tiempos físicos reales son .40447573137371634/.40447574001814635: se conservan tal como estaban, junto a las interpolaciones que cubren el reloj. Cada malla había aceptado 75 pasos, con 1097 evaluaciones vivas DOP853. No se confunde el reloj con una sincronización o frontera física nueva.

Hasta este transporte: máximos de deriva FV 1.004e-9/2.267e-10, energía mixta 4.390e-11/4.384e-11 y carga 5.552e-16/4.441e-16, inferiores a las puertas originales. Son balances de un prefijo corto; no certifican todavía τ8, convergencia espacial final, estabilidad, robustez ni eliminación del mecanismo.

La producción continuó después de la conservación y auditoría. Los transportes locales siguen cada .4, y los respaldos completos recuperados/auditados el primero y cada 1.6; las fronteras científicas siguen cada ocho unidades. Un supervisor externo sólo retira copias temporales redundantes ya conservadas y auditadas, reteniendo las dos más recientes de cada clase y todos los comprobantes, negativos y archivos permanentes. No modifica el solver ni borra evidencia permanente.

Comprobantes en `checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/transporte_dop853_20261015/`: `TRANSPORTE_TAU_000004.json`, `CONTROL_TRANSPORTE_M2_UN_INTERVALO.json`, `RECUPERACION_INDEPENDIENTE_000004.json`. La guía y herramienta `RECUPERAR.md`/`recuperar_transporte.py` permiten continuar desde el transporte más avanzado sin volver a τ0. Este transporte es numéricamente recuperable y **no** es un checkpoint científico aceptado. CP12 permanece abierto y CP11 sigue siendo el último aceptado. Main, PR #2 y las 33 etapas permanecen intactos.
