# 📊 Análisis de Resultados: CPU vs QPU

Este documento explica cómo interpretar los datos generados por la ejecución refactorizada.

---

## 📁 Archivos Generados

Después de ejecutar `run_batch(batch_id, semiprimes)`, se generan 3 archivos CSV:

```
datasets/
├── batch_01_classical.csv       # Datos del algoritmo clásico (CPU)
├── batch_01_quantum.csv         # Datos del algoritmo cuántico (QPU)
└── batch_01_all.csv             # Combinación de ambos
```

---

## 📋 Estructura del CSV Cuántico

### Ejemplo de fila:
```csv
batch_id,run_id,algo,N,N_bits,M,rep,success,time_sec,factors,status,seed,hw_backend,hw_qubits,quantum_seconds,job_id
1,156,quantum,21,5,100,1,1,0.2345,"[3, 7]",OK_QUANTUM_HARDWARE,100111101,ibm_brisbane_127_0,5,0.0234,cwd9y9n20ks600093ng0
```

### Significado de cada columna:

| Columna | Significado | Ejemplo |
|---------|-------------|---------|
| `batch_id` | ID del lote | 1 |
| `run_id` | Identificador único de la ejecución | 156 |
| `algo` | Algoritmo utilizado | `quantum` |
| `N` | Número a factorizar | 21 |
| `N_bits` | Número de bits de N | 5 |
| `M` | Número de shots (mediciones) | 100 |
| `rep` | Repetición dentro de este (N, M) | 1 |
| `success` | 1=encontró factores, 0=no encontró | 1 |
| `time_sec` | Tiempo TOTAL de ejecución (incluyendo compilación) | 0.2345 s |
| `factors` | Factores encontrados | `[3, 7]` |
| `status` | Estado de la ejecución | `OK_QUANTUM_HARDWARE` |
| `seed` | Semilla para reproducibilidad | 100111101 |
| **`hw_backend`** | **Nombre del QPU utilizado** | **ibm_brisbane_127_0** |
| **`hw_qubits`** | **Qubits utilizados en el circuito compilado** | **5** |
| **`quantum_seconds`** | **TIEMPO REAL de ejecución en QPU (sin cola)** | **0.0234 s** |
| **`job_id`** | **ID único del job en IBM** | **cwd9y9n20ks600093ng0** |

---

## 🔍 Columnas Clave para Análisis

### **`quantum_seconds`** ⭐⭐⭐
- **Más importante para benchmarking**
- Tiempo REAL de ejecución en el procesador cuántico
- **NO incluye tiempo de cola o compilación**
- Comparable con tiempo CPU

**Uso:**
```python
import pandas as pd

df = pd.read_csv("datasets/batch_01_quantum.csv")

# Tiempo promedio en QPU
avg_qpu_time = df[df["status"] == "OK_QUANTUM_HARDWARE"]["quantum_seconds"].mean()
print(f"Tiempo promedio en QPU: {avg_qpu_time:.6f} s")

# Tiempo mínimo y máximo
print(f"Min: {df['quantum_seconds'].min():.6f} s")
print(f"Max: {df['quantum_seconds'].max():.6f} s")
```

---

### **`time_sec`**
- Tiempo TOTAL desde inicio hasta fin
- Incluye:
  - Creación del circuito
  - Transpilación a ISA (compilación)
  - Tiempo de espera en cola
  - Ejecución real (`quantum_seconds`)
  - Post-procesamiento

**Relación:**
```
time_sec = compilation_time + queue_time + quantum_seconds + postprocess_time
```

**Uso para análisis completo:**
```python
# Diferencia entre tiempo total y tiempo QPU real
overhead_time = df["time_sec"] - df["quantum_seconds"]
print(f"Overhead promedio: {overhead_time.mean():.6f} s")
```

---

### **`hw_backend`**
- Nombre del procesador cuántico utilizado
- Ejemplo: `ibm_brisbane_127_0`
  - `ibm_brisbane`: Nombre del backend
  - `127`: Número de qubits
  - `_0`: Versión

**Uso para ver qué backend se usó:**
```python
# Agrupar por backend
by_backend = df.groupby("hw_backend").agg({
    "success": "mean",
    "quantum_seconds": "mean",
    "N": "count"
})
print(by_backend)
```

---

### **`hw_qubits`**
- Número de qubits utilizados en el circuito **después de transpilación**
- Puede ser diferente al circuito original
- Refleja optimización del compilador

**Uso para ver la compilación:**
```python
# Comparar qubits antes y después
print(f"Qubits en circuito original: 5")
print(f"Qubits en circuito compilado (promedio): {df['hw_qubits'].mean()}")
```

---

### **`job_id`**
- ID único del job en IBM Quantum
- Permite rastrear la ejecución exacta en el Dashboard de IBM

**Uso para debugging:**
```python
# Si una ejecución falló, obtener el job ID
failed_jobs = df[df["status"] != "OK_QUANTUM_HARDWARE"]
for job_id in failed_jobs["job_id"].head(3):
    print(f"Revisar job en: https://quantum.ibm.com/jobs/{job_id}")
```

---

## 📊 Análisis: CPU vs QPU

### Comparación Básica

```python
import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos
df_cpu = pd.read_csv("datasets/batch_01_classical.csv")
df_gpu = pd.read_csv("datasets/batch_01_quantum.csv")

# Tiempos promedios
cpu_avg = df_cpu["time_sec"].mean()
qpu_avg = df_gpu[df_gpu["status"] == "OK_QUANTUM_HARDWARE"]["quantum_seconds"].mean()

print(f"CPU (promedio):       {cpu_avg:.6f} s")
print(f"QPU (promedio):       {qpu_avg:.6f} s")
print(f"Speedup (QPU/CPU):    {cpu_avg / qpu_avg:.2f}x")

# Si speedup > 1: QPU es más rápido
# Si speedup < 1: CPU es más rápido (esperado para este problema en pequeña escala)
```

### Gráficas Comparativas

```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Distribución de tiempos
axes[0, 0].hist(df_cpu["time_sec"], bins=20, alpha=0.7, label="CPU", color="blue")
axes[0, 0].hist(df_gpu["quantum_seconds"], bins=20, alpha=0.7, label="QPU", color="red")
axes[0, 0].set_xlabel("Tiempo (segundos)")
axes[0, 0].set_ylabel("Frecuencia")
axes[0, 0].set_title("Distribución de Tiempos de Ejecución")
axes[0, 0].legend()
axes[0, 0].set_yscale("log")

# 2. Tasa de éxito
cpu_success = df_cpu["success"].mean()
qpu_success = df_gpu[df_gpu["status"] == "OK_QUANTUM_HARDWARE"]["success"].mean()

axes[0, 1].bar(["CPU", "QPU"], [cpu_success, qpu_success], color=["blue", "red"])
axes[0, 1].set_ylabel("Tasa de Éxito (%)")
axes[0, 1].set_ylim(0, 1)
axes[0, 1].set_title("Tasa de Éxito: CPU vs QPU")
for i, v in enumerate([cpu_success, qpu_success]):
    axes[0, 1].text(i, v + 0.02, f"{v:.1%}", ha="center")

# 3. Tiempo vs Tamaño de N
cpu_by_n = df_cpu.groupby("N")["time_sec"].mean()
qpu_by_n = df_gpu[df_gpu["status"] == "OK_QUANTUM_HARDWARE"].groupby("N")["quantum_seconds"].mean()

axes[1, 0].plot(cpu_by_n.index, cpu_by_n.values, marker="o", label="CPU", color="blue")
axes[1, 0].plot(qpu_by_n.index, qpu_by_n.values, marker="s", label="QPU", color="red")
axes[1, 0].set_xlabel("N (número a factorizar)")
axes[1, 0].set_ylabel("Tiempo (segundos)")
axes[1, 0].set_title("Tiempo de Ejecución vs Tamaño de N")
axes[1, 0].legend()
axes[1, 0].grid(True)

# 4. Overhead: Compilación vs Ejecución Real
overhead = df_gpu["time_sec"] - df_gpu["quantum_seconds"]
axes[1, 1].hist(overhead, bins=20, color="green", alpha=0.7)
axes[1, 1].set_xlabel("Overhead (segundos)")
axes[1, 1].set_ylabel("Frecuencia")
axes[1, 1].set_title("Overhead: Compilación + Cola + Post-procesamiento")
axes[1, 1].axvline(overhead.mean(), color="red", linestyle="--", label=f"Promedio: {overhead.mean():.6f}s")
axes[1, 1].legend()

plt.tight_layout()
plt.show()
```

---

## 📈 Tabla de Estadísticas

```python
import pandas as pd

df_cpu = pd.read_csv("datasets/batch_01_classical.csv")
df_qpu = pd.read_csv("datasets/batch_01_quantum.csv")

# Filtrar solo QPU exitosas
df_qpu_ok = df_qpu[df_qpu["status"] == "OK_QUANTUM_HARDWARE"]

stats = pd.DataFrame({
    "Métrica": [
        "N total de ejecuciones",
        "Ejecuciones exitosas",
        "Tasa de éxito (%)",
        "Tiempo promedio (s)",
        "Tiempo mínimo (s)",
        "Tiempo máximo (s)",
        "Desviación estándar (s)",
        "Mediana (s)"
    ],
    "CPU": [
        len(df_cpu),
        df_cpu["success"].sum(),
        f"{df_cpu['success'].mean():.1%}",
        f"{df_cpu['time_sec'].mean():.6f}",
        f"{df_cpu['time_sec'].min():.6f}",
        f"{df_cpu['time_sec'].max():.6f}",
        f"{df_cpu['time_sec'].std():.6f}",
        f"{df_cpu['time_sec'].median():.6f}"
    ],
    "QPU": [
        len(df_qpu_ok),
        df_qpu_ok["success"].sum(),
        f"{df_qpu_ok['success'].mean():.1%}",
        f"{df_qpu_ok['quantum_seconds'].mean():.6f}",
        f"{df_qpu_ok['quantum_seconds'].min():.6f}",
        f"{df_qpu_ok['quantum_seconds'].max():.6f}",
        f"{df_qpu_ok['quantum_seconds'].std():.6f}",
        f"{df_qpu_ok['quantum_seconds'].median():.6f}"
    ]
})

print(stats.to_string(index=False))
```

---

## 🔍 Estados Posibles de Ejecución

### Estados de Éxito

| Estado | Significado | Acción |
|--------|-------------|--------|
| `OK_QUANTUM_HARDWARE` | ✅ Ejecución exitosa en QPU | Usar para análisis |
| `OK` | ✅ Ejecución clásica exitosa | Datos validos |

### Estados de Fallo

| Estado | Significado | Solución |
|--------|-------------|----------|
| `SKIPPED_TOO_LARGE` | N demasiado grande | Reduce tamaño de N |
| `NO_FACTORS_EXTRACTED` | No se extrajeron factores | Error de algoritmo |
| `INSUFFICIENT_COHERENCE` | Ruido en QPU | Aumenta calidad de compilación |
| `HW_ERROR_...` | Error de hardware | Espera a que se recupere |
| `FALLBACK_CLASSICAL` | QPU no disponible | Usa resultados de CPU |

---

## 💡 Interpretación de Resultados Típicos

### Escenario A: QPU Mucho Más Lenta
```
CPU promedio:    0.001 s
QPU promedio:    0.5 s
Speedup:         0.002x (QPU es 500x más lenta)

Razones esperadas:
- Problemas pequeños: overhead > beneficio cuántico
- Compilación a ISA toma tiempo
- Tiempo de cola en el hardware
- Algoritmo Shor simplificado (no es el Shor completo real)
```

### Escenario B: QPU Más Rápida
```
CPU promedio:    0.05 s
QPU promedio:    0.02 s
Speedup:         2.5x (QPU es 2.5x más rápida)

Razones esperadas:
- Algoritmo Shor real en hardware
- Paralelismo cuántico aprovechado
- Compilación óptima para el hardware específico
```

### Escenario C: Tiempos Similares
```
CPU promedio:    0.01 s
QPU promedio:    0.009 s
Speedup:         1.1x (Similar)

Razones esperadas:
- Break-even point
- Overhead de compilación compensado por QPU
```

---

## 🎯 Métricas Importantes a Extraer

```python
# Análisis completo recomendado:

df = pd.read_csv("datasets/batch_01_all.csv")

print("=== ANÁLISIS COMPLETO ===\n")

# 1. Tasa de éxito general
print("1. TASA DE ÉXITO")
print(f"   CPU: {df[df['algo']=='classical']['success'].mean():.1%}")
print(f"   QPU: {df[df['algo']=='quantum']['success'].mean():.1%}\n")

# 2. Tiempos
print("2. TIEMPOS DE EJECUCIÓN")
cpu_data = df[df['algo']=='classical']
qpu_data = df[(df['algo']=='quantum') & (df['status']=='OK_QUANTUM_HARDWARE')]
print(f"   CPU - Promedio: {cpu_data['time_sec'].mean():.6f}s")
print(f"   QPU - Promedio: {qpu_data['quantum_seconds'].mean():.6f}s\n")

# 3. Overhead
print("3. OVERHEAD CUÁNTICO")
overhead = qpu_data['time_sec'] - qpu_data['quantum_seconds']
print(f"   Overhead promedio: {overhead.mean():.6f}s")
print(f"   % del tiempo total: {(overhead.mean() / qpu_data['time_sec'].mean() * 100):.1f}%\n")

# 4. Speedup
print("4. SPEEDUP")
speedup = cpu_data['time_sec'].mean() / qpu_data['quantum_seconds'].mean()
print(f"   Speedup (CPU/QPU): {speedup:.2f}x")
print(f"   Ganancia: {(1 - 1/speedup) * 100:.1f}% más rápido\n")

# 5. Por tamaño de N
print("5. ANÁLISIS POR TAMAÑO DE N")
for n_bits in sorted(df['N_bits'].unique()):
    subset_cpu = df[(df['N_bits']==n_bits) & (df['algo']=='classical')]
    subset_qpu = df[(df['N_bits']==n_bits) & (df['algo']=='quantum') & (df['status']=='OK_QUANTUM_HARDWARE')]
    if len(subset_cpu) > 0 and len(subset_qpu) > 0:
        speedup_n = subset_cpu['time_sec'].mean() / subset_qpu['quantum_seconds'].mean()
        print(f"   {n_bits} bits: Speedup {speedup_n:.2f}x")
```

---

## 📞 Preguntas Frecuentes

### P: ¿Por qué QPU es más lenta que CPU?
**R:** Es normal para problemas pequeños. El overhead de compilación, cola y transpilación supera el beneficio cuántico. Para problemas grandes (N > 1000 bits), el cuántico gana.

### P: ¿Qué significa "quantum_seconds"?
**R:** Tiempo REAL de ejecución en el procesador cuántico, sin incluir compilación ni cola. Es la métrica más importante para benchmarking.

### P: ¿Puedo comparar directamente "time_sec" con "quantum_seconds"?
**R:** No directamente. "time_sec" incluye overhead. Usa "quantum_seconds" para comparación justa.

### P: ¿Qué es el overhead?
**R:** `overhead = time_sec - quantum_seconds`. Incluye compilación a ISA, tiempo de cola, y post-procesamiento.

### P: ¿Por qué algunos jobs no tienen job_id?
**R:** Porque fueron fallback a CPU (si QPU no estaba disponible) o errores.

---

## 🚀 Próximas Análisis

1. **Escalar N**: Aumentar tamaño de los semiprimos gradualmente
2. **Comparar backends**: Ejecutar en diferentes QPUs y comparar `running_time`
3. **Error mitigation**: Aplicar técnicas de mitigación y medir impacto
4. **Paralelización**: Ejecutar múltiples jobs en paralelo

---

**Última actualización:** 16 de Enero, 2026
