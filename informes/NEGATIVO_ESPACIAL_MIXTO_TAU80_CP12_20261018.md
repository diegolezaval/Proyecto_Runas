# CP12: negativo espacial mixto en τ80 y diagnóstico pasivo

La versión Φ-FV / χ-K4 queda **suspendida en τ80**: fases χ = **2.31190799094648 % >2 %**. Las otras cuatro métricas pasan. La cápsula completa fue recuperada y auditada con 28 controles positivos; el negativo se conservó y recuperó antes de la salida propia observada con código2. No se ejecutó 80→88. La última frontera con las cinco puertas positivas es τ72. CP12 permanece abierto; CP11 sigue aceptado.

## Puertas y conservación

| Métrica original | Error (%) | Límite (%) | Decisión |
|---|---:|---:|---|
| Norma temporal suprema | 0.0208614923952 | 2 | Pasa |
| Campo Φ | 0.0347184015964 | 2 | Pasa |
| Fases Φ | 0.0580769705122 | 2 | Pasa |
| Campo χ | 1.62881967649 | 2 | Pasa |
| Fases χ | 2.31190799095 | 2 | NEGATIVO |

Energía FV máxima 2.87059382931e-08; energía mixta máxima 2.2061275029e-10; ambas ≤2e-4. Carga máxima 8.881784197e-16 ≤1e-9. Cierre/orden máximo 1.65989882682e-06 ≤.001; Parseval 2.03821044247e-14 ≤2e-11. Identidad, simetría, configuración, fuentes, semillas y contadores pasan sus controles originales.

| Evidencia recuperada | Bytes | SHA256 |
|---|---:|---|
| Frontera completa80 | 232220697 | `af4c927287e6eec056af436b8f40fca0fc7553a429aa0de049b30a6fe4aa5801` |
| Negativo espacial80 | 232196186 | `d883338d801a2357f8904ae89a2866b0ad4d8b0057e935e82343b067c1c7394d` |

Estado80: `abfae6d6b88a1f5b6a58df1657ea3f860a81b02835fe6598b97315da3c1f3ba4`. Recibo: `ee4c1d86652736ca3ac227f6e1a65adc539a8320ba49c415fabcd3108b14c6c5`. Configuración: `0719d82ab2187b6076fa2baf6d010495bdffd59622b9ca8f56345beb19e7f182`. El recibo conserva el tramo terminado; la suspensión científica está en el certificado de secuencia, sin reescribir la historia.

La auditoría completa terminó a 2026-10-18T08:12:03.842519+00:00, la lectura negativa a 2026-10-18T08:12:09.096653+00:00, la conservación del negativo a 2026-10-18T08:12:33.480335+00:00 y la salida propia a 2026-10-18T08:12:33.566034+00:00. El diagnóstico condicionado se ejecutó después, a 2026-10-18T08:12:56.250054+00:00. Las sesiones anteriores inaccesibles conservan actividad desconocida.

## Causa condicionada por los observadores guardados

Se aplicó el diagnóstico prerregistrado a la extracción independiente80 y a la fila original del mismo τ80 conservada en el NPZ original160. Datos iniciales y configuración coinciden exactamente. El error original era 4.45986767457 % y el mixto 2.31190799095 % (reducción de norma 48.16195996 %). Cero pasos M2; los bytes de entrada permanecen idénticos.

El **operador χ acoplado sigue siendo suficiente en las tres ventanas** con los criterios originales (proyección≥.8, coseno≥.8 y reducción cuadrática al retirar≥.5). El residuo continúa atribuido a ese canal radial dentro de esta descomposición. Las puertas energéticas y de observadores positivas delimitan un fallo del acuerdo espacial.

| Ventana original | Norma original del canal χ (%) | Norma mixta (%) | Mixta/original | Proyección mixta | Coseno mixto | Reducción cuadrática al retirar (%) |
|---|---:|---:|---:|---:|---:|---:|
| core_phase | 4.4421438874 | 2.29187912707 | 0.515939867137 | 0.991251823013 | 0.999914429865 | 99.9755288776 |
| short_core_k4 | 4.44210747151 | 2.29187901206 | 0.515944070863 | 0.9913562848 | 0.999967057856 | 99.9860532748 |
| short_smooth_k4 | 4.44210739435 | 2.29187858866 | 0.51594398451 | 0.991356362897 | 0.999967063962 | 99.986054609 |

La reducción de norma del canal χ acoplado es 48.40601329 % en core_phase (aproximadamente48,4 % en las tres ventanas). Este cociente de un prefijo no decide la puerta causal final de τ160. El canal χ libre también satisface ahora las tres ventanas; en el original del mismo tiempo no las satisfacía. Los otros cuatro canales acoplados no son suficientes individualmente. La norma absoluta guardada de Φ inducida por el canal χ acoplado pasa de 0.00283600502886 a 0.000911719227697 (razón 0.321480116721), sin identificar una fracción de retorno puro χ→Φ→χ.

El comparador localiza 99.9897795528 % de la diferencia cuadrática de χ en 10≤r<20; multipolos ℓ2=91.0153224665 % y ℓ4=8.98467753346 %. La rotación descriptiva no intervino en la puerta.

## Todos los canales: signos y cancelaciones conservados

Las normas aisladas no se suman como potencias independientes. La reducción cuadrática es un contraste pasivo condicionado a las historias adquiridas; un valor negativo significa que retirar ese canal empeora el residuo en ese contraste. Las matrices Gram originales de las dos ventanas cortas permanecen en el JSON.

| Ventana | Familia | Canal | Norma original (%) | Norma mixta (%) | Proyección mixta | Coseno mixto | Reducción cuadrática (%) |
|---|---|---|---:|---:|---:|---:|---:|
| core_phase | raw | inicial_libre | 0.001124154696 | 0.001123012946 | 8.253575522e-06 | 0.01699135105 | 0.001627119645 |
| core_phase | raw | operador_chi | 6.677602296 | 2.523782061 | 0.9925821171 | 0.9092538394 | 79.34761254 |
| core_phase | raw | transferencia_chi | 0.01692947073 | 0.00918390951 | -0.002973557379 | -0.7485473434 | -0.5962895016 |
| core_phase | raw | densidad_rho | 3.773414393 | 0.843413499 | 0.008205344077 | 0.02249193375 | -11.66776503 |
| core_phase | raw | reaccion_chi | 0.9459610972 | 0.2129503839 | 0.002177861079 | 0.02364407304 | -0.4128572884 |
| core_phase | coupled | inicial | 0.0009961957231 | 0.001000754743 | 4.403384566e-06 | 0.01017254231 | 0.0008619393021 |
| core_phase | coupled | operador_Phi | 0.02599063448 | 0.02607218396 | 0.003156380334 | 0.2798868299 | 0.6185582159 |
| core_phase | coupled | operador_chi | 4.442143887 | 2.291879127 | 0.991251823 | 0.9999144299 | 99.97552888 |
| core_phase | coupled | transferencia_Phi | 0.008903585956 | 0.01029801447 | 0.002643780141 | 0.5935296022 | 0.5267719175 |
| core_phase | coupled | transferencia_chi | 0.01350486866 | 0.01531106029 | 0.002943356902 | 0.4444349516 | 0.5842853721 |
| short_core_k4 | raw | inicial_libre | 0.001123796881 | 0.001122651519 | 8.309947509e-06 | 0.01711200619 | 0.001638406738 |
| short_core_k4 | raw | operador_chi | 6.677563251 | 2.52378193 | 0.9926867716 | 0.9093017451 | 79.35597154 |
| short_core_k4 | raw | transferencia_chi | 0.01692943313 | 0.009183841313 | -0.002973875998 | -0.7485935853 | -0.5963533686 |
| short_core_k4 | raw | densidad_rho | 3.773324789 | 0.8430775568 | 0.008100481635 | 0.022212167 | -11.67954178 |
| short_core_k4 | raw | reaccion_chi | 0.9459579398 | 0.2129500104 | 0.002178331359 | 0.02364797156 | -0.4128498494 |
| short_core_k4 | coupled | inicial | 0.0009933381487 | 0.0009976903842 | 4.414010879e-06 | 0.01022787071 | 0.0008641771733 |
| short_core_k4 | coupled | operador_Phi | 0.01058604277 | 0.01078619947 | 0.003051255697 | 0.6539699193 | 0.6080742235 |
| short_core_k4 | coupled | operador_chi | 4.442107472 | 2.291879012 | 0.9913562848 | 0.9999670579 | 99.98605327 |
| short_core_k4 | coupled | transferencia_Phi | 0.008854964804 | 0.01025543193 | 0.00264546612 | 0.5963426405 | 0.5271252802 |
| short_core_k4 | coupled | transferencia_chi | 0.01347132285 | 0.01528147586 | 0.002942323129 | 0.4451154638 | 0.5840950893 |
| short_smooth_k4 | raw | inicial_libre | 0.001112715276 | 0.001090303847 | 8.227463242e-06 | 0.01744479663 | 0.001623249304 |
| short_smooth_k4 | raw | operador_chi | 6.6775632 | 2.523781545 | 0.9926868503 | 0.9093017218 | 79.35596225 |
| short_smooth_k4 | raw | transferencia_chi | 0.01692943313 | 0.009183841313 | -0.00297387753 | -0.7485937784 | -0.5963536759 |
| short_smooth_k4 | raw | densidad_rho | 3.773324789 | 0.8430775568 | 0.008100485765 | 0.02221217261 | -11.6795478 |
| short_smooth_k4 | raw | reaccion_chi | 0.9459579398 | 0.2129500104 | 0.0021783325 | 0.02364797787 | -0.4128500579 |
| short_smooth_k4 | coupled | inicial | 0.0009807843947 | 0.0009611516859 | 4.331529315e-06 | 0.01041829932 | 0.000849020088 |
| short_smooth_k4 | coupled | operador_Phi | 0.01058604167 | 0.01078619844 | 0.003051257206 | 0.6539701364 | 0.6080745245 |
| short_smooth_k4 | coupled | operador_chi | 4.442107394 | 2.291878589 | 0.9913563629 | 0.999967064 | 99.98605461 |
| short_smooth_k4 | coupled | transferencia_Phi | 0.008854964801 | 0.01025543193 | 0.002645467483 | 0.5963427944 | 0.5271255518 |
| short_smooth_k4 | coupled | transferencia_chi | 0.01347132285 | 0.01528147586 | 0.002942324641 | 0.4451155779 | 0.5840953894 |

## Alcance y siguiente investigación

La corrección reduce el error frente al original, pero deja un residuo radial χ suficiente para superar el 2 % a τ80. Esta versión no autoriza el horizonte160. Se conserva su negativo junto con el K4 de tres campos fallido y el CP12 original, sin relajar criterios, ajustar fase, repetir tramos o lanzar otra corrección.

Una nueva evolución requerirá una pregunta y una derivación/prerregistro nuevos sobre el residuo identificado. Quedan pendientes la causalidad final de160 y las pruebas justificadas de convergencia adicional, referencia, estabilidad y robustez. No se reconstruyeron grupos del núcleo completo sin sus historias de campos, no se estimó una fracción pura del bucle y no se afirmó orden de convergencia a partir de dos mallas. Toda la evidencia es matemática o numérica del modelo M2, sin validación física experimental.

Entradas y salida verificables: `checkpoints/CP12/continuacion_20261018/negativo_espacial_tau0080/`. La conservación permanente del diagnóstico se documenta en `CONSERVACION_DIAGNOSTICO.json` junto a esos archivos. Main sigue en CP11 y PR#2 en borrador.
