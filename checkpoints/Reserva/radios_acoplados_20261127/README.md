# Donante cargada · primer intervalo rechazado

El horizonte acreditado en todo el volumen sigue en **s=14,625**. A s=14,75 solo el núcleo r<10 excede el tubo de 1e−4. Los 117 intervalos de entrada y el candidato de control coinciden exactamente con el archivo de la [comparación anterior](../caja_componentes_20261127/README.md).

| Comparación en s=14,75 | Envolvente en r<10 | Fuerza no lineal en D | Gradiente de caras | Curvatura | Trabajo κq̇ | Fase común restaurada, máx. |
|---|---:|---:|---:|---:|---:|---:|
| Cinco techos, entrada archivada | 1,43605e−4 | 9,56842e−5 | 3,60011e−5 | 2,40647e−6 | 1,86608e−5 | 3,37022e−6 |
| Radios por banda, misma entrada | 1,22183e−4 | 3,35528e−5 | 3,60011e−5 | 2,40647e−6 | 6,12956e−6 | 3,27288e−6 |
| Radios por banda y traslado de We, misma entrada | 1,21263e−4 | 3,03501e−5 | 3,60011e−5 | 2,40647e−6 | 6,12317e−6 | 3,26870e−6 |
| Ambos cambios desde cero | 1,16101e−4 | 3,01753e−5 | 3,58545e−5 | 2,39747e−6 | 6,05962e−6 | 3,11972e−6 |

Los valores tabulados se redondean hacia arriba. Fuerzas y trabajo entran en la derivada del presupuesto reducido. La fase restaurada entra en la reconstrucción del desplazamiento. Los máximos de esas columnas tienen funciones distintas.

## Insumos, método y controles

Se usaron el puente corregido archivado, sus fuentes y defectos entre muestras, la pared FV y la escalera publicada. Se recalculó el prefijo con los radios archivados y se exigió igualdad de todas sus filas antes del contraste. Al probar el intervalo siguiente, solo la banda 40–60 necesitó subir su radio entre las cuatro exteriores, de 5e−9 a 7e−9. Con los cinco radios finales (1e−4, 3e−5, 7e−9, 1,5e−5, 1,5e−5) se recalculó la solución acoplada desde la misma entrada. Se exigió por banda el máximo de entrada y envolvente menor o igual a su radio, todo en un único candidato.

Para 10–40 se extendió la diagonal de evaluación de las inversas FV a carga fija y fase transversal. El peor residuo fue 1,775e−12. Se conservaron la corrección por el hueco y el margen publicado. Para cada componente, la cota de We suma la parte reducida en D y las restituciones locales κq y uβ. Tras convertir a unidades físicas se divide por W en celdas con W>0 y se intersecta con la caja previa. En W=0 se comprueba su conservación exacta. Solo se afina el jacobiano local en la estimación del núcleo, conservando las cotas físicas independientes, el defecto de fase, q̇ y el conmutador.

A entrada fija, la contribución de la fuerza de r<10 baja de 6,60708e−6 a 5,26442e−6 con los radios y a 5,21082e−6 con el traslado. Al repetir desde cero, la última cota interior aceptada es 9,43109e−5. Para la fila rechazada, las otras cuatro envolventes son como máximo 2,44530e−5, 5,18472e−9, 1,18946e−5 y 1,12199e−5 respectivamente. El JSON conserva los intentos, los gradientes, la carga y el defecto de fase. Reproducir en este directorio con `OPENBLAS_NUM_THREADS=1 python3 comparar.py`. [Protocolo](PROTOCOLO.md) · [Datos](resultado.json)

## Siguiente comprobación del mismo contacto

El término de gradiente del conmutador de caras es ahora la mayor contribución individual a la derivada de D en la fila rechazada. A igual estado entrante, comprobar si el operador FV exacto [T,W] restringido a las caras del recorte admite una norma menor respecto de la energía positiva disponible en 10–40. Usar la métrica y los pesos que realmente acota la continuación, incluir ambos lados de cada cara y verificar por residuo o inercia cualquier mayorante espectral. Comparar con la suma anterior de gradiente y curvatura, conservando la proyección paralela en q̇. Si no mejora a estado fijo, conservar el límite y evitar repetir la trayectoria.

La misión sigue exigiendo 1,66414371e−6 en energía y 1,84762579e−6 en carga, cruce conjunto atribuible en r60 y entrega útil a la receptora. El fallo de esta estimación deja indeterminado el desplazamiento físico real. El piloto sigue pendiente.
