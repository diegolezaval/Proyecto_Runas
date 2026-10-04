# Rúnica — proyecto científico y técnico

Rúnica desarrolla una física para un sistema ficticio de runas: desde una teoría común hasta soluciones, estabilidad, preparación, componentes y dispositivos con límites comprobables. El modelo fundamental actual es M2, con un campo complejo y un mediador real. Las fichas y metas operacionales describen funciones propuestas; la aceptación depende de evidencia y puertas explícitas.

**Estado y siguiente acción:** [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md), generado desde [progreso](estado_progreso.json) y [registro de cálculos](datos/registro_calculos.json). CP12 retoma la reconstrucción explícita desde un reinicio τ=0 recuperado y verificado; [retoma y pruebas](informes/RETOMA_CP12_20261004.md), [prerregistro de reconstrucción](informes/PRERREGISTRO_RECONSTRUCCION_CP12.md) y [protocolo causal](informes/PROTOCOLO_CP12_CAUSA_CHI.md). Cada frontera requiere respaldo permanente descargado y comprobado antes de continuar. El [incidente anterior](informes/INCIDENTE_RECUPERACION_CP12.md) queda conservado. El último checkpoint científico cerrado sigue siendo CP11; la causa permanece abierta. No hay causa ni corrección CP12 certificada. No repetir E00/E01/C0 ni otras campañas cerradas.

El repositorio autoritativo es [Proyecto_Runas](https://github.com/diegolezaval/Proyecto_Runas). `main` está protegida: crear ramas desde el último `origin/main`, verificar y entrar sólo mediante PR. [Política vigente](https://github.com/diegolezaval/Proyecto_Runas/blob/migration/cp10/gobernanza/POLITICA_MAIN.md). El documento de migración describe la preparación histórica CP10; no es el estado actual de publicación.

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
| Antecedente de la auditoría arquitectónica | [Informe CP09](informes/AUDITORIA_ARQUITECTURA_CP09.md) |
| Resultado y alcance de CP10 | [Informe CP10](informes/ENTREGA_10_MEDIADOR_ESPACIOTEMPORAL.md) y [resumen generado](informes/RESUMEN_NUMERICO_CP10.md) |
| Diagnóstico y puerta de parada CP11 | [Informe CP11](informes/ENTREGA_11_DIAGNOSTICO_RADIAL_CHI.md), [resumen generado](informes/RESUMEN_NUMERICO_CP11.md) y [capítulo 31](tratado/31_diagnostico_radial_del_mediador.md) |
| Preparación local para GitHub | [MIGRACION_GITHUB.md](MIGRACION_GITHUB.md) |
| Protocolo y procedencia de la continuación | [Protocolo CP10](informes/PROTOCOLO_CP10_MEDIADOR.md) y [configuración](datos/ensayo_mediador_CP10.json) |

Ante discrepancias, prevalece la evidencia reproducible del corpus sobre el resumen de estado; éste prevalece sobre el plan original. Las definiciones, hipótesis, resultados numéricos, negativos, aproximaciones y problemas abiertos se distinguen en la evidencia y los capítulos. R1 contiene metas de diseño, no mediciones. La versión del proyecto no cambia la identidad del modelo físico.

## Reconstruir y comprobar

El checkpoint completo contiene todo el corpus, los estados y la hoja de ruta original. Extraerlo en una carpeta nueva. Los dos ZIP complementarios de CP08 también reconstruyen su entrada original si se extraen juntos; sus instrucciones se conservan como antecedente en [LEEME_ENTREGA_CP08.md](LEEME_ENTREGA_CP08.md). Las instantáneas y hashes permiten recuperar las fuentes de CP09 y CP08 sin un archivo externo no declarado.

Con Python, la integridad de bytes no requiere bibliotecas científicas:

```bash
python herramientas/checkpoint.py --verificar
python herramientas/verificar_continuidad.py --solo-lectura
```

Con el entorno de referencia instalado:

```bash
python herramientas/verificar_entorno.py --cp10
python herramientas/verificar_CP10.py
python herramientas/verificar_CP11.py
python herramientas/generar_resumen_CP11.py --comprobar
python herramientas/generar_continuidad.py --comprobar
python herramientas/auditar_arquitectura.py
python herramientas/regresion_estructural.py --salida ../regresion_estructural.json
```

La regresión usa una copia temporal y los datos guardados; conserva el corpus. El entorno probado es Linux/POSIX, Python 3.12.14 y requirements.txt. El adaptativo usa fcntl. El protocolo CP10 registra la fuerza C y requiere `cc` para reproducir esas ejecuciones; el solucionador histórico también ofrece NumPy. Los comandos de comprobación funcionan invocando el script por ruta desde otra carpeta.

Consultar el [mapa de generadores y protocolo de continuación](ARQUITECTURA.md) antes de modificar. No editar fichas, tablas ni integrado por separado. Los verificadores históricos pueden escribir salidas: ejecutarlos en una copia. reproducir.py conserva una reproducción científica histórica distinta de esta auditoría; no usarla como siguiente investigación automática.

Después de cambios justificados y comprobados, actualizar las vistas y crear una entrega:

```bash
python herramientas/generar_continuidad.py
python herramientas/regresion_estructural.py --salida ../regresion_estructural.json
python herramientas/checkpoint.py --salida ../Proyecto_Runas_checkpoint.zip
```

El manifiesto cubre historia y fallos, además de fuentes y estados válidos. Un intento fallido de colocación tiene un NPZ ilegible conservado por hash; el auditor lo identifica como no reanudable, sin confundirlo con el resultado posterior válido. Las limitaciones de procedencia de cálculos antiguos permanecen declaradas.

## Ejecuciones y recuperación

CP10 guarda cada ejecución nueva en `validacion/P06/no_radial/CP10/<caso>__<ID completo>/`. `procedencia.json` se escribe **antes** del cálculo, captura código/Θ/protocolo y registra estados, segmentos, reinicios y hashes de salidas. `configuration.json` distingue configuraciones exactas aunque el nombre histórico del NPZ redondee una malla.

Para reanudar un caso pendiente del protocolo CP10, comprobar primero el estado y sus fuentes y usar `ejecutar_con_procedencia.py --caso <caso> --reanudar`. No iniciar el solucionador directamente ni alterar el protocolo de una ejecución existente. Los casos completados se reutilizan; los intentos fallidos se conservan. Una ejecución cerrada y una etapa científica aceptada son decisiones distintas.

Para nuevos protocolos M2, usar `herramientas/ejecutar_protocolo.py` con una carpeta de campaña declarada en el JSON y el adaptador incluido en `extra_code`. Así se conserva CP10, se aplica la política de hilos y se comprueba la identidad antes de recuperar un estado. El [contrato y alcance del adaptador](ARQUITECTURA.md) deben revisarse antes de usar otro trabajador o modelo.

Los prerregistros CP11 están en [diagnóstico](datos/ensayo_diagnostico_chi_CP11.json), [respuesta forzada](datos/ensayo_respuesta_forzada_CP11.json) y [referencia extendida](datos/ensayo_respuesta_forzada_precisa_CP11.json). Los recibos se conservan en `validacion/P06/no_radial/CP11/`. Una FALLIDA aritmética permanece incluida y delimitada; las ejecuciones completadas se reutilizan.

La reproducción de los tres diagnósticos válidos se hace en temporales con recibo previo. Para verificar un clon y conservar limpio su payload, guardar el recibo de publicación fuera del repositorio:

```bash
python herramientas/verificar_CP11.py --protocolo datos/verificacion_diagnostico_CP11.json --caso verificacion_publicacion --recibo-externo ../comprobacion_clon_CP11
```

Este modo externo sólo permite la verificación sin evoluciones del protocolo CP11. No mueve evidencia científica ni cambia `main`. Registra hashes y entorno antes de reproducir; el recibo externo es un comprobante de publicación, no una dependencia del checkpoint.
