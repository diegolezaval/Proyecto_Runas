# Prerregistro CP11 · Respuesta forzada recuperable desde los extremos

Este análisis se registra después del resultado negativo del contraste
congelado, antes de ejecutarlo. No cambia sus criterios ni intenta otra
corrección de fase. Contrato: `datos/ensayo_respuesta_forzada_CP11.json`.

## Justificación independiente

La ecuación exacta de cada coeficiente en la autobase radial libre es
\[
\ddot a_j+\omega_j^2a_j=F_j(t),\qquad
F=-\mathcal P_L[(g+h\chi)|\Phi|^2].
\]
Los estados inicial y final permiten recuperar EXACTAMENTE las dos
respuestas integradas por modo:
\[
b_j=a_j(T)-a_j(0)\cos\omega_jT
-\dot a_j(0)\sin\omega_jT/\omega_j,
\]
\[
\dot b_j=\dot a_j(T)+\omega_ja_j(0)\sin\omega_jT
-\dot a_j(0)\cos\omega_jT.
\]
Son los momentos de Duhamel de la fuente real, no una simulación nueva ni
una fuente supuesta. Se recuperan sus potencias modales y la diferencia
entre mallas, normalizada como CP10. Por desigualdad triangular,
\[
\|\Delta b\|_{ps}\ge\max(0,\|\Delta\chi\|_{ps}
-\|\Delta\chi_{libre}\|_{ps}).
\]
La norma de espacio de fases es la misma que en CP10, con velocidad/M.

## Separación de las causas todavía no identificadas

Con I la interpolación spline fija, A=M²−L y d=Iχc−χf,
\[
\ddot d+A_fd=(A_fI-IA_c)\chi_c+(IF_c-F_f).
\]
Se calculan ambos términos en los dos extremos y se verifica esta identidad
contra la fuerza original completa. No se usa el tamaño de un término en
un extremo como estimación de su contribución integrada a τ=160.

## Puerta y límite de información

Se requieren residuo algebraico relativo <2e−12 y cierre de la
descomposición con residuo <2e−11. Un fallo detiene la inferencia; no
relaja esas tolerancias. Si la cota inferior de la respuesta forzada es
>50 % de la diferencia observada, se descarta que la discrepancia sea
principalmente propagación libre de los datos iniciales. No se atribuye
automáticamente la diferencia a error de fuente o a error de dispersión:
los dos momentos no separan sus historias temporales.

La limitación es demostrable en el problema inverso de la fuente: añadir
η¨+ω²η a F, con η=t⁴(T−t)⁴ times una amplitud, deja q, q̇ y F, Ḟ iguales
en ambos extremos, pero cambia la fuente interior. Esto NO afirma varias
soluciones de M2 para los mismos datos de Cauchy: M2 sigue siendo
determinista. Muestra que los extremos guardados no reconstruyen la
historia de una fuente sin resolver de nuevo la dinámica completa.

Se preserva el 2 %. Ningún propagador o momento reconstruido es una
corrección para aprobar. Se cierra esta unidad si continúa faltando la
historia necesaria, sin abrir otra campaña, cambiar M2 o declarar
agotamiento de la línea física. Los tres análisis son finitos, baratos y
reproducibles desde CP10; la continuación sólo podrá diseñarse cuando se
resuelva esa ambigüedad con evidencia discriminante.
