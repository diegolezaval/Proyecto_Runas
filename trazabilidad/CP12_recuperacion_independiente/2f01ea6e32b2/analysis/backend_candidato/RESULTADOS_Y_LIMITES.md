# Backend de cinco bandas: resultado del control pasivo

El prerregistro `e343095802f4a69b6e9a792253404c73b73f1f5a` precede la ejecución. Pasan las quince representaciones espaciales (tres mallas, ℓ0…4) y las 48 respuestas lineales manufacturadas. Cero pasos M2; las catorce fuentes originales y las trayectorias activas permanecen intactas.

El residuo máximo entre la acción variacional y la representación simétrica de cinco bandas es 3.99605e−16. El espectro es positivo en los casos examinados. El backend general admite tanto campos físicos como arreglos de etapas y canales sin cambiar W.

Con las tablas originales de Gauss–Legendre 7/6, pasos .005/.01, masas Φ²=1 y χ²=10000, el error máximo frente a la respuesta lineal matricial exacta es 1.54918e−12 en fases. Se conserva la actualización original del observador; sólo el resolvente del prototipo usa la acción candidata.

Con fuerza nula, las variaciones máximas de energía cuadrática y carga escalada son 8.70415e−14 y 3.90621e−12, respectivamente. Las puertas originales 2e−4 y 1e−9 pasan. Es la energía de la acción candidata en un sistema lineal manufacturado, no una certificación de balances de una trayectoria M2 corregida.

No se ha validado aquí la realimentación no lineal, su historia, una evolución DOP853 corregida, la convergencia espacial ni la puerta física del 2 %. No se ha conectado este backend al trabajador original. La promoción física sigue condicionada a identificación causal suficiente, prerregistro y controles posteriores. CP12 permanece abierto.
