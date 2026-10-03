# Parámetros de referencia

Perfil R1. Los valores adoptados son objetivos de diseño. Las constantes conservan su clasificación propia; no se infiere calibración por tener muchas cifras.

## constants

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| c | 2.99792e+08 | m/s | Velocidad de la luz | constante_SI_exacta |
| kB | 1.38065e-23 | J/K | Boltzmann | constante_SI_exacta |
| h | 6.62607e-34 | J s | Planck | constante_SI_exacta |
| sigmaSB | 5.67037e-08 | W/(m2 K4) | Stefan-Boltzmann | constante_derivada_SI |
| g | 9.81 | m/s2 | Gravedad del caso de laboratorio | hipotesis_del_caso |
| Rgas | 8.31446 | J/(mol K) | Constante molar de gases | constante_SI_redondeada |
| F | 96485.3 | C/mol | Faraday | constante_SI_redondeada |

## seed

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| prep_energy | 5 | J | Energia incorporada al estado inicial | objetivo_de_diseno_R1 |
| input_power | 2 | W | Potencia fisicamente transferida en el arranque de referencia | objetivo_de_diseno_R1 |
| hold_power | 0.05 | W | Mantenimiento durante y despues de preparar | objetivo_de_diseno_R1 |
| settle_time | 0.25 | s | Asentamiento tras alcanzar la energia preparada | objetivo_de_diseno_R1 |
| idle_energy | 5 | J | Energia retenida en la estructura de Semilla | objetivo_de_diseno_R1 |
| idle_power | 0.05 | W | Mantenimiento en espera | objetivo_de_diseno_R1 |

## solar

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| irradiance | 1000 | W/m2 | Iluminacion del ensayo | hipotesis_del_caso |
| efficiency | 0.8 | 1 | Conversion bruta de luz interceptada a bus antes de servicio local | objetivo_de_diseno_R1 |
| maintenance_area | 2 | W/m2 | Servicio propio del captador | objetivo_de_diseno_R1 |
| deployment_energy_area | 200 | J/m2 | Energia estructural de despliegue | objetivo_de_diseno_R1 |
| front_speed | 10 | m/s | Velocidad maxima de preparacion del borde | objetivo_de_diseno_R1 |
| starter_area | 0.0025 | m2 | Colector inicial de 5 cm por 5 cm | objetivo_de_diseno_R1 |

## power_channel

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| signal_speed | 1e+07 | m/s | Velocidad de transporte en la banda del perfil | objetivo_de_diseno_R1 |
| attenuation | 0.0001 | 1/m | Atenuacion de potencia, exponencial | objetivo_de_diseno_R1 |
| cross_section | 0.0001 | m2 | Seccion fisica del enlace de referencia | objetivo_de_diseno_R1 |
| power_flux_max | 1e+09 | W/m2 | Flujo de potencia admisible | objetivo_de_diseno_R1 |
| structural_energy_length | 1 | J/m | Energia de estructura del canal de potencia; no del soporte mecanico | objetivo_de_diseno_R1 |
| hold_power_length | 0.01 | W/m | Mantenimiento por longitud | objetivo_de_diseno_R1 |
| signal_bandwidth | 1e+06 | Hz | Banda equivalente de datos | objetivo_de_diseno_R1 |
| snr | 100 | 1 | Relacion senal a ruido del ensayo | objetivo_de_diseno_R1 |

## reserve

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| volume | 0.001 | m3 | Celda de un litro | objetivo_de_diseno_R1 |
| usable_density | 1e+09 | J/m3 | Energia coherente recuperable antes de perdidas de descarga | objetivo_de_diseno_R1 |
| structural_density | 5e+07 | J/m3 | Suelo estructural independiente de la carga util | objetivo_de_diseno_R1 |
| power_density | 1e+08 | W/m3 | Potencia maxima de cada sentido, no simultanea | objetivo_de_diseno_R1 |
| eta_charge | 0.98 | 1 | Rendimiento de carga desde terminal | objetivo_de_diseno_R1 |
| eta_discharge | 0.98 | 1 | Rendimiento a terminal | objetivo_de_diseno_R1 |
| leak_rate | 1e-07 | 1/s | Fuga proporcional de energia util | objetivo_de_diseno_R1 |
| idle_power | 0.2 | W | Servicio de celda no incluido en la fuga | objetivo_de_diseno_R1 |
| recover_structure | 0.9 | 1 | Fraccion de energia estructural recuperada en desmontaje ordenado | objetivo_de_diseno_R1 |

## mechanical

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| structural_density | 1e+09 | J/m3 | Densidad energetica del soporte mecanico | objetivo_de_diseno_R1 |
| young_modulus | 2e+08 | Pa | Modulo longitudinal del estado de soporte | objetivo_de_diseno_R1 |
| max_strain | 0.1 | 1 | Deformacion elastica longitudinal maxima del perfil | objetivo_de_diseno_R1 |
| cross_section | 0.0001 | m2 | Seccion del elemento de referencia | objetivo_de_diseno_R1 |
| length | 2 | m | Longitud del elemento de referencia | objetivo_de_diseno_R1 |
| mechanical_efficiency | 0.9 | 1 | Conversion de bus a trabajo mecanico | objetivo_de_diseno_R1 |
| regen_efficiency | 0.8 | 1 | Trabajo mecanico a energia util de reserva, global | objetivo_de_diseno_R1 |
| hold_fraction | 1e-05 | 1/s | Perdida de energia estructural compensada | objetivo_de_diseno_R1 |
| surface_pressure_max | 100000 | Pa | Objetivo de presion en terminal material comun; no limite de tejido vivo | objetivo_de_diseno_R1 |

## thermal

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| carnot_fraction | 0.5 | 1 | COP_real / COP_Carnot para el ciclo de referencia | objetivo_de_diseno_R1 |
| radiator_temperature | 400 | K | Temperatura del caso de radiador | objetivo_de_diseno_R1 |
| ambient_temperature | 300 | K | Entorno radiativo uniforme | objetivo_de_diseno_R1 |
| emissivity | 0.9 | 1 | Emisividad hemisferica del caso | objetivo_de_diseno_R1 |
| water_cp | 4184 | J/(kg K) | Aproximacion cerca del ambiente | aproximacion_material_del_caso |
| water_latent_fusion | 333500 | J/kg | Calor latente del caso | aproximacion_material_del_caso |
| interface_conductance | 100 | W/K | Conductancia por terminal del ejemplo | objetivo_de_diseno_R1 |

## logic

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| temperature | 300 | K | Temperatura del baño de referencia | objetivo_de_diseno_R1 |
| barrier_kBT | 60 | 1 | Barrera libre en unidades kBT | objetivo_de_diseno_R1 |
| attempt_time | 1e-12 | s | Prefactor termico del ejemplo | objetivo_de_diseno_R1 |
| density_bits | 1e+15 | bit/m3 | Capacidad bruta de memoria | objetivo_de_diseno_R1 |
| switch_energy | 1e-17 | J | Presupuesto de conmutacion de referencia | objetivo_de_diseno_R1 |
| clock_frequency | 1e+06 | Hz | Reloj local de referencia | objetivo_de_diseno_R1 |
| control_period | 0.001 | s | Periodo del controlador de servicio | objetivo_de_diseno_R1 |
| ecc_block_bits | 7 | bit | Bloque ilustrativo de codigo (7,4) | objetivo_de_diseno_R1 |
| ecc_data_bits | 4 | bit | Datos utiles por bloque | objetivo_de_diseno_R1 |
| scrub_interval | 1 | s | Intervalo ilustrativo de lectura y correccion | objetivo_de_diseno_R1 |

## optical

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| efficiency | 0.6 | 1 | Rendimiento en banda util del emisor | objetivo_de_diseno_R1 |
| wavelength | 5.5e-07 | m | Longitud de onda del ejemplo | objetivo_de_diseno_R1 |
| aperture_diameter | 0.02 | m | Apertura efectiva circular del ejemplo | objetivo_de_diseno_R1 |

## acceptance

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| geometry_join_tolerance | 1e-09 | u | Tolerancia del verificador numerico tras datos racionales | objetivo_de_diseno_R1 |
| numerical_relative_tolerance | 1e-06 | 1 | Balance algebraico de ensayos simples | objetivo_de_diseno_R1 |
| deployed_position_tolerance | 0.001 | m | Error de seguimiento del caso macromecanico con control dimensionado | objetivo_de_diseno_R1 |
| nominal_temperature_error | 0.2 | K | Banda de servicio del termostato | objetivo_de_diseno_R1 |
| passive_crosstalk_power | 1e-06 | 1 | Potencia transferida a ruta ajena / potencia incidente, banda y carga nominales | objetivo_de_diseno_R1 |

## layout

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| unit_length | 0.01 | m/u | Longitud de unidad gráfica | objetivo_de_diseno_R1 |
| core_radius | 0.0001 | m | Radio objetivo de núcleo modal | objetivo_de_diseno_R1 |
| bend_radius_min | 0.0005 | m | Radio mínimo de redondeo | objetivo_de_diseno_R1 |
| crossing_layer_gap | 0.001 | m | Separación de capas de cruce | objetivo_de_diseno_R1 |

## lamp_case

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| optical_power | 6 | W | Consigna óptica | objetivo_de_diseno_R1 |
| channel_length | 10 | m | Longitud de Canal | objetivo_de_diseno_R1 |
| collector_area | 0.02 | m2 | Área de captación | objetivo_de_diseno_R1 |
| aux_power | 0.5 | W | Control y terminales del ejemplo | objetivo_de_diseno_R1 |
| aux_preparation_energy | 20 | J | Preparación de emisor, control y terminales sobre soporte existente | objetivo_de_diseno_R1 |

## control_case

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| mass | 100 | kg | Carga de referencia | objetivo_de_diseno_R1 |
| height | 1 | m | Elevación de referencia | objetivo_de_diseno_R1 |
| natural_frequency | 10 | 1/s | Frecuencia natural angular de lazo | objetivo_de_diseno_R1 |
| damping_ratio | 1 | 1 | Amortiguamiento relativo | objetivo_de_diseno_R1 |
| sensor_time_constant | 0.01 | s | Transductor termométrico | objetivo_de_diseno_R1 |
| sensor_temperature_uncertainty | 0.05 | K | Incertidumbre del caso | objetivo_de_diseno_R1 |
| thermostat_hysteresis | 0.1 | K | Semiancho de histéresis | objetivo_de_diseno_R1 |
| heater_power | 100 | W | Potencia del calentador | objetivo_de_diseno_R1 |
| water_mass | 1 | kg | Masa de agua del caso | objetivo_de_diseno_R1 |
| thermal_loss_conductance | 2 | W/K | Pérdidas hacia entorno | objetivo_de_diseno_R1 |
| initial_temperature | 293.15 | K | Temperatura inicial | objetivo_de_diseno_R1 |
| target_temperature | 313.15 | K | Consigna térmica | objetivo_de_diseno_R1 |

## vibration_case

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| mass | 0.01 | kg | Masa modal | objetivo_de_diseno_R1 |
| frequency | 100 | Hz | Frecuencia modal | objetivo_de_diseno_R1 |
| damping_ratio | 0.05 | 1 | Amortiguamiento relativo | objetivo_de_diseno_R1 |
| amplitude | 0.0001 | m | Amplitud máxima del ejemplo | objetivo_de_diseno_R1 |

## chemistry_case

| Parámetro | Valor | Unidad | Significado | Estado |
|---|---:|---|---|---|
| carbon_mass | 0.001 | kg | Carbono del balance | objetivo_de_diseno_R1 |
| carbon_molar_mass | 0.012011 | kg/mol | Masa molar adoptada | objetivo_de_diseno_R1 |
| oxygen_molar_mass | 0.031998 | kg/mol | Oxígeno molecular | objetivo_de_diseno_R1 |
| co2_fraction | 0.00042 | 1 | Fracción molar del aire del ejemplo | objetivo_de_diseno_R1 |
| temperature | 298.15 | K | Temperatura del caso | objetivo_de_diseno_R1 |
| pressure | 101325 | Pa | Presión del caso | objetivo_de_diseno_R1 |
| decomposition_gibbs | 394389 | J/mol | CO2 gas a grafito y O2 gas; JANAF 298.15 K | dato_termoquimico |
| decomposition_enthalpy | 393522 | J/mol | Mismos estados y temperatura | dato_termoquimico |

