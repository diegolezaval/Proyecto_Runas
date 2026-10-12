# Símbolo interior y propagación: resultado pasivo

Prerregistro publicado antes de la prueba: `7d87c80ea30147573829945e191cc9e30398a493`. Cero pasos M2; ninguna modificación de las trayectorias o de las catorce fuentes. La masa usada es la original, 100. Las ondas son manufacturadas; sus amplitudes no proceden de χ.

Para θ=kh, η=(1−cosθ)/(2+cosθ), a=3/4+21η/64 y b=1/4+15η/64, la prolongación interior del CubicSpline entre centros con razón dos es

\[
I_h e^{ikr}=A e^{ikr}+B e^{i(k+2\pi/h)r},\quad
A=a\cos(\theta/4)+b\cos(3\theta/4),\quad
B=a\sin(\theta/4)-b\sin(3\theta/4).
\]

La ecuación de las segundas derivadas del spline es M[j−1]+4M[j]+M[j+1]=6(q[j−1]−2q[j]+q[j+1])/h². Sobre la onda, M[j]=−6ηq[j]/h². Insertarla en los puntos a un cuarto de celda produce la fórmula. La imagen se entiende módulo el número de onda de la malla fina. La comparación con el interpolador original en el interior R220 da un residuo máximo 1.9633e−13, frente a la tolerancia preregistrada 2e−11.

El símbolo original es κ₂²=4 sin²(kh/2)/h²=k²−h²k⁴/12+O(h⁴). La composición positiva derivada tiene κ₄²=κ₂²+h²κ₂⁴/12=k²−h⁴k⁶/90+O(h⁶). El coeficiente 1/12 es fijo, independiente de las amplitudes y errores de χ. La frecuencia es √(10000+κ²).

| k | Fase entre mallas a τ160, original | Composición candidata |
|---:|---:|---:|
| 2 | 0.0124650 | 0.000129422 |
| 4 | 0.1977703 | 0.008133807 |
| 8 | 3.0598571 | 0.484085176 |
| 12 | 14.6501507 | 4.886543112 |
| 20 | 94.6421892 | 71.420915737 |

Son fases en radianes del modelo interior, no errores físicos ni pruebas de la puerta del 2 %. La mejora en k20 es pequeña. El orden de los errores de frecuencia del símbolo tiende a dos y cuatro, respectivamente. El candidato radial completo, con sus fronteras, conserva el resultado negativo previo: orden espectral global dos y empeoramiento de algunos primeros modos. No se declara un operador global de cuarto orden.

Para datos q(0)=1, v(0)=−i100, sea Pω(t)=cos(ωt)−i(100/ω)sin(ωt). En cada componente j de la prolongación, el conmutador es a[j](ωf[j]²−ωc²)Pωc. Su respuesta libre de Duhamel, con estado inicial cero, es a[j](Pωc−Pωf[j]); ambas derivadas iniciales se anulan. La parte inicial tiene amplitud A−1 en la componente baja y B en la imagen. Su suma con Duhamel reproduce exactamente A Pωc−Pωf y B Pωc, respectivamente, tanto en q como en v/100. El residuo máximo es 2.9297e−16. Los términos cruzados se conservan en `resultados.json`.

Así, la norma instantánea del conmutador, incluida una imagen de interpolación, no determina por sí sola su peso en el defecto propagado. Tampoco lo determina un residuo sobre un armónico regular sin amplitud e historia. Esta identidad explica por qué se necesitan presupuestos de respuesta y cancelaciones.

El resultado apoya una prueba posterior del mecanismo de dispersión, pero no reconstruye la geometría radial, el fondo no lineal, la realimentación ni la historia de CP12. El trabajador original continúa sin cambios. Una corrección física exige la identificación causal final, una campaña independiente desde las condiciones de Cauchy originales y las pruebas de convergencia, conservación y estabilidad con criterios intactos. CP12 permanece abierto.
