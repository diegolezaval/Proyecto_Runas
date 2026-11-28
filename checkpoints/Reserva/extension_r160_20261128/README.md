# Campo exterior de la donante cargada con energía a ambos lados de r160

La garantía del tubo en todo el volumen de la cargada pasa de **s=22,25 a s=22,375**. En s=22,5 solo el núcleo r<10 excede el techo de 1e−4. Su mayorante es 1,04839e−4 y el exterior r≥160 queda bajo 7,77199e−5.

En la comparación a entrada fija en s=22,375, el máximo exterior permanece en r=160,0125. Para X≈0,0548091801 y E≈0,0401353711, el mayorante pasa de 1,05394e−4 a 9,07406e−5. Se recuperan exactamente las otras cuatro envolventes y los radios. El candidato contiene la entrada y las cinco envolventes. La repetición desde cero incorpora toda la historia posterior con sus propios radios. Las cotas citadas se redondean hacia arriba.

## Método

El control usa la [marcha desde cero de las cinco bandas](../evaluacion_60_160_20261128/README.md). La prueba a entrada fija conserva el estado, el historial causal y los radios de la primera fila rechazada en s=22,375. En la comparación se reconstruye el máximo entre las celdas de r≥160 después de tomar en cada una el mínimo de la escalera publicada de λ.

Se incorporan 80 celdas hasta r=158, una longitud de caída del peso. En ellas la masa de energía es 4πwᵢkᵢ y el potencial escalar se acota inferiormente con el piso 0,17−1e−10. Las caras internas reciben la media aritmética de los pesos de las dos celdas. Así se recupera la energía disponible en la cara r160. La cara cortada en r158 se omite y la pared de r256 conserva la distancia de media celda. La forma restringida consta de términos positivos de la energía acreditada. La observación se evalúa únicamente en r≥160.

Para cada λ se añade λM en la región observada. De este modo, el presupuesto E²+λX² solo usa la norma de desplazamiento X donde ya está disponible. La matriz física actúa directamente sobre valores de campo. Antes de factorizar se resta una reserva de 1e−8 veces la masa ponderada. El control exige pivotes positivos y reserva suficiente para cubrir tanto el residuo de reconstrucción como una holgura de 128 unidades de precisión doble escalada por la norma de la matriz. La diagonal inversa se calcula hacia atrás con redondeos ascendentes en precisión extendida y margen relativo adicional. Se conserva por celda el menor mayorante, además del mínimo con la conversión vigente.

El contraste usa una segunda matriz en coordenadas normalizadas por la masa. Se cotejan seis columnas por λ, incluidas las celdas que comparten la cara r160. Un campo de prueba suave contrasta la forma cuadrática con una suma directa de potencial, caras y pared. El archivo numérico contiene todos los márgenes y resultados de las dos resoluciones. Se mantienen el alcance numérico y los controles de discretización del diagnóstico de origen.

Para reproducir, ejecutar `OPENBLAS_NUM_THREADS=1 python3 contraste.py` desde este directorio. [Protocolo](PROTOCOLO.md) · [Resultados](resultado.json) · [Recibo](RECUPERACION.json)

Para λ=0 el margen de factorización supera 2,32387e−5. En la primera celda de observación la raíz de la diagonal inversa usada es inferior a 0,002262738428 y la solución independiente da aproximadamente 0,002262738386. Se comprobaron 42 columnas en total.

## Siguiente comprobación

Conservar la historia hasta s=22,375 y los radios del rechazo en s=22,5. Comparar por celda del núcleo la evaluación vigente con una evaluación conjunta de amplitud y fase. Las columnas restauradas κq y uβ están en subespacios ortogonales en las coordenadas canónicas. Verificar sus soportes y la conversión física. Como primer contraste sumar al coste transversal D la norma euclídea de ambas restauraciones, con sus coeficientes locales. Si la escala resulta insuficiente, estudiar la matriz local de evaluación del Hessiano ya invertido, distinguiendo el bloque de amplitud y la fase perpendicular con el mismo presupuesto D. Usar un mayorante de la norma con margen, contrastar el límite con restauraciones nulas y conservar el mínimo vigente. Medir primero la celda limitante y el ahorro posible a la misma entrada. Mantener por separado carga, fase, defectos y caras en la propagación.

La corona en s=40 conserva las historias parciales con cortes de fuente en 13,875 y 14,625. Las puertas de misión siguen pendientes, con mínimos de 1,66414371e−6 en energía y 1,84762579e−6 en carga. El piloto sigue en espera.
