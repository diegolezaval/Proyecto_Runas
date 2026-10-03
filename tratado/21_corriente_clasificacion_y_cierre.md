# 21 · Corriente, clasificación física y condiciones de avance

## 21.1. Una corriente axial uniforme no estabiliza este tubo libre

**Resultado analítico, bajo hipótesis explícitas.** Considérese un tubo recto sin nodos, aislado, sin materia ni fuentes, con amplitudes independientes de tiempo y coordenada axial:

\[
 \Phi=f(\rho)e^{i(\omega t-Kz)},\qquad\chi=z_\chi(\rho),
 \qquad\mu^2=\omega^2-K^2.
\]

El subíndice distingue el mediador de la coordenada axial. Las ecuaciones transversales dependen de \(\omega,K\) sólo por \(\mu^2\). Escalar el radio transversal en \(E-\omega Q\) —o en la acción transversal— da

\[
 \int d^2x\,V=\mu^2\int d^2x\,f^2.
\]

Como \(V>0\) para todo campo no nulo del benchmark, no existe un perfil no trivial localizado de esta clase con \(\mu^2\leq0\). Si \(\mu^2>0\), hay un marco inercial con \(K'=0\), frecuencia \(\mu\) y el mismo perfil. La corriente uniforme es un estado en movimiento de ese tubo; no añade una presión de soporte independiente ni un parámetro fundamental.

La conclusión sobre crecimiento de onda larga se restringe a ramas con \(c_L^2<0\), comprobadas para el tubo del capítulo 18 y en el límite capilar del capítulo 20. No se ha demostrado aquí ese signo para toda rama posible de frecuencia. La simple frase «es un boost» no basta para trasladar sin cuidado un espectro con número de onda real: un modo con frecuencia compleja puede tener número de onda complejo en otro marco. Se comprueba por separado la banda de onda larga. Si en reposo \(\Omega'^2=-a^2k'^2\), \(a>0\), la transformación de Lorentz da

\[
 (\Omega-vk)^2=-a^2(k-v\Omega)^2.
\]

Para \(k\) real y \(|v|<1\),

\[
 \frac{\Omega}{k}=\frac{v(1+a^2)\pm i a(1-v^2)}{1+a^2v^2}.
\]

Usando perturbaciones \(e^{i(kz-\Omega t)}\), siempre existe una rama creciente. El coeficiente imaginario sólo tiende a cero en el límite singular \(|v|\to1\). El benchmark del capítulo 18 tiene \(a^2\simeq0.0226604\); el capítulo 20 da su origen capilar para tubos grandes.

Esta conclusión concierne a perturbaciones temporales de onda larga en tubos infinitos o suficientemente largos y al régimen de la ley efectiva. No clasifica inestabilidades absolutas frente a convectivas de paquetes localizados, ni impone condiciones en un dispositivo finito. Tampoco excluye flujos no uniformes, campos con momento angular, materia, contactos o realimentación. Esas alternativas requieren ecuaciones y estados propios; no heredan estabilidad de este cálculo. La rotación azimutal no es la corriente axial aquí estudiada.

## 21.2. Qué puede reutilizarse entre funciones

Una primordial es una función o especificación; una familia de soluciones es una estructura física. El mismo conjunto de campos puede producir distintas funciones según estado, geometría y acoplamiento. Conviene reutilizar soluciones demostradas sin confundir equivalencia funcional con equivalencia física.

| Recurso común | Resultado disponible | Funciones relacionadas | Eslabón pendiente |
|---|---|---|---|
| Estado cargado localizado | Perfil y evidencia espectral/dinámica condicionada | Reserva, referencias y resonadores | Preparación, acceso a carga y transducción |
| Interfaz y tensión superficial | Perfil de ambos campos, balance mecánico y límite capilar | Reserva, Recinto, modos de Vibración | Barreras de especies y contacto mecánico material |
| Modos y respuesta espectral | Modos ligados y dispersión en sectores calculados | Sensor, Retardo, Reloj, Vibración | Excitación, lectura, pérdidas y ruido derivados |
| Grafo de puertos | Modelo reducido condicionado | Canal, Distribuidor, Puente | Guías y uniones físicas estables |
| Control de estados | Contratos operacionales | Compuerta, Selector, Memoria, Comparador, Secuenciador | Estados distinguibles, barreras, trabajo y error |
| Contactos y portales materiales | Forma candidata; benchmark desacoplado | Captador solar, Luz, Intercambio térmico, Impulso, Polarización | Hamiltoniano material común y coeficientes medibles |
| Transporte y transformación de especies | Restricciones de conservación | Separación, Reacción, Ensamblaje | Identidades de especies, potenciales químicos, cinética y errores |

No se fusionan Reserva y Memoria: un depósito de energía no demuestra dos estados legibles con retención. Tampoco se fusionan Canal y Retardo: incluso compartiendo una estructura, el segundo requiere dispersión o almacenamiento temporal controlado. Ni Recinto y Anclaje: una barrera de transporte no constituye una referencia mecánica que reciba reacción. La evidencia disponible no determina aún una clasificación física mínima superior a las 24 funciones históricas. Mantener sus identificadores permite trazar contratos; no protege su número ni sus geometrías frente a resultados futuros.

Surgen recursos que la lista funcional no representa como primordiales independientes: **reservorio de carga, contacto de transducción, interfaz de fase y preparación de estado**. Se registran como requisitos de construcción comunes, sin asignarles una nueva ley ni convertirlos automáticamente en cuatro primordiales. Un futuro componente puede reunir varios si se demuestra su funcionamiento conjunto.

## 21.3. Revisión de Separación, Reacción y Ensamblaje

Las tres se incluyen en la evaluación actual. La instrucción de aplazarlas pertenecía a una etapa anterior y ya no delimita el alcance vigente.

En el benchmark \(A=B=1\), la dinámica material y electromagnética no recibe un acoplamiento rúnico directo. Por tanto, ese sector no predice separación selectiva, cambio de tasas químicas ni ensamblaje dirigido por los campos M2. La física material ordinaria puede realizar procesos por sí misma, pero no establece estas funciones rúnicas.

Una extensión justificable debe fijar un Hamiltoniano material común, observables de especies, estados ambientales y portales antes de calcular prestaciones. P-22 requiere diferencias de potencial químico o respuesta de especies y un mecanismo de transporte. P-23 requiere superficies de energía y tasas con balance detallado cuando corresponda; una fuente puede sacar al sistema del equilibrio, con su trabajo explícito. P-24 añade transporte, selección de estructura, cinética y acumulación de errores. Compartir un transductor sería una simplificación física real; asignar constantes de eficacia a cada función no lo demuestra. No se publican parámetros de operación ni instrucciones de fabricación material sin esa base.

## 21.4. Ciencia, ingeniería e interfaz

La interfaz «intención → configuración → control → resultado» sigue siendo un **objetivo de diseño**. Su arquitectura puede especificarse antes de disponer de un dispositivo, pero debe rechazar una tarea si no existe una realización admitida dentro del dominio verificado.

La ciencia debe aportar soluciones, incertidumbre, estabilidad y balances. La ingeniería debe aportar preparación, contactos, calibración, sensores, márgenes y retirada controlada. La interfaz debe seleccionar configuraciones ya caracterizadas; no debe pedir al operador que resuelva las ecuaciones ni ocultar la falta de una solución aceptada. Con el catálogo actual, ninguna receta R1 equivale a una operación física habilitada.

Las puertas de aceptación indican si existe evidencia de cada eslabón. Un valor `false` significa **demostración no disponible**; el resultado negativo de una realización concreta se codifica aparte. La función física se evalúa por medidas y límites derivados. Los números R1 pueden revisarse o abandonarse: no son condiciones que la teoría deba satisfacer a cualquier precio.

## 21.5. Programa siguiente con condiciones de parada

| Trabajo | Evidencia exigida para avanzar | Resultado que obliga a revisar o abandonar la vía |
|---|---|---|
| Preparación de una gota | Fuente o reservorio con energía y carga contabilizadas; transitorio que alcanza el estado objetivo | Creación neta de carga sin contrapartida; asumir una semilla sin explicar su origen |
| Primer componente de almacenamiento | Entrada/salida derivadas, accesibilidad del estado y balances de carga/energía | Usar la energía de equilibrio como capacidad extraíble sin calcular el proceso |
| Contacto material común | Hamiltoniano, escalas y respuesta que sirvan a varias funciones; límites de validez | Pérdida, fuerza o ruido asignados sólo para lograr una prestación |
| Alternativa a Canal libre | Estado completo y espectro con fronteras físicas | Reutilizar el tubo inestable o imponer un extremo ideal como prueba de estabilidad |
| Memoria | Estados distinguibles, barrera derivada, lectura/escritura y ruido | Codificar bits sólo en fases U(1) globales con barrera nula |
| Modelo capilar ampliado | Barrido de Θ, curvatura y dinámica no lineal contrastados con M2 | Extrapolar fuera del régimen o atribuir errores de malla a física |

El paquete no contiene los datos materiales ni una preparación que permitan cerrar los tres primeros renglones. Inventarlos no constituye desarrollo. El avance actual llega a soluciones comunes y coeficientes efectivos contrastados; la cadena hasta dispositivo y uso sigue abierta en los eslabones identificados.
