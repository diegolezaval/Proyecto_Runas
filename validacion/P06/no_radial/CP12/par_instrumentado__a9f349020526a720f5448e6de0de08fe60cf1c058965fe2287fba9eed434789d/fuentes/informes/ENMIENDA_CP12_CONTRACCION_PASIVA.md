# CP12 · Contracción exacta del Jacobiano angular pasivo

El control positivo `991469c2b8e28bf9af3170caa2dcf544e95e7bf4bd9f82c8c3819a580a9baedc` se conserva íntegro. La simetría pasó en ambos estados CP10; ninguna evolución nueva se ha iniciado. Su tiempo pasivo fue 1.69 s, dominado por evaluar repetidamente el Jacobiano en direcciones angulares durante la iteración de etapas.

En la base de seis funciones `Z=YᵀS`, se precalcula a cada nodo temporal cada matriz `Jᵃᵇᵢⱼ(r)=ΣΩ wΩ Zᵢ(Ω) Jᵃᵇ(r,Ω) Zⱼ(Ω)`. Es exactamente la misma cuadratura de 180 direcciones, sin bajar su orden ni aproximar el Jacobiano en tiempo. Cada iteración aplica después estas matrices 6×6 a los cinco canales. No cambia la matemática de las etapas Gauss ni sus criterios. La equivalencia con la acción de 25 modos se exige a 2e−12 antes de M2. No se usa el Jacobiano pasivo en el RHS físico.

Esta operación elimina trabajo algebraico repetido y reduce memoria; no prueba una corrección científica ni cambia modelo, configuración, semilla, solver o puerta.
