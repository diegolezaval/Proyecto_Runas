# P3: origen discreto, espectro radial y alcance causal finito

Esta derivación complementa las notas ya conservadas de grupo interior y datos C1. No modifica fuentes, acción, observadores, umbrales o trabajador. No repite F0…F5. El nuevo contraste racional de filas polinómicas se publica antes de ejecutarse, con ℓ=0…4, grados de u=0,2,4,6, h=1 y1/2 y las primeras tres filas fijas. No se usan estados físicos para seleccionar casos o coeficientes. Se conservan todos los coeficientes; un desacuerdo exige investigar esta derivación, sin alterar el piloto para aprobarla.

## Filas a distancia de origen O(h)

Escribiendo q_i=r_i^ℓu_i, r_i=h(i+1/2), el operador registrado es L2q=r^ℓT_hu. Sus masas son m_i=h(r_i²+h²/12)r_i^(2ℓ) y sus caras c_i=(2ℓ+3)Σ_{j≤i}m_j/[(i+1)h²]. Por homogeneidad exacta, T_h aplicado a r^s es h^(s−2) veces la misma secuencia en h=1. Las sucesivas composiciones no introducen otro parámetro. Para P3:

\[
L_{3,h}q=r^\ell[T_h-h^2T_h^2/12+h^4T_h^3/90]u.
\]

T_h1=0 y T_hr²=2(2ℓ+3) exactamente en toda fila cuyo stencil no alcance la frontera exterior. Por tanto P3 reproduce ambos monomios; no hay un término de error originado por u0 o u2. En u=r4 cada composición contribuye a la misma escala h² en las filas i fijas. Así el nuevo término h4T_h³, aunque comienza en h4 a radio fijo positivo, puede cambiar el coeficiente de h² cerca del origen. No procede insertar r=h/2 en una expansión demostrada sólo para r fijo.

Si u admite una expansión par u0+u2r²+u4r4+O(r6) con resto controlado cerca del origen, el error en cada una de las tres primeras filas es r_i^ℓ[h²u4 C_{ℓ,i}+O(h4)]. Los coeficientes C se calculan por aritmética racional independiente de las fuentes M2. Diez puntos permiten tres aplicaciones y conservar tres filas sin ningún cierre exterior artificial. Para el resto basta usar la homogeneidad de las filas y acotar los valores O(h6) en su stencil: T_h cuesta O(h−2); cada término compuesto queda O(h4) después de sus factores.

Con W_i=h(r_i²+h²/12), la norma ponderada de ese error en un número fijo de celdas es O(h^(ℓ+7/2)). Es una cota local del residuo espacial suave, no de la solución, ni de una banda cuyo número de celdas crezca al refinar. No demuestra que el origen carezca de influencia histórica. Tampoco puede aplicarse sin verificar regularidad par a un nudo C1 alejado del origen.

## Frecuencias radiales exactas del operador congelado libre

B=W^(1/2)A2W^(−1/2) es simétrica positiva. El operador P3 tiene exactamente sus autovectores y autovalores p3(λ)=λ+αλ²+βλ³. Para μ²≥0, ω3=√(μ²+p3(λ)) y ω3−ω2=βλ³/(ω3+ω2)>0. Elevar la frecuencia no prueba una mejora frente a una frecuencia radial continua ω*: reduce su error absoluto exactamente cuando ω3+ω2≤2ω*; fuera de ese caso puede sobrecorregir. Esta condición no permite identificar la discretización con menor error de una trayectoria acoplada, porque cambian amplitudes, historias e interpolación entre mallas.

Para un oscilador libre la propagación en las variables de la norma original (q,v/μ), μ>0, es

\[
P_\omega(t)=\begin{pmatrix}\cos(\omega t)&\mu\sin(\omega t)/\omega\\-\omega\sin(\omega t)/\mu&\cos(\omega t)\end{pmatrix}.
\]

La matriz exacta, y no sólo tδω, controla los errores de q y v. Si C_ab es la prolongación en las dos bases radiales, cada pareja aporta C_ab[P_{ωc,b}−P_{ωf,a}]. Se conservan las diferencias iniciales y todos los cruces. El defecto de fase se satura y una aproximación lineal puede ser inútil a tiempos largos. Las referencias ocupadas D2 y el negativo inicialℓ2 permanecen; no se repite ese cálculo ni se anuncia mejora universal.

## Colas de propagación de la matriz radial finita

Sea H=B+αB²+βB³+μ²I, para el problema libre congelado. H tiene rango de stencil tres y es positiva. C(t)=cos(t√H) y S(t)=sin(t√H)/√H están definidos por sus series enteras. Si d=|i−j| y m0=ceil(d/3), entonces (H^m)_ij=0 para m<m0. Con Λ≥||H||2 se obtiene

\[
|C(t)_{ij}|\le\sum_{m\ge m_0}\frac{(|t|\sqrt\Lambda)^{2m}}{(2m)!},\qquad
|S(t)_{ij}|\le |t|\sum_{m\ge m_0}\frac{(|t|\sqrt\Lambda)^{2m}}{(2m+1)!}.
\]

Son cotas factoriales válidas para cualquier caja radial finita. Una cota explícita de Λ es p3(g)+μ², donde g=max_i(B_ii+|B_i,i−1|+|B_i,i+1|) por Gershgorin. La coordenada física recupera el factor √(W_j/W_i); no se elimina ese peso cerca del origen. Las series pueden dar valores muy grandes y no se afirma que certifiquen el2% en R220,τ160.

La matriz A2 tiene caras no nulas y conecta celdas vecinas; el término de mayor alcance de H también conecta tres celdas. Por ello existen entradas de potencias a distancias arbitrarias dentro de la caja y colas analíticas a tiempos pequeños. La matriz semidiscreta no posee en general un cono de soporte exactamente compacto. La cota de velocidad de grupo ≤1 del interior homogéneo no permite descartar por sí sola una influencia de la frontera radial. M2 añade un Jacobiano variable local y acoplamiento: H libre positivo no prueba positividad del Hessiano total ni estabilidad de esa historia. La sensibilidad de caja requiere los contrastes registrados después de una pareja positiva, o el diagnóstico correspondiente si P3 falla.

CP12 sigue abierto; CP11 aceptado. Estas identidades no sustituyen las métricas, la causalidad en tres ventanas, la tercera malla ni las pruebas de referencia y robustez.
