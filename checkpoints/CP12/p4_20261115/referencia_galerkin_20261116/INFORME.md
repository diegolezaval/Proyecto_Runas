# CP12/P4 · Contraste Galerkin hasta τ160

Las cinco métricas oficiales de las tres mallas quedaron dentro del 2 % en todos los cierres.
Todos los márgenes al 2 % siguen siendo positivos al incluir la variación observada de referencia y la sensibilidad a interpolación.
En τ160, para χ en espacio de fases de la malla más fina se informa la cota empírica conjunta 0.098480 %. La lectura oficial fue 0.028900 %.

La comparación cubre la semilla CP04 registrada, R=220, L=4 y el horizonte τ160. Las variaciones son observadas entre discretizaciones y se publican por métrica en cada corte.

| τ | χ fase P4 .125 | χ fase P4 .0625 | χ fase P4 .03125 | U referencia | Sensibilidad de interpolación h=.03125 | Cota conjunta h=.03125 | Precisión h=.03125 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 120 | 0.726686 % | 0.020429 % | 0.005421 % | 0.008264 % | 0.000000 % | 0.013685 % | Cota conjunta |
| 128 | 0.791202 % | 0.047010 % | 0.043504 % | 0.064122 % | 0.000000 % | 0.107627 % | Cota conjunta |
| 136 | 0.850594 % | 0.027030 % | 0.023369 % | 0.038238 % | 0.000000 % | 0.061607 % | Cota conjunta |
| 144 | 0.911121 % | 0.061220 % | 0.059924 % | 0.094603 % | 0.000000 % | 0.154527 % | Cota conjunta |
| 152 | 0.966804 % | 0.023086 % | 0.016729 % | 0.049700 % | 0.000000 % | 0.066429 % | Cota conjunta |
| 160 | 1.023599 % | 0.036883 % | 0.028900 % | 0.069580 % | 0.000000 % | 0.098480 % | Cota conjunta |

Siguen pendientes los contrastes de estabilidad temporal de P4, caja, truncamiento angular y amplitud inicial antes de decidir el cierre de CP12.

[Resultados y presupuestos](RESULTADO.json) · [Controles previos](CONTROL_PREVIO.json) · [Prerregistro](PRERREGISTRO.md) · [Plan de estabilidad y robustez](../tercera_malla_20261116/SIGUIENTE_CONTRASTE.md)
