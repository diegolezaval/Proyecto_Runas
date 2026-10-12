# Referencia instantánea condicionada a Φ: diagnóstico pasivo

Se leerán únicamente fronteras independientes permanentemente recuperadas, desde τ32. Se empleará frozen_equilibrium del código CP11 original y sus tolerancias ya registradas (CG interno rtol=1e−12, residual elíptico 2e−10, identidad de fuerza 2e−12). Es una solución elíptica auxiliar, con cero pasos temporales M2; no sustituye el solver, estados ni observadores de las trayectorias en curso.

Para cada Φ físico guardado se define χ* como el mínimo único de la energía de χ a Φ fijado:

\[(M^2-L_h+h_{\rm M2}\rho)\chi_*=-g\rho,\quad
(M^2-L_h+h_{\rm M2}\rho)\dot\chi_*=-(g+h_{\rm M2}\chi_*)\dot\rho.\]

La positividad A≥M² del operador y la cuadratura positiva justifican esta referencia. No se supone que la evolución real sea estacionaria o adiabática. Se separará algebraicamente el defecto observado entre diferencia de referencias χ* y diferencia de residuos χ−χ*. Se conservarán productos cruzados: esas partes no son ortogonales ni canales causales nuevos. El residuo puede contener forzamiento no estacionario y no se denominará onda libre sin otra prueba.

Se usarán las ventanas originales de núcleo y k>4, incluyendo recorte suave, con el mismo producto de fases y escala. La proyección por encima de k=4 se calculará por complemento de la subautobase inferior del laplaciano original; su norma observada deberá reproducir la matriz guardada con la tolerancia Parseval original 2e−11. Se publicarán también alineación y retirada cuadrática de la respuesta Φ al canal de operador χ respecto del defecto Φ real, sin aplicar una puerta causal nueva a Φ.

Que χ* explique un defecto sería una descripción condicionada a los Φ que ya contienen la historia y su realimentación. No localizaría por sí sola la causa del error, no probaría eliminación del mediador, no alteraría M2, Θ, solver DOP853, tolerancias, observadores ni puerta del 2 %. Todo resultado negativo se conservará; CP12 continúa abierto.
