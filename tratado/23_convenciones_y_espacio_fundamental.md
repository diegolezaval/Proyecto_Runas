# 23 · Convenciones y espacio fundamental de M2

## 23.1. Resultado de E01

La acción escalar de 13.1 se conserva. La signatura es (−+++), Φ=f exp(+iωt), Q positivo para ω>0. Se corrigen en 20.3 tres signos covariantes que no concordaban con esa signatura. Los operadores radiales y sus resultados no requieren un cambio físico. M2 sigue siendo M2; 4.2 es una versión del proyecto.

La autoridad de parámetros es `datos/theta_comun.json`. `modelo_m2.ScalarModel` admite cinco coordenadas independientes; los solucionadores generales están en `soluciones_m2.py`. Los scripts históricos contienen reducciones propias del benchmark y ahora rechazan explícitamente cambios de sus constantes. Sus vistas numéricas históricas no son fuentes alternativas para variar Θ.

## 23.2. Noether, tensor y flujos

Para δΦ=iαΦ,

\[
j^\mu=i(\Phi^*\partial^\mu\Phi-\Phi\partial^\mu\Phi^*)
=-2\operatorname{Im}(\Phi^*\partial^\mu\Phi),\quad
j^0=2\operatorname{Im}(\Phi^*\dot\Phi).
\]

La ecuación de Φ implica ∂μjμ=0: las dos contribuciones de V_s se cancelan. El tensor de Hilbert es

\[
T^{\mu\nu}=2\operatorname{Re}(\partial^\mu\Phi^*\partial^\nu\Phi)
+\partial^\mu\chi\partial^\nu\chi+\eta^{\mu\nu}\mathcal L.
\]

T⁰⁰ es exactamente la densidad positiva de 13.5. Su flujo es

\[
T^{0i}=-2\operatorname{Re}(\dot\Phi^*\partial_i\Phi)-\dot\chi\partial_i\chi.
\]

Al escribir Φ=√s exp(iθ), X=−∂θ·∂θ y L≈P(X), resulta jμ=−2s∂μθ y Tμν=2s∂μθ∂νθ+ημνP. Para θ=μt, j⁰=2μs y T⁰⁰=2μ²s−P=μ²s+U. Esto comprueba conjuntamente corriente y tensor: no basta cambiar X aislado.

Con θ=ωt−Kz+nφ se obtiene Pz=KQ y Jz=−nQ. El signo angular cambia si se escribe −nφ. Q,n,J no son controles independientes dentro de ese ansatz. Los ensembles a Q, P, J fijos deben incluir sus restricciones en la segunda variación. Para el Hessiano radial a Q fija se conserva el término de rango uno de 14.4.

## 23.3. Dimensiones y coordenadas

| Magnitud | Dimensión de masa |
|---|---:|
| Φ, χ, m, M, g | 1 |
| λ₀, h, λ | 0 |
| V, L, Tμν | 4 |
| jμ | 3 |
| Q | 0 |
| tensión superficial | 3 |

Θ=(m,M,λ₀,g,h); λ=g²/(2M²)−λ₀ es derivada. La familia original λ₀=99λ, M=100m, g=M√(200λ), h=100λ es una restricción voluntaria, no una identidad de la teoría.

Para comparar parámetros sin ocultar cambios por reescalado se fijan las unidades m_ref=1 eV y λ_ref=10⁻³, y se usan f=√λ_ref Φ/m_ref, z=√λ_ref χ/m_ref. Entonces el potencial adimensional tiene coeficientes (m/m_ref)², λ₀/λ_ref, (M/m_ref)², g/(m_ref√λ_ref), h/λ_ref. λ_ref es una unidad de amplitud, no un sexto acoplamiento. Coincide con λ del benchmark hasta redondeo; no se impone esa igualdad al barrer Θ.

La variación de m, M, λ₀, g o h puede ahora mantener las otras cuatro constantes fijas. Cada benchmark candidato debe evaluarse globalmente; no se autoriza un conjunto por primordial. El estado, los terminales, las fuentes y las mallas permanecen clases de entradas diferentes.

## 23.4. Dominio suficiente para vacío y Cauchy

Considérese m,M,λ₀,h>0 y g real. Completando el cuadrado del mediador se obtiene el U de 13.7. Si g²≤2λ₀M², U(s)/s≥m². Si g²>2λ₀M², el mínimo está en

\[
s_*={|g|M/\sqrt{2\lambda_0}-M^2\over h},\qquad
\beta=\min U(s)/s=m^2-{(|g|-\sqrt{2\lambda_0}M)^2\over2h}.
\]

La condición estricta β>0 da un vacío único y coercividad. Para ver que se controlan ambos campos, separar una fracción δM²χ²/2, con δ>0 suficientemente pequeña, y aplicar el mismo cálculo al resto con M²→(1−δ)M². Por continuidad βδ>0; por tanto V≥βδs+δM²χ²/2. La energía controla H¹ de los tres campos reales y L² de sus velocidades.

En tres dimensiones, la fuerza polinómica de grados dos y tres es localmente Lipschitz H¹→L² por Sobolev y Hölder. La estimación de onda da existencia y unicidad local en C_tH¹∩C_t¹L²; la cota coerciva permite iterar a todo tiempo finito. Conservación se extiende por aproximación suave. No se afirman cotas puntuales desde H¹, dispersión asintótica ni estabilidad de cada estado.

El símbolo principal sigue siendo (−ξ_t²+|ξ|²)I₃. No hay fantasmas cinéticos; el frente causal es c. El argumento vale en R³ para energía finita y en dominios con condiciones que justifiquen el balance correspondiente. No se traslada automáticamente a materia, gravedad, portales con derivadas ni frontera controlada.

Si β≤0, esta prueba de coercividad no admite esa región; no se sigue automáticamente que no exista una solución de Cauchy de otro tipo. Si β<0, el origen no es el mínimo global del potencial. Los límites de la teoría cuántica son una pregunta distinta de E02.

## 23.5. Comprobación y alcance

`identidades_m2.py` compara derivadas de la acción y Jacobianos por paso complejo, equivalencia dimensional, cancelación local de Noether, cambios separados de las cinco coordenadas y solución del benchmark mediante la interfaz general. `validacion/identidades/resultados.json` conserva valores y tolerancias. E,Q coinciden con la base con diferencias relativas del orden de 10⁻¹⁴.

La regresión del programa original después de la refactorización comprueba los observables afectados. Ni los controles ni esta auditoría prueban identificabilidad experimental de Θ, estabilidad cuántica o un dispositivo completo. Los resultados y la redacción anteriores permanecen en el archivo de referencia.
