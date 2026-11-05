# CP12/P3: continuación desde τ12,8

**CP11 aceptado; CP12 abierto; P3 sin validar. La descarga pública deτ12,8 pasó305 cargas y30+14 controles originales con el compilador real restaurado, sin construcciones/pasos DOP853.** [Informe y alcance](informes/CIERRE_AUDITORIAS_Y_REANUDACION_P3_20261104.md).

| Referencia | Estado comprobado |
| --- | --- |
| Última frontera completa positiva | τ8 |
| Transporte vigente | τ12,8; no es una frontera completa |
| Próxima frontera | τ16, pendiente de todas sus puertas |
| Adjunto vigente | 711173125 |
| Tamaño | 229945240 bytes |
| SHA256 | a58969092423501904f45bfa9e6143d41afac19970c9b61fa0222beb9e13c1d3 |
| Cargas / controles actuales | 305 /30 deτ8 +14 deτ12,8, positivos |
| Compilador | Ubuntu13.3.0 original; respaldo público711636597 |
| Control del proceso nuevo | Nativo y público recuperados; adjunto711636683 |
| Asignación nueva | p3_128_a16_20261104b; reserva previa a activación |
| Repeticiones9,6→11,2 y11,2→12,8 | Prohibidas; conservar el transporte más reciente |
| Transferencia histórica116/308 | Incompleta; no es inventario del proyecto |

## Recuperar y continuar

En [la Release experimental](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027), identificar CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_TRANSPORTE_000128_P3_112_A16_20261030.zip.

[Origen](checkpoints/CP12/p3_20261018/reanudacion_t128_20261104/ORIGEN.json) · [Auditorías actuales](trazabilidad/cierre_auditorias_20261104/auditoria_t128/RESULTADO.json) · [Restauración exacta](checkpoints/CP12/p3_20261018/reanudacion_t128_20261104/RESTAURACION_EXACTA.json) · [Capacidad](checkpoints/CP12/p3_20261018/reanudacion_t128_20261104/capacidad/ACEPTACION_COMBINADA.json) · [Reserva](checkpoints/CP12/p3_20261018/reanudacion_t128_20261104/ASIGNACION_128_A16.json).

El [registro canónico](checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json) distingue trabajador, actividad, transporte recuperable y frontera científica. Comprobarlo junto al head antes de iniciar otro proceso. No duplicar la asignación vigente. La asignación anterior quedó inaccesible: no reactivarla ni recrear su archivo privado de publicación.

En16 se exige recuperación independiente, cinco métricas espaciales≤.02 y todos los demás umbrales originales. Un negativo suspende esa versión. Un respaldo correcto no valida P3 ni cierra CP12.

## Antecedentes

[Recuperación12,8](informes/RECUPERACION_P3_T128_20261104.md) · [Guía histórica11,2](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/README.md) · [Aceptación global ya publicada](trazabilidad/continuidad_20261104/ACEPTACION_GLOBAL_GITHUB.json).

No reanudar P2 ni repetir CP10, CP12 original, CP04, F0…F5 o tramos P3 cerrados. Main mantiene CP11. [Panorama](informes/PANORAMA_GLOBAL_Y_PRIORIDADES_20261029.md) · [Relevo actualizado](CONTINUAR_EN_CHAT_NUEVO.md).
