# 24 · Exclusiones tubulares y búsqueda de Canal

## 24.1. Resultado y contrato

**Resultado analítico condicionado:** el argumento de dilatación y Schur se extiende a tubos estacionarios con cualquier arrollamiento entero finito y amplitud sin nodos radiales. También se extiende a fondos axiales periódicos de amplitud positiva y fase espacial constante, o de arrollamiento azimutal fijo, frente a perturbaciones Bloch de periodo mayor. No demuestra imposibilidad general de Canal ni agotamiento de M2.

El contrato de investigación está registrado antes de estas campañas en `datos/campana_4_2.json`: longitud 100ℓ₀, misión 500t₀, banda relativa 0.01–0.08/t₀, señal de amplitud relativa ≤0.01, energía recibida ≥0.8, distorsión ≤0.05 y residuo de balance ≤10⁻⁴. Son objetivos para candidatos nuevos, no propiedades alcanzadas. El R1 histórico permanece intacto. Preparación, fuente, receptor, ruido y apagado deben resolverse para admitir un candidato.

La fuente de las 22 comprobaciones sigue siendo B.2 de la hoja original. `datos/P04_busqueda.json` copia literalmente cada requisito y registra resultados o falta de estudio. Una exclusión temprana no aprueba las pruebas posteriores.

## 24.2. Tubos con arrollamiento

Considérese, en el marco sin corriente axial,

\[
\Phi=f(\rho)e^{i(\omega t+n\varphi)},\quad \chi=z(\rho),\quad n\in\mathbb Z,
\]

con 0<ω²<m², f>0 para ρ>0, regularidad f=O(ρ^{|n|}) en el eje, mediador regular y decaimiento exponencial. Se exige energía finita por longitud y suficiente regularidad para que la variación de escala esté en el dominio del Hessiano. No hay pared, fuente, fijación local de carga ni términos cinéticos adicionales. Para n=0 no se exige monotonía: una amplitud hueca pero positiva también está incluida.

La acción transversal a frecuencia fija contiene

\[
S_\omega=2\pi\int_0^\infty\rho\,[f'^2+n^2f^2/\rho^2+z'^2/2+V-\omega^2f^2]d\rho.
\]

Al cambiar f(ρ)→f(ρ/L), z(ρ)→z(ρ/L), **también el término angular es invariante de escala**. Por estacionariedad, U−ω²I=0. Para y=(√2f,z), w=−ρy′,

\[
\langle w,H_nw\rangle=0,\quad
H_nw=2\Delta_{\perp,n}y\ne0,
\]

con Δ⊥,n actuando con −n²/ρ² en la primera componente y sin ese término en la segunda. Si ambas componentes fueran armónicas, regularidad y decaimiento obligarían a y=0. Un operador autoadjunto no negativo anularía w cuando su forma cuadrática es cero. La contradicción implica una dirección negativa. El gap exterior sitúa esa dirección en espectro discreto negativo.

En perturbaciones con el mismo arrollamiento y amplitudes axisimétricas, el operador de fase satisface Lᵥ,n f=0 y

\[
\langle v,L_{v,n}v\rangle=2\pi\int_0^\infty \rho f^2 |(v/f)'|^2d\rho\ge0.
\]

Los términos de borde se anulan en el dominio regular. Lχ≥M²>0, pues h≥0. Si λmin(Hn)=−κ²<0, para 0<k<κ se aplica el mismo complemento de Schur que en 18.7:

\[
A(\sigma)=L_u+k^2+\sigma^2-C(L_\chi+k^2+\sigma^2)^{-1}C
+4\omega^2\sigma^2(L_v+k^2+\sigma^2)^{-1}.
\]

A(0) tiene una dirección negativa; A(σ) es positivo para σ grande. Los inversos son regulares para k>0, el espectro esencial está separado de cero y la continuidad da un cruce A(σ)u=0 con σ>0. Al reconstruir fase y mediador se obtiene un modo creciente de ambos campos. La perturbación axial de promedio cero conserva Q y J a primer orden; en esta convención J=−nQ.

**Consecuencia:** añadir arrollamiento rígido a un tubo positivo, sin cambiar las restantes hipótesis, no elimina la inestabilidad longitudinal. La prueba cubre cada n finito, no sólo n=1,2. No afirma existencia para todo n ni caracteriza los modos azimutales: un sector creciente ya basta para rechazar estabilidad. No existe protección topológica inferible de la fase en el vacío Φ=0.

## 24.3. Extensión a modulación axial periódica

Sean f(ρ,z),χ(ρ,z) periódicos de periodo a, localizados transversalmente, positivos f>0 fuera del eje y con la misma fase temporal uniforme y, opcionalmente, e^{inφ}. La amplitud no depende del tiempo. Se estudia primero el funcional por celda, con periodo a fijo y **sin imponer carga fija en cada celda**. Fijarla artificialmente impediría la transferencia que el modelo sí permite.

Separar gradientes transversales y axiales da

\[
S_\omega[y_L]=T_\perp+L^2(T_z+U-\omega^2I).
\]

La estacionariedad implica Tz+U−ω²I=0. Otra vez ⟨w,H(0)w⟩=0 y H(0)w=2Δ⊥,n y≠0. Por tanto H(0) tiene una dirección negativa, que persiste para cuasimomento q suficientemente pequeño por continuidad de las formas H(q).

Para el operador de fase con derivada axial ∂z+iq,

\[
\langle v,L_v(q)v\rangle=
\int_{\rm celda}f^2\{ |\partial_\rho(v/f)|^2+
|(\partial_z+iq)(v/f)|^2\}\,dV\ge0.
\]

La igualdad exigiría v/f proporcional a e^{−iqz}; para una función periódica en la celda esto es imposible cuando q no es un múltiplo de 2π/a. Para cada q no nulo suficientemente pequeño, el gap exterior y la ausencia de kernel dan Lᵥ(q)>0. Lχ(q)≥M². Reemplazar los tres operadores del complemento de Schur por sus versiones Bloch vuelve a producir una raíz σ>0. Aunque las amplitudes Bloch sean complejas, los operadores son autoadjuntos; combinar q y −q da una perturbación física real.

La prueba usa un cuasimomento arbitrariamente pequeño, accesible en superceldas suficientemente largas. **Una celda o una simulación de pocas celdas puede no contenerlo.** No se obtiene de esta prueba un límite uniforme de la tasa de crecimiento, del número mínimo de celdas ni de la vida práctica al aumentar la separación entre gotas.

Queda descartada como guía infinita estable la clase periódica estacionaria positiva descrita, incluyendo modulación de sección y cadenas periódicas en fase. No se precisa una campaña de Newton/Bloch para refutar su estabilidad general. Si interesa un enlace finito de vida limitada, todavía hay que resolver su existencia, extremos, tasas, recepción y misión bajo otro contrato.

## 24.4. Mediador, capas y corriente

A f fijo, (−Δ+M²+h f²)χ=−g f² tiene solución localizada única: la diferencia de dos soluciones tiene energía cuadrática estrictamente positiva, salvo cero. Para g>0, el principio del máximo da χ≤0. No es posible elegir una pared estática independiente de χ y omitir su ecuación. Con Φ=0, el único mediador estático localizado es χ=0. Capas sin nodos siguen bajo la exclusión; nodos o dinámica real cambian las hipótesis y se mantienen abiertos.

Para fase ωt−Kz+nφ y amplitudes axiales uniformes, la identidad virial es U=(ω²−K²)I. V>0 excluye ω²−K²≤0. Para corriente temporal hay un marco de reposo. El paso a inestabilidad temporal con k real en un marco distinto requiere el análisis del capítulo 21; se conserva su condición cL²<0. No se extrapola automáticamente ese signo a cada rama con arrollamiento, ni se confunde inestabilidad temporal con absoluta/convectiva.

## 24.5. Comprobación numérica y alternativas abiertas

`P04_exclusiones.py` verifica el límite de onda larga del tubo de referencia mediante elementos finitos independientes, refinamiento espacial y extrapolación k→0. Da σ/k≈0.1505389, frente a √(−q/(ωq′))≈0.1505336: diferencia relativa 3.54×10⁻⁵. También calcula modos permitidos en una longitud periódica 100. Esa periodicidad es un diagnóstico; no representa extremos físicos.

| Rama original | Decisión delimitada | Pregunta que permanece abierta |
|---|---|---|
| C1 | Tubos positivos libres excluidos | Perfiles con nodos y otras ramas fuera de las hipótesis |
| C2 | Caso uniforme con cL²<0 conserva crecimiento | Corrientes no uniformes; respuesta convectiva y conjunto finito |
| C3 | Arrollamiento rígido sin nodos excluido para todo n finito | Rotación no rígida o dependencia temporal genuina |
| C4 | Capas positivas estacionarias y pared χ independiente no salvan la clase | Nodos, fuentes o mediador dinámico |
| C5 | Fondos periódicos positivos de fase axial uniforme excluidos frente a superceldas | Fase axial no uniforme, nodos, estados dinámicos y enlaces limitados |
| C6 | Sin exclusión general nueva | Gotas finitas, superficies, lazos y extremos reales |
| C7 | Cadenas infinitas estacionarias en fase bajo 24.3 | Contactos transitorios, cadenas de fase alternada, soporte y conjuntos finitos |
| C8 | Abierta | Fuente, observación y actuación con energía y retardos derivados |
| C9–C10 | Dependientes de un candidato superviviente | No se ha aprobado cuerpo de guía que permita cerrar terminales y operación |

**C0 está resuelta; C1–C8 no están agotadas en conjunto.** Las familias excluidas no se vuelven a simular como supuesta estabilización sin cambiar una hipótesis. La prioridad siguiente de Canal es C6/C7 y las variantes con flujo/fase no cubiertas; preparar contactos de Reserva comparte parte de ese trabajo. No se activa M3.

## 24.6. Procedencia y revisión

La extensión de dilatación/Schur y la demostración Bloch son derivaciones de esta entrega, con las hipótesis publicadas aquí. No se atribuyen a un artículo externo ni a una revisión científica independiente. Deben reabrirse si se identifica un error en el dominio, el argumento espectral o una solución que viole la conclusión bajo todas las hipótesis.

Como contraste metodológico, [Sakai, Ishihara y Nakao, Q-tubes and Q-crusts](https://arxiv.org/html/1011.4828v2) estudian perfiles con arrollamiento en otra teoría; su análisis energético no certifica todos los modos dinámicos. [Chen, Hydrodynamic and Rayleigh–Plateau instabilities of Q-strings](https://arxiv.org/html/2412.09815v2) estudia inestabilidad longitudinal y el límite capilar en otro potencial. Ninguno valida numéricamente M2 ni un dispositivo rúnico.
