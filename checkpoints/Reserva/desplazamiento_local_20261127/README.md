# Desplazamiento positivo local de la cargada

El tubo de error puntual de **1e−4** se mantiene en toda la malla hasta **s=11,125** para la primera referencia radial corregida de la cargada. El control anterior llegaba a s=7,25. La primera banda que pierde la garantía con la comparación más ajustada es **r<10**, en el intervalo que termina en s=11,25. El exterior conserva cotas inferiores al tubo en ese intervalo condicional. Sigue pendiente controlar el resto de la ventana hasta s=40 y atribuir una salida conjunta al contacto.

[Protocolo previo](PROTOCOLO.md) · [Protocolo de radios](PROTOCOLO_RADIOS.md) · [Cálculo](desplazar.py) · [Contraste independiente](verificar.py) · [Resultados por intervalo](resultado.json) · [Comparación reproducida](../realimentacion_cargada_20261127/README.md)

## Comparaciones con los mismos datos

Se usaron los perfiles de la cargada, M2 radial FV, R256, dr=0,025, el puente de Hermite, las dos correcciones firmadas, la pared y los mayores defectos entre muestras previamente registrados. Se cotejaron las tres bandas de fuerza prescrita y ambos defectos numéricos en cada intervalo. Cada prueba comienza con error cero, con h=0,125. Los cinco pesos se conservan durante todo el historial. Se mantienen el trabajo de las caras interiores, la cancelación en la pared, las coordenadas físicas de carga y fase y el término directo del defecto cinemático en la derivada de la traza. Son comparaciones en doble precisión.

| Energía y tratamiento del resto | Último s con garantía | Primer extremo rechazado | Bandas que exceden 1e−4 |
|---|---:|---:|---|
| Comparación publicada, V+I | 7,25 | 7,375 | 60–160 |
| V+S con un único exponente | 7,25 | 7,375 | 60–160 |
| V+S con trabajo por banda | 10,75 | 10,875 | 60–160 y 160–256 |
| Trabajo por banda y jacobiano exterior firmado, radio uniforme | 10,75 | 10,875 | 60–160 y 160–256 |
| Jacobiano exterior firmado y radios autoconsistentes | 11,125 | 11,25 | r<10 |

## Dónde hace falta desplazar el potencial

Para cada autovalor λ del potencial rotante simétrico de tres campos se eligió s=max(0,m−λ,−2λ), m=0,17. En la región λ+s≥m y s≥0, la derivada de s/√(λ+s) tiene el signo de 2λ+s. La elección minimiza ese cociente. S conserva los autovectores locales. Se comprueba que V+S alcanza el piso exigido y que S es nulo en el exterior r≥40. Solo **529 celdas** requieren S; la más alejada tiene centro en **r=13,2125**. Su mayor autovalor es 0,818344 redondeado hacia arriba.

Para un peso k, la energía suma velocidad, gradiente FV y potencial V+S. Su derivada contiene el trabajo físico de las fuentes y el término auxiliar ⟨v,Sx⟩ₖ. Absorber este último en un solo exponente cambia μ de 0,650945 a 0,639666. Como muestra la tabla, ambos fallan en el mismo intervalo. Para localizar el trabajo se conserva el signo en la identidad y se usa Cauchy para la cota. Si X_b domina el desplazamiento en la banda disjunta b, se tiene

    ‖Sx‖ₖ ≤ [Σ_b (max_b(√k ‖S‖) X_b)²]½.

El producto de este mayorante por la cota de velocidad en energía controla el trabajo para cada peso. Se registra en cada fila. El coste de las caras usa las diferencias de k y las masas y conductancias FV publicadas. En las dos caras de borde se mantiene el tratamiento de la malla original. El propio intervalo se resuelve con la inversa positiva de la comparación lineal y tres afinaciones descendentes; se comprueban la suma máxima de filas y la positividad numérica de la inversa. El desplazamiento auxiliar no se añade como si fuese una fuerza física a q̇ ni a las seis semillas de la interfaz.

## Jacobiano exterior y resto

En r≥40 se congeló durante cada intervalo el jacobiano **con signo** del resto del potencial en el centro de la caja del puente corregido. La fuerza de M2 contiene el negativo de este gradiente, por lo que la energía lleva **V+J**. El centro de la caja es fijo durante el intervalo. Las envolventes de Bernstein y las dos correcciones delimitan sus anchos, incluida la evolución entre muestras. El mínimo exterior congelado fue superior a 0,18999 en los intervalos analizados.

Al cambiar de intervalo se compara H_n con H_anterior mediante la mayor raíz generalizada del incremento relativo, usando Cholesky en cada celda. Se toma como mínimo el factor uno para la parte cinética y las caras. Los historiales anteriores reciben el factor en norma, incluida la truncación numérica acumulada. La cota del defecto de posición usa también la norma del nuevo potencial. No se contabiliza el salto como trabajo externo de M2.

Quedan dos contribuciones a la fuerza. La primera procede de la variación de la referencia dentro de su caja. La segunda procede de evaluar el jacobiano entre la referencia y la solución desconocida. Para una caja de semiancho w y una desviación adicional ρ se usan el radio matricial T(w) y el incremento T(w+ρ)−T(w), respectivamente. La fórmula polinómica publicada mayoriza los coeficientes en valor absoluto; la expansión binomial del incremento contiene los términos con al menos un factor de la desviación adicional. La matriz es simétrica, por lo que la máxima suma absoluta por fila acota su norma. Se contrastaron el centro firmado y ambos radios por diferenciación compleja del gradiente físico. Para la carga y la traza se restaura el mayorante de la fuerza física completa J_b X_b. Así se mantiene separada la modificación usada únicamente en el balance energético.

Con el radio uniforme el jacobiano firmado reduce la cota exterior pero queda cerca del límite. En s=10,875 la cota en 60–160 pasa de 1,112e−4 a 1,008e−4 (redondeo superior). La prueba final usa la escalera registrada para el resto exterior. Cada candidato conserva el historial aceptado; verifica el extremo entrante y el mayorante de todo el nuevo intervalo. Las dos bandas interiores mantienen el radio máximo. Si se agotan los candidatos se conserva la prueba al radio máximo. En s=11,125 las tres bandas exteriores aceptan radios 5e−9, 3e−6 y 3e−6. El máximo puntual interior es ≤8,977e−5, y la cota para 60–160 es ≤2,844e−6.

## Alcance para la interfaz y la misión

Al anular solo la fuerza física de realimentación se recupera **2,78259e−6** para la integral propagada de |z′| hasta s=40. Con realimentación, la cota de la **integral simple** de |z′| hasta **s=11,125** ya es **1,44252e−5** en el método de radios. El cribado lineal previo de 3,96e−6 queda sin acreditar para este presupuesto no lineal; la cota puede sobreestimar el error real. La extensión del tubo en volumen tampoco mide transferencia. El piloto sigue pendiente. Se conservan los umbrales de energía 1,66414371e−6 y carga 1,84762579e−6, la atribución conjunta en r60 y la entrega útil a la receptora.

**Siguiente comprobación del mismo contacto.** En r<10 domina ahora el coste de estabilizar el núcleo. Comparar para esa banda una energía a carga fija con el modo de fase separado, apoyándose en el Hessiano FV ya contrastado y en las cotas exteriores por banda para los términos de interfaz o de variación del peso. Registrar el trabajo de estos términos, el defecto de fase, q̇ y la restitución de κq y uβ. Antes de propagar otra trayectoria, comprobar el balance homogéneo y si el coste total mejora el del desplazamiento local a la misma fecha. Para la traza conservar aparte el jacobiano físico en la proyección del adjunto; el cribado lineal por sí solo sigue siendo insuficiente.

**Resumen para el Dot principal.** Diego, confinar la corrección positiva al núcleo extiende la garantía del tubo de 7,25 a 10,75. El jacobiano exterior firmado y los radios por banda permiten llegar a 11,125. En 11,25 falla primero la cota de r<10. El presupuesto no lineal de la traza sigue por encima del cribado y el piloto continúa pendiente. [Informe y resultados](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/desplazamiento_local_20261127)

Para reproducir, ejecutar desde este directorio `OPENBLAS_NUM_THREADS=1 python3 desplazar.py` y `OPENBLAS_NUM_THREADS=1 python3 verificar.py`.
