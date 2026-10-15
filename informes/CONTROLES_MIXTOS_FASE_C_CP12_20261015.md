# CP12 · Fase C mixta: matriz y resolventes

Se ejecutó exclusivamente el control publicado antes del cálculo en `b23d28701e3a9557f6b066bd8eb17be702434fc0`. No se repitieron las fases A/B ni las trayectorias originales; cero pasos M2.

Las cuatro combinaciones de malla y fondo congelado pasan 16 comprobaciones. La matriz canónica independiente usa pesos originales, Φ-FV, χ-K4 y Jacobiano medio ponderado. Su acción coincide con el backend a ≤4.379e-16 y su simetría a ≤1.994e-17. Los resolventes originales de 7 y 6 etapas pasan sus ecuaciones con residuo ≤1.087e-12, inferior a 2e-12. Los datos completos se conservan en `checkpoints/CP12/continuacion_20261014/mixto_chi_prefLight_20261015/fase_C/RESULTADO.json`.

Estos controles no son una propagación temporal ni una corrección validada. Queda el contraste congelado durante τ=.1 con los órdenes y paso originales, referencia independiente y precisión ≤1e-8 antes de juzgar el error ≤1e-3 y balance ≤2e-4. Su código y tres rutas de referencia fijas se capturan antes de ejecutarlo; no hay barrido para mejorar un resultado.

Sigue sin autorizarse una evolución física. Las puertas de energía FV y consistente, carga y 2 % permanecen intactas, al igual que K4 fallido, CP10/CP12 original τ160, las 33 etapas y todos los negativos. Main sigue CP11, PR #2 abierto/borrador y CP12 abierto.
