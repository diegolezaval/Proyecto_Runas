# Realimentación radial por celda en el comparador causal

**La garantía del error de desplazamiento en todo el volumen de la donante cargada alcanza s=15,5.** El último extremo del control era 15,25. El primer rechazo pasa a 15,625 y corresponde únicamente a r<10. Las otras cuatro bandas tienen envolventes inferiores a 1,88165e−5.

| Comparación | Extremo | Mayorante del núcleo | Coste de caras en la tasa de D |
|---|---:|---:|---:|
| Control Sx | 15,375 | 1,03112e−4 | 3,32349e−5 |
| Solo la fila rechazada, misma entrada y mismos radios | 15,375 | 1,02688e−4 | 3,17844e−5 |
| Cálculo causal desde 13,5 | 15,375 | 8,57966e−5 | 2,10426e−5 |
| Última fila aceptada | 15,5 | 9,43380e−5 | 2,29585e−5 |
| Primera fila rechazada | 15,625 | 1,03805e−4 | 2,50590e−5 |

Los mayorantes se redondearon hacia arriba. Para el peso de 10–40, en la comparación a entrada fija el coste de la realimentación en la emisión del intervalo baja de 1,37627e−4 a 3,83377e−5. Al conservar la historia afinada desde 13,5, en ese mismo intervalo baja a 1,64141e−5. El archivo de resultados contiene las cinco energías y todas las combinaciones de banda de origen y peso de observación.

## Método

La primera evaluación de cada candidato reproduce las cotas de WJ, q̇, caras y Sx con la historia de entrada. A partir de esa evaluación condicional, en 0–40 se intersecta el radio físico de la banda con la caja por componente obtenida de D, κq y uβ. La división por el recorte se limita a celdas con peso positivo. Fuera de 40 se conserva el radio de la banda. Los techos físicos se convierten a unidades canónicas con √2 para las dos componentes de Φ y se multiplican por la raíz de la masa FV.

El jacobiano simétrico se descompone en centro firmado y radio de caja. Para cada celda interior se usa la matriz de magnitudes del centro más el radio; para las exteriores se usa únicamente el radio, pues el centro forma parte del potencial firmado de la energía. Se comprueba que la matriz exterior utilizada coincide con ese radio. En ambas regiones se retiene el menor radio válido entre la caja candidata y la caja afinada.

Para cada banda de origen y peso de observación se obtiene un techo local de fuerza, aplicando la matriz de magnitudes a la caja, y una ganancia local mediante la raíz del producto de las normas matriciales 1 e infinito. Se usa el [dual cuadrático](../fuerza_wj_20261127/README.md) con el presupuesto X de esa banda. Se combinan en cuadratura las bandas disjuntas con márgenes relativos 1e−11. Durante la nueva evaluación se intersecta el techo de realimentación con el coste anterior en cada una de las cuatro pasadas. Se conserva la inversa positiva que inicializa la comparación.

En cada evaluación se vuelve al mismo estado entrante. Solo el candidato aceptado aporta su fuente al historial. El control exige igualdad de las filas publicadas al desactivar únicamente el nuevo techo. Los ensayos conservan el trabajo directo del núcleo, la proyección paralela de carga y los defectos independientes.

Reproducir en este directorio con `OPENBLAS_NUM_THREADS=1 python3 marcha_fb.py`. [Protocolo](PROTOCOLO.md) · [Filas y desglose](resultado.json) · [Recibo](RECUPERACION.json)


## Alcance y siguiente comprobación

En s=15,625, la tasa de D recibe hasta 2,50590e−5 de caras, 5,66242e−6 de fuerza no lineal y 8,40109e−7 de κq̇. Las mejoras causales se activaron en 13,5 con un estado heredado cuya cota interior ya era 1,92801e−5. El siguiente contraste del mismo contacto es medir cuánto pesa esa historia previa en el nuevo rechazo: reconstruir las contribuciones anteriores y posteriores a 13,5 al presupuesto de caras y al acumulador D, manteniendo juntas las historias de estado y sus saltos. Si hay margen material, aplicar las cotas ya verificadas desde cero y comparar con la activación tardía sin cambiar datos ni tolerancias.

El piloto sigue pendiente. El prefijo aislado no acredita salida conjunta por r60 ni entrega útil. Los mínimos de misión son 1,66414371e−6 en energía y 1,84762579e−6 en carga. La corona a s=40 conserva los cortes no lineales 13,875 y 14,625.
