# Resultados de verificación

Validación de archivos, geometría exacta, algunos modelos reducidos y un sector radial. No valida realizaciones físicas, biología, un reactor ni correspondencia microscópica conjunta.

**Resultado:** 194/194 comprobaciones satisfactorias.

## Ensayo microscópico

| Magnitud | Resultado |
|---|---:|
| f0 | 0.74261594621 |
| Qhat | 2845.7469227 |
| Ehat | 2616.44350748 |
| E_over_Q | 0.919422414765 |
| virial_relative | 3.67153193298e-11 |
| solver_max_rms_residual | 9.90207583329e-09 |
| Cambio relativo de energía entre dominios | 1.30881052507e-07 |

No se fija una escala física m_r. No se ha probado estabilidad espectral completa.

## lamp

| Magnitud o supuesto | Resultado |
|---|---|
| incident_W | 20 |
| optical_W | 6 |
| heat_W | 8.70000500167 |
| export_W | 5.29999499833 |
| required_bus_W | 10.6600050017 |
| preparation_J | 39 |

## heater

| Magnitud o supuesto | Resultado |
|---|---|
| time_s | 1068.64720492 |
| input_J | 106864.720492 |
| stored_J | 83680 |
| loss_to_environment_J | 23184.7204918 |

## freezing

| Magnitud o supuesto | Resultado |
|---|---|
| heat_extracted_J | 417180 |
| minimum_work_J | 27410.1882566 |
| R1_work_ideal_terminals_J | 54820.3765132 |
| heat_rejected_J | 472000.376513 |
| entropy_generated_J_K | 93.5022625162 |

## reserve

| Magnitud o supuesto | Resultado |
|---|---|
| useful_J | 1000000 |
| structural_J | 50000 |
| max_power_W | 100000 |
| runtime_1kW_s | 979.759959594 |

## lifting

| Magnitud o supuesto | Resultado |
|---|---|
| gravity_J | 981 |
| actuator_input_J | 1090 |
| reserve_debit_J | 1112.24489796 |
| regenerated_J | 784.8 |
| net_cycle_loss_J | 327.444897959 |

## support

| Magnitud o supuesto | Resultado |
|---|---|
| stiffness_N_m | 10000 |
| max_force_N | 2000 |
| structural_J | 200000 |
| static_extension_m | 0.0981 |
| elastic_J | 48.11805 |
| hold_W | 2 |
| terminal_area_m2 | 0.00981 |
| conditional_wave_speed_m_s | 134071263.046 |

## controller

| Magnitud o supuesto | Resultado |
|---|---|
| duration_s | 1 |
| target_step_m | 0.05 |
| final_x_m | 0.0499750300386 |
| analytic_x_m | 0.0499750300386 |
| refinement_change_m | 1.72722947056e-13 |
| max_force_N | 1481 |
| scope | Sin ruido ni retardo de sensor mecánico; no prueba robustez ante todos los fallos. |

## solar_growth

| Magnitud o supuesto | Resultado |
|---|---|
| initial_area_m2 | 0.0025 |
| target_area_m2 | 1 |
| time_ideal_s | 1.50796590521 |
| assumption | Sustrato, soporte, sumidero y control salvo servicio Semilla preexistentes. |

## radiator

| Magnitud o supuesto | Resultado |
|---|---|
| net_W_m2 | 893.083970992 |
| area_per_collector_m2 | 0.226182538889 |

## channel

| Magnitud o supuesto | Resultado |
|---|---|
| delay_1km_s | 0.0001 |
| transmission_1km | 0.904837418036 |
| capacity_bound_bit_s | 6658211.48275 |

## logic

| Magnitud o supuesto | Resultado |
|---|---|
| landauer_J | 2.87097888508e-21 |
| single_bit_thermal_lifetime_s | 1.14200738982e+14 |

## photon_support_power_W

294096401298.0

## carbon

| Magnitud o supuesto | Resultado |
|---|---|
| amount_mol | 0.0832570144035 |
| air_m3_complete_capture | 4.84980111417 |
| minimum_work_J | 32835.6506536 |
| oxygen_kg | 0.00266405794688 |
| global_reversible_voltage_V | 1.0218884864 |

## Comprobaciones

| Prueba | Estado |
|---|---|
| 24 identidades únicas | Correcta |
| Contrato para cada glifo | Correcta |
| P-01 uniones racionales exactas | Correcta |
| P-01 extremos declarados | Correcta |
| P-01 puertos válidos | Correcta |
| P-01 sin superposición recta | Correcta |
| P-01 conectividad | Correcta |
| P-02 uniones racionales exactas | Correcta |
| P-02 extremos declarados | Correcta |
| P-02 puertos válidos | Correcta |
| P-02 sin superposición recta | Correcta |
| P-02 conectividad | Correcta |
| P-03 uniones racionales exactas | Correcta |
| P-03 extremos declarados | Correcta |
| P-03 puertos válidos | Correcta |
| P-03 sin superposición recta | Correcta |
| P-03 conectividad | Correcta |
| P-04 uniones racionales exactas | Correcta |
| P-04 extremos declarados | Correcta |
| P-04 puertos válidos | Correcta |
| P-04 sin superposición recta | Correcta |
| P-04 conectividad | Correcta |
| P-05 uniones racionales exactas | Correcta |
| P-05 extremos declarados | Correcta |
| P-05 puertos válidos | Correcta |
| P-05 sin superposición recta | Correcta |
| P-05 conectividad | Correcta |
| P-06 uniones racionales exactas | Correcta |
| P-06 extremos declarados | Correcta |
| P-06 puertos válidos | Correcta |
| P-06 sin superposición recta | Correcta |
| P-06 conectividad | Correcta |
| P-07 uniones racionales exactas | Correcta |
| P-07 extremos declarados | Correcta |
| P-07 puertos válidos | Correcta |
| P-07 sin superposición recta | Correcta |
| P-07 conectividad | Correcta |
| P-08 uniones racionales exactas | Correcta |
| P-08 extremos declarados | Correcta |
| P-08 puertos válidos | Correcta |
| P-08 sin superposición recta | Correcta |
| P-08 conectividad | Correcta |
| P-09 uniones racionales exactas | Correcta |
| P-09 extremos declarados | Correcta |
| P-09 puertos válidos | Correcta |
| P-09 sin superposición recta | Correcta |
| P-09 conectividad | Correcta |
| P-10 uniones racionales exactas | Correcta |
| P-10 extremos declarados | Correcta |
| P-10 puertos válidos | Correcta |
| P-10 sin superposición recta | Correcta |
| P-10 conectividad | Correcta |
| P-11 uniones racionales exactas | Correcta |
| P-11 extremos declarados | Correcta |
| P-11 puertos válidos | Correcta |
| P-11 sin superposición recta | Correcta |
| P-11 conectividad | Correcta |
| P-12 uniones racionales exactas | Correcta |
| P-12 extremos declarados | Correcta |
| P-12 puertos válidos | Correcta |
| P-12 sin superposición recta | Correcta |
| P-12 conectividad | Correcta |
| P-13 uniones racionales exactas | Correcta |
| P-13 extremos declarados | Correcta |
| P-13 puertos válidos | Correcta |
| P-13 sin superposición recta | Correcta |
| P-13 conectividad | Correcta |
| P-14 uniones racionales exactas | Correcta |
| P-14 extremos declarados | Correcta |
| P-14 puertos válidos | Correcta |
| P-14 sin superposición recta | Correcta |
| P-14 conectividad | Correcta |
| P-15 uniones racionales exactas | Correcta |
| P-15 extremos declarados | Correcta |
| P-15 puertos válidos | Correcta |
| P-15 sin superposición recta | Correcta |
| P-15 conectividad | Correcta |
| P-16 uniones racionales exactas | Correcta |
| P-16 extremos declarados | Correcta |
| P-16 puertos válidos | Correcta |
| P-16 sin superposición recta | Correcta |
| P-16 conectividad | Correcta |
| P-17 uniones racionales exactas | Correcta |
| P-17 extremos declarados | Correcta |
| P-17 puertos válidos | Correcta |
| P-17 sin superposición recta | Correcta |
| P-17 conectividad | Correcta |
| P-18 uniones racionales exactas | Correcta |
| P-18 extremos declarados | Correcta |
| P-18 puertos válidos | Correcta |
| P-18 sin superposición recta | Correcta |
| P-18 conectividad | Correcta |
| P-19 uniones racionales exactas | Correcta |
| P-19 extremos declarados | Correcta |
| P-19 puertos válidos | Correcta |
| P-19 sin superposición recta | Correcta |
| P-19 conectividad | Correcta |
| P-20 uniones racionales exactas | Correcta |
| P-20 extremos declarados | Correcta |
| P-20 puertos válidos | Correcta |
| P-20 sin superposición recta | Correcta |
| P-20 conectividad | Correcta |
| P-21 uniones racionales exactas | Correcta |
| P-21 extremos declarados | Correcta |
| P-21 puertos válidos | Correcta |
| P-21 sin superposición recta | Correcta |
| P-21 conectividad | Correcta |
| P-22 uniones racionales exactas | Correcta |
| P-22 extremos declarados | Correcta |
| P-22 puertos válidos | Correcta |
| P-22 sin superposición recta | Correcta |
| P-22 conectividad | Correcta |
| P-23 uniones racionales exactas | Correcta |
| P-23 extremos declarados | Correcta |
| P-23 puertos válidos | Correcta |
| P-23 sin superposición recta | Correcta |
| P-23 conectividad | Correcta |
| P-24 uniones racionales exactas | Correcta |
| P-24 extremos declarados | Correcta |
| P-24 puertos válidos | Correcta |
| P-24 sin superposición recta | Correcta |
| P-24 conectividad | Correcta |
| P-20 cinco piezas y dos ciclos | Correcta |
| Trazabilidad de 50 hallazgos | Correcta |
| Unidades y evidencia constants | Correcta |
| Unidades y evidencia seed | Correcta |
| Unidades y evidencia solar | Correcta |
| Unidades y evidencia power_channel | Correcta |
| Unidades y evidencia reserve | Correcta |
| Unidades y evidencia mechanical | Correcta |
| Unidades y evidencia thermal | Correcta |
| Unidades y evidencia logic | Correcta |
| Unidades y evidencia optical | Correcta |
| Unidades y evidencia acceptance | Correcta |
| Unidades y evidencia layout | Correcta |
| Unidades y evidencia lamp_case | Correcta |
| Unidades y evidencia control_case | Correcta |
| Unidades y evidencia vibration_case | Correcta |
| Unidades y evidencia chemistry_case | Correcta |
| P-01 referencias de parámetros | Correcta |
| P-02 referencias de parámetros | Correcta |
| P-03 referencias de parámetros | Correcta |
| P-04 referencias de parámetros | Correcta |
| P-05 referencias de parámetros | Correcta |
| P-06 referencias de parámetros | Correcta |
| P-07 referencias de parámetros | Correcta |
| P-08 referencias de parámetros | Correcta |
| P-09 referencias de parámetros | Correcta |
| P-10 referencias de parámetros | Correcta |
| P-11 referencias de parámetros | Correcta |
| P-12 referencias de parámetros | Correcta |
| P-13 referencias de parámetros | Correcta |
| P-14 referencias de parámetros | Correcta |
| P-15 referencias de parámetros | Correcta |
| P-16 referencias de parámetros | Correcta |
| P-17 referencias de parámetros | Correcta |
| P-18 referencias de parámetros | Correcta |
| P-19 referencias de parámetros | Correcta |
| P-20 referencias de parámetros | Correcta |
| P-21 referencias de parámetros | Correcta |
| P-22 referencias de parámetros | Correcta |
| P-23 referencias de parámetros | Correcta |
| P-24 referencias de parámetros | Correcta |
| R-LUZ autómata determinista | Correcta |
| R-LUZ módulos existentes | Correcta |
| R-LUZ recorrido normal | Correcta |
| R-LUZ recorrido de fallo | Correcta |
| R-SOPORTE autómata determinista | Correcta |
| R-SOPORTE módulos existentes | Correcta |
| R-SOPORTE recorrido normal | Correcta |
| R-SOPORTE recorrido de fallo | Correcta |
| R-TERMOSTATO autómata determinista | Correcta |
| R-TERMOSTATO módulos existentes | Correcta |
| R-TERMOSTATO recorrido normal | Correcta |
| R-TERMOSTATO recorrido de fallo | Correcta |
| R-CRECIMIENTO autómata determinista | Correcta |
| R-CRECIMIENTO módulos existentes | Correcta |
| R-CRECIMIENTO recorrido normal | Correcta |
| R-CRECIMIENTO recorrido de fallo | Correcta |
| Lámpara: balance externo energía | Correcta |
| Calefacción: energía y pérdidas integradas | Correcta |
| Congelación: primer y segundo principios | Correcta |
| Reserva: duración a 1 kW y no energía negativa | Correcta |
| Ciclo elevación: energía neta igual a pérdidas | Correcta |
| Soporte: carga y velocidad causal | Correcta |
| Control mecánico: convergencia y solución analítica | Correcta |
| Crecimiento a 1 m²: rama energética admisible | Correcta |
| Lógica: presupuesto de conmutación sobre Landauer | Correcta |
| Todos los JSON se pueden leer | Correcta |
| SVG XML íntegros | Correcta |
| Enlaces locales existentes | Correcta |
| Ensayo microscópico: dominio, residuo y virial | Correcta |
| Extensión microscópica: ensayos aprobados | Correcta |
| Correspondencia explícita de 24 primordiales | Correcta |
