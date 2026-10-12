# Regularidad del operador: resultados positivos y negativos

Son pruebas estáticas, con cero pasos M2 y las catorce fuentes originales intactas. No se usaron resultados del ejecutor perdido ni se alteraron las trayectorias CP12. El prerregistro precede a resultados.json; allí están las cinco mallas, todos los modos y hashes.

## Identidades de los armónicos sólidos

Con W=h(r²+h²/12), el operador original anula r^ℓYℓm para ℓ=0,1. En filas interiores, incluidos el origen y excluida la fila Dirichlet exterior, se verificó:

\[
L_{h,2}r^2=\frac{h^2}{2(r^2+h^2/12)},\qquad
L_{h,3}r^3=\frac{7rh^2}{2(r^2+h^2/12)},\qquad
L_{h,4}r^4=\frac{h^2(13r^2+h^2/2)}{r^2+h^2/12}.
\]

El contraste que sustituye el término angular hℓ(ℓ+1)/W por ℓ(ℓ+1)/r² anula el residuo de ℓ=2. Sin embargo, aplicado a rY₁m produce

\[
L^{\rm ingenuo}_{h,1}r=-\frac{h^2}{6r(r^2+h^2/12)},\qquad
(L^{\rm ingenuo}_{h,1}r)_0=-\frac1h.
\]

La primera celda diverge al refinar y su norma ponderada escala como h^(1/2). En N=256/512, R=1, se obtienen −256/−512 en esa celda y normas .0364246822050/.0257561398083. El operador original anula el mismo armónico hasta redondeo. Corregir exclusivamente una identidad polinómica mediante esa sustitución no da una discretización regular satisfactoria. La simetría de la semilla CP12 no autoriza una modificación general que degrade otros modos.

## Contraste derivado de la acción cuadrática

Para qℓ=r^ℓuℓ, una identidad de integración por partes da

\[
\int_0^R\!\big(r^2(q_\ell')^2+\ell(\ell+1)q_\ell^2\big)dr
=\int_0^Rr^{2\ell+2}(u_\ell')^2dr
+[\ell r^{2\ell+1}u_\ell^2]_0^R.
\]

El término de borde desaparece para regularidad central y Dirichlet exterior. La masa cinética es ∫r^(2ℓ+2)u̇ℓ²dr. Se toman volúmenes exactos Wℓ,j=(r₊^(2ℓ+3)−r₋^(2ℓ+3))/(2ℓ+3), conductancias cℓ,j+1/2=r₊^(2ℓ+2)/h y penalización Dirichlet positiva. La forma cuadrática discreta es la suma de cℓ(Δuℓ)² y la penalización exterior. Por tanto es simétrica y positiva definida bajo esa condición de borde. No contiene constantes ajustadas a resultados.

La acción determina el laplaciano de contraste, transformado de vuelta a q. Anula r^ℓ en filas interiores y reproduce Lℓ r^(ℓ+2)=(4ℓ+6)r^ℓ, ℓ=0…4. Estas identidades pasaron en las cinco mallas. No se ha implementado el potencial M2 no lineal con la misma reconstrucción radial; cambiar sólo la parte cuadrática sin cerrar esa consistencia sería insuficiente. No se aplicó este contraste a CP12 ni se probó una corrección física.

## Resultado espectral negativo para una mejora universal

Se compararon las tres primeras autofrecuencias espaciales, λ=k², con ceros de jℓ(k) para R=1. Todas las mallas N=32…512 y ℓ=0…4 dieron valores positivos y orden asintótico aproximado dos en ambas discretizaciones. El operador original ya tiene ese orden en estas pruebas, pese al residuo de primera celda para r²Y₂m.

Para ℓ=2 y N=512:

| Discretización | Error relativo λ₁ | Error relativo λ₂ | Error relativo λ₃ |
|---|---:|---:|---:|
| Original | 1.86311e−6 | 1.17312e−5 | 2.79270e−5 |
| Contraste regular variacional | 6.74480e−6 | 2.24806e−5 | 4.44572e−5 |

El contraste regular tiene errores mayores en esos tres modos; no elimina un mecanismo físico demostrado ni mejora universalmente la dispersión. Anular armónicos sólidos no sustituye pruebas de propagación, fuente, realimentación o del régimen CP12. Ninguna cifra de esta tabla es la puerta física del 2 %.

La identificación causal sigue pendiente de las respuestas originales hasta τ160 y sus puertas en las tres ventanas. Estos resultados descartan atajos matemáticos y acotan una posible investigación futura; CP12 permanece abierto.
