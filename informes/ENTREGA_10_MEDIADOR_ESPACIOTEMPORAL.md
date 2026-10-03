# CP10 · Mediador: control temporal y refinamiento espacial

CP10 continúa la pregunta científica pendiente de CP08 sobre la base arquitectónica CP09. No reorganiza el corpus ni cambia la acción M2, Θ, la preparación fuente, las puertas, la hoja de ruta original o los resultados negativos. Las etapas E00/E01/C0 permanecen cerradas; E03/E04/RES0/RES1 conservan sus contratos generales.

**Decisión finita: REFINAMIENTO_PENDIENTE.** Dos evoluciones nuevas terminadas, cuatro recibos cerrados y ninguna etapa general cerrada. Los valores se leen en el resumen generado y en el único resultado numérico registrado.

## Pregunta y decisiones previas

El refinamiento anterior dejó sin superar la comparación del mediador real, aunque los balances y los observables de Φ fueran satisfactorios. El control temporal histórico estaba realizado en una malla gruesa. Por eso no bastaba para atribuir a la discretización espacial la diferencia de la malla fina.

Antes de nuevas evoluciones se guardó `datos/ensayo_mediador_CP10.json`, se implementó la procedencia y se contrastó la recuperación de métricas históricas. El protocolo separa dos controles: reducir la tolerancia temporal en h=.125 y comparar h=.125/.0625 con la misma tolerancia estricta. No ajusta la fase de χ, no cambia el límite del 2 % y no utiliza el refinamiento como prueba automática de convergencia continua.

El diagnóstico de datos guardados descompone la diferencia cuadrática por bandas radiales y armónicos. La discrepancia de χ se concentra principalmente entre r=5 y r=20; la rotación global descriptiva apenas la reduce. La transformada seno de rχ identifica componentes cortas sobre un núcleo finito, pero no diagonaliza el operador radial acoplado ni mide por sí sola energía física. La dispersión libre cartesiana ω_h²=M²+4 sin²(kh/2)/h² sólo ilustra cómo una frecuencia espacial mal resuelta puede acumular fase durante una ventana larga. Ninguno de estos diagnósticos certifica la causa del error observado.

## Método y estado inicial

Las dos evoluciones nuevas utilizan el integrador DOP853 y las fuerzas completas, sin modificar los cinco archivos numéricos de CP09. En las etiquetas, h representa Δr=config.dx, el paso radial; el parámetro h del potencial M2 se mantiene fijo. Ambas conservan L=4 con todos los m, R=220, ε=.02 y la ventana τ≤160; rtol=1e-10, atol=1e-12 y paso máximo .02. Su diferencia es exclusivamente la malla radial. Las fuerzas del potencial C se compararon con NumPy sobre el estado inicial y cuatro perturbaciones de auditoría en cada malla, antes del piloto.

El origen es el estado completo de CP04 en t=1200, guardado en `validacion/P06/preparacion/w7.20_h0.100_dt0.0020_R1300_T1200_estado.npz`. Se transfieren posiciones y velocidades desde ese archivo y se añade la misma deformación cuadrupolar registrada. No se regresa a una gaussiana ni se repite la preparación. Interpolar una fuente h=.1 a una malla .0625 no certifica su resolución física; el alcance de la fuente se conserva explícitamente.

La comparación utiliza el núcleo r<40, pesos de volúmenes finitos e interpolación cúbica hacia la malla más fina, con la definición de CP08. La norma de espacio de fases incluye campo y velocidad dividida por su masa. Únicamente se elimina la fase U(1) de Φ. La puerta comprueba cinco métricas y conserva los criterios de energía, carga, retención del núcleo y amplificación.

Los controles históricos de caja, truncación angular y perturbaciones mantienen sus propias resoluciones. No se presentan como una prueba conjunta de los nuevos valores de h, tolerancia y L. Las mallas gruesas y los integradores que fallaron siguen disponibles como resultados negativos.

## Procedencia y recuperación

El ID completo de cada ejecución depende de configuración exacta, modelo, parámetros, entradas, código local y entorno. Antes del proceso se guardan `procedencia.json`, `configuration.json` y copias de código/Θ/protocolo. Los estados grandes de origen se referencian por ruta y hash dentro del mismo checkpoint. Las salidas tienen hashes al cerrar el segmento; un recibo activo no certifica una salida final.

El campo BLAS_threads del recibo del diagnóstico previo declara la política prevista, pero no capturó una observación del número de hilos: se añadió una aclaración explícita y se conservó el recibo anterior sin alterar su identidad o salida científica. Ambas evoluciones sí aplican threadpool_limits(1) en su trabajador. La comparación final se lanzó con las variables de hilos fijadas. No se atribuye a cálculos antiguos una observación de entorno que no se registró.

Los pilotos concluyeron en τ=8 y se continuaron desde sus propios NPZ. La sesión anterior se interrumpió sin cerrar el segundo segmento. Al retomar se comprobó que no existía otro escritor, que la identidad y la configuración seguían intactas y que los arrays y tiempos guardados eran válidos. El control temporal se recuperó desde τ=56 y el espacial desde τ=24. Se conservaron el registro anterior y los hashes de esos estados. El instante exacto de terminación del proceso anterior es desconocido; los recibos distinguen la detección posterior de esa terminación.

No se repitieron E00/E01/C0, la preparación CP04, las ocho evoluciones Verlet de CP06 ni las cuatro DOP853 cerradas en CP07–CP08. Los reinicios recuperan el último estado durable: los pasos posteriores no guardados de una sesión interrumpida no se dan por recuperados.

## Resultados y alcance

Las cifras, balances, segmentos, estados y distribuciones del error se publican en [RESUMEN_NUMERICO_CP10.md](RESUMEN_NUMERICO_CP10.md), generado desde el resultado vigente señalado por `datos/registro_calculos.json`. El JSON final es la autoridad numérica, el CSV y el SVG son vistas derivadas y el registro decide qué resultado usar. El resultado CP08 permanece en su ruta y con sus bytes originales. El resumen se regenera con generar_resumen_CP10.py y se comprueba sin escribir con --comprobar; no constituye una segunda autoridad numérica.

El control temporal fino supera las cinco métricas. En la comparación espacial, las tres métricas de Φ superan la puerta, mientras que las dos de χ la incumplen. Los balances y la retención de ambas evoluciones son satisfactorios. La discrepancia espacial de χ no disminuye en este par de mallas hasta un nivel aceptable: no hay base para extrapolar una ley asintótica de convergencia o certificar el continuo. La comparación temporal reduce considerablemente la plausibilidad de que el cambio de tolerancia temporal explique esa diferencia, dentro de las configuraciones examinadas; no certifica una causa única. La nueva distribución radial del error se distingue del diagnóstico previo en el resumen generado.

E03/E04/RES0/RES1 continúan PARCIALES incluso si una comparación finita supera su puerta. No se demuestra estabilidad orbital, convergencia continua, cobertura de perturbaciones arbitrarias, fuente primaria, apagado, retroacción, ciclo o dispositivo. No se interpreta una discrepancia de discretización como inestabilidad física.

## Conservación y continuidad

Las fuentes originales afectadas se conservan en `trazabilidad/CP09_entrada/`; sus hashes cubren los 833 archivos de entrada. Se verifican por separado la conservación de resultados, figuras, fallos y hoja original; las ecuaciones, Θ y el integrador; los cierres de E00/E01/C0; y las puertas/dependencias de las 33 etapas. El índice de trazabilidad se genera desde las autoridades y los recibos, con enlaces en las dos direcciones. Las copias de código capturadas son evidencia de ejecución y no deben ejecutarse desde su carpeta como un segundo proyecto.

No se mueve, renombra ni elimina ningún archivo previo. El mapa de modificaciones registra archivos actualizados y su copia original; la tabla de migración indica cero traslados. Las vistas se regeneran desde sus fuentes. Las comprobaciones de datos guardados y las regresiones estructurales no integran de nuevo las campañas.

## Siguiente estado científico pendiente

Diagnosticar el operador radial y las componentes cortas de chi sobre los estados CP10 guardados; prerregistrar el próximo control espacial o una discretización contrastada, sin relajar la puerta ni repetir las catorce evoluciones cerradas.

El origen radial CP04 y los dos estados terminales CP10 siguen disponibles. Prolongar la ventana o cambiar la caja, la perturbación, el modelo o el trabajador requiere otro protocolo; el estado truncado R=220 no representa por sí solo el exterior evolucionado.

## Comprobaciones realizadas y preparación posterior

- [Verificación científica CP10](../validacion/arquitectura/ciencia_CP10.json): cuatro recibos cerrados, estados finitos hasta τ=160, campos y velocidades iniciales exactamente transferidos, reinicios reales, umbrales originales y conservación histórica. La puerta negativa se comprueba como resultado válido, no como fallo de la infraestructura.
- [Regresión estructural](../validacion/arquitectura/regresion_CP10.json): suite aislada sobre datos guardados, rechazo de escritores simultáneos/configuración distinta, protección de temporales y enlaces externos, reutilización de estados cerrados y recuperación completa CP08.
- [Trazabilidad en ambas direcciones](../validacion/arquitectura/trazabilidad_CP10.json): afirmación → ecuaciones/Θ/código/configuración/estados/figura/puerta; estados → ejecución que los produjo y comparación que los consume. El índice diferencia hashes previos de ejecución de hashes de la instantánea actual.
- [Regeneración](../validacion/arquitectura/regeneracion_vistas_CP10.json): el resultado JSON, CSV y SVG se regeneran byte a byte sin nuevos pasos de integración. La figura se revisó visualmente; «fase» designa campo y velocidad, no una corrección de la fase real de χ.
- [Recuperación CP09](../validacion/arquitectura/recuperacion_CP09.json): sus 833 archivos originales se recuperan mediante bytes vigentes e instantáneas, sin el ZIP externo. El ZIP reconstruido coincide también byte a byte con la entrada.
- [Procedencia futura](../validacion/arquitectura/adaptador_procedencia_futura.json): comprobaciones aisladas de registro previo, hilos, identidad, bloqueo, estados inválidos y recuperación/reutilización; no campañas nuevas. El adaptador sigue limitado a su contrato M2.
- [Preparación Git](../validacion/arquitectura/preparacion_git_CP10.json): índice/checkout temporal conserva todos los bytes incluso con autocrlf; incluye NPZ, CSV, JSON, SVG, logs y fuente histórica. No se inicializa Git en el proyecto ni se publica.

[MIGRACION_GITHUB.md](../MIGRACION_GITHUB.md) recoge la distribución propuesta y las decisiones que corresponden a una migración posterior. Se conservan las reglas de exclusión y preservación de bytes de CP09. El README actualizado es un puente generado al LEEME canónico. No se instala LFS ni se retiran estados por su tamaño.

El [mapa de cambios](../trazabilidad/CP10_cambios.json) conserva la relación entre cada fuente actualizada y su original CP09: **cero archivos movidos, renombrados o eliminados**. Los nuevos archivos son protocolo, ejecuciones, herramientas compatibles, evidencia, vistas y comprobaciones. El manifiesto definitivo lo genera el empaquetador; la comprobación externa de entrega identifica el ZIP y la reconstrucción en una carpeta limpia.

Durante el cierre documental, la regresión detectó que la versión original del README actualizado aún no estaba incorporada a la instantánea. Se recuperó desde la entrada CP09 con su hash exacto y se completó el mapa de cambios. El [recibo de ese intento documental](../validacion/arquitectura/regresion_CP10_intento_documental.json) se conserva; no hubo pérdida o modificación de evidencia numérica.
