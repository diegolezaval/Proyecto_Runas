# Residuo formal de la composición K4 con masa radial fija

Sea q=r^ℓu, a=2ℓ+2 y d=a+1. El prototipo conservado usa m_j=h r_j^a(1+h²/(12r_j²)) y c_{j+1/2}=d(Σ_{i≤j}m_i)/(r_{j+1/2}h). Para r>0 fijo, la suma de puntos medios da

\[
c(r)=r^a/h+h C_a r^{a-2}+O(h^3),\qquad
C_a=(a+1)\left[-a/24+1/(12(a-1))\right].
\]

Es la expansión del operador realmente registrado, no la de otro volumen regular. Con D_a u=u''+a u'/r, la diferencia de flujos da

\[
L_{2,h}(r^ℓu)=r^ℓ(D_a u+h²B_a u)+O(h^4),
\]

\[
B_a u=u''''/12+a u'''/(6r)
+[a(a-1)/8+C_a-1/12]u''/r²
+[a(a-1)(a-2)/24+C_a(a-2)-a/12]u'/r³.
\]

La composición registrada es L4=L2−h²L2²/12. Restando D_a²/12 y simplificando se obtiene

\[
L_{4,h}q=L_ℓq+\frac{h²r^ℓ}{6(2ℓ+1)}
\left(\frac{u''}{r²}-\frac{u'}{r³}\right)+O(h^4).
\]

El término es generalmente distinto de cero. Para u par suave, los términos singulares aparentes se cancelan: si u=u0+u2r²+u4r⁴+…, el paréntesis tiende a8u4. Esta expansión interior no certifica el orden uniforme de la primera fila o de la clausura exterior; se contrastan separadamente. Añadir términos h⁴L2³ u órdenes superiores no cancela este residuo h². Tampoco demuestra que ese término domine el error de las trayectorias actuales: a kh finito persiste la dispersión del símbolo interior y hace falta medir su ocupación.

## Restricción estructural del peso original

Para funciones suaves compactas lejos de ambos extremos, W_j=h(r_j²+h²/12). La suma de puntos medios aproxima con orden alto las integrales compactas. Si un operador exactamente W-simétrico aproximase puntualmente L_ℓ con errorO(h⁴), la antisimetría de su forma debería serO(h⁴). Sin embargo el peso adicional deja

\[
\frac{h²}{12}\int(f L_ℓg-g L_ℓf)dr
=\frac{h²}{6}\int\frac{f g'-f'g}{r}dr,
\]

que es generalmenteO(h²). Por tanto esa combinación de masa nodal fija, simetría exacta y precisión puntual global cuatro no puede suponerse para funciones generales. Esto no descarta mejoras de dispersión con orden asintótico dos. Cambiar masa, interpretación de los grados de libertad o cuadratura exige cerrar también el potencial M2 acoplado; una corrección aislada de fuerza no basta.

## Alternativas que se contrastan

La serie 4arcsin²(√s/2)=Σ a_n s^n tiene a_n=2/[n² binom(2n,n)]>0. Las truncaciones P1…P4 son positivas sobre cualquier espectro positivo; sus coeficientes no dependen deχ. P2 es exactamente el ensayo fallido. P3/P4 pueden mejorar la dispersión interior de frecuencias ocupadas y conservan el residuo geométrico anterior. No se llaman operadores radiales de orden global seis/ocho. Una discretización con masa y potencial de mayor orden es otra alternativa más amplia, con obligaciones variacionales y energéticas adicionales. Los diagnósticos prefijados deben separar estos alcances antes de seleccionar una propuesta.
