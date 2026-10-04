# Protocolo CP11 · Diagnóstico radial de χ

Prerregistro anterior a los cálculos, desde `origin/main` =
`47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81` (tag CP10). Rama
`ciencia/cp11-diagnostico-chi`. Este documento explica el contrato ejecutable
`datos/ensayo_diagnostico_chi_CP11.json`; no es otra autoridad numérica.

## Pregunta y alcance

El control temporal CP10 pasa; la comparación espacial Δr=.125/.0625 falla
en χ. Se busca distinguir error de comparación, defecto del operador y
desfase de componentes cortas. No se cambia M2, Θ, el estado CP04, las
perturbaciones, los estados guardados ni la aceptación del 2 %. No se
realizan evoluciones M2 ni se incrementa resolución o tiempo.

## Hipótesis y decisiones anteriores a los resultados

1. **H-MÉTRICA:** la interpolación unilateral o el denominador producen el
   fallo artificialmente. Se reproduce exactamente la métrica CP10 y se
   contrasta con spline simétrico integrado por Gauss en la unión de nudos,
   comparación inversa y spline con paridad en el origen. Se mide también
   el error inicial y una prueba de interpolación fabricada con funciones
   regulares de ℓ=2,4. Se descarta esta explicación del cruce del umbral si
   las tres comparaciones spline independientes siguen por encima del 2 %
   en espacio de fases, con ambos denominadores iniciales. La discrepancia
   entre métodos se conserva; no se escoge el que apruebe. La interpolación
   lineal es sólo un control de sensibilidad de orden inferior.
2. **H-OPERADOR:** el stencil no representa el operador de la acción o
   tiene modos radiales espurios negativos. Se construye independientemente
   la matriz tridiagonal de −Lℓ con pesos de volumen. Se contrasta su acción
   con `Evolution.lap`, su simetría ponderada, positividad y residuo modal.
   Tolerancia algebraica relativa 2e−12; identidad de Parseval 2e−11.
   Una incompatibilidad detiene cualquier atribución de dispersión. Un
   resultado favorable sólo descarta estos defectos algebraicos, no
   garantiza precisión de fase ni estabilidad física del M2 acoplado.
3. **H-CORTAS:** componentes de χ con k=sqrt(λ)>4 explican una parte
   importante del desacuerdo. Se diagonaliza el operador radial REAL de
   R=220 para ℓ=1…4 y ambas mallas existentes. Se proyectan campos,
   velocidades y diferencias, al inicio y al final. Se declarará predominio
   corto sólo si esos modos contienen >50 % de la diferencia cuadrática
   del espacio de fases. Se publican también cortes k=2,8,12,20, y un
   recorte suave del núcleo para controlar el borde artificial de r=40.
4. **H-DISPERSIÓN:** la diferencia de frecuencias radiales puede producir
   desfases grandes a τ=160. Se comparan λ discretos de igual índice y ℓ,
   con referencias continuas de Bessel esférico para los modos indicados.
   Se calcula Δω·τ sin ajuste a los datos. El propagador libre exacto de
   los datos iniciales es un control analítico, no una evolución de M2.
   Se exige al menos 50 % de la diferencia cuadrática observada y coseno
   ponderado entre diferencias ≥.8 para considerarlo explicación suficiente.
   Si su diferencia no explica la observada, queda descartada la explicación
   «propagación libre de χ inicial basta»; no se descarta la dispersión de
   componentes generadas por el acoplamiento.
5. **H-FUENTE:** el acoplamiento y la preparación contienen una componente
   rápida que no coincide con χ inicial completo. Si el operador pasa y
   el propagador libre no basta, el segundo caso calcula, sin evolucionar,
   χeq y χ̇eq de la ecuación elíptica CON Φ congelado en cada extremo.
   Se analiza ξ=χ−χeq, ν=χ̇−χ̇eq y la fuente exacta proyectada. Se aplica
   a esos residuos un cambio modal de fase determinado exclusivamente
   por Δω·τ, conservando χeq. Una reducción ≥50 % de la diferencia
   cuadrática apoya una explicación dispersiva delimitada. Ni esta
   corrección ni χeq se utilizan para aceptar el ensayo o para eliminar
   físicamente χ. Una reducción insuficiente se registra como resultado
   negativo y no conduce automáticamente a variantes ajustadas.

## Operador que se deriva y comprueba

Con Wᵢ=(rᵢ₊½³−rᵢ₋½³)/3 y cᵢ=rᵢ₊½²/Δr,

\[
K_\ell=D^T\operatorname{diag}(c)D
+\Delta r\,\ell(\ell+1)I
+\frac{2R^2}{\Delta r}e_Ne_N^T,
\quad -L_\ell=W^{-1}K_\ell,
\quad A_\ell=W^{-1/2}K_\ell W^{-1/2}.
\]

El flujo central es cero y la frontera exterior es Dirichlet a distancia
de media celda. La forma es positiva: suma de cuadrados de diferencias,
término centrífugo y frontera. Para el mediador libre
ωⱼ²=M²+λⱼ. El símbolo cartesiano es sólo el límite local lejos del origen;
se emplean aquí autovalores radiales, no ese símbolo como sustituto.

Congelando únicamente como diagnóstico ρ=|Φ|²,
\[
(M^2-L+h\mathcal P_L\rho)\chi_{eq}=-g\mathcal P_L\rho,
\quad (M^2-L+h\mathcal P_L\rho)\dot\chi_{eq}
=-\mathcal P_L[(g+h\chi_{eq})\dot\rho].
\]
Son problemas lineales definidos positivos, con la misma cuadratura angular
y condiciones radiales. Su residuo relativo debe ser <2e−10. La fuente
real cambia durante la evolución: sus extremos no reconstruyen su historia.

## Procedencia, reproducibilidad y puerta de parada

Ambos casos pasan exclusivamente por `herramientas/ejecutar_protocolo.py`.
Se capturan antes de ejecutar protocolo, Θ, código y hashes de todos los
estados/recibos de entrada. Un hilo BLAS/OMP, entorno y pools observados;
sin aleatoriedad física. La prueba algebraica usa semilla 20261003.
No se modifica ningún resultado de CP10. Se reutilizan recibos terminados;
se verifica que todas las entradas conservan sus hashes.

La puerta física original permanece `REFINAMIENTO_PENDIENTE` mientras la
comparación sin corrección siga fallando. Los resultados negativos tienen
decisión explícita y alcance. Si estos diagnósticos dejan una ambigüedad
causal que requiere historia de la fuente no guardada, se cierra esta
unidad como diagnóstico limitado, se identifica exactamente la evidencia
faltante y se detiene antes de otra campaña. No se declara agotamiento de
M2 ni inestabilidad física por esa limitación. Una continuación posterior
requiere un contraste discriminante, independiente de aumentar la malla,
y un nuevo prerregistro; no una variante elegida para pasar el 2 %.
