# Datos C1: lo que puede deducirse sobre el orden de una trayectoria

El diagnóstico D1/D2 conservado demuestra saltos no nulos de segunda derivada de la perturbación χ preparada a partir de CP04. Esta nota desarrolla una consecuencia analítica y sus límites; no ejecuta M2, no repite controles ni modifica datos, candidato o puertas. No estima un orden observado de P3.

## Referencia lineal explícita

Considérese sólo una onda escalar en un dominio plano infinito, localizada suavemente lejos de extremos, con masa constante no negativa. Si f es C1, suave por tramos y tiene saltos J_j de segunda derivada en x_j, la integración por partes en cada tramo da

\[
\widehat f(k)=\frac{1}{(ik)^3}\sum_j J_j e^{-ikx_j}+O(|k|^{-4}),
\]

salvo el signo según la convención de salto. Esto permite f∈H^σ para σ<5/2; no da regularidad arbitraria ni, en general, H^(5/2). Es una afirmación sobre el modelo localizado y las derivadas por tramos, no un ajuste del espectro M2 final.

Para un símbolo de onda con defecto de frecuencia |ω_h−ω|≤C h^p |k|^(p+1) en su banda resoluble, la diferencia de factores de propagación está acotada por C min(1,T h^p |k|^(p+1)). Para 0≤s≤p+1,

\[
\min(1,T h^p |k|^{p+1})
\le C_T h^{ps/(p+1)} |k|^s.
\]

Aplicando Parseval a la solución de onda y su velocidad, y controlando también el error de amplitud ω_h/ω y la cola no resuelta, se obtiene en este problema de referencia

\[
\|e_v(T)\|_{L^2}+\|e_q(T)\|_{H^1}
\le C_T h^{ps/(p+1)}
\left(\|q_0\|_{H^{s+1}}+\|v_0\|_{H^s}\right).
\]

Los modos pequeños se absorben en C_T; la equivalencia de símbolos positivos en la banda controla las amplitudes. Se supone una restricción inicial consistente o proyección espectral y se incluye su cola. La cota no certifica automáticamente un interpolador particular. Como la velocidad contiene ω sin(ωT)q_0, la regularidad exigida a q_0 tiene una derivada más que la de v_0.

Si la única información es la regularidad C1 con esos saltos, este razonamiento sólo permite s<3/2. Para las expansiones interiores respectivas, los exponentes que se acercan por debajo a ps/(p+1) son:

| Símbolo interior | p | Límite de los exponentes deducibles de esta cota |
|---|---:|---:|
| FV plano | 2 | 1 |
| P2 plano | 4 | 6/5 |
| P3 plano | 6 | 9/7 |

Estos números son garantías posibles de una **cota de referencia**, no tasas medidas, techos universales ni predicciones de la campaña. Datos específicos, cancelaciones, ventanas y amplitudes pueden dar errores menores. Tampoco se ha demostrado que los saltos iniciales dominen la generación no lineal del espectro observado en80; ℓ4 era inicialmente nulo.

## Consecuencias para CP12

No procede deducir orden seis de una trayectoria por la expansión interior, ni deducir orden dos en la norma con velocidad únicamente de las pruebas suaves. El operador radial mantiene además su defecto geométrico h², origen y cierre finito; M2 añade acoplamiento y fuente no lineal. La referencia anterior no demuestra una cota de ese sistema completo.

La tercera malla deberá medir reducción de diferencias con proyección común y examinar direcciones, modos, ventanas y régimen asintótico; no fijar ni ajustar de antemano un exponente para lograr aceptación. La referencia independiente y las sensibilidades de interpolación, angular y caja permanecen necesarias. Las métricas y umbrales originales no cambian. No se suaviza ni sustituye CP04. CP12 sigue abierto; evidencia numérica, sin validación física experimental.
