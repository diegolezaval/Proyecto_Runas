# Enmienda de escritura JSON tras el primer intento

El lector registrado en `a77fa401a6f649f117dd7ce270954ace08b29066` llegó al
final de las comprobaciones y de las lecturas τ112/120/128/160. La escritura
de D1 se detuvo con `TypeError: ndarray` al encontrar matrices NumPy en el
diccionario de resultados. El intento conservó la auditoría independiente,
la historia y las proyecciones espectrales en el entorno de diagnóstico,
sin intentos de construcción o pasos DOP853 ni avance de observadores.

El reintento convierte arreglos NumPy a listas sólo al serializar. Las
entradas, comparaciones, coeficientes, puertas y fuentes científicas
permanecen fijadas. Se exige una salida nueva, se repiten las comprobaciones
y se cotejan las huellas de la historia y de los espectros ya escritos.
La enmienda se registra antes de repetir la lectura.
