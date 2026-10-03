# Política del proyecto: main estable y trabajo mediante Pull Request

Esta es la política operativa canónica del repositorio `diegolezaval/Proyecto_Runas`. El trabajo científico futuro debe realizarse en ramas separadas, verificarse y entrar a `main` mediante un Pull Request. La norma se aplica a personas, agentes, herramientas y automatizaciones, incluidas las que tengan permisos de administrador.

## Estado técnico comprobado el 3 de octubre de 2026

El repositorio es **público**, tras la autorización y la confirmación expresa del usuario. La regla clásica de `main` está **aplicada por GitHub**: exige Pull Request y resolución de conversaciones, se aplica también a administradores sin bypass y no permite force push ni borrado. La API confirma `protected: true`; la interfaz confirma que la regla se aplica a la rama `main` y conserva esas opciones. No se realizaron escrituras experimentales en main para probar el bloqueo.

**main es la rama estable protegida; todo trabajo científico se realiza en una rama y se integra por PR después de verificarse.** La protección no autoriza cambios científicos ni convierte una puerta pendiente en superada. Los administradores conservan la capacidad de modificar la configuración del repositorio; hacerlo para eludir esta política no está autorizado. La documentación oficial de GitHub describe la disponibilidad de estas protecciones:

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets

La configuración exige PR, pero no añade un requisito de aprobación por otra cuenta inexistente. La verificación científica documentada sigue siendo obligatoria antes de fusionar. No hay un status check científico obligatorio configurado en el servidor: el recibo del contenido final verificado debe adjuntarse al PR y revisarse antes de integrarlo. Un check automático sólo se incorporará cuando compruebe realmente el corpus en un entorno compatible; no se sustituye la verificación por un indicador de éxito ficticio.

Antes de la publicación, la misma regla estaba guardada pero figuraba **Not enforced** y la API devolvía `protected: false`; los rulesets daban 403 por el plan privado. Ese antecedente se conserva en el historial administrativo y los recibos anteriores. Ya no describe el estado vigente.

## Flujo obligatorio

1. Leer esta política, `ESTADO_ACTUAL.md`, `estado_progreso.json`, las enmiendas, los últimos informes y recibos. Resolver el checkpoint y la fuente científica vigentes antes de cambiar archivos.
2. Usar `main` para consultar, clonar y verificar estados estables. Crear una rama `ciencia/<objetivo>` desde el último `origin/main` antes de editar o ejecutar trabajo científico. Los cambios operativos usan una rama separada igualmente.
3. Mantener la trazabilidad de teoría, parámetros, estados, resultados negativos, historia, incertidumbres, procedencia y puertas de decisión. Registrar el código, configuración, entradas, entorno, hashes, resultados y conclusión de cada ejecución con el sistema de procedencia existente.
4. Ejecutar las comprobaciones pertinentes de la rama y conservar su recibo fuera del corpus o en el lugar científico ya previsto. Verificar la integridad, las regresiones, la regeneración de vistas y la reanudación aplicables. Un resultado negativo puede ser evidencia válida; no se exige falsificar una puerta física como superada para integrar un checkpoint parcial correctamente verificado.
5. Abrir un PR hacia `main`. Identificar el commit exacto verificado, el estado de partida, los cambios, los recibos y sus sumas, la configuración y el entorno, las comprobaciones ejecutadas, los resultados negativos y los puntos pendientes.
6. Revisar el diff y resolver las conversaciones. Si cambian la rama o la base de forma que afecten a la prueba, repetir las comprobaciones necesarias. El recibo utilizado para integrar debe corresponder al contenido final que se fusionará.
7. Fusionar mediante el PR de GitHub conservando los commits de la rama. Usar un merge commit para mantener alcanzables los identificadores que utiliza la procedencia. Después, comprobar el árbol integrado, el estado científico y el checkpoint de entrega. No usar commits, pushes, force pushes, borrados ni escrituras de archivos por API directamente en `main`.

La creación de una rama no autoriza una campaña nueva por sí sola. En esta intervención CP10 permanece vigente y **CP11 no se inicia**; las campañas posteriores requieren un objetivo científico pedido por el usuario.

## Guardas técnicas locales

[`instalar_guardas_main.py`](instalar_guardas_main.py) instala dos hooks dentro de los metadatos de Git, sin añadir archivos al corpus científico:

- `pre-commit` bloquea commits sobre `main` y sobre HEAD separado; obliga a crear una rama de trabajo.
- `pre-push` bloquea cualquier actualización, force push o borrado de `refs/heads/main`, incluso si se intenta enviar desde otra rama. También conserva el tag autoritativo `CP10`.

La instalación respeta hooks y configuraciones personalizados: se detiene ante un conflicto para que se integren explícitamente. No modifica archivos registrados, manifiestos, parámetros ni resultados. Es idempotente para sus propios hooks.

Cada clon nuevo debe instalar estas guardas. Git no distribuye automáticamente los hooks al clonar. Desde un clon de este repositorio, puede obtenerse el instalador versionado de la rama administrativa y guardarse fuera del corpus:

```sh
git fetch origin migration/cp10
git show origin/migration/cp10:gobernanza/instalar_guardas_main.py > ../instalar_guardas_main.py
python ../instalar_guardas_main.py --repositorio .
```

Los hooks complementan la protección efectiva de GitHub. Actúan sólo en el cliente: un cliente sin instalarlos o con `--no-verify` puede omitirlos, pero sigue sujeto a la regla de main del servidor. El recibo del instalador describe únicamente el alcance local de los hooks; no comprueba ni informa el estado global de la protección de GitHub. Nunca debe confundirse ese alcance con el estado técnico de main descrito arriba. Git no distribuye los hooks automáticamente: deben instalarse en cada clon nuevo.

## Conservación de CP10

Al establecer esta política, el tag anotado `CP10`, su commit `47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81`, el ZIP y las pruebas de la Release siguen siendo el checkpoint científico autoritativo y `main` mantiene sus 938 archivos originales. Las etapas y conclusiones futuras se consultan en las fuentes científicas vigentes, no en esta instantánea administrativa. Esta política y el instalador se guardan en `migration/cp10/gobernanza/`, la rama administrativa; esa rama no es una base científica para nuevas campañas.

El empaquetador de CP10 incluye todos los archivos del corpus salvo transitorios declarados. Añadir documentación de gobierno dentro de ese corpus rompería la comprobación exacta de su manifiesto. Por eso la entrada del repositorio enlaza esta política desde los metadatos de GitHub y las guardas se instalan en `.git`, preservando la reproducción de CP10. No se cambian generadores ni exclusiones para ocultar nuevos archivos.

La comparación exacta de CP10 sigue requiriendo el entorno de referencia documentado en la Release, con OpenBLAS SkylakeX/AVX-512 y un hilo. No se suavizan sus criterios para adaptar el resultado a un ejecutor genérico.

El tag anotado `CP10` está además protegido por el ruleset activo `CP10: conservar checkpoint` (24433943), limitado exactamente a `refs/tags/CP10`: restringe actualizaciones y borrado y bloquea force pushes, sin actores con bypass. No se mueve el tag ni se altera la Release. Los hashes originales y sus recibos siguen permitiendo comprobar cualquier descarga del checkpoint.

El 3 de octubre de 2026 se verificó un clon nuevo obtenido de la URL pública de GitHub sin credenciales: las 13 comprobaciones de CP10 aprobaron, los 938 archivos conservaron sus bytes, se regeneraron de forma idéntica JSON/CSV/SVG y el ZIP reproducido coincidió exactamente con el original. La comparación de fuerza C compilada en frío dio errores relativos cero sin pasos de integración. Se conservan el recibo de ese clon, el entorno y la comprobación administrativa fuera del corpus científico.

Se mantiene la distribución de `MIGRACION_GITHUB.md`: código, documentación, configuraciones, datos, resultados y todos los estados actuales en Git directo; checkpoints completos en Releases; cachés y temporales según las exclusiones existentes. No se introduce LFS ni se excluye evidencia necesaria. Un traslado futuro de estados grandes exige justificarlo y demostrar antes que un clon nuevo recupera todos los objetos y reproduce el checkpoint.

## Antecedentes y alternativas comprobadas

| Alternativa | Resultado y decisión |
|---|---|
| Protección clásica de main | No se aplicaba en privado. Tras la publicación confirmada, está aplicada: `protected: true`. Se conserva la regla existente. |
| Rulesets de ramas o de pushes | En privado estaban bloqueados por el plan. Ya no hace falta reemplazar ni duplicar la regla efectiva de main. |
| Bloqueo completo de rama | Pertenece a la misma protección y, además, impediría integrar los PR científicos requeridos. |
| Restricciones a colaboradores o CODEOWNERS | No resolvían el límite privado ni eliminaban la escritura del propietario. No se añade dependencia de una segunda cuenta inexistente. |
| Hooks locales | Se instalan y se prueban; previenen commits y pushes accidentales sobre main en clientes configurados. |
| Archivo del repositorio | Haría el proyecto de sólo lectura e impediría trabajar e integrar mediante PR. No cumple el objetivo. |
| Cambiar privacidad o adquirir un plan | Se publicó el repositorio con confirmación expresa y la protección funciona. No se contrató un plan ni se incurrió en gastos. |

No se utiliza una automatización que sobrescriba main después de un push: corregir el puntero tras una escritura no equivale a impedirla y puede dañar historia o evidencia. La regla efectiva, la política, los hooks y la configuración de PR conservan el control del proyecto. No se reorganiza el corpus ni se inicia CP11.
