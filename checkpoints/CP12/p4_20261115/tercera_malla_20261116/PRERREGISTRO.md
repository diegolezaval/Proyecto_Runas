# CP12/P4 · Prerregistro de la tercera malla

16 de noviembre de 2026. Probar si el acuerdo espacial del piloto P4 mejora al reducir a la mitad $h=0.0625$. La entrega del piloto en `5e00e74ec733ad1171f3bb024404ddfc30e1d2c2` proporciona las dos historias P4 cerradas. Identidad original `8a6775db0628457ca53ffece57c210d3`, run `1494ea1de6f7c1c084b99b4fa7e9892fc74d0c7089cdbc96dea82d334829cc18`. El registro de insumos fija el respaldo y los recibos originales por tiempo.

## Único cambio físico-numérico ensayado

Integrar solamente la malla candidata $h=0.03125$, con 7040 celdas en la misma caja $R=220$, $L=4$, $\epsilon=0.02$, M2/Θ, acción P4, DOP853 original, rtol $10^{-10}$, atol $10^{-12}$, paso máximo 0.02 y observaciones cada 0.4. Reiniciar el integrador en cada frontera de ocho unidades, igual que el piloto. Preparar las seis componentes de Cauchy con `seed` original, perfil radial CP04 guardado en $\tau=1200$, extensión par, cúbica y deformación cuadrupolar original. Volver a preparar las dos mallas guardadas para comprobar sus Cauchy exactos con cero pasos M2. Comparar fuerza C y NumPy en la nueva resolución y comprobar el enrutado de Φ y χ, la finitud y la simetría de la semilla antes del primer paso.

El origen y cada frontera de la malla nueva registrarán la identidad propia, configuración, hashes de estado y observaciones, saldo de pasos aceptados, salida observada y recuperación por SHA-256 desde una sesión nueva con cero pasos M2. Publicar el respaldo y su recibo en GitHub antes de avanzar. Verificar la exclusividad mediante un grupo de concurrencia propio y publicación condicionada al HEAD del registro. Si se interrumpe el proceso, reanudar desde el último cierre exacto de esta identidad. Ante una puerta fallida conservar el estado, su recibo y el último cierre válido.

## Comparaciones y decisión

| Par | Trayectorias | Comparación oficial |
| --- | --- | --- |
| $0.125 \to 0.0625$ | Dos estados guardados de P4 al mismo tiempo | Reproducir las cinco métricas publicadas con tolerancia de lectura rtol $10^{-11}$, atol $10^{-13}$. |
| $0.0625 \to 0.03125$ | Estado P4 guardado y estado nuevo al mismo tiempo | Cúbica gruesa→fina, $r<40$, mismos pesos y normalización a la semilla fina. Cinco discrepancias ≤ 0.02 en cada cierre. |

Aplicar la función original `diagnosticar_mediador_CP10.compare`. Para prefijos se parametriza únicamente la guarda del tiempo final, manteniendo los tiempos reales. La fase global de Φ sigue el protocolo original. χ se evalúa con el campo real y su velocidad, sin girarlo. Conservar la parte de campo y la de velocidad de χ en la métrica conjunta, además de las fracciones radiales y angulares. Exigir que las observaciones de los tres estados sean prefijos completos en los mismos tiempos.

Exigir en la malla nueva la deriva de cada energía, FV y P4, ≤ $2\times10^{-4}$ y la deriva de carga ≤ $10^{-9}$ en los pasos aceptados, el cambio de carga del núcleo ≤ 0.005 y la amplificación ≤ 3 en los observadores originales, más la comprobación de simetría e identidad a escala original ≤ $2\times10^{-12}$ en las fronteras. Aplicar las puertas físicas también al evaluar los dos estados recuperados del piloto. Los observadores de balance a cada 0.4 conservan sus definiciones. El presupuesto causal pasivo de dos historias del piloto se conserva en su alcance. Esta prueba de refinamiento no recalcula ese presupuesto sobre la tercera malla.

Para χ en espacio de fases, comparar en cada cierre $D_{01}(\tau)$ y $D_{12}(\tau)$. Publicar la serie, con atención a $120\le\tau\le160$. En τ160, $D_{12}<D_{01}$, con todas las puertas satisfechas, apoya mejora al refinar. $D_{12}\ge D_{01}$ con puertas satisfechas deja el acuerdo dentro del umbral y la mejora sin respaldo. Una puerta de comparación o de balance fallida exige suspender. Cuando las diferencias son positivas y distinguibles del redondeo, publicar $\log_2(D_{01}/D_{12})$ como orden observado de las discrepancias. Indicar qué cambia al medir ambos defectos con pesos y escala inicial en el mismo retículo fino. Ni el orden formal del término radial ni la estructura de altas frecuencias del operador fijan el orden de una trayectoria con esta preparación.

El resultado se limita a la semilla, caja, truncamiento, intervalo y comparador registrados. La decisión global de CP12 requiere además el contraste de referencia, estabilidad y robustez. [Plan del siguiente contraste](SIGUIENTE_CONTRASTE.md)
