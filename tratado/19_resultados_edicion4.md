# 19 · Resultados y verificaciones de la base M2 4.0

El resultado físico del ensayo de guía es negativo: el Q-tubo autosostenido presenta una banda longitudinal creciente. Un verificador correcto puede, por tanto, confirmar un fallo de diseño; «pruebas correctas» no significa «dispositivo aceptado».

| Verificación | Resultado | Alcance |
|---|---:|---|
| Geometría, contratos y balances anteriores | 194 comprobaciones correctas | Geometría y modelos R1 condicionados |
| Nueva evaluación M2 | 38 comprobaciones correctas | Convergencia, balances, resultados negativos y coherencia de su clasificación |
| Dispositivos completamente derivados | 0 | Conjunción de los eslabones exigidos |

Esta tabla describe la base de entrada, cuyos bytes se conservan en `trazabilidad/fuente_M2_4_0.zip`. Los registros actualizados están en `validacion/informe.json`, `validacion/verificacion_m2.json` y `validacion/capilaridad/verificacion.json`; sus contadores pueden variar al incorporar nuevos archivos. Los 52 controles capilares se interpretan con el alcance del capítulo 22. Las soluciones, espectros, transitorios y contraste térmico están en archivos JSON/CSV separados para evitar ocultar precisión tras el redondeo de las tablas.

La estabilidad del vacío y las propiedades del problema de Cauchy corresponden al sector clásico definido. La prueba analítica de inestabilidad del tubo declara sus hipótesis. La estabilidad espectral completa de una primordial no está demostrada. Las verificaciones en coma flotante no se renombran como certificaciones por intervalos.

Para repetir las pruebas de esta edición se usan las instrucciones de `M2_RESULTADO.md`. Las versiones de dependencias están en `requirements.txt`; el código no necesita conexión de red para ejecutar los cálculos una vez instaladas. El manifiesto SHA-256 identifica el contenido de la entrega, no prueba la corrección física de las ecuaciones.
