# Entrega 04 · Preparación radial, con puerta abierta

**Pregunta:** ¿un paquete cargado distinto del estado final puede asentarse conservando la contabilidad de ambos campos?

**Resultado:** sí en un ensayo radial condicionado de anchura 7.2 hasta t=1200; no en las ventanas cortas ensayadas. **E04/RES1 siguen PARCIALES**, con sus puertas completas no superadas. E00, E01 y C0 no se han reabierto ni repetido.

## Método y verificación

Ocho ejecuciones de la acción M2 común, con volúmenes finitos, Verlet, caja explícita y estados reiniciables. Se parte de una gaussiana cargada y mediador vestido cuya energía se cuenta; la fuente primaria no está derivada. Se comparan por separado tiempo y espacio en la ventana corta, y ambos en la larga. Se cotejan los inventarios finales con los estados guardados y se ajusta un equilibrio a igual carga.

La prolongación fina usa el estado a t=240 y no repite esos pasos. Se conserva un fallo de transferencia y un error de lanzamiento que hizo comenzar el caso largo grueso desde cero; ese resultado válido se etiqueta como control directo, sin atribuirle una reanudación inexistente. El capítulo 26 detalla la corrección de la guarda de frontera.

La auditoría final también recuperó una marca de progreso atrasada del control grueso después de verificar sus archivos completos. Se conservan la marca y el informe fallido; sólo se actualizó el metadato, sin repetir la evolución. La verificación final CP04 pasa sus diez controles.

## Evidencia cuantitativa y límites

| Magnitud | Resultado |
|---|---:|
| Deriva energética máxima muestreada | <1.92×10⁻⁷ |
| Deriva de carga máxima muestreada | <7.00×10⁻¹⁵ |
| Reducción de deriva al dividir Δt por dos | 4.00001 |
| Diferencia larga de E,Q medios del núcleo | <9.79×10⁻⁵ relativa |
| Carga tardía retenida, caso largo fino | 90.132 % |
| Máxima desviación tardía del perfil fino | 1.124 % |
| Exceso sobre equilibrio de la misma malla | 0.15818; diferencia entre mallas 0.611 % |

El éxito numérico no demuestra estabilidad 3D ni retención indefinida. El exceso energético no es energía útil demostrada. Se preservan los rechazos de asentamiento a t=240, la sensibilidad a la anchura y los diagnósticos de energía/carga inicialmente desajustados.

## Puerta y continuación

Se supera el subensayo radial de asentamiento, no las puertas E04/RES1. E02, E03 y RES0 permanecen parciales. No se habilita E08, no hay ninguna primordial completa y no se activa M3.

Se añaden los scripts de evolución/reanudación, diagnóstico, equilibrio discreto y figura, datos crudos, ocho estados completos, capítulo 26, informe y registros actualizados. Todos los fallos anteriores y las fuentes originales siguen incluidos.

**Siguiente trabajo:** validar el candidato fuera de la simetría radial y su región de preparación; estudiar una fuente y contactos con recursos explícitos. La investigación analítica C7 iniciada queda en notas EN_PROGRESO, sin excluir todavía ninguna clase adicional. El último estado fino válido es `validacion/P06/preparacion/w7.20_h0.100_dt0.0020_R1300_T1200_estado.npz`. No volver a ejecutar las ocho evoluciones terminadas para reanudar.
