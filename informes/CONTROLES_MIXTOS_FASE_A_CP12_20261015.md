# CP12 · Controles mixtos, fase A: resultado parcial positivo

Se ejecutó exclusivamente el subconjunto capturado antes del cálculo en `b3b65b072f5584b5786c3ab05ea187c8016d73e0`. No se ejecutó DOP853, ningún paso físico M2, el piloto K4 ni una nueva trayectoria. El backend mixto completo todavía no está aprobado.

Se recuperó la cápsula negativa K4 original (39 126 835 bytes, SHA256 `f4176ec466647faa5a48a427403db3a865f3eef8fda21ea0f837520adfc5bf0b`), con cobertura exacta y sus 84 hashes. Los datos CP10 iniciales/finales de ambas mallas y las fuentes proceden de esa cápsula; todos sus hashes permanecieron iguales después de los controles. Se reutilizan los resultados cerrados de K4 sin convertirlos en una validación del diseño mixto.

## Resultado

Pasaron ocho comprobaciones en cada uno de los cuatro estados (32 en total):

- Φ conserva exactamente el FV y χ coincide exactamente con el prototipo K4; la acción pasiva y la física mixta coinciden `array_equal`.
- Gradiente de la acción mixta por paso complejo independiente: error relativo máximo 3.723e-15.
- Identidad U(1): error relativo máximo 3.514e-17.
- Diferencia de formas energéticas: error relativo máximo 4.790e-16.
- Identidad de trabajo de la energía FV original: error relativo máximo 1.145e-13.
- Potencial fusionado C frente a NumPy con el nuevo enrutado: 20 comparaciones con diferencia exactamente cero, incluidos los estados y cuatro perturbaciones por estado.

Se observaron BLAS SkylakeX de un hilo sin forzar su dispatch. Todos los límites algebraicos siguen en 2e-12; se conservaron las escalas y la semilla registradas. Datos completos en `checkpoints/CP12/continuacion_20261014/mixto_chi_prefLight_20261015/fase_A/RESULTADO.json`. El certificado incluye hashes de las fuentes y del resultado para una recuperación independiente desde este commit y la cápsula autenticada.

## Puerta siguiente

El resultado sólo completa la fase A. Siguen pendientes la identidad completa de defecto/Jacobiano extendida, la construcción dispersa y simetría ponderada independientes y la propagación congelada Gauss 7/6 contra referencia controlada. En particular, la clase `MixedGauss` publicada aún no fue certificada por estos controles. Deben registrarse/capturarse las implementaciones siguientes antes de ejecutarlas.

No se autoriza aún una evolución mixta. Incluso un aprobado completo previo sólo permitirá preparar otro prerregistro físico y conservar/recuperar/auditar τ0 antes de M2. La energía FV y la consistente mantendrán sus puertas 2e-4, la carga 1e-9 y la aceptación espacial 2 %. La pequeñez del trabajo sobre los estados medidos no acota una futura trayectoria.

El K4 de tres campos sigue fallido, la evolución original τ160 y todos sus certificados permanecen intactos, y CP12 continúa abierto sin corrección validada. Las 33 etapas y todos los negativos se conservan; main sigue CP11 y PR #2 abierto/borrador, sin merge, tag ni Release.
