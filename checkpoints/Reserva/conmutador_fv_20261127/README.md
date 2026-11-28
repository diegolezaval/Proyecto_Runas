# Donante cargada · norma del conmutador de caras

**La cota de error de la donante cubre todo el volumen hasta s=14,625.** La última fila de la ventana de diez intervalos, que termina en s=14,75, sigue sin cerrar en r<10. El cálculo parte de las mismas fuentes y del [resultado de radios acoplados](../radios_acoplados_20261127/README.md).

| Cálculo | Trabajo directo de caras por unidad de tiempo a 14,75 | Cota interior a 14,75 |
|---|---:|---:|
| Control publicado reconstruido | 3,82520e−5 | 1,16101e−4 |
| Norma del conmutador, idéntica entrada | 3,56237e−5 | 1,15343e−4 |
| Norma del conmutador desde s=13,5 | 3,56237e−5 | 1,11872e−4 |

Los mayorantes tabulados se redondean hacia arriba. En las diez filas, incluida la candidata rechazada, la suma de costes de caras multiplicados por h pasa de 2,50743e−5 a 2,32857e−5. En el control representan el 78,19 % del coste acumulado hasta esa candidata. La última fila aceptada del nuevo cálculo tiene cota interior 9,08725e−5. En la rechazada, las otras cuatro envolventes caben en sus radios.

## Qué energía controla las caras

Se toma C=[T,W] en las coordenadas canónicas con masa FV absorbida. Hay 1042 filas activas y 1042 columnas tocadas entre r=11,9875 y r=38,0125. En todas ellas el peso de la energía de la banda 10–40 vale uno. La sección se encuentra entera en la región con potencial desplazado V+S. Se verificó su mínimo por celda y se empleó el piso común m=0,1699999999 para cada componente.

Para una cara interna i, la fila de B aplicada a x es √(4π faceᵢ) [xᵢ₊₁/swᵢ₊₁ − xᵢ/swᵢ], con swᵢ la raíz de la masa FV. Se construyó Kloc=BᵀB+mI a partir de las 1041 caras entre celdas del soporte. Ambas caras que lo conectan con el exterior se omiten por completo. La prueba B·sw=0 comprueba la energía de gradiente del campo físico constante; las entradas fuera de la diagonal se cotejan con el operador original. Por positividad de los términos omitidos, la energía de la banda domina la suma de las tres formas locales.

Se obtuvo γ=0,11464169525701416. Para verificar γ²Kloc−CᵀC se sustrajo 1e−9 de la diagonal y se factorizó la pentadiagonal resultante por Cholesky. El residuo en norma de filas fue 1,51e−14 y la holgura para aritmética en doble precisión, 3,03e−12. El margen numérico restante superó 9,96e−10. El cociente de una prueba sinusoidal independiente fue 0,07483. La clasificación usa el menor entre el mayorante anterior y γ por la amplitud de energía de 10–40. La proyección de carga del conmutador se evalúa con el operador anterior. Se mantienen κq̇, la fase, el defecto cinemático y los historiales exteriores.

## Reconstrucción y continuación

Se ejecutó desde cero el control de [radios acoplados](../radios_acoplados_20261127/README.md), incluidas todas las fuerzas, pesos, comparaciones causales y radios. Se exigió igualdad exacta de todas sus filas. En la comparación aislada se exigieron también las mismas 117 filas de entrada y los mismos radios en la candidata. Para las diez filas se reconstruyeron las 108 primeras y se siguió con el objeto de estado y sus historias en memoria. La nueva cota de caras reduce en un 6,87 % el coste directo a entrada fija. En la última fila de la marcha de diez, la fuerza no lineal en D vale como máximo 3,01322e−5, el trabajo de κq̇ 6,02832e−6 y la coordenada de fase β 1,59116e−4.

La siguiente comparación del mismo contacto es acotar WJ por celda en 10–40 antes de maximizar sobre la banda. El presupuesto actual multiplica por separado el máximo de W y el del jacobiano. A igual entrada de la primera fila rechazada, comparar esa estimación con el producto local, manteniendo la caja física por componente, el trabajo transversal, la proyección de carga y el conmutador ya verificado. Medir la reducción en la fuerza y en el punto interior antes de justificar otra marcha.

La estimación sigue sin establecer el cruce conjunto atribuible en r60 ni entrega útil a la receptora. Permanecen los mínimos de 1,66414371e−6 en energía y 1,84762579e−6 en carga.

Reproducir con `OPENBLAS_NUM_THREADS=1 python3 evaluar_caras.py` en este directorio. [Protocolo](PROTOCOLO.md) · [Filas, márgenes y controles](resultado.json) · [Recibo](RECUPERACION.json)
