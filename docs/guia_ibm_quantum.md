# Guía de Ejecución: Factorización en IBM Quantum Hardware

## 🚀 Inicio Rápido

### Paso 1: Configurar el Token de IBM Quantum

#### En PowerShell (Windows):
```powershell
# Opción A: Variable temporal (solo sesión actual)
$env:IBM_QUANTUM_TOKEN = "tu_token_aqui"

# Opción B: Variable permanente (recomendado)
[Environment]::SetEnvironmentVariable("IBM_QUANTUM_TOKEN", "tu_token_aqui", [EnvironmentVariableTarget]::User)
# Luego reinicia VS Code para que cargue la variable
```

#### En Bash (Linux/Mac):
```bash
# Opción A: Temporal
export IBM_QUANTUM_TOKEN="tu_token_aqui"

# Opción B: Permanente (agregar a ~/.bashrc o ~/.zshrc)
echo 'export IBM_QUANTUM_TOKEN="tu_token_aqui"' >> ~/.bashrc
source ~/.bashrc
```

#### Obtener tu Token:
1. Ir a https://quantum.ibm.com
2. Iniciar sesión con tu cuenta
3. Ir a "Account" → "Copy token" (esquina derecha)

---

### Paso 2: Verificar la Autenticación

Ejecuta en una celda del notebook:

```python
import os
from qiskit_ibm_runtime import QiskitRuntimeService

# Verificar que el token esté configurado
token = os.getenv("IBM_QUANTUM_TOKEN", None)
if token:
    print("✓ Token detectado en variable de entorno")
    print(f"  Primeros 10 caracteres: {token[:10]}...")
else:
    print("ℹ Sin token en variable de entorno")
    print("  Intentando cargar credenciales guardadas...")

# Intentar inicializar el servicio
try:
    service = QiskitRuntimeService(channel="ibm_quantum")
    print("✓ Conexión exitosa a IBM Quantum")
    
    # Listar backends disponibles
    backends = service.backends()
    print(f"✓ {len(backends)} backend(s) disponible(s):")
    for backend in backends[:5]:  # Mostrar primeros 5
        print(f"  - {backend.name}")
        
except Exception as e:
    print(f"✗ Error: {e}")
```

---

### Paso 3: Ejecutar con Hardware Real

Una vez verificada la autenticación, el notebook ejecutará automáticamente en hardware real:

```python
# El código ya está configurado para:
# 1. Detectar la QPU menos ocupada
# 2. Transpilar automáticamente
# 3. Ejecutar en hardware real
# 4. Extraer métricas de tiempo

# Ejecuta la celda de prueba:
success, qtime, factors, status, meta = quantum_shor_once(15, M=100)
print(f"Resultado: N=15")
print(f"  Factores: {factors}")
print(f"  Tiempo en QPU: {qtime:.6f}s")
print(f"  Backend: {meta.get('backend', 'N/A')}")
print(f"  Job ID: {meta.get('job_id', 'N/A')}")
```

---

## 📊 Ejecución Completa de un Batch

### Script Completo:
```python
# Verificar configuración
print("=== CONFIGURACIÓN ===")
print(f"QUANTUM_READY: {QUANTUM_READY}")
print(f"Backend: {quantum_backend.name if quantum_backend else 'No disponible'}")
print(f"Qubits disponibles: {quantum_backend.num_qubits if quantum_backend else 'N/A'}")

# Ejecutar un batch pequeño
print("\n=== EJECUTANDO BATCH 1 ===")
df_batch1 = run_batch(1, batches[0])

# Mostrar resultados
print("\n=== RESULTADOS ===")
print(df_batch1[df_batch1["algo"] == "quantum"].head(10))
```

---

## 🔍 Análisis de Resultados

### Extraer Métricas de Hardware:

```python
# Leer el CSV generado
import pandas as pd

df_quantum = pd.read_csv("datasets/batch_01_quantum.csv")

# Agrupar por backend y calcular estadísticas
stats = df_quantum.groupby(["hw_backend", "M"]).agg({
    "success": ["mean", "std", "count"],
    "quantum_seconds": ["mean", "min", "max"],
    "time_sec": "mean"
}).round(6)

print(stats)

# Mostrar jobs ejecutados
print("\nJobs ejecutados en hardware:")
print(df_quantum[["N", "hw_backend", "hw_qubits", "quantum_seconds", "job_id"]].head(10))
```

---

## ⏱️ Comparación CPU vs QPU

```python
# Leer datos clásicos y cuánticos
df_classical = pd.read_csv("datasets/batch_01_classical.csv")
df_quantum = pd.read_csv("datasets/batch_01_quantum.csv")

# Tiempos promedio
classical_avg = df_classical["time_sec"].mean()
quantum_avg = df_quantum["quantum_seconds"].mean()

print(f"CPU (Clásico):  {classical_avg:.6f} s")
print(f"QPU (Cuántico): {quantum_avg:.6f} s")
print(f"Speedup:        {classical_avg / quantum_avg:.2f}x")

# Graficar comparación
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Gráfico 1: Tiempos por número
axes[0].scatter(df_classical["N"], df_classical["time_sec"], 
               label="Clásico", alpha=0.6, s=50)
axes[0].scatter(df_quantum["N"], df_quantum["quantum_seconds"], 
               label="QPU", alpha=0.6, s=50)
axes[0].set_xlabel("N (número a factorizar)")
axes[0].set_ylabel("Tiempo (segundos)")
axes[0].set_xscale("log")
axes[0].set_yscale("log")
axes[0].legend()
axes[0].grid(True)
axes[0].set_title("Comparación de Tiempos")

# Gráfico 2: Tasa de éxito
classical_success = df_classical["success"].mean()
quantum_success = df_quantum["success"].mean()

axes[1].bar(["Clásico", "QPU"], [classical_success, quantum_success], color=["blue", "red"])
axes[1].set_ylabel("Tasa de Éxito (%)")
axes[1].set_ylim(0, 1)
axes[1].set_title("Tasa de Éxito")

for i, v in enumerate([classical_success, quantum_success]):
    axes[1].text(i, v + 0.02, f"{v:.1%}", ha="center")

plt.tight_layout()
plt.show()
```

---

## 📈 Tabla de Resultados

```python
# Crear tabla resumen
summary = pd.DataFrame({
    "Métrica": [
        "Tiempo Promedio (s)",
        "Tiempo Mín (s)",
        "Tiempo Máx (s)",
        "Std Dev Tiempo",
        "Tasa de Éxito",
        "Total Ejecuciones"
    ],
    "Clásico": [
        df_classical["time_sec"].mean(),
        df_classical["time_sec"].min(),
        df_classical["time_sec"].max(),
        df_classical["time_sec"].std(),
        f"{df_classical['success'].mean():.1%}",
        len(df_classical)
    ],
    "QPU": [
        df_quantum["quantum_seconds"].mean(),
        df_quantum["quantum_seconds"].min(),
        df_quantum["quantum_seconds"].max(),
        df_quantum["quantum_seconds"].std(),
        f"{df_quantum['success'].mean():.1%}",
        len(df_quantum)
    ]
})

print(summary.to_string(index=False))
```

---

## 🐛 Troubleshooting

### Problema: "IBM_QUANTUM_TOKEN no definida"
```python
import os
print(os.getenv("IBM_QUANTUM_TOKEN", "❌ NO CONFIGURADA"))

# Solución:
# 1. En PowerShell:
#    $env:IBM_QUANTUM_TOKEN = "tu_token"
# 2. O usar save_account:
#    from qiskit_ibm_runtime import QiskitRuntimeService
#    QiskitRuntimeService.save_account(token="tu_token", overwrite=True)
```

### Problema: "AuthenticationError"
```
Causa: Token inválido o expirado
Solución: 
  1. Verifica el token en https://quantum.ibm.com
  2. Vuelve a copiar y configurar
  3. Limpia credenciales antiguas: 
     QiskitRuntimeService.delete_account(channel="ibm_quantum")
```

### Problema: "No backends available"
```
Causa: Sin backend disponible (mantenimiento o límites de cuota)
Solución:
  1. Espera un tiempo e intenta nuevamente
  2. Usa service.backends() para listar opciones
  3. Usa simulador temporalmente (USE_SIMULATOR = True)
```

### Problema: "Circuit too large for this backend"
```
Solución: Reduce n_qubits en create_shor_circuit():
  - Cambia n_qubits = min(n_counting_qubits, 3)  # en lugar de 5
  - O reduce OPTIMIZATION_LEVEL a 1
```

---

## 💾 Estructura de Datos Guardados

### Archivo: `batch_XX_quantum.csv`

```
batch_id,run_id,algo,N,N_bits,M,rep,success,time_sec,factors,status,seed,hw_backend,hw_qubits,quantum_seconds,job_id
1,1,quantum,15,4,100,1,1,0.123,"[3, 5]",OK_QUANTUM_HARDWARE,100111101,ibm_brisbane_127_0,5,0.087,abc123xyz...
1,2,quantum,15,4,100,2,0,0.125,"[]",INSUFFICIENT_COHERENCE,100111102,ibm_brisbane_127_0,5,0.089,abc124xyz...
```

**Columnas Clave:**
- `quantum_seconds`: Tiempo REAL de ejecución en QPU (sin cola)
- `hw_backend`: Nombre del backend utilizado
- `hw_qubits`: Número de qubits utilizados en el circuito compilado
- `job_id`: ID del job (para rastrear en IBM Dashboard)
- `status`: OK_QUANTUM_HARDWARE = ejecución exitosa en QPU

---

## 🎯 Próximos Pasos

1. **Ejecutar batches completos**: Todos los 10 batches con datos reales
2. **Análisis comparativo**: CPU vs QPU para diferentes tamaños de N
3. **Optimización**: Ajustar OPTIMIZATION_LEVEL y n_qubits según resultados
4. **Escalado**: Aumentar M_list con números más grandes según capacidad

---

## 📞 Soporte

- Documentación oficial: https://docs.quantum.ibm.com/
- Comunidad: https://github.com/Qiskit/qiskit-ibm-runtime
- Problemas: https://github.com/Qiskit/qiskit-ibm-runtime/issues

---

**Última actualización:** 16 de Enero, 2026
