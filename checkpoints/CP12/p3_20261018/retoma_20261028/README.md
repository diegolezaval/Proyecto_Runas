# Retoma P3 · 28 de octubre de 2026

Esta carpeta reúne las comprobaciones y el código administrativo para recuperar y retomar P3 bajo sus puertas originales. CP11 sigue aceptado; CP12 abierto y P3 sin validar.

| Paso | Estado | Evidencia |
| --- | --- | --- |
| Recuperar τ8 y transporte τ9,6 desde GitHub | Superado: 30 y 14 controles originales; cero pasos | [Auditoría inicial](auditoria_inicial/RESULTADO.json) |
| Probar conservación integrada por Releases | Superado: cápsula de 230902380 bytes, 292 archivos, descarga y auditoría independiente | [Aceptación](conservacion_control/ACEPTACION.json), [auditoría recuperada](conservacion_control/AUDITORIA_RECUPERADA.json) |
| Repetir una sola vez τ9,6→τ11,2 y conservar el nuevo estado | Reservado, pendiente de ejecución y conservación | [Registro del lanzador acotado](REGISTRO_EJECUCION.json) |

La [Release](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027) conserva los tres originales y el adjunto adicional `CONTROL_RUTA_RELEASE_TAU9P6_20261028`. Este último incluye relleno determinista identificado como prueba administrativa de capacidad. Conserva el mismo transporte τ9,6; no es un avance científico.

El [prerregistro](PRERREGISTRO.md) fija orden, puertas y límites. Los [controles de conservación](CONTROLES_CONSERVACION.json) y [del bloqueo de reanudación](CONTROLES_REANUDACION.json) rechazan entradas inválidas sin física. Las fuentes científicas y administrativas capturadas originalmente permanecen intactas; la nueva administración se añade por separado.

[Estado vigente de P3](../../../../RECUPERACION_CP12_ACTUAL.md).
