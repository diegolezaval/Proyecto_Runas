# Guía del proyecto Rúnica

**Este es el mapa para orientarte sin recorrer todo el repositorio.** Rúnica desarrolla una física para un sistema ficticio de runas y estudia qué funciones podrían derivarse de ella. La teoría, las simulaciones y los objetivos de dispositivos tienen distintos grados de evidencia.

Esta guía reúne enlaces y explica su papel. La evidencia reproducible y los registros científicos mantienen su autoridad. Referencias de investigación y respaldo comprobadas el 28 de octubre de 2026.

## Dónde estás

| Línea | Qué representa | Dónde leer |
| --- | --- | --- |
| Base aceptada: CP11 | Último checkpoint científico aceptado. `main` conserva esta base. | [Resumen CP11](informes/RESUMEN_NUMERICO_CP11.md), [informe CP11](informes/ENTREGA_11_DIAGNOSTICO_RADIAL_CHI.md) y [Release CP11](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/CP11). |
| Investigación posterior: CP12/P3 | Trabajo experimental abierto. Última frontera completa aprobada del ensayo: τ8; transporte íntegro preservado: τ9,6. P3 sigue sin validar. | [Rama P3](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-residuo-p3-20261018), [recuperación vigente](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/RECUPERACION_CP12_ACTUAL.md) y [prerregistro posterior de conservación](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/conservacion_git_20261020b/PRERREGISTRO.md). |
| Respaldos descargables | Tres cápsulas originales: P3 τ9,6, CP12 original τ160 y diagnóstico P2 τ80. Descarga y extracción verificadas. | [Release de respaldo](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027) y [guía para recuperarlas](https://github.com/diegolezaval/Proyecto_Runas/blob/respaldo/cp12-p3-20261027/respaldos/CP12_20261027/LEEME.md). |
| Antecedentes | Resultados previos, intentos y negativos que explican las decisiones. Cada documento conserva su fecha y alcance. | [Informes de esta base](informes/) y [trazabilidad](trazabilidad/). Las ramas experimentales contienen sus expedientes posteriores. |

El transporte local P3 τ11,2 se perdió tras el incidente de conservación. Su hash o un registro antiguo no equivalen a una cápsula recuperable. La transferencia histórica quedó en **116 de 308 partes**, índices 0–115. Los tres ZIP publicados completos tienen una verificación independiente; la transferencia parcial conserva su estado incompleto.

La recuperación de P3 debe leerse junto a sus prerregistros posteriores: el texto inicial de recuperación precede a la excepción condicional de repetición τ9,6→τ11,2. La nueva conservación no consumió esa excepción. No volver a iniciar τ0 ni reanudar P2, cuyo negativo τ80 permanece conservado.

## Encontrar algo por su propósito

| Buscas… | Punto de entrada |
| --- | --- |
| Qué afirma el proyecto y qué está pendiente | [Estado de evidencia](datos/estado_evidencia.json) y [progreso de esta base](estado_progreso.json). |
| Qué falta en la investigación posterior | [Registro de reanudación P3](https://github.com/diegolezaval/Proyecto_Runas/blob/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json), informes y prerregistros de esa rama. |
| Ecuaciones y convenciones | [Capítulo 13: M2 común](tratado/13_M2_comun_y_teoremas.md), [capítulo 23: convenciones](tratado/23_convenciones_y_espacio_fundamental.md). |
| Parámetros comunes del modelo | [Θ común](datos/theta_comun.json). |
| Plan a largo plazo | [Guía original](hoja_ruta_original/Guia_tecnica.md), [directrices de desarrollo](DIRECTRICES_DESARROLLO.md) y enmiendas de la rama correspondiente. |
| Pruebas, decisiones y fallos | [Registro de cálculos](datos/registro_calculos.json), después el informe y los datos enlazados de esa campaña. |
| Archivos para descargar y conservar | [Catálogo de respaldos CP12](https://github.com/diegolezaval/Proyecto_Runas/blob/respaldo/cp12-p3-20261027/respaldos/README.md) y [Releases](https://github.com/diegolezaval/Proyecto_Runas/releases). |
| Entorno, herramientas y comprobaciones | [Arquitectura](ARQUITECTURA.md) y [comandos de la entrada técnica](LEEME.md). |

## Mapa de carpetas

| Lugar | Qué contiene | Cómo usarlo |
| --- | --- | --- |
| [tratado/](tratado/) | Capítulos de teoría, convenciones y resultados delimitados. | Empieza por los capítulos 13 y 23; usa los capítulos específicos cuando el informe los cite. |
| [datos/](datos/) | Parámetros, protocolos, configuraciones y registros de decisiones. | Busca el protocolo de una campaña y su resultado autoritativo. |
| [informes/](informes/) | Explicaciones de cada entrega: pregunta, resultado, fallo, límites y siguiente condición. | Lee el informe antes de inspeccionar cientos de archivos numéricos. |
| [herramientas/](herramientas/) | Generadores, verificadores, lanzadores y solucionadores. | Consulta primero su alcance; algunos comandos ejecutan cálculos o escriben resultados. |
| [validacion/](validacion/) | Estados numéricos, mediciones del modelo, diagnósticos, recibos, logs y fallos. | Entra desde el informe o registro que identifica la ejecución exacta. |
| [trazabilidad/](trazabilidad/) | Instantáneas, fuentes históricas, hashes y auditorías. | Sirve para comprobar origen y evolución; las copias históricas conservan su contexto. |
| [hoja_ruta_original/](hoja_ruta_original/) | Plan maestro original. | Léelo junto al progreso y las enmiendas de la rama que estés consultando. |
| [fichas/](fichas/) y [graficos/](graficos/) | Fichas, esquemas y vistas generadas. | Son una vía visual; para editarlas usa sus fuentes y generadores. |
| [investigacion/](investigacion/) | Notas exploratorias. | Revisa qué fue contrastado y qué sigue siendo una propuesta. |
| `checkpoints/` en la rama P3 | Prerregistros y expedientes de recuperación de CP12. | [Abrir el expediente P3](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-residuo-p3-20261018/checkpoints/CP12/p3_20261018). |
| `respaldos/` en la rama de conservación | Catálogo, instrucciones, hashes y comprobantes de los adjuntos grandes. | [Abrir el catálogo](https://github.com/diegolezaval/Proyecto_Runas/blob/respaldo/cp12-p3-20261027/respaldos/README.md). |

Las rutas largas de ejecución y sus identificadores permiten distinguir estados que tienen nombres visibles parecidos. Los informes y catálogos proporcionan los nombres de lectura humana. Las referencias técnicas siguen apuntando a los archivos originales.

## Cómo leer el avance sin confundir versiones

1. Mira qué rama tienes seleccionada en GitHub. `main` contiene la base aceptada; P3 conserva investigación posterior todavía abierta.
2. Abre el estado y el último informe específico de esa línea. Una indicación antigua de actividad o de archivos locales describe el momento en que se escribió.
3. Sigue los enlaces a protocolo, configuración, recibos y resultados. Una carpeta existente o un archivo con `passed` sólo acredita la comprobación que declara.
4. Usa el plan original para las dependencias y el objetivo. Usa la evidencia actual para decidir qué se completó realmente.
5. Para continuar en otro chat, facilita este repositorio, la rama exacta y la guía de recuperación. Recupera y comprueba los archivos antes de ejecutar.

El orden de autoridad es: **evidencia reproducible → estado, progreso e informes → enmiendas → plan original → conversación**. Esta guía facilita encontrar esas fuentes.

## Qué significan los nombres

| Término | Significado |
| --- | --- |
| CP10, CP11, CP12 | Identificadores de entregas o checkpoints. Que exista un CP no implica que todas sus etapas estén cerradas. |
| P2 y P3 en los expedientes CP12 | Ensayos de corrección numérica. Son distintos de las funciones primordiales P-04 y P-06. |
| τ | Tiempo del ensayo; un transporte interno entre fronteras no es una frontera completa aprobada. |
| M2 | Modelo fundamental actual. Un cambio documental o de esquema numérico no lo convierte en M3. |
| NPZ | Archivo de matrices y metadatos numéricos; su configuración y su identidad forman parte de la recuperación. |
| JSON | Datos estructurados: parámetros, contratos, resultados o comprobantes, según el archivo. |
| Release | Publicación de GitHub con adjuntos descargables. La de respaldo CP12 está marcada como experimental. |
| PR | Propuesta de cambios entre ramas. Una propuesta abierta todavía no está integrada en su rama de destino. |

## Organización para las próximas entregas

Usa un catálogo legible por campaña y conserva junto a él un índice técnico, los hashes y una guía de recuperación. Los ZIP grandes van a Releases con sus nombres originales y una descarga de comprobación. Un respaldo sólo pasa a completo después de verificarlo desde GitHub.

Conserva los resultados negativos y las cápsulas que respaldan decisiones. Una depuración grande de carpetas requiere mapa origen→destino, actualización de referencias y pruebas de recuperación. La mejora actual añade navegación sobre las rutas existentes.

[Volver a la portada](README.md) · [Entrada técnica completa](LEEME.md) · [Autoridad y arquitectura](ARQUITECTURA.md).
