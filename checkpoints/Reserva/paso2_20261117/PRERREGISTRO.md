# Reserva · primer contraste de estabilidad y contacto

Protocolo previo a toda evolución de esta entrega. El origen científico es CP12 cerrado en `843dc24113a966c650d37e721593391be73ec23e`. Las magnitudes emplean las unidades normalizadas comunes de M2. Se ensaya la carga finita de un depósito, con simetría esférica exacta.

| Candidato o antecedente | Evidencia que se reutiliza | Alcance para esta misión |
|---|---|---|
| Rama de Q-balls estacionarias | 23 perfiles a distintas frecuencias. En $\omega=0,9$, $E=2525,65891$, $Q=2745,77392$, menor autovalor radial a carga fija muestreado $0,19199$, raíz cuadrupolar seleccionada $0,04378$ bajo el umbral $0,1$. | Se elige este punto, con el perfil y el espectro publicados. La estabilidad no lineal se medirá en el canal radial de la misión. |
| Preparación CP04 | Gaussiana cargada de anchura 7,2 y mediador relajado. A $t=1200$ retiene en promedio 90,132 % de la carga en $r<40$. El equilibrio discreto de carga comparable tiene $Q=2474,83057$, $\omega=0,901326$ y el núcleo conserva un exceso medio de energía $0,15818$. | Se reutilizan la acción radial de volúmenes finitos de dos campos, Verlet y el corte de núcleo con media cara. La campaña P4 delimitó la evolución no radial de esta preparación. Trasladar ese resultado al equilibrio elegido requeriría un nuevo contraste. |
| Fondo de acceso lineal | El capítulo 29 leyó el mismo CSV de $\omega=0,9$ que el capítulo 25. A $\Omega=2,3$ la probabilidad de conversión monocromática es $0,00122117$. | La entrada positiva predice un déficit relativo de flujo exterior $2\omega P/(\Omega+\omega)\simeq0,000687$. Orienta el signo y la portadora. La envolvente finita tiene un espectro de frecuencias propio. |

[Capítulo 25](../../../tratado/25_carta_validez_y_rama_reserva.md) · [Capítulo 26](../../../tratado/26_preparacion_radial_condicionada.md) · [Capítulo 29](../../../tratado/29_acceso_lineal_a_reserva.md) · [Decisión lineal y huella del perfil](../../../validacion/P06/acceso_lineal/puerta_decision.json) · [Operador y alcance CP12](../../CP12/p4_20261115/OPERADOR_CHI.md)

## Datos, dominio y contraste de estabilidad

Se leen el [perfil](../../../validacion/P06/rama/perfil_w0.90000.csv) (SHA-256 `9037fb7f1fa691fe5d8712efee3092d26cc2303b95853694cb7a2539ec1f5574`) y [Θ](../../../datos/theta_comun.json) (`ccba93368f572cae3ba1727ecb454a08491c508ee93d207528b8c5527c0e0cc3`). En cada malla se interpola $f,z$ con sus derivadas, se prolonga su cola despreciable y se resuelven las ecuaciones radiales estacionarias a frecuencia fija en la misma acción que se evolucionará. Registrar la corrección al perfil y el residuo. Ambos campos estarán activos. Como contraste propio del paso 2 se usará el operador FV radial de CP04 para ambos campos.

Caja $R=256$, regularidad central y Dirichlet nulo en la cara exterior. Mallas $(\Delta r,\Delta t)=(0,05;0,002),(0,025;0,002),(0,025;0,001)$, con el paso temporal menor como lectura principal. Las dos comparaciones varían un eje por vez. El núcleo es $r<40$ y la esfera de medida del contacto $r=60$. Se evolucionan $0\le\tau\le240$. Los emisores de estabilidad están localizados en el núcleo. Desde el extremo exterior del paquete, $r=144$, el trayecto por el borde hasta la esfera de medida es 308, mayor que la duración del ensayo.

En $\tau=0$ se fijan $\Phi=f$, $\chi=z$, $\dot\chi=0$ y $\dot\Phi=i\omega f+\eta f\exp[-(r/12)^2]$ para $\eta=-0,005,0,+0,005$. El impulso real cambia la energía cinética conservando la carga inicial. Se medirán $Q_{40}$, energía exterior, flujo energético neto y saliente por $r=40$, y desviación ponderada de $|\Phi|$ respecto de $f$ dentro del núcleo. Exigir en todos los casos deriva relativa global $|\Delta E|/E_0<2\times10^{-4}$ y $|\Delta Q|/Q_0<10^{-9}$, $Q_{40}/Q_{40}(0)>0,99$, incremento máximo de energía exterior $<10^{-3}E_0$ y error de perfil $<5\%$. El cambio por refinamiento de la retención mínima será $<0,002$ en valor absoluto. Publicar el primer fallo si lo hubiera. Estos puntos discretos delimitan la muestra.

## Preparación condicionada y pulso

Tras aprobar estabilidad se preparará el estado desde campos nulos con una fuente coherente prescrita que aporta energía y carga positiva, y un actuador real que prepara el mediador. Fijar $T_p=8$, $x=t/T_p$, $b=10x^3-15x^4+6x^5$. La trayectoria de referencia es $\Phi_b=b f e^{i\omega t}$, $\chi_b=b^2 z$. Aplicar durante la rampa las dos fuentes calculadas como aceleración de esa trayectoria menos la fuerza libre discreta evaluada en ella. Evolucionar los campos con esas fuentes y retirarlas al terminar. Medir ambos trabajos $\int 4\pi\sum w[2\operatorname{Re}(\dot\Phi^*J_\Phi)+\dot\chi J_\chi]dt$ y la carga aportada $\int 8\pi\sum w\operatorname{Im}(\Phi^* J_\Phi)dt$, su saldo y el costo positivo que atraviesa cada actuador. Exigir errores relativos de balances y del perfil de amplitud $<3\times10^{-4}$. La fase global se puede rotar para comparar estados. La fuente es un insumo ideal externo con presupuesto explícito. La fabricación de esa fuente y el desmontaje físico quedan abiertos. La trayectoria inversa da un destino previsto para la energía y la carga en el actuador reversible.

El contacto es exclusivamente la interacción interna del campo cargado con la gota y su mediador. Tras preparar el depósito se superpone un único paquete entrante de carga positiva. Con $s=r-120$, $H=24$, usar $B=\cos^4[\pi s/(2H)]$ si $|s|<H$ y cero fuera. Para $a=0,010$ y $0,020$,

$$
\delta\Phi=a B e^{iks}/r,\quad
\delta\dot\Phi=a(i\nu B+v_g B')e^{iks}/r,\quad
\nu=\omega+2,3=3,2,\quad k=\sqrt{\nu^2-m^2},\quad v_g=k/\nu.
$$

La envolvente entrante dura aproximadamente $2H/v_g=50,5$ en la esfera. Registrar espectro del paquete, inventarios $E,Q$ de la fuente incidente y su cruce efectivo. Reservar un gemelo preparado sin pulso y controles del mismo pulso en vacío. $\chi$ conserva su velocidad y campo preparados al añadir el paquete. Fuente del pulso y depósito se presupuestan por separado.

## Decisión de acceso y paso 3

A través de la misma cara $r=60$ integrar los flujos **orientados hacia fuera** de energía y carga de M2. Sustraer el gemelo por tiempo. La entrada se integra con signo invertido entre 0 y 105, y la reflexión total entre 105 y 240. Registrar también los cortes 100, 110 y 220. La energía absorbida neta al cierre es entrada menos salida. Comprobarla con el incremento de energía dentro del puerto y dentro de $r=40$, y publicar $\Delta Q$ y $\Delta E_{40}-\omega\Delta Q_{40}$ para distinguir cambio de carga y excitación. Registrar además el cambio del perfil de la gota respecto del gemelo.

Para cada amplitud y cada saldo $X=\Delta E,\Delta Q$, estimar $U_X$ como máximo de los cambios absolutos al refinar malla o tiempo, del residuo neto del pulso en vacío en el puerto, del error flujo–inventario, de la variación del saldo al cierre 220→240 y de la variación de entrada y salida al mover el corte a 100/110. Evaluar $X>3U_X$ en **ambas** amplitudes, balances globales dentro de las tolerancias de estabilidad, y que los incrementos del núcleo a 240 concuerden con los del puerto dentro de $3U_X$ (piso $10^{-8}$ en unidades del observable). Comparar la fracción absorbida entre las dos amplitudes, con discrepancia relativa $<25\%$ como prueba limitada de escalado débil. La decisión se toma sobre el paquete resuelto, sin sustituir su banda por una portadora monocromática.

Un positivo habilita **diseñar y probar** el ciclo del paso 3. El receptor previsto es una segunda gota M2 preparada de carga conocida, inicialmente separada, con inventarios propios y disposición de dos centros. La recepción útil deberá superar su incertidumbre con un control de transmisión directa, una espera y una descarga seguidas de recarga. La esfera de medida cuenta todo lo que cruza. Para un negativo se publicarán el saldo, su piso de resolución y el criterio concreto que falte. Las puertas generales RES0–RES5 y E08 exigirán la evidencia de sus propios alcances.
