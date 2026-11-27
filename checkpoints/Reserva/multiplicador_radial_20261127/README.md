# Multiplicador espacial del error en gemela y receptora

[Protocolo previo](PROTOCOLO.md) · [Control por subintervalos](PROTOCOLO_SUBINTERVALOS.md) · [Método](medir.py) · [Verificación independiente](verificar.py) · [Cotas y estados por bloque](resultado.json) · [Fuentes y carga de partida](../energia_fisica_corregida_20261127/README.md)

## Qué se comprueba

Se usan los datos iniciales, el borde, la primera corrección firmada y las tolerancias de la entrega física anterior. En R256 con dr=0,025 se reconstruyen nuevamente las envolventes por celda de cada puente de s=0…40 (h=0,125). En gemela y receptora se coteja el máximo local del jacobiano con los 640 registros publicados. La lectura del CSV de fuerzas verifica su huella. No hay evolución M2 no lineal ni segunda corrección. Las envolventes de Bernstein del puente y las sumas absolutas de los coeficientes de ambas correcciones cubren el interior de los intervalos. Para el multiplicador se toma el máximo de las amplitudes por celda en ocho bloques de cinco unidades.

En un tubo puntual de radio ρ se amplía el desplazamiento complejo U y el real Y por ρ. Con d=2|f|U+U² y g₀=g+hₘz se utiliza el mayorante local del jacobiano ya publicado: el máximo de 6λd+|g₀|Y+hₘY²/2 y hₘd, más √2[(|g₀|+hₘY)U+hₘY|f|]. Su valor Lᵢ multiplica las tres componentes canónicas en la celda i. La construcción conserva las capas exteriores y permite que la forma de energía radial, incluida la rigidez de las caras, limite cuánto puede concentrarse el error donde L es grande.

## Norma reducida y margen

En amplitud se calcula la mayor raíz del cociente ‖M_L X‖²/(XᵀCX), con C=A+4ω²vvᵀ. En fase se calcula el análogo con P sobre u-perpendicular, donde la fase común se ha separado. Las normas se estiman con un problema simétrico de mayor autovalor que aplica la inversa por un sistema bordeado. El borde de fase impone uᵀb=0; el de amplitud incorpora el rango uno. Se usa como límite λ el valor estimado multiplicado por 1,001.

Una segunda factorización contrasta positividad de λ²H−M_L² después de sustraer además 10⁻⁷·0,17·λ² veces la identidad. Se usa orden radial, LU sin permutaciones y recuento de pivotes negativos. Al recuento del bloque base se añade el signo negativo del complemento de Schur, si procede, y se resta uno. Para amplitud el complemento es −1/(4ω²λ²)−vᵀB⁻¹v; para fase es −uᵀB⁻¹u. Aquí B es el bloque base desplazado. Se archivan para cada prueba el margen, el número de negativos, el mínimo pivote absoluto, el complemento, el residuo del autovalor y el error hacia atrás. El verificador compara ambas construcciones con proyección explícita y autovalores densos en un ejemplo independiente. Las pruebas numéricas usan doble precisión; el margen no constituye un certificado con aritmética de intervalos.

Si D es la amplitud energética reducida, el término de realimentación en fuerza queda acotado por max(λₐ,λᵦ)D+‖M_Lκ‖ |q|+‖M_Lu‖ |β|. La proyección sobre carga retiene una cota propia: para la fila imaginaria de la diferencia de fuerza, se mayoran las tres derivadas canónicas por 4λ(|f|+U)|b|, |δK|+4λ|b|² y √2(|g₀|+hₘY)|b|. Se proyecta esa fila sobre u y se usa el hueco 0,17 para la parte transversal; las contribuciones de κ y u se calculan con sus perfiles. Se conserva el menor mayorante válido entre esa proyección y la norma completa.

Se propaga el sistema positivo publicado para (D,|q|,|β|), sumando estos coeficientes por separado a la fuerza y a q̇. Se mantienen ‖Pu‖, la respuesta estática κ, el término de fase γ, las dos fuentes de truncación de los polinomios y la envolvente del cambio de Taylor. Se aplica la traza FV física previamente verificada. En cada intervalo el sistema comparador tiene coeficientes y fuentes no negativos, por lo que el extremo acota también el interior. Una continuación con radio menor es válida únicamente si la cota al comienzo y al extremo caben en ese mismo radio. El estado de error acumulado se arrastra cada vez; nunca se reinicia al reducir o aumentar el radio.

## Resultado

| Control del tubo | Gemela, primer extremo que excede | Receptora, primer extremo que excede |
|---|---:|---:|
| Traza anterior con el máximo global del jacobiano | 3,625 | 3,625 |
| Multiplicador espacial, radio fijo 1e−4 | 5,625 | 5,625 |
| Radio interno autoconsistente por bloque de cinco | 31,375 | 31,375 |
| Radio interno autoconsistente por intervalo de 0,125 | 34,375 | 34,375 |

En el último caso la comparación se sostiene hasta s=34,25. Allí la cota puntual es 9,134e−5 en la gemela y 9,226e−5 en la receptora. En el intervalo siguiente el mayorante alcanza 1,2974e−4 y 1,3105e−4, respectivamente, aun con el radio admisible más amplio. Los valores por fuera de la prueba solo diagnostican el fallo de la condición suficiente. **No queda garantizada la ventana hasta s=40** y no se ha demostrado que el campo físico haya salido del tubo.

Como referencia numérica, en el primer bloque de la gemela con el radio completo, los límites de amplitud y fase transversal son 0,783753 y 0,945961. Los coeficientes de fuerza para |q| y |β| son 0,317758 y 0,425211. En q̇ los coeficientes correspondientes a (D,|q|,|β|) son 0,630688, 0,019012 y 0,165127, redondeados hacia arriba. En ambos bloques espectrales se contaron cero negativos después del desplazamiento de margen. El cálculo conserva las diferencias de las dos preparaciones incluso cuando comparten el instante de pérdida.

## Qué cubre el número de la cargada

La integral del mayorante prescrito original en r≥160 es 1,11926996e−4. Por el factor exterior lineal previamente medido (0,0024787613) su aporte aislado a la amplitud energética de la corona 40–60 está acotado por **2,775e−7** a s=40, redondeado hacia arriba. Con la envolvente ajustada se obtiene 2,77406e−7, también redondeado hacia arriba. El primer factor proviene de la cota de propagación desde la banda lejana; el producto no mide un saldo de energía transferida. [Factor de propagación exterior](../defecto_localizado_20261127/README.md)

Se mantienen por separado la fuente ajustada en 60–160 (integral 1,93736e−6), la de r<60 (7,992e−9, sin dividir aquí núcleo y corona), la entrada por la cara de r40 (coeficiente 35860,74 multiplicado por la traza interior de error en la norma de fuerza) y la realimentación no lineal. Las integrales de las bandas cercanas son de fuerza previa a propagación. El producto de la banda lejana no controla por sí solo ninguna de esas contribuciones. La atribución conjunta en r60 y la entrega útil a la receptora siguen abiertas con los umbrales originales.

**Siguiente iteración del mismo diagnóstico.** En los controles, comprobar si se está pagando dos veces la dirección de fase: el multiplicador escalar Lᵢ se aplica a todas las componentes, incluida la fase común restaurada. Evaluar la columna real del jacobiano del resto en esa dirección y en κ con las cotas por celda; conservar el signo estructural de la simetría U(1) donde pueda verificarse y los valores absolutos en los demás términos. Contrastar estas direcciones con los coeficientes archivados y repetir la misma continuación sin reiniciar el error. Si dominan todavía los términos transversales, documentar ese límite antes de otra corrección. Para la cargada queda pendiente cerrar la interfaz y las otras bandas. No se habilita piloto ni se avanza a captura o recarga.

**Resumen para el Dot principal.** Diego, el multiplicador espacial y la continuación por intervalo extienden el control numérico del tubo de gemela y receptora hasta s=34,25; en s=34,375 la cota ya excede 1e−4. La contribución lineal aislada de la cola de la cargada hacia la corona es ≤2,775e−7 y quedan pendientes la entrada en r40, la banda cercana y la realimentación. La siguiente comprobación separará las columnas de fase común y carga del jacobiano. [Informe en la rama científica](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/multiplicador_radial_20261127)

Para reproducir desde este directorio, ejecutar con OPENBLAS_NUM_THREADS=1 los programas medir.py y verificar.py y cotejar resultado.json con el publicado.
