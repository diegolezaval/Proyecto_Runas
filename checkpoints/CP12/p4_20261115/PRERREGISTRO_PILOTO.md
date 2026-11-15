# CP12 · Prerregistro del piloto P4 y sus controles previos

La [prueba pasiva](prueba_pasiva/RECIBO.json) habilita preparar el ensayo P4. La hipótesis es que añadir a la fuerza de χ solamente −h⁶A₂⁴χ/560 reducirá la discrepancia tardía de χ entre h=.125 y h=.0625. La acción complementaria es h⁶‖A₂²χ‖²_W/1120. A₂, su peso, los cierres y el término geométrico h² se mantienen. Usar la rama científica dedicada `ciencia/cp12-p4-20261115`, con una identidad física propia fijada en el registro.

## Controles antes del primer paso de M2

El registro fija las fuentes, el ensayo pasivo precedente y los criterios antes de las nuevas mediciones. F0–F5 reutilizan las comparaciones de P3 con la nueva acción, el término y el resolvente de P4. Los controles de referencia de P3 se ejecutan sobre P4. Los fondos son los datos de Cauchy CP10 originales, el final CP10 original y la frontera forense P3 a τ160. Esta última solo entra en los controles congelados. Verificar su manifiesto de 747 cargas y el entorno original.

| Control | Contraste y criterio |
|---|---|
| F0 | Coeficientes exactos 1, 1/12, 1/90, 1/560, símbolo plano hasta k⁸h⁶, positividad, nueve bandas, espectro, origen y cierre. Residuos algebraicos ≤2×10⁻¹² y consistencia en perfiles centrados y de banda. Orden final centrado ℓ=2/4 entre 1,5 y 2,5. |
| F1 | Rutas numéricas de Φ-FV y χ-P4, potencial C/NumPy, gradiente por paso complejo, carga U(1), diferencia de las dos energías y trabajo FV con cuatro perturbaciones, a escala original. Residuos ≤2×10⁻¹². |
| F2 | Conmutador, identidad linealizada bare/acoplada, simetría con peso (2,2,1), referencia de precisión extendida y D₂ en los dos tamaños originales. Residuos ≤2×10⁻¹². |
| F3 | Matriz canónica de caras independiente, acción, simetría y resolventes GL7/6 en ambos tamaños y tres fondos. Residuos ≤2×10⁻¹². |
| F4 | Referencia independiente exponencial dispersa y Taylor grado 32 con 16/32 subpasos en .1. Referencias y cota ≤10⁻⁸, fases GL ≤10⁻³, balance cuadrático ≤2×10⁻⁴, iteración ≤12 y residual ≤10⁻¹². |
| F5 | Energía incremental positiva y gradiente contra la cuarta potencia independiente del grafo de caras, ℓ=0…4, incluyendo R220. Residuos ≤2×10⁻¹². |
| Banda ocupada | Contrastar dispersión radial y velocidad de grupo plana P3/P4 en k>8 común, ponderadas por χ y χ̇/μ de las dos mallas a τ160. Comprobar la derivada hasta 10⁻⁸. Conservar discrepancias y empeoramientos. |
| Transporte y recuperación | Crear τ0 desde las seis matrices CP10 exactas. Verificar la cápsula, la acción, dos energías, carga, identidad y ceros M2 desde una extracción nueva. Comprobar con el supervisor y dos invocaciones independientes que se elige la misma frontera y se reserva un único trabajador. |

Completar además el contraste pasivo reservado de τ120 y τ128 con la cúbica original y GL7/6, conservando los cambios de potencia de los tres brazos y la comparación geométrica. Esta lectura revisa la persistencia de la señal durante el desplazamiento radial.

## Ejecución y puertas

Crear el origen τ0 con los datos originales CP10 exactos, CP04 y Θ originales, R220, h=.125/.0625, L4, ε=.02, DOP853 rtol=10⁻¹⁰, atol=10⁻¹², paso máximo .02, observaciones cada .4 y esquemas pasivos GL7/6 originales. Publicar y recuperar la cápsula de origen. Cada sesión de continuación verifica la asignación, su respaldo exacto, la exclusividad y la reserva antes del primer paso.

Avanzar por tramos de 8 hasta τ160. En cada cierre, aplicar las cinco métricas originales ≤.02 con cúbica gruesa→fina, r<40 y χ sin giro. Exigir ambas energías por separado ≤2×10⁻⁴, carga ≤10⁻⁹, cierres/fases ≤10⁻³, identidad/simetría ≤2×10⁻¹², Parseval ≤2×10⁻¹¹ y los controles originales de carga de núcleo y amplificación. Descargar y auditar cada cápsula en GitHub con cero pasos de M2 antes del próximo tramo. Si falla una puerta científica, conservar el fallo y certificar el último cierre válido. Recuperar el respaldo acreditado más reciente de esta identidad si se interrumpe el entorno, previa conciliación de su proceso.

En τ160 evaluar las tres ventanas causales con contribuciones firmadas y escala original. Exigir la reducción ≥50 % del canal acoplado operador χ frente al original y todas las puertas. Contrastar además la fase tardía de χ con el 2,0666 % publicado de la repetición P3. Una decisión positiva en pareja deja pendientes la tercera malla, la referencia independiente, la sensibilidad de caja y angular, estabilidad temporal y robustez de los datos originales.
