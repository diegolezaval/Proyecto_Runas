# CP12 · Trabajo recuperado y bloqueo por estado faltante

El último checkpoint científico cerrado sigue siendo **CP11**, en `main`/tag `CP11`, commit `ed8d818b622a0687aeb56d34ca9e3913bd54e124`. La rama `ciencia/cp12-causal-chi` conserva el prerregistro CP12, su instrumentación y seis controles con sus fuentes y recibos, commit `3fdffd3df115f18f2abfaceff97efe4d1a203c12`.

La limpieza automática del espacio de ejecución retiró el trabajo local no publicado. La transferencia del estado CP12 no llegó a completar su conservación permanente. Fue un fallo de persistencia del trabajo; **no** un resultado negativo de M2, una inestabilidad física ni una prueba de la causa de la falta de convergencia. Debió asegurarse la copia permanente antes de prolongar el cálculo.

## Qué se ha recuperado y qué falta

Se recuperó el repositorio de la rama científica. Los 1047 archivos originales de CP11 son recuperables por sus hashes, mediante sus rutas actuales o la instantánea `trazabilidad/CP11_entrada/`. Los seis controles de instrumentación conservan sus recibos íntegros, incluidos los tres intentos técnicos FALLIDA. Se conservan exactamente M2, Θ, el estado CP04 de origen, las evoluciones cerradas, resultados negativos y la puerta espacial del 2 %. No se ha movido ni eliminado evidencia.

No se encontró el estado operativo del par instrumentado, sus presupuestos temporales ni el recibo completo de esa ejecución en la rama, Releases, artefactos de ejecución o archivos guardados disponibles. La búsqueda por nombre de CP12 y del NPZ no devolvió una copia. La subida completa del estado τ=8 tampoco creó el objeto Git esperado. Un fragmento de transferencia de 524286 bytes de τ=16 no constituye un NPZ completo ni un reinicio válido.

Los siguientes datos proceden de **salidas de herramientas de la sesión anterior conservadas en la conversación**. Se registran como antecedente de recuperación; sus archivos originales están ausentes y no se presentan como evidencia numérica actualmente reverificable:

| Antecedente | Valor observado anteriormente | Alcance actual |
|---|---|---|
| Ejecución | `a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d` | Identidad del protocolo, no sustituto del recibo perdido |
| Último estado observado | τ=16, dos mallas .125/.0625 | No disponible para reanudar |
| Estado τ=8 | SHA-256 `4f79027f479da1136825b47bcff9bb90a8a989cd78af90e570c205eafa904281`, 28259626 bytes | Ausente |
| Estado τ=16 | SHA-256 `3262c6eb99838319c31e2379cc11c4cd97b0631d5fd2760b741fc716622f4b21`, 28393475 bytes | Ausente |
| Observaciones hasta τ=16 | 41 por malla, `array_equal` con el prefijo CP10 | Comprobación previa; archivos ausentes |
| Pasos/evaluaciones hasta τ=16 | 2966 / 36136 por malla | Contadores previos; no acreditan τ=160 |
| Residual máximo observado del presupuesto | 5.80276454319202e−7, límite 1e−3 | Control previo; no causa certificada |
| Reinicio sin avance τ=8 | Hash antes/después idéntico | Prueba previa; archivo ausente |
| Auditoría de reinicio τ=16 | Primera FALLIDA `e1a6d6f2cd4132887e2defa40020e0b701628ff3655515e01088a5ed8ed2cb00`, después positiva `f61bd08da85ea65072aa39e9b20b86eea521f68b06ed93b84bb75272d385f3fe` | Sus recibos y fuentes no fueron publicados |

La primera auditoría independiente confundió un subconjunto de parámetros físicos con metadatos adicionales de configuración y dos representaciones flotantes de rótulos temporales. La diferencia de rótulos era ≤1.7763568394002505e−15; las observaciones físicas mantuvieron la exigencia exacta. Su corrección no cambió el solver ni el 2 %. Este relato no reconstruye ni inventa los archivos de aquella auditoría.

## Puerta de recuperación

**CONTINUACIÓN CIENTÍFICA BLOQUEADA POR ESTADO FALTANTE.** No hay cálculo activo comprobado ni una reproducción terminada a τ=160. No se certifica causa, convergencia, corrección ni cierre científico CP12. Las 33 etapas y todos sus registros científicos permanecen como en CP11; el último estado no radial terminado válido sigue siendo el de CP10.

1. Si existe una copia del paquete de trabajo CP12, recuperar el NPZ junto con su `configuration.json`, progreso, recibo, fuentes capturadas y presupuesto. Verificar sus hashes y la cadena de reinicios antes de ejecutar `--reanudar`.
2. Un NPZ aislado puede permitir recuperar arrays, pero no restituye por sí solo la procedencia previa. Declarar explícitamente cualquier componente faltante, sin fabricar un recibo histórico.
3. Si no existe copia, retomar exactamente desde τ=16 resulta imposible. Haría falta una reconstrucción numérica explícitamente prerregistrada del tramo perdido de las **mismas dos trayectorias autorizadas**, con comparación contra los hashes anteriores si el entorno permite identidad binaria. No tratar esa reconstrucción como un cálculo nuevo ya terminado ni ejecutarla silenciosamente. Antes, establecer una conservación permanente comprobada de cada reinicio.
4. Después de recuperar un estado válido, retomar sólo el presupuesto causal previsto, exigir reproducción final exacta de CP10 y aplicar las puertas originales. No probar una corrección sin mecanismo suficientemente discriminado.

El siguiente paso es una decisión de recuperación, no otra malla, una variante física, CP13 ni un cambio fundamental. La causa científica sigue abierta. No se integra esta rama en `main`, ni se crea un tag/Release CP12 mientras falten las pruebas necesarias.

## Comprobación actual

El protocolo [revisión de recuperación](../datos/revision_recuperacion_CP12.json) captura antes de ejecutar los hashes, entorno y fuentes de la revisión. Su resultado conserva los controles y verifica antecedentes, puertas y ausencia del estado. `passed` en ese recibo significa integridad del material recuperado; `resume_ready=false` mantiene el bloqueo científico. No ejecuta pasos M2.

No hay migraciones de rutas: origen → destino = ninguno. No se cambió la hoja de ruta, teoría, parámetros, configuración instrumentada ni documentación científica histórica.
