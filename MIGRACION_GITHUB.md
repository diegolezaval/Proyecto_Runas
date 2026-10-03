# Preparación para una migración posterior a GitHub

CP10 está preparado localmente. No se ha creado un repositorio Git en el corpus, conectado un remoto, instalado Git LFS ni publicado archivos. La organización científica de CP09 se conserva. La decisión científica y el trabajo pendiente se consultan en [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md); este documento sólo define la distribución futura.

## Política de archivos

| Clase | Distribución propuesta | Condición de integridad |
|---|---|---|
| Código Python/C, requirements, Markdown, JSON, SVG y configuraciones | Git directo | Mantener rutas, fuentes y generadores; verificar el manifiesto después del checkout. |
| CSV y pequeños datos reproducibles utilizados por conclusiones | Git directo en el estado actual | Conservar también negativos y procedencia; que un dato sea reproducible no vuelve prescindible su evidencia histórica. |
| NPZ actuales, campos/velocidades de origen y estados de reinicio | Git directo para este corpus | Ningún estado actual necesita LFS por un límite individual de tamaño. Un clon debe contener los bytes, no sólo referencias. |
| Estados futuros grandes o que cambien con frecuencia | Evaluar Git LFS antes de incorporarlos | Primero demostrar descarga de objetos y reconstrucción en un clon nuevo; mantener hashes, configuraciones y recibos. No convertir ahora ni reescribir historia. |
| Resultados JSON, CSV, SVG y registros científicos | Git directo | Distinguir evidencia numérica de vistas generadas mediante los metadatos existentes; no ignorarlos por ser generados. |
| Instantáneas, fallos y ZIP de fuente histórica ya incluidos | Git directo en el estado actual | Preservar su papel en recuperación e integridad. El NPZ fallido ilegible sigue siendo un antecedente ligado a su hash. |
| Nuevos checkpoints completos comprimidos | Releases o artefactos fuera del árbol del proyecto | Distribuir el corpus, manifiesto y comprobación externa del ZIP. No sumar una copia completa a cada commit. |
| Cachés compiladas, locks de ejecución, entornos, pycache y temporales | Ignorar mediante .gitignore | Regenerables o transitorios. Un temporal científico pendiente debe resolverse antes de empaquetar; ignorarlo no certifica un estado válido. |

El inventario medido se guarda en [trazabilidad/CP10_inventario_git.json](trazabilidad/CP10_inventario_git.json). Es una medición de la preparación, no una nueva autoridad de hashes. El manifiesto del checkpoint define los bytes definitivos. El archivo individual mayor medido es la fuente histórica `trazabilidad/fuente_M2_4_1.zip`, de 6 022 627 bytes. El estado CP10 de la malla .0625 ocupa 4 681 805 bytes. No procede retirar esos archivos ni adoptar LFS sólo por esta medición.

## Preparación ya comprobada

Se conservan `.gitignore` y `.gitattributes` de CP09. La regla `* -text` evita conversiones automáticas de fin de línea y permite conservar los SHA-256 incluso con `core.autocrlf=true`. No se añade un filtro LFS. [README.md](README.md) es un puente generado desde [LEEME.md](LEEME.md), la entrada canónica; no duplica manualmente conclusiones o progreso.

El ensayo [validacion/arquitectura/preparacion_git_CP10.json](validacion/arquitectura/preparacion_git_CP10.json) crea únicamente un repositorio temporal aislado, añade una copia del payload al índice y la extrae en otra carpeta. Compara todos los hashes, incluidos estados, negativos, logs y fuente histórica; comprueba que los transitorios quedan ignorados y que no hay remotos. No modifica ni inicializa Git en el proyecto. Puede repetirse con:

```bash
python herramientas/verificar_preparacion_git.py
```

La comprobación sin `--salida` no escribe informes en el corpus. Cualquier modificación posterior invalida una afirmación de igualdad basada en un recibo anterior y debe volver a comprobarse.

## Cuando se autorice la migración

1. Elegir visibilidad, licencia y destino. Esas decisiones no se infieren de esta preparación.
2. Verificar el checkpoint y sus recibos; crear una copia de trabajo conservando sus rutas.
3. Inicializar Git en esa copia y revisar qué se va a registrar. Incluir el corpus científico completo según la tabla; mantener el ZIP de entrega fuera del árbol.
4. Hacer un checkout limpio, comprobar hashes, entorno, fuentes de C y regresiones de datos guardados antes de publicar.
5. Si en el futuro se adopta LFS, comprobar también la descarga real de objetos desde el nuevo destino. Una referencia LFS por sí sola no contiene un estado numérico reproducible.
6. Publicar sólo después de esa comprobación y con la autorización de destino correspondiente. Mantener el checkpoint verificable como punto de recuperación.

## Referencias técnicas consultadas

- [GitHub: archivos grandes](https://docs.github.com/es/repositories/working-with-files/managing-large-files/about-large-files-on-github) y [límites de repositorios](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits).
- [Git: atributos y tratamiento de texto](https://git-scm.com/docs/gitattributes).
- [GitHub: Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).
- [GitHub: README](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) y [Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).

La política se basa en el papel reproducible y tamaño medido de los archivos de CP10; no en una exclusión global de binarios o de resultados generados.
