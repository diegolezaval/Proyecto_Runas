CP10 autoritativo: `main` y el tag anotado `CP10` conservan el commit original `47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81`. Repositorio privado.

Los 938 archivos del ZIP original permanecen idénticos, incluidos estados, negativos, resultados, historia y procedencia. Sin reorganización, Git LFS, cambios de ciencia ni continuación de CP11.

El clon nuevo obtenido realmente de GitHub pasó las comprobaciones originales en el entorno de referencia: regresiones, procedencia, fuerza C compilada de nuevo, regeneración exacta de JSON/CSV/SVG y reproducción byte a byte del ZIP. Los recibos distinguen la creación del clon en GitHub de su comprobación en el hardware de referencia.

**Entorno:** Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, OpenBLAS 0.3.30 SkylakeX, AVX-512 y un hilo. El ejecutor genérico de GitHub con Haswell no pasó dos aserciones de igualdad exacta; se conserva ese fallo y no se relajaron criterios. Consulta `Entorno_y_reproduccion_CP10.md`.

La conclusión científica continúa siendo `REFINAMIENTO_PENDIENTE`, con la puerta finita no superada. No se ejecutaron campañas nuevas.

ZIP original: 81 773 782 bytes; SHA-256 `c1b8b472f8d1f89c466fd5cb89470f63993ec73dedc9dac3896a88ffc2add4c1`. La publicación se condiciona a comprobar también una descarga del ZIP de la Release. El acta final registra el resultado de esa descarga.
