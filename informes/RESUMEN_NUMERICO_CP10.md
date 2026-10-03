# Resumen numérico · CP10

> Vista generada por herramientas/generar_resumen_CP10.py. Las cifras y puertas proceden del resultado registrado; no editar esta tabla manualmente.

**Decisión finita: REFINAMIENTO_PENDIENTE.** Resultado fuente: [resultados.json](../validacion/P06/no_radial/CP10/comparacion_final__db37e89de7f122c528ea607fd13272a54e1151406fbc140e4c509c49d4aca654/resultados.json).

## Comparaciones

En las etiquetas, h=Δr=config.dx es el paso radial; el parámetro h del potencial M2 permanece fijo.

Núcleo r<40 y τ=160. Errores relativos a la perturbación inicial; el espacio de fases incluye la velocidad dividida por la masa del campo. Sólo se elimina la fase U(1) de Φ. χ no se alinea ni se ajusta para aceptar el ensayo.

| Magnitud | Temporal h=.125, rtol 1e-9→1e-10 (%) | Espacial h=.125→.0625, rtol=1e-10 (%) | Puerta (%) |
|---|---:|---:|---:|
| Norma temporal Φ | 4.12796949e-07 | 0.0356222583 | 2 |
| Φ: campo final | 4.35690491e-07 | 0.0706237819 | 2 |
| Φ: campo y velocidad | 2.0936558e-06 | 0.0747153223 | 2 |
| χ: campo final | 0.000278490181 | 3.61743537 | 2 |
| χ: campo y velocidad | 0.000394580033 | 5.12639096 | 2 |

Control temporal: **SUPERADO**. Control espacial: **NO SUPERADO**.

CSV derivado: [comparaciones.csv](../validacion/P06/no_radial/CP10/comparacion_final__db37e89de7f122c528ea607fd13272a54e1151406fbc140e4c509c49d4aca654/comparaciones.csv). Figura derivada: [CP10_errores_mediador.svg](../validacion/P06/no_radial/CP10/comparacion_final__db37e89de7f122c528ea607fd13272a54e1151406fbc140e4c509c49d4aca654/CP10_errores_mediador.svg).

## Balances de las dos evoluciones nuevas

| Caso | Deriva relativa E | Deriva relativa Q | Cambio relativo Q del núcleo | Amplificación máxima | Balance/retención |
|---|---:|---:|---:|---:|---|
| temporal_h0125 | 4.20328439e-10 | 2.66453526e-15 | 0.000104165701 | 1 | SUPERADO |
| espacial_h00625 | 4.04016598e-10 | 2.10942375e-15 | 0.000104602816 | 1 | SUPERADO |

Los umbrales completos están en el protocolo capturado. Conservar balances no sustituye superar las comparaciones de campo.

## Segmentos y estados recuperados

| Caso/segmento | Estado del segmento | Inicio UTC | Cierre o detección UTC | τ final guardado/recuperado |
|---|---|---|---|---:|
| temporal_h0125/1 | PAUSADA_REANUDABLE | 2026-10-02T22:38:09.912719+00:00 | 2026-10-02T22:40:02.284473+00:00 | 8.0 |
| temporal_h0125/2 | INTERRUMPIDA | 2026-10-02T22:42:34.298744+00:00 | 2026-10-03T02:44:57.533651+00:00 | 56.0 |
| temporal_h0125/3 | COMPLETADA | 2026-10-03T02:44:58.115533+00:00 | 2026-10-03T03:07:44.715909+00:00 | 160.0 |
| espacial_h00625/1 | PAUSADA_REANUDABLE | 2026-10-02T22:38:18.179220+00:00 | 2026-10-02T22:42:18.237723+00:00 | 8.0 |
| espacial_h00625/2 | INTERRUMPIDA | 2026-10-02T22:42:47.581744+00:00 | 2026-10-03T02:44:57.574850+00:00 | 24.0 |
| espacial_h00625/3 | COMPLETADA | 2026-10-03T02:44:59.516249+00:00 | 2026-10-03T03:48:06.542330+00:00 | 160.0 |

Recibo temporal_h0125: [procedencia.json](../validacion/P06/no_radial/CP10/temporal_h0125__47db345be15dc994ff09e5e67db405e90092844a156198dc4370ecc7f906d177/procedencia.json). Estado final: [dop853e10_L4_h0.125_dt0.0200_R220_eps0.020_T160_estado.npz](../validacion/P06/no_radial/CP10/temporal_h0125__47db345be15dc994ff09e5e67db405e90092844a156198dc4370ecc7f906d177/dop853e10_L4_h0.125_dt0.0200_R220_eps0.020_T160_estado.npz).
Recibo espacial_h00625: [procedencia.json](../validacion/P06/no_radial/CP10/espacial_h00625__51eec4febb8920be17635aa90d6025d512bebc507c4babba03852872ca163b30/procedencia.json). Estado final: [dop853e10_L4_h0.062_dt0.0200_R220_eps0.020_T160_estado.npz](../validacion/P06/no_radial/CP10/espacial_h00625__51eec4febb8920be17635aa90d6025d512bebc507c4babba03852872ca163b30/dop853e10_L4_h0.062_dt0.0200_R220_eps0.020_T160_estado.npz).

La detección de una interrupción no fija su instante exacto. Los recibos conservan los hashes del piloto y de los estados válidos desde los que se reanudó; no se repitió la preparación ni se inició otra vez desde τ=0.

## Distribución del error de χ en el nuevo control espacial

Fracciones de la diferencia cuadrática en espacio de fases; no son fracciones de energía física.

| Banda radial | Fracción (%) |
|---|---:|
| 0≤r<2 | 8.80171065e-06 |
| 2≤r<5 | 2.30544257e-05 |
| 5≤r<10 | 0.0155119613 |
| 10≤r<20 | 70.2841517 |
| 20≤r<40 | 29.7003045 |

| ℓ | Fracción (%) |
|---|---:|
| 1 | 3.65011984e-20 |
| 2 | 83.7623138 |
| 3 | 7.21907631e-20 |
| 4 | 16.2376862 |

## Alcance de la decisión

Deformación cuadrupolar CP04, todos los m hasta L=4, R=220, ε=.02, τ≤160; nuevos controles de espacio/tiempo y controles históricos con sus resoluciones. No perturbaciones arbitrarias ni dispositivo.

Los controles de caja, truncación angular y otras perturbaciones heredados conservan sus resoluciones históricas. No son una prueba conjunta en las nuevas mallas. La fuente de Cauchy procede de la preparación radial h=.1 de CP04; interpolarla a una malla más fina no certifica la resolución del estado fuente.

E03/E04/RES0/RES1 siguen PARCIALES. No se establece estabilidad orbital o continua, causa certificada del error, preparación primaria, apagado, retroacción, ciclo ni dispositivo. Los resultados negativos CP06–CP08 y el fallo de la nueva puerta, cuando corresponda, permanecen conservados.
