# CP12/P4 · Estabilidad temporal y robustez

El piloto, la tercera malla y el contraste Galerkin alcanzaron τ160. La tercera malla redujo la discrepancia nominal de χ en espacio de fases entre los dos pares de 1,014856 % a 0,018464 %. El contraste Galerkin mantuvo el margen empírico al 2 % en las cinco métricas y, para la malla candidata, acotó χ en espacio de fases por 0,098480 % en τ160. Se reutilizan las cápsulas acreditadas de la malla candidata de τ0 a τ160.

## Contrastes registrados

La base es P4 con las seis funciones de Cauchy de CP04, h=.03125, R=220, L=4, ε=.020, DOP853, paso máximo .02, rtol 10⁻¹⁰ y atol 10⁻¹². Mantener la acción, el código numérico, el entorno original acreditado, las observaciones cada .4 y los cierres cada 8 hasta τ160.

| Caso | Cambio respecto de la base | Lectura |
| --- | --- | --- |
| PASO | Paso máximo .01 | Sensibilidad a la cota de paso |
| TOL | rtol 10⁻¹¹ y atol 10⁻¹³ | Sensibilidad a las tolerancias |
| CAJA | R=264 | Extensión del dominio y contabilidad del exterior |
| ANGULAR | L=6 | Efecto de ampliar la proyección |
| EPS018 | ε=.018 | Respuesta a menor amplitud de semilla |
| EPS022 | ε=.022 | Respuesta a mayor amplitud de semilla |

Antes de evolucionar, acreditar un origen por variante con cero pasos M2. Reconstruir con la preparación original, reproducir la semilla de la malla candidata, contrastar las seis funciones en el dominio y los modos comunes y comprobar la proyección, las dos energías, la carga y la fuerza C contra NumPy. En CAJA registrar por separado el exterior de CP04 omitido, el costo de remallado y frontera, y la deformación. Para las amplitudes, comprobar el escalado del cuadrupolo en las seis funciones. En ANGULAR comprobar la ortogonalidad de la cuadratura y que los modos nuevos inician en cero.

## Lectura y decisión registrada

- Aplicar a cada tramo las puertas físicas originales de ambas energías, carga, núcleo y amplificación. Conservar los recibos de recuperación con comprobación de hash, auditoría de cero pasos M2 y último cierre válido. Preservar cualquier fallo numérico o físico.
- Para PASO y TOL, calcular las cinco discrepancias del comparador original contra h=.03125 al mismo reloj. Conservar la puerta nominal del 2 %. En cada métrica y reloj, la suma de las dos discrepancias debe quedar por debajo o igual al 25 % del menor valor entre la discrepancia espacial publicada del par h=.0625/.03125 y el margen de la malla candidata al incluir la variación de referencia e interpolación. El presupuesto por corte está fijado en [REGISTRO.json](REGISTRO.json). Registrar los pasos aceptados de cada ejecución y del archivo base para interpretar cuándo la cota de paso cambia la secuencia.
- Si la estabilidad pasa, ejecutar los cuatro contrastes de robustez. Cuantificar la sensibilidad frente a la base al mismo h, un eje a la vez. Para L=6 producir la lectura común proyectada a L=4 y publicar por separado el contenido de los modos añadidos. Para ε publicar la discrepancia con la normalización del caso y la diferencia de las respuestas de χ por unidad de amplitud inicial. El 2 % del comparador sigue siendo la puerta de acuerdo numérico para una configuración común. Las diferencias entre configuraciones físicas se usan para delimitar el dominio respaldado.
- En (r<40), (20le r<40) y (40le r<220), medir la norma de χ y su velocidad normalizada por la masa del mediador para ℓ=2 y ℓ=4, con referencia a la norma inicial no radial de χ del caso en (r<40). Publicar las cinco métricas, las dos energías, la carga, la carga de núcleo y la amplificación para los cortes comunes, con lectura de τ120 a τ160.
- Emitir el dictamen de CP12 sobre el caso base con los recibos anteriores, la referencia independiente, el presupuesto temporal y los cuatro contrastes. El alcance de las variantes queda limitado al h registrado y al horizonte medido. Registrar los negativos y su efecto sobre la decisión. El expediente actualiza la vista de progreso de la rama de validación.

[Plan de contraste](../tercera_malla_20261116/SIGUIENTE_CONTRASTE.md) · [Tercera malla](../tercera_malla_20261116/RESULTADO.json) · [Galerkin](../referencia_galerkin_20261116/INFORME.md)
