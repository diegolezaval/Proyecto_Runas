# CP12: τ160 conservado; causa condicionada identificada

La recuperación pública **τ80** está completa y certificada: 145/145 JSON reconstruyen exactamente el NPZ original. Certificado: `checkpoints/CP12/continuacion_20261014/tau0080/CERTIFICACION_CLON_LIMPIO.json`.

La continuación original alcanzó **τ160** y supera las **44 comprobaciones finales**, incluida la igualdad exacta con CP10 en los estados, las 401 observaciones por malla y todos los contadores. NPZ SHA-256 `22078538ebba2e948b433b0ab946ee034be132b27f7e72ca1ee30540323b2413`. Las cápsulas completas de cada frontera de ocho unidades están conservadas; la recuperación numérica pública completa sigue en τ80.

Las tres ventanas causales originales dan suficiencia al **operador χ acoplado** y a **operador_total**. La discrepancia espacial final de χ es **5,126390964 %**, superior al **2 %**: CP12 sigue abierto. Los resultados completos incluyen cancelaciones, términos cruzados y los canales negativos. El fallo inicial del lector al escribir booleanos NumPy quedó conservado; una adaptación exclusiva de serialización completó la lectura con cero pasos M2 y hashes científicos idénticos.

La siguiente tarea es revisar el prerregistro de corrección ya conservado y ejecutar únicamente pruebas justificadas de una evolución corregida autoconsistente. No se repite la evolución original ni los controles certificados. Informe: `informes/RESULTADO_CP12_TAU160_20261015.md`.

Main permanece en CP11, las 33 etapas siguen intactas y PR #2 permanece abierto y en borrador. El trabajador propio terminó tras la evolución; los ejecutores anteriores conservan estado de actividad desconocida. M2, Θ, mallas, DOP853, tolerancias, observadores, spline y criterio del 2 % permanecen originales.

La **primera prueba K4** fue prerregistrada, inicializada y guardada/recuperada/auditada en τ0 con 23 comprobaciones. El piloto se detuvo por la puerta energética FV original: h=.0625, τ=0.017672153921661566, deriva 0.00029807341459231473 >2e-4. El negativo completo quedó guardado, recuperado y verificado. No se alcanzó τ8 ni se validó la corrección. Véase `informes/RESULTADO_NEGATIVO_K4_20261015.md`. La siguiente tarea es analizar pasivamente las formas energéticas y el trabajo del cambio de operador sobre los estados guardados. No se reinicia K4 ni se relajan puertas.
