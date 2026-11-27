# Trabajo transversal y columnas restauradas del jacobiano

[Protocolo previo](PROTOCOLO.md) · [Método](columnas.py) · [Verificador independiente](verificar.py) · [Coeficientes por bloque y decisiones](resultado.json.gz) · [Continuaciones por intervalo](pasos.csv.gz)

## Qué se compara

Se mantienen las referencias aisladas de gemela y receptora, la malla radial FV R256 con dr=0,025, el borde, la primera corrección y el tubo puntual de 1e−4. Se verificó la huella del CSV físico de fuentes, con la fuerza de Taylor corregida, su proyección paralela, los defectos de posición y velocidad y el resto entre muestras. En cada preparación se reconstruyeron los 320 intervalos de 0,125. Los coeficientes espectrales siguen usando máximos espaciales en bloques de cinco, el margen anterior y el recuento de inercia. [Operador e inercia](../multiplicador_radial_20261127/README.md) · [Fuentes y carga física](../energia_fisica_corregida_20261127/README.md)

Cada comparación empieza en s=0 con error cero y lleva su propio estado (D,|q|,|β|). Se prueban la escalera por décadas y una que añade los factores 1,5, 2, 3, 5 y 7 a cada década, de 1e−9 a 1e−4 inclusive. Para cada paso se ensayan los candidatos en orden, se propaga desde el último estado aceptado y se comprueba que tanto entrada como extremo caben en el mismo radio. No se usa búsqueda binaria ni se reutilizan los estados de otra variante. La positividad del sistema de comparación hace que el extremo también acote el interior del paso.

## Derivada sobre las columnas físicas

Sean (a,b,y) las perturbaciones reales, imaginarias y de mediador respecto al perfil (f,z), y λ,g,h los acoplamientos M2. Definimos d=2fa+a²+b², g₀=g+hz y K=2λd+g₀y+hy²/2. En coordenadas canónicas el jacobiano simétrico del resto tiene las entradas

| Entrada | Valor |
|---|---|
| aa | K+4λ(2fa+a²) |
| ab | 4λ(f+a)b |
| aχ | √2[g₀a+hy(f+a)] |
| bb | K+4λb² |
| bχ | √2(g₀+hy)b |
| χχ | hd |

Se construye por celda una caja firmada que cubre los coeficientes de Bernstein del puente, ambas correcciones entre muestras y el radio candidato. Para cada entrada se evalúa el polinomio en el centro más un resto absoluto de primer y segundo grado; por ejemplo, el cambio de 2fa+a² queda acotado por 2|f+a₀|Δa+Δa². Para la columna de carga se contrae el centro con (κₐ,0,κχ) **antes** de tomar normas, y el radio con sus valores absolutos. Para fase se procede igual con (0,u,0). El verificador deriva de forma independiente el polinomio del resto por paso complejo, comprueba el recinto y prueba ambas columnas. La fase restaurada uβ es la del fondo; no se supone que sea una simetría exacta de todo estado corregido.

En el trabajo directo de D solo intervienen las componentes de amplitud y la componente imaginaria perpendicular a u. Si c es el centro imaginario de una columna y e su radio por celda, se usa que el proyector elimina cualquier αu. Por tanto ‖(I−uuᵀ)Fᵢₘ‖≤‖|c−αu|+e‖ para todo α. Se comparan α=0, α=uᵀc y un candidato de minimización escalar convexa; la validez no depende de encontrar el mínimo exacto. La cota obtenida se combina en cuadratura con la cota de amplitud. La proyección que alimenta q̇ se acota separadamente por |uᵀc|+|u|ᵀe. Se conserva el menor de estas cotas y las anteriores cuando ambas son válidas; usar una cota de la norma completa para la norma proyectada también es válido por contracción. Para la fuerza prescrita y la parte transversal no acotada por columnas se mantienen las envolventes completas previas: no se resta de una norma un **mayorante** del componente paralelo. La comparación para D mantiene además ‖κ‖C|q̇|. El control sin proyectar conserva el mismo q̇ y cambia solo la cota del trabajo directo. En cada escalera se prueban por separado la columna κ, la de fase y ambas. Son presupuestos numéricos en doble precisión, con el alcance de redondeo y discretización de las entregas anteriores.

## Resultado y atribución de la mejora

**Gemela y receptora mantienen la cota puntual dentro de 1e−4 durante los 320 intervalos, hasta s=40.** Para ello basta usar la columna de fase sobre su dirección física, conservando la columna de carga anterior. La tabla muestra la cota en s=40 para las pruebas que completaron la ventana; «hasta» indica el último extremo aceptado para las demás.

| Trabajo directo y q̇ | Gemela, décadas | Gemela, intermedia | Receptora, décadas | Receptora, intermedia |
|---|---:|---:|---:|---:|
| Ambas columnas anteriores | hasta 34,25 | hasta 38,25 | hasta 34,25 | hasta 38,25 |
| Solo κ direccional | hasta 34,25 | hasta 38,25 | hasta 34,25 | hasta 38,25 |
| Solo fase direccional | 9,639e−8 | 8,576e−8 | 1,355e−7 | 1,020e−7 |
| Ambas direccionales, norma completa en D | 9,599e−8 | 8,542e−8 | 1,350e−7 | 1,016e−7 |
| Ambas direccionales, trabajo proyectado en D | 9,599e−8 | 8,542e−8 | 1,350e−7 | 1,016e−7 |

La última fila con escalera intermedia da 8,54116e−8 en gemela y 1,01504e−7 en receptora (redondeo superior). Antes de proyectar el trabajo directo las cotas eran 8,54148e−8 y 1,01506e−7. Por tanto, el efecto adicional de la proyección en este recinto es pequeño. El avance decisivo procede de medir la columna completa de fase en lugar de asignarle el peor coste transversal.

La comparación de escaleras por sí sola reproduce el fallo anterior y lo desplaza cuatro unidades de tiempo. En s=33,75, con columnas anteriores, la escalera por décadas de la gemela necesitó radio 1e−4 para un extremo de 1,797e−5; la intermedia, continuada desde el comienzo, llegó con radio 2e−6 y extremo 1,759e−6. En la receptora se observaron los mismos radios y cotas de 1,815e−5 y 1,788e−6. El cambio incluye el efecto acumulado de los pasos previos. Se conservan los fallos de esas cuatro variantes.

## Alcance y siguiente dependencia

Se cierra esta comprobación de trayectoria aislada para los dos controles, en la malla y ventana declaradas. En la cargada el mayorante global del resto corregido sigue dominado por r≥160. El factor exterior publicado aplicado a esa fuente cubre como máximo 2,775e−7 de **amplitud energética** en la corona 40–60. Quedan por sumar la fuente cercana, el intercambio con el núcleo y la realimentación de la cargada. Ninguna de estas cotas establece flujo conjunto atribuible en r60, ni entrega útil en la receptora. Se mantienen ambos umbrales de misión y el piloto no queda habilitado.

**Siguiente iteración del diagnóstico localizado.** Para la cargada, probar primero la desigualdad de energía FV con un peso radial dependiente del tiempo. Tomar como geometría de prueba un peso plano hasta 60+(40−s) y decreciente hacia la pared. Calcular en las caras si el término temporal del peso puede compensar el trabajo producido por su variación espacial, incluyendo la transición discreta, la pared y las proyecciones de carga y fase. Conservar por separado la fuente cercana y la lejana. Exigir una estimación del flujo de error que conecte el núcleo con la corona antes de propagar una nueva trayectoria. Si la comparación no reduce el coste o deja una entrada desconocida, registrar el límite. No se precisa repetir los controles aislados ni iniciar una evolución M2 completa.

**Resumen listo para el Dot principal.** Diego, con las columnas reales de carga y fase y el trabajo perpendicular en D, gemela y receptora cumplen la cota puntual de 1e−4 hasta s=40. Los extremos son 8,55e−8 y 1,02e−7 como cotas redondeadas hacia arriba. La columna de fase explica la mayor parte de la mejora. Queda pendiente controlar el error que alcanza la zona de contacto desde la cola de la cargada; el piloto continúa sin habilitarse. [Resultado en la rama científica](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/columnas_contacto_20261127)

Desde este directorio ejecutar con OPENBLAS_NUM_THREADS=1 los programas columnas.py y verificar.py. Los dos ficheros regenerados se pueden comparar byte a byte con los dos ficheros gzip publicados tras descomprimirlos.
