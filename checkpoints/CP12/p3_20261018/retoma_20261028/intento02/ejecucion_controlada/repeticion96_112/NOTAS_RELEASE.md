**CP11 aceptado. CP12 abierto y P3 sin validar. Último transporte conservado y recuperado en GitHub: τ11,2. Última frontera completa aprobada del ensayo: τ8.**

La repetición adicional autorizada τ9,6→τ11,2 terminó. La cápsula completa fue recuperada de su copia temporal, adjuntada aquí y descargada y auditada de forma independiente, sin repetir el cálculo. Consulta primero el [estado vigente](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/RECUPERACION_CP12_ACTUAL.md) y el [registro canónico](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json). La autorización adicional quedó consumida al comenzar M2; no iniciar otra repetición desde τ9,6.

### Estado vigente para continuar: τ11,2

Descarga **CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_TRANSPORTE_TAU_000112_TRANSITO_INTENTO02_20261028.zip**. Adjunto **688783601**, **229880902 bytes**. SHA256:

`b0e2b2c1320358a41d2f8910e28fc17e65ec330e27ce8bdcf05e59e93f0fae8d`

Su descarga pública pasó la cobertura exacta del manifiesto y las **293 cargas**, más los **30 controles originales de τ8 y 14 del transporte τ11,2**, con cero construcciones o pasos DOP853 durante la recuperación. [Guía de la cápsula y alcance](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/README.md) · [Aceptación de la descarga](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/github/ACEPTACION.json).

Este transporte contiene también la frontera completa τ8. **τ11,2 es un transporte interno; no valida P3 ni cierra CP12.** La siguiente frontera completa es τ16 y sigue pendiente de todas las puertas originales. No se lanzó el siguiente tramo. La autorización adicional está consumida; no volver a ejecutar τ9,6→τ11,2.

### Cápsulas originales

En **Assets**, identifica los archivos por su nombre completo:

| Archivo | Bytes | Uso |
| --- | ---: | --- |
| P3 · TRANSPORTE_TAU_000096.zip | 229821160 | Estado interno τ9,6; contiene también la frontera cerrada τ8 |
| CP12_RI · tau0160.zip | 84575117 | Antecedente original; CP12 sigue abierto |
| CANDIDATO_MIXTO · DIAGNOSTICO_DISCRIMINANTE_TAU0080_20261018.zip | 232883013 | Negativo de P2, conservado; P2 no se reanuda |

Los originales se conservan sin recomprimir ni modificar. El adjunto **SHA256SUMS** cubre estos tres ZIP. [Guía de recuperación](https://github.com/diegolezaval/Proyecto_Runas/blob/respaldo/cp12-p3-20261027/respaldos/CP12_20261027/LEEME.md) · [Verificación de integridad](https://github.com/diegolezaval/Proyecto_Runas/blob/respaldo/cp12-p3-20261027/respaldos/CP12_20261027/verificacion_descarga.json).

### Conservación comprobada antes del nuevo tramo

La ruta actual guarda y recupera una cápsula temporal desde el propio proceso y después conserva el mismo ZIP en esta Release. El control03 completó ambas fases: **230901677 bytes**, con descarga independiente, manifiesto, todos los hashes y 30+14 controles originales sin construcciones o pasos DOP853. [Aceptación combinada](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/ACEPTACION_CAPACIDAD_COMBINADA.json).

Los tres controles de conservación son evidencia administrativa del mismo transporte τ9,6, con relleno de capacidad identificado:

| Control | Bytes |
| --- | ---: |
| CONTROL_RUTA_RELEASE_TAU9P6_20261028 | 230902380 |
| CONTROL_TRANSITO_INTENTO02_TAU9P6_20261028 | 230900851 |
| CONTROL03_TRANSITO_INTENTO02_TAU9P6_20261028 | 230901677 |

Estos controles no representan avance físico ni una frontera nueva. La copia pública del control01 también pasó la recuperación completa; los fallos de interpretación administrativa y sus correcciones permanecen documentados.

### Historia y reglas de continuación

La primera repetición excepcional terminó con auditorías locales positivas, pero sus bytes desaparecieron antes de una publicación observada. Se conservan sus [resultados](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/retoma_20261028/repeticion96_112/RESULTADO.json) y el [incidente](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/retoma_20261028/INCIDENTE_SEGUNDA_PERDIDA_LOCAL.json). Su lanzador sigue bloqueado.

La autorización adicional pertenece al [intento02](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/PRERREGISTRO.md), con restauración exacta auditada y asignación exclusiva. El proceso se detuvo en reloj observador τ11,2 y completó el guardado y la recuperación; la publicación y auditoría final en GitHub también están comprobadas. La continuación debe respetar el protocolo y todas las puertas originales. Un hash, un latido o una reserva no reconstruyen un estado.

El tag mantiene la referencia científica original **be4bf493517e3f6f51989fa8fc8d6c6ea8cb8cb2**. **Source code** son instantáneas automáticas del repositorio; no sustituyen las cápsulas. La transferencia histórica **116/308** continúa incompleta y se conserva. No se relaja ninguna puerta científica.


