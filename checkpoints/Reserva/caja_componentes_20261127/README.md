# Cajas por componente del núcleo y respuesta tardía en r40

[Protocolo registrado](PROTOCOLO.md) · [Cálculo reproducible](evaluar.py) · [Resultados y series](resultado.json) · [Fuentes de cinco bandas](../traza_cinco_bandas_20261127/README.md) · [Resultado anterior del núcleo](../columnas_nucleo_20261127/README.md)

## Qué se ha corregido en el cribado

El valor provisional de 3,96e−6 se obtuvo para una **integral simple de |z′|** en el presupuesto del levantamiento. En el relevo anterior se lo comparó con una integral que incluye exp(0,051(40−s)). Esa comparación mezcló dos presupuestos diferentes. Para la ruta sin peso se suma la parte lineal de toda la ventana a la respuesta de las fuerzas no lineales de cada intervalo, incluida su respuesta tardía. En la ruta ponderada se aplica el peso a todos los términos bajo la integral. La restitución terminal del desplazamiento se registra aparte para ambas rutas.

Las 111 filas aceptadas hasta s=13,875 fijan las cinco normas de fuerza de entrada por intervalo. A partir de entonces solo se introduce fuerza no lineal cero en esta prueba de atribución. En cada observación posterior se vuelven a aplicar los núcleos de retardo correspondientes a **todas las fuentes antiguas**. Se conserva la contribución lineal hasta 40, incluidos los dos defectos y la componente cinemática directa de z′. El mínimo por par de intervalos entre las agrupaciones de tres y cinco bandas, el resto formal entre muestras y la cola discreta son los publicados. Se contrastan todas las filas del prefijo anterior. En los datos, cada fila de la traza contiene el extremo temporal, las cotas lineales de z y z′, y las cotas adicionales de z y z′ de las fuentes incluidas. La restitución se calcula con la norma de energía de L publicada, 891,64691 redondeada hacia arriba. Son cotas en doble precisión.

## Cajas del núcleo

En las 400 celdas de r<10 se obtienen las diagonales de evaluación de las amplitudes real y de χ en C⁻¹, y de la fase en P restringida a u perpendicular. A cada diagonal se le añade el residuo de su propia columna dividido por el hueco 0,17 y el mismo margen 1e−10 antes de tomar la raíz y dividir por la raíz del volumen. Se comprueba que las tres evaluaciones son compatibles con el límite conjunto anterior.

Dentro de esta región W=1. Al producto de cada coeficiente local por D se le añade su propia restitución de carga o fase: |κₐq|, |uβ| o |κχ q| en las unidades físicas correspondientes. Para las componentes de Φ se deshace también el factor √2 antes de recortar el ancho de la caja del campo. La envolvente del puente corregido se conserva. El jacobiano sobre ese intervalo usa el menor entre el radio derivado así y el radio del candidato. Para la fuerza del núcleo se intersectan el mayorante por volumen y la norma de los productos celda a celda del jacobiano con las tres cotas de campo. Para q̇ se comprueban la fila imaginaria y la proyección sobre u. Se efectúan cuatro sustituciones descendentes desde el mayorante anterior, manteniendo el estado entrante. Cada una es válida en todo el intervalo bajo la hipótesis de continuidad del tubo. La puerta puntual final sigue siendo la misma cota conjunta de los tres campos, con restituciones, caras, truncación y defecto de fase.

La conversión física de la fuerza del adjunto sigue usando el jacobiano y el volumen por banda previos. Solo se usa la nueva comparación en el control del núcleo. Para cualquier prefijo ampliado se conserva la fuente física de cada candidato realmente aceptado. El cálculo verifica que, en la prueba a entrada idéntica, se reproduce íntegramente el control archivado.

## Respuesta de las fuentes aceptadas hasta s=13,875

| Contribución a la integral de la derivada en valor absoluto | Simple | Con peso referido a s=40 |
|---|---:|---:|
| Lineal, toda la ventana | 1,89073e−6 | 2,78259e−6 |
| No lineal antigua, observada hasta 13,875 | 1,92033e−6 | 7,57010e−6 |
| No lineal antigua, observada después de 13,875 y hasta 40 | 8,45054e−5 | 1,61082e−4 |
| Total de las fuentes incluidas | **8,83165e−5** | **1,71434e−4** |

Las cifras de la tabla están redondeadas hacia arriba. El subtotal simple de las dos primeras filas es 3,81106e−6. La respuesta tardía de esas mismas fuentes eleva el mayorante simple por encima del cribado de 3,96e−6 aun sin introducir realimentación posterior. Este resultado limita la capacidad de la estimación. El error físico real y su signo siguen indeterminados.

En s=40 la cota de |z| debida a las fuerzas antiguas es 1,94782e−7, además de 7,34294e−9 lineales. En unidades de amplitud energética, las restituciones terminales respectivas son ≤1,73677e−4 y ≤6,548e−6. Como control de unidades, multiplicar la integral ponderada por la norma energética de L y sumar ambas restituciones da ≤0,153039 para las fuentes incluidas. La misma operación aritmética con la integral simple da ≤0,078928 para el presupuesto provisional sin crecimiento temporal; este último cálculo no certifica la energía móvil. La fuerza no lineal posterior al corte y su restitución aún faltarían en una estimación completa.

La cola simple del mayorante desagregado se concentra en 10–40 (≤6,50934e−5) y 60–160 (≤1,94004e−5). Los valores por banda corresponden a la suma antes del mínimo por retardo. El término 60–160, independiente de la reagrupación interior, ya supera el presupuesto simple disponible. Afinar exclusivamente r<10 o la fuente 10–40 no basta para que esta comparación acredite el cribado.

## Continuación del volumen

A igual estado entrante y radio máximo en s=14, la cota de r<10 baja de **1,20063e−4 a 1,05114e−4**. El coste de la fuerza no lineal en D baja de 6,310e−5 a 3,893e−5 por unidad de tiempo y el coste de la carga, de 3,563e−5 a 7,688e−6. El intercambio de caras conserva su valor de 1,528e−5. El candidato sigue fuera del tubo en esa comparación aislada.

Al repetir desde cero, el tubo conjunto de 1e−4 queda acreditado en toda la malla hasta **s=14,625**. La cota de r<10 en el último intervalo aceptado es 9,934e−5. El primer rechazo ocurre en **s=14,75**, otra vez en r<10, con cota de 1,437e−4. Las otras bandas quedan por debajo de 2,456e−5 en ese candidato. La pérdida de garantía no establece que los campos salgan realmente del tubo.

En un cálculo separado, al incluir las fuentes aceptadas de esta nueva continuación hasta 14,625 y dejarlas responder hasta 40, el mayorante simple llega a 3,341e−4 (ponderado, 6,780e−4). Son fuentes acotadas durante un prefijo más largo; no deben intercambiarse con las fuentes archivadas del prefijo 13,875.

**Siguiente comprobación del mismo contacto.** Antes de prolongar otra trayectoria, comprobar el coste de aplicar el peor jacobiano de cada banda a todos los radios del núcleo adjunto. Para 10–40 y 60–160, aplicar el jacobiano físico transpuesto al adjunto de la velocidad, o acotarlo por subregiones con Cauchy sobre la misma norma de volumen. Conservar la incertidumbre espacial de la referencia y del tubo, el resto entre muestras y la cola hasta 40. Comparar con el mayorante anterior para las mismas fuentes; los coeficientes del trabajo reducido no sirven como sustituto del jacobiano físico. La comprobación debe indicar cuánto presupuesto queda después de las fuentes conocidas, sin tratar una cota amplia como evidencia de transferencia.

**Resumen para el Dot principal.** Diego, el tubo de la cargada llega a 14,625 y falla primero en r<10 a 14,75. Corregida la comparación de unidades, la cota simple para la respuesta a 40 de las fuentes no lineales hasta 13,875, más el término lineal completo, es 8,832e−5. Domina la cola posterior de las fuerzas antiguas. El cribado de 3,96e−6 sigue sin acreditarse y el piloto permanece pendiente. [Informe y series de recuperación](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/caja_componentes_20261127)

Reproducir desde este directorio con `OPENBLAS_NUM_THREADS=1 python3 evaluar.py`. Se mantienen los mínimos de misión E=1,66414371e−6 y Q=1,84762579e−6, la atribución conjunta en r60 y la entrega útil a la receptora.
