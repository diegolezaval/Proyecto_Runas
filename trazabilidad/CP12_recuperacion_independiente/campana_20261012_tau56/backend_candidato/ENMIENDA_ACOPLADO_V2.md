# Enmienda prerregistrada: control acoplado estático v2

Se conserva íntegra la primera versión y su fallo: residuo absoluto 5.033414794833095e-12, dividido por la diferencia de fuerzas 1.1256978466650125, da 4.471372855287116e-12 y supera su umbral 2e-12. El resultado v1 no se acepta ni se borra. La inspección separada encontró residuo de linealidad radial 5.772021315769704e-15 y residuo de la identidad no lineal evaluada por resta en float64 4.855734744683721e-12. Esto indica una posible cancelación numérica, que v2 debe comprobar.

El protocolo original reproducir_par_CP12.reference distingue expresamente el residuo relativo a la diferencia pequeña y el residuo dividido por max(1,max|fuerza interpolada gruesa|+max|fuerza fina|). Su aceptación de la identidad cúbica usa además la referencia extendida sin restar primero fuerzas float64. V1 no aplicó esa definición original a la identidad completa.

Antes de ejecutar v2, se registra: conservar ambas escalas y el resultado negativo v1; usar 2e-12, sin modificarlo, para el residuo con la escala absoluta original; exigir adicionalmente la identidad extendida original, simetría del Jacobiano, equivalencia C/NumPy y partición no lineal originales con 2e-12. La referencia extendida es sólo un control y no se incorpora a la evolución.

El control lee las instantáneas inicial y τ56 del respaldo nuevo permanente, verificando sus hashes y las catorce fuentes. El cambio de τ48 a τ56 responde a la frontera recuperada actual, conservando v1 con su procedencia. Las fuerzas M2 y estados no cambian. Se prueba únicamente el operador candidato sobre datos guardados y un Jacobiano congelado.

Se conservan todos los otros criterios del prerregistro previo: prueba C/NumPy, acción y simetría canónica 2e-12; propagación de cinco canales frente a exponencial dispersa, etapas 7/6, paso .01, iteración 1e-12 y máximo 12, error 1e-3 y energía cuadrática 2e-4. Las semillas son las originales del control. No se aplica una puerta de carga U(1) a un Jacobiano congelado que no tiene esa simetría; la puerta física original de carga 1e-9 sigue intacta para cualquier evolución futura.

Cero pasos físicos M2. No valida una historia no lineal, una trayectoria DOP853 corregida, convergencia física ni el cierre de CP12. Un fallo se conserva y detiene el control.
