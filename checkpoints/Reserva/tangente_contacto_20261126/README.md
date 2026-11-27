# ¿Bastan dos poblaciones y dos fases para describir el contacto?

**Decisión.** En la preparación ensayada, el ajuste de esas cuatro coordenadas deja fuera al menos el 99,80 % de la norma de la fuerza adicional del contacto en el instante inicial. En las tres separaciones falla el balance diferencial de la receptora por encima de los cambios de cuadratura y de paso temporal de la preparación. Esta reducción queda descartada para pronosticar entrega. El mecanismo completo en M2 sigue indeterminado. [Protocolo previo](PROTOCOLO.md)

## Qué se probó

Se reutilizaron los estados físicos preparados. En cada uno de los 36 casos se evaluaron dos cuadraturas. Las fases fueron 0 y ±π/2, las separaciones 80, 100 y 120, y las donantes la cargada y la gemela en las dos preparaciones temporales. La receptora fue la del paso 2. Se trabajó únicamente en la instantánea de contacto.

Sean D y R los campos complejos preparados, incluida su fase, y z e y sus mediadores. Para cada centro se multiplican el campo complejo y su velocidad por exp(a+iφ). Los dos tangentes correspondientes en espacio de fases son (Φ,Π) e i(Φ,Π). El cambio de población aislada a primer orden es 2 da en unidades relativas. Definimos el vector de contacto como el campo vectorial M2 de la superposición menos la suma de los dos campos vectoriales aislados. Su parte cinemática y los laplacianos se cancelan por linealidad. La parte restante es la diferencia de aceleraciones del potencial M2. La interacción en χ incluye el término proporcional a 2 Re(D*R) y los términos de acoplamiento mixto. Θ se lee del modelo publicado.

Se proyectó ese vector por mínimos cuadrados en la base de cuatro tangentes. La norma espacial incluye los campos y velocidades en unidades naturales y el peso 1/2 de χ. Las integrales se calcularon por revolución, particionando por el centro más próximo para cubrir cada volumen una sola vez. La integración alcanza el borde de los soportes. Cada núcleo tiene radio 40. Las lecturas globales incluyen el exterior de los núcleos. La evolución aislada se conserva en el vector base; las tasas ajustadas describen únicamente la corrección al unir los estados. Ningún flujo interviene en el ajuste.

## Identificación y balances

La matriz de Gram de los tangentes estuvo bien condicionada (condición máxima 1,000068). Para el Jacobiano de las seis lecturas se dividió cada fila por su norma euclídea, con iguales unidades adimensionales para log-amplitud y fase. La fase global común se anula, conforme a la simetría U(1). En los 36 casos se resolvieron **dos direcciones de inventario**, con valores singulares próximos a 2 y √2. La condición en ese subespacio es aproximadamente 1,414. La tercera dirección quedó por debajo de la sensibilidad numérica estimada al comparar las dos cuadraturas. Esto mide la identificabilidad en esta prueba, sin establecer el rango algebraico exacto de la fase relativa.

Para verificar cada balance se calculó el flujo entrante de M2 sobre su propia esfera y la variación de inventario de la reducción. La diferencia entre la tasa reducida y la exacta es el diferencial del inventario aplicado al residuo **proyectado menos exacto**. En energía se incluyen la variación de gradientes del campo complejo, la del potencial y la cinética de ambos campos. El flujo energético de cara incluye también el del mediador. La tasa global exacta es cero para los datos compactos. El archivo de resultados contiene ambos flujos de cara, los balances globales, las tasas y los seis defectos por caso. Las 12 corrientes impares de la cara receptora se cotejaron con la cuadratura de 192 nodos del estudio previo. Las diferencias máximas fueron 6,18 × 10⁻¹¹ en Q y 8,17 × 10⁻¹¹ en E por unidad de tiempo.

| Separación | Defecto de tasa Q en la receptora | Defecto de tasa E en la receptora |
|---:|---:|---:|
| 80 | −1,3351 × 10⁻⁵ | −1,2015 × 10⁻⁵ |
| 100 | −1,2999 × 10⁻⁶ | −1,1693 × 10⁻⁶ |
| 120 | −8,1407 × 10⁻⁶ | −7,3249 × 10⁻⁶ |

Cada valor es la semidiferencia de fases opuestas, cargada menos gemela, en la preparación de menor paso temporal. Las unidades son M2 por tiempo. En las tres separaciones el error global tiene el mismo signo y casi la misma magnitud que el de la receptora. El mayor cambio de cuadratura en las seis cifras de la tabla es 8,08 × 10⁻¹⁰; el mayor cambio de preparación temporal es 3,01 × 10⁻⁹. Las cifras son defectos de **tasas iniciales**. Los umbrales históricos son cantidades entregadas durante una ventana; hace falta una predicción temporal con error controlado para compararlas.

## Qué explica el fallo

La aceleración del mediador χ representa del 98,43 % al 98,67 % de la **norma al cuadrado** de la fuerza de contacto bajo la métrica especificada. Los cuatro tangentes elegidos carecen de componente en χ. Es un motivo estructural del residuo de esta base. La masa elevada del mediador permite que una aceleración apreciable produzca una deformación pequeña. La fracción de norma por sí sola no mide energía accesible ni predice una descarga.

El siguiente contraste justificado en **este mismo contacto** consiste en resolver, sobre los mismos estados y sin avanzar el reloj, la respuesta estática inducida del mediador con el operador positivo −Δ+M²+h|Φ|². Deberá contrastar la reducción del residuo en Φ y χ, el coste de deformar el mediador y la incertidumbre del término dinámico. Una cancelación estática por construcción sería insuficiente. La captura, el cruce por r60 y la recarga conservan sus condiciones anteriores. El piloto M2 sigue sin habilitarse.

Para reproducir desde esta carpeta se usan Python 3.12, NumPy 2.3.5 y SciPy 1.17.0. Ejecutar `OPENBLAS_NUM_THREADS=1 python3 proyectar.py` y luego `python3 verificar.py`. [Cálculo](proyectar.py) · [Controles independientes](verificar.py) · [Matrices, tasas y resultados numéricos](resultado.json)
