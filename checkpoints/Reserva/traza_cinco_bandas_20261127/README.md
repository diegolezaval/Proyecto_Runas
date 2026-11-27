# Qué bandas alimentan la traza de r40 en el prefijo con realimentación

Se conserva la continuación a carga fija de la referencia corregida de la cargada. La comparación anterior juntaba en una sola norma de fuerza toda la región r<60 al evaluar la traza del centro 39,9875. Se han recuperado las cinco normas de fuerza física **en los candidatos que realmente se usaron**. El cálculo reproduce exactamente el JSON que recoge el cierre del volumen hasta s=13,875 y el primer rechazo en s=14.

[Protocolo](PROTOCOLO.md) · [Cálculo](traza.py) · [Resultados por intervalo](resultado.json) · [Comparación volumétrica](../nucleo_carga_fija_20261127/README.md)

Para cada una de las seis semillas adjuntas se conservó la misma malla FV, los mismos coeficientes de Taylor de orden 48 con paso de 1/32 y el mismo resto formal de truncación y de corte radial en r104. Se toma la norma de cada coeficiente en 0–10, 10–40, 40–60, 60–160 y 160–256 antes de sumar los órdenes. El resto no localizado se añade a cada banda, incluida la exterior al corte. Este procedimiento conserva la cobertura entre muestras y la cola discreta. Los resultados se evalúan en doble precisión.

Para cada par de intervalos de fuente y observación se usan los dos retardos posibles. Dentro de r<60 se compara la suma de los tres productos (norma del núcleo por norma de fuerza) con el producto previo para el grupo completo y se conserva el menor. Las otras dos bandas mantienen presupuestos independientes. En el resultado se publican las cinco contribuciones antes de tomar el mínimo, el coste lineal y la cota combinada; las contribuciones detalladas pueden sumar más que la cota combinada. Se verificó en todos los intervalos que la agrupación previa recupera ambas trazas, incluida la fila rechazada. La fuerza prescrita, el defecto de velocidad y el defecto cinemático con su aportación directa a z′ conservan sus valores originales.

**Resultado en s=0…13,875.** La cota de la integral simple de |z′| baja de 1,009e−5 a **1,930e−6**. La contribución con peso referido a 40 baja de 3,930e−5 a **7,613e−6**. El cribado provisional de 3,96e−6 sigue sin acreditarse con el presupuesto propagado. La banda 10–40 aporta hasta 7,568e−6 antes del mínimo por retardo. En cambio, la banda r<10 aporta hasta 1,160e−14 con ese mismo peso. El término lineal del prefijo aporta hasta 4,289e−8. La traza terminal de posición queda en ≤3,185e−8. El desagregado reduce una sobreestimación por distancia; no implica cruce en r60 ni entrega útil.

Siguiente comprobación del mismo contacto: en el núcleo a carga fija probar las columnas del jacobiano físico sobre κq y uβ después de aplicar W. Separar el trabajo perpendicular en D y la proyección en q̇. Comparar a igual estado entrante en s=14 y repetir desde cero si mejora. Mantener las fuentes físicas del adjunto independientes de la nueva comparación reducida.

**Resumen para el Dot principal.** Diego, al separar las fuerzas en cinco bandas, la aportación propagada de la traza hasta s=13,875 baja a 7,613e−6. Domina 10–40; r<10 sigue limitando el cierre volumétrico. El presupuesto supera aún el cribado provisional. [Resultado y controles](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/traza_cinco_bandas_20261127)

Para reproducir desde este directorio ejecutar `OPENBLAS_NUM_THREADS=1 python3 traza.py`.
