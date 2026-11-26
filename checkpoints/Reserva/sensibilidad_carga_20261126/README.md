# Qué cambia al variar la carga de equilibrio de la Reserva

**Decisión del paso 3.** El piloto radial por cambio de carga de equilibrio queda suspendido para el paquete registrado. La respuesta estimada alcanza su mayor valor en el perfil central de los tres. Al proyectar las dos pendientes sobre el pequeño exceso almacenado en τ300, una predice una disminución y la otra un aumento. La proyección favorable queda por debajo de una millonésima del objetivo en ambos canales. La entrega a una receptora sigue pendiente. [Protocolo fijado antes del cálculo](https://github.com/diegolezaval/Proyecto_Runas/blob/94ca3b5fefa4116a240e714e956574eb7f5036a2/checkpoints/Reserva/sensibilidad_carga_20261126/PROTOCOLO.md)

## Tres perfiles, el mismo paquete

El paquete tiene amplitud 0,00456, frecuencia física central −1,4 y energía inicial 0,0134937421 M2. La tabla estima la extracción total de cada fondo estacionario en la aproximación lineal, ponderada por el espectro del paquete. Se fija la frecuencia física incidente para cada componente y se desplaza la frecuencia relativa de dispersión con el fondo.

| ω del fondo | Carga de equilibrio | Energía extraída estimada (×10⁻⁶ M2) | Carga extraída estimada (×10⁻⁶ M2) |
|---:|---:|---:|---:|
| 0,895 | 4235,342 | 15,40548 | 17,21282 |
| 0,900 | 2745,774 | 16,64380 | 18,49311 |
| 0,905 | 1894,991 | 11,35155 | 12,54315 |

El objetivo diferencial es extraer el 1 % del exceso histórico, equivalente a 1,66414 × 10⁻⁶ de energía y 1,84763 × 10⁻⁶ de carga. La tabla siguiente muestra la extracción **adicional** proyectada al sumar al equilibrio el exceso histórico de 1,84763 × 10⁻⁴ de carga. El valor 1 en las columnas de la derecha alcanzaría el objetivo.

| Perfiles de la secante | Energía adicional / objetivo | Carga adicional / objetivo |
|---|---:|---:|
| 0,895 y 0,900 | −9,230 × 10⁻⁸ | −8,595 × 10⁻⁸ |
| 0,900 y 0,905 | +6,906 × 10⁻⁷ | +6,994 × 10⁻⁷ |

Las separaciones en carga de equilibrio son 1490 y 851 unidades M2, frente a 0,000185 de exceso histórico. Tres perfiles permiten comprobar esta propuesta de diseño. La derivada a la escala del exceso y la respuesta de una donante fuera del equilibrio siguen sin determinar. Las cotas experimentales vigentes en r = 60 proceden de la [evolución radial con gemela](../mision_paquete_negativo_20261125/README.md).

## Controles de la estimación

De los 540 valores de conversión, 180 proceden de la tabla central publicada y 360 del solucionador M2 aplicado a los perfiles vecinos. Las dos mallas radiales, los dos espaciados espectrales y los dos rellenos de FFT dan el mismo signo para cada secante. Incluyendo la cota de cola registrada, el máximo entre las variantes favorables es 6,927 × 10⁻⁷ del objetivo energético y 7,014 × 10⁻⁷ del de carga. Estos márgenes caracterizan la integración de la banda negativa entrante. Esta banda contiene el 99,999884 % de la energía del paquete. La incertidumbre física de la extrapolación entre perfiles sigue abierta.

El error relativo al recuperar la predicción central publicada fue inferior a 5 × 10⁻¹⁶. El defecto máximo de unitariedad fue 2,60 × 10⁻¹³ y el residuo relativo máximo fue 2,89 × 10⁻¹¹. En la portadora, variar la caja de R = 60 a 80 cambió la probabilidad de conversión en menos de 1,6 × 10⁻¹⁵ en cada perfil. [Nodos de dispersión](dispersion.csv) · [Resultados, controles y huellas](resultado.json)

## Qué quedó entre los radios 40 y 60

Con las cuatro series principales originales se reconstruyeron por separado el flujo diferencial que entró en la corona y su cambio de inventario. En ambos se resta la trayectoria sin paquete de su pareja con paquete y luego se resta la gemela de la cargada. Las medias cubren s = 400…480.

| Magnitud | Flujo acumulado en r40 menos r60 | Cambio de inventario en la corona | Porcentaje del exceso histórico |
|---|---:|---:|---:|
| Energía | 2,96358 × 10⁻⁸ | 2,96360 × 10⁻⁸ | 0,01781 % |
| Carga | 2,94089 × 10⁻⁸ | 2,94090 × 10⁻⁸ | 0,01592 % |

La mayor discrepancia instantánea entre ambos cálculos en la ventana fue 3,09 × 10⁻¹² M2. La continuidad explica por qué parte de la señal que cruzó r = 40 todavía figura en el inventario entre ambos radios.

Se puede reproducir la entrega desde la raíz del repositorio con `OPENBLAS_NUM_THREADS=1 python3 checkpoints/Reserva/sensibilidad_carga_20261126/medir.py`. El programa comprueba las huellas de las cuatro series, compara el caso central con el diseño publicado y regenera los dos archivos de resultados. Usó Python 3.12, NumPy 2.3.5 y SciPy 1.17.0. [Código](medir.py)
