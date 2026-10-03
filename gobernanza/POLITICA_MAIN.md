# Política del proyecto: main estable y trabajo mediante Pull Request

Esta es la política operativa canónica del repositorio `diegolezaval/Proyecto_Runas`. El trabajo científico futuro debe realizarse en ramas separadas, verificarse y entrar a `main` mediante un Pull Request. La norma se aplica a personas, agentes, herramientas y automatizaciones, incluidas las que tengan permisos de administrador.

## Estado técnico comprobado el 3 de octubre de 2026

Se configuró una regla clásica para `main`: exige Pull Request, resolución de conversaciones y aplicación a administradores; no permite force push ni borrado. GitHub permite guardar la regla, pero la marca **Not enforced** en este repositorio privado con el plan actual. La API confirma `protected: false` aunque la configuración esté guardada. Los rulesets tampoco pueden aplicarse: la API devuelve 403 y la interfaz muestra el mismo límite del plan.

Por tanto, **main es la rama estable por política del proyecto; el servidor no proporciona ahora un bloqueo universal de escrituras directas**. Esta limitación debe mantenerse visible y no debe presentarse una regla guardada como una protección efectiva. La documentación oficial de GitHub reserva esas protecciones para repositorios privados con un plan compatible:

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets

La configuración preparada exige PR, pero no añade un requisito de aprobación por otra cuenta inexistente. La verificación científica documentada sigue siendo obligatoria antes de fusionar. Cuando exista un check automático pertinente y verificado, podrá incorporarse como requisito técnico con un plan que lo haga efectivo.

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

Los hooks son una protección del cliente, no un control de acceso del servidor. Un cliente sin instalarlos, `--no-verify` o una escritura por web/API puede eludirlos técnicamente; hacerlo incumple esta política. Nunca debe describirse esta alternativa como equivalente a una protección aplicada por GitHub.

## Conservación de CP10

Al establecer esta política, el tag anotado `CP10`, su commit `47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81`, el ZIP y las pruebas de la Release siguen siendo el checkpoint científico autoritativo y `main` mantiene sus 938 archivos originales. Las etapas y conclusiones futuras se consultan en las fuentes científicas vigentes, no en esta instantánea administrativa. Esta política y el instalador se guardan en `migration/cp10/gobernanza/`, la rama administrativa; esa rama no es una base científica para nuevas campañas.

El empaquetador de CP10 incluye todos los archivos del corpus salvo transitorios declarados. Añadir documentación de gobierno dentro de ese corpus rompería la comprobación exacta de su manifiesto. Por eso la entrada del repositorio enlaza esta política desde los metadatos de GitHub y las guardas se instalan en `.git`, preservando la reproducción de CP10. No se cambian generadores ni exclusiones para ocultar nuevos archivos.

La comparación exacta de CP10 sigue requiriendo el entorno de referencia documentado en la Release, con OpenBLAS SkylakeX/AVX-512 y un hilo. No se suavizan sus criterios para adaptar el resultado a un ejecutor genérico.

## Alternativas comprobadas

| Alternativa | Resultado y decisión |
|---|---|
| Protección clásica de main | Regla guardada; GitHub indica que no se aplica con el plan actual. |
| Rulesets de ramas o de pushes | Bloqueo confirmado por API e interfaz; no resuelven el límite del plan privado. |
| Bloqueo completo de rama | Pertenece a la misma protección y, además, impediría integrar los PR científicos requeridos. |
| Restricciones a colaboradores o CODEOWNERS | No eliminan la escritura del propietario; CODEOWNERS está deshabilitado por el plan. |
| Hooks locales | Se instalan y se prueban; previenen commits y pushes accidentales sobre main en clientes configurados. |
| Archivo del repositorio | Haría el proyecto de sólo lectura e impediría trabajar e integrar mediante PR. No cumple el objetivo. |
| Cambiar privacidad o adquirir un plan | No se cambia la privacidad ni se contraen gastos. Un plan compatible permitiría aplicar la regla preparada posteriormente. |

No se utiliza una automatización que sobrescriba main después de un push: corregir el puntero tras una escritura no equivale a impedirla y puede dañar historia o evidencia. La política, los hooks y la configuración de PR conservan el control del proyecto dentro de las capacidades actuales.
