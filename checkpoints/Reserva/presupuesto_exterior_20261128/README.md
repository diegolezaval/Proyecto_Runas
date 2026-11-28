# Qué limita la cota exterior en s=23,125

A la **misma entrada y con los mismos cinco radios**, la realimentación domina el presupuesto de las dos bandas exteriores. En energía aporta **91,28 %** en 60–160 y **92,25 %** en r≥160. Es el peso dentro de la cota calculada, no una medida del error real ni del transporte de energía. Se reprodujo completa la marcha previa, que conserva la garantía hasta **s=23 de 40**.

| Banda | X | E | X por realimentación | E por realimentación | E por fuerza prescrita |
|---|---:|---:|---:|---:|---:|
| 60–160 | 0,02408762 | 0,01811937 | 78,71 % | 91,28 % | 8,72 % |
| ≥160 | 0,07875693 | 0,05927284 | 81,20 % | 92,25 % | 7,75 % |

En las últimas 4 unidades de retardo se concentra cerca del 85 % de la parte de E atribuida a realimentación, en ambas bandas. En cambio, casi toda la fuerza prescrita propagada a las bandas exteriores llega de emisiones con retardo de 4 o más. Los defectos de posición y velocidad y el desplazamiento positivo no explican el exceso. El mayor multiplicador acumulado de salto fue 1,071775 redondeado hacia arriba. El archivo desglosa los cinco pesos, el aporte nominal por tres ventanas, los saltos efectivos y el reparto cuadrático de la fuerza prescrita por anillos; ese reparto no equivale a medir cinco fuerzas independientes.

## Magnitud de la mejora necesaria

En una sensibilidad aritmética se mantuvieron los radios, las formas de evaluación y los otros aportes. Reducir proporcionalmente la parte de realimentación de X y E requiere **8,72 %** y **7,32 %**, respectivamente, para hacer caber las dos bandas; si solo se reduce la parte de la fuerza prescrita, los requisitos suben a **75,02 %** y **64,44 %**. No se restó ninguna de estas cantidades al comparador de marcha. El diagnóstico conserva el límite anterior y no habilita el piloto.

La siguiente prueba del mismo contacto es contrastar una cota del resto exterior que integre el jacobiano a lo largo del segmento entre la referencia y la solución, en vez de aplicar a todo el segmento el extremo de la caja. El radio polinómico publicado depende cuadráticamente de las semiamplitudes con coeficientes no negativos. Con ancho de referencia W e incremento B debido al error, el mayorante integrado de J se obtiene ponderando los radios en W, W+B/2 y W+B por 1/6, 4/6 y 1/6. La integral de este mayorante es exacta para un polinomio cuadrático. El término debido a W queda intacto; respecto del máximo, el coeficiente lineal en B se reduce a la mitad y el cuadrático a un tercio. La hipótesis debe contrastarse en la caja fija y con los términos efectivos recientes; no se supone que el ahorro completo en el mayorante se traslade al presupuesto. Mantener separados el jacobiano físico para traza y carga y el resto usado para la comparación exterior. Conservar los cortes de corona y los requisitos del piloto.

[Protocolo](PROTOCOLO.md) · [Presupuestos y sensibilidad](resultado.json) · [Recibo](RECUPERACION.json)

Reproducción: `OPENBLAS_NUM_THREADS=1 python3 desglosar.py`.
