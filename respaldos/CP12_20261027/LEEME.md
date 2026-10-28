# Recuperar los respaldos de CP12

**Empieza por aquí si necesitas descargar o recuperar los archivos científicos.** Los tres ZIP originales están en la [Release de respaldo CP12/P3](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027), en el apartado **Assets**. Su publicación ocurrió el 27 de octubre de 2026 en Lima; la comprobación independiente terminó el 28 de octubre.

Los tres ZIP se descargaron públicamente desde GitHub y se verificaron antes de extraerlos en una carpeta nueva: **547.279.290 bytes y 1.021 archivos declarados en los manifiestos**, todos correctos. El número cuenta entradas entre cápsulas, no archivos científicos únicos. Consulta el [comprobante completo](verificacion_descarga.json).

## Qué descargar

| Lo que necesitas | Descarga | Contenido y estado |
| --- | --- | --- |
| Recuperar el trabajo más reciente de P3 | [P3: transporte τ9,6](https://github.com/diegolezaval/Proyecto_Runas/releases/download/respaldo-cp12-p3-20261027/CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_TRANSPORTE_TAU_000096.zip) | 229.821.160 bytes; 283 archivos del manifiesto. Incluye el transporte τ9,6 y el estado cerrado τ8. |
| Consultar la evolución original CP12 | [CP12 original: τ160](https://github.com/diegolezaval/Proyecto_Runas/releases/download/respaldo-cp12-p3-20261027/CP12_RI_2b11da8c1f004704aa3e74d271c24846_tau0160.zip) | 84.575.117 bytes; 254 archivos. Conserva el antecedente original; CP12 sigue abierto. |
| Consultar el ensayo P2 y su diagnóstico | [P2: diagnóstico discriminante τ80](https://github.com/diegolezaval/Proyecto_Runas/releases/download/respaldo-cp12-p3-20261027/CP12_CANDIDATO_MIXTO_2cf74f0d65ad47048781e0502aec6a50_DIAGNOSTICO_DISCRIMINANTE_TAU0080_20261018.zip) | 232.883.013 bytes; 484 archivos. P2 permanece suspendido por su fallo espacial. |
| Comprobar los ZIP con otra herramienta | [SHA256SUMS](SHA256SUMS) | Los tres nombres originales y sus hashes SHA-256. También está adjunto a la Release. |

Conserva los nombres originales al descargarlos. Los enlaces automáticos **Source code (zip)** y **Source code (tar.gz)** de GitHub contienen la instantánea del repositorio; para estos respaldos debes descargar los tres adjuntos identificados en la tabla.

Para guardar una copia de seguridad completa de esta entrega, descarga los tres ZIP y `SHA256SUMS`, y conserva también esta carpeta de instrucciones. El código y los documentos pequeños están en Git; los ZIP grandes están en Releases.

## Comprobar los archivos descargados

Necesitas Python 3.11 o posterior, sin instalar bibliotecas científicas. Coloca los tres ZIP en una carpeta, por ejemplo `../capsulas`. Desde la raíz del repositorio ejecuta:

```bash
python respaldos/CP12_20261027/verificar_respaldo.py --archivos ../capsulas --salida ../verificacion_cp12.json
```

El resultado debe mostrar `"passed": true`. El programa comprueba tamaños, SHA-256 global, CRC de cada entrada, cobertura exacta de los manifiestos, hashes de todos sus archivos y las identidades de los estados clave. Rechaza rutas inseguras, enlaces simbólicos y entradas duplicadas. Conserva cada comprobante con un nombre nuevo.

Si tu herramienta dispone de `sha256sum`, puedes comprobar sólo los hashes globales desde la carpeta de descargas:

```bash
sha256sum -c SHA256SUMS
```

Esa comprobación rápida complementa al verificador completo, que además revisa el contenido de los ZIP.

## Extraer sin iniciar una simulación

Para verificar y luego extraer todos los archivos en una carpeta nueva:

```bash
python respaldos/CP12_20261027/verificar_respaldo.py --archivos ../capsulas --salida ../verificacion_y_extraccion_cp12.json --extraer ../recuperacion_cp12
```

La extracción sólo comienza si los tres ZIP pasan la verificación. La carpeta de destino debe ser nueva. El programa copia archivos; no importa operadores, no ejecuta scripts de las cápsulas y no avanza M2.

| Carpeta creada | Dónde empezar a inspeccionar |
| --- | --- |
| `recuperacion_cp12/P3_tau9p6/` | `configuration.json`, `transport/current.npz`, `outputs/MIXTO_par_estado.npz`, `preregistration/` y fuentes capturadas. |
| `recuperacion_cp12/CP12_original_tau160/` | Carpeta interior `2b11da8c1f004704aa3e74d271c24846/`; contiene `science/`, `proofs/` y su manifiesto. |
| `recuperacion_cp12/P2_diagnostico_tau80/` | `outputs/` y `analysis/DIAGNOSTICO_DISCRIMINANTE_TAU0080_20261018/`. |

## Estado científico al conservar estos archivos

**CP11 sigue siendo el último checkpoint científico aceptado. CP12 permanece abierto y P3 no está validada.** La referencia de esta entrega es el commit `be4bf493517e3f6f51989fa8fc8d6c6ea8cb8cb2` de `ciencia/cp12-residuo-p3-20261018`.

| Elemento | Situación |
| --- | --- |
| P3: última frontera completa aprobada del ensayo | τ8; el estado numérico está incluido en el ZIP τ9,6. |
| P3: último transporte permanente íntegro identificado | τ9,6. Un transporte interno conserva la memoria del integrador y no equivale a aprobar una frontera científica nueva. |
| P3: transporte local τ11,2 | Se perdió tras el incidente de conservación. Los registros y hashes históricos no reconstruyen la cápsula. |
| P2: τ80 | Negativo espacial conservado; el ensayo sigue suspendido. |
| Evoluciones realizadas para este respaldo | Cero pasos M2. |

Las auditorías científicas históricas se consultan en el [registro de reanudación P3](../../checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json) y en el [informe de recuperación τ8/τ9,6](../../informes/RECUPERACION_P3_TAU8_TAU9p6_20261019.md). El comprobante de esta carpeta acredita integridad de archivos y extracción; **no vuelve a certificar la rehidratación del integrador ni las puertas científicas**.

El estado P3 de transporte tiene SHA-256 `1bf0a52cf3cfd357e07d54fc519591558181508fdbb718242d369411a082e4e2`; el estado cerrado τ8 tiene `1984303f49cac1c424952af632b6b5fa552c2a119d233a613c869cf0055b2db0`. Sus rutas y las demás identidades requeridas están en el [índice técnico](indice.json).

## Antes de reanudar P3

La recuperación de archivos es el primer paso. Antes de consumir la excepción de repetición τ9,6→τ11,2, deben cumplirse las condiciones del [prerregistro de conservación del 20 de octubre](../../checkpoints/CP12/p3_20261018/conservacion_git_20261020b/PRERREGISTRO.md) y de su [estado de conservación del 22 de octubre](../../checkpoints/CP12/p3_20261018/conservacion_git_20261022/ESTADO_VERIFICADO.md). Esa excepción no se ha usado en este trabajo.

1. Recuperar fuentes, entradas y memoria DOP853 exactas desde la cápsula P3; comprobar su identidad sin avanzar la física.
2. Preparar y comprobar el entorno científico original y sus dependencias. La cápsula registra Python 3.12.14, Linux x86_64, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, threadpoolctl 3.6.0, compilador C y un hilo BLAS. Consulta `preregistration/identidad_cientifica_original.json` dentro de P3.
3. Registrar y probar una ruta ejecutable de conservación para las próximas salidas. El código histórico de guardado aún contiene referencias al almacenamiento anterior y requiere adaptación administrativa y comprobación antes de usarlo.
4. Auditar la restauración exacta sin pasos. Sólo después corresponde evaluar la continuación bajo el protocolo vigente, sus cinco métricas espaciales, ambas energías, carga y demás puertas originales.

No se habilita una ejecución nueva automáticamente por haber publicado esta Release. No volver a τ0 ni reanudar P2 para eludir su fallo.

## Qué queda de la transferencia antigua

El paquete histórico `CP12_P3_CAPACIDAD_20261020B.zip` tenía 308 subpartes y en el árbol de referencia hay 116, índices 0 a 115; el siguiente índice sería 116. Sigue **INCOMPLETO**. Su [estado histórico](../../checkpoints/CP12/p3_20261018/conservacion_git_20261022/capacidad/ESTADO.json), sus intentos y sus partes se conservan.

La Release proporciona una ruta independiente al ZIP P3 original que contenía ese paquete. No completa el paquete de capacidad, su relleno ni sus pruebas de capacidad. Tampoco acredita espacio para todo el horizonte de simulación.

El diagnóstico P2 conserva los datos de D1/D2 y archivos del negativo previo incluidos en su manifiesto. Esto no supone recuperar byte por byte todos los ZIP históricos, ni constituye una migración completa de todos los archivos de la cuenta anterior.

## Archivos de esta entrega

| Archivo | Para qué sirve |
| --- | --- |
| [Esta guía](LEEME.md) | Descarga, comprobación, extracción y límites. |
| [indice.json](indice.json) | Inventario exacto, tamaños, hashes, rutas y enlaces a los adjuntos. |
| [SHA256SUMS](SHA256SUMS) | Comprobación rápida con herramientas estándar. |
| [verificar_respaldo.py](verificar_respaldo.py) | Verificador independiente que usa sólo la biblioteca estándar de Python. |
| [verificacion_descarga.json](verificacion_descarga.json) | Resultado real de descarga y extracción desde GitHub. |
| [controles_verificador.json](controles_verificador.json) | Controles sintéticos de rechazo de archivos dañados o inseguros. |

[Volver al catálogo de respaldos](../README.md).
