# CP12 · Recuperación aislada del piloto mixto

La rama se recuperó en `1d56b266e32b3df3a4db21bf21f182adaa528746`, posterior al commit indicado en la solicitud. El prerregistro físico, A–D, τ0 y la lectura residual prospectiva ya existían. No se repiten. El piloto anterior sólo conserva un latido en τ≈2.25; no hay campos completos, cápsula τ8 ni salida observada. Su actividad remota sigue desconocida y no se modifica su directorio.

La recuperación aislada fue prerregistrada en `57da2a7e0ca8ba985d55e248138ac6101655df12`. El ZIP original pasa cobertura exacta y 81 hashes; su extracción supera las 28 comprobaciones originales con cero pasos M2. El estado NPZ se copió byte a byte, sin resembrar ni alterar configuración o identidad científica.

La nueva cápsula inicial completa, con la procedencia del intento, tiene 10 992 104 bytes y SHA256 `30250321fb38146d56a398057cf2b4302269548be733907b3d77c24ad74e045c`. Fue guardada, recuperada, verificada en cada archivo y auditada sobre otra extracción, con 28 comprobaciones sin pasos M2. El NPZ conserva SHA256 `753c8400b3fad8a34b8286cfb6ac6ea8a10def61c8abd42ea4336efe5026874b`. Véase `checkpoints/CP12/continuacion_20261014/correccion_mixta_20261015/recuperacion_20261015/CERTIFICADO_TAU0.json`.

Después arrancó el guardián original en una raíz independiente, con fuentes capturadas intactas. La última frontera certificada sigue siendo τ0. Su primer destino es τ8; sólo una frontera completa, conservada, recuperada y auditada desbloquea la siguiente. La conservación de ambas energías, carga, observadores y criterios espaciales permanece original. La actividad no certifica resultados. Cualquier fallo detiene esta versión y conserva el negativo.

El estado de intento anterior y el actual se distinguen: no se presume terminación del primero ni se atribuye al segundo una observación histórica. La procedencia y las identidades operativas completas se conservan privadamente. CP12 sigue abierto, CP11 es el último checkpoint científico aceptado y las 33 etapas conservan sus estados y puertas. Main y PR #2 permanecen intactos; el PR sigue abierto y en borrador.

Para continuar: consultar primero las nuevas pruebas y cápsulas de este intento. Si el guardián propio está observado activo, supervisarlo sin iniciar otro. Si hay negativo, recuperarlo e investigar pasivamente; no reintentar. Si existe una frontera posterior certificada, recuperar su cápsula íntegra y usar sus fuentes capturadas y recibo. No reiniciar desde τ0 por basarse en una vista antigua.
