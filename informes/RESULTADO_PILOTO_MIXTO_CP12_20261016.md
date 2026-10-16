# CP12 · Piloto autoconsistente Φ-FV / χ-K4 hasta τ=8

**Resultado: piloto conservado, recuperado y auditado; se desbloquea la continuación del mismo ensayo. CP12 permanece abierto y CP11 sigue aceptado.** La evolución 8→16 comenzó únicamente después de obtener el certificado permanente positivo de τ8.

Se recuperó el transporte posterior τ3,2 y se continuó su paso DOP853 existente. No se repitió ese prefijo, A–D ni la evolución original CP12/CP10. M2, Θ, datos iniciales, mallas h=.125/.0625, R220, L4, ε=.02, DOP853, tolerancias y observadores mantienen sus fuentes y configuración originales. Los reinicios en fronteras de ocho unidades siguen el protocolo registrado.

La cápsula completa τ8 tiene **229 600 254 bytes**, 136 archivos de carga útil y SHA256 `1ec03795f13feee243498100ffdfc505ea101ae48ace51d65bf028d30ccab561`. Se recuperó por separado, se verificaron cobertura, tamaños y hashes y pasó la auditoría de **28 comprobaciones**, sin pasos M2. La nueva herramienta `recuperar_frontera.py` repitió positivamente la recuperación en otra raíz conservando el estado y recibo; esta comprobación de recuperación tampoco evolucionó M2. La independencia corresponde a la recuperación/recarga en otra raíz y proceso, con las mismas fuentes científicas autenticadas.

| Magnitud hasta τ8 | h=.125 | h=.0625 | Puerta |
|---|---:|---:|---:|
| Observaciones físicas por malla | 21 | 21 | Cadencia original .4 |
| Pasos aceptados | 1483 | 1483 | Contadores conservados |
| Evaluaciones DOP853 cerradas | 18266 | 18266 | Contadores conservados |
| Máxima deriva E FV | 3.477215182e-9 | 8.390481643e-10 | ≤2e-4 |
| Máxima deriva E mixta | 5.711708884e-11 | 5.701805694e-11 | ≤2e-4 |
| Máxima deriva de carga | 6.661338148e-16 | 4.440892099e-16 | ≤1e-9 |

El máximo de los errores registrados de los observadores es 6.331326139e-7, frente a 1e-3. Parseval máximo: 2.038210442e-14 ≤2e-11. La identidad instantánea completa mixta da 7.547194865e-13 ≤2e-12; la simetría ponderada independiente, 5.612714941e-17 ≤2e-12. El cierre de χ en toda la caja da 8.256300109e-8/8.266781410e-8 para las familias libre/acoplada, dentro de 1e-3. Pasan las comprobaciones originales de datos iniciales, fuentes, enrutado físico/pasivo, base angular, configuración, observaciones, balances, integridad y recarga sin mutación.

La discrepancia de fases de χ medida por el observador del núcleo en τ8 es **0.0003399386198**, equivalente a **0,033993862 %**. Describe este prefijo. Las cinco métricas de convergencia originales conservan el horizonte τ160 y el límite 2 %; esta cifra no acredita su aceptación final. Tampoco evalúa aún la reducción necesaria ≥50 % del canal acoplado `operador_chi` en las tres ventanas originales.

Hashes de la frontera:

- Estado NPZ: `4c91c0c61e57635573f69c940205c465b116ce8861c2a105dd361e26f5c4603c`.
- Configuración: `0719d82ab2187b6076fa2baf6d010495bdffd59622b9ca8f56345beb19e7f182`.
- Recibo: `33ecb6eb94139c4c8152455e9a3b9dbcaf54d5c0d0cdbdcd45410e0427dfa599`.

La decisión ejecutable figura en `DECISION_PILOTO_TAU0008.json`; certificados completos y prueba del recuperador, en `FRONTERA_MIXTA_TAU0008.json` y `RECUPERACION_INDEPENDIENTE_FRONTERA_TAU0008.json`, dentro de `transporte_dop853_20261015`. Para continuar después de una interrupción, buscar primero cualquier cápsula posterior y seguir `RECUPERAR_FRONTERA.md` o `RECUPERAR.md` según corresponda. No usar un transporte anterior al último tramo cerrado para repetir ese tramo.

La continuación conserva todas las paradas y negativos, las auditorías cada ocho unidades y los transportes intermedios. En τ160 se aplicarán las cinco métricas espaciales, carga del núcleo, amplificación y lectura residual prerregistradas. La referencia adicional h=.03125 y las pruebas justificadas de convergencia, estabilidad y robustez siguen condicionadas a sus dependencias y prerregistros antes de nuevos cálculos. No se valida la corrección por completar el piloto.

Main, PR #2 abierto/en borrador, las 33 etapas y los negativos históricos permanecen intactos. Este resultado evalúa un esquema numérico de M2 y no aporta demostración experimental.
