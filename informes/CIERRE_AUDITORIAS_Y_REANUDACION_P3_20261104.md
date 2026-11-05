# P3: compilador original, auditorías y reserva desde τ12,8

Entrega del 4 de noviembre de 2026, hora de Lima; recibos en UTC. **CP11 aceptado; CP12 abierto; P3 sin validar. Última frontera completa positiva: τ8. Próxima frontera: τ16, pendiente.**

## Pregunta y protocolo

Se recuperó el entorno registrado y la cápsula existente de τ12,8 para cerrar las auditorías pendientes sin repetir una trayectoria. Se aplicaron el prerregistro P3, la asignación p3_128_a16_20261104b y los adaptadores administrativos registrados. No se cambiaron fuentes científicas, M2, Θ, CP04, mallas, tolerancias, observadores ni umbrales.

Los heads iniciales coincidieron con el relevo: P3 14b8a8e0546e72154d216db4ca77a223146dd0c6; auxiliar 22c8d24a04d2c3a6e6d49191a57129da49badf66; main 90e8fcffbba65629a1628f435d3c3240832fe9c4. [Inventario](../trazabilidad/cierre_auditorias_20261104/HEADS_INICIALES.json).

## Compilador restaurado realmente

Se descargó el artefacto Actions13379651727, ejecución41948353356:34480463 bytes; SHA256 f171dadffe93cd31195c71008eae8b2751d76d182ba29661be2355f762d9d385. Los tres paquetes oficiales coinciden en tamaño y hash con el registro original. Se instaló mediante herramientas/restaurar_compilador_p3.py en prefijo privado, sin reemplazar paquetes del sistema.

La versión real es “cc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0”; SHA256 del ejecutable6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234. No se falsificó la versión ni se adaptaron auditores. [Restauración](../trazabilidad/cierre_auditorias_20261104/RESTAURACION_COMPILADOR.json).

El mismo ZIP quedó en la Release experimental como adjunto **711636597**, P3-compilador-13.3.0-41948353356-1.zip. Una descarga pública independiente coincidió y sus tres paquetes se verificaron otra vez. [Recibo público](../trazabilidad/cierre_auditorias_20261104/COMPILADOR_PUBLICO.json). Ya no se depende exclusivamente de la retención de90 días de CI.

## Cápsula y auditorías originales

Se descargó públicamente el adjunto **711173125** existente:229945240 bytes; SHA256 a58969092423501904f45bfa9e6143d41afac19970c9b61fa0222beb9e13c1d3. El NPZ interno conserva47a13c99178ea12d3682e86cdd347eccdaaf0b9e1b536705b1477663ff6d547f.

El desempaquetador original exigió cobertura exacta y verificó las **305 cargas**. Pasaron los **30 controles de fronteraτ8 y14 del transporteτ12,8**, con cero construcciones/pasos DOP853. Todas las cargas y el ZIP se comprobaron otra vez al terminar. [Resultado y hashes de stdout/stderr](../trazabilidad/cierre_auditorias_20261104/auditoria_t128/RESULTADO.json).

Python3.12.14, NumPy2.3.5, SciPy1.17.0, Matplotlib3.10.8 y threadpoolctl3.6.0 coinciden. Los controles originales de entorno e implementación pasan con BLAS de un hilo y arquitectura sin forzar. El adaptador registrado comprobó después memoria interna/pasiva, alias, contadores y relojes exactos en12,8; ambos límites internos siguen en16. [Restauración exacta](../checkpoints/CP12/p3_20261018/reanudacion_t128_20261104/RESTAURACION_EXACTA.json).

## Conservación del proceso real y reserva

El trabajador nuevo, sesión93920, tomó ambos bloqueos y ejecutó su control antes de física. CONTROL_P3_128_A16_20261104B tiene **231026178 bytes** y SHA256764849209795eab5380e8358e62257c0a97c4681375f4c933ad0665063e5a726. Se guardó y recuperó por su identidad nativa; después se publicó como adjunto **711636683**, se descargó públicamente y se auditaron ambas extracciones mediante los controles originales. [Aceptación combinada del mismo proceso](../checkpoints/CP12/p3_20261018/reanudacion_t128_20261104/capacidad/ACEPTACION_COMBINADA.json).

Se preparó la [reserva12,8→16](../checkpoints/CP12/p3_20261018/reanudacion_t128_20261104/ASIGNACION_128_A16.json) para publicarla antes de activar. En ese instante el trabajador esperaba y no había ejecutado nuevos pasos. Su registro y código siguen idénticos; no fue necesario modificar el lanzador. La activación posterior debe identificar el commit público de esta reserva y el hash de su control.

La asignación anterior sigue bloqueada. No se recreó su archivo privado de publicación, no se presumió su salida y no se repitieron9,6→11,2 ni11,2→12,8.

## Continuidad y alcance

Se sincronizan portadas, progreso, registro de cálculos, registro canónico y vistas desde la evidencia actual. Los campos anteriores y sus blobs quedan identificados en [el registro previo](../trazabilidad/cierre_auditorias_20261104/ANTES_SINCRONIZACION.json); los textos de entrada se conservan en bytes y en Git.

Se revisó [la aceptación global](../trazabilidad/continuidad_20261104/ACEPTACION_GLOBAL_GITHUB.json): el adjunto709420494 ya recuperó2625 archivos del commit e6c388964562cb7f84c8488a7060a6745d049a4b. No se repiten pendientes administrativos antiguos por inercia. Una entrega posterior tendrá identidad propia.

Esta entrega cierra restauración del compilador y auditorías pendientes; acredita capacidad y reserva. No acredita aún una frontera16 positiva ni valida P3. P2 permanece suspendido; los negativos originales, las33 etapas, las24 funciones y116/308 conservan su alcance.

## Puertas y siguiente acción

Publicar la reserva y activar el proceso preparado desde12,8. Recuperar y auditar cada transporte permanente antes de seguir. En16 exigir extracción independiente, cinco métricas≤.02, energías consistente y FV original≤2e-4 por separado, carga≤1e-9, identidades/simetría≤2e-12, Parseval≤2e-11, observadores≤1e-3 y controles originales de núcleo/amplificación aplicables.

Ante un negativo, conservarlo y recuperarlo, suspender esa versión y registrar el diagnóstico pendiente. Si todo pasa, habilitar sólo la siguiente frontera del protocolo. CP12 sigue abierto y CP11 estable.

El commit de la entrega es el commit Git que contiene este informe y su reserva; se evita una autorreferencia circular. La activación posterior registra ese identificador explícitamente.
