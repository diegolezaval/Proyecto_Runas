# CP12 · Conservación y ejecución duraderas sin cambios científicos

Prerregistrado el 11 de octubre de 2026, antes de ejecutar segmentos físicos en GitHub. La autorización vigente exige continuar automáticamente, buscar ejecuciones previas, evitar duplicados y conservar cada frontera antes de avanzar. Dos sesiones locales posteriores al reinicio verificado de τ=16 se perdieron durante interrupciones. Estas pérdidas técnicas no son resultados científicos ni cierran CP12.

## Alcance y límites

Se mantienen el par, ID original a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d, h=.125/.0625, los catorce archivos científicos, M2, Θ, solver, tolerancias, observadores, las fronteras y todas las puertas del protocolo. El cambio consiste únicamente en almacenar y recuperar bytes y organizar segmentos en un ejecutor que persiste después de una desconexión. No modifica los prerregistros científicos anteriores ni renombra sus campañas. El PR #2 sigue en borrador y main en CP11.

## Puerta de entorno, antes de cualquier paso M2

Se exige la identidad completa original, incluido el entorno del recibo, los catorce hashes, los seis controles y las referencias CP10. Se instala Python 3.12.14, las dependencias fijadas y el compilador Ubuntu 13.3.0-6ubuntu2~24.04 desde su archivo oficial firmado. No se simula la salida del compilador ni se relaja la identidad. El primer ensayo de entorno GitHub fue negativo por el sufijo de empaquetado .1 del compilador y ejecutó cero pasos M2; su log se conserva.

La recuperación inicial en GitHub se prueba sin pasos: hash completo del ZIP y todos sus archivos, recibos/configuración intactos y audit() original, incluida la carga del trabajador con stop_at igual al tiempo del reinicio. La igualdad exacta de la base angular pasiva y de los bytes guardados es obligatoria. Un fallo detiene la migración para diagnóstico. No se presume equivalencia aritmética por coincidir las versiones.

## Respaldo permanente mediante Git

El ZIP completo producido por gestionar_respaldo_CP12.py permanece la unidad de respaldo. Su transporte conserva literalmente encabezados, cuerpos comprimidos y directorio central; no recomprime ni transforma arrays. Los cuerpos se dividen en objetos inmutables de hasta 1048576 bytes, identificados por SHA-256. Las piezas pequeñas pueden compartir un objeto, con posición, tamaño y hash de cada pieza comprobados antes de escribirla. Una receta identifica cada objeto, tiempo, run_id, tamaño y SHA-256 del ZIP original. La reutilización de objetos idénticos reduce duplicados, sin omitir ningún byte del ZIP.

Cada receta y todos los objetos requeridos se publican juntos en un commit del PR. Ese commit constituye el identificador permanente del respaldo. Después se obtiene el commit en una copia independiente, se reconstruye el ZIP y se exige igualdad de tamaño y SHA-256 con el original. Se ejecuta verify_download() original: cobertura completa del manifiesto, hashes de cada archivo, recibos y auditoría extraída, prefijo CP10 array_equal, contadores, balances, controles y carga sin avance. Sólo después se publica el comprobante, con commit real, hashes de ZIP/estado/recibo/configuración, verificación y enlace al respaldo anterior. No se inventan identificadores de otro almacenamiento.

Un artefacto temporal de Actions, un objeto aislado, una receta incompleta o un commit no recuperado y verificado no pasan la puerta. Los objetos se guardan fuera de CP12_reconstruccion para que las cápsulas siguientes no encapsulen recursivamente las anteriores. Los comprobantes y antecedentes sí se conservan dentro de la cápsula original.

## Ejecución ordenada y parada

Cada tarea sólo puede avanzar una frontera de ocho unidades. Las tareas usan dependencias success, exclusión mutua y una comprobación del tiempo/certificado actual. Antes de cada avance se recupera y verifica el respaldo previo. Se ejecuta el adaptador original bajo la identidad original, sin añadir RHS, observadores o trayectorias. Tras terminar se audita y respalda la frontera nueva, se recupera el commit y se verifica; la tarea no termina con éxito antes de publicar su comprobante. Un fallo bloquea todas las fronteras posteriores y conserva su diagnóstico. No se ejecuta un tramo ya validado ni se habilita GitHub mientras una ejecución local pueda abarcarlo.

En τ=160 siguen siendo obligatorias la reproducción final exacta CP10, las identidades de defecto y Duhamel, la partición de fuente y la realimentación. La interpretación se ejecuta con su prerregistro existente y se revisan las puertas causales. Terminar tareas no cierra científicamente CP12. No se ensaya ninguna corrección hasta identificar suficientemente el mecanismo; cualquier prueba posterior tendrá fundamento independiente y prerregistro propio.

## Compatibilidad aritmética observada antes del traslado

El control independiente con dispatch Haswell del 11 de octubre, registrado antes de ejecutarse, falló en la igualdad de los datos iniciales CP10 al cargar τ=16; ejecutó cero pasos M2 y no alteró el reinicio. La identidad de versiones original no captura esta diferencia. El runner del primer ensayo GitHub sí informó SkylakeX. Se exige por tanto dispatch observado SkylakeX y un hilo antes de instalar el compilador y de actuar, además de identidad completa y recuperación exacta. No se fuerza un coretype ni se usa un conjunto de instrucciones incompatible. Un fallo de dispatch rechaza ese runner, no la trayectoria ni CP12. Se permiten hasta cuatro asignaciones de runner por frontera exclusivamente cuando el fallo precede a todo paso M2 y se debe a este control de hardware. Cualquier otro fallo, incluida una discrepancia de recuperación o evolución, exige diagnóstico y no habilita reintentos ciegos. Los run_attempt se identifican por separado; no se sobrescriben resultados de intentos anteriores.
