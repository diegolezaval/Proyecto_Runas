# CP12 · Escala absoluta de redondeo del control de fuente

El control `6308bf6d400d008fe982c21160625b24777a4b391ffcab771189c17787a866c2` se conserva FALLIDA. Antes de M2, la identidad cúbica pasó con residual 2.86e−28, la acción C pasiva coincidió exactamente con NumPy y las cotas de fase global de ambos órdenes fueron 5.75e−9/1.57e−6. El único control negativo restante divide una resta de fuentes grandes por la diferencia pequeña, en contradicción con su definición de escala **absoluta de fuerza**.

Se conserva el residual absoluto y el cociente anterior, y se añade el cociente correctamente condicionado por `max(1, max|IFc|+max|Ff|)`. El límite de redondeo sigue siendo 2e−12 sobre la escala absoluta declarada, sin reinterpretar el cociente viejo como si hubiese pasado. La identidad polinómica se certifica separadamente en float128; el cierre **acumulado** y entre órdenes sigue ≤1e−3 de la diferencia, y la puerta física continúa en 2 %. No se atribuye causalidad sobre la base de esta escala instantánea.

La repetición comprueba también que el control positivo pertenece al código efectivamente utilizado por las dos evoluciones. Se registran epsilon float128 y tiempos por operación del observador para detectar costes evitables. Esta corrección se hace sin ningún paso nuevo de M2 y no modifica la física ni sus tolerancias.
