# Reserva · primer checkpoint de estabilidad y carga

**Resultado a τ240.** La Q-ball radial estacionaria con $\omega=0{,}9$ conserva el núcleo tras los impulsos ensayados. Una fuente coherente de energía y carga prepara el depósito y un paquete de $\Phi$ deja un incremento medible de ambas magnitudes. El par de amplitudes 0,010 y 0,020 falla la prueba conjunta de escalado débil. El umbral prerregistrado era 25 % y la diferencia observada alcanza 27,54 %. Este primer checkpoint conserva el resultado negativo del rango y los positivos individuales. [Prerregistro](PRERREGISTRO.md) · [Mediciones y decisión](CONTACTO.json)

## Qué se evolucionó

Se usó el perfil estacionario de la rama del capítulo 25 que identifica el capítulo 29 por SHA-256. La gota asentada de CP04 tiene una carga de núcleo distinta. Se reutilizaron de CP04 la acción radial discreta de **ambos** campos, la integración de Verlet y la contabilidad en las caras. La misión tiene simetría esférica. El cálculo resuelve el mediador dinámico y la retroacción sobre el campo complejo. Las tres discretizaciones separan variación espacial y temporal. La lectura principal usa $\Delta r=0{,}025$, $\Delta t=0{,}001$, $R=256$ y observaciones de inventario cada 0,5. El flujo se integra en cada paso. El espectro publicado y las diferencias entre los tres antecedentes están en el [prerregistro](PRERREGISTRO.md).

| Impulso radial $\eta$ | $Q_{40}(0)$ | $Q_{40}(240)$ | Energía neta radiada por $r=40$ | Máxima desviación de $\lvert\Phi\rvert$ |
|---:|---:|---:|---:|---:|
| −0,005 | 2745,745814 | 2745,750752 | 0,00625095 | 0,16573 % |
| 0 | 2745,745814 | 2745,745814 | $2,15\times10^{-12}$ | 0,0000143 % |
| +0,005 | 2745,745814 | 2745,750756 | 0,00624929 | 0,16526 % |

Los dos impulsos iniciales conservan la carga por construcción. La salida posterior puede transportar energía positiva y carga negativa, por lo que la carga interior final puede superar levemente la inicial. La retención mínima muestreada en la malla fina fue 0,99999999896. Los nueve ensayos cumplieron los criterios registrados. La comparación radial del equilibrio fino con el interpolante de origen cambió el perfil en $1,04\times10^{-5}$ relativo. [Nueve contrastes y flujos salientes](ESTABILIDAD.json)

## Presupuesto de la preparación

La rampa de ocho unidades parte de campos nulos. El impulsor de $\Phi$ hizo trabajo neto +2613,006175 y el de $\chi$ recibió 87,373173. La energía final fue **2525,633310** y la carga final **2745,746206**. El error entre trabajo integrado y energía final fue $1,22\times10^{-7}$ relativo. El error de balance de carga fue $1,11\times10^{-15}$ y el del perfil de amplitud $9,80\times10^{-8}$. Son saldos entregados al campo por actuadores ideales con control espacial y de fase. El trabajo necesario para fabricar el actuador y las pérdidas de una fuente material siguen abiertos. El estado fino preparado conserva los seis campos de Cauchy. [Presupuestos de las tres mallas](CONTACTO.json) · [Huella del estado preparado](MANIFIESTO.json)

## Pulso finito y retroacción

La fuente del paquete estaba entre $r=96$ y 144. La portadora positiva tenía $\nu=3,2$. Por $r=60$ se midieron entrada y reflexión con el mismo signo de flujo y los cortes registrados. Para una cara entre las celdas $i,j$, con $c=r_{\rm cara}^2/\Delta r$, los flujos salientes son

$$
F_E=-4\pi c\left[\operatorname{Re}\big((\dot\Phi_i+\dot\Phi_j)^*(\Phi_j-\Phi_i)\big)
+\tfrac12(\dot\chi_i+\dot\chi_j)(\chi_j-\chi_i)\right],\qquad
F_Q=-8\pi c\,\operatorname{Im}(\Phi_i^*\Phi_j).
$$

Cada saldo descuenta la trayectoria gemela preparada sin pulso. La columna absorbida mide cuánto queda dentro de $r=60$ al cierre. El núcleo $r<40$ y el anillo $40<r<60$ se contabilizaron por separado.

| Amplitud | E inicial del paquete | E incidente | E reflejada | E absorbida a τ240 | Aumento de E del núcleo | Fracción absorbida |
|---:|---:|---:|---:|---:|---:|---:|
| 0,010 | 0,338017470 | 0,338017025 | 0,337831974 | 0,000185050 | 0,000171731 | 0,054746 % |
| 0,020 | 1,352069978 | 1,352068097 | 1,351046635 | 0,001021462 | 0,000861548 | 0,075548 % |

| Amplitud | Q incidente | Q reflejada | Q absorbida a τ240 | Aumento de Q del núcleo | $\Delta E_{40}-\omega\Delta Q_{40}$ |
|---:|---:|---:|---:|---:|---:|
| 0,010 | 0,105557514 | 0,105362815 | 0,000194699 | 0,000189682 | 0,0000010165 |
| 0,020 | 0,422230058 | 0,421169501 | 0,001060557 | 0,000941448 | 0,0000142445 |

La última columna es el residuo respecto de la pendiente local de la rama a carga variable. La norma relativa del cambio en $|\Phi|$ del núcleo fue $3,37\times10^{-5}$ y $1,28\times10^{-4}$ frente al gemelo. Los cambios de $\chi$ fueron $7,84\times10^{-7}$ y $3,26\times10^{-6}$. Estas medidas incluyen la retroacción. La índole recuperable del pequeño residuo energético sigue por medir.

## Resolución, banda y decisión

En orden creciente de amplitud, las escalas empíricas $U_E$ fueron 0,00003220 y 0,00014892. Las de carga fueron 0,00001891 y 0,00004020. En los cuatro casos dominó el cambio entre τ220 y τ240. Las señales de energía superan sus escalas por factores 5,75 y 6,86. Las de carga, por 10,30 y 26,38. En vacío los residuos de energía al cierre fueron inferiores a $2,2\times10^{-12}$. Las diferencias entre el puerto y el núcleo cumplieron el criterio de $3U$. Cada componente del presupuesto, incluidas las variaciones de malla, paso y separación temporal de los frentes, se conserva en [CONTACTO.json](CONTACTO.json).

El 95 % central de la energía entrante positiva del paquete está en $\Omega=2,1234$ a $2,4906$. Como diagnóstico adicional se ponderó por ese espectro la dispersión lineal del capítulo 29. La absorción predicha para el paquete infinitesimal fue **0,046314 %**. La predicción monocromática en el centro era 0,06869 %. Cambiar el muestreo de frecuencia modificó la primera predicción en 0,0000680 puntos porcentuales y refinar la malla radial, en 0,00000609 puntos. Las discrepancias de las fracciones finitas respecto de la predicción integrada son 0,00843 y 0,02923 puntos. La lectura a τ240 incluye energía que aún sale del puerto. Atribuir toda la diferencia a no linealidad requiere una medida de retención más larga. [Espectro, conversiones y refinamientos](BANDA.json)

**Criterio para el paso 3.** Hacen falta dos amplitudes con saldos de energía y carga mayores que $3U$, concordancia puerto–núcleo, balances y discrepancia relativa de fracción absorbida inferior al 25 %. El primer par satisface todos salvo el último, incluso tomando la fracción mayor como denominador. El siguiente contraste reduce la amplitud y conserva los umbrales. El ciclo requerirá una espera, descarga hacia una segunda gota con balance propio, control de transmisión directa y recarga. La energía útil entregada a un receptor sigue sin medirse. [Contraste de amplitudes menores](PRERREGISTRO_AMPLITUD_MENOR.md)

## Recuperación y reproducción

El manifiesto identifica los tres ZIP reproducibles de series. Cada uno contiene ocho CSV por discretización. La ejecución genera nueve estados finos NPZ con los campos y velocidades, entre ellos el estado preparado y el gemelo. Al leerlos desde los archivos se recuperan los inventarios, las amplitudes y los perfiles finales de las ocho evoluciones con una diferencia relativa escalada máxima de $1,81\times10^{-16}$. Las huellas cubren los insumos, el código y los resultados. [Manifiesto](MANIFIESTO.json) · [Integrador](radial.c) · [Preparación y medición](ensayo.py)

Desde la raíz de la rama, con Python, NumPy, SciPy y un compilador C11, ejecutar en una carpeta de salida nueva. El último comando coteja cada huella publicada con los archivos de la reproducción. Entorno original: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 y GCC 14.2.0; el integrador se compiló sin contracción de operaciones flotantes. Otras plataformas pueden diferir en los últimos bits.

```sh
exp=checkpoints/Reserva/paso2_20261117
export OPENBLAS_NUM_THREADS=1
python "$exp/ensayo.py" estabilidad /tmp/runica-reserva-reproduccion
python "$exp/ensayo.py" contacto /tmp/runica-reserva-reproduccion
python "$exp/banda.py" /tmp/runica-reserva-reproduccion/BANDA.json
python "$exp/evidencia.py" verificar-reproduccion /tmp/runica-reserva-reproduccion
```
