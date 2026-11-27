# Qué permite acotar el archivo cuando cambia el contacto

**Decisión.** Ninguna de las tres ventanas de contacto tiene una historia espacial de los campos aislados, o un certificado entre muestras, que permita extender al operador variable la cota firmada del arranque congelado. Se conserva el resultado anterior para H fijo. La predicción de entrega en M2 sigue indeterminada. No se abrió un piloto. [Protocolo previo](PROTOCOLO.md) · [Inventario y controles](resultado.json)

## Cobertura de las preparaciones de τ300

La unidad de tiempo local es s=τ−300. Se verificaron contra el manifiesto los SHA-256 y los relojes de 20 archivos: una serie de inventarios y flujos y una serie de sondas por cada donante sin paquete en cinco réplicas. Cuatro llegan a s=480 y R416 llega a s=300. La tabla cuenta muestras **por trayectoria**, incluidos ambos extremos.

| Ventana | Inventarios y flujos | Sondas complejas | Tiempos posibles de perfil radial aislado en la ventana, contando recibos de estado final |
|---|---:|---:|---|
| 0…40 | 41 | 161 | 0 |
| 0…80 | 81 | 321 | 0 |
| 0…240 | 241 | 961 | 0 y 240 |

Las sondas contienen Re e Im de Φ en las dos celdas junto a r40 y r60. Faltan la fase de Φ y el mediador χ sobre el resto del volumen a tiempos intermedios. Los campos completos de retención en τ260 y τ280 preceden al montaje. En las trayectorias de paquete apagado hay estados hasta s300 o s480. Además, la campaña radial anterior registra diez huellas de estados finales sin actuador en s240; se les ha concedido el extremo s240 en el recuento, sin suponer que las distintas cajas son idénticas. Aun así no aparece ningún perfil en el interior de ninguna ventana. Los estados finales de la primera descarga y de su control apagado corresponden a montajes de dos centros con condiciones concretas. No son una trayectoria aislada de cada donante que pueda trasladarse a las tres separaciones y fases.

Se inventariaron 66 archivos de campos NPZ en el árbol de Reserva y los directorios de los ocho ZIP versionados. Los seis ZIP de series del paso 2 contienen CSV. Los otros dos guardan, respectivamente, ocho y tres NPZ, incluidos insumos de preparación. Los estados de la rama de equilibrio describen fondos estacionarios. Es admisible ensayar un fondo estacionario como referencia para la receptora, siempre que se mida el error respecto de la preparación. La donante cargada conserva su perturbación y radiación propias. El diagnóstico se limita al archivo del proyecto en el commit de origen. [Series originales](../mision_paquete_negativo_20261125/datos) · [Recibo radial anterior](../mision_extraccion_radial_20261124/datos/EJECUCION.json)

## Condición suficiente para la extensión

Sea H(t)=−Δ+M²+h|Φ(t)|² en una caja y un dominio de operador fijos. Con una referencia suficientemente regular, H(t)≥M². Para el mediador lineal forzado, u″+H(t)u=S(t), definir w(t)=H(t)⁻¹S(t), y=u−w. Entonces y″+H(t)y=−w″. El dato inicial del montaje sigue siendo (y,y′)=(−w,−w′) en s=0. Para una referencia que aproxime la solución completa, cualquier defecto de la fuente o del operador respecto de M2 debe incorporarse al forzamiento residual.

Con N²=||y′||²+⟨y,Hy⟩, la identidad de energía da

    (N²/2)′ = −⟨y′,w″⟩ + ⟨y,H′y⟩/2 .
    N′ ≤ ||w″|| + α N/2,    α = ||H⁻¹ᐟ² H′ H⁻¹ᐟ²|| .
    α ≤ h ||∂t |Φ|²||∞ / M² .

Integrar esta desigualdad requiere una cota de la integral temporal de α y de ||w″||. Sirve una cota a posteriori independiente que controle los mismos términos; no es condición necesaria guardar cada paso. Para estimar w″ por diferenciación hay que controlar H w″=S″−H″w−2H′w′. La instantánea inicial del estudio estático solo proporciona el extremo inicial de estas cantidades.

El integral firmado también cambia. Con H₀=H(0), integrar la ecuación produce

    H₀ ∫ y dt = u′(0) − u′(T) − ∫ [H(t)−H₀] y dt .

Una estimación suficiente del término adicional es la integral de ||H(t)−H₀|| · N(t)/M. La velocidad final u′(T) pertenece al mediador de contacto. Un recibo del estado de una donante aislada al final no la mide. Para un factor de fuerza espacial y temporal B(t)=(g+hχₛ)Φ y Y(t)=∫₀ᵗ y, aparece además B(T)Y(T)−∫B′Y. Se requieren supremos espaciales de los multiplicadores y control temporal. El término cuadrático proporcional a Φ y² solo admite sin más información la cota en L¹ basada en ∫N²/M². Estas estimaciones no controlan por sí solas las trazas de Φ, sus derivadas normales ni su retroacción en las dos esferas.

## Comprobación independiente de la pérdida de información

En el perfil real publicado de ω=0,900 se construyeron dos instantáneas auxiliares de donante f(r) exp(±ib(r)), con velocidad iωΦ y χ idéntico. La fase b tiene soporte en 34<r<38, con valor y derivadas nulos fuera. La densidad de carga, el potencial, la energía cinética y la densidad de gradiente son idénticos en ambas, porque |∇Φ|²=f′²+f²b′². Coinciden asimismo las sondas y los flujos en r40 y r60. Con una receptora fija i f a separación 80, las dos densidades de solapamiento |D+R|² difieren sobre el eje en 4 fD fR sin b. El programa verificó esta identidad y obtuvo una diferencia máxima muestreada de 9,14845 × 10⁻¹⁴. Basta su valor no nulo para mostrar que la reconstrucción puntual a partir de esos observables no es única. Su tamaño no constituye un límite para la preparación física. La prueba compara dos estados auxiliares en un instante; no cuestiona la unicidad de la evolución M2 con sus datos iniciales completos.

## Siguiente paso del mismo contacto

Lo que falta es una **referencia temporal con error espacial y temporal evaluable para las preparaciones publicadas**. La siguiente prueba de bajo coste es examinar una referencia radial linealizada alrededor de la rama ω=0,900, inicializada por separado con la cargada y la gemela de τ300. Antes de propagar o estimar entrega, medir la discrepancia de campos y velocidades, la condición de borde y el residuo no lineal en el volumen de solapamiento; fijar un criterio de error y comprobar si puede controlarse al menos hasta s=40. Un buen ajuste en las sondas es solo una comprobación externa. Si no puede obtenerse una cota para la fuente y el operador, registrar el límite de esta referencia. Una referencia aislada admisible aún necesitaría control independiente de la retroacción del contacto, de los balances por núcleo y del trabajo de montaje. Permanecen intactas las condiciones de captura y recarga.

Para reproducir se necesita una copia Git del proyecto que contenga el commit e8d99b4b0c5274bc773fc7e05d9d1e8b340a5f4b y los archivos examinados. Ejecutar `python3 auditar.py` en este directorio con Python 3.12, NumPy 2.3.5 y SciPy 1.17.0. [Método](auditar.py)
