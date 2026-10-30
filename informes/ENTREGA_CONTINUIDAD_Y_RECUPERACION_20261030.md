# Continuidad reconciliada y recuperación de P3 τ11,2

Entrega administrativa del 30 de octubre de 2026. **CP11 aceptado, CP12
abierto, P3 sin validar.** Última frontera completa positiva τ8; transporte
interno vigente τ11,2; próxima frontera τ16. Cero pasos nuevos de M2.

## Pregunta y protocolo

¿Puede el nuevo ejecutor disponer de una continuidad coherente y una entrega
global recuperable, y preparar la continuación exacta sin repetir tramos?
Se aplica el [prerregistro](../checkpoints/CP12/p3_20261018/continuidad_20261030/PRERREGISTRO.md).
La base P3 comprobada es `4a88af2dbdcdbdfbd7983fc3d6ae44a0776cdfbf`;
main sigue en `90e8fcffbba65629a1628f435d3c3240832fe9c4`.

## Interrupción anterior y rescate

El día anterior se preparó una entrega administrativa y un commit local
`6b59489f459cd77c0015ec0d445cbdf326c59031`, pero el intento Git no obtuvo
credenciales y la publicación por conector se interrumpió por límite de uso
de la revisión automática. No se actualizó la rama ni se adjuntó el paquete
global. El entorno temporal desapareció entre sesiones; su causa no está
determinada. No se lanzó un trabajador físico ni se consumió una autorización
nueva. No se presume terminación de ejecutores históricos inaccesibles.

Se recuperaron **doce blobs exactos** y se anclaron en el commit
[`7a1a86e`](https://github.com/diegolezaval/Proyecto_Runas/commit/7a1a86eb5199cc6e82de657f5fed3069fd8e08a7),
rama `rescate/continuidad-20261029-20261030`. El [inventario del rescate](../trazabilidad/continuidad_20261030/rescate/INVENTARIO_RESCATE.json)
declara cada identidad. Incluye los resultados de regresión históricos, el
manifiesto preparado y algunas vistas; no recupera la entrega completa.
Las copias se conservan como historia, no como fuentes operativas actuales.

El ZIP global perdido había sido observado con 304952307 bytes y SHA256
`0c95db9132425796ac5273bc43718c1e5754c31f4cf61d09332719eaea07e35e`.
No se dispone de sus bytes y no se afirma haberlo recuperado ni regenerado
idénticamente. La entrega actual tiene su propia identidad y verificaciones.

## Recuperación científica sin evolución

Se descargó otra vez el adjunto **688783601** de la Release experimental
existente, para recuperar el estado íntegro en el entorno nuevo. Se aplicó
`retoma_20261028/auditar_recuperacion.py` original sin modificaciones.

| Comprobación | Resultado |
|---|---|
| Tamaño del ZIP | 229880902 bytes |
| SHA256 del ZIP | `b0e2b2c1320358a41d2f8910e28fc17e65ec330e27ce8bdcf05e59e93f0fae8d` |
| Cobertura | 293 cargas más manifiesto, exacta |
| Frontera τ8 | 30 controles originales positivos |
| Transporte τ11,2 | 14 controles originales positivos |
| Construcciones / pasos DOP853 | 0 / 0 |
| SHA256 del transporte | `bc129cff71c7558cd0298873fdc816da14e01fdcb4728235b33666a1ecfcf3ac` |

[Auditoría completa](../checkpoints/CP12/p3_20261018/continuidad_20261030/auditoria_recuperacion/RESULTADO.json).
Las cargas se comprobaron antes y después y el archivo fuente permaneció
idéntico. El entorno original, fuentes, implementación DOP853, arquitectura
BLAS sin forzar y un hilo pasaron sus controles. Se conserva toda la memoria
física y pasiva; el límite interno sigue siendo 16. Esta restauración no es
una repetición τ9,6→τ11,2 ni certifica una frontera nueva.

## Integridad del árbol y reparación administrativa

El árbol de entrada P3 tiene 2556 archivos y 413021956 bytes lógicos. El
manifiesto histórico tiene 1384 entradas: ninguna carga ausente, seis hashes
desactualizados y 1171 rutas versionadas fuera de cobertura. El [inventario
íntegro](../trazabilidad/continuidad_20261030/INVENTARIO_ENTRADA_AISLADA.json)
contrasta los blobs y las copias aisladas. Se conservan el [manifiesto y
fuentes anteriores](../trazabilidad/continuidad_20261030/entrada/ORIGEN.json).

Se sincronizan progreso y registro de cálculos desde la evidencia reciente;
se retira la instrucción activa de piloto 0→8 y la opción errónea de reanudar
el CP12 original desde τ8. Las observaciones anteriores permanecen en la
instantánea y la historia. Las 33 etapas mantienen exactamente sus registros.

El empaquetador excluye también el archivo `.git` de los worktrees. Las dos
expresiones matemáticas históricas `a[j](...)` que parecían enlaces se
identifican por expresiones exactas y hash completo del documento; no se
alteran esos bytes ni se omiten carpetas del control. Se restauran tres
antecedentes de herramientas con bytes del commit
`47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81`, según sus manifiestos originales.
Las vistas se generan desde las fuentes JSON. No se cambian hashes a mano.

## Puertas, alcance y siguiente acción

La verificación editorial, la regresión aislada y la recuperación del paquete
global se registran en este expediente al finalizar cada comprobación. Un
respaldo correcto acredita integridad, no convergencia ni cierre de CP12.

Preparar un ejecutor nuevo desde τ11,2 y comprobar restauración exacta y
conservación desde el proceso real antes de M2. Después sólo se habilita τ16
bajo las fuentes, observadores, mallas, tolerancias y puertas originales.
Cada frontera se recupera y audita antes de avanzar; cualquier negativo se
conserva y suspende esa versión. No se reutiliza el lanzador consumido.

P2 conserva su negativo τ80 y última frontera con cinco métricas positivas
τ72. CP12 original, K4, F0…F5, CP04 y prefijos cerrados no se repiten. El
histórico **116/308 permanece INCOMPLETO** y no cuenta documentos originales.
No se activa M3. Las dependencias del primer dispositivo siguen siendo
estabilidad, preparación, acceso finito, retroacción, receptor, retención y
ciclo; las exclusiones de Canal se conservan.
