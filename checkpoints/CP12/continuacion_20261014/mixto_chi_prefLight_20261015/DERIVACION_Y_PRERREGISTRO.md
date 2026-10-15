# CP12 · Derivación y prerregistro de controles Φ-FV / χ-K4

## Autoridad y alcance

Registro prospectivo posterior al diagnóstico energético publicado en `58079431302c1b2ac30bea8f3b3afce3fafba095`. Se reutilizan el presupuesto original τ160, sus tres ventanas y 44 pruebas, el negativo K4 y los controles cerrados. No se repite su cálculo ni se reinterpreta un fallo como aprobación. Este documento no autoriza pasos M2: registra exclusivamente derivación e implementación de controles nuevos. No hay un resultado numérico mixto certificado.

## Acción mixta y motivo independiente

Escribamos x=Re Φ, y=Im Φ, z=χ. W conserva exactamente los pesos radiales originales y K_FV la rigidez original, incluidos origen y frontera. Para cada armónico, Kχ=K2+(h²/12)K2 W⁻¹ K2 usa literalmente la acción regular positiva K2 ya conservada, no otra implementación elegida por sus resultados. El coeficiente fijo 1/12 no se ajusta. El diseño cambia sólo la discretización espacial de χ; las dos componentes de Φ conservan exactamente K_FV. Se mantiene el potencial M2 plenamente acoplado, incluida su parte de masas, sin aproximación adiabática ni fuente congelada en una eventual trayectoria.

La energía consistente es

\[
E_{mix}=v_x^TWv_x+v_y^TWv_y+\tfrac12v_z^TWv_z
+x^TK_{FV}x+y^TK_{FV}y+\tfrac12z^TK_\chi z+U(x,y,z),
\]

sumando los armónicos con las convenciones originales. El potencial U es el original; no se añaden nuevamente sus masas al construir las ecuaciones. La fuerza espacial de cada campo es −W⁻¹K_a q_a; la fuerza de U lleva el factor cinético correspondiente (2,2,1). Ésta debe ser una derivación variacional de la acción mixta, no una sustitución aislada de la fuerza sin su energía y observadores.

La positividad de Kχ se deduce de uᵀKχu=uᵀK2u+(h²/12)(K2u)ᵀW⁻¹(K2u)≥0. La simetría de cada bloque es exacta. La misma forma FV para x e y preserva la cancelación espacial de la carga U(1); cambiar sólo χ no rompe esa simetría. Ambas discretizaciones representan el mismo operador radial continuo, pero aquí no se supone orden global cuatro ni convergencia de sus trayectorias. Los negativos espectrales anteriores siguen vigentes.

Sean ΔKχ=Kχ−K_FV y Gχ=½zᵀΔKχz. Entonces, para cualquier estado y velocidad,

\[
E_{FV}=E_{mix}-G_\chi,\qquad
\dot E_{FV}=-v_z^T\Delta K_\chi z
=\langle v_z,(L_\chi-L_{FV})z\rangle_W.
\]

Los términos de trabajo de Φ se anulan algebraicamente porque sus operadores no cambian. Es una eliminación estructural de la contribución que dominó la diferencia energética medida en el negativo, no una predicción de la evolución mixta. El término restante de χ puede crecer por realimentación; su pequeñez sobre los estados K4 fallidos no acota su futuro en la trayectoria mixta. Conservar E_mix no concede aprobación a E_FV: ambas puertas siguen siendo obligatorias.

## Puerta previa: sólo controles nuevos, cero M2

Se autenticarán antes de usarlos las cápsulas, el manifiesto completo, el estado/configuración/recibo, las catorce fuentes científicas y los prototipos K4 ya conservados. La preparación usará destinos independientes sin enlaces y fuentes heredadas inmutables. Se registrará el código nuevo con su SHA antes de ejecutar cada control. No se editarán fuentes bajo otro trabajador activo. Los registros numéricos previos se reutilizan; un archivo no publicado no cuenta como control terminado.

Semilla fija: 20261015001. Datos: condiciones iniciales y finales CP10 guardadas en ambas mallas h=.125/.0625, además de cuatro perturbaciones 1e-5 por estado para comprobar las operaciones nuevas. No se evoluciona CP10. Los estados K4 fallidos se interpretan con sus propios tiempos, nunca como una frontera común.

1. Enrutado: igualdad `array_equal` de cada acción espacial Φ con el FV original y de χ con el prototipo K4 registrado. Comprobar RHS, energía y resolventes pasivos: cambiar sólo el RHS no basta. Preservar las masas y no contarlas dos veces.
2. Gradiente de la energía mixta por derivada direccional independiente de paso complejo 1e-30, usando la expresión polinómica en componentes reales sin operaciones no holomorfas sobre la perturbación. Residuo relativo ≤2e-12. Identidades de carga y de trabajo anteriores, con escala absoluta original, ≤2e-12. Conservar residuos absolutos y normalizados.
3. Potencial fusionado C/NumPy, identidad polinómica del Jacobiano medio, peso (2,2,1), fuga angular y simetría: límites originales ≤2e-12, referencias extendidas cuando correspondan, sin cambiar sus escalas declaradas.
4. Identidad instantánea de defecto completa con el spline original y cada operador mixto real: conmutador en Φ-FV, conmutador en χ-K4, transferencia no lineal y Jacobiano medio. Residuo de fuerza con escala absoluta original ≤2e-12. No utilizar un conmutador FV en χ ni un resolvente K4 en Φ por herencia accidental.
5. Backend: construir independientemente la matriz canónica dispersa congelada, con bloques Φ-FV, χ-K4, masas originales y Jacobiano medio. Verificar acción, signos, pesos y simetría ≤2e-12 contra el backend nuevo, sin volver a declarar los controles homogéneos K4 como controles de este enrutado.
6. Respuestas pasivas del backend mixto: Gauss–Legendre 7/6, paso .01, cinco canales y etapa iterativa 1e-12/máximo 12 originales. Contrastar el operador congelado con una exponencial dispersa independiente: error en espacio de fases ≤1e-3 y balance cuadrático ≤2e-4. La energía del control linealizado es su forma cuadrática correspondiente; no se exige como si fuese una nueva trayectoria física M2 ni se usa para aceptar la puerta física FV. Duración congelada fija τ=0.1 (diez ventanas .01), sin barrido posterior. Registrar la cota de frecuencia de cada matriz; la referencia independiente debe certificar error de fases ≤1e-8 mediante estimación de resto o contraste controlado antes de juzgar el backend. Si no puede certificarlo, el control queda inconcluso, no aprobado.

Un fallo detiene esta versión y se conserva con fuentes, entradas, salida y recibo. No se modifica una escala, semilla, paso, frecuencia o umbral después del resultado para rescatarla. Una discrepancia meramente administrativa requiere diagnóstico explícito y conservación del intento antes de una enmienda. No se inicia K6/K8 ni otra variante por inercia.

## Puerta posterior: un aprobado previo no valida la corrección

Sólo si todos los controles nuevos pasan procederá otro prerregistro ejecutable de un piloto físico mixto 0→8, con datos de Cauchy originales `array_equal`, M2, Θ, R220, L4, ε=.02, DOP853 y tolerancias originales, observadores, spline, dos mallas y puerta espacial 2 % intactos. Ese registro deberá capturar los resultados del control congelado y todos los hashes del backend, resolver cualquier alcance pendiente y conservar/recuperar/auditar τ0 antes de M2. Este documento por sí solo no autoriza el piloto.

En una eventual evolución, cada paso aceptado mantiene las puertas de ambas energías ≤2e-4 y carga ≤1e-9. Cada frontera de ocho unidades conserva el estado completo, fuentes, configuración, recibos y presupuesto, y exige recuperación y auditoría antes de avanzar. La comparación corregida no debe ser idéntica a CP10; sí debe mantener sus datos iniciales y usar la función comparadora y observadores originales. Se exigirán eliminación del mecanismo, convergencia, conservación, estabilidad y robustez, incluida la resolución adicional ya prevista, antes de validar una corrección. Retirar respuestas offline no cuenta como eficacia autoconsistente.

Main sigue en CP11 y PR #2 abierto/borrador. Las 33 etapas y todos los negativos permanecen intactos. No hay merge, tag, Release ni cierre CP12.
