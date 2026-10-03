# Proyecto Rúnica · continuidad 4.2 / CP08

**Estado vigente: [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md), [progreso](estado_progreso.json) e [informe CP08](informes/ENTREGA_08_REFINAMIENTO_NO_RADIAL.md).** Cálculo h=.125 terminado; puerta del subensayo: REFINAMIENTO_PENDIENTE. E00/E01/C0 cerradas e intactas; E02/E03/E04/RES0/RES1/C7 parciales; RES2 bloqueada. Cero dispositivos completos. Los capítulos 23–30 actualizan el antecedente 4.1 conservado a continuación.

# M2 4.1 · Resultados, evidencia y límites

**No se ha demostrado una realización completa de Canal, Memoria o Intercambio térmico. La prueba directa conservada muestra que M2 sostiene un tubo de dos campos, pero el tubo libre es longitudinalmente inestable. Tampoco se ha derivado el terminal físico Neumann que utilizaba el grafo.**

Este documento distingue un resultado negativo de una ausencia de cálculo. El perfil del tubo y su inestabilidad sí se han calculado, con el mismo M2 y sin parámetros fundamentales de Canal. La región de transición del extremo y la guía completa con bifurcación no se han resuelto. No se presentan como demostradas.

![Guía autosostenida e inestabilidad](graficos/M2_guia_inestable.svg)


## Avance de esta iteración

La auditoría completa y la reproducción del estado de entrada precedieron a los cambios. Los siete CSV originales coinciden exactamente en sus valores numéricos. La fuente original se conserva íntegra para trazar también los resultados negativos.

Se ha derivado y calculado una interfaz plana de **ambos campos**. Su tensión, aproximadamente **0.1265742605132** en unidades M2, determina leyes de equilibrio y modos de esferas y tubos sin ajustes por geometría. Diez perfiles a distintas escalas y cuarenta cálculos espectrales contrastan la conexión microscópica–macroscópica. Para el mayor tamaño estudiado, los errores frente al límite capilar son aproximadamente 0.15 % en frecuencia esférica y 0.68 % en crecimiento tubular, tras refinar y extrapolar la malla.

La aproximación capilar explica la inestabilidad de Canal. Se demuestra además, dentro del ansatz y régimen indicados, que una corriente axial uniforme no elimina su banda inestable de onda larga. No se añaden paredes ni pérdidas para salvarlo.

| Clasificación | Estado actual |
|---|---|
| Resultados analíticos condicionados | Conservación, vacío, causalidad, identidades de estabilidad y tensiones; restricciones de preparación y corriente |
| Resultados numéricos reproducibles | Gotas, tubos, interfaz, espectros seleccionados y transitorio conservativo |
| Aproximación contrastada | Ecuación de estado de fase y límite capilar de radios grandes |
| Provisional | Correspondencias funcionales, grafos, Kerr, motor y contratos R1 |
| Abierto | Preparación, contactos/materiales, terminales, estabilidad general y primer dispositivo completo |

Se revisan **las 24 primordiales**, incluidas Separación, Reacción y Ensamblaje. Ninguna se acepta aún como dispositivo completo. Los objetivos R1 son revisables y deben someterse a la teoría. El registro de evidencia y los límites de cada afirmación están en [el capítulo 22](tratado/22_evidencia_y_metodologia.md) y `datos/estado_evidencia.json`.

La derivación nueva está en [20 · Interfaz y límite capilar](tratado/20_interfaz_y_limite_capilar.md); la revisión de corriente, clasificación y condiciones de avance está en [21 · Corriente y cierre físico](tratado/21_corriente_clasificacion_y_cierre.md).

![Interfaz, equilibrio y modos](graficos/M2_capilaridad.svg)

## Resultado negativo preservado

| Pregunta | Resultado |
|---|---|
| ¿Existe un perfil transversal autosostenido en M2? | Sí: solución numérica convergente de ambos campos |
| ¿Es estable como guía recta larga? | No: hay crecimiento longitudinal para \(0<\hat k\lesssim0.22656\) |
| ¿La inestabilidad desaparece al refinar? | No: las tasas positivas convergen; se aporta el argumento analítico |
| ¿Basta imponer Neumann en los extremos? | No: un segmento suficientemente largo sigue admitiendo modos inestables |
| ¿El exterior de vacío equivale a Neumann? | No: produce una respuesta de decaimiento/radiación dependiente de frecuencia |
| ¿Hay un terminal completo derivado? | No: el mapa del exterior no sustituye a la solución del extremo |
| ¿Queda demostrado P-04/R1? | No; esta realización libre falla la condición de estabilidad |

La energía lineal adimensional del tubo es 51.6294938554 y su carga lineal 55.0393673559. La mayor tasa entre los puntos muestreados es \(\hat\sigma=0.0165338\). El umbral de longitud de onda es \(\lambda_c\simeq27.7331\ell_0\). En la escala ilustrativa común de 1 eV, esto equivale a 5.47248 μm y a un tiempo de crecimiento por un factor \(e\) de \(3.9810\times10^{-14}\) s. Las unidades físicas ilustran las escalas; no son mediciones ni una calibración de R1.

La demostración, sus hipótesis y el cálculo del exterior están en [18 · Guía y terminal desde M2](tratado/18_guia_y_terminal_desde_M2.md). No se infiere de este fallo que cualquier guía con materia, corriente o control sea imposible; esas realizaciones no están demostradas aquí.

## Qué quedó establecido en el sector común

- Problema de Cauchy global en la clase de energía del sector escalar clásico aislado, con un potencial coercivo y las hipótesis explicitadas.
- Vacío clásico estable y propagación causal; separación de estas propiedades respecto de las cuestiones cuánticas y materiales.
- Q-ball de dos campos con refinamiento de dominio y tolerancia, Hessianos radiales y no radiales, modo cuadrupolar ligado y dinámica no lineal conservativa.
- Identidades para todos los índices angulares de perfiles monótonos; distinción expresa entre esas identidades y una certificación espectral completa del continuo que no se ha obtenido.
- Límites cuantitativos de aproximaciones: truncación sextica, eliminación del mediador, cinética inducida y un ensayo local de linealización.

![Resultados del estado radial](graficos/M2_evidencia_numerica.svg)

## Las otras pruebas

Para **Memoria**, se deriva cómo debe calcularse el coeficiente cuártico a partir del modo y del mediador. Una codificación por dos fases globales del campo aislado tiene barrera exactamente nula; no produce la barrera R1 de \(60k_BT\). La memoria alimentada anterior no tiene aún sus coeficientes y ruido derivados de M2.

Para **Intercambio térmico**, se calculan contrastes de conductancia por canal y se identifica la necesidad de contactos y correlaciones derivadas. El benchmark desacoplado tiene intercambio rúnico con materia igual a cero. El motor de tres niveles anterior no constituye su realización.

Para **Semilla**, se demuestra que un campo clásico exactamente nulo permanece nulo bajo una modulación multiplicativa y que un bombeo U(1)-invariante no crea carga neta en un sistema cerrado. Fluctuaciones cuánticas, pares de carga y terminales cargados son casos distintos; no se han calculado como preparación completa de P-04.

Los detalles están en [16 · Pruebas de dispositivo](tratado/16_pruebas_de_dispositivo.md). Las 24 fichas conservan su geometría y contratos; [17 · Aceptación del catálogo](tratado/17_aceptacion_catalogo.md) registra **0 dispositivos completamente derivados**, 24 evaluados respecto de sus dependencias; P-22, P-23 y P-24 ya no están excluidos por la antigua instrucción.

## Lectura y reproducción

1. [M2 común, parámetros y teoremas](tratado/13_M2_comun_y_teoremas.md).
2. [Espectro y dinámica de M2](tratado/14_espectro_y_dinamica_M2.md).
3. [Regímenes de validez y coeficientes](tratado/15_regimenes_y_coeficientes.md).
4. [Pruebas de las primeras primordiales](tratado/16_pruebas_de_dispositivo.md).
5. [Guía y terminal: cálculo directo](tratado/18_guia_y_terminal_desde_M2.md).

Los números completos se conservan en JSON y los perfiles/transitorios en CSV. Las figuras son SVG. El código Python usa NumPy y SciPy; Matplotlib sólo genera las figuras. Desde la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
python herramientas/reproducir.py
```

Para comprobar sólo los resultados incluidos:

```bash
python herramientas/reproducir.py --solo-verificar
```

La reproducción completa incluye todos los ensayos originales, los nuevos perfiles/espectros y la regeneración de documentos. Se detiene al primer fallo y conserva las salidas en `validacion/reproduccion/`. Ejecutarla modifica resultados generados; el manifiesto identifica los bytes entregados, no se actualiza automáticamente.

`cierre_m2.py` es el nombre del ensayo de evaluación; sus resultados incluyen `complete_device_derived: false`. Ejecutar el código no maneja hardware. [Runica_Tratado_integrado.md](Runica_Tratado_integrado.md) conserva el tratado completo y las fichas; las secciones nuevas delimitan explícitamente el alcance de los ensayos anteriores.
