# CP12: recuperación vigente

**Actualización del 28 de octubre de 2026: P3 τ9,6 recuperado desde GitHub y auditado sin pasos.** CP11 sigue siendo el último checkpoint científico aceptado; CP12 continúa abierto y P3 no está validada. La frontera completa aprobada del ensayo sigue en τ8.

Los [tres ZIP originales](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027) están conservados íntegros. La [guía de recuperación](respaldos/CP12_20261027/LEEME.md) y los comprobantes están integrados en esta rama. El [nuevo comprobante de restauración](checkpoints/CP12/p3_20261018/retoma_20261028/auditoria_inicial/RESULTADO.json) acredita 30 controles de τ8 y 14 del transporte τ9,6, con cero intentos de construcción/avance DOP853 y todas las cargas originales idénticas.

**Siguiente puerta: conservación integrada por Releases.** El [prerregistro del 28](checkpoints/CP12/p3_20261018/retoma_20261028/PRERREGISTRO.md) exige una prueba completa de tamaño superior a la cápsula τ11,2 perdida, publicación, descarga independiente, hashes y nueva auditoría sin pasos. La publicación sola no habilita física. La repetición excepcional τ9,6→τ11,2 no ha empezado en esta retoma.

El transporte τ11,2 anterior se perdió después del fallo de cuota; sus registros siguen en el [informe de interrupción](informes/INTERRUPCION_P3_TAU11p2_20261019.md). Se mantiene la transferencia histórica de 116/308 partes como INCOMPLETA. La nueva ruta conserva sus pruebas separadas. El [registro de reanudación](checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json) conserva los antecedentes y el estado operativo.

P2 terminó con negativo espacial en τ80 y no se reanuda. No repetir CP10, CP12 original, F0…F5 ni P3 τ0→τ9,6. Las puertas originales permanecen. No hay trabajador científico propio iniciado en esta retoma; no se presume terminación de ejecutores antiguos inaccesibles. `main` conserva CP11 con mejoras documentales; PR2 continúa en borrador sin aceptación CP12.
