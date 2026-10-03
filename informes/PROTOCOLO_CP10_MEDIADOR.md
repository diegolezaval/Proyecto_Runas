# CP10 · Continuación prerregistrada del mediador

Base arquitectónica CP09; resultado científico pendiente CP08. Este documento explica el protocolo de `datos/ensayo_mediador_CP10.json`, guardado antes del diagnóstico y de las evoluciones nuevas. No modifica la hoja original, Θ, las puertas ni el integrador.

La pregunta separa error temporal fino y refinamiento espacial. Primero se descomponen las diferencias de los estados ya guardados. Después se ejecutan dos resoluciones nuevas desde los seis campos de Cauchy de CP04 en t=1200: un control temporal sobre h=.125 y una malla h=.0625 con la misma tolerancia estricta. Se utiliza el integrador DOP853 completo de CP09 y el potencial C equivalente contrastado con NumPy en cada nueva malla. La ventana, perturbación, caja y truncación angular son las del protocolo explícito.

Cada ejecución tiene un ID de 64 dígitos derivado de configuración exacta, parámetros, entradas, código e identidad del entorno. Antes de iniciar el proceso se guardan el recibo y copias de código/Θ/protocolo; se capturan comandos, semillas, segmentos, hashes de reinicio y salidas. Los pilotos en τ=8 se reanudan con el mismo ID y NPZ. Un caso cerrado se reutiliza; un caso fallido conserva sus archivos y no se reanuda automáticamente.

Los hashes de salida de un recibo EN_PROGRESO pertenecen al último segmento cerrado y pueden diferir durante una continuación activa. Sólo un recibo terminado, sus salidas verificadas y una puerta explícita constituyen un cálculo cerrado. Las copias de `fuentes/` capturan los bytes usados: no deben ejecutarse desde su carpeta como si fueran el proyecto actual. Para reproducción se restaura su jerarquía lógica en una copia aislada y se verifica el estado inicial indicado.

El comando del segmento usa una descripción lógica con dos bases: el `entrypoint` es relativo a la raíz del proyecto; `configuration.json` y el destino `.` describen la carpeta de esa ejecución. El lanzador capturado construye las rutas efectivas y ejecuta el hijo con la raíz como directorio de trabajo. Para invocar directamente un trabajador desde la raíz, prefijar configuración y destino con la ruta de la ejecución; para continuar con control de identidad usar el lanzador. La descripción lógica no debe copiarse como un comando literal desde cualquier carpeta.

La rotación descriptiva del espacio de fases de χ y la dispersión libre ilustrativa sirven para investigar el error. No se emplean para ajustar los campos ni para superar el límite del 2 %. La fase U(1) global de Φ se trata igual que en CP08. Los controles históricos conservan sus mallas y alcances; no certifican convergencia conjunta en una malla nueva.

No se repiten E00/E01/C0, la preparación CP04 ni las doce evoluciones cerradas. La entrega final sólo podrá declarar la puerta que realmente resulte de comparar datos concluidos. E03/E04/RES0/RES1 mantienen sus contratos generales, y la validación de un dispositivo sigue pendiente.
