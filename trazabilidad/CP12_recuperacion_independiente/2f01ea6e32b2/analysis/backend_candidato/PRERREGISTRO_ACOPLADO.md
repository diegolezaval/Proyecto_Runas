# Fuerza M2 e interacción congelada: control pasivo adicional

Se usa exclusivamente la cápsula permanente τ48 de la instancia 2f01ea6e32b2, cuyos hashes y auditor original pasan. Se examinan las condiciones de Cauchy originales τ0 y los campos τ48 de ambas mallas. Las trayectorias, los catorce códigos, M2, Θ, tolerancias y observadores originales no se modifican. No se ejecutan pasos físicos M2 ni se conecta el prototipo al trabajador activo.

En cada estado y malla, se compara la fuerza del candidato variacional calculada con NumPy con la fuerza fusionada C original. Se usan el estado y cuatro perturbaciones aleatorias de amplitud 1e−5, semilla fija 20261012009; se exige el umbral original 2e−12. La fuerza potencial M2 queda intacta y sólo el laplaciano pertenece a la acción candidata.

Se comprueba la identidad del defecto completo entre mallas con la prolongación cúbica original, el conmutador candidato, la transferencia no lineal original y el Jacobiano medio original. Residuo escalado máximo ≤2e−12. No se confunde esta identidad instantánea con un presupuesto propagado.

Para el Jacobiano medio de cada extremo τ0/48, congelado durante un paso, se conserva el subespacio D2 original de seis componentes angulares. La transformación canónica es (√2Φ1,√2Φ2,χ) con peso radial W. Se construye independientemente la matriz dispersa H de la acción candidata y del Jacobiano. Se exige simetría ponderada y equivalencia de acción hasta 2e−12. Los datos de ensayo son aleatorios, con la misma semilla, cinco canales y sin fuerza externa; no representan una nueva solución M2.

Se comparan las respuestas Gauss–Legendre originales 7/6, paso .01 y criterio de iteración 1e−12 en un máximo de 12 iteraciones, con la exponencial de la matriz dispersa congelada. El error relativo de fases debe cumplir 1e−3 y el balance de la energía cuadrática congelada 2e−4. No se exige conservación de la carga de una perturbación con fondo Φ congelado, porque ese operador no conserva por sí solo la simetría de fase del sistema completo. La conservación de la carga M2 requiere la prueba no lineal física posterior, con su puerta original 1e−9.

Este control no valida una historia de realimentación, una trayectoria DOP853 corregida ni la convergencia espacial. No evalúa la puerta física del 2 % ni los inicios finales. Se conservan fallos y límites; la promoción física queda condicionada a identificación causal suficiente en τ160 y a un prerregistro independiente de la campaña.
