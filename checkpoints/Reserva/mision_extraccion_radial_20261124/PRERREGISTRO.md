# Paso 3 · extracción por la donante aislada

**Pregunta y origen.** ¿Cuánta energía y carga adicionales atraviesan los radios 40 y 60 al disparar sobre la donante previamente cargada, una vez descontados la evolución espontánea, la respuesta de la gemela y el trabajo del actuador? Base científica `bce7113d1cb9befef6699578d61f95613ed0dcdf`. La retención radial hasta τ300 y el dictamen de 0/4 para la primera entrega a la receptora se conservan. Esta es una misión independiente. [Retención de referencia](../paso3_20261118/RETENCION.json) · [Ensayo previo con señal apagada](../mision_senal_apagada_20261124/README.md)

## Cuatro preparaciones y controles

Se harán los cuatro casos físicos cargada encendida, cargada apagada, gemela encendida y gemela apagada. Cada pareja parte de los mismos campos y velocidades. Se conserva la acción M2 radial de volúmenes finitos con media energía de cara, regularidad central, pared exterior de Dirichlet y Verlet de velocidades del paso 2. Se reutilizan su fuerza y sus flujos con signo saliente positivo. Para el caso encendido se suma la fuente de χ de radio 6, duración 8, portadora 2,3 y amplitud ya calibrada A = 0,0035912196276076985. Se computa su trabajo efectivo con el promedio de las fuentes de ambos extremos de cada paso por el desplazamiento de χ. La fuente neutra aporta cero carga. El reloj local s = τ − 300 empieza al disparar. [Señal original](../paso3_20261118/calibrar.py) · [Flujos e integrador originales](../paso2_20261117/radial.c)

La caja histórica parte directamente de ambos estados finos de τ300, verificados contra el manifiesto de retención. Las cajas grandes se reconstruyen desde la preparación sin pulso de τ0, antes del primer contacto del paquete con la pared a τ112. Se prolonga con ceros sólo el fondo preparado, comprobando su cola en la última unidad radial. Se añade en la cargada exactamente el paquete original, a = 0,010 y soporte 96 < r < 144. Se evoluciona hasta τ240 con dt = 0,001 y hasta τ300 con dt = 0,0005. En h = 0,025 se reutiliza el archivo verificado de preparación. Para la sensibilidad h = 0,05 se reproduce la preparación en R = 256 a dt = 0,001 con el perfil y el método originales antes de extenderla. En τ300 se publican la diferencia con el archivo histórico, por campo y velocidad y en inventarios hasta r = 40 y r = 60, para la malla fina. Se exige que en ambas cajas amplias los inventarios de cada caso a esos dos radios coincidan con el histórico dentro de 10⁻⁷ unidades M2 y que la cola inicial en la última unidad sea menor de 10⁻²⁰ en valor absoluto. Si falla la identidad interior se diagnostica antes de interpretar.

| Réplica | R | h | dt tras disparar | Finalidad |
|---|---:|---:|---:|---|
| Histórica | 256 | 0,025 | 0,0005 | Medir el efecto real de la pared sobre flujos brutos, restas y saldo |
| Principal | 384 | 0,025 | 0,0005 | Salida de extracción |
| Temporal | 384 | 0,025 | 0,001 | Misma pareja de estados en τ300 |
| Espacial | 384 | 0,05 | 0,001 | Comparar con la temporal a igual dt |
| Segunda caja amplia | 416 | 0,025 | 0,0005 | Sensibilidad al borde entre dos ventanas causales limpias |

Con velocidad límite uno, el primer retorno del paquete de carga a r es τ = 2R − 144 − r. En R = 256 llega como pronto a r60 en s = 8 y a r40 en s = 28. La señal nueva alcanza r60 a partir de s = 54 y r40 a partir de 34. No hay una ventana de descarga protegida del pulso antiguo en la caja histórica. En R = 384 los primeros retornos del paquete a r60 y r40 son s = 264 y 284, y en R = 416 son 328 y 348. Los retornos de la nueva señal ocurrirían en s = 2R − 6 − r. Se comparará R256 con R384 en las ramas apagadas, en las restas encendida−apagada y en el contraste entre preparaciones. El resultado principal usa las dos cajas con margen geométrico positivo. [Prerregistro de retención](../paso3_20261118/PRERREGISTRO.md)

## Observables y ventana congelados

Guardar en las 241 muestras enteras s = 0…240 los inventarios E y Q de la caja, de r < 40 y de r < 60, el trabajo W y los flujos **netos acumulados** F de E y Q en ambas caras, integrados en cada paso interno del integrador. Se conserva el signo de las entradas. Para cada preparación p y cada radio r se define

- δF = F_encendida − F_apagada, δW = W_encendida − W_apagada.
- Y_p,E = δF_E − δW. Y_p,Q = δF_Q.
- D_X = Y_cargada,X − Y_gemela,X. Para contrastar se infiere independientemente Y_p,X como −(ΔX_interior,encendida − ΔX_interior,apagada), con cada Δ referido al propio s = 0. El balance de una rama es ΔE + F_E − W o ΔQ + F_Q. Se publicará el balance global y el de la corona 40…60, donde no hay fuente.

La lectura primaria es la media trapezoidal de estas curvas acumuladas en **s = 200…240**. Así se mide la cantidad que ya cruzó cada cara desde el disparo. Se conservarán las dos mitades 200…220 y 220…240 y los valores finales por separado. No se elegirá un máximo retrospectivo.

## Sensibilidad y decisión

Se adopta como mínima extracción útil para este diseño el **1 % del exceso de inventario fino en r < 40 al disparar**, común a ambos radios. Los excesos verificados son 0,00016641437105136 de E y 0,00018476257901057 de Q. Los umbrales son 1,6641437105 × 10⁻⁶ y 1,8476257901 × 10⁻⁶ unidades M2. Son criterios de diseño para esta misión.

Para cada Y y D, cada radio y magnitud, se fija U como el máximo de (i) cambios absolutos de medias temporal−espacial, principal−temporal y principal−segunda caja amplia, (ii) cambio de cada media de media ventana frente a la principal, (iii) suma de los máximos |ΔX+F−W_X| de las ramas principales que entran en la resta, (iv) mayor discrepancia puntual entre la lectura por flujo y la inferida por inventario en la réplica principal, (v) máximo absoluto de la respuesta diferencial de **flujo bruto** antes de la llegada (s ≤ 30 a r40, s ≤ 50 a r60) en las réplicas de caja amplia, y (vi) piso 10⁻¹⁰ M2. Para Q se toma W_Q = 0. Informar los residuos globales y del anillo por separado. U es una sensibilidad determinista de los contrastes ensayados.

Se considera resuelta una salida adicional en r60 si, para E y Q, tanto D − 3U(D) como Y_cargada − 3U(Y_cargada) son positivos. La etiqueta «útil al 1 %» exige además superar el umbral en ambas cotas inferiores de cada canal. r40 localiza si salió del núcleo y el balance de la corona relaciona las dos caras. Una salida conjunta resuelta en r60 dará lugar a una propuesta de captura ajustada a esa salida. Un canal aislado se reportará por separado. Para un saldo pequeño se darán la cota superior unilateral D + 3U, la magnitud conservadora |D| + 3U y sus fracciones del exceso almacenado. Si el máximo positivo compatible queda por debajo del 1 %, procede revisar el acoplamiento de la señal. Si la incertidumbre impide distinguir ese tamaño, procede mejorar la resolución o prolongar el seguimiento según su componente dominante. La recarga y la segunda descarga siguen supeditadas a la primera entrega útil a la receptora.
