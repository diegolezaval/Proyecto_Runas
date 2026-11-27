# Campo de la corona producido por las fuentes ya acotadas

[Protocolo](PROTOCOLO.md) · [Contracción física](contraer.py) · [Respuesta al escalón](escalon.py) · [Series de la traza](contraccion.json) · [Presupuestos de la corona](escalon.json)

## Contracción del jacobiano con el adjunto

Se mantuvieron la cargada, las bandas, el jacobiano físico de la primera referencia corregida y los candidatos aceptados de los dos prefijos publicados. Para cada intervalo de fuente se reconstruyó la misma norma de volumen del error en cada banda. La traza de tres bandas coincide con cada fila de la continuación anterior y la de cinco bandas reproduce la respuesta a s=40 de las fuerzas antiguas en ambos historiales. Se conservan la fuerza prescrita durante toda la ventana, los defectos numéricos y la contribución cinemática directa a z′. La fuerza no lineal posterior al prefijo se fija a cero solo en esta atribución.

En 10–40 y 60–160 se usaron subregiones de dos unidades. En cada una se acotan las nueve entradas de la matriz física por el valor absoluto del centro firmado más el radio de caja. En el núcleo del adjunto se acumula la norma de Frobenius por componente de campo y grupo de tres observables para cada coeficiente de Taylor. La suma sobre los órdenes cubre todo el intervalo entre nodos. El cambio de signo de la componente imaginaria empleado en la propagación conserva esas normas. Multiplicar el vector de normas por la traspuesta del mayorante matricial y sumar en cuadratura sobre entradas y subregiones da una cota de la norma del operador compuesto. Se multiplica **una vez por la norma de desplazamiento de la banda completa**. El error global del núcleo recortado y discretizado se multiplica por el mayorante global del jacobiano en esa banda y se añade una vez. La elección del menor producto válido por intervalo, banda y retardo preserva también la comparación anterior. Se verificó la desigualdad contra una contracción matricial directa de prueba.

| Fuentes no lineales incluidas | Cota simple anterior hasta 40 | Con contracción | Parte no lineal observada después del prefijo | Cota ponderada hasta 40 |
|---|---:|---:|---:|---:|
| s≤13,875 | 8,832e−5 | 4,323e−5 | 4,046e−5 | 8,575e−5 |
| s≤14,625 | 3,341e−4 | 2,060e−4 | 1,998e−4 | 4,218e−4 |

La integral simple incluye el término lineal de toda la ventana y se compara con el cribado provisional de 3,96e−6. En el prefijo 13,875 la banda 10–40 aporta hasta 3,485e−5 y la 60–160 hasta 6,486e−6 a la integral simple, antes del mínimo conjunto interior. El presupuesto sigue siendo demasiado amplio. La integral ponderada pertenece a la estimación con crecimiento temporal y se conserva por separado.

## Tres columnas de la respuesta al escalón

En r≥40 se corta la cara FV con la primera celda interior vecina; el valor de error canónico físico z de esa vecina entra como Bz. Se conserva la diagonal completa del bloque exterior K y la pared de media celda en R256. Se resuelve KL=B para las tres componentes y se propaga la ecuación homogénea rotante (x,v) desde (L,0). Para cada centro de la corona 40≤r<60 se calcula la matriz Hᵢ(l)=Cᵢ(L−x(l)). La resta se realiza por entrada, antes del valor singular máximo. Cᵢ divide por la raíz de volumen y, en la salida de campos M2, también por √2 en las dos componentes de Φ. Se registra además la salida en las coordenadas canónicas físicas usadas para la prueba conjunta del tubo.

Con traza inicial cero, el desplazamiento provocado por el borde es la convolución de Hᵢ con z′. La derivada de H es la respuesta impulsiva al forzado Bz. Así se incluye directamente la contribución que en la ruta de levantamiento se restituía al extremo. El método conserva Hᵢ(0)=0 exactamente y no vuelve a sumar Lz. Para un vector de traza proporcional a sen(s), se compara la convolución con una evolución lineal forzada independiente mediante exponencial dispersa aumentada. El contraste usa la malla exterior completa y dos órdenes de Gauss.

Se aprovecha la energía exterior positiva, conservada por la giroscopia. Para h=1/32 y Taylor de orden 40 se mayoriza la norma del generador en energía por b=√‖K‖∞+2ω. El error relativo local queda bajo exp(bh)(bh)^41/41!. Se acumulan los 1280 defectos con la estabilidad homogénea y se añade dos veces el coste energético del residuo de KL=B, para el desplazamiento estático y el homogéneo. Se evalúan matrices en extremos y punto medio de cada paso con su propio control de truncación. Para cubrir el interior de cada mitad se añade (h/2)²‖B‖/(8√(4πwᵢ)) al mayor valor singular de sus extremos: la solución diferenciada parte de (0,−B) para la elevación exacta, y su energía acota la norma de la aceleración. La convexidad de la norma matricial permite interpolar en matriz. A cada observación se le asignan ambos intervalos posibles de retardo. Los restos formales se evalúan en doble precisión; no se certificó el redondeo de la máquina.

## Fuentes de volumen y alcance

A la respuesta del borde se añade una vez el desplazamiento del problema exterior con borde interior homogéneo, debido a la fuerza prescrita, los defectos de posición y velocidad, y la fuerza no lineal local ya aceptada en las bandas 40–60, 60–160 y 160–256. La fuerza prescrita archivada en r<60 sirve como mayorante para la porción 40–60. Se emplea la energía con frente móvil y exponente 0,051 previamente verificado, conservando el máximo temporal desfavorable de cada intervalo y sumando en cuadratura los soportes disjuntos de cada fuente. En la corona el peso vale uno. La conversión a campo usa el menor entre la resistencia FV acumulada desde la cara interior homogénea y la cota por el mínimo del potencial positivo exterior. Las fuerzas de la cara de r40 quedan en H, fuera de las fuentes de volumen. Se suman los términos por celda **antes** de tomar el máximo espacial; las columnas de máximos de borde y volumen pueden corresponder a radios distintos.

Las filas de cada historial de escalon.json dan el tiempo y los máximos de intervalo del borde en coordenadas canónicas y M2, del volumen y de la suma en ambos sistemas. Los máximos por celda, en ese mismo archivo, cubren toda la ventana temporal. Esta prueba observa desplazamiento. La energía y la carga entregadas a la receptora aún requieren sus propios balances.

| Historia de realimentación | Máximo del borde en norma canónica | Máximo conjunto en norma canónica | Máximo conjunto en campos M2 |
|---|---:|---:|---:|
| s≤13,875 | 4,502e−5 | **4,524e−5** | 3,268e−5 |
| s≤14,625 | 2,144e−4 | **2,147e−4** | 1,549e−4 |

Los máximos conjuntos canónicos ocurren al final de la ventana, en la primera celda exterior (r=40,0125). Para el histograma de fuentes hasta 13,875, en esa celda se suman ≤4,502e−5 del borde, ≤1,179e−8 de la fuente prescrita, ≤2,088e−7 de la realimentación exterior y ≤1,189e−19 de los defectos numéricos. El contraste con forzado directo tuvo error relativo 1,390e−15; la deriva relativa máxima de la matriz de energía de las tres columnas fue 8,433e−14. La cuadratura de ocho nodos difiere de la de dieciséis en 1,480e−6 relativo. El resto formal nodal, incluido el residuo del levantamiento, es ≤1,980e−10 en energía; el mayor suplemento de interpolación entre nodos es 0,04880 en norma del mapa.

**Decisión.** El primer historial cabe en el presupuesto puntual de 1e−4 de la corona hasta 40 para las fuentes incluidas, aunque la integral simple de la traza continúe por encima del cribado provisional. Con el segundo historial, el mayorante conjunto rebasa 1e−4 por primera vez en el intervalo que termina en s=26,75. La garantía del volumen completo sigue en s=14,625; la realimentación posterior, los balances conjuntos de contacto y la entrega útil permanecen abiertos. El piloto no queda habilitado.

**Siguiente comprobación.** El exceso del segundo historial se concentra en la primera celda exterior y en la entrada de borde. Comprobar si se puede usar simultáneamente la cota archivada de |z| y la de |z′|. Una comparación exacta resta primero una matriz constante del núcleo H y solo entonces integra esa constante de forma firmada con z(t)−z(0). Contrastar a la misma historia con el núcleo completo, sin duplicar el término estático ni relajar el tubo.

**Resumen para el Dot principal.** Diego, el escalón exterior sitúa en ≤4,524e−5 el desplazamiento canónico de la corona hasta 40 para las fuentes no lineales aceptadas hasta 13,875. Para el historial hasta 14,625 la cota es ≤2,147e−4 y domina la entrada por r40. Son presupuestos parciales. [Informe y datos](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/contraccion_escalon_20261127)

Desde este directorio ejecutar `OPENBLAS_NUM_THREADS=1 python3 contraer.py` y luego `OPENBLAS_NUM_THREADS=1 python3 escalon.py`. Se conservan E≥1,66414371e−6, Q≥1,84762579e−6, atribución en r60 y entrega útil.
