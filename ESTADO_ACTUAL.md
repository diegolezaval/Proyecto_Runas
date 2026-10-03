# Estado actual · CP10_MEDIADOR_ESPACIOTEMPORAL

> Vista generada por herramientas/generar_continuidad.py. Editar las fuentes JSON; no este archivo.

Proyecto: **4.2.0-dev10**. Modelo: **M2**. Último checkpoint científico: **CP10_MEDIADOR_ESPACIOTEMPORAL**.

**Completadas:** E00, E01, C0. **Parciales:** E02, E03, E04, C7, RES0, RES1.

**Puerta no radial vigente:** REFINAMIENTO_PENDIENTE. **Cálculos numéricos activos:** 0. **Primordiales/dispositivos completos:** 0.

Las etapas conservan sus puertas; completar una campaña no equivale a completar una etapa. La evidencia reproducible prevalece ante una discrepancia documental.

## Siguiente trabajo científico

- Diagnosticar el operador radial y las componentes cortas de chi sobre los estados CP10 guardados; prerregistrar el próximo control espacial o una discretización contrastada, sin relajar la puerta ni repetir las catorce evoluciones cerradas.
- RES0/RES2: paquete finito, retroacción y contabilidad de recursos tras estabilidad útil
- C7: nodos/vórtices o candidatos dinámicos con recursos

## Estados de origen y continuación

- Estado CP04 terminado de origen para nuevas perturbaciones: [validacion/P06/preparacion/w7.20_h0.100_dt0.0020_R1300_T1200_estado.npz](validacion/P06/preparacion/w7.20_h0.100_dt0.0020_R1300_T1200_estado.npz).
- Último estado no radial terminado; no repetir ni prolongar sin protocolo nuevo: [validacion/P06/no_radial/CP10/espacial_h00625__51eec4febb8920be17635aa90d6025d512bebc507c4babba03852872ca163b30/dop853e10_L4_h0.062_dt0.0200_R220_eps0.020_T160_estado.npz](validacion/P06/no_radial/CP10/espacial_h00625__51eec4febb8920be17635aa90d6025d512bebc507c4babba03852872ca163b30/dop853e10_L4_h0.062_dt0.0200_R220_eps0.020_T160_estado.npz).
- Diagnóstico guardado después de la puerta: [validacion/P06/no_radial/CP10/comparacion_final__db37e89de7f122c528ea607fd13272a54e1151406fbc140e4c509c49d4aca654/resultados.json](validacion/P06/no_radial/CP10/comparacion_final__db37e89de7f122c528ea607fd13272a54e1151406fbc140e4c509c49d4aca654/resultados.json).
- Tiempo no radial final registrado: 160.

## Qué no repetir

- E00 salvo una condicion de reapertura documentada.
- E01 salvo causa de reapertura registrada.
- C0 salvo condición explícita de reapertura.
- Campañas cerradas CP03/CP04 y ocho continuaciones VV de CP06.
- Cuatro evoluciones DOP853 h=.5 (dos tolerancias), h=.25 y h=.125 finalizadas a tau=160; dispersión lineal y su verificación cerradas.
- Dos evoluciones CP10 temporal_h0125 y espacial_h00625 terminadas hasta tau=160, con recibos y comparación final. Reutilizar sus estados; no volver a evolucionarlas sin una pregunta y protocolo nuevos.

## Resultados vigentes y límites

- C0: [validacion/P04/exclusiones/resultados.json](validacion/P04/exclusiones/resultados.json) — Alcance en el archivo fuente.
- E02: [validacion/validez/resultados.json](validacion/validez/resultados.json) — Alcance en el archivo fuente.
- E03_RES0: [validacion/P06/rama/resultados.json](validacion/P06/rama/resultados.json) — Alcance en el archivo fuente.
- E04_RES1: [validacion/P06/preparacion/resultados.json](validacion/P06/preparacion/resultados.json) — Alcance en el archivo fuente.
- excitation_diagnostic: [validacion/P06/preparacion/exceso_energia.json](validacion/P06/preparacion/exceso_energia.json) — Alcance en el archivo fuente.
- linear_access: [validacion/P06/acceso_lineal/puerta_decision.json](validacion/P06/acceso_lineal/puerta_decision.json) — SUBPREGUNTA_LINEAL_COMPLETADA.
- nodal_phase: [validacion/P04/C7/puerta_fase_sin_nodos.json](validacion/P04/C7/puerta_fase_sin_nodos.json) — COMPLETADA.
- nonradial_latest_completed_comparison: [validacion/P06/no_radial/CP10/comparacion_final__db37e89de7f122c528ea607fd13272a54e1151406fbc140e4c509c49d4aca654/resultados.json](validacion/P06/no_radial/CP10/comparacion_final__db37e89de7f122c528ea607fd13272a54e1151406fbc140e4c509c49d4aca654/resultados.json) — REFINAMIENTO_PENDIENTE.
- mediator_diagnostic_before_CP10: [validacion/P06/no_radial/CP10/diagnostico_guardado__0cc9af79f3804e54e2f65309e9fad57934b04c55536c5dd07519c2bacc87ea47/diagnostico.json](validacion/P06/no_radial/CP10/diagnostico_guardado__0cc9af79f3804e54e2f65309e9fad57934b04c55536c5dd07519c2bacc87ea47/diagnostico.json) — Alcance en el archivo fuente.

## Etapas y puertas

| Etapa | Estado | Puerta registrada |
|---|---|---|
| E00 | COMPLETADA | Cierre histórico conservado |
| E01 | COMPLETADA | Cierre histórico conservado |
| E02 | PARCIAL | NO_SUPERADA; SUBRESULTADOS_VERIFICADOS |
| E03 | PARCIAL | ETAPA_GENERAL_PARCIAL; PUERTA_FINITA_EN_RESULTADO_CP10 |
| E04 | PARCIAL | ETAPA_GENERAL_PARCIAL; PUERTA_FINITA_EN_RESULTADO_CP10 |
| E05 | BLOQUEADA | Consultar expediente |
| E06 | BLOQUEADA | Consultar expediente |
| E07 | BLOQUEADA | Consultar expediente |
| E08 | BLOQUEADA | Consultar expediente |
| E09 | BLOQUEADA | Consultar expediente |
| E10 | BLOQUEADA | Consultar expediente |
| E11 | BLOQUEADA | Consultar expediente |
| E12 | BLOQUEADA | Consultar expediente |
| E13 | BLOQUEADA | Consultar expediente |
| E14 | BLOQUEADA | Consultar expediente |
| C0 | COMPLETADA | SUPERADA |
| C1 | BLOQUEADA | Consultar expediente |
| C2 | BLOQUEADA | Consultar expediente |
| C3 | BLOQUEADA | Consultar expediente |
| C4 | BLOQUEADA | Consultar expediente |
| C5 | BLOQUEADA | Consultar expediente |
| C6 | BLOQUEADA | Consultar expediente |
| C7 | PARCIAL | SUBCLASE_SIN_NODOS_DESCARTADA; C7_NO_SUPERADA |
| C8 | BLOQUEADA | Consultar expediente |
| C9 | BLOQUEADA | Consultar expediente |
| C10 | BLOQUEADA | Consultar expediente |
| RES0 | PARCIAL | NO_SUPERADA; SUBRESULTADOS_VERIFICADOS |
| RES1 | PARCIAL | ETAPA_GENERAL_PARCIAL; PUERTA_FINITA_EN_RESULTADO_CP10 |
| RES2 | BLOQUEADA | SUBPREGUNTA_LINEAL_COMPLETADA; PUERTA_FUNCIONAL_NO_SUPERADA |
| RES3 | BLOQUEADA | Consultar expediente |
| RES4 | BLOQUEADA | Consultar expediente |
| RES5 | BLOQUEADA | Consultar expediente |
| M3 | BLOQUEADA | Consultar expediente |

Informe de esta entrega: [informes/ENTREGA_10_MEDIADOR_ESPACIOTEMPORAL.md](informes/ENTREGA_10_MEDIADOR_ESPACIOTEMPORAL.md).

Índice derivado de trazabilidad: [trazabilidad/arquitectura/indice_trazabilidad.json](trazabilidad/arquitectura/indice_trazabilidad.json).

Entrada y comandos: [LEEME.md](LEEME.md). Autoridad y límites: [ARQUITECTURA.md](ARQUITECTURA.md).
