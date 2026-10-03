# 22 · Estado de evidencia y metodología de continuidad

## 22.1. Auditoría de entrada

La fuente única de estado inicial de esta iteración es `Proyecto_Runas_M2_4_0(1).zip`, conservada íntegra en `trazabilidad/fuente_M2_4_0.zip`. Se revisaron sus 156 archivos antes de modificar el proyecto. El inventario con tamaños y SHA-256 se conserva en `trazabilidad/auditoria_entrada.json`.

Se leyeron teoría, derivaciones, fichas, JSON y código, se contrastó el integrado con sus fuentes, se analizaron los datos brutos y la estructura SVG y se verificó la integridad del manifiesto original. La reproducción de los cálculos originales terminó correctamente: los siete CSV previos coinciden exactamente en sus valores numéricos. Esa coincidencia es una prueba de reproducibilidad de este entorno, no una demostración independiente de que todas las ecuaciones describan un dispositivo.

El archivo de origen preserva tanto las conclusiones negativas como las instrucciones de alcance que fueron sustituidas. Los documentos de trabajo vigentes y `datos/estado_evidencia.json` fijan el estado actual; no se importa información de otras conversaciones o versiones no incluidas.

## 22.2. Taxonomía

| Categoría | Qué permite afirmar | Qué no permite inferir |
|---|---|---|
| Definición | Significado de variable, observable o criterio | Existencia física |
| Hipótesis | Acción, acoplamiento o estado postulado con consecuencias contrastables | Confirmación por conveniencia |
| Aproximación | Relación dentro de una jerarquía de escalas declarada | Validez fuera de ese régimen |
| Resultado derivado | Consecuencia de premisas y operaciones explícitas | Verdad de las premisas en todo contexto |
| Resultado analítico | Demostración simbólica bajo hipótesis indicadas | Certificación de entradas numéricas no demostradas |
| Resultado numérico | Solución o estimación producida por un algoritmo concreto | Exactitud del continuo o del sistema material |
| Resultado validado | Contraste especificado, con objeto, método y rango de validez | Validación universal o experimental si sólo fue interna |
| Objetivo de diseño | Prestación que se desea obtener y se puede revisar | Parámetro medido o coeficiente derivado |
| Problema abierto | Eslabón sin evidencia suficiente y su condición de resolución | Imposibilidad demostrada |

«Derivado» puede coexistir con «analítico» o «numérico»: el primero indica procedencia, los otros el método. «Validado» exige decir **qué** se contrastó y **cómo**. En esta entrega la validación nueva es numérica interna, mediante balances, refinamiento y comparación con un límite analítico; no se declara validación experimental.

## 22.3. Qué estaba establecido y qué cambia

| Sector | Estado de entrada | Avance o conservación en 4.1 |
|---|---|---|
| Geometría y contratos | Construcción exacta de plantillas; R1 son metas | Geometría conservada; metas sometidas expresamente a la teoría |
| Acción M2 | Hipótesis escalar común; Θ total interactuante no identificado | Sin nuevos términos ni constantes fundamentales |
| Vacío, causalidad y Cauchy | Resultados analíticos del sector clásico con hipótesis | Se conservan con su alcance; no se extienden al sector cuántico/material |
| Gota cargada | Perfil convergente, sectores espectrales y transitorio | Familia de escalas, presión, energía y modo de superficie |
| Tubo libre P-04 | Perfil convergente y prueba de inestabilidad longitudinal | Resultado negativo preservado y explicación capilar; corriente axial uniforme no elimina la banda de onda larga |
| Memoria de fase | Barrera U(1) nula; no realiza la retención R1 | Se conserva; no se identifica carga almacenada con memoria legible |
| Preparación | Cero clásico invariante y carga conservada | Sigue faltando un proceso completo de preparación |
| Contactos y térmica | Contrastes condicionales; benchmark desacoplado | Sigue faltando Hamiltoniano material y ruido derivados |
| Interfaz micro–macro | Ecuación de estado y límites locales | Pared de dos campos, tensión, balance curvo, Laplace, energía y modos |
| Catálogo | 21 funciones evaluadas y 3 aplazadas | 24 evaluadas, 0 dispositivos completos; nuevas dependencias registradas |

La correspondencia funcional por sí sola sigue siendo provisional. Una ficha con ecuaciones y puertos no establece una realización. La inestabilidad de un tubo específico tampoco demuestra que todas las implementaciones posibles de Canal sean imposibles.

## 22.4. Cobertura de la cadena física

| Eslabón | Evidencia actual | Límite pendiente |
|---|---|---|
| Leyes y parámetros comunes | Acción escalar y benchmark único | Calibración, EFT cuántica y Θ material total |
| Soluciones físicas | Gota, tubo e interfaz de ambos campos | Estructuras conectadas y terminales completos |
| Modos y estabilidad | Teoremas condicionados, espectros y resultado negativo tubular | Certificación continua y dinámica no lineal general |
| Coeficientes efectivos | Ecuación de estado, tensión y respuesta capilar | Disipación, ruido y acoplamientos materiales |
| Preparación | Restricciones de conservación | Fuente/reservorio y transitorio que lleguen al estado |
| Comportamiento medible | Predicciones de energía, presión y frecuencias de campos | Transductor y protocolo de medición realizados |
| Componentes y dispositivos | Candidatos y contratos revisables | Primer dispositivo de extremo a extremo |
| Operación sencilla | Arquitectura objetivo e interfaces tipadas | Selección automática de realizaciones caracterizadas |

El inventario de evidencia enlaza premisas, resultados y bloqueos en `datos/estado_evidencia.json`. El catálogo de aceptación se refiere a **dispositivos**; no invalida los resultados de sectores que sí están derivados.

## 22.5. Reproducibilidad y criterios de detención

`herramientas/reproducir.py` ejecuta la cadena en orden, conserva un registro de cada salida y se detiene ante cualquier código de fallo. `--solo-verificar` comprueba los resultados incluidos sin repetir los solucionadores. Las versiones probadas están en `requirements.txt`; se limitan los hilos BLAS para evitar diferencias innecesarias de ejecución. Las semillas deterministas de los solucionadores espectrales quedan en el código.

Los criterios capilares se fijan en `datos/ensayo_capilaridad.json`. Son tolerancias del contraste numérico, no contratos R1. Incluyen dominio, paso, norma, virial, balance de tensiones, primera ley, cotas de la interfaz, comparación microscópica–macroscópica y persistencia del resultado negativo. Se guardan las mallas gruesas que fallan como aproximación: no se borran por obtener una gráfica menos favorable.

La convergencia se ha estudiado en el conjunto de estados indicado. No se publican intervalos certificados ni probabilidades de estabilidad. La sensibilidad a la carga está calculada; la robustez respecto de todos los parámetros independientes del modelo sigue abierta. El comportamiento no lineal general no se deduce de autovalores muestreados. No se agregan ensayos redundantes sólo para aumentar un contador.

## 22.6. Regla de autoridad y cambios

`datos/theta_comun.json` fija el benchmark escalar. `datos/estado_evidencia.json` y `datos/aceptacion_m2.json` fijan el alcance de afirmaciones y realizaciones. Los capítulos fuente contienen las derivaciones; los JSON/CSV de validación contienen los resultados. `Runica_Tratado_integrado.md`, fichas y tablas son vistas regenerables. Los textos redondeados del capítulo 20 corresponden al benchmark incluido; cualquier cambio en Θ obliga a revisar sus cifras y dominio, aunque un script termine correctamente.

El manifiesto identifica los bytes de entrega. La verificación de hashes comprueba integridad, no ciencia. La fuente archivada y el registro de cambios permiten reconstruir qué afirmaciones se conservaron, corrigieron o añadieron. Las directrices de continuidad están en `DIRECTRICES_DESARROLLO.md`.
