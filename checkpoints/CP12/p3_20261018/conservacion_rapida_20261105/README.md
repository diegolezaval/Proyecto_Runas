# Conservación P3: serialización sin pérdidas

Versión administrativa preparada después de recuperar16 y antes de cualquier uso en un trabajador nuevo. No altera fuentes científicas, solver, tolerancias ni puertas.

La única diferencia de `ejecutor/preservar.py` con el preservador de continuidad_20261030 es `compress_type=ZIP_STORED` para cargas cuyo nombre termina en `.npz`. Se escriben los mismos bytes tras las comprobaciones originales de tamaño y SHA256. Las demás cargas usan DEFLATE nivel6. `continuar.py` y `probar.py` son copias exactas; el preservador original se conserva.

[REGISTRO.json](REGISTRO.json) fija los hashes y alcance. [COMPARACION_EMPAQUETADO.json](COMPARACION_EMPAQUETADO.json) conserva dos parejas de mediciones y la equivalencia exacta de todas las entradas. [CONTROLES_ADMINISTRATIVOS.json](CONTROLES_ADMINISTRATIVOS.json) conserva los doce rechazos originales. [AUDITORIA_CONTENEDOR_RAPIDO.json](AUDITORIA_CONTENEDOR_RAPIDO.json) conserva los30 controles originales sobre una extracción de la variante rápida.

`comparar_empaquetado.py` recibe `--archive`, `--sha256`, `--bytes`, `--original`, `--candidate`, `--auditor` y `--output` nuevo. Verifica el cambio único por AST, compara orden/nombres/bytes completos y usa el desempaquetador original. No importa módulos científicos, construye solvers ni avanza M2. Los ZIP medidos no sustituyen la cápsula científica autoritativa de16.

Para usar esta versión, registrar sus hashes en una asignación nueva. El trabajador real debe completar sus controles originales y conservación nativa y pública antes de la reserva/activación. Se mantienen todas las auditorías y guardados. No se cambia código de trabajadores activos ni se omite recuperación independiente.

El ahorro medido es del empaquetado:9,91→0,312 segundos;31,8 veces;5522 bytes adicionales sobre230213899. No constituye una aceleración medida del integrador ni de todo el ciclo.
