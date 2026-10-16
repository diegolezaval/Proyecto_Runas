# CP12 · Frontera mixta τ16 y métricas espaciales de los prefijos

**La evolución mixta alcanzó τ16; su cápsula completa está guardada, recuperada y auditada con 28 comprobaciones positivas.** La continuación 16→24 comenzó después del certificado permanente. CP12 permanece abierto y CP11 sigue siendo el último checkpoint científico aceptado.

La cápsula τ16 contiene **155 archivos**, 229 872 238 bytes y SHA256 `b6d9edf7660e4d175febe8f093e3be8917bf5ce5b4cca4da84b32cdf2bd32615`. Estado NPZ: `0acb7e746b5368c620ef8cb9f92de34076daca469b85bfef0b1d1b489640f714`; recibo: `67386aa1220fd870fa5eabb2fbd4dae51f61f91f091a3b9af4c9028e9644c92d`. La configuración conserva SHA256 `0719d82ab2187b6076fa2baf6d010495bdffd59622b9ca8f56345beb19e7f182`.

| Magnitud hasta τ16 | h=.125 | h=.0625 | Puerta |
|---|---:|---:|---:|
| Observaciones por malla | 41 | 41 | Cadencia .4 |
| Pasos aceptados | 2965 | 2965 | Contadores conservados |
| Evaluaciones DOP853 cerradas | 36124 | 36124 | Contadores conservados |
| Máxima deriva E FV | 3.477215182e-9 | 8.390481643e-10 | ≤2e-4 |
| Máxima deriva E mixta | 7.069933528e-11 | 7.055889206e-11 | ≤2e-4 |
| Máxima deriva de carga | 6.661338148e-16 | 5.551115123e-16 | ≤1e-9 |

El máximo registrado de los errores de los observadores es 1.431133284e-6 ≤1e-3. Parseval: 2.038210442e-14 ≤2e-11; identidad instantánea completa: 6.009780215e-13 ≤2e-12; simetría ponderada: 2.654213579e-15 ≤2e-12. El cierre de χ en toda la caja es 1.693324858e-7/1.694666240e-7 para las familias libre/acoplada. Las fuentes, Cauchy inicial, enrutado, configuración, base angular, estados, recibo e integridad pasan la auditoría recuperada sin pasos M2.

## Lectura espacial complementaria

La lectura se registró antes de calcularla en `c0c8006685294ace20d3204b315f4e5781288355`, sobre estados ya evolucionados. Reutiliza las fórmulas originales de `diagnosticar_mediador_CP10.compare`; sólo parametriza sus dos constantes de comprobación del tiempo. Un control AST verifica identidad de las demás instrucciones. Los archivos conservan tiempos reales 8/16, spline, núcleo, pesos, normalizaciones y tratamiento original de la fase de Φ. La rotación descriptiva de χ queda excluida de aceptación.

| Métrica original, en porcentaje | Prefijo τ8 | Prefijo τ16 | Límite |
|---|---:|---:|---:|
| Error supremo de la norma | 0.00512332 % | 0.00512332 % | 2 % |
| Campo no radial de Φ | 0.02748172 % | 0.02996337 % | 2 % |
| Espacio de fases de Φ | 0.03455550 % | 0.04530524 % | 2 % |
| Campo no radial de χ | 0.03349831 % | 0.02467040 % | 2 % |
| Espacio de fases de χ | 0.03399386 % | 0.02486277 % | 2 % |

Pasan los cinco límites para ambos prefijos. La lectura ejecutó **cero pasos M2** y conservó exactamente estados y recibos. Son acuerdos de las dos mallas a tiempos concretos: no determinan un orden de convergencia ni aceptan la comparación final de τ160. La comparación con el resultado original de χ en τ160 exige completar ese mismo horizonte y las ventanas causales originales. No se deduce eliminación del mecanismo a partir de estas normas.

Los JSON `METRICAS_ESPACIALES_PREFIJO_TAU0008.json` y `METRICAS_ESPACIALES_PREFIJO_TAU0016.json` conservan cifras completas, bandas radiales, multipolos, diagnósticos descriptivos y hashes. Fuente métrica original: `41f0b56b797f9caca7601577d8db7f846d1d452e77a80940de6092be6a8fea64`; lector registrado: `3043d3f58bb0a28cac20a528d3680408191a75c18a0c36505884e0cd9eac330b`.

La limpieza administrativa registrada retiró las copias incompletas antiguas sólo después del certificado positivo de τ16; sus hashes y autorizaciones permanecen en los inventarios. Los archivos científicos y negativos siguen conservados. No se cambió el controlador activo ni se repitieron A–D o campañas certificadas.

Siguen pendientes τ160 con las cinco métricas originales, carga del núcleo y amplificación; reducción necesaria del canal acoplado `operador_chi` en las tres ventanas; y las pruebas justificadas de referencia adicional, convergencia, conservación, estabilidad y robustez con sus prerregistros. Main, PR #2 abierto/en borrador y las 33 etapas permanecen intactos. Esta evidencia es numérica dentro de M2 y no constituye demostración experimental.
