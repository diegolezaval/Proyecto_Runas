# Proyecto Rúnica · continuidad 4.2 / CP05

**Estado vigente: [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md), [progreso](estado_progreso.json) e [informe CP05](informes/ENTREGA_05_SIMETRIA_C7.md).** E00/E01/C0 cerradas; E02/E03/RES0/E04/RES1 parciales; C7 parcial; cero dispositivos completos. Los apartados 4.1 que siguen describen el antecedente conservado. Los capítulos 23–27 y registros 4.2 actualizan sus alcances.

# Rúnica · Proyecto técnico 4.1.0

**Empieza por [M2_RESULTADO.md](M2_RESULTADO.md): estado de evidencia, nuevo puente capilar, resultados negativos y reproducción.**

La edición 4.1 deriva la interfaz y la tensión superficial de ambos campos, y contrasta su predicción de equilibrio y modos en gotas y tubos. La guía libre conserva su inestabilidad longitudinal. No hay aún una realización completa de dispositivo.

**Empieza por [Runica_Tratado_integrado.md](Runica_Tratado_integrado.md).** Reúne el tratado, las derivaciones, la especificación R1, los procedimientos, las tablas y las veinticuatro fichas. Para consultar dibujos, abre [graficos/atlas.svg](graficos/atlas.svg) en un navegador o editor vectorial.

Como objetivo de diseño, la interfaz de uso se reduce a tarea, región y consigna. La ingeniería que la sostiene incluye captación, reservas, apoyo, control local, medidas y evacuación de calor. Los contratos cuantifican metas de referencia; no son operaciones físicas habilitadas.

## Contenido y autoridad

| Ruta | Contenido | Cómo se modifica |
|---|---|---|
| `tratado/01_tratado.md` | Principios, arquitectura y repertorio conceptual | Edición directa |
| `tratado/02_micro_derivaciones.md` | Acción, tensores, estabilidad y correspondencia | Edición directa |
| `tratado/03_especificacion_operacional.md` | Contratos y leyes operacionales R1 | Edición directa |
| `tratado/04_procedimientos_y_casos.md` | Casos y procedimientos cuantificados | Edición directa; actualizar cálculos si cambian supuestos |
| `DIRECTRICES_DESARROLLO.md` | Directrices permanentes de investigación | Criterio de continuidad |
| `datos/estado_evidencia.json` | Clasificación, alcance y problemas abiertos | Registro científico vigente |
| `datos/ensayo_capilaridad.json` | Mallas, dominios y criterios del nuevo contraste | Configuración reproducible |
| `trazabilidad/` | Fuente íntegra, auditoría y cambios | Conservación de antecedentes |
| `datos/geometria.json` | Tres piezas, transformaciones racionales, uniones y puertos | Fuente única de geometría |
| `datos/parametros.json` | Valores, unidades, significado y estado de evidencia | Fuente de objetivos R1 y casos; Θ escalar común en `datos/theta_comun.json` |
| `datos/modulos.json` | Texto específico de las 24 primordiales | Fuente de las fichas |
| `datos/modelos.json` | Estados, entradas, salidas y contratos reducidos | Fuente de contratos; ecuaciones descriptivas |
| `datos/microscopia.json` | Parámetros y alcance de los ensayos microscópicos | Fuente de perfiles de ensayo |
| `datos/correspondencia.json` | Mecanismo, coeficientes y evidencia por primordial | Fuente de la correspondencia |
| `datos/interfaces.json` | Vocabulario de puertos, unidades y compatibilidad | Contrato de integración |
| `datos/recetas.json` | Cuatro máquinas de estados para tareas de referencia | Especificación de secuencias |
| `datos/revision.json` | Los 50 hallazgos, por prioridad y con estado | Registro de corrección y límites |
| `datos/procedencia.json` | Fuente y cambios de edición | Trazabilidad |
| `fichas/` | 24 fichas derivadas | Regenerar; no editar por separado |
| `graficos/` | Atlas, piezas, glifos y planos técnicos SVG | Regenerar desde JSON |
| `validacion/` | Resultados, residuos, perfil radial y comprobaciones | Regenerar mediante scripts |
| `herramientas/` | Generación y comprobaciones reproducibles | Código Python legible |

Las tablas de parámetros, revisión, resultados y el documento integrado son derivados. Las cifras redondeadas en la prosa deben revisarse si se cambian parámetros: el generador no interpreta ni recalcula frases en lenguaje natural. Los scripts detectan las inconsistencias concretas que cubren sus pruebas, no cualquier contradicción imaginable.

## Estado técnico

La edición 4 añade análisis del problema de Cauchy, vacío e hiperbolicidad; espectros de dos campos; transitorios no lineales; límites cuantitativos y la prueba de una guía autosostenida inestable. Los capítulos 13–22 y los registros de evidencia y aceptación fijan el estado vigente. La revisión cubre las 24 funciones, sin exclusiones por instrucciones de etapas anteriores. Ninguna primordial se acepta como completamente derivada.

Se distinguen postulados, objetivos adoptados, deducciones y resultados verificados. R1 es una especificación operacional cuantificada; no un conjunto de mediciones. Se incluyen soluciones radiales M1 y M2, una compleción del potencial mediante mediador, dispersión de grafos, memoria modal, bombeo paramétrico y un ciclo térmico. Cada ensayo declara su alcance. No demuestra los 24 dispositivos, el primer arranque manual ni la existencia de un único conjunto microscópico de parámetros que alcance simultáneamente R1.

Esos límites figuran en el tratado y en la revisión: no se ocultan bajo la palabra «completo». El paquete entrega la arquitectura, los datos, las geometrías y los procedimientos especificados. La correspondencia física completa sigue siendo un problema de investigación. Las modalidades biológicas y nucleares no tienen un perfil operativo habilitado en esta edición.

## Reproducción

La reproducción completa se ejecuta con `python herramientas/reproducir.py`; la comprobación de resultados incluidos, con `python herramientas/reproducir.py --solo-verificar`. Véase [M2_RESULTADO.md](M2_RESULTADO.md). `requirements.txt` registra las versiones usadas. Los comandos siguientes conservan la reproducción de los sectores de ediciones previas.

Para leer MD y JSON basta un editor de texto. Los SVG son archivos vectoriales autónomos, sin fuentes remotas ni scripts. Un visor Markdown con soporte de LaTeX presenta las fórmulas; el texto fuente conserva todas las ecuaciones aunque el visor no las renderice.

Desde esta carpeta, con Python 3.11 o posterior (entorno probado: Python 3.12.14):

```bash
python herramientas/generar.py
python herramientas/verificar.py
python herramientas/generar.py
```

La última generación incorpora los resultados actuales al integrado. Para repetir además el ensayo microscópico se requieren NumPy y SciPy; las figuras requieren también Matplotlib:

```bash
python herramientas/ensayo_microscopico.py
python herramientas/correspondencia_micro.py
python herramientas/complecion_escalar.py
python herramientas/preparacion_y_motor.py
python herramientas/graficos_micro.py
python herramientas/resultados_micro.py
python herramientas/verificar.py
python herramientas/generar.py
```

El ensayo usa continuación de soluciones para evitar confundir la solución nula con un condensado. Registra dos dominios, refinamiento, identidad virial y cociente energía/carga. Las versiones del entorno de cálculo se registran en la validación. No hace falta ejecutar código para consultar los resultados incluidos.

El código de verificación comprueba geometría, contratos y casos reducidos. No maneja hardware ni ejecuta órdenes físicas. El archivo `MANIFIESTO_SHA256.json` permite identificar los bytes entregados; cambia al editar cualquier archivo y no se regenera al ejecutar los scripts anteriores.

Para comprobar los bytes de esta entrega: `python herramientas/empaquetar.py --verificar`. Después de editar y reproducir, un nuevo paquete se crea con `python herramientas/empaquetar.py --salida ../Proyecto_Runas_M2_4_1.zip`; conserva la fuente y actualiza los hashes y diferencias.
