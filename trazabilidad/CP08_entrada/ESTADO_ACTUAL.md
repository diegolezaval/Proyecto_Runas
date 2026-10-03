# Estado actual · CP07_ACCESO_LINEAL_PARCIAL

E00, E01 y C0 COMPLETADAS e intactas. No repetirlas ni las campañas cerradas CP03/CP04, las ocho evoluciones Verlet de CP06 o las tres adaptativas terminadas de CP07.

Acceso lineal muestreado: subpregunta COMPLETADA sobre el fondo guardado ω=.9. Conversión de bandas con ganancia máxima muestreada de 0,157 %, balances, refinamientos y colocación independiente. No retroacción finita ni ciclo: RES0 PARCIAL, RES2 BLOQUEADA. Véase el capítulo 29 y `validacion/P06/acceso_lineal/puerta_decision.json`.

C7: la subpregunta de fase suave sin nodos está COMPLETADA por la prueba condicionada del capítulo 30. C7 permanece PARCIAL para nodos/vórtices y dinámica. No repetir la prueba de CP05.

Continuación no radial: control temporal del mediador superado con DOP853 hasta τ=160. El control espacial h=.5/.25 falla: diferencia de χ 4,03 % y con velocidades 5,01 %, límite 2 %. El siguiente cálculo es la nueva malla h=.125, con reinicio adaptativo de tiempo explícito si ya existe. La campaña sigue PARCIAL. Conservar todos los fallos split4/split4c, los pilotos split4b y el fallo espacial; no reanudar automáticamente configuraciones que fallaron conservación.

Comando pendiente: `OPENBLAS_NUM_THREADS=1 python herramientas/continuar_no_radial_adaptativo.py --rtol 1e-9 --atol 1e-11 --dx .125`; después `python herramientas/verificar_no_radial_m2.py`, puerta y checkpoint. Estado individual en `validacion/P06/no_radial/*_progreso.json`; inventario en `datos/registro_calculos.json`.

E02/E03/E04/RES0/RES1/C7 siguen PARCIALES; cero dispositivos completos. Informe: [ENTREGA_07_ACCESO_LINEAL_PARCIAL.md](informes/ENTREGA_07_ACCESO_LINEAL_PARCIAL.md).
