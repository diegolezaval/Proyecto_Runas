# Fuerza auxiliar Sx en las cinco comparaciones causales

**La garantía del tubo de 1e−4 en todo el volumen de la donante cargada pasa de s=14,875 a s=15,25.** Se aceptan tres intervalos adicionales de 0,125. El primer rechazo conjunto termina en s=15,375 y lo determina únicamente r<10.

| Comparación | Extremo | Mayorante del núcleo | Coste de caras en la tasa de D |
|---|---:|---:|---:|
| Control causal anterior | 15 | 1,06485e−4 | 4,82899e−5 |
| Solo el intervalo actual, entrada y radios idénticos | 15 | 1,05550e−4 | 4,50923e−5 |
| Historia refinada desde 13,5 | 15 | 7,24288e−5 | 2,27045e−5 |
| Último intervalo aceptado | 15,25 | 9,14663e−5 | 2,92957e−5 |
| Primera fila rechazada | 15,375 | 1,03112e−4 | 3,32349e−5 |

Los mayorantes de la tabla se redondean hacia arriba. En la fila rechazada las otras cuatro envolventes quedan por debajo de 2,29793e−5. La fuerza no lineal en la tasa de D está acotada por 5,14704e−6 y el trabajo de κq̇ por 8,09598e−7. El coste real del comparador causal a s=15 difiere del cribado que reemplazaba Sx en las 120 fuentes manteniendo las demás magnitudes fijas: aquí se conserva la historia original anterior a 13,5 y se recalculan los términos acoplados a partir de ese punto.

## Método

Se mantiene el control de WJ, la proyección independiente en q̇, la fase, el conmutador FV y los defectos. La norma acotada para cada peso de observación es la de √k Sx en coordenadas canónicas de volumen. Solo r<10 y 10–40 intersectan el soporte de S. En cada banda se acota por celda la acción de la matriz completa de S sobre la caja de componentes y se combina con la norma X mediante el [dual cuadrático publicado](../fuerza_wj_20261127/README.md). Se retiene el mínimo con la ganancia previa y se combinan las dos bandas en cuadratura. Cada uno de los cinco pesos tiene su propio techo. Se mantiene la holgura relativa de 1e−11.

Para cada candidato de radios se calcula primero la solución condicional anterior del propio intervalo con la historia disponible. De ella se obtienen X, D, Q y β; el recorte y las componentes restauradas determinan las cajas por celda. En una segunda evaluación se parte del mismo estado entrante. Se conserva la inversa positiva original para inicializar el mayorante, y en sus cuatro pasadas descendentes cada coste de Sx se intersecta con el techo ya justificado. Así se evita suponer por adelantado la mejora de la celda. Se recalculan realimentación, energía, trazas y núcleo para el nuevo candidato. Solo se incorpora a los historiales una fuente por intervalo aceptado. Las cinco envolventes y la entrada deben caber simultáneamente en esos radios.

El control desactivado exige igualdad con todas las filas del archivo de q̇. En la prueba aislada se usa la misma historia y los mismos radios en el intervalo que termina en s=15. Para el peso de 10–40 se contrasta además el nuevo techo del propio intervalo con la emisión del [cribado de historia fija](../cribado_sx_20261127/README.md). La marcha de varias filas se activa solo si la prueba aislada reduce el coste de caras y la cota interior según el protocolo. Las primeras 108 filas se reconstruyen desde cero y se comprueba su igualdad.

Reproducir en este directorio con `OPENBLAS_NUM_THREADS=1 python3 marchar.py`. [Protocolo](PROTOCOLO.md) · [Filas y presupuestos](resultado.json) · [Recibo](RECUPERACION.json)


## Siguiente diagnóstico

En la emisión del intervalo rechazado, para el peso de 10–40, la realimentación usada en la energía vale 1,37627e−4 frente a 5,27645e−5 para Sx y 1,43400e−10 para la fuerza prescrita. Estas cifras describen la emisión del propio intervalo. El siguiente contraste del mismo contacto es acotar la realimentación por celda para cada peso en esa fila, manteniendo los historiales a entrada fija. En r<40 usar el jacobiano físico con su caja y en r≥40 solo el resto de la parte firmada que ya entró en la energía. Aplicar el presupuesto X de cada banda, conservar el mínimo previo y validar la recuperación del control al desactivar el refinamiento. Probar la marcha de varias filas únicamente si la comparación reduce el coste de caras y la cota interior.

Los cortes de la corona a s=40 siguen siendo 13,875 y 14,625. El prefijo radial aislado no mide transferencia. Se mantienen los mínimos de energía 1,66414371e−6 y de carga 1,84762579e−6, el cruce atribuible en r60 y la entrega útil a la receptora.
