# Diccionario de Datos — Experimentos de Factorización de Semiprimos

Este directorio contiene todos los resultados experimentales generados durante el proyecto.
Los datos abarcan desde experimentos de simulación local hasta ejecuciones reales en hardware cuántico IBM.

**Total de registros:** ~77,360 filas en 34 archivos CSV

---

## Índice de carpetas

| Carpeta | Etapa | Tipo | Registros | Recomendación |
|---------|-------|------|-----------|---------------|
| [`0.0_beta.algoritmo_simulado/`](#00_beta) | Beta — validación inicial | Simulado (clásico) | ~24,200 | Histórico |
| [`0.1_ibm_algoritmo/`](#01_ibm) | IBM Hardware Real | **Cuántico real QPU** ⭐ | ~900 | **Principal** |
| [`1.gdc_luck_algoritmo_uno/`](#1_gcd) | Iteración 1 — GCD Luck | Simulado | 5,500 | Histórico |
| [`2.algorirmo_dos/`](#2_v2) | Iteración 2 | Simulado + cuántico | 10,250 | Histórico |
| [`3.primer_exito_algoritmo_tres/`](#3_exito) | Iteración 3 — Primer éxito | Simulado + cuántico | 3,120 | Histórico |
| [`4.algoritmo_optimizado_4-17 bits/`](#4_opt) | Iteración 4 — Optimizado | Simulado + cuántico | 10,200 | Histórico |
| [`5.aislar_cuantico_de_parte_clasica/`](#5_final) | Experimento final | Simulado + cuántico | 22,470 | **Principal** ⭐ |

---

## Descripción detallada por carpeta

---

### `0.0_beta.algoritmo_simulado/` {#00_beta}

**Etapa:** Beta — primera validación del pipeline de datos  
**Tipo:** Simulación clásica (sin circuitos cuánticos reales)  
**Recomendación:** Histórico — muestra el punto de partida del proyecto

**Archivos:**

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `batch_01.csv` … `batch_09.csv` | 2,200 c/u | Batches independientes de experimentos beta |
| `batch_09_all.csv` | 2,200 | Concatenación completa del batch 9 |
| `batch_09_classical.csv` | 200 | Filtrado: solo ejecuciones clásicas del batch 9 |
| `batch_09_quantum.csv` | 2,000 | Filtrado: solo ejecuciones cuánticas del batch 9 |

**Esquema de columnas:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `batch_id` | int | Identificador del batch |
| `run_id` | int | Identificador único del experimento |
| `algo` | str | Algoritmo usado: `classical` |
| `N` | int | Número semiprimo a factorizar |
| `N_bits` | int | Tamaño en bits de N |
| `M` | int | Número de shots del circuito |
| `rep` | int | Índice de repetición |
| `success` | bool | `True` si se factorizó correctamente |
| `time_sec` | float | Tiempo de ejecución (segundos) |
| `factors` | str | Factores encontrados (ej: `[3, 5]`) |
| `status` | str | Estado del experimento |
| `seed` | int | Semilla aleatoria para reproducibilidad |

> **Nota:** Esta versión beta **no incluye columnas de hardware IBM** (`hw_backend`, `job_id`). Es la versión preliminar antes de integrar el backend real.

---

### `0.1_ibm_algoritmo/` {#01_ibm}

> ⭐ **DATASET PRINCIPAL — Hardware cuántico real**

**Etapa:** Ejecución en IBM Quantum hardware (QPU real)  
**Tipo:** Cuántico real — backend `ibm_fez` (156 qubits)  
**Recomendación:** **Principal** — único conjunto con tiempos reales de QPU y job IDs verificables

**Archivos:**

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `batch_01_all.csv` | 260 | Batch 1 completo (clásico + cuántico) |
| `batch_01_classical.csv` | 200 | Batch 1 — solo ejecuciones clásicas (Pollard's Rho) |
| `batch_01_quantum.csv` | 60 | Batch 1 — solo ejecuciones en IBM QPU |
| `batch_04_all.csv` | 260 | Batch 4 completo |
| `batch_04_classical.csv` | 200 | Batch 4 — clásico |
| `batch_04_quantum.csv` | 60 | Batch 4 — IBM QPU |
| `batch_05_all.csv` | 260 | Batch 5 completo |
| `batch_05_classical.csv` | 200 | Batch 5 — clásico |
| `batch_05_quantum.csv` | 60 | Batch 5 — IBM QPU |
| `batch_09_quantum.csv` | 60 | Batch 9 — IBM QPU |

**Esquema de columnas (extiende el esquema beta con columnas de hardware):**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `batch_id` | int | Identificador del batch |
| `run_id` | int | ID único del experimento |
| `algo` | str | `classical` o `quantum` |
| `N` | int | Número semiprimo a factorizar |
| `N_bits` | int | Tamaño en bits de N |
| `M` | int | Shots del circuito cuántico |
| `rep` | int | Repetición del experimento |
| `success` | bool | `True` si factorización exitosa |
| `time_sec` | float | Tiempo total incluyendo cola IBM |
| `factors` | str | Factores encontrados |
| `status` | str | `OK_QUANTUM_HARDWARE` / `INSUFFICIENT_COHERENCE` |
| `seed` | float | Semilla aleatoria |
| `hw_backend` | str | ⭐ Backend IBM usado (ej: `ibm_fez`) |
| `hw_qubits` | float | ⭐ Qubits del circuito compilado en el QPU |
| `quantum_seconds` | float | ⭐ Tiempo real de ejecución en QPU (sin cola ni compilación) |
| `job_id` | str | ⭐ ID verificable en IBM Quantum Dashboard |

**Muestra real de datos:**
```
N=2773 (12 bits) | backend=ibm_fez | qubits=156 | quantum_sec=4.72 | job_id=d5ltp69h2mqc739a8dig
```

> **Valor académico:** Los `job_id` permiten verificar independientemente cada ejecución en [quantum.ibm.com](https://quantum.ibm.com). El campo `quantum_seconds` aísla el tiempo real de computación cuántica de la latencia de red y cola.

---

### `1.gdc_luck_algoritmo_uno/` {#1_gcd}

**Etapa:** Iteración 1 — primera implementación con método GCD Luck  
**Tipo:** Simulado local (Qiskit Aer)  
**Recomendación:** Histórico — sirve como baseline de comparación

**Archivos:**

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `shor_experiment.csv` | 5,500 | Experimentos con método `gcd_luck` |
| `analysis_plots.png` | — | Visualización de distribuciones |
| `cumulative_probability.png` | — | Probabilidad acumulada de éxito |

**Esquema de columnas:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `n_bits` | int | Tamaño en bits del número N |
| `N` | int | Número semiprimo |
| `p_true` | int | Factor primo real p (ground truth) |
| `q_true` | int | Factor primo real q (ground truth) |
| `M_shots` | int | Shots del circuito |
| `rep` | int | Repetición |
| `success` | int | 1=éxito, 0=fallo |
| `attempts` | int | Intentos necesarios para factorizar |
| `time_sec` | float | Tiempo de ejecución |
| `qubits_used` | int | Qubits utilizados |
| `method` | str | `gcd_luck` |
| `factors_found` | str | Factores encontrados |

> **Diferencia con versiones posteriores:** Este esquema tiene `qubits_used` y `factors_found` en lugar de `qubits` y sin columna `is_quantum`.

---

### `2.algorirmo_dos/` {#2_v2}

**Etapa:** Iteración 2 — introducción del campo `is_quantum`  
**Tipo:** Simulado local — comienza a distinguir rutas clásica vs cuántica  
**Recomendación:** Histórico

**Archivos:**

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `shor_experiment_v2.csv` | 10,250 | Experimentos con distinción clásico/cuántico |
| `cumulative_quantum.png` | — | Probabilidad acumulada cuántica |
| `distributions_v2.png` | — | Distribuciones por n_bits |

**Esquema:** Ver **Esquema A** (sección final de este documento).

---

### `3.primer_exito_algoritmo_tres/` {#3_exito}

**Etapa:** Iteración 3 — primer experimento con separación exitosa cuántico/clásico  
**Tipo:** Simulado local  
**Recomendación:** Histórico — hito investigativo relevante

**Archivos:**

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `shor_experiment_v2.csv` | 3,120 | Dataset reducido del hito de éxito |
| `cumulative_quantum.png` | — | Probabilidad acumulada |
| `distributions_v2.png` | — | Distribuciones |

**Esquema:** Ver **Esquema A**.

---

### `4.algoritmo_optimizado_4-17 bits/` {#4_opt}

**Etapa:** Iteración 4 — algoritmo optimizado con rango ampliado (4–17 bits)  
**Tipo:** Simulado local  
**Recomendación:** Histórico — muestra la progresión del rango experimental

**Archivos:**

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `shor_experiment_v2.csv` | 10,200 | Cobertura 4–17 bits |
| `cumulative_quantum.png` | — | Probabilidad acumulada |
| `distributions_v2.png` | — | Distribuciones por n_bits |
| `quantum_analysis.png` | — | Análisis cuántico detallado |

**Esquema:** Ver **Esquema A**.

---

### `5.aislar_cuantico_de_parte_clasica/` {#5_final}

> ⭐ **DATASET PRINCIPAL — Experimento final más completo**

**Etapa:** Experimento definitivo — aislamiento de la parte cuántica pura  
**Tipo:** Simulado local — separación metodológica estricta clásico vs cuántico  
**Recomendación:** **Principal** — dataset de referencia para todos los análisis y visualizaciones

**Archivos:**

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `shor_experiment_v2.csv` | **22,470** | ⭐ Dataset completo y definitivo |
| `cumulative_quantum.png` | — | Probabilidad acumulada cuántica |
| `distributions_v2.png` | — | Distribuciones por n_bits |
| `force_quantum_analysis.png` | — | Análisis forzando ruta cuántica |
| `quantum_analysis.png` | — | Análisis cuántico general |
| `risk_dashboard_final.png` | — | Dashboard de riesgo vs éxito |
| `shots_efficiency.png` | — | Eficiencia de shots por n_bits |

**Muestra real de datos:**
```
n_bits=4, N=15, p_true=3, q_true=5, M_shots=50, success=1, is_quantum=1,
method=quantum_success, attempts=2, time_sec=0.091, qubits=12
```

**Esquema:** Ver **Esquema A** (sección siguiente).

---

## Esquemas de columnas de referencia

### Esquema A — `shor_experiment_v2.csv`
Usado en carpetas: `2.algorirmo_dos`, `3.primer_exito_algoritmo_tres`, `4.algoritmo_optimizado_4-17 bits`, `5.aislar_cuantico_de_parte_clasica`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `n_bits` | int | Tamaño en bits del número N |
| `N` | int | Número semiprimo a factorizar |
| `p_true` | int | Factor primo real p (ground truth) |
| `q_true` | int | Factor primo real q (ground truth) |
| `M_shots` | int | Número de shots del circuito cuántico |
| `rep` | int | Índice de repetición del experimento |
| `success` | int | 1=factorización exitosa, 0=fallo |
| `is_quantum` | int | 1=circuito cuántico real, 0=ruta clásica |
| `method` | str | `quantum_success`, `gcd_luck`, `failed` |
| `attempts` | int | Intentos necesarios para factorizar |
| `time_sec` | float | Tiempo total de ejecución (segundos) |
| `qubits` | int | Qubits utilizados en el circuito |

### Esquema B — `batch_*_quantum.csv` (IBM Hardware)
Usado en: `0.1_ibm_algoritmo/`

Ver tabla completa en la sección [`0.1_ibm_algoritmo/`](#01_ibm).

### Esquema C — `batch_*.csv` (Beta simulada)
Usado en: `0.0_beta.algoritmo_simulado/`

Ver tabla completa en la sección [`0.0_beta.algoritmo_simulado/`](#00_beta).

---

## Notas de reproducibilidad

- Todos los experimentos simulados usan **Qiskit Aer** como backend local.
- Los experimentos IBM usan **`qiskit-ibm-runtime` con SamplerV2**.
- El campo `seed` garantiza reproducibilidad para los experimentos clásicos.
- Los experimentos cuánticos reales (IBM) no son 100% reproducibles por naturaleza estocástica del QPU, pero son **verificables** mediante `job_id` en [quantum.ibm.com](https://quantum.ibm.com).
- Para reproducir el experimento final, ver [`../docs/guia_ibm_quantum.md`](../docs/guia_ibm_quantum.md).

---

*Última actualización: 2026-05-13*
