# CP12/P3 · D1 y D2 para el negativo de τ160

Registro de una lectura posterior al fallo de P3 en el ensayo independiente de
`e9e5677` y anterior a la ejecución de estos dos diagnósticos. La referencia del
ensayo suspendido es `b66aea958759ec777cc5b98810f57ba3a2dd41ca`. El último
checkpoint aprobado es τ152. Este trabajo conserva el resultado oficial de
τ160 y termina con evidencia y una decisión de diseño.

## Entradas y comprobaciones

- `REGISTRO.json` fija repositorio, trayectoria, adjuntos, bytes, huellas de
  estados, código, métricas, configuración y recibos. Reusar los prefijos
  publicados τ32–τ152 y la atribución causal de tres ventanas de `SUSPENSION.json`.
- Recuperar en privado el adjunto cifrado 750993142 y cotejar SHA-256 y tamaño
  de CMS, ZIP, cobertura del manifiesto, sus 747 cargas, estado, configuración
  y procedencia. Ejecutar el auditor de frontera capturado en modo de cero
  pasos, con entorno original acreditado. Guardar el resultado independiente.
- Recuperar sólo las otras cápsulas de τ112, τ120 y τ128 de esta misma
  trayectoria. Aportan los vectores no publicados antes, durante y después del
  desplazamiento radial. Verificar el ZIP, todas las cargas, la identidad y los
  datos de Cauchy. Reusar el recibo original de cada una si las huellas coinciden.
  τ0 se lee del estado de τ160. El manifiesto marca el transporte interno viejo
  como forense. Los datos utilizados corresponden a la frontera, con sus tiempos
  reales.
- Usar los estados y observadores de P3 con el operador realmente capturado
  A₂ + h²A₂²/12 + h⁴A₂³/90, Φ en volumen finito, R220, L4, h=.125/.0625.
  Verificar huellas antes/después. Bloquear creación y pasos DOP853 y avance
  de los observadores. Se lee la historia almacenada sin regenerar trayectorias.

## D1 · historia, observadores, localización y comparación

1. Leer las 401 observaciones de τ0 a τ160 en intervalos de 0,4. Conservar error,
   normas, proyecciones firmadas, cosenos, retirada cuadrática y fracciones
   espectrales de las ventanas núcleo y suave en la base FV histórica. Registrar
   la primera *observación guardada* que excede .02 y la anterior. Los tiempos
   de certificación oficiales son los múltiplos de ocho.
2. En τ112/120/128/160 separar dχ y dχ̇/μ en la misma norma inicial y cuadratura.
   Dar las potencias de ambos, ℓ1…4 con foco en ℓ2/4, las bandas
   [0,2), [2,5), [5,10), [10,20), [20,40), [40,220), y un control del borde
   [200,220). Publicar fracciones con denominador explícito y centroide.
   Comparar porcentajes de la ventana r<40 con la publicación oficial.
3. Reconstruir las respuestas libres y acopladas del primer orden registrado
   (GL7), desplegando la base angular D2 capturada, y medir Gram y proyecciones
   en r<40 y en la caja completa no radial. Comparar el mismo forzamiento χ
   con y sin Jacobiano: ||c−r||, 2⟨r,c−r⟩, proyección sobre el defecto y
   respuesta inducida en Φ. Conservar signos de los otros canales y sus
   cruces. Un cambio condicionado al Jacobiano tiene alcance distinto
   de un retorno χ→Φ→χ aislado.
4. Medir conmutador instantáneo P3, transferencia no lineal e incremento
   algebraico del conmutador al añadir a₄=1/560 en las mismas muestras.
   Informar signos, cancelaciones y razón de normas por ℓ2/4 y banda.
   Un conmutador instantáneo es una fuerza, mientras que el presupuesto
   conserva respuestas acumuladas a lo largo de ambas historias.
5. En los mismos cuatro puntos contrastar cúbica oficial gruesa→fina, extensión
   por paridad central, cúbica inversa fina→gruesa y PCHIP gruesa→fina. Evaluar
   también caja completa con la escala inicial de caja y advertir el extremo
   extrapolado de media celda. La puerta oficial usa la cúbica original y .02
   en r<40, sin rotar χ. Ejecutar `compare` original sin modificar su guardia
   de τ160. Comparar las cinco medidas y reutilizar los controles físicos y
   causales registrados del fallo.
6. Releer regularidad de la semilla CP04 original a través de sus splines pares,
   sin modificar los datos. Repetir el contraste instantáneo de fuga de fuente
   por ℓ>4 con cuadratura L12 en las dos mallas, en τ0/160 y r<40. Su alcance es
   el de fuerza con historias L4 fijas.

## D2 · pruebas radiales estáticas

1. En cada malla diagonalizar A₂ simétrico ponderado para ℓ2/4, verificar
   positividad, residuos de autovectores y Parseval ≤2e-11 de campo y velocidad
   por separado. Proyectar χ en τ0/112/120/128/160 en su malla nativa. Proyectar
   también el defecto interpolado y la respuesta de operador χ acoplado en
   la malla fina. Dar caja, corte r<40 y ventana suave 32–40. Conservar potencia
   nula inicial de ℓ4 como tal, sin cocientes indefinidos.
2. Emparejar autovalores por índice radial con ceros de jℓ/R, limitando el
   contraste de frecuencias al intervalo común k·h_gruesa≤π, con la fracción
   de potencia emparejada explícita. Comparar P1…P4 con los coeficientes fijos
   2/[j² binom(2j,j)]. Separar exactamente la diferencia de frecuencias entre
   mallas en la diferencia de los símbolos planos al mismo k y la diferencia
   de los restos radiales (geometría, origen y cierre). Guardar ambos RMS
   ponderados y el cruce firmado, además de los errores por malla frente a
   la referencia esférica. El resto espectral radial tiene alcance más
   amplio que el término formal h². Los proxies de fase libre ignoran
   evolución no lineal y diferencias entre autofunciones.
3. Perfiles pares fabricados q=r^ℓu, R40, ℓ0/2/4, h=.25,.125,.0625,.03125,.015625.
   Repetir u=exp(−r²/64)(1−r²/1600)^6 y
   u=exp(−((r²−225)/60)^2)(1−r²/1600)^6. Añadir el perfil centrado en r28
   u=exp(−((r²−784)/120)^2)(1−r²/1600)^6, liso y con portadoras cos(kr)
   para k=2,4,8,12 en ℓ2/4. Contrastar P3, P3 al restar el residuo analítico
   h²r^ℓ[u''/r²−u'/r³]/[6(2ℓ+1)] y la composición P4 algebraica, contra
   Lℓ exacto. Normar en r<32. Informar primera celda y resto 32–40 aparte.
   En P3 y P4 queda el término geométrico h² a r fijo.

## Decisión registrada antes de la lectura

Un presupuesto condicionado apoya el canal total cuando la proyección tiene el
signo del defecto, la retirada reduce su norma y el cierre registrado pasa.
La preferencia entre submecanismos exige concordar tres observaciones:
ocupación del defecto y de la respuesta, magnitudes y cruces de los términos
espectrales en las dos mallas, y contraste fabricado al cambiar frecuencia y
refinar h. La evolución radial del defecto por sí sola es localización.

Si domina la contribución plana en los modos que portan el defecto tardío y
P4 la reduce, la hipótesis mínima a probar es el término fijo h⁶A₂⁴/560.
Un incremento contrario del conmutador o una sensibilidad importante de la
métrica se guardan como evidencia adversa. Preceder toda propuesta física
con un contraste de respuestas en historia congelada, indicando lo que
cuenta como refutación. Si las firmas son mixtas, separar las fuentes
experimentalmente antes de seleccionar un cambio de acción. El h² formal
queda registrado en los dos casos. La ejecución de este diagnóstico
comprende cero pasos nuevos de M2.
