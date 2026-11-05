# P3: recuperación de τ14,4 y auditorías originales

Entrega del 5 de noviembre de 2026, hora de Lima. **CP11 aceptado; CP12 abierto; P3 sin validar. Última frontera completa positiva: τ8. Próxima frontera completa: τ16, pendiente.**

## Pregunta y estado real

Se recupera el estado más reciente ya calculado y se cierran las auditorías del entorno actual sin repetir trayectorias. La rama científica comenzó en `8f91bac9470edee86810ac22b146240c62cc71dc`, posterior al relevo recibido; la auxiliar sigue en `22c8d24a04d2c3a6e6d49191a57129da49badf66` y main en `90e8fcffbba65629a1628f435d3c3240832fe9c4`. Los recibos posteriores al relevo ya acreditaban restauración, reserva y activación de p3_128_a16_20261104b. Se reutiliza esa historia; no se reconstruye una autorización consumida.

La cápsula nativa de **τ14,4**, creada por esa asignación y conservada como `libfile_a21bf95078208191be81265f55c1c719`, sobrevivió fuera de su directorio temporal. Se recuperaron sus bytes, sin recalcular τ12,8→τ14,4. La búsqueda de nombres de esa asignación devolvió esta cápsula y su control; no se presenta esa búsqueda como prueba universal de ausencia de otros archivos.

## Compilador y entorno

Se descargó de nuevo el artefacto Actions **13379651727**, ejecución **41948353356**: **34480463 bytes**, SHA256 `f171dadffe93cd31195c71008eae8b2751d76d182ba29661be2355f762d9d385`. El restaurador original comprobó los tres paquetes oficiales y los instaló en un prefijo privado. Versión real: `cc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0`; SHA256 del ejecutable: `6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234`.

Pasaron los controles originales de entorno con Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8 y threadpoolctl 3.6.0. No se modificaron auditores ni se forzó la arquitectura BLAS. [Recibo del restaurador](../trazabilidad/reanudacion_20261105/RESTAURACION_COMPILADOR.json).

## Recuperación y controles actuales

| Cápsula existente | Bytes | Cargas verificadas | Auditorías originales actuales |
| --- | ---: | ---: | --- |
| τ12,8, adjunto GitHub 711173125 | 229945240 | 305 | 30 de frontera τ8 + 14 de transporte, positivas |
| τ14,4, identidad nativa recuperada | 230010057 | 314 | 30 de frontera τ8 + 14 de transporte, positivas |

τ12,8 conserva SHA256 `a58969092423501904f45bfa9e6143d41afac19970c9b61fa0222beb9e13c1d3`. τ14,4 conserva SHA256 **`5e2c494249b31d598af20559bfa5dbdb3f1d4038331a921dd3f9dc29d640b38d`**. El estado interno de τ14,4 tiene SHA256 `c1258c5381f307212bfcae26d9f955fb703c9d62fe59aa5d9bf17a00bcbf347d`.

Ambas extracciones exigieron cobertura exacta del manifiesto y todos los tamaños y hashes antes y después. Cada auditor declaró **cero construcciones/pasos DOP853**. Los stdout originales y sus hashes quedan en [auditoría τ12,8](../trazabilidad/reanudacion_20261105/auditoria_t128/RESULTADO.json) y [auditoría τ14,4](../trazabilidad/reanudacion_20261105/auditoria_t144/RESULTADO.json). Se mantienen idénticos los 240 archivos de ciencia, candidato, antecedentes científicos y prerregistros compartidos por ambas cápsulas; sólo cambiaron el transporte y se añadieron nueve registros o fuentes administrativas. [Comparación de inventarios](../trazabilidad/reanudacion_20261105/CONTINUIDAD_128_144.json).

El adaptador registrado restauró exactamente los estados físicos y pasivos, memoria, alias, contadores y muestreo denso. Los tiempos internos son 14.402373447614625 y 14.40236299909726, con 2670 pasos aceptados en cada malla; ambos límites internos siguen en 16. No se construyó un solver nuevo ni se avanzó M2. [Restauración exacta](../checkpoints/CP12/p3_20261018/reanudacion_t144_20261105/RESTAURACION_EXACTA.json).

## Trabajador y asignación

La sesión anterior 93920 ya no es accesible y su directorio científico no está presente. No se observó su salida y no se presume terminación. Esa asignación no se reactiva; tampoco se recreará su archivo privado de publicación de τ14,4. [Alcance de la comprobación](../checkpoints/CP12/p3_20261018/reanudacion_t144_20261105/ACCESIBILIDAD_ANTERIOR.json).

La asignación `p3_144_a16_20261105` queda **preparada, sin reserva ni activación**, con los adaptadores y ayudantes originales sin cambios y con origen exacto en τ14,4. Su [registro](../checkpoints/CP12/p3_20261018/reanudacion_t144_20261105/REGISTRO.json) no acredita capacidad de un trabajador futuro. No hay trabajador físico nuevo en este proceso.

## Conservación pendiente y siguiente acción

τ14,4 está recuperado y auditado por su identidad nativa; **todavía no tiene adjunto GitHub ni recuperación pública comprobada**. El acceso conectado permite publicar estos registros Git, pero no ofrece carga de adjuntos a Releases. El navegador y la CLI están sin sesión de GitHub. Se requiere iniciar sesión para publicar esos mismos bytes, descargarlos independientemente y aplicar otra vez los auditores originales. No se declara superada esa puerta pendiente.

Después se comprobará conservación nativa y pública desde el proceso real que continuará; se publicarán su reserva y activación con hashes antes de M2. Sólo entonces se continuará **τ14,4→τ16**. No repetir τ9,6→τ11,2, τ11,2→τ12,8 ni τ12,8→τ14,4.

En τ16 son obligatorias recuperación independiente, cinco métricas espaciales ≤0.02 sin redondear, ambas energías ≤2e-4 por separado, carga ≤1e-9, identidades/simetría ≤2e-12, Parseval ≤2e-11, observadores ≤1e-3 y controles originales de núcleo/amplificación aplicables. Un negativo se conserva y suspende esa versión; no se lanza otro candidato automáticamente.

Se preserva la aceptación pública del paquete global anterior; no se repiten sus arreglos administrativos como si siguieran pendientes. P2, CP10, CP12 original, CP04 y F0…F5 no se reabren. M2, Θ, datos, mallas, tolerancias, observadores y umbrales permanecen originales. **Esta entrega ejecutó cero pasos M2 y no resuelve la puerta espacial de τ16.**

Las fuentes anteriores de continuidad están conservadas en [la instantánea de entrada](../trazabilidad/reanudacion_20261105/ENTRADA.json). El commit que contiene este informe identifica la entrega; la publicación binaria posterior tendrá su recibo propio y no se anticipa su resultado.

## Verificación de la entrega administrativa

Las vistas generadas coinciden con sus fuentes y la comprobación editorial pasa. La regresión estructural aislada pasó todos sus comandos y 16 controles, sin ejecutar campañas numéricas y con los CSV/NPZ y el corpus de entrada intactos. [Recibo final](../trazabilidad/reanudacion_20261105/REGRESION_ESTRUCTURAL.json).

Se conservan dos incidencias administrativas corregidas: el contexto de enlaces de las copias Markdown se declaró en el mapa documental existente, sin cambiar sus bytes ni el verificador; una primera regresión coincidió con una edición del registro canónico y falló sólo su condición de fuente congelada. La repetición sin ediciones concurrentes pasó íntegramente. Estos incidentes no son negativos científicos y no se atribuyen a M2.
