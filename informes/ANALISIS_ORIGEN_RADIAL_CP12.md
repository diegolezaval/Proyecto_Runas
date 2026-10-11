# CP12: identidad local del operador original y límite de atribución

Este análisis matemático se realizó durante la continuación original 24→32. No cambia esa evolución ni prueba una corrección. El prerregistro, código y resultado están en trazabilidad/CP12_reconstruccion/analitica_origen. Se preservan las dos mallas originales, configuración, fuentes y el umbral del 2 %.

El operador variacional del capítulo 31 usa W_j=h(r_j²+h²/12), conductancias de cara r_{j+1/2}²/h y término angular hℓ(ℓ+1). Aplicado al armónico sólido regular r²Y_{2m}, el flujo radial da 6W_j; el término angular resta 6h r_j². El laplaciano continuo de ese armónico es cero, pero el operador original produce, en las filas interiores,

\[
L_{h,2}(r^2)_j=\frac{h^2}{2(r_j^2+h^2/12)}.
\]

En r_0=h/2 resulta 3/2 para ambas mallas. Para r fijo positivo el residuo es O(h²), y su norma con los pesos W_j sobre un núcleo fijo tiene escala asintótica h^{3/2}. Se excluye la fila exterior porque el polinomio de prueba no satisface la condición Dirichlet en R. Esta identidad local es compatible con la positividad y conservación variacional ya comprobadas; no reemplaza esas pruebas ni convierte su éxito en precisión espacial.

| h | Primera celda | Error absoluto máximo frente a la identidad | Norma ponderada del residuo, r<40 |
|---|---:|---:|---:|
| .125 | 1.5 | 1.76258e−15 | .0437093978026 |
| .0625 | 1.5 | 1.76258e−15 | .0154566910846 |

La razón de normas es .3536239770 frente a la razón asintótica 2^{−3/2}=.3535533906. El control usa sólo lap original y cero pasos M2. Los hashes de continuar_no_radial_m2.py y del protocolo de datos coinciden antes/después. Son normas de un polinomio unitario de prueba, no el error de χ de la trayectoria ni un porcentaje de aceptación.

La semilla original usa la extensión radial par s y la deformación −epsilon*r*exp(−(r/20)^4)*s'(r)Y_{2m}. Por tanto tiene comportamiento central O(r²), coherente con la regularidad cuadrupolar. El spline de fondo es C²; la deformación que usa su derivada es en general C¹ en los nudos. Una futura afirmación de orden superior debe tener en cuenta esta regularidad y la representación de los datos iniciales, además de conservar la acción y las observaciones.

El resultado identifica un defecto matemático concreto del operador en un campo regular. Todavía no demuestra que ese defecto local domine la diferencia observada ni separa su contribución de la dispersión restante, fuente no lineal y realimentación. Esa atribución sigue sometida a las integrales originales, cancelaciones y puertas causales de las tres ventanas en τ=160. No se cambia el operador, no se ensaya una corrección y CP12 permanece abierto.
