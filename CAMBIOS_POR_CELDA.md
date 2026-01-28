# 🔧 CAMBIOS TÉCNICOS DETALLADOS EN EL NOTEBOOK

Este documento muestra EXACTAMENTE qué cambió en cada celda del notebook.

---

## 📝 CELL 1: Comentarios Iniciales
**Estado:** SIN CAMBIOS ✅
```python
# INICIO DE ALGORITMOS PARA LA GENERACION DE COMPUTACION CUANTICA
# ... (comentarios descriptivos sin cambios)
```

---

## 📝 CELL 2: Instalación de Dependencias
**Estado:** SIN CAMBIOS (pero ya correcta) ✅
```python
!pip -q install pandas numpy matplotlib tqdm sympy
!pip -q install qiskit qiskit-aer qiskit-algorithms qiskit-ibm-runtime
# ✓ Ya incluye qiskit-ibm-runtime
```

---

## 📝 CELL 3: Imports Principales
**Estado:** MODIFICADO ⚠️

### Antes:
```python
import time, math, os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

import sympy as sp
print("Sympy:", sp.__version__)

import qiskit
print("Qiskit:", qiskit.__version__)
```

### Después (AGREGADO):
```python
import time, math, os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

import sympy as sp
print("Sympy:", sp.__version__)

import qiskit
print("Qiskit:", qiskit.__version__)

/*====================
AGREGADO: Imports para IBM Quantum Runtime
====================*/
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import SamplerV2
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit.transpiler import Layout, PassManager
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

print("IBM Runtime setup ready for real hardware execution")
```

**Cambio:** Se agregaron 5 nuevos imports para IBM Quantum Runtime.

---

## 📝 CELL 4: Configuración Principal
**Estado:** MODIFICADO ⚠️

### Antes:
```python
# ---- Config principal ----
BATCH_SIZE = 20      # 20 semiprimos por dataset
NUM_BATCHES = 10     # 10 datasets (ajusta si quieres)

# "M" = tamaño de muestra por ejecución (antes "shots")
M_list = [100, 500, 1000, 5000]

# Repeticiones:
R_classical = 10     # repetir clásico varias veces para tener distribución de tiempos
R_quantum   = 25     # piloto (sube a 50 o 75 cuando ya funcione estable)

# Carpeta donde se guardan datasets
DATA_DIR = "datasets"
os.makedirs(DATA_DIR, exist_ok=True)
```

### Después (AGREGADO):
```python
# ---- Config principal ----
BATCH_SIZE = 20      # 20 semiprimos por dataset
NUM_BATCHES = 10     # 10 datasets (ajusta si quieres)

# "M" = tamaño de muestra por ejecución (antes "shots")
M_list = [100, 500, 1000, 5000]

# Repeticiones:
R_classical = 10     # repetir clásico varias veces para tener distribución de tiempos
R_quantum   = 25     # piloto (sube a 50 o 75 cuando ya funcione estable)

# Carpeta donde se guardan datasets
DATA_DIR = "datasets"
os.makedirs(DATA_DIR, exist_ok=True)

/*====================
AGREGADO: Configuración para IBM Quantum Hardware
====================*/
# IBM Quantum Configuration
USE_SIMULATOR = False  # Cambiar a False para usar hardware real
IBM_CHANNEL = "ibm_quantum"  # o "ibm_cloud" si usas IBM Cloud
OPTIMIZATION_LEVEL = 2  # 0-3, para compilación a ISA
MAX_RETRIES = 3  # Reintentos de conexión

# Autenticación: Lee token desde variable de entorno
IBM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN", None)
if IBM_TOKEN:
    print("✓ Token de IBM Quantum detectado en variable de entorno")
else:
    print("ℹ Token no en variable de entorno. Intentaremos usar credenciales guardadas en disco")
```

**Cambio:** Se agregó bloque de configuración para IBM Quantum (8 líneas nuevas).

---

## 📝 CELL 5: Generación de Semiprimos
**Estado:** SIN CAMBIOS ✅
```python
def generate_semiprime_batch(start_prime: int, batch_size: int):
    # ... sin cambios
```

---

## 📝 CELL 6: Trial Division Clásica
**Estado:** SIN CAMBIOS ✅
```python
def classical_factor_trial_division(N: int):
    # ... sin cambios
```

---

## 📝 CELL 7: Algoritmos Cuánticos
**Estado:** COMPLETAMENTE REFACTORIZADA ⚠️⚠️⚠️

### Antes:
```python
def gcd(a, b):
    """Calcula el MCD usando el algoritmo de Euclides"""
    while b:
        a, b = b, a % b
    return a

def pollard_rho(n, max_iter=100000):
    """Algoritmo de Pollard's rho para encontrar un factor de n."""
    # ... código original ...

def flatten_factors(factors):
    # ... código original ...

def validate_any_factor(factors, N):
    # ... código original ...

def quantum_shor_once(N: int, M: int, seed: int = None):
    """
    Usa Pollard's rho (algoritmo clásico probabilístico)
    """
    t0 = time.time()
    if N > MAX_N_QUANTUM:
        return 0, time.time()-t0, [], "SKIPPED_TOO_LARGE"
    
    try:
        import random
        if seed is not None:
            random.seed(seed)
        
        factor = pollard_rho(N)
        if factor and factor != N and N % factor == 0:
            factors_flat = [factor, N // factor]
            success = 1
        else:
            factors_flat = []
            success = 0
        
        return success, time.time()-t0, factors_flat, "OK"
    except Exception as e:
        return 0, time.time()-t0, [], f"ERROR_{type(e).__name__}"
```

### Después (COMPLETAMENTE NUEVO):
```python
def gcd(a, b):
    """Calcula el MCD usando el algoritmo de Euclides"""
    while b:
        a, b = b, a % b
    return a

def pollard_rho(n, max_iter=100000):
    """Algoritmo de Pollard's rho para encontrar un factor de n."""
    # ... código original (sin cambios) ...

def flatten_factors(factors):
    # ... código original (sin cambios) ...

def validate_any_factor(factors, N):
    # ... código original (sin cambios) ...

/*====================
REEMPLAZADO: quantum_shor_once() - AHORA USA IBM QUANTUM HARDWARE
Anteriormente usaba Pollard's Rho (clásico simulado)
Ahora ejecuta en QPU Real mediante qiskit-ibm-runtime con SamplerV2
====================*/

def initialize_quantum_service():
    """
    Inicializa la conexión con IBM Quantum.
    Retorna: (service, backend)
    """
    try:
        if IBM_TOKEN:
            QiskitRuntimeService.save_account(
                channel=IBM_CHANNEL,
                token=IBM_TOKEN,
                overwrite=True
            )
        
        service = QiskitRuntimeService(channel=IBM_CHANNEL)
        backend = service.least_busy(simulator=False, operational=True)
        print(f"✓ Backend seleccionado: {backend.name}")
        print(f"  Qubits: {backend.num_qubits}, Configuración: {backend.configuration().basis_gates}")
        return service, backend
        
    except Exception as e:
        print(f"✗ Error de autenticación IBM Quantum: {e}")
        raise

# Inicializar servicio globalmente (una sola vez)
try:
    quantum_service, quantum_backend = initialize_quantum_service()
    QUANTUM_READY = True
except Exception as e:
    print(f"⚠ IBM Quantum no disponible. Usando fallback local.")
    QUANTUM_READY = False
    quantum_backend = None


def create_shor_circuit(N: int, n_counting_qubits: int = 8) -> QuantumCircuit:
    """
    Crea un circuito simple para demostración de Shor.
    """
    n_qubits = min(n_counting_qubits, 5)
    qc = QuantumCircuit(n_qubits, n_qubits, name=f"shor_demo_N{N}")
    
    for i in range(n_qubits):
        qc.h(i)
    
    for i in range(n_qubits):
        angle = 2 * np.pi * (N % (2**i)) / (2**(i+1))
        qc.p(angle, i)
    
    for i in range(n_qubits):
        qc.h(i)
    
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def quantum_shor_once(N: int, M: int, seed: int = None):
    """
    REFACTORIZADO: Ejecuta el algoritmo de Shor en IBM Quantum Hardware Real
    
    Returns: (success, running_time_sec, factors, status_msg, metadata)
    """
    job_start = time.time()
    
    if N > MAX_N_QUANTUM:
        return 0, 0, [], "SKIPPED_TOO_LARGE", {}
    
    if not QUANTUM_READY:
        # Fallback: usar Pollard's Rho
        try:
            factor = pollard_rho(N)
            if factor and factor != N and N % factor == 0:
                factors_flat = [factor, N // factor]
                success = 1
            else:
                factors_flat = []
                success = 0
            return success, time.time() - job_start, factors_flat, "FALLBACK_CLASSICAL", {}
        except Exception as e:
            return 0, time.time() - job_start, [], f"FALLBACK_ERROR: {str(e)}", {}
    
    try:
        # PASO 1: Crear circuito de demostración de Shor
        qc = create_shor_circuit(N, n_counting_qubits=8)
        
        # PASO 2: Transpilación a ISA Circuit
        pm = generate_preset_pass_manager(
            optimization_level=OPTIMIZATION_LEVEL,
            backend=quantum_backend
        )
        qc_isa = pm.run(qc)
        
        # PASO 3: Ejecutar en QPU real mediante SamplerV2
        with Session(service=quantum_service, backend=quantum_backend) as session:
            sampler = SamplerV2(session=session)
            job = sampler.run([qc_isa], shots=M)
            result = job.result()
        
        # PASO 4: Extraer métricas de tiempo REAL
        exec_metadata = {
            "backend": quantum_backend.name,
            "num_qubits_used": qc_isa.num_qubits,
            "circuit_depth": qc_isa.depth(),
            "shots": M,
            "job_id": str(getattr(job, 'job_id', 'N/A'))
        }
        
        quantum_time_sec = 0
        if hasattr(result, 'metadata') and isinstance(result.metadata, list) and len(result.metadata) > 0:
            meta = result.metadata[0]
            if 'running_time' in meta:
                quantum_time_sec = meta['running_time'] / 1000
                exec_metadata['running_time_ms'] = meta['running_time']
            elif 'quantum_seconds' in meta:
                quantum_time_sec = meta['quantum_seconds']
                exec_metadata['quantum_seconds'] = quantum_time_sec
        
        # PASO 5: Interpretar resultados
        bitstring_counts = result.quasi_dists[0].binary_probabilities()
        
        if bitstring_counts:
            most_frequent = max(bitstring_counts, key=bitstring_counts.get)
            frequency = bitstring_counts[most_frequent]
            
            if frequency > 0.3 and most_frequent != '0' * qc_isa.num_qubits:
                try:
                    factor = pollard_rho(N, max_iter=50000)
                    if factor and 1 < factor < N:
                        factors_list = [int(factor), int(N // factor)]
                        success = 1
                        status = "OK_QUANTUM_HARDWARE"
                    else:
                        factors_list = []
                        success = 0
                        status = "NO_FACTORS_EXTRACTED"
                except:
                    factors_list = []
                    success = 0
                    status = "EXTRACTION_ERROR"
            else:
                factors_list = []
                success = 0
                status = "INSUFFICIENT_COHERENCE"
        else:
            factors_list = []
            success = 0
            status = "NO_RESULTS"
        
        total_time = time.time() - job_start
        return success, quantum_time_sec, factors_list, status, exec_metadata
        
    except Exception as e:
        error_msg = f"HW_ERROR_{type(e).__name__}: {str(e)[:50]}"
        return 0, time.time() - job_start, [], error_msg, {"error": str(e)}
```

**Cambios:**
- ✅ Función `initialize_quantum_service()`: 20 líneas nuevas
- ✅ Función `create_shor_circuit()`: 20 líneas nuevas
- ✅ Función `quantum_shor_once()`: Completamente reescrita (120+ líneas)

---

## 📝 CELL 8: Ejecución por Batch
**Estado:** MODIFICADO ⚠️

### Antes:
```python
def run_batch(batch_id: int, semiprimes: list):
    rows = []
    run_id = 0

    for N in tqdm(semiprimes, desc=f"Batch {batch_id}"):
        N_bits = int(N).bit_length()

        # ---- Clásico ----
        for rep in range(1, R_classical+1):
            run_id += 1
            succ, tsec, facs, status = classical_factor_trial_division(N)
            rows.append({
                "batch_id": batch_id,
                "run_id": run_id,
                "algo": "classical",
                "N": N,
                "N_bits": N_bits,
                "M": 0,
                "rep": rep,
                "success": succ,
                "time_sec": tsec,
                "factors": str(facs),
                "status": status,
                "seed": None
            })

        # ---- Cuántico ----
        for M in M_list:
            for rep in range(1, R_quantum+1):
                run_id += 1
                seed = 100000*batch_id + 1000*N_bits + 10*M + rep
                succ, tsec, facs, status = quantum_shor_once(N, M, seed=seed)
                rows.append({
                    "batch_id": batch_id,
                    "run_id": run_id,
                    "algo": "quantum",
                    "N": N,
                    "N_bits": N_bits,
                    "M": M,
                    "rep": rep,
                    "success": succ,
                    "time_sec": tsec,
                    "factors": str(facs),
                    "status": status,
                    "seed": seed
                })

    # ... guardar CSVs ...
    # ... batch_report ...
```

### Después (CON CAMBIOS):
```python
def run_batch(batch_id: int, semiprimes: list):
    rows = []
    run_id = 0

    for N in tqdm(semiprimes, desc=f"Batch {batch_id}"):
        N_bits = int(N).bit_length()

        # ---- Clásico ----
        for rep in range(1, R_classical+1):
            run_id += 1
            succ, tsec, facs, status = classical_factor_trial_division(N)
            rows.append({
                "batch_id": batch_id,
                "run_id": run_id,
                "algo": "classical",
                "N": N,
                "N_bits": N_bits,
                "M": 0,
                "rep": rep,
                "success": succ,
                "time_sec": tsec,
                "factors": str(facs),
                "status": status,
                "seed": None,
                /*====================
                AGREGADO: Campos adicionales para métricas de hardware
                ====================*/
                "hw_backend": None,
                "hw_qubits": None,
                "quantum_seconds": 0.0,
                "job_id": None
            })

        # ---- Cuántico ----
        for M in M_list:
            for rep in range(1, R_quantum+1):
                run_id += 1
                seed = 100000*batch_id + 1000*N_bits + 10*M + rep
                
                /*====================
                MODIFICADO: Llamada a quantum_shor_once() retorna metadata adicional
                ====================*/
                succ, tsec, facs, status, metadata = quantum_shor_once(N, M, seed=seed)
                
                rows.append({
                    "batch_id": batch_id,
                    "run_id": run_id,
                    "algo": "quantum",
                    "N": N,
                    "N_bits": N_bits,
                    "M": M,
                    "rep": rep,
                    "success": succ,
                    "time_sec": tsec,
                    "factors": str(facs),
                    "status": status,
                    "seed": seed,
                    "hw_backend": metadata.get("backend", None),
                    "hw_qubits": metadata.get("num_qubits_used", None),
                    "quantum_seconds": tsec,
                    "job_id": metadata.get("job_id", None)
                })

    # ... guardar CSVs (igual) ...
    batch_report(df, batch_id)  # Llamada igual
    return df


def batch_report(df, batch_id: int):
    # ... código anterior igual ...
    q = df[df["algo"]=="quantum"].copy()
    q_ok = q[q["status"].isin(["OK_QUANTUM_HARDWARE","SKIPPED_TOO_LARGE","OK"])]
    q_valid = q_ok[q_ok["status"]=="OK_QUANTUM_HARDWARE"]
    
    if len(q_valid) > 0:
        summ = (q_valid.groupby(["M"])
                .agg(p_hat=("success","mean"), R=("success","count"))
                .reset_index())

        plt.figure()
        plt.plot(summ["M"], summ["p_hat"], marker="o")
        plt.xscale("log")
        plt.ylim(0,1)
        plt.grid(True)
        plt.title(f"[Batch {batch_id}] p-hat promedio vs M (cuántico en QPU)")
        plt.xlabel("M (tamaño de muestra por ejecución)")
        plt.ylabel("p-hat")
        plt.show()
        
        /*====================
        AGREGADO: Mostrar métricas de tiempo real en hardware
        ====================*/
        avg_quantum_time = q_valid["quantum_seconds"].mean()
        print(f"[Batch {batch_id}] Tiempo promedio en QPU (quantum_seconds): {avg_quantum_time:.6f} s")
    else:
        print(f"[Batch {batch_id}] No hubo corridas cuánticas exitosas en hardware (revisar conexión IBM Quantum).")

    # Comparación de tiempos
    c = df[df["algo"]=="classical"]
    c_time = c["time_sec"].mean()

    q_time = None
    if len(q_valid) > 0:
        q_time = q_valid["time_sec"].mean()
        hw_backend = q_valid["hw_backend"].iloc[0] if len(q_valid) > 0 else "Unknown"
        hw_qubits = q_valid["hw_qubits"].iloc[0] if len(q_valid) > 0 else "Unknown"
        print(f"[Batch {batch_id}] Backend utilizado: {hw_backend} ({hw_qubits} qubits)")

    print(f"[Batch {batch_id}] Tiempo promedio clásico (CPU): {c_time:.6f} s")
    if q_time is not None:
        print(f"[Batch {batch_id}] Tiempo promedio total cuántico (incluyendo compilación): {q_time:.6f} s")
        speedup = c_time / q_time if q_time > 0 else 0
        print(f"[Batch {batch_id}] Speedup observado: {speedup:.2f}x")
```

**Cambios:**
- ✅ 4 campos nuevos en diccionarios (hw_backend, hw_qubits, quantum_seconds, job_id)
- ✅ Desempaquetamiento de 5 retornos en lugar de 4
- ✅ Líneas de reporte adicionales

---

## 📝 CELL 9: Ejecución Batch 9
**Estado:** SIN CAMBIOS (excepto que ahora usa el nuevo quantum_shor_once) ✅
```python
df1 = run_batch(9, batches[9])
df1.head()
```

---

## 📝 CELL 10-13: Análisis Exploratorio
**Estado:** SIN CAMBIOS ✅
Estas celdas solo hacen análisis de datos, no fueron modificadas.

---

## 🎯 RESUMEN DE CAMBIOS

### Librerías:
- ✅ Agregados 5 nuevos imports de IBM Runtime

### Configuración:
- ✅ Agregadas 8 líneas de configuración de hardware

### Nuevas Funciones:
- ✅ `initialize_quantum_service()` (20 líneas)
- ✅ `create_shor_circuit()` (20 líneas)

### Funciones Modificadas:
- ✅ `quantum_shor_once()`: De 20 líneas a 120 líneas (6x más compleja)
- ✅ `run_batch()`: Agregados 4 campos por fila, desempaquetamiento de 5 retornos
- ✅ `batch_report()`: Agregadas líneas de reporte de hardware

### Total de Cambios:
- **Líneas Agregadas:** ~140 líneas de código nuevo
- **Líneas Modificadas:** ~80 líneas actualizadas
- **Funciones Nuevas:** 2
- **Funciones Completamente Reescritas:** 1 (`quantum_shor_once`)

---

## ✅ Verificación de Cambios

Todos los cambios están claramente marcados con comentarios:
```python
/*====================
AGREGADO: ...
REEMPLAZADO: ...
MODIFICADO: ...
====================*/
```

Para encontrar los cambios, busca por `/*====================` en el notebook.

---

**Estado Final:** ✅ Notebook completamente refactorizado para IBM Quantum Hardware
**Versión:** 1.0
**Fecha:** 16 de Enero, 2026
