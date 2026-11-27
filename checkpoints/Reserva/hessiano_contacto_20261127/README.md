# Hessiano rotante radial de la Reserva a carga fija

**Decisión.** La forma cuadrática reducida supera la puerta espectral en las cuatro realizaciones registradas. En el equilibrio FV corregido controla las perturbaciones radiales homogéneas de carga tangente cero, módulo la fase común. La referencia publicada usa un interpolante con defecto de fase medible. Queda por controlar el error forzado de esa trayectoria en el volumen. El piloto sigue sin habilitarse.

[Protocolo previo](PROTOCOLO.md) en 57842cc80961e276b50baf1327ca56c295462ed0. La geometría y el fondo proceden de la [referencia radial corta](../referencia_radial_contacto_20261127/README.md). Se conservan R256, ω=0,900, los volúmenes esféricos, el flujo nulo en el origen y la pared exterior del paso 2. Newton se aplicó únicamente al fondo de control en memoria.

| dr | Fondo | Amplitud libre | Amplitud a Q fija | Fase mínima | Primera fase tras simetría | Defecto relativo de fase |
|---|---|---:|---:|---:|---:|---:|
| 0,050 | interpolado | −0,02281992 | 0,19016252 | −1,5764e−6 | 0,18501449 | 1,4377e−5 |
| 0,050 | Newton FV | −0,02280443 | 0,19016252 | 4,09e−14 | 0,18501723 | 1,31e−13 |
| 0,025 | interpolado | −0,02280880 | 0,19016252 | −3,9409e−7 | 0,18501748 | 3,5950e−6 |
| 0,025 | Newton FV | −0,02280492 | 0,19016252 | −9,97e−14 | 0,18501816 | 4,67e−13 |

## Construcción y controles

La transformación por raíz del volumen diagonal W hace simétrico el laplaciano FV. Se escalan por √2 las dos componentes de Φ para usar la misma métrica cinética que en χ. Llamemos A al bloque real de amplitud de la segunda variación de E−ωQ y P al bloque de fase. En amplitud se ordenan primero la parte real de Φ y luego χ. Sea u la dirección unitaria de √W f y v=(u,0). En estas coordenadas el incremento de carga, normalizado por una constante, es q=uᵀpᵦ+2ωvᵀx, con x la amplitud y pᵦ la velocidad de fase rotante. A q=0, el término cinético longitudinal (uᵀpᵦ)² introduce exactamente 4ω² vvᵀ en A. Para las dos donantes se debe seguir cada q real, incluida cualquier fuente del error, antes de aplicar la reducción.

Se resuelven A y A+4ω²vvᵀ por inversión desplazada, con actualización de rango uno en el segundo caso. La fase usa un solucionador tridiagonal por índices. Un segundo recuento de signos por eliminación de bloques radiales 2×2 y complemento escalar del sistema ampliado confirma el índice cero de los dos mínimos calculados: a cada lado de λ±1e−7 cuenta cero y un modo bajo el corte, respectivamente. En las cuatro configuraciones hay una sola dirección de amplitud negativa libre y ninguna a carga fija por debajo de +0,17. El mayor residuo propio absoluto en norma canónica es 2,63e−12. Son comprobaciones en doble precisión.

El defecto publicado es ‖Pu‖. En el interpolante fino la alineación absoluta de u con el modo más bajo es 0,9999999999923. En u-perpendicular se obtiene la cota numérica λ₁−(λ₁−λ₀)‖(I−uuᵀ)e₀‖² a partir de los dos autovalores de fase y el modo inferior normalizado e₀. El control Newton separa la fase de simetría del pequeño valor negativo del interpolante. Al dividir dr por dos, el defecto del interpolante disminuye aproximadamente cuatro veces.

En P06, R80 y dr=0,04, la discretización nodal da −0,02281503, +0,19198859 y +0,18501673 en amplitud libre, amplitud fija y primera fase tras simetría. Comparte los signos y la escala con la FV. La caja y la discretización son distintas. [Datos nodales](../../../validacion/P06/rama/resultados.json) · [Construcción nodal de rango uno](../../../herramientas/cierre_m2.py)

## Límite para la trayectoria forzada

En equilibrio discreto Pu=0, la carga tangente se conserva en el sistema homogéneo y la fase común es neutra. La energía rotante controla las amplitudes y la fase perpendicular con el mínimo de los dos huecos reducidos. La dirección cinética de fase longitudinal se reconstruye mediante q. Sobre el interpolante, aun en la ecuación lineal, la proyección obedece q̇=−(Pu)ᵀb+uᵀFᵦ, con b la perturbación de fase y Fᵦ su fuerza rotante. Descartar esa componente introduciría un error en el balance. Para q distinto de cero el término cinético exacto es (q−2ωvᵀx)².

Siguiente diagnóstico del mismo contacto: en s=0…40, descomponer el residuo de la referencia en fuerza transversal, carga forzada y fase común, contabilizar Pu, y construir una cota temporal del error con cuadratura y resto entre muestras. Tratar el cambio de Hessiano y el resto no lineal en un entorno del estado real antes de propagar la incertidumbre a S, H o balances locales. Si el presupuesto de error no resuelve los dos umbrales de misión, registrar la limitación. La prueba espectral no mide cruce en r60, captura ni recarga.

Reproducción desde este directorio con NumPy y SciPy: ejecutar `OPENBLAS_NUM_THREADS=1 python3 medir.py` y cotejar los cuatro casos de [resultado.json](resultado.json). El programa registra residuos, recuentos, defecto y alineación, referencia nodal y decisión del protocolo.
