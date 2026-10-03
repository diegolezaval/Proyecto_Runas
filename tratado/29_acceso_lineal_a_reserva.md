# 29 · Acceso lineal condicionado a Reserva

## 29.1. Pregunta y estado de evidencia

El perfil de la rama guardado en CP03 para ω=0.9 permite plantear una pregunta pendiente de RES0/RES2: ¿una onda incidente de los campos existentes puede intercambiar energía y carga con el depósito? Se reutiliza ese perfil, sin resolver otra vez su fondo ni su espectro. La preparación no radial de CP04 y este fondo estacionario son objetos distintos. No se identifica la respuesta de uno con la del otro.

La subpregunta de dispersión lineal monocromática queda verificada en nueve frecuencias y con el mediador completo. No quedan cerradas E03, RES0 o RES2: faltan una región de estabilidad útil, la preparación de la onda incidente, amplitud y duración finitas, retroacción, recepción y ciclo. Es una investigación exploratoria condicionada, sin saltar sus dependencias funcionales.

Dos antecedentes primarios orientan el método. Cardoso, Vicente y Zhong, *Energy Extraction from Q-balls and Other Fundamental Solitons*, [Phys. Rev. Lett. 131, 111602 (2023)](https://doi.org/10.1103/PhysRevLett.131.111602), estudian conversión de bandas laterales y extracción en otro modelo. Zhang, Li, Xie y Zhou, *Superradiance of Friedberg-Lee-Sirlin solitons*, [Phys. Rev. D 111, 103027 (2025)](https://doi.org/10.1103/PhysRevD.111.103027), incluyen dos campos con un potencial diferente. Aquí se deriva el operador de M2; no se importan sus cifras ni se iguala una densidad de energía en una capa con un flujo.

## 29.2. Tres canales de la acción común

Escribir el fondo Φ₀=f(r)e^{iωt}, χ₀=z(r), con z negativo. Para ℓ=0 y Y₀₀ normalizado a integral angular cuadrática uno, usar

\[
\delta\Phi=\frac{\epsilon Y_{00}}r e^{i\omega t}
 [u_+(r)e^{i\Omega t}+u_-^*(r)e^{-i\Omega t}],\qquad
\delta\chi=\frac{\epsilon Y_{00}}r
 [u_\chi(r)e^{i\Omega t}+u_\chi^*(r)e^{-i\Omega t}].
\]

La linealización de las ecuaciones completas, sin eliminar χ, da

\[
-u''+\begin{pmatrix}
U-(\omega+\Omega)^2&V&Z\\
V&U-(\omega-\Omega)^2&Z\\
Z&Z&C-\Omega^2
\end{pmatrix}u=0,
\tag{29.1}
\]

\[
U=m^2+4\lambda_0 f^2+gz+\tfrac h2z^2,\quad
V=2\lambda_0 f^2,\quad Z=(g+hz)f,\quad C=M^2+hf^2.
\]

Las constantes escaladas proceden de `herramientas/modelo_m2.py`. No se añaden portales, fricción ni fuentes internas. El factor de la ecuación de χ se comprueba incluyendo ambas bandas conjugadas de Φ. El auditor independiente perturba la fuerza no lineal y contrasta estos coeficientes por diferencias centrales; también calcula los flujos directamente desde derivadas de ondas planas.

La regularidad impone u(0)=0. Para Ω>1.9 y Ω<100 hay dos canales cargados abiertos, de frecuencias físicas ν₊=ω+Ω>0 y ν₋=ω−Ω<0; el mediador es evanescente en el infinito. Sigue siendo dinámico en (29.1), con su término −Ω². No es una aproximación algebraica de mediador pesado.

## 29.3. Flujos, recurso incidente y balance

Definir k±=√(ν±²−m²). En las variables u±, la onda saliente es e^{-ikr} y la entrante e^{ikr}. El conjugado que reconstruye la banda de frecuencia negativa invierte su fase espacial física. Este detalle evita asignar la dirección de energía equivocada a u₋.

Normalizar los coeficientes por √k. La matriz real simétrica de (29.1), la regularidad en el origen y la ausencia de flujo del canal cerrado conservan el Wronskiano. Por tanto S†S=I entre canales abiertos. Esta unitariedad no iguala el flujo de energía de bandas de frecuencias distintas.

Para una entrada de carga negativa de norma de Wronskiano uno, sea P=|S₊₋|². Los flujos energéticos salientes relativos al incidente dan

\[
G_E=\frac{(\Omega+\omega)P+(\Omega-\omega)(1-P)}{\Omega-\omega}
=1+\frac{2\omega P}{\Omega-\omega}.
\tag{29.2}
\]

Usando el tensor y la corriente comunes de M2, la diferencia entre salida y entrada es

\[
\Delta\dot Q_{\rm exterior}=4\epsilon^2P,\qquad
\Delta\dot E_{\rm exterior}=4\epsilon^2\omega P
=\omega\,\Delta\dot Q_{\rm exterior}.
\tag{29.3}
\]

El fondo debe perder esas cantidades a segundo orden si se construye una solución completa con retroacción. El cálculo de fondo fijo sólo proporciona esta contabilidad perturbativa; no evoluciona su pérdida de carga ni demuestra cuánto tiempo puede sostenerla. La onda entrante ya aporta energía positiva y carga negativa. No se crea ese recurso a partir del vacío.

Para entrada de carga positiva, la unitariedad de dos canales da la misma probabilidad de conversión y

\[
G_E^{(+)}=1-\frac{2\omega P}{\Omega+\omega}.
\]

La pérdida de flujo exterior es una ruta candidata de depósito de energía y carga a segundo orden. No demuestra que el estado perturbado retenga ese incremento ni que vuelva a la rama. No se denomina a esta razón de flujos eficiencia neta de carga o descarga.

Con sólo un canal cargado abierto y χ cerrado, el mismo argumento obliga a |S|²=1 y G_E=1. Los tres controles de ese régimen lo confirman. La existencia de energía ligada, por sí sola, nunca se equipara a energía accesible.

## 29.4. Método y verificación

Se lee `validacion/P06/rama/perfil_w0.90000.csv` mediante interpolación cúbica de Hermite de los campos y sus derivadas. La campaña usa el mismo fondo guardado; su error no se recertifica aquí. La puerta se refiere al problema lineal sobre ese interpolante y las frecuencias muestreadas, no a una región continua de parámetros.

La discretización radial resuelve simultáneamente las dos incidencias mediante un sistema complejo disperso de tres canales. En cada canal abierto se utiliza la dispersión exacta de la diferencia central,

\[
\kappa_h=\frac2h\arcsin(kh/2),\qquad
v_h=\frac{\sin(\kappa_hh)}h,
\]

y su condición saliente y normalización √v_h. El canal cerrado emplea la raíz evanescente discreta. Así no se mezcla una velocidad de flujo continua con una onda discreta. En este párrafo h es el paso radial, no el acoplamiento del potencial.

Las mallas h=0.1, 0.05 y 0.025 no bastaron para la puerta de conversión relativa de 2 %. Se conservaron esos fallos y se añadieron 0.0125 y 0.00625; Ω=1.95 necesitó 0.003125. Hay 46 soluciones de la campaña y ocho controles de vacío, canal único y caja. Ninguna solución cerrada se recalcula al reanudar.

Un segundo método resuelve la ODE continua con condiciones de radiación continuas en Ω=1.95, 2.3 y 5. El primer intento complejo de colocación no convergió y se conserva íntegro en sus resultados, estados y registro. La formulación en partes real e imaginaria con Jacobiano de frontera explícito converge sin cambiar las tolerancias finales. La diferencia máxima de conversión frente a la malla fina es 0.239 %; la de ganancia, 1.25×10⁻⁷.

La campaña discreta tiene defecto máximo de unitariedad 1.07×10⁻¹³, residuo relativo 8.08×10⁻¹¹ y error en (29.3) de 1.34×10⁻¹⁴. El último cambio relativo de conversión es como máximo 1.60 %. Vacío y canal único tienen ganancia uno dentro de 8×10⁻¹⁶. Los tres controles de caja R=60→80 no muestran cambio significativo. Los resultados íntegros, las puertas y sus alcances están en `validacion/P06/acceso_lineal/puerta_decision.json`.

## 29.5. Resultados y puerta

Valores de las mallas finales, para incidencia negativa; se redondean para lectura.

| Ω | Probabilidad de conversión P | Ganancia energética G_E |
|---:|---:|---:|
| 1.92 | 2.74334×10⁻⁵ | 1.00004841 |
| 1.95 | 2.84988×10⁻⁶ | 1.00000489 |
| 2.00 | 2.48590×10⁻⁵ | 1.00004068 |
| 2.10 | 1.05909×10⁻⁴ | 1.00015886 |
| 2.30 | 1.22117×10⁻³ | 1.00157007 |
| 2.60 | 2.74827×10⁻⁵ | 1.00002910 |
| 3.00 | 2.67965×10⁻⁴ | 1.00022968 |
| 4.00 | 4.70079×10⁻⁴ | 1.00027295 |
| 5.00 | 3.15990×10⁻⁴ | 1.00013873 |

La mayor ganancia entre estas muestras es aproximadamente 0.157 % en Ω=2.3; no se afirma un máximo global ni una banda operativa. La verificación continua en ese punto da G_E=1.001570199. La conversión aparece en la acción M2 sin un término especial por dispositivo, pero es pequeña y condicionada a un campo incidente cargado ya disponible.

**Puerta de subpregunta:** superada para la dispersión infinitesimal, estacionaria y muestreada descrita. **Puertas funcionales:** RES0 sigue PARCIAL y RES2 sigue BLOQUEADA. El siguiente cálculo admisible deberá incluir un paquete incidente finito, coste explícito, retroacción sobre un depósito respaldado en su dominio, balances con una frontera común, recepción y recarga antes de aspirar a un ciclo. Los límites de acceso material con los portales ya fijados permanecen los de los capítulos anteriores; no se vuelven a presentar como un descubrimiento de esta entrega.
