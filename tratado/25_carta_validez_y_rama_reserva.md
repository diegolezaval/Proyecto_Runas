# 25 · Carta provisional de validez y rama de Reserva

## 25.1. Puertas y autoridad

E02, E03 y RES0 permanecen **PARCIALES**. El éxito de una campaña numérica no completa sus puertas. Los resultados siguientes delimitan subproblemas del M2 clásico y autorizan ensayos radiales exploratorios, sin admitir una primordial ni superar la puerta general de preparación. Las fuentes son `validacion/validez/resultados.json`, `validacion/P06/rama/resultados.json` y `validacion/verificacion_CP03.json`.

Se conservan los intentos de continuación fallidos. El último punto pendiente, M aumentado en 10⁻⁴ relativos, se recuperó mediante una ruta de continuación en dos tramos. Sus estados intermedios cambian g y M; **el punto final cambia únicamente M**. Esto es un método de resolución, no un nuevo parámetro físico. El refinamiento final conserva las tolerancias exigidas. `partial_sensitivity.json` es una instantánea anterior, sustituida como resultado vigente por `resultados.json`; no se elimina.

## 25.2. Cinco coordenadas y sensibilidad

Las unidades de comparación permanecen fijas al variar m, M, λ₀, g o h. La cantidad λ=g²/(2M²)−λ₀ es derivada. En el benchmark es pequeña por cancelación; variar las cinco coordenadas preservando esta cancelación habría ocultado la sensibilidad real.

Se calcularon diez estados a ω=0.9: ±0.01 % por coordenada, dejando las otras cuatro constantes. Cada uno tiene refinamiento de caja de 60 a 75 y de tolerancia de 2×10⁻⁹ a 5×10⁻¹⁰. La discrepancia relativa máxima de E,Q es 2.98×10⁻¹¹; no incluye error del modelo ni incertidumbre experimental. Los cocientes secantes Δln Q/Δln p son:

| Coordenada | Variación negativa | Variación positiva |
|---|---:|---:|
| m | 89.76 | 90.10 |
| M | 3488.73 | 4157.87 |
| λ₀ | 1814.56 | 1980.32 |
| g | −4179.50 | −3504.28 |
| h | 9.032 | 9.036 |

Son secantes finitas, no derivadas convergidas. Su asimetría es evidencia de no linealidad del barrido. En particular, Q pasa de 2745.77 a 4161.31 al aumentar sólo M un 0.01 %. Esta muestra no autoriza una región robusta continua ni una tolerancia de fabricación. Falta propagar una covarianza identificada y comprobar estabilidad fuera del benchmark.

El mapa analítico registra 55 muestras. Dentro del sector atractivo λ₀,h,M>0, el mínimo exacto β=min U(s)/s del capítulo 23 controla el vacío. β>0 y β<ω²<m² son condiciones de admisibilidad y localización, no un teorema de existencia o estabilidad de cada perfil. Cuando una condición falla, se registra cuál: no se identifica una iteración de Newton fallida con inexistencia física.

## 25.3. Aproximaciones y error

| Descripción | Alcance disponible | Límite actual |
|---|---|---|
| Dos campos clásicos | Acción común, coercividad condicionada, perfiles y mallas publicados | Sin identificación experimental, ruido ni garantía de error para cualquier transitorio |
| Mediador eliminado | Ecuación estática exacta elíptica; eliminación algebraica sólo si sus gradientes y frecuencias son pequeños frente a su masa efectiva | No sustituirlo en una interfaz o choque sin contrastar ambos campos |
| Expansión séxtica | Expansión local del potencial racional para h s/M² pequeño | No hay carta global nueva del error dinámico de la truncación |
| Hidrodinámica | Rama homogénea y gradientes lentos, coeficientes derivados | No describe por sí sola la pared ni todos los modos de amplitud |
| Capilaridad | 18 puntos espectrales adicionales y tres mallas por punto | Los niveles de error se aplican a esas muestras, no al espacio entre ellas |
| Reducción modal | Modos seleccionados por debajo del continuo exterior | No se ha cerrado acceso, fuga no lineal ni error de fase a largo plazo |
| Teoría cuántica | Auditoría de operadores a un lazo | Potencial de cinco términos no cerrado; sin condiciones de renormalización ni corte identificado |

La anchura plana 10–90 % de la pared es 4.41072ℓ₀. Las campañas emplean radios de norma 16,32,64; éstos no se confunden con el radio equimolar utilizado en las fórmulas. Para tubos se ensayan kR=0.2,0.6,0.9; para esferas ℓ=2,3,4. Las mallas son 0.025,0.0125,0.00625. La diferencia máxima entre extrapolaciones sucesivas es 4.50×10⁻⁶ relativa, estimación numérica y no cota certificada.

En tubos con kR=0.9 el error capilar es 26.99 %, 14.07 % y 7.18 % al aumentar el radio. Los dos primeros puntos no pasan siquiera el nivel del 10 %. En las nueve muestras esféricas el error está entre 0.31 % y 1.29 %. No se ajusta la tensión para mejorar estos valores. La fórmula capilar no se aplica al modo radial ℓ=0 de una gota.

Si una aproximación tiene error de frecuencia ΔΩ, un límite necesario de uso para error de fase εφ es t≤εφ/|ΔΩ|, antes de considerar no linealidad y ruido. El hecho de reproducir una frecuencia a 1 % no garantiza una misión larga. La carta JSON guarda límites de fase derivados para las muestras oscilatorias, no para tasas de crecimiento como si fueran fases.

En campos canónicos, a Φ=0, el polinomio que multiplica la divergencia del potencial efectivo a un lazo es proporcional a

\[
\operatorname{Tr}{\cal M}^4=2(m^2+g\chi+h\chi^2/2)^2+M^4.
\]

Contiene χ, χ³, χ⁴ y una constante ausentes del potencial declarado. Una condición de tadpole puede fijar el vacío; no proporciona por sí sola los coeficientes finitos de todos los operadores restantes. El sector clásico sigue definido, pero no se lo presenta como una teoría cuántica renormalizada completa. No se adoptan nuevos términos ni un corte arbitrario, y esto no activa M3.

## 25.4. Rama, estabilidad y controles negativos

Se continuaron 23 soluciones entre ω=0.885 y 0.995. Las integrales de sus CSV, recalculadas por Simpson, difieren de las publicadas en menos de 2.25×10⁻¹³ relativos. Las soluciones a 0.9,0.94,0.985 tienen refinamientos adicionales de caja y malla; se conserva el control con Hessiano restringido negativo a 0.985.

El cambio de signo de dQ/dω está entre 0.980 y 0.985. La estimación ω≈0.9823, Q≈162.10 no es una frontera certificada: la derivada residual cambia al reducir su paso. No se asignan todos los dígitos del solucionador a una incertidumbre física.

El mínimo radial del Hessiano a carga fija es positivo en las muestras hasta 0.980 y negativo a 0.985,0.990,0.995. El argumento angular condicionado requiere un fondo exactamente positivo y monótono; las comprobaciones muestreadas no son una prueba por intervalos de esas hipótesis. Se han calculado raíces dinámicas seleccionadas, no todo el generador, ni una campaña no lineal 3D de la rama. E03 no se cierra.

Los modos cuadrupolares seleccionados están bajo el umbral exterior 1−ω sólo en las muestras 0.885–0.920. Una raíz de caja por encima de ese umbral no se acepta como modo ligado. Cerca del giro E/Q>1, aunque algunas mallas aún tengan Hessiano restringido positivo: estabilidad local y resistencia energética a dispersarse en carga libre son preguntas distintas.

## 25.5. Energía ligada, energía accesible y fragmentación

Para un estado esférico estacionario, la identidad virial da T+3(U−ω²I)=0 y

\[
E-\omega Q=\frac23T>0,\qquad
\frac{dE}{dQ}=\omega,\qquad
\frac{d(E/Q)}{dQ}=-\frac{2T}{3Q^2}<0.
\]

La última identidad vale en una rama suave parametrizable por Q. Implica que dividir una solución en estados menores de **esa misma rama**, cuando todos existen y las interacciones son despreciables, cuesta energía. No prueba minimalidad global frente a cualquier configuración, cambio de rama o fragmentación con radiación. La primera ley se contrasta en las 23 muestras con error absoluto máximo 1.46×10⁻⁶.

En el estado de referencia E=2525.65891 y Q=2745.77392. Ondas libres diluidas de carga neta Q obedecen E≥m|Q|. Liberar toda esa carga requiere aportar al menos mQ−E=220.11501 unidades, si no queda otro recurso ligado. Incrementalmente, m−ω=0.1 por unidad de carga. Un receptor capaz de ligar carga cambia el problema y debe incluirse en el balance.

La energía de equilibrio a Q fija no equivale a energía recuperable. Una reserva debe especificar la excitación o el cambio de Q, fuente y receptor, balance, retención y ciclo. RES0 conserva pendientes la estabilidad suficiente de su dominio y la separación cuantitativa entre almacenamiento por carga y excitaciones accesibles.

## 25.6. Próximo cálculo autorizado como exploración

La simulación radial de preparación parte de un paquete gaussiano ya cargado y de su mediador relajado. Es una investigación condicional de dinámica de dos campos, no una fuente primordial resuelta. Su procedencia inicial, estabilidad no radial, apagado y ciclo siguen pendientes aunque conserve E,Q o deje una gota. Sus resultados deben archivarse antes de pasar a contactos. No se cambia ninguna puerta original para admitirla.
