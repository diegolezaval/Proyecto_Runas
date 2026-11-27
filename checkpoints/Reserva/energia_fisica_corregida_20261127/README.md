# Coste físico de la cola tras la primera corrección

**Decisión.** Al retirar la ponderación exponencial desaparece el coste del conmutador del propagador. En la cargada reaparece una fuente exterior suficientemente grande para agotar el presupuesto transversal de esta comparación. La gemela y la receptora pasan ese primer cribado, pero la prueba suficiente con realimentación no lineal tampoco cubre en ellas las 40 unidades. Queda indeterminado el error real de trayectoria. El piloto continúa sin habilitarse.

[Protocolo](PROTOCOLO.md) · [Cálculo](auditar.py) · [Resultados](resultado.json) · [960 intervalos](bandas.csv.gz) · [Contraste radial registrado](PROTOCOLO_TRAZA.md) · [Método de traza](traza.py) · [Resultados de traza](traza.json)

## Dónde se consume el presupuesto

Se reconstruyeron las mismas correcciones temporal y de Taylor, y solo esas dos, desde los datos originales con los mismos puentes h=0,125, orden 22, ocho subdivisiones, R256 y dr=0,025. En cada intervalo se reprodujo la envolvente ponderada publicada. Se retuvo el volumen FV 4πW y la normalización canónica (√2,√2,1); se retiró el peso exponencial al sumar la norma de aceleración. La tabla da la integral desde s=0 hasta 40 del mayorante original del cambio de Taylor, con cobertura entre muestras.

| Preparación | r<60 | 60≤r<160 | r≥160 | Toda la malla |
|---|---:|---:|---:|---:|
| Cargada | 9,854e−9 | 1,939e−6 | 1,11927e−4 | 1,12049e−4 |
| Gemela | 9,643e−9 | 1,107e−15 | 2,961e−16 | 9,643e−9 |
| Receptora | 9,650e−9 | 2,850e−28 | 1,583e−62 | 9,650e−9 |

Se combinan cuadráticamente las bandas dentro de cada intervalo y después se integra; los tres números de una fila no se suman linealmente para obtener el total. En la cargada, la misma envolvente con peso exponencial había dado 1,04148e−8. El límite provisional es 1e−4/423,9711=2,35865e−7. La cola r≥160 por sí sola supera ese presupuesto unas 475 veces. Ello compara dos mayorantes y no mide la magnitud del error real ni un flujo físico.

El mayorante original multiplica la envolvente de corrección por un mayorante local del jacobiano. Como control adicional se expandió la diferencia finita de cada término del polinomio M2; por ejemplo, para un desplazamiento complejo acotado por d alrededor de una amplitud de módulo ≤U, el cambio de densidad queda acotado por (2U+d)d. Se retuvo el menor de ambos mayorantes por celda y se comprobó por sustitución en cada extremo. En el volumen completo se obtuvieron integrales 1,12035e−4, 7,912e−9 y 7,915e−9 respectivamente. Las sumas absolutas de coeficientes de posición de los polinomios de corrección y los coeficientes de Bernstein del puente cubren el interior de todos los subintervalos.

## Carga física y presupuesto diferencial

Con w la perturbación compleja en el marco rotante y p su velocidad rotante, Q se descompone en la carga del fondo, √2‖√(4πW)f‖q y Q₂=2∫[Im(w* p)+ω|w|²]dV. Para la cargada, la deriva máxima de Q corregida fue 2,16e−10, mientras que |Q₂(s)−Q₂(0)| alcanzó 7,60e−8. La diferencia de Q₂ entre las referencias corregida y original llegó a 7,64e−11. En la gemela y la receptora la deriva máxima fue 1,91e−11 y 1,14e−11. La coordenada tangente reconstruida de ΔQ−ΔQ₂ concuerda con la proyección directa hasta 1,30e−14 en los tres casos. Se contrastó Q también con el medidor FV de M2. La carga total de la solución exacta se conserva por la pared cerrada; en la diferencia entre esa solución y la referencia aún aparece la diferencia de sus términos cuadráticos. El contraste por inventario es independiente de la estimación de q̇ y no asigna origen a un saldo en r60.

Se usó la energía rotante sin conmutador y el hueco publicado k=0,17. El vector de comparación contiene D, |q| y la fase común |β|, con desplazamiento S≤√(2/k)D+‖κ‖|q|+|β|. La ecuación de carga retiene el defecto de fase ‖Pu‖(D/√k+|β|), la fuerza proyectada y los dos defectos cinemáticos. La de D incluye la fuerza transversal, ‖κ‖C|q̇|, ‖Pu‖|β| y el defecto de posición en la norma del Hessiano. La fase incluye 2ωD/√k, |γq| y el defecto de posición. La proyección de la fuerza usa el mayorante de la componente imaginaria de la diferencia del resto. En la cargada su integral es 1,057e−9. Para la truncación formal de los polinomios, las integrales físicas de los defectos de posición y velocidad son menores que 1,43e−19 y 1,43e−17. Se conservaron las sensibilidades de discretización y muestreo de la [entrega anterior](../correccion_firmada_20261127/README.md). Las cifras se calcularon en doble precisión sin certificado de redondeo.

En toda la ventana se integró el sistema de comparación lineal. Para el no lineal se añadió a la fuerza y a su proyección el mayorante L S del jacobiano del resto en el recinto de la referencia corregida más el tubo de 1e−4. Los máximos de L fueron 0,465, 0,440 y 0,441 (redondeados hacia arriba). Se detuvo cada argumento condicional al primer extremo en que su conversión puntual superó la tolerancia.

## Contraste de conversión con el gradiente radial

Para cualquier campo canónico físico y que se anule en la pared, |yᵢ|² ≤ (Σⱼ≥ᵢ1/(4πcⱼ)) Σⱼ≥ᵢ4πcⱼ|Δyⱼ|². La resistencia máxima de la malla es 5,23568, con la última media celda incluida, y se verificó la igualdad para el perfil proporcional a la resistencia acumulada. La menor curvatura local de los bloques rotantes es −0,409172. La suma de los gradientes cuadrados de amplitud reducida y fase transversal está acotada por (1+0,409172/k)D², usando el hueco y la positividad de la actualización de rango uno. Se restituyen κq y uβ con sus máximos espaciales. Resulta una conversión puntual suficiente para todo el radio de 4,22344D+0,013451|q|+0,019101|β| (redondeo superior). La parte transversal admitiría por sí sola 2,36774e−5; incluso ese presupuesto queda por debajo de la fuente global de la cargada.

| Preparación | Cota puntual lineal a s=40 con traza | Primer extremo sin garantía no lineal, conversión original | Con traza |
|---|---:|---:|---:|
| Cargada | 6,152e−4 | 0,250 | 1,250 |
| Gemela | 4,807e−8 | 2,500 | 3,625 |
| Receptora | 4,817e−8 | 2,500 | 3,625 |

La traza mejora la conversión sin cambiar el tubo. En la cargada sigue pesando la cola; en los controles el presupuesto del término no lineal pierde resolución pese a que la parte lineal cabe. No hay evidencia de que los campos hayan salido físicamente del tubo. No se añadió una segunda corrección ni se lanzó evolución M2 completa.

**Siguiente iteración defendible.** Usar los valores absolutos por celda y la traza dependiente de r para acotar el multiplicador no lineal de la energía reducida por separado para D, κq y uβ. El actual L S combina el peor jacobiano en cualquier celda con el máximo desplazamiento global, incluso si están separados. Contrastar primero en gemela y receptora, donde la fuente lineal ya cabe. Para la cargada queda además pendiente acotar cómo el defecto exterior corregido alcanza la región de contacto; una mejora del multiplicador por sí sola no resolvería su cribado. Mantener explícitas las caras y la cola del propagador FV, la atribución conjunta en r60 y la entrega útil a la receptora. Siguen vigentes E≥1,66414371e−6 y Q≥1,84762579e−6.

**Resumen para el Dot principal.** Diego, sin ponderación exponencial la integral del mayorante del cambio de Taylor alcanza 1,12049e−4 en la cargada, casi toda en r≥160, frente a 2,36e−7 disponibles en el cribado original. Gemela y receptora pasan el cribado transversal. Ni la mejora de traza ni la conservación de Q total cierran la prueba no lineal hasta s=40. El piloto sigue sin habilitarse. [Informe en la rama](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/energia_fisica_corregida_20261127)

Desde este directorio ejecutar con OPENBLAS_NUM_THREADS=1 los programas auditar.py y traza.py. Comparar los dos JSON y el CSV regenerado con el CSV comprimido publicado.
