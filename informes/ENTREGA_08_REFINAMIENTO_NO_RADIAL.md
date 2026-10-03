# Entrega 08 · Refinamiento no radial terminado

**Checkpoint: CP08_REFINAMIENTO_NO_RADIAL.** Se terminó el cálculo pendiente h=.125 hasta τ=160 desde el último estado válido guardado. Se completaron las comparaciones de error y se aplicó la puerta: **NO SUPERADA; cálculo finalizado, refinamiento adicional pendiente**. No queda ninguna evolución activa en esta entrega.

## Qué quedó terminado

La campaña exigida reúne ocho evoluciones Verlet cerradas en CP06 y cuatro evoluciones adaptativas DOP853. Sólo faltaba completar la cuarta adaptativa; tras la pausa se reanudó en τ=48, sin volver a τ=0 ni repetir E00, E01, C0, la preparación CP04 o las otras evoluciones terminadas. También se conserva el control `split4c` fino que completó su ventana y los pilotos interrumpidos o rechazados.

Se reutilizó el estado de Cauchy de CP04, con su hash de origen verificado. La nueva ejecución mantuvo L=4, R=220, ε=.02, h=.125, rtol=10⁻⁹, atol=10⁻¹¹ y paso máximo .02. Las derivas relativas máximas son 6.33108e-09 en energía y 5.44009e-15 en carga, por debajo de 2×10⁻⁴ y 10⁻⁹. La amplificación máxima de la norma no radial es 1, frente al límite 3; el cambio de carga del núcleo es 0,0104166 %, frente al límite 0,5 %. La conservación se vigiló en cada paso aceptado.

## Comparaciones y puerta

| Control | Φ: campo final | χ: campo final | χ: campo y velocidad | Decisión |
|---|---:|---:|---:|---|
| Tolerancia 10⁻⁸→10⁻⁹, h=.5 | 1,51828e-05 % | 0,00190771 % | 0,00271886 % | Superada |
| Malla .5→.25 (fallo conservado) | 1,12264 % | 4,03411 % | 5,00924 % | No superada |
| Malla .25→.125 (nuevo) | 0,285106 % | 3,45323 % | 5,04292 % | No superada |
| Angular L4→L6 (ya cerrado) | 1,67967 % | 1,39832 % | 1,64526 % | Superada |

Las diferencias se normalizan por la perturbación inicial no radial en r<40, con las masas de cada campo para ponderar velocidades. Sólo se elimina la fase U(1) global de Φ. Los límites son 2 % para espacio/tiempo y 5 % para el control angular. El error de la norma de Φ a lo largo de la ventana en la comparación fina es 0,152733 %; el error final de Φ incluyendo velocidades es 0,929822 %.

La puerta vigente está en `validacion/P06/no_radial/resultados.json`: `REFINAMIENTO_PENDIENTE`. Conserva el fallo L2→L4 y el fallo espacial .5→.25 como antecedentes, usando los refinamientos prerregistrados para la decisión final. No cambia los umbrales para aceptar un resultado. Los controles son individuales; no constituyen una cota rigurosa del error continuo ni una exploración conjunta de todas las mallas y truncaciones.

El diagnóstico adicional sobre los tres estados guardados muestra reducción casi cuádruple en el error de posiciones de Φ (factor 3,94), pero ninguna reducción en χ con velocidades (5,009 %→5,043 %). La diferencia inicial correspondiente de χ entre las mallas finas es sólo 0,00620 %; esto no identifica por sí solo la causa de la separación posterior. No se justifica extrapolar por Richardson ni asegurar que una nueva malla pasará. Se conserva esta incertidumbre y no se inicia otra campaña antes de la entrega solicitada. Datos: `validacion/P06/no_radial/diagnostico_convergencia_CP08.json`.

## Fallos y continuidad conservados

Se incluyen los pilotos `split4`, los fallos de conservación `split4c`, los pilotos `split4b` sin mejora, los fallos de refinamiento y el primer intento de colocación compleja que no convergió. No se confunden con inestabilidades físicas. Los archivos históricos parciales siguen presentes; el registro de cálculos identifica cuál es el resultado vigente.

El cambio a la fuerza opcional en C pasó una auditoría de igualdad exacta en cinco muestras antes de la reanudación. El incidente de doble lanzamiento interrumpido queda registrado; el último estado válido se identificó por tiempo explícito, campos finitos y procedencia. El bloqueo de escritor único se comprobó rechazando una segunda apertura sin modificar el estado. Las fuentes se entregan; las cachés compiladas no son necesarias.

## Avances incluidos desde CP04

CP05 cerró la subpregunta condicionada de simetría para estados positivos localizados de fase común. CP07 cerró la subpregunta de fase espacial sin nodos y el acceso lineal muestreado a Reserva: nueve frecuencias sobre el fondo guardado ω=.9, refinamientos, balances y colocación independiente. La ganancia energética máxima de la muestra fue 0,157 % en Ω=2.3; no es una ganancia máxima global ni un ciclo de extracción finita. Los capítulos 27–30 e informes 05–07 contienen las derivaciones y límites.

## Qué sigue parcial

**E02, E03, E04, RES0, RES1 y C7 permanecen PARCIALES; RES2 sigue BLOQUEADA.** E00, E01 y C0 permanecen COMPLETADAS. No se declara estabilidad orbital general, cierre de la preparación física, apagado, retroacción finita, recepción, ciclo de Reserva ni dispositivo completo.

Investigar el fallo de la puerta con los datos guardados; prerregistrar el refinamiento necesario antes de iniciarlo. No repetir las doce evoluciones terminadas.

Esta entrega cierra el cálculo solicitado y conserva el punto de continuación. Los pilotos fallidos no requieren reanudación automática; no hay un cálculo válido pendiente que deba reiniciarse desde cero.

## Archivos y comprobación

Extraer `Proyecto_Runas_M2_4_2_CP08_PROYECTO.zip` y `Proyecto_Runas_M2_4_2_CP08_ESTADOS_ACCESO.zip` en la misma carpeta. Juntos reconstruyen el proyecto completo con todos sus estados. El manifiesto SHA-256 corresponde a esa unión. Las verificaciones de integridad y continuidad son de lectura y no repiten la física histórica.

Leer `ESTADO_ACTUAL.md`, `estado_progreso.json` y `datos/registro_calculos.json`. Para verificar archivos, ejecutar `python herramientas/checkpoint.py --verificar`. No usar una reproducción histórica como siguiente paso de investigación.

Verificación de entrega: 154 archivos protegidos de CP04 y 189 archivos de cálculos terminados en CP07 conservan sus hashes; E00/E01/C0 conservan exactamente sus registros. La comprobación editorial y estructural pasó sin incidencias (279 JSON, 52 archivos Python, 66 SVG y 147 enlaces locales). No se repitieron evoluciones para estas comprobaciones.
