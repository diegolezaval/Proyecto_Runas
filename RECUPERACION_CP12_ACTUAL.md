# CP12: por dónde continuar

**El transporte de P3 en τ11,2 ya está conservado en GitHub y fue descargado y auditado de forma independiente.** La repetición adicional τ9,6→τ11,2 terminó; no hay una nueva evolución en marcha. [Resultado, datos y comprobaciones](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/README.md).

| Referencia | Estado comprobado |
| --- | --- |
| Checkpoint aceptado | CP11 |
| CP12 / ensayo P3 | Abierto / sin validar |
| Última frontera completa aprobada del ensayo | τ8 |
| Último transporte recuperable en GitHub | τ11,2; contiene también la frontera completa τ8 |
| Cápsula vigente | 229880902 bytes; SHA256 `b0e2b2c1320358a41d2f8910e28fc17e65ec330e27ce8bdcf05e59e93f0fae8d` |
| Verificación de la descarga | Manifiesto y 293 cargas; 30 + 14 controles originales positivos; cero pasos de evolución |
| Repetición adicional | Terminada; autorización de un solo uso consumida |
| Siguiente frontera completa del ensayo | τ16, pendiente; exige todas las puertas originales |
| Transferencia histórica de archivos | 116/308; sigue incompleta |

## Recuperar los archivos

Abre [Respaldos CP12/P3](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027) y descarga **TRANSPORTE_TAU_000112_TRANSITO_INTENTO02_20261028.zip**, cuyo nombre completo empieza por `CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_`. La [guía de esta cápsula](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/README.md) identifica el adjunto exacto y sus hashes. Los ZIP `CONTROL…TAU9P6` son pruebas de conservación anteriores; **Source code** es la instantánea automática del repositorio.

La [aceptación pública](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/github/ACEPTACION.json) acredita la descarga independiente, el manifiesto y las auditorías originales. Se conserva también la recuperación de la copia temporal, sin nuevas subidas ni repeticiones físicas.

## Qué falta ahora

Preparar la continuación desde el estado exacto de τ11,2 hacia la frontera τ16 con el protocolo P3, su límite interno original y todos sus umbrales. Al llegar a una frontera completa deben pasar las cinco puertas espaciales originales, las demás comprobaciones y la conservación recuperable antes de cualquier tramo posterior. El transporte interno τ11,2 no es una frontera completa ni valida P3.

**No volver a lanzar τ9,6→τ11,2.** La [asignación exclusiva](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/ASIGNACION_EXCLUSIVA.json) se consumió. Esta recuperación no ejecutó el siguiente intervalo. El horizonte original τ160 sigue condicionado a las puertas de cada frontera; no es un resultado alcanzado.

## Historia conservada

El bloqueo anterior al abrir el editor de GitHub se debió a un límite de uso de la revisión automática. Al retomar, el acceso funcionó sin nuevo inicio de sesión. Los archivos temporales habían desaparecido, pero el ZIP guardado permitió recuperar todos sus bytes y terminar la publicación. [Incidente y alcance de los documentos reconstruidos](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/INCIDENTE_PUBLICACION_Y_RECUPERACION.json).

La primera repetición perdió sus bytes antes de una publicación observada; su [resultado histórico](checkpoints/CP12/p3_20261018/retoma_20261028/repeticion96_112/RESULTADO.json) y su [incidente](checkpoints/CP12/p3_20261018/retoma_20261028/INCIDENTE_SEGUNDA_PERDIDA_LOCAL.json) permanecen. Los escalares comparables del intento adicional coinciden con ese registro; no se afirma identidad binaria con archivos antiguos inaccesibles. Los intentos de conexión local y del ejecutor Haswell permanecen como antecedentes administrativos.

CP11 sigue aceptado. P2 conserva su negativo y no se reanuda. No se repiten CP10, CP12 original, F0…F5 ni P3 τ0→τ9,6; no se modificaron fuentes científicas ni puertas. La migración histórica 116/308 continúa pendiente.

[Registro canónico](checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json) · [Expediente histórico](checkpoints/CP12/p3_20261018/retoma_20261028/README.md) · [Guía del proyecto](https://github.com/diegolezaval/Proyecto_Runas/blob/main/GUIA_DEL_PROYECTO.md).

Para una visión del programa completo y el relevo entre chats: [panorama global y prioridades](informes/PANORAMA_GLOBAL_Y_PRIORIDADES_20261029.md) · [prompt de continuación](CONTINUAR_EN_CHAT_NUEVO.md). Son documentos de orientación; los protocolos y registros científicos mantienen su autoridad.

