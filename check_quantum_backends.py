#!/usr/bin/env python3
"""
Diagnóstico: Verificar qué backends de QPU reales están disponibles en IBM Quantum
"""
import os
from qiskit_ibm_runtime import QiskitRuntimeService

# Configurar token
token = os.getenv("IBM_QUANTUM_TOKEN")
if not token:
    print("❌ ERROR: IBM_QUANTUM_TOKEN no configurada")
    exit(1)

print("=" * 70)
print("DIAGNÓSTICO DE BACKENDS IBM QUANTUM")
print("=" * 70)

try:
    # Conectar con IBM Quantum
    service = QiskitRuntimeService.save_account(
        channel="ibm_quantum_platform",
        api_key=token,
        overwrite=True
    )
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
    
    # Obtener todos los backends
    print("\n📋 BACKENDS DISPONIBLES:\n")
    
    # Backends operativos
    operational_backends = service.backends(operational=True, simulator=False)
    print(f"🟢 Backends OPERATIVOS (real QPU):")
    if operational_backends:
        for backend in operational_backends:
            print(f"   ✓ {backend.name} | {backend.num_qubits} qubits | Estados: {backend.status().status_msg}")
    else:
        print("   ❌ NINGUNO DISPONIBLE EN ESTE MOMENTO")
    
    # Backends simuladores
    simulator_backends = service.backends(operational=True, simulator=True)
    print(f"\n🟡 Backends SIMULADORES:")
    if simulator_backends:
        for backend in simulator_backends:
            print(f"   ✓ {backend.name} | {backend.num_qubits} qubits")
    
    # Intentar usar least_busy
    print(f"\n🔍 INTENTANDO SELECCIONAR BACKEND MENOS OCUPADO:")
    try:
        least_busy_backend = service.least_busy(simulator=False, operational=True)
        print(f"   ✓ Seleccionado: {least_busy_backend.name}")
        print(f"     - Qubits: {least_busy_backend.num_qubits}")
        print(f"     - Estado: {least_busy_backend.status().status_msg}")
        print(f"\n✅ QUANTUM REALMENTE DISPONIBLE ✅")
    except Exception as e:
        print(f"   ❌ No hay QPU disponible: {str(e)}")
        print(f"\n⚠️  EL SISTEMA USARÁ FALLBACK CLÁSICO (Pollard's Rho)")
        
except Exception as e:
    print(f"❌ Error de conexión: {str(e)}")
    
print("\n" + "=" * 70)
