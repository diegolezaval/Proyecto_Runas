# CP12: primera prueba independiente de la acción K4

Registro previo a cualquier paso físico del candidato. CP12 original alcanzó τ160, reprodujo CP10 exactamente y superó sus 44 comprobaciones. Las tres ventanas originales identifican suficientemente `operador_chi` acoplado y `operador_total`. El presupuesto completo conserva el negativo del operador libre, los cruces y las cancelaciones. La discrepancia original de fases de χ es 0.0512639096419456, superior a 0.02. CP12 permanece abierto.

## Fundamento y alcance

Se recuperó el diseño condicional anterior del ZIP ancestral τ80 autenticado por SHA-256 `709cbb21e338b78597e6b4708a3d89dd0a60997c5d7f7cc085e2e65da5a7584c`. Se conservan sus controles estáticos y lineales ya cerrados: regularidad, acción positiva, gradiente variacional, carga U(1), equivalencia del potencial M2 C/NumPy y backend de cinco bandas con controles Gauss–Legendre 7/6 libres y congelados. Se reutilizan los resultados y hashes; no se repiten esas pruebas ni las trayectorias originales.

Para qℓ=r^ℓuℓ, se conserva la masa W original y la rigidez regular positiva K2 del prototipo guardado. Se prueba exactamente K4=K2+(h²/12)K2 W⁻¹K2 en los tres campos. El coeficiente 1/12 procede de la serie fija de `4 arcsin²(sqrt(s)/2)`; no se elige con amplitudes, fases o errores de χ. El Hamiltoniano consistente usa factores 1,1,1/2 para Re Φ, Im Φ y χ, el potencial M2 intacto y la misma forma espacial para ambos componentes Φ. La simetría de la forma y la positividad conservan las identidades semidiscretas de energía y carga. Se mide su conservación temporal.

K4 nombra la truncación de la composición. Los resultados previos de orden espectral radial global dos y empeoramiento de algunos modos se mantienen como negativos. K2 se conserva como control estático; esta primera prueba no separa físicamente por sí sola la regularidad del origen y la composición de dispersión. Se ensaya una única modificación derivada conjuntamente. Ningún orden radial global cuatro está supuesto.

## Configuración invariable y nueva procedencia

La prueba empieza en τ0 con los seis campos de Cauchy originales, sin relajación ni retoque. Las matrices iniciales de ambas mallas deberán coincidir `array_equal` con CP10. Se mantienen M2, Θ, h=.125/.0625, R220, L4, ε=.02, DOP853, rtol=1e-10, atol=1e-12, max_step=.02, observaciones cada .4 y fronteras cada 8 hasta τ160. Se observa BLAS SkylakeX de un hilo, sin forzar su dispatch.

El ensayo usa raíces, salidas, recibos, bloqueos, temporales y cachés propios; copias sin enlaces y fuentes originales inmutables. Su identidad declara una evolución M2 nueva con otra discretización espacial. La evidencia causal τ160 es el antecedente científico; sus campos finales no son los datos de Cauchy del candidato. No se presupone la terminación de otros ejecutores. Main queda en CP11 y PR #2 abierto y en borrador.

## Observadores y balances

Se conserva el código de las ecuaciones de observación, los cinco canales libres y acoplados, los grupos, el Jacobiano medio, los órdenes 7/6, el paso .01, la iteración 1e-12/12, spline fijo, norma de fases, núcleo40, recorte32→40, bases y cortes originales. Sólo el laplaciano y su resolvente usan la acción K4 real, mediante el backend ya comprobado. Los cortes modales usan la base original para mantener la definición de las ventanas.

En cada paso DOP853 aceptado se calculan por separado la energía FV original y el Hamiltoniano K4 consistente, con sus propios valores iniciales. Ambas derivas deben ser ≤2e-4. La deriva de carga original debe ser ≤1e-9. Un fallo de la medida energética original detiene el ensayo aunque la energía K4 se conserve. Se guardan ambas series y sus máximos.

Se mantienen los límites originales: identidad y simetría 2e-12; Parseval 2e-11; cierres y controles temporales de observadores 1e-3. Cada frontera comprueba además la identidad instantánea completa del defecto con la escala absoluta original de fuerza y el cierre de χ en toda la caja. La auditoría de recarga ejecuta cero pasos M2, reproduce la base angular y verifica que el estado no cambió. Estas son comprobaciones del ensayo nuevo; no se presentan como igualdad final de la trayectoria corregida con CP10.

## Orden, paradas y decisión

1. Publicar este registro y las fuentes ejecutables. Construir, guardar, recuperar y auditar la frontera inicial τ0 antes de M2.
2. Ejecutar el piloto K4 0→8. Cualquier fallo científico se conserva como negativo íntegro y detiene la prueba. No se relajan criterios ni se reintenta a ciegas.
3. Si los controles del piloto pasan, continuar automáticamente el mismo ensayo en fronteras de ocho unidades hasta τ160. Cada frontera debe guardarse, recuperarse con verificación de todos los hashes y auditarse antes de iniciar la siguiente.
4. En τ160 aplicar la función original `diagnosticar_mediador_CP10.compare` sin editarla: norma temporal suprema y errores finales de campo/fases de Φ y χ, con la misma escala inicial y puerta ≤0.02. La fase global U(1) de Φ sigue su tratamiento original; no se ajusta χ para aceptación. Se exigen también cambio de carga del núcleo ≤.005 y amplificación ≤3, junto con ambos balances y todos los observadores. Se publican todos los resultados.
5. Un aprobado entre las dos mallas originales seguirá siendo provisional. La referencia adicional h=.03125 y las pruebas independientes de robustez contempladas en el diseño condicional requerirán su registro ejecutable posterior; se conserva la obligación antes de validar la corrección o cerrar CP12. Un fallo final se documenta como tal. Este registro no lanza K6/K8 ni otra variante automáticamente.

Una disminución de respuestas retiradas offline no cuenta como prueba de una evolución corregida. La evidencia de eficacia debe proceder de las trayectorias autoconsistentes guardadas, de sus puertas originales y de las comprobaciones posteriores. El presupuesto de respuesta completo se conserva para examinar el mecanismo residual. El resultado de esta primera prueba no concede por sí solo el cierre de CP12.
