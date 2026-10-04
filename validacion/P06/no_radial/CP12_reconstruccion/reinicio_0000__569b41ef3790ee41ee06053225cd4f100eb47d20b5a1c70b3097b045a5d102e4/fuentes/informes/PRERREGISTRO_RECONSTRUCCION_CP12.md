# CP12 · Reconstrucción explícita del tramo perdido y conservación de reinicios

Registrado antes de ejecutar la reconstrucción, el 4 de octubre de 2026. Autorización: reconstruir expresamente 0→16 de las mismas dos trayectorias y, sólo si reproduce, continuar desde 16 a 160. El PR #2 permanece en borrador. Este documento complementa la procedencia; **no modifica** el [protocolo causal](PROTOCOLO_CP12_CAUSA_CHI.md), sus enmiendas, código, observadores, hipótesis ni puertas.

## Identidad y alcance

Se conserva el ID `a9f349020526a720f5448e6de0de08fe60cf1c058965fe2287fba9eed434789d`, la configuración original de h=.125/.0625 y los catorce archivos de su clausura. El recibo de la reconstrucción tendrá fechas nuevas y declarará su origen. No se reconstruye un recibo histórico ni se atribuyen al nuevo cálculo los segmentos perdidos. El [incidente](INCIDENTE_RECUPERACION_CP12.md) y sus límites permanecen como historia.

El estado inicial se obtiene de CP04 mediante la semilla original, y se exige `array_equal` con ambos datos iniciales CP10. M2, Θ, R=220, L=4, ε=.02, DOP853, fuerza C, rtol=1e−10, atol=1e−12, max_step=.02, fronteras físicas de ocho unidades, observaciones .4, ventanas pasivas .01 y órdenes Gauss 7/6 permanecen idénticos. No se repiten preparación CP04, E00/E01/C0 ni otras campañas. No se prueba ninguna corrección.

La nueva herramienta de gestión sólo registra, verifica, pausa y empaqueta. Invoca el trabajador y el adaptador originales. No participa en sus fuerzas, pasos, dense output ni acumuladores. Sus verificaciones se registran con identidades independientes bajo `CP12_reconstruccion`, sin renombrar la ejecución científica.

## Pruebas anteriores al avance

1. Verificar identidad a9f349…, las 33 etapas, Θ y controles originales. Registrar fuentes y entorno antes de cada verificación. Capturar todas las entradas del par, además del código y protocolo, sin inventar procedencia anterior.
2. Crear una cápsula de preejecución con recibo registrado, configuración, fuentes, controles y este prerregistro. Guardarla permanentemente, descargarla por su identidad y verificar SHA-256 y cobertura del manifiesto. No iniciar pasos M2 sin este comprobante.
3. Inicializar el trabajador con pausa en τ=0, sin pasos M2. Verificar y respaldar también ese estado inicial acumulado. Luego ejecutar únicamente 0→8, pausar, comprobar y respaldar; después 8→16, pausar, comprobar y respaldar.

## Antecedentes que se comparan

Los valores siguientes son antecedentes conservados en salidas de herramientas de la conversación, no archivos recuperados. Las nuevas comprobaciones conservarán sus propios datos.

| Frontera | Observaciones por malla | Pasos / evaluaciones por malla | SHA-256 del NPZ anterior | Bytes anteriores |
|---|---:|---:|---|---:|
| 8 | 21 | 1483 / 18266 | `4f79027f479da1136825b47bcff9bb90a8a989cd78af90e570c205eafa904281` | 28259626 |
| 16 | 41 | 2966 / 36136 | `3262c6eb99838319c31e2379cc11c4cd97b0631d5fd2760b741fc716622f4b21` | 28393475 |

En cada frontera se exige configuración exacta, arrays finitos, prefijo físico CP10 `array_equal`, tiempos, contadores, balances originales y todos los controles originales del observador. Los rótulos temporales de las vistas pasivas pueden diferir por representación flotante hasta 1e−12, como se explicó en el incidente; las observaciones físicas continúan comparándose **exactamente**. Se comprueban los hashes y tamaños anteriores: una discrepancia detiene el avance y exige distinguir serialización/metadatos, aritmética o evolución antes de cualquier decisión. No se relaja un criterio tras observar datos.

El máximo anterior a 16 de cierre bruto era 5.80276454319202e−7. Se publica su comparación; los límites de aceptación siguen siendo los originales, no un ajuste a ese valor. Un reinicio se carga en copia mediante el trabajador original, con `stop_at` igual a su tiempo, y se exige que no cambien su hash, arrays, contadores ni presupuesto. Esta prueba ejecuta cero pasos M2.

## Respaldo como puerta obligatoria

Cada frontera 8,16,24,…,160 se ejecuta en un segmento que termina antes de la siguiente. Se preservan NPZ, progreso, recibo cerrado del segmento, configuración, log, presupuesto parcial, fuentes capturadas, controles y verificación independiente. Cada cápsula contiene un manifiesto SHA-256 y dependencias suficientes para leer y probar el reinicio fuera del directorio original. Los archivos fuente originales y su vínculo con CP11 quedan identificados; los paquetes de trabajo no se denominan checkpoint científico cerrado.

La puerta de respaldo sólo pasa después de guardar el ZIP, descargar la misma versión a otra ruta, verificar su hash y **todos** sus archivos, comprobar el recibo extraído y cargar el reinicio en esa copia sin avanzar. El comprobante conserva identidad del archivo permanente, hashes de ZIP/estado/recibo/configuración, tiempo, versión, verificación y vínculo al respaldo anterior. El siguiente segmento exige ese comprobante y que coincida con los bytes presentes. Un fallo de subida o descarga no autoriza a continuar.

No se usa una transferencia incompleta ni un fragmento como respaldo. No se sobreescriben cápsulas previas. Las cachés compiladas se reconstruyen desde fuentes y no constituyen dependencia. Las pausas, verificaciones y transferencias cambian sólo tiempo de pared/procedencia, nunca la física ni el presupuesto acumulado.

## Continuación y decisión

Después de validar y respaldar 16, continuar el **mismo** par/ID/protocolo por fronteras originales hasta 160. En cada frontera se comprueban los controles originales y se verifica el respaldo antes de avanzar. Cualquier discrepancia de reproducción, hash, configuración, balance, identidad, simetría, Parseval, cierre o control entre órdenes detiene el avance para diagnóstico. El incidente no cierra CP12 ni constituye un resultado negativo científico.

A 160 se exige reproducción final exacta CP10 de campos, velocidades, iniciales, observaciones, pasos, evaluaciones y máximos E/Q. Sólo entonces se interpreta el presupuesto operador/fuente/inicial, sus componentes cortas, comienzos, cancelaciones y realimentación según el prerregistro original. La puerta física sigue 2 %. Una atribución condicionada no prueba estabilidad continua ni convergencia de una corrección. No integrar el PR, crear tag/Release ni ensayar corrección antes del cierre científico y sus pruebas pertinentes.

No hay reorganización, migración ni renombrado: origen → destino = ninguno.
