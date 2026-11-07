# Comparación de controles sin rehacer código

`herramientas/comparar_control_publico_p3.py` compara un control contra la frontera pública ya recuperada y el registro/código de un commit público concreto. Recibe `--control`, `--publico`, `--repositorio`, `--salida`, `--sha-control`, `--sha-publico`, `--commit-publico`, `--registro-publico`, `--ejecutor-publico` y `--publico-asset-id`.

Clasifica todos los bytes: cargas idénticas a la frontera, fuentes administrativas idénticas a Git, inventario y relleno determinista del preservador original. Rechaza archivos desconocidos aunque tengan un hash declarado válido, o un registro distinto del que contiene el control. No importa kernels ni avanza M2; no concede permisos de publicación ni convierte el control en frontera científica.

Las referencias deben haberse recuperado de sus destinos públicos antes de compararlas. El informe conserva identidades, commit y conteos; el script no presume publicidad por el nombre del archivo. Las tres comprobaciones acotadas están en `COMPARADOR_REUTILIZABLE_VERIFICACION.json`: caso público real positivo, versión de registro incorrecta rechazada y carga sintética no declarada rechazada. Las copias sintéticas se retiraron.

La comparación original del control24→32 permanece íntegra en su expediente. Si sus entradas y condiciones no cambian, reutilizar su recibo. No repetir campañas, auditorías cerradas ni benchmarks para comprobar este código administrativo. Esta utilidad no modifica el ejecutor activo.
