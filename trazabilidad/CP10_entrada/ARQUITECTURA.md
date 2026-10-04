# Arquitectura y continuidad de Rúnica

## Autoridad y lectura

El proyecto busca derivar un sistema físico e ingenieril de runas dentro de un mundo ficticio. La cadena de desarrollo y los criterios científicos siguen en [directrices](DIRECTRICES_DESARROLLO.md) y [hoja de ruta original](hoja_ruta_original/Guia_tecnica.md). La auditoría completa está en [el informe CP09](informes/AUDITORIA_ARQUITECTURA_CP09.md).

| Para saber… | Abrir… | Papel |
|---|---|---|
| Qué es y cómo empezar | [LEEME](LEEME.md) | Punto de entrada |
| Dónde estamos y qué sigue | [Estado](ESTADO_ACTUAL.md) | Vista generada del progreso y resultados |
| Estados y dependencias de las 33 etapas | [Progreso](estado_progreso.json) | Autoridad operativa |
| Qué resultado usar y qué no repetir | [Registro de cálculos](datos/registro_calculos.json) | Autoridad de continuidad de campañas |
| Qué se afirma y con qué límites | [Evidencia](datos/estado_evidencia.json) | Clasificación científica |
| Ecuaciones comunes y convenciones | [Capítulo 13](tratado/13_M2_comun_y_teoremas.md), [23](tratado/23_convenciones_y_espacio_fundamental.md) | Fuentes de teoría; 23 fija las convenciones vigentes |
| Parámetros físicos | [Θ](datos/theta_comun.json) | Benchmark común; no metas R1 |
| Parámetros operacionales adoptados | [Parámetros R1](datos/parametros.json) | Metas de diseño |
| Ruta de investigación/enmiendas | [Guía original](hoja_ruta_original/Guia_tecnica.md), [enmiendas](ENMIENDAS_HOJA_RUTA.md) | Plan conservado y cambios explícitos |
| Relacionar una afirmación con código/datos/puerta | [Índice derivado](trazabilidad/arquitectura/indice_trazabilidad.json) | Vista bidireccional; no nueva autoridad |

Ante discrepancias: evidencia reproducible actual → progreso/estado/informes → enmiendas → plan original → conversación. Un hash demuestra identidad; un `passed` demuestra sólo el criterio declarado. Un cálculo finalizado no completa una etapa.

## Carpetas que se conservan

| Ruta | Responsabilidad | Precaución |
|---|---|---|
| tratado/ | Capítulos fuente y algunas tablas generadas | Consultar el mapa de generadores antes de editar |
| datos/ | Definiciones, geometría, protocolos y registros | aceptacion_m2.json es una salida de un evaluador científico |
| herramientas/ | Modelos, solucionadores, generación y comprobación | Los scripts históricos tienen alcance de benchmark; no ejecutar campañas para verificar hashes |
| validacion/ | Datos numéricos, estados, diagnósticos, fallos y logs | Evidencia derivada que debe preservarse; no ignorarla por ser generada |
| fichas/ y graficos/ | Vistas y figuras | Editar sus fuentes; las vistas no demuestran un dispositivo |
| informes/ | Decisiones de cada entrega y auditorías | Cada informe describe su checkpoint, no siempre el estado vigente |
| investigacion/ | Notas exploratorias | La nota C7 está contextualizada como antecedente |
| trazabilidad/ | ZIP fuente, snapshots, hashes, auditorías e índices | No ejecutar como actuales los scripts copiados en snapshots |
| hoja_ruta_original/ | Plan maestro original | Se conserva byte a byte; sus rutas propuestas pueden no existir todavía |

## Mapa de generadores

El mapa completo de patrones y entradas está en [datos/arquitectura.json](datos/arquitectura.json). Contiene únicamente metadatos organizativos y enlaces; no física ni estados de etapa.

| Generador | Salidas principales | Uso |
|---|---|---|
| generar.py | 24 fichas, geometría SVG, atlas, capítulos 05/06, integrado | Vistas de fuentes existentes |
| verificar.py | Informe R1 y capítulo 07 | Verificación de casos reducidos y datos incluidos |
| resultados_micro.py | Capítulo 11 | Resumen de resultados microscópicos guardados |
| catalogo_aceptacion_m2.py | aceptacion_m2.json y capítulo 17 | Evaluador con política científica codificada; revisar evidencia antes de regenerarlo |
| figuras_m2.py | Tres figuras M2 de referencia | JSON y CSV guardados |
| figuras_capilaridad.py | M2_capilaridad.svg | Resultados capilares guardados |
| figuras_campana_4_2.py | Figuras CP03 SVG/PNG | Rama y carta de validez |
| figuras_preparacion_m2.py | Figura CP04 SVG/PNG | Ensayo radial guardado |
| graficos_micro.py | Cuatro figuras de microscopia | Resultados y grafos reducidos |
| generar_continuidad.py | ESTADO_ACTUAL e índice de trazabilidad | Progreso/evidencia/enlaces, sin simulación |

El capítulo 19 conserva una síntesis histórica manual 4.0. El linaje inicial de E00 enumera 16 afirmaciones; el índice actual deriva las 26 de estado_evidencia y conserva los enlaces de aquel linaje sin reescribir la evidencia del cierre E00. Las figuras E00 forman parte de su resultado archivado; no es necesario ejecutar su reproducción independiente para continuar.

## Entorno y verificación segura

Entorno probado: Python 3.12.14, Linux/POSIX y las cuatro versiones fijadas en requirements.txt. El adaptativo importa fcntl; en Windows debe usarse un entorno compatible, por ejemplo Linux/WSL, hasta implementar y ensayar otra plataforma. El solucionador histórico ofrece NumPy; el protocolo CP10 usa y registra la fuerza C, por lo que su reproducción exige `cc`. No se incluyen bibliotecas instaladas ni cache compilada como dependencia del checkpoint.

```bash
python -m pip install -r requirements.txt
python herramientas/verificar_entorno.py --cp10
python herramientas/checkpoint.py --verificar
python herramientas/verificar_continuidad.py --solo-lectura
python herramientas/generar_continuidad.py --comprobar
python herramientas/auditar_arquitectura.py
python herramientas/regresion_estructural.py --salida ../regresion_estructural.json
```

La regresión se ejecuta en una copia temporal y usa datos guardados. Comprueba fuentes, estados, enlaces, regeneración, reutilización de un cálculo terminado y recuperación de CP08; conserva los bytes del corpus. Algunos verificadores históricos escriben resultados/informes, por lo que se deben ejecutar en copia si se usan directamente. reproducir.py conserva la reproducción histórica, que es distinta de continuar investigación y puede ser costosa.

Para actualizar las vistas de continuidad, después de actualizar sus fuentes:

```bash
python herramientas/generar_continuidad.py
python herramientas/regresion_estructural.py --salida ../regresion_estructural.json
python herramientas/checkpoint.py --salida ../Proyecto_Runas_checkpoint.zip
python herramientas/checkpoint.py --verificar
```

empaquetar.py delega al mismo empaquetador. Se puede añadir `--estados-salida ../Estados_acceso.zip`; ambos ZIP deben extraerse juntos. Si no se divide, un solo ZIP contiene todo. No guardar el ZIP dentro de Proyecto_Runas/. El empaquetado rechaza temporales científicos pendientes y cambios de archivos durante la lectura. No genera ni supera puertas físicas.

## Nombres y versiones

| Término | Significado |
|---|---|
| project en VERSIONES.json | Versión del corpus de código/documentación/datos, independiente del modelo |
| M2 | Identidad de la acción fundamental; no cambia por mover un archivo o refinar malla |
| schema_version / continuity_schema | Formato de un registro; las versiones antiguas no son ediciones vigentes del corpus |
| CP09_AUDITORIA_ARQUITECTURA | Base administrativa conservada; no nuevo resultado físico |
| checkpoint / scientific_checkpoint | Entrega actual / último resultado científico cerrado, según el progreso vigente |
| run_id | SHA-256 completo de una ejecución, independiente de la versión del corpus y del tag redondeado |
| R1 | Perfil de objetivos operacionales, distinto de una realización física |
| P-xx | Identidad estable de una función primordial propuesta |
| Realización/dispositivo | Configuración física y cadena aceptada cuando exista evidencia suficiente |

No renumerar esquemas históricos ni llamar M3 a cambios de geometría, control o presentación. VERSIONES.json y el progreso deben coincidir; el manifiesto se genera desde ese estado.

## Procedencia de ejecuciones futuras

Los estados históricos conservan configuración y, en la continuación no radial, el hash del estado de origen. No todos guardan el hash de Θ, código y entorno durante la ejecución. El índice distingue hashes **del snapshot recibido** de recibos capturados antes de las ejecuciones CP10; no finge un recibo antiguo. El NPZ complejo de colocación Ω=5 es ilegible y está declarado por hash como intento fallido no reanudable. Su resultado negativo y el método posterior válido siguen separados.

Para campañas nuevas, usar un identificador completo independiente del redondeo visible y un recibo junto a los datos. Debe registrar: modelo; hash de parámetros; configuración exacta y hash; fuente/estado inicial y hash; código/importaciones relevantes y hashes; entorno; comando/semillas; método; tiempos inicial/final; estado de ejecución; salidas y hashes; comparaciones; puerta y límites; afirmaciones/informe que usan el resultado. No escribir campos de procedencia retroactivos en los NPZ antiguos.

El protocolo `datos/ensayo_mediador_CP10.json` aplica este sistema mediante `herramientas/ejecutar_con_procedencia.py`. Las ejecuciones tienen carpetas `<caso>__<run_id de 64 dígitos>` bajo `validacion/P06/no_radial/CP10/`; su configuración y fuentes capturadas preceden al proceso. El recibo conserva segmentos de piloto, continuación e interrupción, hashes de reinicio y salidas cerradas. Un recibo EN_PROGRESO no es un cálculo aceptado y sus hashes de salida anteriores pueden quedar desfasados mientras el trabajador escribe. Antes de reanudar se comprueban identidad, configuración, estado finito y tiempo guardado; una interrupción sin cierre conserva su registro y declara que el instante exacto de terminación es desconocido.

Los tags redondeados históricos se conservan dentro de cada carpeta única. La malla espacial CP10 de valor exacto .0625 aparece como .062 en el tag antiguo del NPZ: prevalecen `configuration.json`, la identidad y la configuración interna del estado. El bloqueo de la procedencia y el del integrador excluyen dobles escritores. Un resultado terminado se reutiliza; no se reconstruye desde cero para comprobarlo.

La comparación final del protocolo lee estados terminados y verifica recibos, balances y puertas. El registro de cálculos apunta a su único `resultados.json`; no se copia ese resultado sobre el de CP08. El índice derivado añade los enlaces ejecución→salidas y entrada→ejecuciones, y enlaza las afirmaciones con datos, figuras, configuración y puertas. Completar una evolución, superar una puerta finita y certificar estabilidad continua son hechos distintos.

Para siguientes protocolos M2 se añade `herramientas/ejecutar_protocolo.py`: el JSON declara `campaign_directory` bajo `validacion/` y cada caso incluye el adaptador en `extra_code`, para capturarlo también. Fija las variables de hilos antes de crear el trabajador y reutiliza el sistema de recibos CP10. `--reanudar` exige una identidad ya existente; un cambio de código o entradas no puede iniciar silenciosamente otro cálculo desde cero. Un segmento sin cierre sólo se recupera después de obtener el bloqueo y comprobar configuración, arrays y tiempo. Los estados terminados con diagnóstico pendiente se distinguen de la evolución pendiente; una salida diagnóstica parcial conflictiva requiere cierre conservador en copia.

Este adaptador conserva el lanzador CP10 y sus identidades originales. Requiere el contrato de estado NPZ de esta familia M2 (`q/v`, iniciales, `rows`, `time`, `config` y progreso compañero); otro modelo o esquema necesita su adaptador explícito. No convierte el trabajador CP10 en un solucionador universal ni cambia su estado fuente. Los bloqueos transitorios conservan la ubicación compatible de CP09. Los controles aislados de reanudación, escritor único, código cambiado y reutilización están en `validacion/arquitectura/adaptador_procedencia_futura.json`; no son una campaña física.

Antes de editar una evidencia ya entregada, conservar sus bytes y manifiesto en una instantánea identificada. `trazabilidad/CP09_entrada/` conserva los originales afectados y los hashes de los 833 archivos de entrada; los demás permanecen en su ruta con los mismos bytes. Actualizar progreso mediante una única escritura acordada y generar sus vistas después; cada colaborador trabaja en una copia/rama separada. Las dependencias textuales originales no habilitan etapas automáticamente.

## Git y crecimiento

Git directo para código, Markdown, JSON, configuraciones, SVG y datos de referencia razonables. NPZ/CSV grandes pueden pasar a LFS cuando su tamaño y frecuencia de cambio lo justifiquen, con hashes y recuperación probada. ZIP completos nuevos deben distribuirse como artefactos/Releases. Los ZIP fuente históricos actuales permanecen incluidos. No se activó LFS ni se creó/publicó un repositorio remoto.

Las exclusiones locales sólo cubren cachés, entornos y escritura temporal. Los atributos conservan bytes al hacer checkout para que la conversión automática de líneas no invalide los manifiestos. Datos numéricos, fallos y logs científicos se conservan. Las limitaciones de GitHub y la precaución de recuperar objetos LFS están documentadas con fuentes oficiales en el informe de auditoría.

No hace falta una nueva jerarquía ahora. Para nuevas campañas numerosas, crear una subcarpeta por modelo/campaña con recibo e índice; no mover las campañas cerradas. Una migración grande futura exige mapa origen→destino, hashes, actualización de referencias, prueba de extracción/recuperación y preservación de historia antes de reemplazar rutas.
