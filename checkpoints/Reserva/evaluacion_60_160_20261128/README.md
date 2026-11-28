# Evaluación del campo de la donante en 60 ≤ r < 160

La marcha causal desde cero acredita el tubo en las cinco bandas hasta **s=22,25**. El primer rechazo se produce en s=22,375. Solo r≥160 supera el techo de 1e−4, con una cota de 1,05394e−4 redondeada hacia arriba. El núcleo queda por debajo de 9,70337e−5 y la banda 60–160 por debajo de 9,14999e−5.

## Comparación a la misma entrada

El control recuperó todas las filas del cálculo exterior, incluido el rechazo en s=19,625. En esa fila, X=0,005480911696 y la amplitud de energía E=0,003837935437 en la banda 60–160. La conversión por masa da 1,62944e−4 y la de volumen más gradiente da 1,11838e−4. Con la evaluación puntual de la forma de energía, la cota baja a **2,74765e−5**. Basta λ=0. Estos tres mayorantes se redondean hacia arriba. Los radios y las otras cuatro envolventes coinciden exactamente con el control. La misma fila contiene la entrada y las cinco envolventes. Esto justificó rehacer la marcha completa con ambos operadores de evaluación activos desde cero.

## Forma y contraste

Se usan los campos físicos, la masa escalar 4πw, las conductancias de las caras internas y el piso positivo 0,17−1e−10. El peso de energía vale uno en la banda. Se omiten las dos caras que la separan de sus vecinas. El campo físico constante tiene gradiente nulo en este operador. La banda exterior r≥160 conserva por separado su pared real de media celda. El cálculo usa el presupuesto E²+λX² para K+λM y conserva el mínimo con las dos cotas de control.

La factorización LDLᵀ se hace tras reservar 1e−8 M. Se comprueba cada pivote, el residuo de reconstrucción y el margen frente al redondeo. La recurrencia hacia atrás para la diagonal inversa y los productos incluyen las holguras del protocolo exterior. Para λ=0, el residuo es inferior a 1,82e−12 y el margen restante superior a 9,85e−6. El coeficiente máximo queda bajo 0,007159162252 en r=60,0125. Una segunda matriz, ensamblada en coordenadas normalizadas por la masa, dio 0,007159162150 en esa celda. Las cinco columnas de cada una de las siete matrices cumplen el contraste independiente. La serie conserva las salidas por banda, carga, fase y caras. Para reproducir, ejecutar `OPENBLAS_NUM_THREADS=1 python3 contrastar.py` en este directorio. [Protocolo](PROTOCOLO.md) · [Datos por intervalo](resultado.json) · [Recibo](RECUPERACION.json)

## Relevo del mismo contacto

En la fila s=22,375, recuperar el perfil por celda de la cota exterior y localizar el máximo después de minimizar sobre λ. Si se concentra cerca del corte artificial en r160, probar a entrada fija una extensión de la forma hacia el interior de dos unidades radiales (la longitud de caída del peso de energía). Usar los pesos acreditados de masa, potencial y caras, incluida la cara r160, omitir la nueva cara cortada y conservar la pared real. Contrastar el ensamblaje con la energía original y con columnas independientes. Comparar la región r≥160 del nuevo operador con la cota anterior y conservar su mínimo. Si el máximo está lejos del corte o no hay ahorro suficiente, desglosar la energía exterior por términos e historial antes de otra marcha. Repetir desde cero solo al justificarlo con la fila acoplada.

La corona en s=40 sigue cubierta para las dos historias con fuentes no lineales cortadas en 13,875 y 14,625. Esta prueba solo amplía el intervalo de control del error en volumen. Quedan pendientes el cruce atribuible en r60 y la entrega útil a la receptora. El piloto permanece en espera y se conservan los mínimos de misión de 1,66414371e−6 en energía y 1,84762579e−6 en carga.
