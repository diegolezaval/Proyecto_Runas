# Hipótesis P3: composición positiva mínima del operador de χ

Esta propuesta responde al diagnóstico pasivo publicado en `68f5ffbc53dccded58bcdbbfb3ac9065102b0a74`. El ensayo P2 terminó con negativo espacial en τ80 y no se reanuda. La nueva rama es `ciencia/cp12-residuo-p3-20261018`. CP12 sigue abierto.

## Acción discreta y conservación

Se mantienen M2, Θ, la masa de volumen finito W, el potencial angular, todos los términos de acoplamiento, los datos de Cauchy y Φ-FV. Para cada ℓ, sea A2=−L2 el operador regular radial ya definido, q=r^ℓu, m_i=W_i r_i^(2ℓ), c_i=(2ℓ+3)Σ_{j≤i}m_j/(r_{i+1/2}h), b=2(2ℓ+3)Σm/(Rh). Su forma es

\[
\langle q,A_2q\rangle_W=\sum_i c_i(u_{i+1}-u_i)^2+b u_N^2.
\]

W,c,b son positivos. Esta identidad demuestra simetría y positividad estricta: una energía nula requiere u constante y u_N=0. No se añade una condición de contorno diferencial distinta: se compone el mismo operador finito, incluido su cierre de frontera y origen regular.

Se propone únicamente

\[
A_3=A_2+\alpha A_2^2+\beta A_2^3,\quad
\alpha=h^2/12,\quad\beta=h^4/90,\qquad
L_3=L_2-\alpha L_2^2+\beta L_2^3.
\]

Como B=W^(1/2)A2 W^(−1/2) es simétrica positiva, B+αB²+βB³ tiene autovalores λ+αλ²+βλ³>0 y la misma base. No hay ajuste de coeficientes a un porcentaje. El Hamiltoniano propuesto es el de P2 más

\[
\Delta E_{32}=\frac\beta2\langle A_2q_\chi,A_2(A_2q_\chi)\rangle_W.
\]

Puede evaluarse por la forma positiva de caras y frontera aplicada a A2qχ, sin productos cancelantes. Su derivada es βWA2³qχ; por tanto, el flujo variacional produce exactamente L3 en χ. La energía cinética conserva los pesos (2,2,1). No cambia el potencial ni su Hessiano acoplado. La simetría U(1) de Φ, las degeneraciones en m y la forma cuadrática de carga permanecen. Esto prueba conservación semidiscreta, no conservación de un integrador temporal ni estabilidad del Hessiano no lineal completo.

Además se seguirá midiendo la **energía FV original**, distinta de la consistente. Si ΔG=E3−EFV, la identidad de trabajo es dEFV/dτ=ΣW vχ (L3−LFV)qχ=−dΔG/dτ. Ambas puertas de energía originales se conservan por separado.

## Dispersión, consistencia y límites

En el interior plano, x=h²λ2=4sin²(kh/2). La serie inversa exacta es h²k²=Σ a_j x^j, con a_j=2/[j² binom(2j,j)]. Los tres primeros coeficientes son 1,1/12,1/90. P3 cancela el primer término omitido por P2 y deja h²λ3=(kh)²−(kh)^8/560+O((kh)^10). Se comprobará esta expansión con aritmética racional independiente.

Esto **no** convierte el operador radial en uno global de orden seis. La derivación y pruebas D1 establecen, a r fijo positivo,

\[
L_{3,h}(r^\ell u)=L_\ell(r^\ell u)+
\frac{h^2r^\ell}{6(2\ell+1)}\left(\frac{u''}{r^2}-\frac{u'}{r^3}\right)+O(h^4).
\]

La nueva contribución comienza en h⁴ sobre funciones suficientemente regulares y no elimina ese término h². El límite del paréntesis para u par es regular, pero no se presume una expansión uniforme en la primera celda ni en la frontera. Se medirán ambos residuos aparte. La preparación cuadrupolar CP04 es C1 entre ciertos nudos: su regularidad impide deducir una ventaja de orden alto sobre la trayectoria a partir de funciones fabricadas suaves.

La matriz simétrica B³ tiene ancho tres. Sus diagonales son d_i³+e_{i−1}²(2d_i+d_{i−1})+e_i²(2d_i+d_{i+1}); sus tres bandas superiores son e_i[d_i²+d_i d_{i+1}+d_{i+1}²+e_{i−1}²+e_i²+e_{i+1}²], e_i e_{i+1}(d_i+d_{i+1}+d_{i+2}) y e_i e_{i+1}e_{i+2}. Se contrastarán con productos dispersos independientes, sin compartir este constructor. Φ mantendrá su resolvente tridiagonal; χ usará siete bandas y las mismas tablas GL7/6, paso y criterio de iteración.

## Motivo del ensayo y alternativas

El canal operador χ acoplado es suficiente en las tres ventanas condicionadas a las historias conservadas. El 99,63018% de la potencia de su defecto observado80 tiene k>8. Las referencias espectrales ocupadas favorecen P3 frente a P2 en80, pero la exposición inicialℓ2 empeora ligeramente; ese negativo está conservado. La exposición libre no predice la trayectoria no lineal.

P3 es la extensión mínima de P2 con coeficiente fijo que contrasta ese defecto de dispersión. P4 añade complejidad y no se ensaya automáticamente. Una corrección geométrica de mayor orden con masa/potencial nuevos requiere una derivación conjunta más amplia; no se sustituye aisladamente la fuerza. Cambiar fuente, preparación, fase, tolerancias o umbrales no está justificado. Si P3 falla se conserva el negativo y se investiga antes de seleccionar otra hipótesis.

El ensayo puede discriminar utilidad de esta extensión conservativa. Incluso un resultado positivo no demuestra que la dispersión sea la única causa, ni elimina las obligaciones de una tercera malla, referencia, independencia angular/de caja y robustez. Evidencia numérica; ninguna validación física experimental.
