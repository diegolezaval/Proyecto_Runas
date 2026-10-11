# CP12 · Presupuesto causal de la diferencia espacial de χ

Base autoritativa: `main`/tag CP11, commit `ed8d818b622a0687aeb56d34ca9e3913bd54e124`. Rama `ciencia/cp12-causal-chi`. Este prerregistro responde a la autorización explícita de reproducir **sólo** las dos evoluciones CP10 relevantes con instrumentación pasiva. No modifica su física, Θ, datos CP04, deformación, dominio, L, solver, tolerancias o puerta 2 %. No es una nueva campaña de refinamiento.

## Pregunta y puerta previa

CP11 valida el operador FV y localiza la discrepancia en componentes cortas de la respuesta forzada; no dispone de la historia para separar operador y fuente. Se reproducen h=.125 y .0625, R=220, L=4, ε=.02, τ=0…160, DOP853 completo con fuerza C auditada, rtol=1e−10, atol=1e−12, max_step=.02. Se conservan los reinicios deterministas cada ocho unidades y las observaciones originales cada .4. Los estados iniciales, campos/velocidades finales, observaciones, número de pasos aceptados y evaluaciones originales deben ser **idénticos** a CP10. El tiempo de pared y evaluaciones adicionales de observación se registran por separado. Cualquier discrepancia detiene la atribución y exige diagnóstico, sin cambiar el criterio de reproducción.

Las dos trayectorias pueden intercalarse en un trabajador sincronizado. Cada integrador conserva sus propios pasos adaptativos y fronteras de ocho unidades. No se obliga a compartir pasos. Los interpolantes pasivos se obtienen de una copia del estado interno de DOP853: las etapas extra de dense output y sus contadores no se escriben en el integrador físico. Una prueba aislada debe comprobar la identidad de y, f, K, h y nfev con/sin lectura pasiva antes de evolucionar M2.

## Identidad y presupuesto de Duhamel

I es el spline cúbico fijo de centros gruesos a finos de CP10/CP11, sin ajuste de fase ni cambio de normalización. A_f=M²−L_f. En toda la caja, no sólo en el núcleo,

\[
d=I\chi_c-\chi_f,\quad
\ddot d+A_fd=C_\chi+\Delta F,\quad
C_\chi=(A_fI-IA_c)\chi_c.
\]

Cada término se integra como respuesta lineal retarda de A_f, con las condiciones iniciales correspondientes. El término inicial libre y las respuestas de Cχ y ΔF deben sumar la diferencia observada. Se retienen el campo y la velocidad, las cancelaciones y productos cruzados, no sólo normas de fuerzas instantáneas. Las respuestas sin una fuente o sin el conmutador son los contrastes de fuente común y operador común condicionados a estas historias; no son soluciones autoconsistentes alternativas de M2.

Se descompone ΔF **durante toda la evolución**, aunque luego no domine, para no perder el contraste:

\[
\tilde q=Iq_c,\quad \tilde\rho=|\tilde\Phi|^2,
\quad T=IF_c-F_f(\tilde q),
\]
\[
R=-\mathcal P_L\{[g+h(\tilde\chi+\chi_f)/2](\tilde\rho-\rho_f)\},
\quad B=-\mathcal P_L\{h(\tilde\rho+\rho_f)d/2\},
\quad \Delta F=T+R+B.
\]

T identifica la transferencia/proyección no lineal; R el cambio de densidad; B la reacción de χ en la fuente. Es una descomposición simétrica declarada antes del resultado. B puede ser una respuesta al error que empezó en otro término. No se llama causa dominante a B por tener una norma grande.

## Contraste de realimentación y origen del error

Para separar la causa de la reacción se acumula además una identidad exacta de todos los campos. Sea N la fuerza no lineal, después de retirar los términos lineales de masa y Laplaciano, y δq=Iq_c−q_f. La identidad polinómica

\[
N(\tilde q)-N(q_f)=\overline J(t)\,\delta q,\qquad
\overline J=\int_0^1DN(q_f+s\delta q)\,ds
\]

es exacta: N es cúbica y el Jacobiano cuadrático, de modo que dos nodos Gauss integran el segmento exactamente. Se usa la misma cuadratura angular y el mismo spline. El peso cinético diag(2,2,1) hace simétrico el Jacobiano de la acción; esta propiedad se comprueba.

La ecuación completa de diferencias es una ecuación lineal no autónoma a lo largo de las **dos** historias efectivamente medidas:

\[
\delta\ddot q=(L_f-\operatorname{diag}(m^2,m^2,M^2))\delta q
 +\overline J\delta q + C_q+T_q.
\]

Se resuelven pasivamente cinco respuestas: inicial, defecto del operador en Φ, defecto en χ, transferencia no lineal en Φ y transferencia en χ. Su suma debe reproducir δq. La respuesta de Φ a un forzamiento exclusivo en χ prueba el canal χ→Φ; su retorno a χ constituye realimentación en este sistema de diferencias. La atribución está condicionada al spline y a la trayectoria; no es una afirmación sobre todos los estados de M2. No se cambia la solución física ni se usa ninguna respuesta corregida para aceptar.

## Resolución temporal y suficiencia de la evidencia

La unión de los intervalos aceptados de ambos DOP853 suministra interpolantes de orden siete de todos los campos. Dentro de cada intervalo común se integran los observadores con colocación Gauss de cinco y cuatro etapas (órdenes diez y ocho), ambos sobre las mismas historias. Se incluye en la unión cada observación .4. La matriz radial lineal se resuelve por factores tridiagonales; el Jacobiano variable se trata mediante iteración de etapas con residuo controlado. No se altera ningún paso físico para mejorar el observador.

No se muestrean oscilaciones rápidas sólo cada .4: esa cadencia guarda vistas de un presupuesto acumulado dentro de **cada** paso. El control de órdenes, el cierre frente a los campos reales y los controles fabricados a frecuencia ≥ la máxima frecuencia radial justifican la resolución. La autobase FV de R=220 analiza k>4, y cortes 2,8,12,20, con el núcleo r<40 y recorte suave CP11. Se guardan respuestas finales completas, estado acumulado reanudable y serie de normas/productos cruzados/comienzos; el historial de cada etapa física no se requiere como un gran binario: los momentos/respuestas se acumulan. Los temporales del integrador no se declaran como evidencia persistente.

Puertas anteriores al cálculo:

- Identidad algebraica y Jacobiano/spline: tolerancia relativa 2e−12, referencia longdouble para las cancelaciones CP11; Parseval 2e−11.
- Controles físicos CP10 sin cambio: E<2e−4, Q<1e−9, y los restantes límites originales.
- Cierre de observadores y diferencia entre órdenes ≤1e−3 de la diferencia observada, con suelo de normalización 1e−5 de la norma inicial para instantes donde la diferencia se anula. Las respuestas individuales también deben diferir ≤1e−3 de su propia norma con el mismo suelo. Un fallo bloquea la inferencia, no elude el 2 %.
- Comienzo: primer cruce sostenido durante tres observaciones del 1 % de la norma **final observada**; se publica también el umbral para evitar confundir redondeo con aparición física.
- Mecanismo mayoritario suficiente: proyección firmada ≥.8 sobre d, coseno ≥.8, y retirar su respuesta reduce ≥50 % la diferencia cuadrática, tanto en espacio de fases del núcleo como en las componentes cortas. Se publican todas las contribuciones y cancelaciones. Si varias clases son necesarias o estos criterios no discriminan, se describe el mecanismo conjunto o se conserva la ambigüedad; no se escoge una clase por su norma aislada.

## Decisión y conservación

Un fallo de reproducción detiene primero el diagnóstico causal. Un fallo de identidad/cuadratura detiene su interpretación. Un presupuesto cerrado discrimina las hipótesis sólo dentro de su alcance: un negativo no excluye M2. No se prueba ninguna corrección física/discreta antes de identificar suficientemente el mecanismo. Una corrección posterior necesita derivación y prerregistro independientes, preservación variacional, pesos, positividad/flujo/frontera y conservación, prueba de eliminación del mecanismo y **después** comparación con la puerta original. No se sustituye esto por más malla o tiempo.

Se conserva íntegramente CP11 y su negativo. La instantánea `trazabilidad/CP11_entrada/` y el inventario de 1047 archivos permiten recuperar las autoridades que se actualicen. La procedencia CP10 registra este protocolo, Θ, fuente CP04, código, compilador, entorno y hashes antes del trabajador. Reinicio de ocho unidades sólo con identidad, estado, presupuesto y configuración válidos. No se reabre E00/E01/C0 ni otra evolución. Integración sólo por PR; no se escribe directamente en main.
