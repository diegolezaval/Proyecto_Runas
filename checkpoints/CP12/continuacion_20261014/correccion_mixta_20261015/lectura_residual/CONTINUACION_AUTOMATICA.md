# Lectura automática posterior al guardián propio

Este suplemento administrativo no altera al controlador en ejecución ni autoriza pasos físicos nuevos. Implementa la lectura ya prerregistrada en `1d56b266e32b3df3a4db21bf21f182adaa528746`, después de la salida **observada** del guardián del intento aislado. No usa la ausencia de un PID o un latido antiguo como prueba de terminación.

`despues_del_guardian.py` espera el recibo de salida creado por el padre del guardián propio. Si la salida no es cero, conserva el estado de espera fallida y no reintenta M2. Si es cero, exige τ160 íntegro con auditoría positiva, y el suplemento final físico guardado y recuperado por el controlador original. Revalida cobertura, tamaños y todos los hashes de las extracciones separadas. No interpreta el directorio activo.

La lectura usa exactamente `leer_residuo_mixto.py`, SHA256 `b29659e0fd03731ec2aa11f2175a604f9ce64eed9562dee8de01249cea9fb314`, el resultado original autenticado y el resultado físico recuperado. Mantiene las cinco métricas espaciales y las tres ventanas originales. También puede conservar una lectura residual negativa cuando el resultado físico final es negativo; no la convierte en aceptación. Ninguna otra variante ni refinamiento se ejecuta por este suplemento.

Tras leer, conserva la salida, las fuentes del suplemento y su procedencia dentro de una nueva cápsula adicional, recuperada y verificada por los auxiliares originales. Los fallos administrativos quedan separados de los fallos científicos. Un resultado positivo sólo desbloquea el diseño y prerregistro de referencia h=.03125, estabilidad y robustez: no cierra CP12 ni abre etapas dependientes por sí solo. CP11, main y PR #2 siguen intactos.
