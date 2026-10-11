# CP12: reinicio τ=24 íntegro y actividad original desconocida

La revisión del 11 de octubre de 2026 no encontró una cápsula completa posterior a τ=24. La actividad del ejecutor que inició 24→32 no puede determinarse desde el entorno disponible. Se bloquea un segundo trabajador; no se declara perdido, terminado ni científicamente fallido ese segmento. Main sigue en CP11 y el PR #2 abierto y en borrador.

El registro persistente, leído en su versión actual 13, conserva una observación ACTIVE del 11 de octubre a las 17:25:20 UTC. El entorno revisado a las 21:16:14 UTC tiene una identidad de ejecutor distinta y no muestra los procesos registrados. Se comparó la identidad con el mismo método original, sin publicar datos del host. Esta ausencia local y el latido antiguo no prueban inactividad en el ejecutor registrado. Las sesiones antiguas tampoco son accesibles desde este entorno. No se sustituye el registro original por una observación de otro host. Los detalles operativos completos se conservan privadamente.

La búsqueda de archivos CP12 permanentes, los ZIP/comprobantes locales y los artefactos del flujo 38155352563 no halló τ32…τ160 ni interpretación final. El HEAD del PR era 43b51cc419897783f3111586b16dfc76875f1c61. Los jobs remotos están terminados; los artefactos denominados frontera32 son diagnósticos de rechazo de hardware, no estados físicos. Se mantienen agotadas las cuatro asignaciones autorizadas para τ32. No se reejecutó Actions, no se editó activacion.json y no se inició M2.

## Recuperación independiente sin evolución

Se recuperó nuevamente el ZIP permanente τ24 por su identidad y se comprobó con verify_download() original en una extracción nueva. Pasan los 329 archivos, configuración, recibo, catorce fuentes, seis controles, datos iniciales/prefijo de observaciones CP10 array_equal, balances, identidades algebraicas, simetría, Parseval, órdenes pasivos y recarga original sin avance. El estado no cambió.

| Evidencia | Valor |
|---|---|
| ZIP completo | 75 252 550 bytes; SHA256 77db2bc9b8c76cd7779c565ca2d6d8baf90aaee504ac52abbe27356a610e8c52 |
| NPZ | SHA256 508f32f167abd6211b330d707172612a47fec1f2701577b1a9939d8390fbc529 |
| Recibo | SHA256 1e75549f9a67d04edef4eb92f49d3ba3de910292068b5041180d8ec04ab42437 |
| Configuración | SHA256 148dfb982ce59ff5e9e7696749f58c77584c96c2833ca5fb4bd03122af5e5541 |
| Por malla | 61 observaciones, 4435 pasos aceptados y 53838 evaluaciones |
| Cierre máximo bruto/acoplado | 5.80276454319202e−7 / 5.798568786415206e−7; límite original 1e−3 |

Se reutiliza la auditoría de contadores capturada en la cápsula: pasos y máximos E/Q coinciden exactamente con los logs CP10; nfev intermedio cumple la contabilidad original. No hay un antecedente CP10 exacto de nfev en τ24: la comparación final exacta en τ160 sigue obligatoria. Una solicitud redundante de ejecutar el auditor rechazó la escritura porque el comprobante ya existe; se conserva ese rechazo y no se repitió la auditoría ni se alteró el estado.

## Protección del monitor

La función anterior del monitor podía informar INACTIVE_OBSERVED_ON_ORIGINAL_EXECUTOR después de consultar procesos en otro boot. Se exige ahora --expected-boot-sha256 tomado del registro original. Un boot distinto produce UNKNOWN_ACTIVITY, active=null y ninguna identidad de coordinador original certificada, incluso si un PID coincide. El control administrativo prerregistrado reproduce el defecto anterior y pasa los siete casos de consulta completa/incompleta, PID reutilizado, coordinador activo y procesos huérfanos. Son pruebas con procesos sintéticos, cero pasos M2 y ninguna publicación de actividad; no certifican una frontera ni la inactividad real.

La corrección sólo afecta a la exclusión de trabajadores. El coordinador, M2, Θ, solver, tolerancias, observadores, ambas mallas y el umbral del 2 % no cambiaron. El registro histórico conserva el hash del monitor que realmente emitió su última observación; no se atribuye esta versión nueva a aquel proceso. Un primer control se detuvo antes de consultar procesos porque una copia textual tenía un LF final adicional: su diagnóstico y restauración del SHA original se conservan.

## Siguiente paso permitido

Hace falta una observación fiable de inactividad en el ejecutor original, o un comprobante autoritativo de su terminación. Después debe diagnosticarse el motivo y buscarse toda cápsula posterior antes de retomar. Un fallo científico no habilita reintentos; una cápsula completa ya guardada debe recuperarse y certificarse sin repetir su segmento. Si la actividad sigue sin poder determinarse, se conserva la exclusión del segundo trabajador y se supervisan los comprobantes permanentes sin integrar M2. No se interpreta un timeout o un lock libre de otro host como autorización para duplicar.

La fuente canónica y su vista generada expresan esta incertidumbre y τ24; se elimina la indicación obsoleta de reanudar desde τ8. Las 33 etapas, evidencias CP11 y puertas científicas permanecen iguales. La vista y el índice se generan sobre los bytes publicados del corpus científico, cuyo binario CP12 sigue en τ0, sin mezclarlo con el recibo de τ24 recuperado.

El defecto local r²Y₂m ya documentado sigue siendo una pista matemática. No identifica por sí solo el mecanismo dominante de χ. Continúan pendientes τ160, reproducción final exacta, Duhamel, cancelaciones, aportes operador/fuente y realimentación, y las puertas causales de las tres ventanas. No se ensayó una corrección y CP12 no está cerrado.

Diagnóstico: [actividad_incierta_20261011.json](../trazabilidad/CP12_ejecucion_durable/actividad_incierta_20261011.json). Comprobantes: [supervisión y recuperación](../trazabilidad/CP12_ejecucion_durable/supervision_20261011_2105/recuperacion_tau0024_original.json), [control administrativo](../trazabilidad/CP12_ejecucion_durable/supervision_20261011_2105/control_monitor_resultados.json). Antecedentes: [decisión de ejecutor](DECISION_EJECUTOR_CP12_20261011.md), [protocolo](PROTOCOLO_CP12_CAUSA_CHI.md), [análisis radial](ANALISIS_ORIGEN_RADIAL_CP12.md).

La revisión automática rechazó divulgar metadatos internos del ejecutor en el repositorio público. Los comprobantes públicos omiten rutas internas, identificadores privados, procesos y datos de identidad del host; el respaldo privado conserva las observaciones completas. Esta limitación de publicación no altera las verificaciones científicas ni certifica inactividad.
