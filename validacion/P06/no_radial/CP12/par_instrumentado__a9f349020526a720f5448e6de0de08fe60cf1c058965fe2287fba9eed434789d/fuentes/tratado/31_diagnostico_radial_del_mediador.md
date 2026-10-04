# 31 · Diagnóstico radial del mediador y límite causal de CP11

## 31.1. Problema que se continúa

El control temporal CP10 está superado y la comparación espacial del
mediador real falla la puerta original. Los resultados y cifras actuales
se consultan en [el resumen generado CP11](../informes/RESUMEN_NUMERICO_CP11.md)
y en los resultados enlazados por [el registro](../datos/registro_calculos.json).
Este capítulo deriva e interpreta los diagnósticos; no reemplaza los datos.
M2, Θ, los estados, la perturbación inicial y el umbral del 2 % se conservan.

## 31.2. Operador de la acción discreta

En una malla uniforme de centros, Wᵢ=∫celda r²dr, cᵢ=rᵢ₊½²/Δr y D
la diferencia entre celdas vecinas. Para cada ℓ,
\[
K_\ell=D^T\operatorname{diag}(c)D+
\Delta r\ell(\ell+1)I+\frac{2R^2}{\Delta r}e_Ne_N^T,
\qquad L_\ell=-W^{-1}K_\ell.
\]
El origen tiene flujo cero y la frontera exterior Dirichlet está a media
celda. K es simétrica y positiva definida en esta caja: el gradiente sólo
se anula para constantes, y la frontera elimina esa constante. El término
centrífugo es no negativo. La transformación y=W¹ᐟ²χ da la matriz real
simétrica Aℓ=W⁻¹ᐟ²KℓW⁻¹ᐟ². Esto garantiza modos libres reales y una norma
completa de proyección; NO garantiza precisión de fase del sistema acoplado.

Las frecuencias libres son ωⱼ=√(M²+λⱼ). La referencia continua en la misma
caja es λⱼ=(zℓⱼ/R)², con jℓ(zℓⱼ)=0. Comparar índices iguales sirve para
diagnosticar dispersión de la discretización radial. No identifica el
espectro del generador acoplado ni certifica el continuo de M2.

Las pruebas independientes de la acción original, simetría, residuo modal
y Parseval pasan. Las métricas spline inversa, simétrica por cuadratura y
con paridad en el origen conservan el fallo espacial. La componente corta
predomina en la diferencia, incluso con un recorte suave que evita un
borde espectral artificial en r=40. Sus fracciones son fracciones de una
norma de diferencia, no de la energía física.

## 31.3. Resultado negativo del mecanismo libre

La propagación libre exacta de los datos iniciales no reproduce la
diferencia observada. Como diagnóstico adicional se resuelve el equilibrio
elíptico con Φ congelado en cada extremo, manteniendo todos los modos
retenidos y el acoplamiento angular. Se separan χeq y su derivada de los
residuos rápidos. Un cambio de fase modal fijado por las frecuencias
radiales reduce la discrepancia, pero no supera el criterio explicativo
prerregistrado. Este resultado descarta esa corrección libre como
explicación mayoritaria suficiente. No descarta dispersión de componentes
generadas durante la respuesta acoplada, ni permite otra fase ajustada.

Ni χeq ni la corrección se usan para aceptar la evolución. χ sigue siendo
dinámico y real; no se introduce una nueva simetría ni una eliminación
adiabática en M2.

## 31.4. Respuesta forzada y evidencia no guardada

En la autobase libre, cada modo de la solución M2 satisface exactamente
\[
\ddot a_j+\omega_j^2a_j=F_j(t),\qquad
F=-\mathcal P_L[(g+h\chi)|\Phi|^2].
\]
Restar de los extremos la solución homogénea determina los dos momentos
de Duhamel de F, sin suponer su historia ni resolver una evolución nueva.
La diferencia entre las respuestas forzadas satisface la cota triangular
prerregistrada. Esta cota descarta el propagador libre inicial como causa
principal de la discrepancia.

La identidad exacta para d=Iχc−χf, con I fijo y A=M²−L, es
\[
\ddot d+A_fd=(A_fI-IA_c)\chi_c+(IF_c-F_f).
\]
El primer término registra el defecto del operador entre mallas; el
segundo, la diferencia de fuente no lineal. Sus valores en los extremos
no son un presupuesto de error integrado. Para separar sus contribuciones
a τ=160 hace falta su historia o evidencia equivalente con control de
error. Las normas, E y Q guardadas no contienen esa historia.

En el problema inverso de una fuente, η(t)=C t⁴(T−t)⁴ permite añadir
η¨+ω²η sin cambiar q, q̇, F ni Ḟ en los extremos. Esto delimita la
información recuperable; no cuestiona la unicidad de Cauchy de M2.

La evaluación doble de la identidad inicial falló por cancelación de
fuerzas casi iguales. Se conserva ese intento y la
[enmienda aritmética anterior al control nuevo](../informes/ENMIENDA_CP11_PRECISION_DEFECTO.md).
La referencia extendida valida la misma identidad con la misma tolerancia,
coeficientes, estados y spline. Un fallo de un control aritmético no es
una inestabilidad física.

## 31.5. Puerta de decisión y parada

Se cierra el diagnóstico finito de CP11. La aceptación no radial permanece
REFINAMIENTO_PENDIENTE; E03/E04/RES0/RES1 permanecen PARCIALES. No se prueba
estabilidad orbital, convergencia conjunta o continua, ni un dispositivo.
No se declara agotamiento de M2: la ambigüedad causal pendiente es real.

Se detiene antes de otra campaña. No procede resolver la ambigüedad con
otra malla, más tiempo o variantes elegidas después del fallo. Un siguiente
protocolo deberá definir un contraste que distinga el presupuesto de
defecto radial del presupuesto de fuente acoplada, explicitar qué historia
se conservará y cómo evitará repetir las evoluciones cerradas. Los estados
CP04 y CP10 siguen siendo los últimos orígenes válidos, no estados nuevos
creados por los diagnósticos de este capítulo.
