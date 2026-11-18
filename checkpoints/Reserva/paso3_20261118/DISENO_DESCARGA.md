# Primera descarga de Reserva

Este diseño concreta la segunda fase del [prerregistro](PRERREGISTRO.md) tras superar la espera. El reloj local s empieza en el disparo. Las decisiones de calibración, controles y lectura se fijan antes de obtener las ganancias del receptor.

## Campos, señal y calibración

Los centros están en z = −60 (donante) y +60 (receptor). Se interpolan las seis componentes radiales completas. El donante procede de τ300 con el paso 0,0005. El receptor parte de la preparación fina del paso 2. En la configuración inicial se elige la fase central cero para cada gota mediante una rotación constante de Φ y de su velocidad. Las colas y el paquete exterior del donante forman parte de los datos iniciales. El control gemelo sustituye el donante por su gemelo de τ300. En transmisión directa se conserva el receptor y se aplica la misma fuente en el espacio vacío del donante.

Se añade a la ecuación de χ la fuente J = A cos⁴(πr/12) sen²(πs/8) sen(2,3s), en r < 6 alrededor del donante y 0 < s < 8. Fuera de ese soporte vale cero. Su trabajo es la integral de J dχ en el volumen. La fuente preserva la simetría de fase y su aporte directo de Q es cero.

Se calibra en el gemelo radial aislado, sin receptor. El trabajo objetivo equivale al 10 % del saldo de energía del núcleo fino en τ300. Se inicia en A = 0,01 y se actualiza A por la raíz del cociente entre trabajo objetivo y medido hasta quedar a un 2 % del objetivo. Se congelan la amplitud y los seis campos finales de cada ensayo de calibración antes del contraste. El trabajo efectivo se vuelve a medir en cada montaje.

## Integración y lectura

Se usa la acción M2 de ambos campos, volúmenes finitos cilíndricos, regularidad sobre el eje y campos nulos en los bordes ρ = 320 y |z| = 384. La distancia mínima del borde a cualquier núcleo es 280, superior a toda la ventana de 240. La malla es fina alrededor de los dos núcleos y ensancha suavemente hacia el exterior. Se comparan tres discretizaciones con (paso espacial interior, paso temporal) iguales a (0,40; 0,01), (0,30; 0,01) y (0,30; 0,005). La última da la lectura principal. Se registran por unidad de tiempo los inventarios globales, de ambos núcleos de radio 40 y del exterior, y el trabajo acumulado.

Para E y Q se resta en cada trayectoria el inventario inicial de su propio receptor. Se integra por trapecios la media entre s = 200 y 240 y se resta el resultado de cada control al de la gota cargada. Para cada uno de los cuatro contrastes, U es el máximo de las dos variaciones sucesivas de discretización (espacio a paso temporal fijo y tiempo a malla fija) y de las diferencias entre la media principal y las de 200–220 y 220–240 en la misma malla. Se exige D > 0 y D > 3U en los cuatro. Un fallo cierra esta misión en la primera descarga. Los residuos globales y el efecto de mapear los campos radiales a la malla cilíndrica se informan por separado.

Un saldo frente a un receptor también puede recoger radiación de la carga inicial. Si los cuatro contrastes pasan, se contrasta la atribución al disparo con los mismos campos cargados sin señal antes de interpretar la entrega útil. La recarga sólo tiene sentido a partir del estado final de una primera entrega resuelta.
