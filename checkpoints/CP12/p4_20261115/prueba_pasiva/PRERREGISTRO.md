# CP12 · Prueba pasiva factorial del candidato P4

Esta prueba aplica el [plan publicado](../../p3_20261018/diagnostico_tau160_20261115/PLAN_VALIDACION.md) en `5cd9fbacc78ff9ea1815a36e48cb0a42eb7d3737`. Las dos entradas provienen de la repetición independiente P3. τ112 es un cierre válido y τ160 es la evidencia de suspensión. El último checkpoint válido de P3 es τ152.

## Entradas y contraste

- Usar los adjuntos 750322957 y 750993142 de `respaldo-cp12-p3-20261027`. Verificar el CMS de τ160 y ambos ZIP con las huellas registradas. El auditor de extracción original comprobará tamaño, cobertura y huella de cada archivo. Reutilizar sus recibos originales de recuperación exacta con cero pasos M2.
- Fijar, en cada corte, el Jacobiano acoplado del observador P3 en la comparación original cúbica gruesa→fina. Usar el subespacio angular guardado de seis columnas pares, mallas h=.125/.0625, R220, masas, cierres y datos iniciales de ese experimento. La rama inversa usa el mismo Jacobiano cúbicamente transferido a la malla gruesa. Mantenerlo fijo en el tiempo y entre brazos. Fijar también las fuentes en el estado del corte.
- Usar condiciones iniciales pasivas nulas, que sustraen la respuesta homogénea común. Integrar durante Δτ=.4 con cuarenta pasos pasivos .01 en GL7 y GL6. Bloquear la construcción, avance y salida densa de DOP853 y el avance histórico del presupuesto. Contar cero pasos físicos M2.
  
| Brazo | Fuente χ | Propagador pasivo |
|---|---|---|
| Base | C₃=I L₃χₛ−L₃ Iχₛ | P3 |
| Conmutador | C₃+ΔC₄ | P3 |
| Propagador | C₃ | P4 |
| Combinado | C₃+ΔC₄ | P4 |
| Geometría k≤4 | C₃−(I hₛ²Gℓ[χₛ]−hₜ²Gℓ[Iχₛ]) | P3 |
| Geometría k≤8 | Igual contraste geométrico con la proyección ampliada | P3 |

En cada malla, ΔC₄ proviene únicamente de ΔL=-h⁶A₂⁴/560. El propagador P4 conserva Φ-FV, masas y acoplamiento y añade ese mismo incremento a χ. El control geométrico usa proyección W sobre funciones de Bessel esféricas regulares con cero en R y evalúa la expresión analítica de Gℓ. La inversión gruesa←fina se orienta con signo común antes de formar el presupuesto.

## Verificación y decisión

- Antes de leer los campos guardados, contrastar ambos resolventes con la solución analítica de un modo propio forzado de χ en ℓ=2,4 en ambas resoluciones y ambos GL. Umbral relativo 2×10⁻⁹. Contrastar Gℓ con perfiles regulares fabricados de coeficientes y signos conocidos antes de aplicar las dos proyecciones, con el mismo umbral.
- Para cada respuesta, guardar χ y χ̇/μ, potencia, Gram, término firmado 2⟨base,Δ⟩ y potencia ‖Δ‖². Exigir cierre de linealidad ≤2×10⁻¹⁰, residual de iteración ≤10⁻¹² y Parseval ≤2×10⁻¹¹. Usar r<40, 10≤r<20, 20≤r<40 y 40≤r<220. Tras aplicar cada máscara radial, proyectar W½χ y W½χ̇/μ en los vectores propios del A₂ simétrico y seleccionar k de referencia esférico >8 por índice nodal. Normalizar potencias por la escala inicial de χ de la comparación original. Informar cambios porcentuales relativos a la potencia de la base de cada caso.
- Aplicar la decisión a la potencia conjunta de χ y χ̇/μ en τ160, r<40 y k>8, por separado en ℓ=2 y ℓ=4. Exigir concordancia de los dos GL, con tolerancia de norma relativa 10⁻³ y mismo signo en el efecto combinado. La combinación tiene que reducir la potencia en ambos modos en la cúbica original y conservar el signo de la reducción con paridad en el origen y cúbica inversa. Una reducción ausente o de signo contrario con concordancia de GL refuta el candidato en este ensayo. Una falta de concordancia de GL deja la decisión inconclusa y se resolverá con una referencia independiente del mismo problema lineal congelado.
- Registrar la magnitud del contraste geométrico. Para hacer operativa la comparación, se marca como comparable cuando su cambio absoluto de potencia alcanza la mitad del cambio combinado de P4 para un modo en la banda principal. Este cociente se refiere a la porción regular proyectada.
- Si la señal conjunta supera la puerta, revisar la transición con τ120 y τ128 antes del piloto. Este resultado local usa cortes congelados. La validación física, su comparador original del 2 % y el prerregistro de sus propios controles tienen su propia puerta.
