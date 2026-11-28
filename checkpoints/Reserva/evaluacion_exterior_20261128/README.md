# Evaluación puntual del campo en r≥160

**El tubo integral de la donante cargada pasa de s=17,875 a s=19,5.** En la primera fila rechazada de la nueva marcha, s=19,625, la única envolvente que excede 1e−4 es la de 60≤r<160. El exterior r≥160 queda por debajo de 1,88123e−5 en esa misma fila.

| Extremo y comparación | Cota 60–160 | Cota r≥160 | Decisión |
|---|---:|---:|---|
| 18, control | 7,99730e−5 | 1,02938e−4 | Rechazado |
| 18, misma entrada y mismos radios | 7,99730e−5 | 2,02085e−5 | Aceptado |
| 19,5, desde cero | 9,97688e−5 | 1,72449e−5 | Aceptado |
| 19,625, desde cero | 1,11838e−4 | 1,88123e−5 | Rechazado |

A igual entrada en s=18, X=0,01031687575 y E=0,00743485817 (redondeados). La conversión anterior por masa daba ≤1,15033e−4; la combinación de volumen y gradiente, ≤1,02938e−4. El nuevo coeficiente máximo para λ=0 es ≤0,002718064664 y corresponde a r=160,0125. Con la sola energía caben la entrada y las cinco envolventes en los radios originales. Las filas siguientes de la prueba desde cero usan el menor mayorante válido conforme al protocolo. Los mayorantes de la tabla se redondearon hacia arriba.

Para λ=0 el residuo de factorización es ≤3,64e−12. Tras descontar la holgura aritmética (≤5,618e−6) queda margen positivo superior a 7,4819e−5 en las unidades de la matriz física. En la primera celda la solución independiente da 0,002718064624, y en la última 0,0001228849611. Los 35 contrastes independientes, cinco por matriz, satisfacen la tolerancia relativa 1e−7 y quedan bajo los coeficientes usados.

## Forma de energía y borde

La forma escalar está escrita en las componentes canónicas del campo en valores físicos por celda. Su masa es Mᵢ=4πwᵢ. Una cara interior entre i e i+1 aporta cᵢ|fᵢ₊₁−fᵢ|², con cᵢ=4πr² de la cara dividido por dr. La pared impone el valor cero a distancia dr/2 y aporta c_últ|f_últ|². La cara de corte en r=160 se omite por completo. El peso exterior vale uno en las celdas retenidas. Se aplica el piso 0,17−1e−10 al potencial; el control comprueba en cada intervalo el mínimo del potencial firmado frente a ese piso. Por positividad, la suma de las formas de las tres componentes está dominada por el cuadrado de la amplitud de energía E. X domina la norma de masa exterior.

Para cada celda, el cuadrado de la norma de evaluación con la métrica K+λM es su diagonal inversa Gᵢ. Por tanto, la magnitud conjunta de las tres componentes está acotada por √Gᵢ √(E²+λX²). Se evalúan todas las celdas, incluida la pared. La masa ya figura en la forma, de modo que el coeficiente se aplica directamente al campo.

## Margen y contraste independiente

Antes de la factorización tridiagonal LDLᵀ se resta 1e−8 M. Se exige positividad de todos los pivotes. Se reconstruyen las dos diagonales del producto para controlar el residuo en norma de filas y se añade una holgura de 128 unidades de precisión doble por la norma máxima usada en el ensamblaje. La reserva mínima debe dominar la suma de ambas cantidades. Así, la inversa de la forma factorizada proporciona un mayorante para la de interés. La recurrencia Gᵢ=1/dᵢ+ℓᵢ₊₁²Gᵢ₊₁ usa precisión extendida, redondeos hacia arriba y margen relativo adicional de 1e−12 en el coeficiente y en el producto final.

En paralelo al cálculo algebraico se ensambla el gradiente en coordenadas normalizadas por la raíz de M y se resuelven cinco columnas mediante LU dispersa. Para un campo físico constante se comprueba que solo contribuye la pared. Las tablas numéricas incluyen los coeficientes de ambas rutas, pivotes, residuos y márgenes para cada λ. La comparación de control exige recuperar todas las filas del [cálculo anterior](../activacion_cero_20261128/README.md). La evaluación exterior se aplica antes de comprobar conjuntamente la entrada y las cinco envolventes.

Reproducir en este directorio con `OPENBLAS_NUM_THREADS=1 python3 medir_exterior.py`. [Protocolo](PROTOCOLO.md) · [Filas y coeficientes](resultado.json) · [Recibo](RECUPERACION.json)


## Relevo

La siguiente comprobación del mismo contacto es evaluar la banda 60–160 a idéntica entrada y radios en s=19,625. Su forma escalar solo puede emplear las caras internas y el potencial acreditado: en esta banda se omiten las caras de corte de ambos extremos. Mantener la conversión exterior ya verificada, recuperar el control e intentar una marcha nueva solo si la fila completa entra. El prefijo aislado no acredita cruce conjunto por r60 ni entrega útil. Los mínimos de misión siguen siendo 1,66414371e−6 en energía y 1,84762579e−6 en carga; la corona a s=40 conserva sus dos cortes de fuente previos.
