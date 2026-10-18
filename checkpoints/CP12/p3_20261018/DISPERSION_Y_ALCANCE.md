# P3: velocidad de grupo interior y límites de la afirmación causal

Esta nota añade una identidad analítica al candidato ya fijado en c7a61e6. No cambia su operador, configuración, puertas ni protocolo; no repite F0…F5 ni evoluciones. El control racional adjunto se registra antes de ejecutarlo. El piloto sigue condicionado a cada frontera original.

En una región plana homogénea, con paso h, θ=kh en [0,π], x=4sin²(θ/2) y masa constante μ²≥0, el símbolo es p(x)=x+x²/12+x³/90. La frecuencia satisface h²ω²=p(x)+μ²h². Por derivación directa,

\[
v_g^2=\frac{x(1-x/4)[p'(x)]^2}{p(x)+\mu^2h^2},\qquad
\frac{p(x)}{x}-(1-x/4)[p'(x)]^2
=\frac{x^3}{80}+\frac{x^4}{600}+\frac{x^5}{3600}\ge0.
\]

Luego |v_g|≤1 para toda la banda; en x=0 se toma el límite correspondiente. P3 no introduce una rama de grupo superluminal en este problema lineal interior. Esta identidad es distinta de la expansión de orden comprobada en F0. El control adjunto usa sólo fracciones racionales y multiplicación de polinomios, sin cargar el backend ni trayectorias.

La expansión inversa exacta 4arcsin²(√x/2)=Σ[j≥1]2x^j/[j² binom(2j,j)] tiene coeficientes positivos. P3 retiene los tres primeros: para masa nula su velocidad de fase sigue por debajo de la continua fuera de θ=0. En Nyquist, p(4)=272/45 frente a θ²=π². Mejorar el primer término omitido no elimina el defecto a kh finito. La nueva banda también aumenta la frecuencia máxima del problema plano respecto de P2; el integrador adaptativo debe seguir verificándose con las tolerancias originales.

La afirmación de velocidad de grupo se limita a un operador homogéneo infinito y una masa constante no negativa. No demuestra un cono causal estricto para la matriz radial finita, ausencia de colas semidiscretas, estabilidad del Hessiano no lineal M2, independencia de la caja ni precisión en el origen. Las potencias del mismo operador conservan su cierre variacional, pero requieren comprobar los efectos de frontera sobre los estados físicos. Tampoco eliminan el término radial h² ni la regularidad limitada de CP04 ya documentados.

Por ello siguen pendientes las tres ventanas originales, la tercera malla, la referencia y la independencia respecto de interpolación, truncamiento angular y caja. Ninguna inferencia sobre una corrección física experimental se obtiene de esta identidad. CP12 continúa abierto.
