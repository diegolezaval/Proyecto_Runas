# CP12: frontera τ=16 conservada y comprobada

El 10 de octubre se continuó 8→16 desde la cápsula τ=8 recuperada y verificada. El nuevo NPZ reproduce exactamente el antecedente histórico: SHA-256 `3262c6eb99838319c31e2379cc11c4cd97b0631d5fd2760b741fc716622f4b21`, 28 393 475 bytes, 41 observaciones, 2966 pasos y 36136 evaluaciones en cada malla. Iniciales y prefijo CP10 son array_equal. Pasan configuración, fuentes, recibos, seis controles y todas las puertas originales del observador. El mayor residual de cierre es 5.80276454319202e-7.

La cápsula permanente `Proyecto_Runas_CP12_REINICIO_tau0016.zip` tiene 74 911 170 bytes, 291 archivos y SHA-256 `505840842b4d2097a67981f7e71e0af3a95dc1ec98fbe909d2d2faf55c5233cf`. Se descargó, se verificaron todos los hashes y se auditó el árbol extraído, incluida recarga sin avance. El [comprobante](../trazabilidad/CP12_reconstruccion/respaldos/tau0016.json) identifica el archivo y encadena el respaldo τ=8.

Esta frontera sustituye a τ=8 como último reinicio permanente comprobado. El binario del par bajo validacion/ en GitHub sigue en τ=0: recuperar la cápsula completa y comprobarla antes de reanudar. No repetir 0→16 ni mezclar recibos. Se inició 16→24 únicamente después de la verificación permanente. Comprobar el escritor activo antes de lanzar otro proceso.

Se añade una auditoría administrativa de lectura de los pasos aceptados y máximos E/Q de cada frontera frente a los logs CP10. No modifica las catorce fuentes científicas, solver, tolerancias ni observadores. Las evaluaciones tienen comparación histórica exacta en 8, 16 y 160; las restantes sólo pueden contrastarse mediante contabilidad DOP853 hasta la igualdad final. Sus fuentes, recibos y resultados quedan capturados.

CP12 permanece abierto, sin interpretación causal final ni corrección ensayada. CP11 sigue siendo el checkpoint científico cerrado; la puerta física permanece en 2 %. PR #2 borrador; sin merge, tag ni Release.
