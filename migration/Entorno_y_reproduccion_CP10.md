# Reproducción de CP10 después de la migración

CP10 se conserva byte a byte en `main` y en el tag anotado `CP10`. La evidencia científica permanece en los 938 archivos originales. Los recibos de migración, este documento y las herramientas de publicación son anexos operativos; no sustituyen `estado_progreso.json`, la teoría ni las puertas científicas. No se trasladó ni renombró ningún archivo del corpus.

## Resultado comprobado

Un ejecutor autenticado de GitHub creó un clon nuevo mediante `git clone` desde el repositorio privado, sin reutilizar el bundle de importación. Su recibo identifica commit, árbol, tag, archivo de transporte y sumas de ocho partes. Se verificaron las sumas de los ZIP de artefactos, las partes y el archivo ensamblado antes de extraerlo. Ese mismo clon, con su base de objetos Git y su origen original, pasó el verificador CP10 sin modificaciones en el entorno de referencia.

Pasaron las trece comprobaciones registradas, la compilación nueva de la fuerza C y su comparación con NumPy, la regeneración idéntica de JSON/CSV/SVG y la creación del ZIP exacto. El repositorio permaneció limpio y sus 938 archivos conservaron sus bytes. No se ejecutaron campañas científicas ni pasos nuevos de integración. `REFINAMIENTO_PENDIENTE` y el resultado negativo de la puerta finita permanecen vigentes. E03, E04, RES0 y RES1 siguen parciales.

## Dependencia numérica que debe conservarse

Las versiones Python 3.12.14, NumPy 2.3.5 y SciPy 1.17.0 son necesarias, pero dos aserciones de igualdad exacta también dependen de la selección de kernels numéricos. La referencia verificada usa OpenBLAS 0.3.30 con arquitectura SkylakeX, CPU con AVX-512 (AVX512F y AVX512_SKX) y un hilo. El perfil completo y el compilador constan en `Vinculo_clon_y_verificacion_CP10.json`.

El ejecutor estándar Ubuntu 24.04 de GitHub Actions utilizado seleccionó Haswell y carecía de AVX-512. Fallaron exactamente las dos reconstrucciones bit a bit de los campos iniciales desde CP04: diferencias de hasta 1.3877787807814457e-17 en las columnas cuadrupolares. Se conservaron el registro negativo y ambos diagnósticos. No se suavizó `np.array_equal`, no se cambiaron semillas, parámetros, tolerancias, estados guardados ni conclusiones.

La migración está verificada en el entorno de referencia. Este informe no afirma que un ejecutor genérico de GitHub reproduzca esas dos igualdades exactas. Un contenedor con las mismas versiones no basta si el hardware cambia. No fuerces SkylakeX ni características AVX-512 sobre un CPU que no las soporte. Cualquier ampliación de portabilidad debe ser una tarea explícita posterior, separada de CP10.

## Repetir la comprobación

1. Autentícate normalmente en GitHub con una cuenta que tenga acceso al repositorio privado.
2. Clona en una carpeta nueva: `git clone --branch main --single-branch https://github.com/diegolezaval/Proyecto_Runas.git Proyecto_Runas`.
3. Comprueba `git rev-parse HEAD` = `47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81`, `git rev-parse HEAD^{tree}` = `15e40bba81afaf7c6b4a5be14dcf4bad4e2134bd` y `git rev-parse CP10` = `b361fae70ba0c90a4d7a73e6f9049881bc702982`.
4. En el hardware de referencia, usa Python 3.12.14 e instala `requirements.txt`. Mantén `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1` y `MPLBACKEND=Agg`.
5. Descarga de la Release el ZIP original y `verificar_clon_CP10.py`; guárdalos fuera del clon. Verifica sus sumas en el manifiesto y en el acta.
6. Ejecuta `python verificar_clon_CP10.py --clon Proyecto_Runas --zip Proyecto_Runas_M2_4_2_CP10_MEDIADOR_ESPACIOTEMPORAL.zip --salida comprobacion_nueva.json --origen github`. El recibo debe escribirse fuera del corpus.

El verificador usa temporales para las vistas, la compilación y el reempaquetado; no requiere las cachés anteriores. El ZIP reproducido debe tener SHA-256 `c1b8b472f8d1f89c466fd5cb89470f63993ec73dedc9dac3896a88ffc2add4c1`.

## Conservación y organización en GitHub

Los 938 archivos entran directamente en Git, incluidos NPZ, registros científicos, negativos, fuentes de ruta, historia y procedencia. Se mantienen `.gitignore` y `.gitattributes` originales; ningún archivo de evidencia fue excluido. No se implantó Git LFS ni se añadió una licencia. La rama `migration/cp10` conserva el arranque y las herramientas operativas. El borrador privado `cp10-transferencia` conserva los originales de transporte. Los artefactos de Actions son temporales y no constituyen la única copia de evidencia: la Release CP10 incluye los recibos, diagnósticos, fallo inicial y prueba final.

El mapa de migración de rutas del corpus está vacío. `main` no contiene herramientas adicionales ni cambios científicos. CP11 no ha comenzado.
