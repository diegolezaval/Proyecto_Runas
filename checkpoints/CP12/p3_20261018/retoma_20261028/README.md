# Retoma P3 · 28 de octubre de 2026

**Estado: bloqueada la continuación.** La repetición única terminó en transporte τ11,2, pero sus bytes no quedaron acreditados como respaldo permanente y no se encontraron al retomar. Los comprobantes de texto permanecen íntegros. Consulta el [incidente](INCIDENTE_SEGUNDA_PERDIDA_LOCAL.json).

| Paso | Resultado | Evidencia |
| --- | --- | --- |
| Integrar los tres respaldos originales | Completado; PR #3 integrado en P3 | [Guía de recuperación](../../../../respaldos/CP12_20261027/LEEME.md) |
| Recuperar τ8 y τ9,6 sin pasos | 30 y 14 controles superados | [Auditoría inicial](auditoria_inicial/RESULTADO.json) |
| Probar publicación y recuperación por Releases | Superado; 230902380 bytes y 292 archivos del manifiesto | [Aceptación](conservacion_control/ACEPTACION.json) |
| Repetir τ9,6→τ11,2 una sola vez | Cálculo terminado; 297 pasos físicos por malla; transporte local auditado | [Resultado](repeticion96_112/RESULTADO.json) y [comparación con recibo histórico](COMPARACION_CON_RECIBO_HISTORICO.json) |
| Conservar y recuperar el transporte nuevo τ11,2 | No completado; bytes no encontrados tras la interrupción | [Incidente](INCIDENTE_SEGUNDA_PERDIDA_LOCAL.json) |

La excepción está consumida y el lanzador de entrada queda bloqueado. Su [código exacto usado](https://github.com/diegolezaval/Proyecto_Runas/blob/4088598a647401c49b2f944fa08fe8417b45c5a2/checkpoints/CP12/p3_20261018/retoma_20261028/retomar_hasta11p2.py), [registro previo](REGISTRO_EJECUCION.json), [asignación exclusiva](ASIGNACION_UNICA.json) y resultados conservan su trazabilidad. Un hash o un comprobante no reconstruyen los bytes perdidos.

El último transporte permanente recuperable sigue en τ9,6. La frontera científica del ensayo sigue en τ8. CP11 aceptado; CP12 abierto y P3 sin validar. Las fuentes científicas, sus parámetros, puertas, estados anteriores y negativos se conservan.

[Estado vigente](../../../../RECUPERACION_CP12_ACTUAL.md) · [Prerregistro](PRERREGISTRO.md).

Se preparó un [publicador desde el proceso y sus condiciones](PUBLICACION_DIRECTA_Y_CONDICIONES.md), con ocho controles superados. La autenticación y la prueba real siguen pendientes; no autorizan otra física.
