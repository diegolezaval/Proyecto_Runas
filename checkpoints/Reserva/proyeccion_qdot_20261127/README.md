# Proyección imaginaria de la fuerza en la tasa de carga

**La donante cargada conserva la certificación de todo el volumen hasta s=14,875.** En s=15, reconstruir los doce intervalos con la nueva proyección baja el mayorante del núcleo a 1,06485e−4. Solo r<10 excede el tubo de 1e−4. El rechazo limita la estimación del error en esa fila.

| Prueba en s=15 | Mayorante de la tasa de carga en valor absoluto | Trabajo κq̇ | Mayorante del desplazamiento interior |
|---|---:|---:|---:|
| Control causal de WJ y caras FV | 1,28532e−5 | 1,29423e−5 | 1,18688e−4 |
| Caja, Cauchy y WJ, entrada del control | 8,80849e−7 | 8,86960e−7 | 1,15166e−4 |
| Dual y cotas anteriores, misma entrada | 8,80848e−7 | 8,86958e−7 | 1,15166e−4 |
| Dual desde s=13,5, con el historial completo | 8,07597e−7 | 8,13199e−7 | 1,06485e−4 |

Los mayorantes de las tablas se redondean hacia arriba. En la última pasada dual a entrada fija, los valores comparables para la proyección de 10–40 son 1,19641e−5 para el control previo, 1,78051e−8 para la caja, 3,39171e−7 para Cauchy, 5,14163e−7 para ‖u‖ por el mayorante WJ y 1,78037e−8 para el dual. La mayor parte del ahorro la aporta la caja. Manteniendo entrada y demás tasas del control, suprimir hipotéticamente q̇ en la última fila deja la cota interior en 1,14991e−4. Por ello se probó el efecto acumulado con las historias causales reconstruidas.

## Presupuesto de carga por banda a igual entrada en s=15

| Banda | Fuerza imaginaria proyectada, control | Fuerza imaginaria proyectada, dual | Conmutador proyectado | Defecto de fase |
|---|---:|---:|---:|---:|
| r<10 | 5,49158e−7 | 5,23099e−7 | 0 | 1,25778e−9 |
| 10≤r<40 | 1,19641e−5 | 1,78037e−8 | 3,38242e−7 | 4,26275e−10 |
| 40≤r<60 | 0 | 0 | 0 | 0 |
| 60≤r<160 | 0 | 0 | 0 | 0 |
| r≥160 | 0 | 0 | 0 | 0 |

Los ceros corresponden a la proyección recortada. El presupuesto añade la fuente prescrita ≤1,92916e−11 y los defectos cinemáticos de velocidad ≤3,38975e−19 y de posición ≤6,11909e−21. El código contrasta su suma con el valor usado en la marcha. La restitución de fase y el trabajo de caras se registran en el presupuesto de energía por separado.

## Método

La referencia es la [marcha causal WJ con conmutador FV](../fuerza_wj_20261127/README.md). Se reconstruyen sus fuentes, historias, recortes y radios desde cero y se exige igualdad exacta de todas las filas de control. En 10 ≤ r < 40, cada pasada recalcula la matriz de magnitudes Uᵢ y convierte la caja de los tres campos al vector canónico pᵢ con la masa de la celda. El factor |uᵢ| Wᵢ proyecta la fila imaginaria sobre la coordenada de carga.

Los tres contrastes simples son la suma de techos aᵢ, la cota de Cauchy X‖c‖₂ y ‖u‖₂ de la banda multiplicada por el mayorante certificado de ‖WJx‖₂. Para combinar cajas y norma de banda, cada celda contribuye a lo sumo min(aᵢ,cᵢrᵢ), donde aᵢ=|uᵢ|Wᵢ(Uᵢpᵢ)imag, cᵢ=|uᵢ|Wᵢ‖(Uᵢ)imag‖₂ y la suma de los rᵢ² está acotada por X². Si caben todos los techos se usa su suma. En otro caso, para cualquier λ positivo se suma λX² al máximo separable de min(aᵢ,cᵢrᵢ)−λrᵢ². Ese máximo se alcanza en rᵢ=min(aᵢ/cᵢ,cᵢ/(2λ)) para las ganancias positivas. La bisección usa la norma de r para elegir λ; la expresión dual sigue siendo mayorante con cualquier valor positivo de λ. Se omiten las ganancias nulas.

La implementación usa precisión extendida para el dual y holgura relativa 1e−11. Se comprueban dos celdas de ganancias 2 y 1 con presupuestos que dan saturación parcial, ninguna y total. Se añade una celda de ganancia cero al contraste. Se conserva el mínimo con la estimación anterior. El desglose numérico contiene por banda la proyección de la fuerza, el defecto de fase y el conmutador proyectado, además de la fuente prescrita y los defectos de posición y velocidad. El trabajo directo de WJ, la restitución de fase y el conmutador en la energía siguen sus cálculos propios.

Reproducción desde este directorio con `OPENBLAS_NUM_THREADS=1 python3 medir_qdot.py`. [Protocolo](PROTOCOLO.md) · [Resultados y bandas](resultado.json) · [Recibo](RECUPERACION.json)


## Continuación del mismo contacto

En la marcha desde s=13,5, el último punto aceptado del núcleo es 9,06134e−5 a s=14,875. En s=15 las cuatro bandas exteriores quedan por debajo de 3,31462e−5. El trabajo directo de caras en la tasa de D es 4,82899e−5, frente a 4,81969e−6 de fuerza no lineal y 8,13199e−7 de κq̇. La nueva proyección de carga deja el coste de caras como término principal.

La siguiente comprobación es identificar qué alimenta la energía de 10–40 usada por el conmutador. A igual entrada, desagregar su historial causal por fuente y por retardo: fuerza prescrita, trabajo del desplazamiento positivo, realimentación y defectos numéricos. Conservar pesos, saltos de métrica y los términos del propio intervalo. Exigir que la suma recupere la envolvente publicada de energía y el coste de caras antes de intentar otra marcha. Así se puede elegir qué término afinar por su contribución efectiva.

El piloto continúa pendiente del cruce atribuible en r60 y de la entrega útil a la receptora. Se mantienen los mínimos E=1,66414371e−6 y Q=1,84762579e−6. Los presupuestos de la corona hasta s=40 siguen limitados a los cortes previos de sus fuentes no lineales (13,875 y 14,625).
