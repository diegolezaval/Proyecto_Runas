# CP12 mixto: crecimiento medido del error de fases χ

Aritmética de las comparaciones guardadas y auditadas; cero pasos M2. Los factores comparan tiempos sucesivos con las mismas dos mallas. No son órdenes de convergencia espacial ni certifican una ley exponencial o una predicción hasta τ160.

| τ | Error χ (%) | Cambio (puntos porcentuales) | Factor frente a anterior | Cinco puertas ≤2 % |
|---|---:|---:|---:|---|
| 8 | 0.0339938620 | — | — | Pasan |
| 16 | 0.0248627697 | -0.0091310923 | 0.73138997 | Pasan |
| 24 | 0.0375399569 | 0.0126771872 | 1.50988636 | Pasan |
| 32 | 0.1432151757 | 0.1056752188 | 3.81500640 | Pasan |
| 40 | 0.3841277316 | 0.2409125559 | 2.68217198 | Pasan |
| 48 | 0.7508082788 | 0.3666805472 | 1.95457973 | Pasan |
| 56 | 1.1827210176 | 0.4319127389 | 1.57526369 | Pasan |
| 64 | 1.6121229097 | 0.4294018920 | 1.36306271 | Pasan |
| 72 | 1.9942703120 | 0.3821474023 | 1.23704607 | Pasan |

Un factor que disminuye puede acompañar a un error que sigue aumentando. Cada frontera conserva su propia decisión con el límite original del 2 %. Superar ese límite suspende la continuación correspondiente, aunque el crecimiento relativo se reduzca. El acuerdo entre mallas y estos incrementos son evidencia numérica de M2; no validación experimental.

Fuentes exactas y hashes: `CRECIMIENTO_ERROR_CHI_MIXTO_CP12_20261018.json`.
