# Historial de la amplitud de energía que acota el trabajo de caras

**La fuerza auxiliar Sx del comparador explica el 76,83 % del mayorante de amplitud de energía de 10–40 en la fila rechazada de s=15.** La realimentación aporta el 23,17 %. En la última fila aceptada, s=14,875, sus fracciones son 78,52 % y 21,48 %. El coste publicado de caras se recupera en ambos extremos. El horizonte integral sigue en 14,875 y el piloto continúa pendiente.

| Fuente de la amplitud en 10–40 | s=14,875, aceptado | s=15, candidato rechazado |
|---|---:|---:|
| Fuerza prescrita | 1,66486e−8 | 1,73243e−8 |
| Desplazamiento positivo S | 2,78394e−4 | 3,23617e−4 |
| Realimentación | 7,61529e−5 | 9,75906e−5 |
| Defecto de posición | 1,54790e−16 | 1,60966e−16 |
| Defecto de velocidad | 1,14050e−16 | 1,18600e−16 |
| Amplitud total | 3,54563e−4 | 4,21225e−4 |
| Coste de caras en la tasa de D | 4,06477e−5 | 4,82899e−5 |

Los mayorantes se redondean hacia arriba. En s=15 el intervalo propio aporta el 12,50 % de la amplitud, los retardos de 1–7 pasos el 51,37 %, los de 8–31 el 33,28 % y los de al menos 32 pasos el 2,85 %. En el propio intervalo la comparación de Sx tiene componentes cuadráticos 5,542e−8 en r<10 y 1,670e−8 en 10–40; los otros tres son cero. La fuerza auxiliar S está concentrada en el interior. Queda justificado probar una cota espacial de Sx a la misma entrada y en las fuentes históricas conservadas.

## Reconstrucción

Se usó la [marcha de q̇ y WJ](../proyeccion_qdot_20261127/README.md) de la donante cargada. Para una observación al final del intervalo n, la fuente nacida en el intervalo i recibe el coeficiente E[n−i,1] del comparador en 10–40 y el producto de los saltos de métrica desde i+1 hasta n. El impulso de la propia fila recibe E[0,1] y producto uno. Se conservaron el historial causal y las cajas de cada candidato aceptado; se incluyó por separado la última fila ensayada. La auditoría no altera los radios ni la decisión de aceptación.

En la amplitud de energía se suman cinco presupuestos positivos: norma ponderada de la fuerza prescrita, norma ponderada de la fuerza auxiliar Sx del comparador, mayorante de realimentación, defecto de posición convertido por el operador y defecto de velocidad. Para Sx se reconstruyó la norma de las cinco contribuciones de banda. Para la realimentación se recuperó el mínimo entre la norma por bandas y el máximo global por la cota del desplazamiento ponderado. Se guardan los cuadrados de los componentes espaciales de dichas normas. Las bandas no se suman linealmente dentro de una norma cuadrática.

Se calculó de nuevo el coste de caras con la amplitud reconstruida. Antes de s=13,5 se aplicó el coste de gradiente y curvatura original; después se comparó con γ veces la amplitud de energía y se conservó el menor, tal como en el control. Las columnas de fuente describen sumandos del mayorante y sus dependencias causales, sin interpretación como energías físicas independientes.

En `resultado.json`, cada intervalo contiene sus totales por fuente y cuatro bandas de retardo en pasos de 0,125. Para los extremos 14,875 y 15 se publica además la tabla de todos los intervalos de emisión con sus saltos y pesos. La reproducción exige igualdad de las filas con el cálculo publicado y verifica energía y coste de caras con tolerancia 2e−12 relativa más 1e−25 absoluta.

Reproducir desde este directorio con `OPENBLAS_NUM_THREADS=1 python3 auditar.py`. [Protocolo](PROTOCOLO.md) · [Series por fuente y retardo](resultado.json) · [Recibo](RECUPERACION.json)


## Relevo

Las discrepancias máximas en las 120 filas fueron 3,80e−19 para la amplitud y 4,07e−20 para las caras. La siguiente comprobación del mismo contacto es intersectar la norma de desplazamiento de cada banda con las cajas por componente al acotar Sx por celda. Conservar el peso de observación, el soporte y las tres componentes reales del operador S. Comparar primero en el historial fijo sin realimentar el ahorro. Solo un recálculo causal con márgenes y entrada común puede acreditar una fila adicional. La corona a 40 conserva sus cortes 13,875 y 14,625; la atribución en r60 y la entrega siguen pendientes con los mínimos E=1,66414371e−6 y Q=1,84762579e−6.
