# Recuperación administrativa del compilador original de P3

Pregunta: ¿se pueden conservar los tres paquetes oficiales exactos para restaurar el entorno registrado, sin ejecutar física?

Esta rama auxiliar parte de `14b8a8e0546e72154d216db4ca77a223146dd0c6`. Solo su workflow específico se activa al publicar este archivo en `infra/p3-compilador-20261104`. Descarga los tres paquetes de Canonical ya identificados en `trazabilidad/continuidad_20261104/RESTAURACION_COMPILADOR.json`, exige sus tamaños y SHA256 y conserva el conjunto con su recibo durante 90 días.

La tarea tiene permisos de lectura, no usa secretos, no importa fuentes científicas y no construye ni avanza DOP853. Tampoco ejecuta el compilador. El resultado de CI únicamente acredita bytes de dependencias; la instalación en prefijo privado y los auditores originales siguen pendientes.

Motivo: en el proceso local anterior, cpp y libgcc coincidieron, pero la descarga de gcc quedó truncada. Esto es un impedimento administrativo, no un negativo científico. El entorno local desapareció posteriormente. Los bytes de τ12,8 sí están recuperables en el adjunto 711173125 de la Release experimental y conservan la identidad `a58969092423501904f45bfa9e6143d41afac19970c9b61fa0222beb9e13c1d3`.

Puertas: ningún paso M2 hasta restaurar el compilador real, recuperar τ12,8, aprobar los auditores originales y completar la prueba de conservación desde el nuevo proceso. Última frontera completa positiva τ8; τ16 pendiente; CP12 abierto. Se mantienen consumidas las repeticiones anteriores.

Resultado: pendiente de la ejecución identificada por GitHub; no se anticipa aprobación. Siguiente acción: recuperar el artefacto de CI, comprobar sus hashes e instalar mediante el restaurador registrado.
