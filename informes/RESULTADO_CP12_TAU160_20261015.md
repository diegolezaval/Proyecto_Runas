# CP12 · τ160 reproducido y presupuesto causal evaluado

La evolución original está conservada y auditada hasta τ160. Pasan las **44 comprobaciones finales** y hay igualdad exacta con CP10 en ambas mallas: q, v, condiciones iniciales, las 401 filas observadas y los contadores accepted, nfev, maxe y maxq. El último checkpoint científico aceptado sigue siendo CP11; CP12 permanece abierto.

La discrepancia espacial de χ en espacio de fases es **5,126390964 %**, superior a la puerta original del **2 %**. El resultado físico continúa como `REFINAMIENTO_PENDIENTE`.

## Reproducción y conservación

| Malla | Pasos aceptados | Evaluaciones | Deriva máxima de energía | Deriva máxima de carga |
|---|---:|---:|---:|---:|
| 0.125 | 28630 | 345436 | 4.2032843872163994e-10 | 2.6645352591003757e-15 |
| 0.0625 | 28753 | 346912 | 4.040165979546373e-10 | 2.1094237467877974e-15 |

NPZ SHA-256 `22078538ebba2e948b433b0ab946ee034be132b27f7e72ca1ee30540323b2413`. Cápsula íntegra: 84575117 bytes; SHA-256 `1c13b199592dc91ab2ec3ac382d4bd73736ba5e2c577438882de8932a6ec69c9`. Se recuperó independientemente y se verificaron todos sus hashes antes del auditor original, que ejecutó cero pasos M2. Las fronteras de ocho unidades anteriores se conservan. La recuperación numérica pública completa sigue en τ80, con su NPZ original exacto y 145/145 JSON; las cápsulas científicas completas posteriores permanecen privadas.

## Tres ventanas originales

El lector original aplica simultáneamente proyección firmada ≥0,8, coseno ≥0,8 y reducción cuadrática al retirar una respuesta ≥0,5. El canal **operador_chi acoplado** y el grupo **operador_total** cumplen en las tres ventanas. Para operador_chi:

| Ventana | Proyección firmada | Coseno | Reducción cuadrática offline | Cumple |
|---|---:|---:|---:|---|
| core_phase | 0.997255202 | 0.999913577 | 0.999820545 | Sí |
| short_core_k4 | 0.997419468 | 0.999991898 | 0.999977220 | Sí |
| short_smooth_k4 | 0.997419505 | 0.999991901 | 0.999977226 | Sí |

Estas métricas describen respuestas lineales offline condicionadas a las dos historias CP10 y al spline fijo. Todavía falta ensayar una evolución corregida autoconsistente y comprobar las puertas físicas.

El operador χ libre queda como resultado negativo:

| Ventana | Proyección firmada | Coseno | Reducción cuadrática offline | Cumple |
|---|---:|---:|---:|---|
| core_phase | 1.079276754 | 0.756818901 | 0.124877774 | No |
| short_core_k4 | 1.079463913 | 0.756869037 | 0.124816218 | No |
| short_smooth_k4 | 1.079463970 | 0.756869019 | 0.124816020 | No |

El cierre de la identidad χ en toda la caja es 0.000005641671118181181 (libre) y 0.000005437128410420561 (acoplado), por debajo del límite 0,001. Los términos cruzados se conservan completos. En core_phase, las potencias diagonales libres suman 2,630061648 veces la norma cuadrática observada y los cruces aportan −1,630063212; el total es 0,999998436. Las cancelaciones impiden asignar causalidad a una magnitud aislada.

El primer cruce sostenido del operador χ acoplado es τ=16,8 en las tres ventanas, con umbral del 1 % de la norma final y tres muestras consecutivas. La respuesta inducida en Φ termina con norma 0.0002971472850210229. El propagador acoplado contiene el Jacobiano completo; su diferencia con el propagador libre mezcla cambios diagonales y acoplamientos. Sigue pendiente una separación adicional si se desea cuantificar un bucle puro χ→Φ→χ.

## Fallo de serialización conservado

Después de conservar τ160, el lector original terminó con TypeError al serializar booleanos NumPy. Se conservó, recuperó y verificó ese fallo antes de repetir la lectura. Una extracción independiente ejecutó el mismo lector y los mismos criterios; la adaptación convierte exclusivamente seis valores NumPy false en booleanos Python false al escribir JSON. Ningún número cambió. Los hashes científicos y las 14 fuentes originales siguen idénticos; las 44 comprobaciones pasan antes y después. La lectura y la publicación ejecutan cero pasos M2. Se conserva el fallo original y la salida posterior sin sobrescrituras.

## Puerta de continuidad

La atribución condicionada autoriza revisar el prerregistro de corrección existente. El fundamento matemático y físico, las pruebas autoconsistentes de convergencia, conservación, estabilidad y robustez y la conservación de resultados negativos siguen siendo requisitos. El cierre del presupuesto matemático no concede el cierre de CP12. M2, Θ, ambas mallas, DOP853, tolerancias, observadores, spline y puerta del 2 % permanecen originales. Main y PR #2 permanecen intactos.

Comprobantes: `checkpoints/CP12/continuacion_20261014/tau0160/AUDITORIA_FRONTERA_GUARDADA.json`, `checkpoints/CP12/continuacion_20261014/tau0160/diagnostico/RESULTADOS_LECTOR_ORIGINAL.json` y `checkpoints/CP12/continuacion_20261014/tau0160/diagnostico/ALCANCE_Y_PUERTAS.json`.
