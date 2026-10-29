# P3: cápsula de τ11,2 conservada y recuperada

La repetición adicional autorizada τ9,6→τ11,2 terminó. El ZIP se guardó antes de la interrupción y se recuperó después sin repetir el cálculo. La copia final en GitHub y su descarga independiente pasaron las auditorías originales. **CP11 sigue aceptado; CP12 está abierto, P3 sin validar y la última frontera completa aprobada del ensayo es τ8.**

## Lectura rápida

| Necesito | Abrir |
| --- | --- |
| Ver el resultado y sus límites | [Resultado de recuperación](RESULTADO_RECUPERACION.json) |
| Comprobar la descarga desde GitHub | [Aceptación original](github/ACEPTACION.json) y [auditoría completa](github/auditoria/RESULTADO.json) |
| Consultar las pruebas originales | [30 controles de τ8](github/auditoria/boundary8_stdout.json) y [14 del transporte τ11,2](github/auditoria/transport_stdout.json) |
| Comprobar la recuperación de la copia temporal | [Recibo](RECIBO_CAPSULA_TEMPORAL.json) y [auditoría](auditoria_recuperacion/RESULTADO.json) |
| Revisar todos los archivos contenidos | [Manifiesto de la cápsula](MANIFIESTO_CAPSULA.json) |
| Entender la interrupción y lo reconstruido | [Registro administrativo](INCIDENTE_PUBLICACION_Y_RECUPERACION.json) |
| Comparar los contadores con la repetición anterior | [Comparación y alcance](COMPARACION_METADATOS.json) |

## Descargar el estado correcto

En la [Release de respaldos](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027), el estado vigente es:

`CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_TRANSPORTE_TAU_000112_TRANSITO_INTENTO02_20261028.zip`

| Identidad | Valor |
| --- | --- |
| Adjunto de GitHub | 688783601 |
| Tamaño | 229880902 bytes |
| SHA256 del ZIP | `b0e2b2c1320358a41d2f8910e28fc17e65ec330e27ce8bdcf05e59e93f0fae8d` |
| SHA256 del transporte | `bc129cff71c7558cd0298873fdc816da14e01fdcb4728235b33666a1ecfcf3ac` |
| Contenido verificado | 293 cargas y su manifiesto; frontera completa τ8 y transporte interno τ11,2 |
| Auditorías de cada recuperación | 30 + 14 controles positivos; cero construcciones o pasos DOP853 |

Los archivos `CONTROL…TAU9P6` son pruebas administrativas de conservación de τ9,6. Las cápsulas originales y `SHA256SUMS` conservan su identidad; ese adjunto de hashes cubre únicamente los tres ZIP originales. El hash del nuevo τ11,2 se verifica mediante su manifiesto, sus metadatos y la aceptación enlazada arriba. Los archivos automáticos **Source code** de GitHub no sustituyen las cápsulas.

## Qué se pudo conservar y qué se reconstruyó

El ZIP contiene la instantánea exacta [CALCULO_TERMINADO_CONSERVACION_PENDIENTE.json](CALCULO_TERMINADO_CONSERVACION_PENDIENTE.json), tomada antes del guardado. Sus campos `passed=false` y `permanent_preservation_pending=true` describen ese momento. El estado administrativo posterior, con recuperación pública terminada, está en [RESULTADO_RECUPERACION.json](RESULTADO_RECUPERACION.json).

La interrupción eliminó los archivos temporales externos al ZIP, incluida la solicitud original de publicación y el informe final del lanzador. No se inventaron esos documentos. La [solicitud recuperada](SOLICITUD_RECUPERADA.json) se construyó a partir del ZIP intacto y de sus auditorías originales. En ella, `source_home` identifica la extracción recuperada: la comprobación posterior de fuente inalterada se refiere a esa extracción, cuyos bytes coinciden con todas las cargas guardadas. La aceptación la emitió el conservador original sin modificarlo.

Los siete escalares comparados de cada malla y los contadores de pasos y evaluaciones coinciden exactamente con el registro anterior. Los bytes antiguos no están disponibles; esta comparación no prueba identidad binaria entre ejecuciones.

## Por dónde continuar

La excepción adicional quedó consumida y su proceso terminó. **No repetir τ9,6→τ11,2 ni reconstruir su permiso de un solo uso.** Recuperar siempre el ZIP de τ11,2 ya conservado y ejecutar las auditorías originales sobre una extracción nueva antes de una continuación.

La siguiente frontera completa del ensayo es τ16. Su preparación debe respetar el estado interno guardado, el límite interno original τ16 y el protocolo P3. Allí deben pasar las cinco puertas espaciales originales, las demás auditorías de frontera y su conservación recuperable antes de continuar. Esta recuperación no ejecutó τ11,2→τ16, no modificó fuentes científicas ni umbrales y no valida P3.

P2 mantiene su negativo de τ80 y no se reanuda. No repetir CP10, CP12 original, F0…F5 ni P3 τ0→τ9,6. La migración histórica 116/308 sigue incompleta. Los antecedentes y los incidentes anteriores permanecen en sus rutas históricas.
