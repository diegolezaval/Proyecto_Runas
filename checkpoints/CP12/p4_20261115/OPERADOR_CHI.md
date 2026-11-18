# Operador espacial discreto del mediador χ

En el modelo de dos campos M2, $\Phi$ es complejo, $\chi$ es real y $\tau$ es el tiempo en las unidades del benchmark. Se expande $\chi(r,\theta,\varphi)=\sum_{\ell,m}q_{\ell m}(r)Y_{\ell m}(\theta,\varphi)$ en armónicos esféricos reales ortonormales. Para un $(\ell,m)$ fijo, $q_i$ es el coeficiente de la **celda** $i$. El operador radial depende de $\ell$ y es el mismo para cada $m$ de ese grado.

## Malla, flujos y acción en una celda

Sea $N$ el número de celdas uniformes de una esfera de radio $R$, con $\delta=\Delta r=R/N$. Para $i=0,\ldots,N-1$ las caras son $x_i=i\delta$ y $x_{i+1}$, el centro es $r_i=(x_i+x_{i+1})/2$ y el peso radial es

$$
w_i=\int_{x_i}^{x_{i+1}}r^2\,dr=\frac{x_{i+1}^3-x_i^3}{3},\qquad
p_i=r_i^\ell,\quad u_i=\frac{q_i}{r_i^\ell},\quad
\mu_i=w_i p_i^2 .
$$

El factor angular ya está integrado. En la cara interior $x_j$, $1\le j<N$, el coeficiente y el flujo orientado hacia radios crecientes son

$$
c_j=\frac{2\ell+3}{x_j\,\delta}\sum_{k=0}^{j-1}\mu_k,\qquad
F_j=c_j(u_j-u_{j-1}).
$$

En el origen, la regularidad de $q=r^\ell u$ permite flujo $F_0=0$. En la cara exterior se fija $u(R)=0$ y se usa la distancia de media celda hasta el borde. Con la misma suma radial,

$$
c_R=\frac{2(2\ell+3)}{R\,\delta}\sum_{k=0}^{N-1}\mu_k,\qquad
F_N=-c_R u_{N-1}.
$$

El operador positivo de base, que aproxima el negativo del laplaciano modal $\partial_r^2+2r^{-1}\partial_r-\ell(\ell+1)r^{-2}$, actúa por

$$
(A_{2,\ell}q)_i=\frac{F_i-F_{i+1}}{w_i p_i}.
$$

El signo se comprueba con su forma de energía, $\sum_i w_i q_i(A_{2,\ell}q)_i=\sum_{j=1}^{N-1}c_j(u_j-u_{j-1})^2+c_R u_{N-1}^2$. Para $\ell=0$, $c_j=x_j^2/\delta$ y $c_R=2R^2/\delta$.

## Operador completo y ecuación de movimiento

Con $A=A_{2,\ell}$,

$$
\boxed{A_{\chi,\ell}=A+\frac{\delta^2}{12}A^2+
\frac{\delta^4}{90}A^3+\frac{\delta^6}{560}A^4.}
$$

Cada potencia aplica de nuevo el mismo operador de celda, incluidos ambos cierres. Sea $s=|\Phi|^2$ en los puntos angulares y $\Pi_{\ell m}b$ la proyección de $b$ sobre el armónico con la cuadratura del cálculo. En las unidades normalizadas, $M$, $g$ y $h$ son respectivamente la masa del mediador y los acoplamientos de $\chi s$ y $\chi^2s/2$ en el potencial. Para cada celda,

$$
\ddot q_{\ell m,i}=-(A_{\chi,\ell}q_{\ell m})_i
-M^2q_{\ell m,i}-\big[\Pi_{\ell m}(g\,s+h\,s\chi)\big]_i .
$$

La corrección afecta a la fuerza espacial de $\chi$. Los términos locales vienen de derivar $M^2\chi^2/2+g\chi s+h\chi^2s/2$. El campo $\Phi$ usa los volúmenes finitos de su propia ecuación. [Fuerza y cuadratura](../../../herramientas/continuar_no_radial_m2.py) · [Parámetros y normalización](../../../herramientas/modelo_m2.py)

## Procedencia de los coeficientes y cotejo

En el problema plano de paso $\delta$, el símbolo positivo de la diferencia de tres puntos es $a=4\sin^2(k\delta/2)/\delta^2$. Invertirlo en la rama $0\le k\delta\le\pi$ da $k^2=4\arcsin^2(\sqrt{s_*}/2)/\delta^2$, con $s_*=\delta^2a$. Los cuatro primeros términos de $4\arcsin^2(\sqrt{s_*}/2)=\sum_{n\ge1}2s_*^n/[n^2\binom{2n}{n}]$ producen los coeficientes de la caja anterior. Son coeficientes analíticos del símbolo plano. La geometría y los pesos radiales dejan en general un residuo de orden $\delta^2$, incluso con la cuarta potencia. [Derivación del residuo radial](../residuo_tau80_20261018/DERIVACION_GEOMETRIA.md)

En el código, `lap2_general` devuelve $L=-A$. La fuerza espacial implementa $L-\delta^2 L^2/12+\delta^4 L^3/90-\delta^6 L^4/560$. La matriz del resolvente construye el polinomio positivo. Como cotejo directo, usando las 17 columnas de la identidad, $\delta=0{,}125$ y $\ell=0,\ldots,4$, la diferencia relativa en norma matricial infinito entre la fuerza del código y el negativo del polinomio de caras fue como máximo $1{,}9\times10^{-16}$. Los controles de la campaña incluyen positividad, cierres, nueve bandas y acción. [Flujos implementados](../../../trazabilidad/CP12_recuperacion_independiente/2f01ea6e32b2/analysis/backend_candidato/backend.py) · [Fuerza completa](p4_backend.py) · [Matriz positiva](prueba_pasiva/operador_pasivo.py) · [Certificado de controles](CERTIFICADO_CONTROLES_P4.json)

## Alcance de la campaña P4

Se evolucionaron los datos de Cauchy procedentes de la preparación radial CP04 en $t=1200$, con la deformación cuadrupolar triaxial registrada de amplitud $\epsilon=0{,}020$, $R=220$, grados hasta $L=4$ y $0\le\tau\le160$. En veinte cierres de ocho unidades se cotejaron las mallas $\delta=0{,}125$, $0{,}0625$ y $0{,}03125$. En $\tau=160$ la discrepancia de $\chi$ en espacio de fases pasó de 1,014856 % al comparar las dos primeras a 0,018464 % al comparar las dos últimas. Frente a la referencia Galerkin, la lectura de la malla más fina fue 0,028900 % y la estimación conjunta empírica, 0,098480 %. El presupuesto temporal se cumplió en los veinte cortes. Las variantes de caja, truncamiento y amplitud cuantificaron la sensibilidad de esa preparación. El cierre de CP12 está circunscrito a la configuración base y al horizonte indicado. Una Q-ball estacionaria, un contacto de amplitud finita o un ciclo de Reserva requieren su propio contraste. [Piloto](piloto_t0_t160/tramo_0152_0160/VALIDACION_FINAL.json) · [Tercera malla](tercera_malla_20261116/INFORME.md) · [Galerkin](referencia_galerkin_20261116/INFORME.md) · [Decisión de cierre](validacion_20261116/INFORME.md)
