# Dispersión local de referencia: fase acumulada y límites

La parte principal del operador original permite diferencias de fase apreciables entre h=.125 y .0625 para las ondas cortas del protocolo, incluso con integración temporal exacta. Es un diagnóstico analítico de una onda unitaria, no una medición de la solución CP12.

En el límite local de amplitud lentamente variable y geometría subdominante frente a k², una onda e^(ikr) satisface

\[
\kappa_h^2=\frac{4}{h^2}\sin^2\frac{kh}{2},\quad
\omega_h=\sqrt{M_\chi^2+\kappa_h^2},\quad
v_{g,h}=\frac{\sin(kh)}{h\omega_h}.
\]

Mχ=100 se leyó del modelo original. Para kh pequeño, la diferencia de fase entre las dos mallas tiene término principal

\[
\Delta\varphi(t,k)\simeq-\frac{t(h_c^2-h_f^2)k^4}{24\sqrt{M_\chi^2+k^2}}.
\]

La tabla usa las expresiones exactas del símbolo principal, no su expansión. Los cortes k son los prerregistrados del observador.

| k | Magnitud Δφ en τ24, rad | Magnitud Δφ en τ160, rad | vg, h=.125 | vg, h=.0625 | vg continuo |
|---:|---:|---:|---:|---:|---:|
| 2 | 0.00186975021 | 0.0124650014 | 0.01978838 | 0.0199439741 | 0.0199960012 |
| 4 | 0.0296655444 | 0.197770296 | 0.0383240291 | 0.0395531679 | 0.0399680383 |
| 8 | 0.458978564 | 3.05985709 | 0.0671204955 | 0.0764688159 | 0.0797452223 |
| 12 | 2.1975226 | 14.6501507 | 0.0793292005 | 0.10832071 | 0.119145221 |
| 20 | 14.1963284 | 94.6421892 | 0.0473352324 | 0.149244157 | 0.196116135 |

Se conserva también la fase firmada sin envolver. El contraste 2|sin(Δφ/2)| de ondas complejas es periódico: una coincidencia de fases en un instante puede reducirlo sin reducir la dispersión acumulada. Por ejemplo, k=20 pasa de 1.45542 en τ24 a .0788615 en τ32, mientras |Δφ| aumenta de 14.1963 a 18.9284 rad. Se publican ambos valores y no se usa ese contraste para una puerta física.

La lentitud de grupo de un campo masivo y la dispersión de las mallas justifican examinar propagación de ondas cortas, además del defecto central. La referencia omite geometría radial, acoplamiento Φ/χ, fuentes, amplitudes de cada modo, borde e historia efectiva. El éxito de las pruebas espectrales de segundo orden tampoco basta para cumplir una tolerancia a resolución y tiempo fijados. Vincular esta referencia con el error real exige el presupuesto causal original y sus ventanas; no hay identificación causal nueva ni corrección física probada.

El cálculo hizo cero pasos M2, conservó catorce hashes científicos y dejó intactas las trayectorias. CP12 permanece abierto.
