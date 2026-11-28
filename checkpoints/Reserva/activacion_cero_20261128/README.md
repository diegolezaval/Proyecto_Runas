# Efecto de la historia acumulada antes de s=13,5

**El tubo de error de 1e−4 queda acreditado en todo el volumen de la donante cargada hasta s=17,875**, frente a s=15,5 con activación en 13,5. Son 19 intervalos adicionales de 0,125. El primer rechazo en s=18 se debe exclusivamente a r≥160. En esa fila la cota exterior vale 1,02938e−4 y la del núcleo r<10 es 7,76819e−6.

| Activación y extremo | Cota en r<10 | Cota en r≥160 | Decisión conjunta |
|---|---:|---:|---|
| Desde 13,5, extremo 15,625 | 1,03805e−4 | 1,77767e−5 | Primer rechazo del control, r<10 |
| Desde cero, extremo 15,625 | 1,28954e−6 | 1,75382e−5 | Aceptado |
| Desde cero, extremo 17,875 | 6,98245e−6 | 9,16551e−5 | Última fila aceptada |
| Desde cero, extremo 18 | 7,76819e−6 | 1,02938e−4 | Primer rechazo, r≥160 |

Los mayorantes mostrados se redondean hacia arriba. En s=18, las tres bandas intermedias quedan en 1,69125e−6, 3,46280e−9 y 7,99730e−5, respectivamente. El resultado limita la comparación de error de la referencia aislada. El contacto entre dos núcleos y su salida física siguen pendientes.

## Cuánto pesaba la historia anterior

En la fila rechazada del control tardío (s=15,625), las emisiones hasta 13,5 aportaban 1,16820e−4 a la amplitud de energía de 10–40; las posteriores aportaban 1,01766e−4. Correspondían al 53,44 % y 46,56 %. En el coste de caras de esa fila aportaban 1,33925e−5 y 1,16666e−5. El término de curvatura separado era cero en la ruta seleccionada.

En esa misma fila D=4,34055e−5. Su saldo al corte era 8,16395e−6. Después del corte, las caras aportaron 2,12496e−5 por emisiones antiguas y 8,84026e−6 por emisiones posteriores; los demás términos acumularon 5,15169e−6. Al retirar solo el saldo de D al corte con las demás magnitudes fijas, la cota aritmética del núcleo pasó de 1,03805e−4 a 8,51519e−5. Esta comparación justificó probar la activación temprana. La nueva certificación se obtiene de la marcha completa.

## Método

El control reconstruye la [marcha con activación en 13,5](../realimentacion_celda_20261128/README.md) y comprueba todas las filas contra su archivo. En cada extremo se separan las emisiones hasta 13,5 inclusive y las posteriores. En la amplitud de energía del peso 10–40 se suman la fuente y los defectos numéricos de cada intervalo con su núcleo de retardo. Los historiales ya contienen el producto de los saltos de métrica posteriores a cada emisión. La suma de ambos grupos debe recuperar la amplitud completa. Para el coste de caras se comprueba si se usó la norma espectral FV o el coste anterior de gradiente y curvatura. El desglose conserva aparte la curvatura cuando corresponde.

En el acumulador D se separa el saldo a 13,5 de los incrementos posteriores. Los incrementos por caras se contabilizan según el origen de las emisiones en la amplitud; los demás términos conservan el coste de la fuerza prescrita, la fuerza no lineal, la proyección de carga, la fase y los defectos. Ambas reconstrucciones se exigen en cada fila con tolerancia relativa 2e−12 más absoluta 1e−25. La partición identifica el origen directo de los sumandos de la comparación. Las fuerzas posteriores dependen también del estado entrante que dejó el prefijo.

El contraste aritmético retira solo D(13,5) al reconstruir el punto interior en la fila rechazada. Mantiene las cotas finales de carga y fase. Si supera el criterio prerregistrado, se inicia otra marcha desde los mismos datos iniciales en s=0 con el conmutador FV, WJ, la proyección de carga, Sx y la realimentación por celda activos desde el primer intervalo. En ambas marchas se usan la misma malla, radios, fuentes entre muestras, cinco pesos y umbral de 1e−4. Solo se acepta una fila si la entrada y las cinco envolventes caben simultáneamente. Se detiene en el primer rechazo conjunto.

Reproducir desde este directorio con `OPENBLAS_NUM_THREADS=1 python3 comparar_inicio.py`. [Protocolo](PROTOCOLO.md) · [Filas y contabilidad](resultado.json) · [Recibo](RECUPERACION.json)


## Siguiente comprobación del mismo contacto

El obstáculo ahora es la evaluación puntual del campo exterior en r≥160. En la fila s=18, con la misma entrada y radios del control desde cero, recuperar por separado X y la amplitud de energía de la banda, así como las dos conversiones que forman el mínimo puntual vigente. Contrastar ese mínimo con una cota de evaluación por celda de la energía FV exterior disponible. Usar únicamente el potencial positivo acreditado y las caras realmente cubiertas por el peso; verificar el borde de pared y omitir la contribución de la cara cortada en r160 si no está controlada. Comparar en todas las celdas exteriores antes de decidir si se justifica repetir el historial. Mantener el control de las otras cuatro bandas. Los resultados de la corona hasta s=40 conservan los cortes anteriores de fuente, 13,875 y 14,625. El piloto sigue pendiente del cruce conjunto atribuible en r60 y de entrega útil, con mínimos de misión E=1,66414371e−6 y Q=1,84762579e−6.
