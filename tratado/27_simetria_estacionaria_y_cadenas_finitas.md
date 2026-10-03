# 27 · Simetría de los estados positivos y cadenas finitas

## 27.1. Pregunta resuelta y alcance

**Resultado analítico condicionado, con demostración explícita:** en la clase siguiente, todo estado estacionario localizado de fase espacial común es esférico y ambos perfiles decrecen estrictamente desde un mismo centro. Una cadena finita de varios centros, un cilindro finito o un anillo sin arrollamiento no son soluciones estacionarias positivas de esa clase. Esto no refuta contactos dinámicos, nodos, fase espacial variable, rotación, soportes ni un dispositivo de duración limitada. **La subpregunta de CP04 queda resuelta; C7 permanece PARCIAL.**

Se suponen Φ(t,x)=f(x)e^{iωt}, χ(x)=−u(x), en todo R³; f>0; f,u clásicos C², acotados, en H¹ y con límite uniforme cero al infinito; λ₀≥0, g,h,M>0 y a=m²−ω²>0. No hay fronteras internas, fuentes, potenciales externos ni carga fijada artificialmente por celda. Son hipótesis del resultado, no afirmaciones de existencia, unicidad o estabilidad. Se usan las constantes dimensionales; un cambio de unidades positivo preserva cada signo.

La prueba que sigue es propia de esta entrega. Se inspira en el método clásico de planos móviles, pero no atribuye el resultado específico M2 a Busca–Sirakov ni presupone un teorema suyo que no se haya leído. La referencia metodológica original es [Gidas, Ni y Nirenberg, 1979](https://doi.org/10.1007/BF01221125). No se afirma una revisión matemática externa ni una certificación formal por ordenador.

## 27.2. Mediador y ecuaciones cooperativas

Las ecuaciones son

\[
-\Delta f=F(f,u)=-af-2\lambda_0f^3+guf-\tfrac h2u^2f,
\qquad
-\Delta u=G(f,u)=-M^2u+gf^2-hf^2u.
\]

En la ecuación (−Δ+M²+hf²)u=gf², cero es subsolución y g/h es supersolución estricta. El decaimiento y el principio fuerte del máximo dan 0<u<g/h. Por tanto Fᵤ=f(g−hu)>0 y Gf=2f(g−hu)>0. La cota también vale en todos los segmentos que unen valores reflejados, porque el intervalo (0,g/h) es convexo.

## 27.3. Comparación que inicia el plano desde el exterior

Para Σλ={x₁<λ}, reflejar x en xλ=(2λ−x₁,x₂,x₃), y escribir fλ=f(xλ), uλ=u(xλ), U=fλ−f y V=uλ−u. En la frontera plana U=V=0. Las diferencias satisfacen **exactamente**

\[
-\Delta U=A U+B V,\qquad -\Delta V=C U+D V,
\]

\[
\begin{aligned}
A&=-a-2\lambda_0(f_\lambda^2+f_\lambda f+f^2)+gu-\tfrac h2u^2,\\
B&=f_\lambda[g-\tfrac h2(u_\lambda+u)]>0,\\
C&=(g-hu_\lambda)(f_\lambda+f)>0,\\
D&=-M^2-hf^2<0.
\end{aligned}
\]

Esta descomposición es relevante: el coeficiente A usa u(x), aunque el punto reflejado esté dentro del núcleo. No basta decir que todos los valores reflejados son pequeños cuando el plano está lejos.

Sean p=max(−U,0), q=max(−V,0). Extenderlos por cero al otro semiespacio. Pertenecen a H¹; se pueden probar las identidades con cortes compactos y llevar el radio a infinito usando H¹ y los coeficientes acotados. Multiplicar las ecuaciones por −p y −q e integrar da

\[
\int(|\nabla p|^2+|\nabla q|^2)
\le\int A p^2+D q^2+3g f\,p q.
\tag{27.1}
\]

En efecto, donde p>0 se tiene fλ<f, de modo que B≤gf; donde p q>0 también C≤2gf. Los términos con U o V positivos tienen signo favorable y se descartan en la desigualdad. No se necesita que los dos valores reflejados estén pequeños fuera del soporte de las partes negativas.

Elegir R de forma que, para |x|>R,

\[
u\le\frac{a}{2g},\qquad f\le\frac{M\sqrt a}{6g}.
\]

Esto es posible por el decaimiento uniforme. Allí A≤−a/2, D≤−M² y, por Young,

\[
3gfpq\le\frac a4p^2+\frac{9g^2f^2}{a}q^2
\le\frac a4p^2+\frac{M^2}{4}q^2.
\]

Si λ<−R, todo Σλ es exterior. (27.1) obliga a ∫(|∇p|²+|∇q|²+a p²/4+3M²q²/4)≤0; luego p=q=0. Queda establecido el arranque del plano sin una suposición no probada sobre los puntos reflejados.

## 27.4. Posición límite y continuación

Mover el plano mientras U,V≥0 para todas sus posiciones anteriores. La posición límite λ* es finita: si se reflejara un punto donde f alcanza su máximo hacia puntos cada vez más lejanos, el decaimiento violaría la desigualdad. Por continuidad U,V≥0 en Σλ*.

El principio fuerte del máximo aplicado al sistema cooperativo implica una alternativa: ambas diferencias son idénticamente cero, o ambas son estrictamente positivas. Para usar el principio escalar puede añadirse un coeficiente diagonal no negativo suficientemente grande; B,C son positivos y acotados. Si una diferencia se anula idénticamente, su ecuación obliga a anular la otra.

Supóngase la alternativa estricta. Fijar el mismo R exterior. Elegir un compacto K dentro de Σλ*∩B_R, alejado del plano y del borde de la bola, con diferencias uniformemente positivas. El conjunto restante dentro de B_R puede tener volumen tan pequeño como se quiera. Al mover el plano una cantidad suficientemente pequeña se conserva la positividad en K; las partes negativas quedan confinadas a ese pequeño conjunto interior D y al exterior.

En el exterior, el lado derecho de (27.1) es no positivo por las cotas anteriores. En D, todos los coeficientes están uniformemente acotados, por lo que

\[
\int(|\nabla p|^2+|\nabla q|^2)
\le C\int_D(p^2+q^2)
\le C C_S |D|^{2/3}\int(|\nabla p|^2+|\nabla q|^2).
\]

La segunda desigualdad es Hölder y Sobolev en R³ para las extensiones por cero. Elegir D tan pequeño que el factor sea menor que uno fuerza p=q=0, contradiciendo que λ* fuera la última posición. Por tanto ambas diferencias son cero en el plano límite: los dos campos comparten ese plano de simetría.

## 27.5. Monotonía y centro común

Para todo plano anterior al límite, las diferencias son estrictamente positivas. No pueden ser simétricas respecto de dos planos paralelos distintos: la composición de esas reflexiones impondría periodicidad a un perfil positivo que decae. El lema de Hopf sobre cada plano anterior da ∂₁f>0 y ∂₁u>0 en su lado izquierdo.

El argumento vale para cualquier dirección espacial e. El máximo de f existe por positividad, continuidad y decaimiento. Sea x₀ un punto donde se alcanza. La monotonía estricta obliga a que cada plano crítico perpendicular a e pase por x₀. Como ambos campos comparten esos planos, son invariantes bajo todas las reflexiones que pasan por x₀; de ahí la simetría radial de ambos respecto del mismo centro. Hopf da f′(r)<0 y u′(r)<0 para r>0, o χ′(r)>0.

No se demuestra unicidad de la solución radial a una carga o frecuencia, ni que toda solución radial minimice la energía. La monotonía exacta sólo se refiere a soluciones que cumplen las hipótesis, no convierte un perfil aproximado en una solución exacta.

## 27.6. Decisiones y verificación

| Clase | Decisión de esta entrega |
|---|---|
| Cadena finita estacionaria, f>0, fase común, libre y localizada | Descartada como estado multicentro bajo las hipótesis |
| Cilindro finito o anillo estacionario de amplitud positiva sin arrollamiento | Descartado como geometría no esférica en esa clase |
| Una gota esférica estacionaria | Permitida por la simetría; existencia y estabilidad son preguntas distintas |
| Nodos, vorticidad, gradientes de fase, frecuencias diferentes o dinámica | No cubiertos |
| Soportes materiales, fuentes, fronteras físicas o control | No cubiertos; requieren su acción y recursos |

Se comprobaron las identidades de diferencias, signos cooperativos y cotas exteriores en un auditor numérico de álgebra. Es una defensa contra errores de implementación y signos; no prueba el argumento funcional. La revisión analítica anterior trata explícitamente H¹, el exterior, el conjunto pequeño, el acoplamiento y el centro común. Las 22 comprobaciones de Canal se conservan sin modificación, con rechazo temprano por existencia en esta nueva clase. Las comprobaciones posteriores no se dan por aprobadas.

**Puerta:** subclase descartada dentro de M2 condicionado; C7 PARCIAL. No reabrir E00, E01 ni C0. La búsqueda restante debe cambiar una hipótesis física; no repetir Newton sobre una cadena positiva de fase común como si pudiera sostenerse estáticamente. Se continúa con estabilidad no radial del estado preparado y contactos dinámicos, manteniendo la contabilidad de sus recursos.
