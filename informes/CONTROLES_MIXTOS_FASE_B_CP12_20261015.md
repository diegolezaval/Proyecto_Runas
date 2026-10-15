# CP12 · Fase B mixta: identidad de defecto y Jacobiano

Se ejecutó el código registrado antes del control en `427659b67b1e6cc259c66b5039f809876f858918`, sobre los pares CP10 iniciales y finales y cuatro perturbaciones nuevas 1e-5 por par, semilla 20261015001. No se evolucionó M2 ni se repitió la fase A. Las entradas de la cápsula negativa original permanecen íntegras.

Pasan 52 comprobaciones: identidad completa de defecto con conmutadores Φ-FV/χ-K4 reales, partición escalar de fuente, acción del Jacobiano polinómico, referencia original float128 y simetría con peso cinético (2,2,1). La invariancia D2 se comprueba sólo para las historias originales sin perturbaciones arbitrarias.

El máximo residuo normalizado de defecto es 1.714e-12 y el de la partición escalar 1.683e-12; ambos pasan el límite original 2e-12, sin cambiar escalas. El máximo residuo de la referencia extendida es 1.654e-28, y la fuga D2 física máxima es 1.783e-14. Se publican todos los residuos, incluidos los cercanos al umbral; no se mejora la cifra mediante otra escala ni se deduce una cota temporal de esos valores instantáneos.

Resultado y certificado: `checkpoints/CP12/continuacion_20261014/mixto_chi_prefLight_20261015/fase_B/`. Cero pasos físicos. Siguen pendientes la matriz canónica dispersa independiente, sus resolventes y la propagación congelada 7/6 frente a referencia controlada. No hay aún aprobado previo completo, autorización de piloto ni corrección validada. El K4 original sigue fallido; τ160 original y sus certificados no se alteran. Main sigue CP11, PR #2 abierto/borrador y CP12 abierto.
