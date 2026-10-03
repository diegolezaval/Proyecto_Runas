# Rúnica — proyecto científico y técnico

Rúnica desarrolla una física para un sistema ficticio de runas: desde una teoría común hasta soluciones, estabilidad, preparación, componentes y dispositivos con límites comprobables. El modelo fundamental actual es M2, con un campo complejo y un mediador real. Las fichas y metas operacionales describen funciones propuestas; la aceptación depende de evidencia y puertas explícitas.

**Estado y siguiente acción:** [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md), generado desde [progreso](estado_progreso.json) y [registro de cálculos](datos/registro_calculos.json). La entrega administrativa CP09 conserva el último resultado científico CP08. No hay que repetir E00/E01/C0 para abrir el proyecto.

## Abrir por primera vez

| Necesidad | Archivo |
|---|---|
| Organización, autoridad, entorno y comandos | [ARQUITECTURA.md](ARQUITECTURA.md) |
| Teoría y convenciones | [Capítulo 13](tratado/13_M2_comun_y_teoremas.md) y [23](tratado/23_convenciones_y_espacio_fundamental.md) |
| Parámetros físicos comunes | [datos/theta_comun.json](datos/theta_comun.json) |
| Qué se demuestra y qué queda abierto | [datos/estado_evidencia.json](datos/estado_evidencia.json) |
| Hoja de ruta y enmiendas | [Guía original](hoja_ruta_original/Guia_tecnica.md), [enmiendas](ENMIENDAS_HOJA_RUTA.md) |
| Resultados actuales, fallos y cálculos cerrados | [Registro de cálculos](datos/registro_calculos.json) |
| Desde qué estados continuar | [Estado actual](ESTADO_ACTUAL.md) y configuración del ensayo correspondiente |
| Leer todo el tratado | [Documento integrado](Runica_Tratado_integrado.md), vista generada |
| Ver las plantillas | [Atlas SVG](graficos/atlas.svg), generado de geometría racional |
| Dictamen y cambios de esta auditoría | [Informe CP09](informes/AUDITORIA_ARQUITECTURA_CP09.md) |

Ante discrepancias, prevalece la evidencia reproducible del corpus sobre el resumen de estado; éste prevalece sobre el plan original. Las definiciones, hipótesis, resultados numéricos, negativos, aproximaciones y problemas abiertos se distinguen en la evidencia y los capítulos. R1 contiene metas de diseño, no mediciones. La versión del proyecto no cambia la identidad del modelo físico.

## Reconstruir y comprobar

El ZIP completo de CP09 contiene todo el corpus, los estados y la hoja de ruta original. Extraerlo en una carpeta nueva. Los dos ZIP complementarios de CP08 también reconstruyen su entrada original si se extraen juntos; sus instrucciones se conservan como antecedente en [LEEME_ENTREGA_CP08.md](LEEME_ENTREGA_CP08.md).

Con Python, la integridad de bytes no requiere bibliotecas científicas:

```bash
python herramientas/checkpoint.py --verificar
python herramientas/verificar_continuidad.py --solo-lectura
```

Con el entorno de referencia instalado:

```bash
python herramientas/verificar_entorno.py --adaptativo
python herramientas/generar_continuidad.py --comprobar
python herramientas/auditar_arquitectura.py
python herramientas/regresion_estructural.py --salida ../regresion_estructural.json
```

La regresión usa una copia temporal y los datos guardados; conserva el corpus. El entorno probado es Linux/POSIX, Python 3.12.14 y requirements.txt. El adaptativo usa fcntl; la fuerza C es opcional y tiene alternativa NumPy. Los comandos funcionan también invocando el script por ruta desde otra carpeta.

Consultar el [mapa de generadores y protocolo de continuación](ARQUITECTURA.md) antes de modificar. No editar fichas, tablas ni integrado por separado. Los verificadores históricos pueden escribir salidas: ejecutarlos en una copia. reproducir.py conserva una reproducción científica histórica distinta de esta auditoría; no usarla como siguiente investigación automática.

Después de cambios justificados y comprobados, actualizar las vistas y crear una entrega:

```bash
python herramientas/generar_continuidad.py
python herramientas/regresion_estructural.py --salida ../regresion_estructural.json
python herramientas/checkpoint.py --salida ../Proyecto_Runas_checkpoint.zip
```

El manifiesto cubre historia y fallos, además de fuentes y estados válidos. Un intento fallido de colocación tiene un NPZ ilegible conservado por hash; el auditor lo identifica como no reanudable, sin confundirlo con el resultado posterior válido. Las limitaciones de procedencia de cálculos antiguos permanecen declaradas.
