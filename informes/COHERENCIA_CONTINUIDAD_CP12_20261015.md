# CP12 · Coherencia de continuidad sin cambio científico

La vista generada `ESTADO_ACTUAL.md` seguía mostrando τ24 y la prohibición operativa histórica de iniciar un trabajador independiente. Esas frases no reflejaban los comprobantes posteriores ni la autorización vigente.

Se actualizan sólo `next_actions`, `delivery_boundary` y esta entrada de historial en `estado_progreso.json`, y se regenera `ESTADO_ACTUAL.md` con `herramientas/generar_continuidad.py`, sin modificar el generador. Se conservan íntegramente las 33 etapas, resultados negativos, historial previo y todos los demás campos canónicos. No se altera código bajo un trabajador activo.

La frontera certificada sigue siendo τ88: 33 controles originales, 221 observaciones CP10 exactas por malla, estado SHA256 `c421fa81728b7d4079807bf0a1848b062ec0a5c596316652be1fb933a994da3a`. La recuperación numérica pública completa corresponde a τ80. Fuentes: `checkpoints/CP12/continuacion_20261014/tau0088/AUDITORIA_FRONTERA_GUARDADA.json` y `checkpoints/CP12/continuacion_20261014/INTERRUPCION_Y_REANUDACION_20261015.json`.

La instancia aislada actual fue observada directamente en 88→96. Esa actividad no es una cápsula ni certifica τ96. No se inicia otra evolución ni se supone la terminación de ejecutores anteriores. Cada frontera exige conservación, recuperación independiente y auditoría antes de avanzar.

Esta revisión ejecuta cero pasos M2. No certifica causa, corrección, convergencia ni cierre de CP12. Main sigue en CP11 y PR #2 abierto/borrador; no hay merge, tag ni Release.
