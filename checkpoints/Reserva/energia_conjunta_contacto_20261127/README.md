# Energía conjunta del error radial del contacto

**Decisión.** Se incorporó el núcleo a la estimación en la misma malla FV que la corona y el exterior. Desaparece la entrada de error desconocida que antes se imponía en r40. Se recuperan la carga tangente y la fase físicas y se mantienen todas las caras hasta la pared R256. La envolvente de fuerza ponderada de la cargada disminuye, pero la estimación de su propagación y realimentación sigue sin certificar el tubo puntual en s=0…40. El piloto permanece sin habilitarse.

[Protocolo](PROTOCOLO.md) · [Contraste firmado registrado antes de medirlo](PROTOCOLO_IMPULSO.md) · [Datos resumidos](resultado.json) · [Método](energia.py) · [Contraste independiente](verificar.py) · [Cota exterior de partida](../defecto_localizado_20261127/README.md)

## Una ecuación para núcleo, corona y cola

En las coordenadas radiales canónicas con volumen 4πW se transforma el error físico e en y=S e, con S diagonal y sᵢ=exp[−0,1 max(rᵢ−60,0)]. El peso es uno dentro de r60 y positivo en toda la cola. El laplaciano positivo T genera en la ecuación de aceleración el término adicional Jy, J=T−STS⁻¹. Solo se modifican los acoplamientos entre celdas vecinas que tienen pesos distintos. La pared y los potenciales locales conmutan con S. En r40 los dos coeficientes de J son exactamente cero. Las fuerzas de esa cara y la derivada de su energía de gradiente se compensan al sumar ambos lados. Sigue existiendo transporte entre núcleo y corona.

Se usa la energía rotante a carga fija de la [malla publicada](../hessiano_contacto_20261127/README.md) sobre y. Sean u el modo de fase unitario, v=(u,0), C=A+4ω²vvᵀ, P el bloque de fase y Cκ=2ωv. En variables ya ponderadas se llevan separadamente q=uᵀpᵦ+2ωvᵀx, β=uᵀb, X=x−κq y B=b−uβ. D² suma XᵀCX, BᵀPB y las normas cuadradas de las velocidades no eliminadas. El hueco empleado es k=0,17. La coordenada estática se restaura al acotar el extremo por √(2/k)D+‖κ‖|q|+|β|. Esta es una norma de desplazamiento ponderado; en r≤60 coincide con la norma espacial sin la ponderación adicional.

La conversión a carga física es exacta con u reemplazado por S⁻¹u en las proyecciones, incluida la de amplitud. La fase física se obtiene de igual manera. ‖(S⁻¹−I)u‖=2,051e−11 redondeado hacia arriba. Se registran por caso las correcciones máximas en ambas magnitudes. Para el proyector uuᵀ el conmutador con S tiene norma 1,447e−11; el del término de rango uno de C, 4,687e−11. El residuo original ‖Pu‖=3,59504e−6 se conserva.

## Propagador y fuerza no lineal

Se midieron ‖Jᵀu‖=4,374e−11, ‖Ju‖=4,347e−11 y ‖diag(J,J)κ‖=1,791e−11 (redondeados hacia arriba). Para las componentes transversales, si Jₐ=diag(J,J), se prueba la positividad numérica de b²C−JₐᵀJₐ y b²(P+uuᵀ)−JᵀJ. La segunda desigualdad se aplica sobre B perpendicular a u. En ambos casos b=0,35 deja una dirección negativa y b=0,50 pasa. Se contaron pivotes en orden radial sin permutación y se añadió la inercia del complemento escalar del término de rango uno. Como contraste, una resolución bordeada del problema inverso y un cociente espectral máximo dan 0,49217628 en los dos bloques. La decisión usa 0,50. Son controles en doble precisión.

El sistema de comparación sin cancelación de fase conserva

- |q̇| ≤ (‖Pu‖+‖Jᵀu‖)(D/√k+|β|)+|uᵀFᵦ|.
- Ḋ ≤ 0,50D+‖Jₐκ‖ |q|+(‖Ju‖+‖Pu‖)|β|+‖F‖+‖κ‖C |q̇|.
- |β̇| ≤ (2ω/√k)D+|1−2ωvᵀκ| |q|.

Aquí F es la fuerza canónica ponderada que queda al descontar el operador fijo. Para el error lineal se usaron por intervalo la envolvente temporal de Bernstein y la del resto de Taylor sobre el puente. Para el error no lineal se añade, tanto en fuerza como en proyección, el mayorante local de jacobiano L del [tubo registrado](../error_forzado_contacto_20261127/README.md) multiplicado por la cota de desplazamiento. La ponderación diagonal conmuta con el jacobiano local. Se probó la condición suficiente del tubo global convirtiendo la norma a punto por punto con min(sᵢ√(4πwᵢ)). Se registró aparte la conversión interior. No se continuó la estimación condicional una vez falló esa prueba.

| Referencia, s=0…40 | Integral superior temporal ponderada | Integral superior de Taylor ponderada | Cota puntual interior del primer intervalo, condicional |
|---|---:|---:|---:|
| Cargada | 0,00492840 | 0,000203316 | 0,011373 |
| Gemela | 0,000355652 | 0,000128807 | 0,000561 |
| Receptora | 0,000341573 | 0,000128730 | 0,000512 |

En la cargada las cotas globales anteriores de esas dos fuerzas eran 2,02365 y 0,33825. La ponderación conserva las fuentes del núcleo y las bandas exteriores, y reduce el peso de las más alejadas. En las tres referencias el primer extremo fino, s=0,125, ya excede la condición suficiente 10⁻⁴, incluso al convertir la cota solo al interior. Para el problema puramente lineal el factor de crecimiento del mayorante hace que la cota de desplazamiento ponderado al final llegue a 1,82e6 en la cargada. Este número caracteriza la pérdida de precisión del mayorante; sigue disponible la cota no lineal independiente de 147,50 en norma global de campos obtenida por energía conservada. Ni una ni otra resuelve los observables de misión.

## Impulso firmado y siguiente decisión

En cada puente de longitud 0,125 se integró primero el vector de fuerza y luego se tomó su norma, sin cancelación entre intervalos. El promedio temporal del defecto afín es la media de sus cuatro coeficientes de Bernstein y se contrastó con el salto de velocidad dividido por el intervalo menos la aceleración afín media. El resto no lineal sobre el puente es un polinomio de grado máximo nueve; la cuadratura de Gauss de cinco puntos integra su vector firmado. En la cargada, la suma de las normas de los impulsos da 0,000903784 en el defecto temporal y 0,000199201 en Taylor. El primer valor es el 18,34 % de su envolvente; el segundo es el 97,98 %. Para la gemela se obtuvo 0,0000922621 y 0,000123016; para la receptora, 0,0000883593 y 0,000122945. Se trata de un contraste con núcleo de integración constante. El propagador que lleva la fuerza al error de campo varía en el tiempo.

**Siguiente iteración justificada.** Medir la primera corrección lineal forzada por el defecto vectorial firmado en el operador radial FV original, sin sustituirlo por la norma ni por un núcleo constante. Conservar los datos iniciales de error cero, los signos y las dos fuentes por separado. Comparar al menos dos resoluciones de la fuerza y del propagador, restaurar carga y fase, y auditar el defecto restante por sustitución sobre la referencia corregida y los observables aislados archivados. Una corrección medida aún necesitará una cota del resto no lineal en el volumen antes de usarse en H, en S o en transporte. Siguen pendientes las puertas conjuntas de misión E≥1,66414371e−6 y Q≥1,84762579e−6, atribución en r60 y entrega útil. No se integró M2 completo.

**Resumen para el Dot principal.** Diego, la energía conjunta elimina la incógnita de interfaz en r40 y conserva la información de carga y fase. En la cargada, la integral superior ponderada del defecto temporal bajó a 0,00492840; la de Taylor, a 0,000203316. La estimación de trayectoria sigue siendo demasiado amplia para el piloto. La siguiente iteración medirá cómo responde el operador radial a la fuerza firmada, con controles de resolución y del resto. [Resultado](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/energia_conjunta_contacto_20261127)

Reproducir con `OPENBLAS_NUM_THREADS=1 python3 energia.py` y `OPENBLAS_NUM_THREADS=1 python3 verificar.py` desde este directorio. [960 intervalos en CSV](envolventes.csv.gz)
