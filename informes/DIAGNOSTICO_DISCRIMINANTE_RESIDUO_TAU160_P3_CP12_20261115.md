# CP12/P3 · Por qué falló la comparación de χ en τ160

El comparador original reproduce el **2,0666023567 %** de discrepancia de χ en espacio de fases, frente al **2 %** prerregistrado. Se acumula una diferencia entre mallas, dominada por la respuesta al operador de χ acoplado y concentrada en números de onda altos. Las dos mallas y los perfiles fabricados apuntan principalmente a dispersión de resolución finita en esa banda. El residuo geométrico h² está comprobado en perfiles suaves. La evidencia justifica **una prueba pasiva de P4 antes de cualquier piloto nuevo**. Su símbolo reduce la diferencia espectral y, en los estados guardados, su incremento aumenta el conmutador instantáneo.

La repetición independiente termina con τ152 como último checkpoint aprobado, el negativo de τ160 conservado y CP12 abierto. La lectura volvió a autenticar la cápsula de τ160 con cero pasos M2. [Fallo original](../checkpoints/CP12/p3_20261018/continuacion_t32_t160_20261114/tramo_0152_0160/SUSPENSION.json) · [Recibo independiente](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/RECUPERACION.json)

## Cuándo y dónde aparece la diferencia

Las 401 filas de observadores conservan tiempos reales cada 0,4. El defecto crece desde 0,0364 % en τ32 a 0,9021 % en τ80, 1,4833 % en τ112 y 1,9863 % en τ152. La primera fila guardada por encima del límite es τ153,6 (2,00284 %). La anterior, en τ153,2, da 1,99872 %. Las últimas 17 filas lo superan. La localización de ese cruce usa las filas existentes. La primera **puerta oficial** fallida es τ160.

Los porcentajes de las dos bandas interiores, la velocidad y los modos se refieren al cuadrado de la norma del defecto no radial en r<40. La columna exterior se divide por el cuadrado de la norma de toda la caja. La velocidad se normaliza por la masa del mediador antes de cuadrar.

| τ | 10≤r<20 | 20≤r<40 | 40≤r<220 (caja) | Aporte χ̇/μ | ℓ=2 | ℓ=4 |
|---:|---:|---:|---:|---:|---:|---:|
| 112 | 96,6810 % | 3,1640 % | 0,000233 % | 50,329 % | 90,027 % | 9,973 % |
| 120 | 59,5611 % | 40,3157 % | 0,000325 % | 50,341 % | 90,347 % | 9,653 % |
| 128 | 9,0778 % | 90,8386 % | 0,000403 % | 50,357 % | 90,627 % | 9,373 % |
| 160 | 0,0688 % | 99,8446 % | 0,000745 % | 50,335 % | 91,224 % | 8,776 % |

El centroide del defecto en r<40 se desplaza de 18,89 a 19,85, 20,81 y 24,52. El canal acoplado del operador χ sigue la misma transición. Su fracción en 20≤r<40 sube de 3,1195 % a 40,0029 %, 90,8602 % y 99,9467 %. Campo y velocidad cambian juntos de banda. En τ160 sus normas cuadráticas respectivas son 4,9904×10⁻⁶ y 5,0577×10⁻⁶, con escala inicial común 0,02352719. El 99,8446 % corresponde al comparador en r<40. Con toda la caja como denominador, esa banda contiene el 99,8439 %. La norma cuadrática en 200≤r<220 es 4,23×10⁻³³ en τ160. La independencia de caja exige su propio contraste.

El error de campo χ solo es 1,4564 % según su puerta original, que lo normaliza con la norma inicial de campo. Los cuatro criterios espaciales restantes, los diez físicos y las tres ventanas causales pasan. La interpolación en τ160 da 2,06660 % con cúbica original o extensión por paridad central, 2,08219 % con cúbica inversa fina→gruesa y 2,00741 % con PCHIP. La magnitud es sensible a la interpolación y el signo del fallo se mantiene en las cuatro lecturas. PCHIP queda cerca del límite. La decisión usa exclusivamente la cúbica original y la norma sin giro de χ. [Resultados agregados](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/RESULTADOS_AGREGADOS.json)

## Presupuesto firmado y significado causal

En τ160 y r<40, el canal acoplado del operador χ tiene norma 2,04555 % con la misma escala inicial, proyección firmada 0,989299 sobre el defecto y coseno 0,999479. Retirar ese vector del defecto guardado reduce su potencia un **99,8865 %** y deja una norma relativa de 0,06964 %. En r<220 la retirada reduce un 99,8861 %. El cierre acoplado de caja es 4,36×10⁻⁶ en error relativo. Los operadores χ frente a la referencia original satisfacen la reducción causal exigida en las tres ventanas, con reducciones cercanas a 59,99 %. Esta última cifra tiene otra referencia que la retirada dentro de P3.

El mismo forzamiento produce una respuesta del 2,17733 % con el propagador escalar y del 2,04555 % con el acoplado. El cambio entre ambas tiene norma 0,31406 % y proyección firmada −0,05492 sobre el defecto. El cruce 2⟨libre,cambio⟩ equivale a −0,15339 veces el cuadrado del defecto. El cuadrado del cambio aporta +0,02310 en esa escala. En el presupuesto libre hay proyecciones negativas de densidad (−0,03377), reacción (−0,00881) y transferencia χ (−0,00164). La transferencia χ acoplada proyecta +0,00402. El total de cruces entre canales es −0,12534 en el libre y +0,01919 en el acoplado. Estos signos distinguen cancelación y redistribución condicionadas al Jacobiano de las dos historias. El desglose de un retorno puro χ→Φ→χ queda pendiente.

En fuerza instantánea no radial, la norma en r<40 del conmutador del operador es 0,02205 y la de la transferencia no lineal es 0,0001325. La lectura angular L12 del campo L4 deja una fracción de potencia de fuente χ en ℓ>4 de alrededor de 7,45×10⁻¹¹ en τ160. El CP04 autenticado reproduce saltos de segunda derivada de la semilla cuadrupolar de 2,3243×10⁻⁴ para χ y 2,9178×10⁻³ para su velocidad, en r=8,85 y 13,65. Estas pruebas conservan la regularidad inicial C1 entre nudos y la posibilidad de excitación de una cola corta. La atribución temporal de esa cola entre semilla, propagación y generación acoplada requiere otro contraste.

## Dispersión en la banda ocupada y residuo radial

D2 usa los autovectores de A₂ de cada malla, que son también los de la composición P3. El número de onda de referencia k usa los ceros esféricos de jℓ/R y el índice radial. En τ0, el 99 % de la potencia ℓ=2 de la ventana suave está en k≤1,328 en ambas mallas; ℓ=4 es exactamente nulo. En τ160 están presentes las colas observadas abajo. La columna de respuesta usa el vector del operador χ acoplado desplegado en la malla fina. Los porcentajes se refieren a cada espectro de χ y χ̇/μ, en la ventana suave 32–40.

| ℓ | χ gruesa con k>8 | χ fina con k>8 | Defecto con k>8 | Respuesta del operador con k>8 | Pico k del defecto |
|---:|---:|---:|---:|---:|---:|
| 2 | 0,3417 % | 0,3406 % | 99,8284 % | 99,9416 % | 12,752 |
| 4 | 21,3992 % | 21,3252 % | 99,8044 % | 99,8347 % | 12,752 |

La cola ocupa una fracción pequeña en ℓ=2 y contiene casi todo su defecto. Las proyecciones de caja completa reproducen las fracciones de defecto en k>8 (99,8280 % y 99,8043 %). En τ112–τ128 la misma banda ya domina el defecto y la respuesta, aunque la localización radial se desplaza. Los espectros del observador FV guardado corroboran la concentración y se mantienen identificados como otra base.

En el dominio radial común, se separó Δω de P3 en la diferencia del símbolo plano al mismo k y el resto radial. Este último incluye geometría, origen y cierre. Las siguientes RMS se ponderan por el defecto de τ160 en la ventana suave. La fracción de potencia emparejada supera el 99,988 % en ambos modos. La descomposición retiene el cruce de las dos contribuciones, que es negativo.

| ℓ | RMS Δω plana P3 | RMS Δω del resto radial P3 | RMS Δω total P3 | RMS Δω total P4 algebraico |
|---:|---:|---:|---:|---:|
| 2 | 1,8065×10⁻² | 2,9948×10⁻⁵ | 1,8036×10⁻² | 7,7181×10⁻³ |
| 4 | 2,0965×10⁻² | 6,7419×10⁻⁵ | 2,0899×10⁻² | 9,5516×10⁻³ |

La contribución plana es unas 603 y 311 veces mayor, respectivamente, en este contraste de frecuencias, también para el vector acoplado. Con pesos del propio estado, el RMS disminuye en P4 respecto de P3 en **ambas mallas** y ambos modos tardíos. En τ160, con pesos finos, los cocientes P4/P3 son 0,409 (ℓ=2) y 0,444 (ℓ=4). Los ceros esféricos y los símbolos prueban un contraste lineal de frecuencias con ocupación medida. Los cocientes cuantifican ese contraste; la trayectoria acoplada conserva su propio error.

Los perfiles fabricados dan dos regímenes.

- En el perfil centrado suave, ℓ=2 y 4, el error P3 en r<32 cae por un factor próximo a cuatro al dividir h por dos, y al quitar el término geométrico h² baja aproximadamente como h⁴ antes de redondeo. Por ejemplo, para ℓ=2 y h=.0625 pasa de 1,9862×10⁻⁷ a 3,5455×10⁻¹⁰ al sustraerlo, ambos relativos a la norma del campo. P4 conserva ese residuo de orden dos. Las pruebas de primera celda y 32≤r<40 están separadas.
- En la banda r≈28 con portadora k=12 y h=.125, el error del operador P3 relativo a la norma del campo vale 2,2269 (ℓ=2) y 2,2312 (ℓ=4). La norma del término h² correspondiente es 1,0201×10⁻⁴ y 5,5995×10⁻⁵. Sustraerlo deja errores de 2,2270 y 2,2313. P4 baja los errores a 0,7880 y 0,7899. Al refinar o cambiar k aparecen cancelaciones, incluidas muestras muy finas en k=8 donde P4 aumenta el error total. El archivo conserva todos los contrastes.

La combinación de ocupación, frecuencias reales de ambas mallas y perfiles fabricados da mayor respaldo a **dispersión finita en la banda tardía** que a un dominio del h² geométrico sobre ese defecto. El h² queda como límite de consistencia radial y puede intervenir en la respuesta integrada. La proporción causal separada de los dos submecanismos sigue por medir. [Resultados agregados](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/RESULTADOS_AGREGADOS.json) · [Derivación del término h²](../checkpoints/CP12/residuo_tau80_20261018/DERIVACION_GEOMETRIA.md)

## Decisión y próximo contraste

**Prerregistrar primero un contraste pasivo de fuentes y propagadores.** El término mínimo candidato es h⁶A₂⁴/560, con coeficiente de la serie inversa, aplicado sólo a χ en acción y fuerza. Su contraste espectral mejora más del 54 % del RMS ponderado por el defecto tardío. En las cuatro muestras, su contribución al conmutador original aumenta la norma instantánea del núcleo cerca de 2,65 % para ℓ=2 y de 1,82 % para ℓ=4. En τ160 las proyecciones sobre el conmutador existente son +0,01454 y +0,00523. Estos datos justifican comprobar cómo se propaga el incremento antes de elegir una nueva acción. [Diseño, refutación y validación τ0→τ160](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/PLAN_VALIDACION.md)

## Reproducción

Se registraron entradas, código y comparaciones en `a77fa401a6f649f117dd7ce270954ace08b29066` antes de ejecutar. El primer intento calculó las métricas y falló al serializar una matriz. La enmienda `22d1d87502f5f012d4b6a30214ae8d8a94590174` corrigió la conversión a JSON y se registró antes del reintento. Historia y espectros completos dieron las mismas huellas en ambos intentos. La salida final verifica antes y después los 747 elementos de τ160 y los 621, 642 y 663 de τ112/120/128. Pasaron los treinta controles originales de τ160. Quedaron registrados cero pasos M2 y ningún intento de propagar observadores.

En un checkout de este diagnóstico, `REGISTRO.json` fija adjuntos, rutas, huellas y comparador. Descargar del Release los tres ZIP públicos en un directorio privado como `frontera112.zip`, `frontera120.zip` y `frontera128.zip`. Descargar el CMS de τ160 y descifrarlo a `frontera160.zip` con la clave privada correspondiente, fuera del repositorio. El SHA-256 del CMS es `171aa617f4394c4fa6ac136b7a7da18e11bd6d511354289c91e488076159a53b` y el del ZIP es `83ee87fbaef59dceabfb1b69e48e500b443ca07aa1af53bbe91db186666925ab`.

Usar las versiones de `requirements.txt`, BLAS SkylakeX sin forzar despacho y el compilador acreditado 711636597. Si hace falta recuperarlo, verificar la huella de `trazabilidad/cierre_auditorias_20261104/COMPILADOR_PUBLICO.json` y extraer los tres DEB del adjunto. `herramientas/restaurar_compilador_p3.py --destino /ruta/prefijo --paquetes-desde /ruta/debs` comprueba cada paquete y instala el ejecutable en un prefijo privado.

```sh
diag=checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115
PATH=/ruta/prefijo/bin:"$PATH" PYTHONNOUSERSITE=1 python3 -B "$diag/diagnosticar.py" \
  --archivos /ruta/capsulas --cifrado /ruta/capsulas/frontera160.cms \
  --salida /ruta/lectura_nueva
```

El comando genera en el directorio privado D1, D2, historia, recibo y `ESPECTROS_COMPLETOS.npz`. La huella del NPZ reproducido dos veces fue `72eb0d315d9376f1198746b788ca4b35437c00fed9d812b07fcd11e7dc683a38`. Contiene los autovalores y frecuencias en ambas mallas, y potencias de campo y velocidad por índice, tiempo y ventana. Las cápsulas verificadas suministran las entradas para regenerarlo. La publicación contiene los agregados, el código y las huellas de los archivos de detalle para cotejar los resultados de la reproducción. Los archivos locales D2 e historia usan JSON compacto, consultable con `jq`.

[Prerregistro y entradas](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/PRERREGISTRO.md) · [Lector](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/diagnosticar.py) · [Recibo](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/RECUPERACION.json) · [Resultados agregados](../checkpoints/CP12/p3_20261018/diagnostico_tau160_20261115/RESULTADOS_AGREGADOS.json)
