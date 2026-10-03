# Entrega 02 · Acción, convenciones y parámetros

**Pregunta:** ¿acción, unidades, corrientes y cinco coordenadas independientes definen una sola teoría sin ambigüedad?

**Puerta E01: COMPLETADA en el sector clásico declarado.** Desbloquea E02/E03, C0 y la investigación RES0. No completa la estabilidad ni ningún dispositivo.

## Derivación y cambios

Se corrigen en 20.3 los signos de X, j y T para la signatura (−+++), manteniendo Q positivo para Φ=f exp(+iωt). Se documentan flujos, dimensiones, ensembles y condiciones de borde. Se auditan Cauchy, coercividad y causalidad y se da una región suficiente general mediante el mínimo exacto de U(s)/s. Las hipótesis y límites están en el capítulo 23.

La fuente de las cinco constantes es theta_comun.json. ScalarModel y soluciones_m2.py permiten variar cada una por separado. Los scripts históricos conservan el benchmark y rechazan su modificación, porque sus fórmulas especializadas no representan todo el espacio fundamental. Las unidades de comparación son explícitas y no son nuevos acoplamientos.

## Pruebas y simulaciones

Se contrastan derivadas de la acción, Jacobianos por paso complejo, equivalencia dimensional, Noether local y solución mediante la interfaz general. Los errores de identidades son menores que 3×10⁻¹⁵ relativos; la solución coincide con energía/carga de referencia a aproximadamente 1.5×10⁻¹⁴. Las cinco variaciones independientes alteran la acción sin cambiar las otras cuatro coordenadas.

Se ejecutó nuevamente el programa original. La primera pasada llegó a la comprobación SVG y detectó una figura truncada; se conservó el informe fallido, se regeneró la figura y la pasada final completa superó los 19 pasos. Los 18 CSV físicos siguen siendo idénticos a 4.1. No se relajó tolerancia alguna ni se reabrió la reproducción física E00 por ese fallo editorial.

## Evidencia y límites

Demostración analítica condicionada para la coherencia clásica y pruebas numéricas de equivalencia. Sin calibración experimental, dominio cuántico, contactos ni dispositivo. No se cambia M2 por M3. La igualdad entre simulaciones no prueba la teoría en la naturaleza.

## Archivos modificados

Theta y convenciones; m2_comun.py y complecion_escalar.py; nuevos modelo_m2.py, soluciones_m2.py e identidades_m2.py; capítulo 20 corregido y capítulo 23 añadido; generación del integrado, registros de regresión, continuidad y enmiendas. Fuentes anteriores íntegramente archivadas.

**Siguiente acción:** C0 y cribado de arrollamiento/capas; carta E02; continuación y estabilidad condicionada para RES0. Los resultados preliminares de campañas posteriores, si están presentes, no se cuentan como etapas cerradas en CP02.
