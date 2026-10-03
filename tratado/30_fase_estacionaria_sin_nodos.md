# 30 · Fase espacial de un estado localizado sin nodos

## 30.1. La posibilidad que quedaba abierta

El capítulo 27 tomó como hipótesis una fase espacial común. Aquí se investiga si una fase no uniforme, por sí sola, permite evitar aquella exclusión en un estado estacionario localizado sin nodos. No se repite la prueba de planos móviles ni C0.

**Resultado analítico condicionado:** para un único campo complejo de M2, un estado monofrecuencial Φ=e^{iωt}ψ(x), con ψ∈C²(R³)∩H¹(R³) y ψ(x)≠0 en todo punto, tiene fase espacial constante. Se suponen χ real estático, ausencia de fuentes y derivadas espaciales ordinarias, sin potencial gauge. No se exige que la fase esté acotada o tenga límite en el infinito. La prueba completa aparece abajo; no se atribuye una certificación formal ni revisión externa.

## 30.2. Fase global y corriente estacionaria

Como R³ es simplemente conexo y ψ no se anula, el mapa ψ/|ψ| admite un levantamiento real global y suave θ. Escribir ψ=f e^{iθ}, f=|ψ|>0. La ecuación estacionaria tiene la forma

\[
-\Delta\psi+A(x)\psi=0,\qquad
A=m^2-\omega^2+2\lambda_0|\psi|^2+g\chi+\tfrac h2\chi^2\in\mathbb R.
\]

Su parte imaginaria, multiplicada por f, da

\[
\nabla\cdot(f^2\nabla\theta)=0.
\tag{30.1}
\]

La descomposición ortogonal de las derivadas implica

\[
\int f^2<\infty,\qquad
E_\theta:=\int f^2|\nabla\theta|^2\le\int|\nabla\psi|^2<\infty.
\tag{30.2}
\]

No se usa que el estado minimice energía. Las dos cotas proceden de H¹ y valen también para un candidato estacionario que no sea un mínimo.

## 30.3. Truncamiento que controla la frontera

Sea Tₙ(s)=max(−n,min(s,n)), con n>0, y sea η_R un corte suave: 0≤η_R≤1, igual a uno en B_R, cero fuera de B_{2R}, y |∇η_R|≤C/R. La función η_R²Tₙ(θ) tiene soporte compacto y es una prueba débil admisible. Se puede obtener mediante aproximaciones suaves de Tₙ; en cada compacto f es estrictamente positivo y todos los campos son regulares.

Usar esa prueba en (30.1) e integrar por partes, conservando el término del corte:

\[
\int\eta_R^2 f^2\mathbf 1_{|\theta|<n}|\nabla\theta|^2
=-2\int\eta_R T_n(\theta)f^2\nabla\theta\cdot\nabla\eta_R.
\tag{30.3}
\]

El lado izquierdo es no negativo. Por Cauchy–Schwarz, |Tₙ|≤n y (30.2),

\[
0\le\int\eta_R^2 f^2\mathbf 1_{|\theta|<n}|\nabla\theta|^2
\le\frac{2Cn}{R}\,E_\theta^{1/2}\,\|f\|_{L^2}.
\tag{30.4}
\]

Primero fijar n y hacer R→∞. Dominación por la densidad integrable de Eθ, o el lema de Fatou, obliga a

\[
\int_{|\theta|<n}f^2|\nabla\theta|^2=0.
\]

Después hacer n→∞. La fase real es finita en cada punto y f>0; por tanto ∇θ=0 casi en todas partes, y por regularidad en todas partes. θ es constante en R³. El orden de los límites es esencial. No se elimina una contribución en el infinito suponiendo de antemano que θ sea acotada.

## 30.4. Comprobación de alcance

La identidad local se contrasta de forma independiente: diferencias centrales de Im(ψ*Δψ), usando campos complejos construidos a partir de jets reales de f y θ, coinciden con ∇·(f²∇θ). Esa auditoría sólo verifica el álgebra y sus signos. El paso global es la desigualdad (30.4), con todas sus hipótesis expuestas, y no una inferencia estadística a partir de muestras.

La ausencia de nodos es sustantiva. Por ejemplo, el campo matemático ψ=(x+iy)e^{−r²} tiene norma y energía de gradiente finitas, corriente proporcional a e^{−2r²}(−y,x,0) de divergencia cero y circulación. Se anula en el eje z, y su ángulo no admite un levantamiento real global en el complemento del eje. Por ello no satisface la hipótesis del lema. Se usa sólo como control lógico de alcance: no se afirma que sea una solución de M2.

La literatura ya relaciona nodos, fases multivaluadas y circulación; el resumen primario de J. Riess, [Phys. Rev. D 2, 647 (1970)](https://doi.org/10.1103/PhysRevD.2.647), ofrece un antecedente en estados cuánticos estacionarios. No se importa de ese artículo un teorema sobre M2 ni se atribuye novedad bibliográfica a este lema. La deducción aplicable al proyecto es la expuesta aquí.

## 30.5. Puerta de C7

Si además se cumplen las hipótesis restantes de 27 —campos clásicos acotados H¹ que tienden uniformemente a cero en el infinito, λ₀≥0, g,h,M>0 y ω²<m²—, una rotación global elimina θ y permite aplicar el resultado ya demostrado allí. No se presupone monotonía radial. Ambos perfiles resultan esféricos y estrictamente monótonos desde un centro común.

Así queda descartada también la tentativa de rescatar una cadena estacionaria finita **sin nodos** añadiéndole únicamente una fase espacial suave. Una fase no constante en un candidato localizado de esta clase requiere violar alguna hipótesis: nodos o defectos topológicos, fuentes o fronteras físicas, campos gauge adicionales, ausencia de localización H¹, o dependencia temporal más general. La lista no asegura que ninguna de esas alternativas funcione.

La corriente espacial y el flujo energético del estado monofrecuencial son proporcionales a f²∇θ y, por tanto, se anulan. Esto no excluye señales o intercambios transitorios. Tampoco contradice el capítulo 29: su perturbación tiene varias frecuencias y un mediador dinámico; el límite monocromático incidente no es un estado aislado H¹. Un paquete finito cumple localización, pero posee dependencia temporal más general.

**Puerta de subpregunta:** completada por el lema y su aplicación condicionada. **C7:** PARCIAL. Siguen abiertos los estados con nodos/vórtices y los contactos o enlaces dinámicos con recursos y estabilidad demostrables. E00, E01 y C0 permanecen cerradas e intactas. Este resultado no agota las clases admisibles de M2 ni habilita M3.
