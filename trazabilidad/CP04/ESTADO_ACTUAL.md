# Estado actual · CP04 / preparación radial parcial

**COMPLETADAS:** E00, E01 y C0 en sus alcances. No repetirlas sin causa concreta. **PARCIALES:** E02, E03, RES0, E04 y RES1. **EN_PROGRESO:** investigación analítica C7 en `investigacion/C7_notas_EN_PROGRESO.md`; no hay una exclusión nueva admitida.

No queda ninguna evolución numérica lanzada a medias: las diez sensibilidades, 23 perfiles, 18 puntos capilares y ocho evoluciones radiales tienen resultados guardados. El punto M+ recuperado y todos los fallos anteriores se conservan. No volver a ejecutar estas campañas para continuar. `datos/registro_calculos.json` distingue resultados vigentes de instantáneas y diagnósticos preliminares.

La preparación radial de anchura 7.2 alcanza el subcriterio de asentamiento a t=1200: 90.13 % de carga localizada y desviación de perfil ~1.12 %. No cierra fuente, estabilidad 3D, apagado ni Reserva. Las ventanas cortas fallidas siguen registradas. El exceso energético estimado ~0.158 no se declara extraíble.

**Último estado válido para continuar:** `validacion/P06/preparacion/w7.20_h0.100_dt0.0020_R1300_T1200_estado.npz`. Contiene campos, velocidades, configuración, paso y diagnósticos. Su evolución fina sí se reanudó desde t=240. El caso largo grueso comenzó desde cero por un fallo del lanzador; está declarado y conservado como control de caja grande.

**Siguiente trabajo exacto:** verificar estabilidad y región de preparación fuera de la simetría radial, partiendo del estado guardado; especificar fuente y contactos con recursos explícitos. En C7, completar el argumento de planos móviles o comprobar íntegramente su teorema y todas las hipótesis antes de excluir cadenas. No cerrar esa nota preliminar como resultado demostrado.

Leer `informes/ENTREGA_04_PREPARACION_PARCIAL.md`, `estado_progreso.json` y capítulos 24–26. El proyecto continúa en M2. No hay primordial ni dispositivo completo, agotamiento de M2 ni habilitación de M3.
