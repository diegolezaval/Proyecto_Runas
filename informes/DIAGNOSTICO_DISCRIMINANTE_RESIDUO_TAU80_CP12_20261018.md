# CP12: residuoτ80, mecanismos separados y propuesta a contrastar

Se recuperó la evidencia posterior completa del negativo mixto y se repitió únicamente la auditoría de recuperación28, con cero pasos. No apareció progreso posterior ni actividad propia de M2; main sigue en CP11 y PR2 en borrador. Los diagnósticos nuevos se registraron en3f2f289 y la enmienda de ocupación nulaℓ4 en f2dd601 antes de ejecutarse. Fuentes históricas, parámetros, estados y recibos permanecen idénticos.

## Qué está demostrado y qué falta separar

| Mecanismo | Evidencia conservada o nueva | Alcance |
|---|---|---|
| Operadorχ acoplado | Suficiente en las tres ventanas; proyección≥.99125, coseno≥.99991, retirada cuadrática≥99.975% | Atribución causal condicionada a las dos historias; no universalidad ni un bucle puro |
| Geometría radial de K4 | Derivación del término h² y contraste fabricado; orden cercano a2 al refinar | Defecto formal demostrado, sin asumir que domina la trayectoria |
| Dispersión finita | 99.63018% del defecto80 está en k>8; referencias de frecuencias radiales ocupadas | Firma compatible con dispersión; la exposición libre no es una trayectoria autoconsistente |
| Acoplamientoχ↔Φ | Contraste de respuestas guardadas, con normas y cruces | Modifica y cancela componentes; no es una amplificación escalar simple |
| Fuente no lineal | Canales negativos y Gram conservados; transferenciaχ acoplada insuficiente | No se justifica cambiar la fuente a partir de una norma instantánea |
| Preparación | La derivada usada para la semilla cuadrupolar es C1 entre nudos del spline | Regularidad limitada demostrada; su papel dominante en el defecto80 no está probado |
| Interpolación de comparación | Paridad y restricción inversa conservan el fallo del2% | El cruce no se explica por esas dos sensibilidades; otras reconstrucciones no son una puerta nueva |
| Truncamiento angular y caja | Fuente omitida y colas medidas sobre estados guardados | Faltan evoluciones de referencia para cerrar independencia angular/de caja |

## Espacio, tiempo e interpolación

χ en fases: original del comparador 2.31190799095%; extensión por paridad 2.31190799095%; restricción fina→gruesa 2.3302294568%. No se ajusta fase ni se cambia la puerta.

En80, la respuesta del operadorχ acoplado tiene99,9988159% de su diferencia cuadrática en10≤r<20, frente a una fracción1,9149e-8 en0≤r<2. Esto localiza la respuesta final; no prueba que una perturbación antigua del origen no haya propagado hacia la banda. El error observado se distribuye enℓ2≈91,0153% yℓ4≈8,9847%.

| τ | Error fasesχ (%) | Fracción de potencia del defecto k>8 (%) | k>12 (%) |
|---|---:|---:|---:|
| 0 | 0.001122314926 | 87.62690584 | 83.48510335 |
| 8 | 0.03399386198 | 5.532557721 | 5.53038479 |
| 16 | 0.02486276969 | 1.220674525 | 0.8061413381 |
| 24 | 0.03753995687 | 61.07452486 | 4.926418718 |
| 32 | 0.1432151757 | 95.15667359 | 5.335805861 |
| 40 | 0.3841277316 | 98.5517318 | 24.8659554 |
| 48 | 0.7508082788 | 99.2801016 | 46.49791121 |
| 56 | 1.182721018 | 99.52322785 | 55.12065192 |
| 64 | 1.61212291 | 99.62253043 | 57.00555065 |
| 72 | 1.994270312 | 99.64571289 | 55.51291602 |
| 80 | 2.311907991 | 99.63018016 | 51.9749586 |

## Acoplamiento, signos y regularidad

El canalχ libre tiene norma 0.0252378206053; el acoplado 0.0229187912707; su diferencia tiene norma 0.0106533159124, con la misma normalización inicial. El cruce2⟨libre,diferencia⟩/‖defecto‖² es -0.421278141206. El acoplamiento reduce la norma total del canal en este contraste y altera su dirección; no se infiere de ello una estabilidad general. El Gram completo del núcleo se reconstruyó con los vectores guardados, sin repetir observadores.

El máximo salto de segunda derivada de la perturbaciónχ inicial es2,3242704654e-4, situado enr8,85; el de su velocidad es2,9178098292e-3, enr13,65. El spline de fondo esC2 y su derivada produce una perturbaciónC1 donde esos saltos no se anulan. La extensión central sigue siendo par y regular. No se suaviza ni sustituye CP04. No se presume ventaja global de un orden alto para estos datos.

En la fuente no lineal deΦ, la fracción cuadrática omitida porL4 es≈1,72e-4 al inicio y≈2,1–2,3e-5 en80. Enχ es≈3,42e-14 al inicio y≈5,10e-10 en80. Son fracciones de **fuente instantánea**, no errores de trayectoria. El error de la pareja espacial vive dentro del mismo modeloL4; estos datos no cierran la convergencia angular del M2 completo.

## Residuo geométrico y frecuencias ocupadas

La expansión exacta está en `checkpoints/CP12/residuo_tau80_20261018/DERIVACION_GEOMETRIA.md`. Para los campos fabricados centrados, los últimos órdenes medidos son≈2,0010 paraℓ2 y≈2,0053 paraℓ4. Al sustraer el término h² derivado, los residuos de esos dos modos bajan aproximadamente con h⁴ antes de redondeo. El comportamiento deℓ0 y del origen se conserva por separado; la expansión a r fijo no demuestra orden uniforme de la primera celda. Los perfiles de banda pasan por un régimen de cancelación entre términos h²/h⁴, lo que impide estimar orden global a partir de sólo dos mallas.

La ocupación inicialℓ2 concentra99% de la norma cuadrática en k≤1,328. En80,ℓ4, inicialmente nulo, tiene99% en k≤12,252 y99,9% en k≤14,723. El defecto relativo puede concentrarse en una cola corta aunque la mayor parte del campo sea suave.

| ℓ | Composición positiva | Exposición de fase del espectro80 | RMS δω entre mallas |
|---|---|---:|---:|
| 2 | P1 | 0.0519308566953 | 0.0019679083757 |
| 2 | P2 | 0.0333102773672 | 0.00067327253491 |
| 2 | P3 | 0.016600202812 | 0.000248785287981 |
| 2 | P4 | 0.00761212701201 | 0.000102447276338 |
| 4 | P1 | 0.602398500857 | 0.0203476827652 |
| 4 | P2 | 0.318927818521 | 0.00729279382336 |
| 4 | P3 | 0.166396950912 | 0.00291142568359 |
| 4 | P4 | 0.089967348534 | 0.00130060566438 |

Estas exposiciones son modelos lineales descriptivos con pesos medidos; no son predicciones de la puerta física. P3/P4 **empeoran** la exposición inicialℓ2 frente aP2:5,1208e-5→7,4503e-5→7,6984e-5. Ese resultado negativo se conserva. No existe una mejora universal de todas las frecuencias. Parseval de las nuevas proyecciones pasa2e-11.

## Comparación de soluciones y elección de una hipótesis mínima

Se descarta presentar K6/K8 como operadores radiales globales de orden seis/ocho: añadir h⁴A2³ no elimina el término geométrico h². Una discretización de masa/potencial de mayor orden exige cambiar y comprobar conjuntamente la acción acoplada; es una alternativa más amplia y no se implementa como sustitución aislada de la fuerza. Retocar fuente o preparación tampoco está justificado por la suficiencia actual del operadorχ.

Se propone contrastar **una sola composición P3**, que añade el primer término interior omitido, h⁴A2³/90, con coeficiente derivado e independiente deχ. Conserva masa, potencial, datos iniciales, Φ-FV y las simetrías actuales. La elección persigue contrastar la dispersión del operador suficiente en el régimen ocupado; la mejora de la exposición80 apoya el ensayo, sin aprobarlo ni garantizar160. P3 es la extensión algebraica mínima deP2 con esa cancelación. No se lanza P4 automáticamente.

Antes de física se requieren una rama experimental, derivación y registro ejecutable, gradiente/acción/carga/trabajo, identidad de defecto, matrices/resolventes independientes y referencia congelada certificada. Serán **controles del nuevo candidato**, sin repetir ni reasignar los A–D cerrados del viejoP2. Sólo si pasan se registrará un piloto nuevo desde los datos originales; jamás desde80. Energías2e-4, carga1e-9, cinco métricas2% y demás puertas permanecen intactas. La tercera malla, sensibilidad de interpolación, referencia angular/de caja, estabilidad y robustez siguen pendientes antes de cualquier aceptación.

Los resultados completos D1/D2 y espectros están en la cápsula documentada por `CONSERVACION_D1_D2.json`; su resumen y hashes permiten reproducir la lectura. CP12 abierto, CP11 aceptado. Evidencia numérica deM2, sin validación física experimental.
