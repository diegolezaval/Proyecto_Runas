# Comprobación adicional de contadores guardados CP12

Se añade una comprobación administrativa de lectura antes de empaquetar cada frontera. No cambia M2, Θ, el solver, su configuración, la instrumentación pasiva ni sus criterios. Las catorce fuentes científicas mantienen su identidad original. El orquestador sólo invoca el nuevo lector después de la auditoría original y antes del respaldo.

Los logs CP10 protegidos por sus recibos contienen los pasos aceptados y máximos acumulados E/Q de las veinte fronteras 8…160. Se exige igualdad exacta de esos tres valores en cada malla. Las evaluaciones tienen referencias exactas disponibles en 8, 16 y 160. En las restantes fronteras se registra expresamente que no existe un contador histórico intermedio de referencia: se comprueba únicamente la contabilidad DOP853 (12 evaluaciones por intento de paso, dos iniciales por segmento y tres por interpolante físico observado), sin inventar rechazos históricos. La igualdad exacta final de evaluaciones CP10 sigue siendo obligatoria.

El lector captura sus fuentes, los logs y recibos CP10 y hashes de entrada, conserva resultados con fecha nueva y no sobrescribe auditorías anteriores. Un resultado negativo detiene la continuación. Su control sobre τ=8 pasa y no ejecuta pasos M2. Los estados científicos y los límites permanecen intactos.
