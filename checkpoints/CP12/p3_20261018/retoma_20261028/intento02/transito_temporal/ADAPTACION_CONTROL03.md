# Identidad devuelta por Biblioteca: control 02 y adaptación 03

La segunda escritura nativa también terminó correctamente. La Biblioteca conservó otra copia y añadió `(1)` al nombre: libfile_449a0e5d8da88191b536c741bfc6c3e2, file_00000000e7cc81fd9dead05961bc2212. El adaptador se detuvo porque exigía que el nombre devuelto coincidiera con el nombre local. Su resultado negativo original se conserva; no se infiere que la escritura fallara ni se repite una escritura incierta.

Se corrige la correlación para usar como autoritativos los identificadores y el nombre devueltos por la Biblioteca. Los bytes de la fuente y de la descarga siguen obligatoriamente ligados por tamaño y SHA-256. Se conservan los identificadores inmediatamente después de una escritura acreditada y antes de validar el resto de la respuesta. No se rebaja ninguna comprobación científica o de integridad.

Se añade un modo de reconciliación de sólo lectura: requiere un recibo existente ligado al SHA-256 de la solicitud y a la identidad exacta del ZIP; no llama al ayudante de subida. Descarga y audita en una raíz nueva. Ese modo marca explícitamente que no realizó el ciclo nativo completo en esa invocación y no puede sustituir por sí solo la puerta de capacidad previa a M2.

Pasan diez controles sintéticos. Primero se reconcilian por lectura las dos identidades conocidas y se conserva la evidencia. La descarga del control01 ya pasó los 30+14 controles originales sin pasos. Después se registrará un tercer control completo, con copia local y nombre nuevos, para exigir todo el ciclo nativo con el adaptador corregido en una sola ejecución. No se usa todavía la autorización de evolución ni se exige otra autorización de repetición. Si aparece un límite real de almacenamiento, se detendrá el flujo antes de M2.
