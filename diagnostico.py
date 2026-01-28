#!/usr/bin/env python
"""
Script de diagnóstico para investigar por qué quantum_shor_once falla.
"""
import time
import math
import sympy as sp
from qiskit_aer import Aer

# ===== FUNCIONES DEL NOTEBOOK =====

def get_shor_class():
    Shor = None
    try:
        from qiskit.algorithms import Shor as ShorOld
        Shor = ShorOld
        print("✓ Shor encontrado en qiskit.algorithms")
    except Exception as e:
        print(f"✗ Error en qiskit.algorithms: {e}")
    
    if Shor is None:
        try:
            from qiskit_algorithms import Shor as ShorNew
            Shor = ShorNew
            print("✓ Shor encontrado en qiskit_algorithms")
        except Exception as e:
            print(f"✗ Error en qiskit_algorithms: {e}")
    
    return Shor

def flatten_factors(factors):
    flat = []
    if factors is None:
        return flat
    if isinstance(factors, (list, tuple)):
        for item in factors:
            if isinstance(item, (list, tuple)):
                flat.extend(list(item))
            else:
                flat.append(item)
    return [int(x) for x in flat if x is not None]

def validate_any_factor(factors, N):
    for f in factors:
        if f not in (1, N) and N % f == 0:
            return True
    return False

def quantum_shor_once(N: int, M: int, seed: int = None):
    MAX_N_QUANTUM = 247
    t0 = time.time()

    print(f"\n--- Probando quantum_shor_once(N={N}, M={M}, seed={seed}) ---")

    # Control de tamaño
    if N > MAX_N_QUANTUM:
        print(f"  ✗ SKIPPED_TOO_LARGE (N={N} > MAX={MAX_N_QUANTUM})")
        return 0, time.time()-t0, [], "SKIPPED_TOO_LARGE"

    Shor = get_shor_class()
    if Shor is None:
        print(f"  ✗ SHOR_NOT_AVAILABLE")
        return 0, time.time()-t0, [], "SHOR_NOT_AVAILABLE"

    try:
        from qiskit_aer import Aer
        backend = Aer.get_backend("qasm_simulator")
        print(f"  ✓ Backend obtenido: {backend}")
        
        # Configurar shots
        try:
            backend.set_options(shots=M, seed_simulator=seed)
            print(f"  ✓ Opciones configuradas: shots={M}, seed={seed}")
        except Exception as e:
            print(f"  ⚠ No se pudieron configurar opciones: {e}")
    except Exception as e:
        print(f"  ✗ Error al obtener backend: {e}")
        backend = None

    try:
        if backend is not None:
            shor = Shor(quantum_instance=backend)
            print(f"  ✓ Shor inicializado con backend")
        else:
            shor = Shor()
            print(f"  ✓ Shor inicializado sin backend")

        print(f"  → Ejecutando shor.factor({N})...")
        result = shor.factor(N)
        print(f"  ✓ Factor completado. Resultado: {result}")

        factors = []
        if hasattr(result, "factors"):
            factors = result.factors
            print(f"    - Acceso via result.factors: {factors}")
        elif isinstance(result, dict) and "factors" in result:
            factors = result["factors"]
            print(f"    - Acceso via dict['factors']: {factors}")
        else:
            print(f"    - Sin atributo 'factors'. Tipo: {type(result)}")

        factors_flat = flatten_factors(factors)
        print(f"  → Factores aplanados: {factors_flat}")
        
        success = 1 if validate_any_factor(factors_flat, N) else 0
        print(f"  → Validación: success={success}")
        
        return success, time.time()-t0, factors_flat, "OK"

    except Exception as e:
        error_type = type(e).__name__
        print(f"  ✗ ERROR_{error_type}: {e}")
        import traceback
        traceback.print_exc()
        return 0, time.time()-t0, [], f"ERROR_{error_type}"


# ===== MAIN DIAGNOSTICO =====

if __name__ == "__main__":
    print("="*60)
    print("DIAGNÓSTICO - Factorización Cuántica")
    print("="*60)
    
    # 1. Verificar importes
    print("\n[1] Verificando importes...")
    Shor = get_shor_class()
    if Shor is None:
        print("ERROR CRÍTICO: No se puede importar Shor")
        exit(1)
    
    # 2. Generar semiprimos pequeños
    print("\n[2] Generando semiprimos pequeños...")
    primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    test_semiprimes = [primes[i] * primes[i+1] for i in range(0, len(primes)-1, 2)]
    print(f"   Semiprimos de prueba: {test_semiprimes}")
    
    # 3. Probar con cada semiprimo
    print("\n[3] Probando quantum_shor_once...")
    results = []
    for N in test_semiprimes[:3]:  # Solo los primeros 3 para no tardar
        for M in [100]:
            success, tsec, facs, status = quantum_shor_once(N, M, seed=42)
            results.append({
                'N': N,
                'M': M,
                'success': success,
                'status': status,
                'time': tsec,
                'factors': facs
            })
    
    # 4. Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    for r in results:
        print(f"N={r['N']:3d}, M={r['M']:4d}: success={r['success']}, status={r['status']:20s}, time={r['time']:.3f}s")
    
    print("\nDiagnóstico completado.")
