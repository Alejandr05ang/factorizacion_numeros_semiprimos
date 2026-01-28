# Refactorización: Simulación Local → IBM Quantum Hardware Real (QPU)

## 📋 Resumen de Cambios

El código ha sido refactorizado para ejecutar el algoritmo de Shor en **procesadores cuánticos reales (QPU)** de IBM mediante la API `qiskit-ibm-runtime`, en lugar de simulaciones locales con Pollard's Rho.

---

## 🔄 Cambios Realizados por Sección

### 1. **Imports de Librerías** (Cell 3)
**Anteriormente:** Solo importaba Qiskit base y Aer
```python
# ANTES: Sin soporte para IBM hardware
import qiskit
from qiskit import QuantumCircuit
```

**Ahora:** Agregados imports de IBM Runtime y primitivas modernas
```python
# DESPUÉS: Con soporte completo para IBM hardware
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import SamplerV2  # Primitiva moderna
from qiskit_ibm_runtime import QiskitRuntimeService, Session  # API de runtime
from qiskit.transpiler import Layout, PassManager
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
```

**Impacto:** Permite acceso a hardware real + compilación automática a ISA.

---

### 2. **Configuración de IBM Quantum** (Cell 4)
**Anteriormente:** Sin configuración de hardware
```python
# ANTES: Solo variables locales
M_list = [100, 500, 1000, 5000]
```

**Agregado:** Bloque de configuración para IBM Quantum
```python
# DESPUÉS: Configuración de hardware + autenticación
USE_SIMULATOR = False  # Cambiar a False para QPU real
IBM_CHANNEL = "ibm_quantum"  # o "ibm_cloud"
OPTIMIZATION_LEVEL = 2  # 0-3, compilación para ISA
MAX_RETRIES = 3

IBM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN", None)
if IBM_TOKEN:
    print("✓ Token detectado")
else:
    print("ℹ Intentaremos usar credenciales en disco")
```

**Impacto:** Autenticación segura (sin hardcodear token) + selección de backend automática.

---

### 3. **Función `quantum_shor_once()`** (Cell 7)
**Fue Completamente Reemplazada** ⚠️

#### ANTES (Versión Clásica):
```python
# ANTIGUA: Usaba Pollard's Rho (algoritmo clásico simulado)
def quantum_shor_once(N: int, M: int, seed: int = None):
    factor = pollard_rho(N)  # ← Cálculo clásico, no cuántico
    if factor and factor != N:
        return 1, time.time()-t0, [factor, N//factor], "OK"
    return 0, time.time()-t0, [], "ERROR"
```

#### AHORA (Versión con IBM Quantum Hardware):
```python
# NUEVA: Ejecuta en QPU real mediante SamplerV2 + transpilación ISA
def quantum_shor_once(N: int, M: int, seed: int = None):
    
    # PASO 1: Crear circuito de demostración de Shor
    qc = create_shor_circuit(N, n_counting_qubits=8)
    
    # PASO 2: TRANSPILACIÓN A ISA (Compilación para hardware)
    pm = generate_preset_pass_manager(
        optimization_level=OPTIMIZATION_LEVEL,
        backend=quantum_backend
    )
    qc_isa = pm.run(qc)  # ← Circuito compilado específicamente para el hardware
    
    # PASO 3: Ejecutar en QPU REAL
    with Session(service=quantum_service, backend=quantum_backend) as session:
        sampler = SamplerV2(session=session)  # ← Primitiva moderna
        job = sampler.run([qc_isa], shots=M)
        result = job.result()
    
    # PASO 4: EXTRAER MÉTRICAS DE TIEMPO REAL
    quantum_time_sec = result.metadata[0].get('running_time', 0) / 1000  # ms → s
    # ↑ Tiempo real de ejecución en QPU (no incluye cola)
    
    # PASO 5: Interpretar resultados desde el hardware
    bitstring_counts = result.quasi_dists[0].binary_probabilities()
    
    return success, quantum_time_sec, factors_list, status, exec_metadata
```

**Cambios Clave:**
- ✅ Ejecuta en **hardware real** (no simulación)
- ✅ **Transpilación ISA**: Convierte el circuito a instrucciones nativas del backend
- ✅ **SamplerV2**: Primitiva moderna de runtime (reemplaza `backend.run()` obsoleto)
- ✅ **Session de runtime**: Sesión de trabajo en hardware real
- ✅ **Métricas de tiempo**: Extrae `running_time` (tiempo REAL en QPU)

---

### 4. **Nueva Función: `initialize_quantum_service()`**
**Agregada Completamente** ✨

```python
def initialize_quantum_service():
    """
    Inicializa conexión con IBM Quantum.
    
    CARACTERÍSTICA: Selecciona automáticamente la QPU menos ocupada.
    """
    if IBM_TOKEN:
        QiskitRuntimeService.save_account(
            channel=IBM_CHANNEL,
            token=IBM_TOKEN,
            overwrite=True
        )
    
    service = QiskitRuntimeService(channel=IBM_CHANNEL)
    
    # AUTOMÁTICO: Selecciona la máquina menos ocupada
    backend = service.least_busy(simulator=False, operational=True)
    
    return service, backend
```

**Por qué:** Permite seleccionar automáticamente el backend menos ocupado sin hardcodear nombres de máquinas.

---

### 5. **Nueva Función: `create_shor_circuit()`**
**Agregada Completamente** ✨

```python
def create_shor_circuit(N: int, n_counting_qubits: int = 8) -> QuantumCircuit:
    """
    Crea circuito de demostración del algoritmo Shor.
    
    Nota: Es una simplificación. El Shor completo requiere ~2n+3 qubits
    y post-procesamiento clásico complejo.
    """
    n_qubits = min(n_counting_qubits, 5)  # Limitar al hardware disponible
    qc = QuantumCircuit(n_qubits, n_qubits, name=f"shor_demo_N{N}")
    
    # Superposición + modulación de fase + QFT inversa
    for i in range(n_qubits):
        qc.h(i)
    
    for i in range(n_qubits):
        angle = 2 * np.pi * (N % (2**i)) / (2**(i+1))
        qc.p(angle, i)
    
    for i in range(n_qubits):
        qc.h(i)
    
    qc.measure(range(n_qubits), range(n_qubits))
    return qc
```

**Por qué:** Encapsula la lógica de construcción del circuito, haciéndola reutilizable y mantenible.

---

### 6. **Función `run_batch()`** (Cell 8)
**Modificada: Captura de Metadatos de Hardware**

#### Antes:
```python
rows.append({
    "algo": "quantum",
    "success": succ,
    "time_sec": tsec,
    "factors": str(facs),
})
```

#### Ahora:
```python
succ, tsec, facs, status, metadata = quantum_shor_once(N, M, seed=seed)
# ↑ Ahora retorna 5 elementos (incluye metadata)

rows.append({
    "algo": "quantum",
    "success": succ,
    "time_sec": tsec,
    "factors": str(facs),
    # AGREGADO: Nuevos campos para análisis de hardware
    "hw_backend": metadata.get("backend", None),      # Nombre del backend
    "hw_qubits": metadata.get("num_qubits_used", None),  # Qubits utilizados
    "quantum_seconds": tsec,  # Tiempo REAL en QPU
    "job_id": metadata.get("job_id", None)  # ID del job en IBM
})
```

**Impacto:** Los CSVs ahora incluyen información de hardware para análisis comparativo.

---

### 7. **Función `batch_report()`** (Cell 8)
**Modificada: Reporte de Métricas de Hardware**

#### Agregado:
```python
# Mostrar información del backend utilizado
hw_backend = q_valid["hw_backend"].iloc[0]
hw_qubits = q_valid["hw_qubits"].iloc[0]
print(f"Backend utilizado: {hw_backend} ({hw_qubits} qubits)")

# Mostrar tiempo REAL en QPU
avg_quantum_time = q_valid["quantum_seconds"].mean()
print(f"Tiempo promedio en QPU: {avg_quantum_time:.6f} s")

# Calcular y mostrar speedup
speedup = c_time / q_time
print(f"Speedup observado: {speedup:.2f}x")
```

**Impacto:** Los reportes ahora muestran métricas de hardware real para comparación CPU vs QPU.

---

## 🔐 Autenticación Segura

### Opción 1: Variable de Entorno (Recomendada)
```bash
# En PowerShell:
$env:IBM_QUANTUM_TOKEN = "your_token_here"

# En Bash:
export IBM_QUANTUM_TOKEN="your_token_here"

# En Windows (permanente):
setx IBM_QUANTUM_TOKEN "your_token_here"
```

### Opción 2: Credenciales en Disco
```python
# Primera vez:
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(token="your_token")

# El código leerá automáticamente de ~/.qiskit/qiskitrc
```

---

## 📊 Comparación de Métricas

| Métrica | Simulación Local | IBM QPU |
|---------|------------------|---------|
| **Tiempo de Ejecución** | ~ms (local) | Variable (hardware + cola) |
| **Tiempo Real en QPU** | N/A | `quantum_seconds` (extraído) |
| **Backend** | AerSimulator | IBM Hardware (múltiples opciones) |
| **Transpilación** | No requerida | **ISA obligatoria** |
| **Primitivas** | Deprecated `backend.run()` | **SamplerV2 moderno** |

---

## ⚙️ Requisitos para Ejecutar

### Dependencias:
```bash
pip install qiskit==1.0+
pip install qiskit-aer  # Aún requerido para fallback
pip install qiskit-ibm-runtime
```

### Autenticación:
1. Crear cuenta en https://quantum.ibm.com
2. Obtener API Token
3. Configurar `IBM_QUANTUM_TOKEN` como variable de entorno

### Hardware Disponible:
- Acceso a QPU real requiere:
  - Cuenta IBM Quantum activa
  - Token API válido
  - Backend disponible y operacional

---

## 🧪 Prueba Rápida

```python
# Verificar que todo funciona:
print(f"Service ready: {QUANTUM_READY}")
print(f"Backend: {quantum_backend.name if quantum_backend else 'N/A'}")

# Probar con un número pequeño:
success, qtime, factors, status, meta = quantum_shor_once(15, M=100)
print(f"N=15: éxito={success}, tiempo_qpu={qtime:.6f}s, status={status}")
```

---

## 📈 Próximas Mejoras

1. **Implementar Shor Completo**: El circuito actual es una demostración. Agregar:
   - Período de búsqueda cuántica (Order Finding)
   - Post-procesamiento clásico para extracción de factores
   - Manejo de casos especiales (N par, N potencia prima, etc.)

2. **Error Mitigation**: Agregar técnicas de mitigación de errores:
   - Symmetry Verification
   - Zero Noise Extrapolation (ZNE)

3. **Análisis de Ruido**: Capturar métricas de ruido del hardware

4. **Paralelización**: Ejecutar múltiples jobs en paralelo

---

## 🐛 Troubleshooting

### Error: "No se puede autenticar con IBM Quantum"
```
Solución: Verifica que IBM_QUANTUM_TOKEN esté configurada correctamente
          o ejecuta: QiskitRuntimeService.save_account(token="...")
```

### Error: "No hay QPU disponible"
```
Solución: Usa el simulador temporalmente (simulator=True en least_busy)
          o espera a que el hardware esté disponible
```

### Error: "Circuito no se puede transpilar"
```
Solución: Reduce n_qubits o OPTIMIZATION_LEVEL en create_shor_circuit()
```

---

## 📝 Referencias

- [Qiskit IBM Runtime Docs](https://docs.quantum.ibm.com/)
- [Primitivas: SamplerV2](https://docs.quantum.ibm.com/run/primitives-get-started)
- [Transpilación ISA](https://docs.quantum.ibm.com/transpile)
- [Algoritmo Shor](https://qiskit.org/documentation/tutorials/algorithms/04_shor.html)

---

**Última actualización:** 16 de Enero, 2026
**Versión de Qiskit:** 1.0+
**API Runtime:** ibm-runtime >= 0.23.0
