# CP12 · Lectura energética del negativo K4

Se analizaron exclusivamente los estados iniciales y fallidos ya guardados de la primera prueba K4. La cápsula negativa se autenticó por SHA-256 y se verificaron todos los archivos seleccionados. **Cero pasos M2 nuevos.** Las dos mallas se detuvieron en tiempos distintos; cada fila se interpreta con su propio tiempo.

Sea G=E_K4−E_FV, diferencia de formas espaciales con la misma energía cinética y el mismo potencial M2. La identidad

\[E_{FV}(t)-E_{FV}(0)=E_{K4}(t)-E_{K4}(0)-[G(t)-G(0)]\]

reproduce el cambio medido. G se separa por Re Φ, Im Φ y χ, y en regularización K2 y composición positiva fija. Los residuos relativos de la identidad son 2.6134028912864507e-16 y 5.232469188875666e-16. También pasan las comprobaciones independientes de gradiente y trabajo con el límite algebraico original 2e-12.

Todos los valores de la tabla están divididos por E_FV(0):

| h | Tiempo físico | ΔE_FV / E_FV(0) | −ΔG_Φ / E_FV(0) | −ΔG_χ / E_FV(0) | ΔE_K4 / E_FV(0) |
|---|---:|---:|---:|---:|---:|
| 0.125 | 0.022873976998663583 | 0.00006610612050728531 | 0.00006610551437449304 | 6.493884474403687e-10 | -4.32553936704968e-11 |
| 0.0625 | 0.017672153921661566 | 0.0002980734145922376 | 0.0002980733373172903 | 1.2055074207289556e-10 | -4.3276318611053135e-11 |

En los estados medidos, la variación de la diferencia entre las formas energéticas se concentra en el cambio espacial de Φ, principalmente en la composición positiva. Los resultados completos conservan ambos componentes Φ, χ, la regularización, los productos de trabajo y su distribución radial. La identidad explica la puerta energética fallida del ensayo; no demuestra cómo evolucionaría otra discretización.

La identidad semidiscreta de trabajo es

\[\dot E_{FV}=\sum_a c_a\langle v_a,(L^{nuevo}_a-L^{FV}_a)q_a\rangle_W,\qquad(c_a)=(2,2,1).\]

Conservar el operador FV original en ambos componentes Φ anula exactamente sus términos de esta identidad. Eso permite formular un ensayo independiente y más específico: Φ con su operador original y χ con la acción K4 positiva, con potencial M2 plenamente acoplado. La atribución original τ160 al operador χ y este negativo energético dan un fundamento para examinar ese diseño. La carga U(1) mantiene una forma común para ambos componentes Φ y el bloque espacial χ sigue siendo positivo. El trabajo restante de χ y las nuevas trayectorias deberán superar las mismas puertas mediante un nuevo prerregistro y controles del backend mixto antes de cualquier evolución.

No se ensayó aquí esa evolución mixta ni se validó una corrección. Se mantienen la puerta energética FV original 2e-4, la carga 1e-9, las dos mallas, M2, Θ, DOP853, tolerancias, observadores y aceptación espacial del 2 %. No se relaja una puerta ni se inicia K6/K8 por inercia. El K4 de tres campos permanece fallido y conservado; CP12 continúa abierto.

El suplemento completo fue guardado, recuperado y verificado: 8556 bytes, SHA-256 `29fb75ee329fce24f510cdede75abaac218051556996b6920c3d92b53bab2bd3`. Fuente y datos científicos: `checkpoints/CP12/continuacion_20261014/correccion_K4_20261015/analisis_energia`. La fuente original del ensayo fallido y su recibo permanecen intactos.
