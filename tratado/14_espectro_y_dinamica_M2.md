# Solución, espectro y dinámica del mismo M2

## 14.1. Qué se ha resuelto

Se resuelve \(\Phi=f(r)e^{i\omega t}\), \(\chi=z(r)\), con \(\hat\omega=0.9\), derivadas nulas en el origen y campos nulos en una frontera remota. Se incluyen ambos campos y sus gradientes. Las unidades son las de (13.6); en este capítulo las variables son adimensionales.

\[
f''+\frac2r f'=(1-\omega^2+198f^2+\hat g z+50z^2)f,
\]

\[
z''+\frac2r z'=10000z+\hat g f^2+100zf^2,
\quad\hat g=100\sqrt{200}.
\tag{14.1}
\]

El método de colocación usa un Jacobiano analítico. La condición en el origen se implementa mediante el término singular regular de `solve_bvp`, no dividiendo por cero. El perfil inicial sirve para elegir la rama no nula; los residuos y la identidad virial comprueban que no se ha confundido con la solución trivial.

| Radio de caja | Tolerancia solicitada | Nodos adaptados | \(\hat E\) | \(\hat Q\) | Residuo virial relativo |
|---:|---:|---:|---:|---:|---:|
| 40 | \(10^{-6}\) | 1068 | 2525.6589035 | 2745.7739135 | \(1.17\times10^{-10}\) |
| 50 | \(10^{-8}\) | 1319 | 2525.6589096 | 2745.7739203 | \(9.95\times10^{-12}\) |
| 60 | \(10^{-9}\) | 2402 | 2525.6589099 | 2745.7739207 | \(8.85\times10^{-13}\) |

La energía cambia \(1.34\times10^{-10}\) relativamente entre las últimas filas. \(f(0)=0.74601920535\), \(z(0)=-0.07827167224\) y \(E/Q=0.91983498383<1\). El último cociente impide la desintegración completa en cuantos libres de la misma carga por balance energético; no excluye todas las fragmentaciones, estados colectivos o inestabilidades.

Se cumple \(T+3U-3\omega^2I=0\). Las diferencias centradas con \(\delta\omega=0.0004\) y 0.0002 dan respectivamente \(dQ/d\omega=-219274.44\) y \(-219206.13\); \(dE/dQ=0.89999409\) y 0.89999852, convergiendo al valor termodinámico \(\omega=0.9\). Estos cálculos son de M2, no los de M1 reutilizados.

Los residuos son verificaciones numéricas ordinarias; no son intervalos rigurosos de existencia y unicidad para una solución exacta del continuo. Los perfiles completos están en `validacion/m2_perfil_convergente.csv`.

## 14.2. Operador lineal completo de dos campos

Con \(\Phi=e^{i\omega t}[f+(u+iv)/\sqrt2]\), \(\chi=z+\zeta\),

\[
\ddot u-2\omega\dot v+L_u u+C\zeta=0,\qquad
\ddot v+2\omega\dot u+L_vv=0,
\]

\[
\ddot\zeta+L_\chi\zeta+Cu=0,
\tag{14.2}
\]

\[
L_v=-\nabla^2+1+198f^2+\hat g z+50z^2-\omega^2,
\quad L_u=L_v+396f^2,
\]

\[
L_\chi=-\nabla^2+10000+100f^2,\qquad
C=\sqrt2f(\hat g+100z).
\tag{14.3}
\]

En (14.2), \(L_vv\) es \(L_v\,v\). La expansión en armónicos esféricos \(Y_{\ell m}\) desacopla los índices \(\ell\) y da degeneración \(2\ell+1\). Al transformar una amplitud radial \(q\) en \(rq\), cada diagonal contiene

\[
-\frac{d^2}{dr^2}+\frac{\ell(\ell+1)}{r^2}.
\]

Las condiciones regulares son amplitudes \(q=O(r^\ell)\) en el origen, y decaimiento o radiación saliente según se estudien estados ligados o dispersión. La caja numérica impone Dirichlet; sus modos extendidos no se confunden con modos ligados del espacio infinito.

## 14.3. Energía a carga fija: por qué un autovalor negativo no basta

El Hessiano de amplitud es

\[
H_\ell=\begin{pmatrix}L_{u,\ell}&C\\C&L_{\chi,\ell}\end{pmatrix}.
\]

En el sector radial, la segunda variación de (13.13), con coordenadas canónicas \((u,\zeta)\), contiene el operador

\[
K_0=H_0+\frac{4\omega^2}{I}|(f,0)\rangle\langle(f,0)|.
\tag{14.4}
\]

El producto interior de esta fórmula usa \(d^3x\). La transformación radial introduce el vector \((rf,0)\) y el factor \(4\pi\) se cancela en el cociente. Se verifica el término de rango uno mediante inversión de Sherman–Morrison, sin sustituirlo por un cambio local de potencial.

Un \(H_0\) con una dirección negativa puede coexistir con \(K_0>0\): la dirección no está libre a carga fija. La pendiente \(dQ/d\omega<0\), por sí sola, no prueba estabilidad de una rama arbitraria con varios modos negativos.

| \(R,N\) | \(\lambda_{min}(H_0)\) | \(\lambda_{min}(K_0)\) | \(\lambda_{min}(H_1)\) | \(\lambda_{min}(H_2)\) |
|---|---:|---:|---:|---:|
| 40, 500 | −0.02284472 | 0.20057676 | −0.000038849 | 0.04491860 |
| 40, 1000 | −0.02281501 | 0.20057713 | −0.000009729 | 0.04494643 |
| 40, 2000 | −0.02280757 | 0.20057722 | −0.000002435 | 0.04495340 |
| 60, 3000 | −0.02280757 | 0.19387455 | −0.000002435 | 0.04495340 |

Los cambios de \(K_0\) al aumentar el dominio son compatibles con aproximarse al borde esencial 0.19; no significan una pérdida de estabilidad. Las cuatro primeras raíces de cada Hessiano se calculan mediante desplazamiento por debajo de una cota inferior puntual del potencial matricial. Así se evitan confusiones entre «más próximos a cero» y «más bajos».

## 14.4. Todos los sectores angulares: reducción analítica

Para un perfil exacto positivo y monótono, se tienen identidades que no requieren cortar la suma en \(\ell=3\).

Primero, \(L_{v,0}f=0\). La transformación de estado fundamental da

\[
\langle v,L_{v,0}v\rangle=
\int f^2\left|\nabla(v/f)\right|^2d^3x\ge0.
\tag{14.5}
\]

El modo nulo es la fase global. Para \(\ell\ge1\), la barrera centrífuga añade una contribución positiva.

Segundo, las traslaciones satisfacen \(H_1(\sqrt2f',z')^T=0\). Si \(f'<0\), \(z'>0\), \(C>0\), se cambia el signo de la primera componente y se obtiene un operador con acoplamiento \(-C\) y estado nulo positivo \((a,b)=(-\sqrt2rf',rz')\). Para funciones de prueba radiales \((p,q)\),

\[
\langle(p,q),\widetilde H_1(p,q)\rangle=
\int_0^\infty\!\left[
a^2((p/a)')^2+b^2((q/b)')^2+
Cab(p/a-q/b)^2\right]dr\ge0.
\tag{14.6}
\]

La identidad se obtiene integrando por partes y usando las dos ecuaciones del estado nulo. Para todo \(\ell\ge2\),

\[
H_\ell=H_1+\frac{\ell(\ell+1)-2}{r^2}I_2,
\tag{14.7}
\]

de modo que no aparece una nueva dirección negativa a alto \(\ell\). Los términos giroscópicos \(\pm2\omega\dot q\) no realizan trabajo; un Hessiano positivo produce energía cuadrática conservada y excluye crecimiento exponencial de norma finita.

Estas identidades cubren todos los índices angulares **si se cumplen sus hipótesis para la solución exacta**. El perfil calculado es positivo y monótono en el intervalo con amplitud resoluble; sus colas decaen. Aun así, una inspección numérica de monotonicidad y los autovalores flotantes de \(K_0\) no constituyen una certificación del continuo. No se declara completada una prueba espectral rigurosa de esta Q-ball, y mucho menos de una guía tridimensional que aún no se ha resuelto.

## 14.5. Frecuencias, continuo y ceros de simetría

Se discretiza también el generador de primer orden

\[
\partial_t\binom{q}{\dot q}=
\begin{pmatrix}0&I\\-\mathcal H&-\mathcal G\end{pmatrix}
\binom{q}{\dot q},\quad q=(u,v,\zeta)^T,
\]

con \(\mathcal G\) antisimétrica. Se conservan en JSON los 18 autovalores encontrados alrededor de \(0.055i\) para \(\ell=0,1,2\); no se describe esta selección como un barrido de todo el generador.

En el exterior de la Q-ball, el espectro esencial es

\[
\sigma=\pm i(\sqrt{k^2+1}\pm\omega),\qquad
\sigma=\pm i\sqrt{k^2+10000},\quad k\ge0.
\tag{14.8}
\]

El umbral inferior es \(|\operatorname{Im}\sigma|=0.1\). El modo cuadrupolar \(\ell=2\) sí está ligado:

| \(R,N\) | Frecuencia \(\Omega_{\ell=2}\) |
|---|---:|
| 40, 500 | 0.04376526611 |
| 40, 1000 | 0.04377915147 |
| 40, 2000 | 0.04378262919 |
| 60, 3000 | 0.04378262869 |

El cambio al aumentar el dominio es \(4.94\times10^{-10}\). La convergencia espacial es de segundo orden; la extrapolación orientativa da aproximadamente 0.04378379. No se asignan a la última cifra más garantías que las del método.

El modo de fase, exactamente nulo en el continuo, aparece como \(\pm i\,0.00024634\), \(\pm i\,0.00012320\), \(\pm i\,0.00006162\) al refinar. La traslación aparece como un pequeño par **real** \(\pm0.00091524\), \(\pm0.00045803\), \(\pm0.00022912\). No se oculta ese par: tiende a cero como el paso de malla y corresponde a la ruptura numérica de la identidad de traslación. Leerlo como inestabilidad física sin estudiar convergencia sería incorrecto; borrarlo del informe también lo sería.

Los valores superiores a 0.1 cambian con el tamaño de caja y son discretizaciones del continuo. Los modos de fase y traslación, junto con sus posibles compañeros generalizados, permiten cambios de fase o posición; estabilidad orbital significa controlar la perturbación después de descontar esas simetrías, no exigir una posición absoluta fija.

## 14.6. Evolución no lineal de ambos campos

Se integran las ecuaciones originales en coordenadas radiales mediante volúmenes finitos conservativos y Verlet. Las variables son \(\Re\Phi,\Im\Phi,\chi\), sin eliminar el mediador. Se impone una perturbación de amplitud \(10^{-3}e^{-r^2/25}\) a \(f\); la velocidad de fase se ajusta para mantener la carga inicial discretizada. Este ajuste define datos iniciales, no una fuente ni preparación desde materia.

| Celdas | Paso temporal | Duración \(\tau\) | Máxima deriva relativa de energía | Máxima deriva relativa de carga |
|---:|---:|---:|---:|---:|
| 800 | 0.002 | 24 | \(1.12\times10^{-7}\) | \(1.33\times10^{-15}\) |
| 1600 | 0.001 | 24 | \(2.82\times10^{-8}\) | \(2.89\times10^{-15}\) |

La desviación relativa ponderada de amplitud permanece por debajo de \(3.33\times10^{-4}\). Se comprueba un transitorio radial pequeño y la conservación de ambos invariantes, con mejora de aproximadamente cuatro veces en la deriva energética. No es una prueba de todas las perturbaciones ni de retención durante segundos.

En la escala SI ilustrativa, \(24t_0=1.58\times10^{-14}\) s. Presentar este ensayo como demostración de funcionamiento macroscópico prolongado sería una extrapolación sin justificar. La caja es cerrada y no añade absorción artificial: sus resultados no estiman las pérdidas de un dispositivo abierto.

## 14.7. Estado exacto de la evidencia espectral

![Convergencia de campos, modos y dinámica](../graficos/M2_evidencia_numerica.svg)

Quedan demostradas analíticamente la estabilidad clásica del vacío, la hiperbolicidad del sector escalar y las identidades que reducen el problema angular de perfiles monótonos. Se obtienen soluciones y autovalores convergentes, un modo no radial ligado y dinámica radial conservativa. La positividad radial restringida es evidencia numérica fuerte, con margen positivo, pero no una certificación de operadores continuos por cotas de error rigurosas.

**No se ha obtenido estabilidad espectral completa de un dispositivo rúnico.** La solución aquí analizada es esférica. No tiene la geometría, terminales ni función de P-04; asignarle ese nombre no completaría la demostración.
