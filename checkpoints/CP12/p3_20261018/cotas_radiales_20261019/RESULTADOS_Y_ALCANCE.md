# Resultado del contraste racional del origen

Los30 controles exactos pasaron; se conservaron20 casos, tres filas por caso. P3 reproduce u=1 y u=r² exactamente; para u=r4 queda un coeficiente no nulo de h² en todas las primeras filas ensayadas. Para u=r6 el residuo escala como h4. No se ejecutó M2 ni se repitió el preflight. Prerregistro público7bbcd08d3dd7fcf189cda4dd0d3b0c57ed71d09d.

| ℓ | Coeficiente exacto de la primera fila para u=r4 | Exponente de la norma del residuo en tres celdas |
|---:|---:|---:|
|0|-1906/4655|7/2|
|1|-219214/25137|9/2|
|2|-2260781066/77911875|11/2|
|3|-655949493578/10604671875|13/2|
|4|-1685587224089728138/15654881738671875|15/2|

El coeficiente multiplica r_i^ℓ h² y puede tener signo opuesto al residuo interior a radio fijo. La norma con pesos FV en un número fijo de celdas decae como h^(ℓ+7/2), bajo la expansión par suave registrada. Esto descarta inferir un residuo singular a partir de sustituir r=h/2 en la fórmula interior; tampoco prueba que la trayectoria sea insensible al origen. El resultado no autoriza cambiar la discretización ni declarar una tasa global.

La derivación adjunta conserva la distinción entre frecuencias del radial finito y símbolo interior, y prueba una cota factorial de colas de la matriz de siete bandas. Esa cota no es una certificación práctica de independencia de R220 ni de estabilidad del Hessiano no lineal. CP12 abierto; todas sus puertas permanecen.
