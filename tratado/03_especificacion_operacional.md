# Especificación operacional R1

## O.1. Arquitectura y uso

R1 separa cuatro funciones: obtener recursos, conservarlos, distribuirlos y aplicar una transformación. La interfaz de usuario presenta una tarea, su región y una consigna. El controlador resuelve conexiones, reservas, secuencias y límites. Una operación sencilla de solicitar puede requerir una instalación compleja.

El equipo portátil ordinario contiene una Semilla asentada, Reserva, Memoria de recetas, Sensor local, control y terminales de enlace. El usuario no reconstruye manualmente todo el grafo en cada uso. Las recetas se copian como información; las estructuras se preparan con energía. La copia no incluye materia, energía ni carga de forma gratuita.

No existe una cuota de potencia ligada a la persona. La potencia crece al ampliar captación, reserva, enlaces, terminales, soporte y evacuación térmica. El control distribuido permite instalaciones grandes sin que toda la información ni toda la energía atraviesen la mano del operador.

Los parámetros de `datos/parametros.json` son valores adoptados del perfil, no resultados experimentales. Permiten dimensionar y comparar diseños de manera inequívoca. Las propiedades que ese archivo no cuantifica no adquieren automáticamente valores favorables.

## O.2. Geometría, tamaño y cruces

La unidad gráfica \(u\) no es una longitud física. Para una plantilla de sobremesa se adopta \(\ell_u=10\,\mathrm{mm}\), radio de núcleo modal objetivo de \(0.1\,\mathrm{mm}\), radio mínimo de redondeo de \(0.5\,\mathrm{mm}\) y distancia entre capas en cruces de \(1\,\mathrm{mm}\). Son tolerancias y dimensiones del diseño R1; no se derivan de \(m_r\). Si una configuración no cabe respetándolas, se amplía uniformemente la plantilla o se modifica su ruta tridimensional conservando la conectividad.

Las esquinas de R y N describen ejes de encaminamiento. En la realización se redondean dentro de la tolerancia de trazado; una discontinuidad matemática no representa curvatura física infinita. Las uniones declaradas reúnen modos mediante una región de transición. Los cruces interiores se separan en altura siguiendo `crossing_lane`; las rampas se colocan fuera del núcleo de las uniones. El esquema 2D no constituye por sí mismo un plano tridimensional de fabricación ni demuestra aislamiento.

Cada canal debe cumplir una medida de transmisión parásita \(P_{ajeno}/P_{inc}\le10^{-6}\) dentro de la banda y cargas nominales. Se mide también la fase y el efecto acumulado de varios vecinos. La especificación geométrica de separación no reemplaza esa medición. En una matriz de dispersión pasiva, \(S^\dagger S\preceq I\); cualquier ganancia utiliza una alimentación explícita.

Polarización conserva sus cinco piezas. R₂ se sitúa mediante \((a,b,t_x,t_y)=(0,1,4,-4)\) y conecta R₂.b con N₂.2 y R₂.a con N₂.3. Así desaparece el tramo superpuesto. Las coordenadas racionales registradas son la autoridad de esta edición; los SVG se regeneran de ellas.

## O.3. Interfaces y composición

Cada puerto declara identificador, dirección, magnitud de esfuerzo, magnitud de flujo, unidad, banda, capacidad y referencia. La potencia positiva entra en el dispositivo. Se admiten:

| Dominio | Esfuerzo | Flujo | Potencia |
|---|---|---|---|
| Eléctrico | Tensión V | Corriente A | \(VI\) |
| Mecánico lineal | Fuerza N | Velocidad m/s | \(\mathbf F\cdot\mathbf v\) |
| Rotación | Torque N m | Velocidad angular rad/s | \(\boldsymbol\tau\cdot\boldsymbol\omega\) |
| Fluido | Presión Pa | Caudal m³/s | \(p\dot V\) |
| Térmico reversible | Temperatura K | Flujo de entropía W/K | \(T\dot S\) |
| Químico | Potencial químico J/mol | Flujo molar mol/s | \(\mu\dot n\) |

Una señal digital transporta información y consume una potencia de implementación; el número lógico no es una variable conjugada de potencia. Un puerto mixto tiene subcanales separados. Una conexión exige unidades compatibles, referencia común, direcciones compatibles y capacidad suficiente. Un enlace entre magnitudes distintas usa un transductor declarado. El integrador nunca convierte un dato de posición en un empuje por simple conexión.

Las regiones funcionales —superficie de Captador, volumen de Reserva, terminal luminoso o campo de aplicación— pertenecen al estado desplegado. No todos sus intercambios atraviesan un extremo dibujado. El modelo enumera tanto puertos de grafo como terminales de campo; un glifo sin extremos libres no está por ello aislado del entorno.

En una unión ideal, esfuerzos compatibles coinciden y los flujos orientados suman cero. La región real de unión puede almacenar energía y tener pérdidas. Para el conjunto portuario:

\[
\dot z=(J-R_d)\nabla_zH+Gu,\quad J=-J^T,\ R_d\succeq0,
\]

\[
\dot H=u^Ty-\nabla H^TR_d\nabla H+
\frac{\partial H}{\partial\lambda_a}\dot\lambda_a.
\]

El último término es trabajo de modulación. Cambiar una barrera, rigidez, frontera o filtro no es gratuito. Una bomba térmica o reacción no se reduce a este Hamiltoniano mecánico: se añaden estados de entropía, composición y sus balances.

## O.4. Fuente, reserva y red

Un captador de área iluminada \(A\) entrega al bus

\[
P_{bus}=\eta_\odot IA-p_AA.
\]

Con R1, son 798 W/m² a la irradiancia del caso. Los 200 W/m² no convertidos y los 2 W/m² de servicio terminan como calor, radiación o transporte expresamente asignado. La eficiencia del 80 % es una hipótesis de ingeniería; estar bajo un límite termodinámico no demuestra su realización espectral.

Una celda de Reserva separa energía estructural \(E_s\) y carga útil \(E\):

\[
\dot E=\eta_c P_c-P_d/\eta_d-kE-P_0,
\quad 0\le E\le\rho_E V.
\]

\(P_c\) es potencia recibida; \(P_d\), potencia entregada. Se impide carga y descarga simultáneas en una misma celda. Si \(E=0\), un suministro externo mantiene \(P_0\) o se inicia retirada; la ecuación no permite energía negativa. La potencia térmica es

\[
P_h=(1-\eta_c)P_c+(\eta_d^{-1}-1)P_d+kE+P_0.
\]

Para un litro: 1 MJ útil, 50 kJ estructurales y límite de terminal de 100 kW. La energía estructural no se cuenta otra vez como carga útil. El desmontaje ordenado recupera hasta 45 kJ según el perfil; una avería puede convertir la totalidad en energía térmica o cinética. Las celdas grandes se segmentan para limitar la energía involucrada en un fallo local.

En un Canal de longitud \(L\):

\[
P_{sal}(t)=e^{-\alpha L}P_{ent}(t-L/v),\quad
E_{viaje}=\int_0^L\frac{P(x,t)}v\,dx.
\]

Se añaden \(e_LL\) de estructura y \(p_LL\) de mantenimiento. El vaciado espera la energía en tránsito. La pérdida proporcional y el mantenimiento son conceptos distintos. La sección de referencia admite 100 kW; dividir el control no multiplica esa capacidad. En 1 km, el retardo es 0.1 ms y la transmisión de potencia, 90.48 %.

La cota de capacidad de información \(C=B\log_2(1+\mathrm{SNR})\) es 6.66 Mbit/s en el ensayo. Es una cota bajo el modelo de ruido correspondiente, no un caudal garantizado después de codificación y protocolos.

## O.5. Despliegue, alcance y crecimiento

Detectar una región, enviarle información y preparar allí una estructura son operaciones diferentes. La detección está limitada por señal, ruido y resolución; el mando por capacidad y retardo; la actuación por terminal, energía y camino de preparación.

Para un captador circular que crece desde \(A_0\), con toda la potencia neta destinada al crecimiento:

\[
\dot A=\min\left[\frac{(\eta I-p_A)A-P_{serv}}{e_A},
2v_f\sqrt{\pi A}\right],
\]

si la primera expresión es positiva; de otro modo no crece. Este modelo no sirve sin cambios para corredores, superficies discontinuas o territorios ocultos. Incluye una restricción energética y otra cinemática. El control de acceso y la verificación del borde deben terminar antes de activarlo. No se prepara una región ocupada sin evaluar sus interfaces.

El tiempo total se calcula en el grafo de dependencias: operaciones simultáneas usan el máximo de sus duraciones; operaciones consecutivas suman. Los límites \(E/P\), distancia/velocidad y ancho de banda son cotas, no una agenda completa. Las tasas variables se integran.

## O.6. Soporte y actuación

El soporte longitudinal R1 es un objetivo para una estructura inhomogénea o un lazo activo. No es una propiedad deducida del condensado homogéneo de M1 o M2, que no tiene rigidez cortante estática. Como modelo de ingeniería tiene

\[
k=YA/L,\quad F_{max}=Y\epsilon_{max}A,\quad
E_s=u_sAL,\quad E_{el}=F^2/(2k).
\]

Con los valores de referencia: \(k=10^4\,\mathrm{N/m}\), \(F_{max}=2000\,\mathrm N\), \(E_s=200\,\mathrm{kJ}\). Una masa de 100 kg produce 98.1 mm de extensión estática si no existe precarga ni corrección. Un objetivo de error de 1 mm requiere medida y corrección de la longitud de reposo; no se obtiene diciendo que el soporte es rígido.

Para la coordenada vertical, \(m\ddot x=F-mg\). Una ley \(F=mg+K_p(x_*-x)-K_d\dot x\), con saturación \(|F|\le F_{max}\), proporciona para 100 kg y \(\omega_n=10\,\mathrm{s^{-1}}\), \(\zeta=1\): \(K_p=10^4\,\mathrm{N/m}\), \(K_d=2000\,\mathrm{N\,s/m}\). Se muestrea a 1 ms, con sensor y terminal locales. Una perturbación constante de 10 N produce 1 mm sin integral. El seguimiento se acepta sólo si ruido, retardo y perturbaciones respetan ese presupuesto. La ganancia integral, si se añade, requiere antiacumulación y nueva comprobación de estabilidad.

Una presión terminal objetivo de 100 kPa exige al menos 98.1 cm² para 981 N. Este valor corresponde a un apoyo material común y no declara tolerancia de piel, vasos o tejidos. El suelo debe admitir el esfuerzo y el torque. El momento de carga, red, apoyo y entorno se contabiliza conjuntamente.

Usar \(\rho_{iner}=u_s/c^2\) como inercia efectiva mínima y la ley longitudinal da \(c_s=c\sqrt{Y/u_s}<c\) para R1. No es una derivación relativista completa del material; sirve como comprobación necesaria del perfil. Un enlace de potencia y un soporte mecánico tienen energías estructurales distintas.

Impulso es el nombre del actuador de fuerza; el impulso mecánico es \(\mathcal J=\int Fdt\). Volar requiere apoyo remoto, reacción aerodinámica, masa eyectada o radiación. Para un chorro ideal \(F=\dot m v_e\), \(P_{jet}=Fv_e/2\). Para fotones \(P=Fc\): sostener 100 kg requiere aproximadamente 294 GW, antes de ineficiencias. La selección del modo de reacción determina la viabilidad del vuelo.

## O.7. Calor y potencia sostenida

Una bomba que extrae \(\dot Q_c\) a \(T_c\) y rechaza a \(T_h>T_c\) cumple

\[
\dot W=\dot Q_c/\mathrm{COP},\quad
\dot Q_h=\dot Q_c+\dot W,\quad
\mathrm{COP}=\eta_C\frac{T_c}{T_h-T_c}.
\]

R1 adopta \(\eta_C=0.5\). Las temperaturas son las del ciclo, no automáticamente las del objeto y el ambiente: en un terminal finito \(\dot Q=G_{th}\Delta T\). Un radiador a 400 K frente a un entorno uniforme de 300 K emite netamente

\[
\dot Q=\epsilon\sigma A_r(400^4-300^4),
\]

unos 893 W por m² de superficie emisora con factor de vista efectivo uno. Ambas caras cuentan sólo si ambas ven el entorno adecuado. Si un captador produce 202 W térmicos/m² y evacúa por este radiador, necesita al menos 0.226 m² emisores por m² captador, además del transporte del calor. El radiador y su montaje deben prepararse y mantenerse; no están incluidos en el coste de la película captadora si no se declaran.

Los valores de energía almacenada y potencia máxima son independientes. Una reserva capaz de 100 kW no puede operar indefinidamente con un disipador de 10 W. Cada receta declara duración, energía, potencia de pico y disipación media.

## O.8. Medida, óptica y electromagnetismo

Sensor no proporciona conocimiento ilimitado. Cada modalidad declara observable, banda, distancia, resolución, incertidumbre y perturbación de medida. Un termómetro mide su terminal; una imagen requiere fotones que lleguen; un análisis químico necesita una señal ligada a especies. Las variables internas del controlador no sustituyen mediciones externas.

En óptica, una apertura circular de diámetro \(D\) tiene escala angular de difracción \(1.22\lambda/D\). Con 550 nm y 2 cm resulta 33.6 µrad; turbulencia, ruido y aberraciones pueden empeorarla. La potencia emitida es \(\eta_LP_{bus}\); el resto se evacua. El muestreo angular, el espectro, la coherencia y la apertura limitan la reproducción de un frente de onda.

El camuflaje por pantalla reproduce radiancia para un conjunto declarado de posiciones y bandas. No equivale a transparencia universal: observadores múltiples, sombras, calor, paralaje, retardo y escenas no medidas necesitan recursos adicionales. Un manto de dispersión completo requeriría un tensor constitutivo realizado y su balance causal; R1 no lo da por disponible.

Polarización conserva su nombre de catálogo y designa acondicionamiento electromagnético: distribución de carga, corrientes y respuesta material. Debe indicarse la modalidad concreta. Un campo magnético obedece Maxwell; \(\nabla\cdot\mathbf B=0\), las corrientes de retorno y la energía \(\int B^2/(2\mu_0)dV\) se incluyen. Cambiar un campo induce campos eléctricos; no se omite la energía de rampa ni las fuerzas sobre el entorno.

## O.9. Computación y control distribuido

Memoria utiliza estados metastables separados por una barrera libre. En el modelo térmico \(\tau\approx\tau_0e^{\Delta F/k_BT}\). R1 adopta 60 \(k_BT\) y \(\tau_0=10^{-12}\) s; ese tiempo caracteriza un bit aislado dentro del modelo, no la vida útil de todo el sistema. Para \(N\) bits independientes, la tasa total aproximada es \(N/\tau\). Radiación, fallos comunes, fabricación y pérdida de alimentación tienen tasas adicionales.

Un bloque (7,4) corrige un error aislado; dos errores dentro del intervalo de corrección pueden producir una palabra equivocada. La corrección consume lecturas, escrituras y energía. El borrado irreversible de un bit equiprobable requiere al menos \(k_BT\ln2\) en el límite cuasiestático; la conmutación R1 presupone \(10^{-17}\) J, por encima de ese límite a 300 K. Un millón de conmutaciones por segundo consume al menos el presupuesto correspondiente, además de sensores, reloj, bus y mantenimiento.

Compuerta, Comparador y Selector implementan umbrales con histéresis y regeneración alimentada. La salida debe mover las entradas siguientes dentro del margen de ruido; la ganancia de una etapa no surge de una figura pasiva. Retardo y Reloj producen tiempos locales. La fase del reloj evoluciona respecto del tiempo propio; sincronizar nodos separados necesita intercambio de señales y estimación del retardo. No existe un reloj global instantáneo.

Secuenciador ejecuta una máquina de estados finita. Cada instrucción incluye unidad, destino, precondición, límite y resultado observable. Los lazos rápidos permanecen junto al actuador; el operador envía consignas más lentas. El fallo de enlace no congela necesariamente el último empuje: cada receta declara la transición autónoma que conserva una situación controlable.

## O.10. Fallos, autoridad y aceptación

Un recurso tiene un controlador propietario y una concesión temporal identificada. Una orden incorpora emisor, número de secuencia, época de configuración y caducidad. Una orden antigua, incompatible en unidades o fuera del dominio se rechaza. Dos operadores no suman fuerzas inadvertidamente: arbitra el controlador del recurso. Las capacidades de actuación se separan del permiso para editar su receta. El formato de identificación no constituye por sí solo un protocolo criptográfico; una implementación expuesta debe añadir autenticación con primitivas establecidas.

Estados comunes: preparación, verificación, disponible, ejecución, degradación, retirada y avería. Una retirada normal descarga campos, transfiere cargas, iguala presiones y recupera energía. Una avería reserva energía local para la transición físicamente posible. Si desaparecen simultáneamente apoyo y toda fuente, no se promete suspensión indefinida. Un dispositivo declara qué fallos cubre y cuánto dura su reserva de emergencia.

La aceptación tiene tres niveles: comprobación de archivos y geometría; simulación bajo leyes constitutivas; ensayo de una realización. El paquete ejecuta los dos primeros sólo en los casos indicados. No etiqueta una prueba algebraica como medición experimental. El inventario de los 50 puntos registra qué se corrigió, qué se adoptó y qué sigue requiriendo una demostración microscópica.
