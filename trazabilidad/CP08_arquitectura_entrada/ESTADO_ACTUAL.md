# Estado actual · CP08_REFINAMIENTO_NO_RADIAL

E00, E01 y C0 COMPLETADAS e intactas. No repetirlas, ni las campañas cerradas CP03/CP04, las ocho evoluciones Verlet de CP06, las cuatro adaptativas completas o la dispersión lineal ya verificada.

**La evolución pendiente h=.125 terminó en τ=160.** Se reanudó desde τ=48 tras la pausa de Work. Se completaron las comparaciones y se aplicó la puerta sin relajar sus límites: **NO SUPERADA; cálculo finalizado, refinamiento adicional pendiente**.

Mallas h=.25→.125: χ difiere 3,45323 % en posiciones y 5,04292 % incluyendo velocidades (límite 2 %). El fallo anterior h=.5→.25, los fallos de integradores y el fallo angular L2→L4 siguen archivados. Resultado vigente: `validacion/P06/no_radial/resultados.json`.

No hay evoluciones activas ni hay que reiniciar los estados terminados. La puerta sólo corresponde a la deformación cuadrupolar y ventana declaradas; E02/E03/E04/RES0/RES1/C7 siguen PARCIALES, RES2 BLOQUEADA y hay cero dispositivos completos.

CP07 también dejó COMPLETADAS las subpreguntas de acceso lineal muestreado y fase estacionaria sin nodos (capítulos 29–30). No demuestra retroacción finita ni un ciclo de Reserva; C7 permanece abierto para nodos/vórtices y dinámica.

Siguiente trabajo: Investigar el fallo de la puerta con los datos guardados; prerregistrar el refinamiento necesario antes de iniciarlo. No repetir las doce evoluciones terminadas.

Informe de entrega: [ENTREGA_08_REFINAMIENTO_NO_RADIAL.md](informes/ENTREGA_08_REFINAMIENTO_NO_RADIAL.md). Para recuperar todos los estados, extraer los dos ZIP complementarios de CP08 en la misma carpeta. Véase [LEEME_ENTREGA_CP08.md](LEEME_ENTREGA_CP08.md).
