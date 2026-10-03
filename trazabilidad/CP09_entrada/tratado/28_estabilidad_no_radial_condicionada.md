# 28 · Estabilidad no radial: identidad analítica y continuación de CP04

## 28.1. Alcance de la pregunta

Se separan dos objetos. El resultado analítico se refiere a una **solución estacionaria exacta** que cumple las hipótesis del capítulo 27. El ensayo numérico parte de los seis campos de Cauchy guardados al final de CP04, en t=1200, que aún contienen movimiento radial y radiación. No se reemplaza ese estado por una solución estacionaria ni se repite su preparación.

Se reutiliza la identidad angular ya cerrada en 14.4, escrita aquí con las variables del capítulo 27. No es una identidad nueva ni se repite su campaña espectral. El avance de CP05 es la justificación analítica de la monotonía que antes se exigía como hipótesis sobre un perfil exacto. La identidad cubre todos los armónicos no radiales de la linealización estacionaria. No prueba estabilidad orbital no lineal, no resuelve el sector radial y no convierte los perfiles numéricos en soluciones exactas certificadas.

## 28.2. Segunda variación y normalización

Usar constantes dimensionales, a=m²−ω²>0, χ=−u, y escribir

\[
\Phi=e^{i\omega t}\left[f+\frac{x+i y}{\sqrt2}\right],\qquad
\chi=-u-z.
\]

El funcional conservado K=E−ωQ, expresado en el sistema que gira en fase con ω, tiene término cinético positivo. Para cada armónico real (ℓ,m), su parte cuadrática es

\[
K_2=\frac12\int_0^\infty r^2\left[\dot x^2+\dot y^2+\dot z^2+
(x,z)\mathcal A_\ell(x,z)^T+y\mathcal H_\ell y\right]dr.
\]

Las expresiones con operadores se entienden como formas cuadráticas, integrando por partes. Con Dᵣ=∂ᵣ²+2r⁻¹∂ᵣ,

\[
\mathcal A_\ell=-D_r I+\frac{\ell(\ell+1)}{r^2}I+
\begin{pmatrix}
a+6\lambda_0 f^2-gu+\frac h2u^2 & -W\\
-W & M^2+hf^2
\end{pmatrix},\qquad W=\sqrt2 f(g-hu)>0,
\]

\[
\mathcal H_\ell=-D_r+\frac{\ell(\ell+1)}{r^2}
+a+2\lambda_0 f^2-gu+\frac h2u^2.
\]

Las ecuaciones lineales incluyen los términos giroscópicos −2ωẏ en la ecuación de x y +2ωẋ en la de y. Estos términos se cancelan al derivar K₂ respecto del tiempo. No se confunde el Hessiano con el generador dinámico ni se eliminan las fluctuaciones de χ.

## 28.3. Identidades de positividad

La ecuación estacionaria da H₀ f=0. Para una función de prueba y regular y localizada,

\[
\langle y,\mathcal H_\ell y\rangle
=\int r^2 f^2\left[\partial_r(y/f)\right]^2dr
+\ell(\ell+1)\int y^2dr.
\tag{28.1}
\]

Por otra parte, la invariancia bajo traslación da

\[
\mathcal A_1 w=0,\qquad w=(-\sqrt2 f',-u')^T.
\]

El capítulo 27 establece w₁,w₂>0 para r>0. Es crucial que ambos componentes tengan el mismo signo y que el acoplamiento de A sea −W<0. Si η=(η₁,η₂), integrar por partes usando A₁w=0 da la identidad exacta

\[
\langle\eta,\mathcal A_1\eta\rangle
=\sum_{i=1}^2\int r^2 w_i^2\left[\partial_r(\eta_i/w_i)\right]^2dr
+\int r^2 W w_1w_2(\eta_1/w_1-\eta_2/w_2)^2dr\ge0.
\tag{28.2}
\]

Primero se demuestra para pruebas suaves compactas en 0<r<∞. La identidad y la no negatividad se extienden por cierre al dominio de la forma con regularidad en el centro y energía finita. Los cocientes no suponen valores no nulos de w en los extremos; se usa la aproximación por funciones de prueba en el interior.

Para ℓ≥2,

\[
\langle\eta,\mathcal A_\ell\eta\rangle
=\langle\eta,\mathcal A_1\eta\rangle+
[\ell(\ell+1)-2]\int(\eta_1^2+\eta_2^2)dr>0
\]

si η≠0. Para ℓ=1 el núcleo de A₁ es el vector de traslación: la anulación de los cuadrados obliga a ηᵢ/wᵢ a ser la misma constante. Todos los valores de m comparten estos operadores.

## 28.4. Qué queda excluido y qué no

K₂ es no negativo en cada sector ℓ≥1, con parte cinética definida positiva. Su conservación excluye modos de energía finita que crezcan exponencialmente en esos sectores: una solución exponencial no trivial haría crecer una energía cuadrática positiva y constante. Para ℓ=1 se conserva el modo neutro de traslación; el movimiento del centro y las posibles contribuciones seculares asociadas no se cuentan como crecimiento exponencial. No se afirma una cota uniforme sobre la posición absoluta del centro.

Este argumento evita inferir la estabilidad de todos los ℓ a partir de unas raíces seleccionadas de caja. **Es la exclusión analítica condicionada de crecimiento exponencial lineal no radial de 14.4**, ahora enlazada con la monotonía demostrada en 27. No cubre nodos, fase espacial variable, giro, campos apoyados, soluciones fuera de las hipótesis ni el sector ℓ=0. Tampoco controla transferencia no lineal entre sectores, resonancias, fuga a largo plazo o amplitudes finitas arbitrarias. E03 continúa PARCIAL.

Una comprobación de la traducción de variables, sin recalcular perfiles ni autovalores históricos, comprueba los factores de normalización y la identidad de traslación mediante jets que satisfacen las ecuaciones estacionarias, y contrasta la identidad de forma por cuadratura independiente. Las muestras numéricas auditan el álgebra; la prueba funcional es la expuesta arriba. No se atribuye una revisión matemática externa ni una certificación formal por ordenador.

## 28.5. Ensayo finito que continúa CP04

La campaña está prerregistrada en `datos/ensayo_no_radial_CP06.json`. Se usan todos los armónicos reales hasta L, incluidos todos sus m. La integral angular del potencial cuártico es exacta para el espacio retenido mediante Gauss–Legendre y cuadratura uniforme azimutal; las fuerzas son su gradiente proyectado. La radial utiliza la misma acción de volúmenes finitos y la evolución es Verlet sin amortiguamiento. El mediador permanece dinámico.

Los cuatro campos radiales Φ, Φ̇, χ, χ̇ se interpolan desde el NPZ fino de CP04, sin volver a la gaussiana. La perturbación es una deformación inicial triaxial cuadrupolar, δq=−ε r exp[−(r/20)⁴] q′ H₂, aplicada también a las velocidades. H₂ combina cinco armónicos reales de ℓ=2 y tiene media cuadrática angular uno. Se contabilizan por separado su energía y carga añadidas, el cambio de malla y frontera, y el exterior que no se evoluciona en este ensayo. La creación física de esa perturbación no se da por derivada.

El núcleo observado es r<40; la ventana adicional es 0≤τ≤160. Las cajas R=220 y 260 tienen margen causal continuo de 20 y 60 después de esa ventana. La comparación de cajas comprueba también el efecto numérico sobre el núcleo; la sola cota de causalidad continua no certifica el esquema discretizado. El estado original de R=1300 se mantiene íntegro con su radiación exterior. No se afirma haber evolucionado esa energía exterior en el experimento truncado.

Las decisiones numéricas y los valores de convergencia se registran en `validacion/P06/no_radial/resultados.json` y en el informe CP06 cuando la campaña termine. Un ensayo que pase sólo respalda la familia de deformaciones, la ventana, el benchmark y las resoluciones declaradas.

## 28.6. Refinamiento posterior a CP06

CP07 conserva el fallo angular L2→L4 y las ocho evoluciones Verlet terminadas. La comparación de posiciones del mediador reveló un error que las normas de Φ y la conservación no detectaban. Los integradores de masa exacta ensayados no resolvieron la ventana completa con paso grueso: el centrado reduce el error inicial pero llega a una deriva energética de 2,354 % en el caso largo h=.5, Δt=.004. Su control Δt=.002 sí completa la ventana con balance. Todos los estados y fallos permanecen registrados.

El refinamiento DOP853 integra las fuerzas completas de la misma acción, con tiempo de reinicio explícito y conservación vigilada en cada paso aceptado. Tres ejecuciones completan τ=160: h=.5 con rtol=10⁻⁸ y 10⁻⁹, e h=.25 con rtol=10⁻⁹; atol=rtol/100 y paso máximo .02. Los pilotos se continuaron desde τ=8 y el control espacial interrumpido desde τ=120. El error temporal final de χ es 0,00191 % respecto de la perturbación inicial.

El diagnóstico adicional incluye velocidades: la norma es la raíz de ∫_{r<40} (|δq|²+|δv|²/masa²), relativa a la perturbación inicial del mismo campo. Se suman todos los modos no radiales y se elimina únicamente la fase U(1) global de Φ. Así una coincidencia momentánea de posiciones no oculta un error de oscilación. El error temporal de χ en esa norma es 0,00272 %.

El refinamiento espacial h=.5→.25 falla todavía: 4,03 % en posiciones de χ y 5,01 % incluyendo velocidades. Se conserva el fallo y se prerregistra h=.125 con la misma tolerancia fina. CP07 no declara cerrada esa prueba pendiente. La comparación se actualizará sólo al concluir la nueva evolución, manteniendo este antecedente y el límite del 2 %.

## 28.7. Cierre del refinamiento en CP08

La nueva malla h=.125 completó τ=160, continuando el estado guardado a τ=48 tras la pausa. Se mantienen rtol=10⁻⁹, atol=10⁻¹¹, paso máximo .02, L=4, R=220 y ε=.02. No se repitió ninguna de las once evoluciones ya terminadas de la campaña.

La comparación h=.25→.125 da un error de norma temporal de Φ de 0,152733 %; los campos finales dan Φ 0,285106 % y χ 3,45323 %. Incluyendo velocidades: Φ 0,929822 %, χ 5,04292 %. Puerta del subensayo: **REFINAMIENTO_PENDIENTE**; el límite espacial se mantiene en 2 %.

El control temporal fino ya cerrado y el control angular L4→L6 se reutilizan. Los errores gruesos y los fallos de conservación anteriores no se borran ni se reinterpretan como inestabilidad física. No se afirma una convergencia conjunta certificada de espacio, tiempo y truncación angular: son los controles individuales declarados, sobre una perturbación concreta y una ventana finita.

La implementación opcional del potencial en C se introdujo al reanudar τ=48, después de una auditoría que obtuvo igualdad exacta de las fuerzas en las cinco muestras comprobadas. No cambia la acción ni las tolerancias. Se conservan los incidentes de ejecución y se añadió un bloqueo de escritor único, verificado sin repetir evolución. E03/E04/RES0/RES1 continúan PARCIALES; faltan, entre otros, modos impares y otras perturbaciones finitas, fuente primaria, apagado, retroacción y ciclo.

El diagnóstico CP08 de las tres mallas obtiene una reducción de 3,94 para posiciones de Φ, pero 0,993 para χ con velocidades. La diferencia inicial fina de χ en esa norma es 0,00620 %. La causa del error tardío no queda identificada: no se extrapola un orden de convergencia de χ ni se promete que otra malla resolverá la puerta. El siguiente protocolo debe discriminar la fase rápida y los errores espaciales/temporales conjuntamente.
