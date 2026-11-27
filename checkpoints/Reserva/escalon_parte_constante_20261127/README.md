# Error de desplazamiento en la corona de la donante cargada

Al integrar con signo la parte constante de la respuesta exterior, el mayorante del desplazamiento en las 800 celdas de 40 ≤ r < 60 queda por debajo de 1e−4 hasta s=40 para **ambas historias parciales**. En cada historia se lleva hasta s=40 la respuesta a las fuerzas ya aceptadas. La fuente no lineal posterior a su corte se fija a cero. La garantía en todo el volumen de la donante alcanza s=14,625.

| Última fuente no lineal incluida | Escalón anterior, máximo canónico | Menor de las dos cotas completas, máximo canónico | Radio del máximo | Máximo con campos en unidades físicas |
|---|---:|---:|---:|---:|
| 13,875 | 4,5240e−5 | 1,4744e−5 | 43,1125 | 1,1703e−5 |
| 14,625 | 2,1469e−4 | 5,9107e−5 | 43,3625 | 4,5579e−5 |

Los mayorantes de la tabla se redondearon hacia arriba. Los máximos canónicos se alcanzan en el intervalo que termina en s=40. En el segundo, el borde aporta ≤5,5520e−5, el volumen prescrito ≤1,3158e−7, la fuerza exterior no lineal aceptada ≤3,4551e−6 y el defecto numérico de volumen ≤1,327e−18.

## Cálculo y controles

Se reutilizan las dos historias de traza, la malla FV, las tres columnas y las fuentes del [estudio anterior](../contraccion_escalon_20261127/README.md). Para una traza inicial nula y Sᵢ=CᵢL constante, se tiene exactamente

    ∫ Hᵢ(t−s) z′(s) ds = Sᵢ z(t) + ∫ [Hᵢ(t−s)−Sᵢ] z′(s) ds.

En cada celda e intervalo se compara la ruta anterior con la suma de ambos términos de la derecha. La segunda usa la envolvente de posición de la traza en el intervalo observado y la envolvente de velocidad en cada intervalo fuente. Primero se forman matrices de tres columnas y después se toma la norma espectral. Al menor coste completo del borde se añade una vez la aportación independiente del volumen. Las series incluyen las dos maneras de convertir las componentes a unidades de campo.

Se mantienen el resto del propagador de Taylor, el residuo de KL=B y el resto entre nodos de retardo de la comparación anterior. El resultado recupera exactamente ambas series de la ruta original. Para una traza sinusoidal, la comparación con el forzado directo Bz por exponencial dispersa da discrepancia relativa 1,57e−15 con la parte constante separada. Este contraste es numérico. El cálculo se puede repetir aquí con `OPENBLAS_NUM_THREADS=1 python3 comparar.py`. [Protocolo previo](PROTOCOLO.md) · [Series y controles](resultado.json)

## Alcance y relevo

La integral simple de |z′| sigue por encima de su cribado provisional de 3,96e−6. El diagnóstico actual acota otro observable, el desplazamiento de la corona. Quedan por controlar la realimentación posterior a 14,625 y el primer rechazo volumétrico en r<10 al terminar s=14,75. Los mínimos de misión siguen siendo 1,66414371e−6 en energía y 1,84762579e−6 en carga. Siguen pendientes el cruce conjunto atribuible en r=60 y la entrega útil a la receptora.

La siguiente comprobación del mismo contacto es volver a la primera fila rechazada con el mismo estado entrante. En la transición 10–40, trasladar la cota por componente de We al campo físico solo donde W>0, dividiendo por W y comparando con la cota física vigente. Donde W=0 se conserva la cota anterior. Separar el coste de la fuerza interior del conmutador de caras y de los términos de carga y fase. Rehacer desde cero únicamente si mejora la comparación a estado fijo. [Relevo](../../../CONTINUAR_RESERVA.md)
