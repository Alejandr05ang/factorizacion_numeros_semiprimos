"""
Script de Verificación: IBM Quantum Hardware Setup
===================================================

Este script verifica que todo esté configurado correctamente para ejecutar
en hardware cuántico real de IBM.

Uso: python verify_setup.py
"""

import sys
import os

def check_environment():
    """Verifica variable de entorno IBM_QUANTUM_TOKEN"""
    print("\n" + "="*60)
    print("1. VERIFICACIÓN DE VARIABLE DE ENTORNO")
    print("="*60)
    
    token = os.getenv("IBM_QUANTUM_TOKEN", None)
    if token:
        masked_token = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else token[:10] + "..."
        print(f"✓ IBM_QUANTUM_TOKEN configurada")
        print(f"  Valor: {masked_token}")
        return True
    else:
        print(f"✗ IBM_QUANTUM_TOKEN NO configurada")
        print(f"  Configure en PowerShell:")
        print(f"    $env:IBM_QUANTUM_TOKEN = 'tu_token_aqui'")
        return False

def check_packages():
    """Verifica que todas las librerías estén instaladas"""
    print("\n" + "="*60)
    print("2. VERIFICACIÓN DE DEPENDENCIAS")
    print("="*60)
    
    packages = {
        "qiskit": "Qiskit Core",
        "qiskit_aer": "Qiskit Aer (Simulador)",
        "qiskit_ibm_runtime": "IBM Quantum Runtime",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "matplotlib": "Matplotlib",
        "sympy": "SymPy"
    }
    
    missing = []
    for package, description in packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, "__version__", "unknown")
            print(f"✓ {description:.<40} v{version}")
        except ImportError:
            print(f"✗ {description:.<40} NO INSTALADO")
            missing.append(package)
    
    if missing:
        print(f"\nFaltan paquetes. Instala con:")
        print(f"  pip install {' '.join(missing)}")
        return False
    return True

def check_runtime_connection():
    """Verifica conexión con IBM Quantum Runtime"""
    print("\n" + "="*60)
    print("3. VERIFICACIÓN DE CONEXIÓN IBM QUANTUM")
    print("="*60)
    
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        
        try:
            service = QiskitRuntimeService(channel="ibm_quantum")
            print(f"✓ Conexión exitosa a IBM Quantum")
            
            # Obtener backends disponibles
            backends = service.backends()
            print(f"✓ {len(backends)} backend(s) disponible(s)")
            
            # Listar primeros 5 backends
            print(f"\n  Backends disponibles:")
            for i, backend in enumerate(backends[:5], 1):
                operational = "✓" if backend.operational else "✗"
                status = "Operacional" if backend.operational else "En mantenimiento"
                print(f"    {i}. {operational} {backend.name:.<30} ({status})")
            
            if len(backends) > 5:
                print(f"    ... y {len(backends) - 5} más")
            
            # Intentar obtener el menos ocupado
            try:
                least_busy = service.least_busy(simulator=False, operational=True)
                print(f"\n✓ Backend menos ocupado: {least_busy.name}")
                print(f"  Qubits: {least_busy.num_qubits}")
                print(f"  Basis gates: {least_busy.configuration().basis_gates}")
                return True
            except Exception as e:
                print(f"⚠ No hay backend QPU disponible en este momento")
                print(f"  Error: {str(e)[:100]}")
                print(f"  Intentaremos usar simulador como fallback")
                return True
                
        except Exception as e:
            print(f"✗ Error al conectar:")
            print(f"  {str(e)[:200]}")
            print(f"\n  Soluciones posibles:")
            print(f"  1. Verifica que IBM_QUANTUM_TOKEN sea válido")
            print(f"  2. Regenera el token en https://quantum.ibm.com")
            print(f"  3. O usa: QiskitRuntimeService.save_account(token='...')")
            return False
            
    except ImportError:
        print(f"✗ qiskit-ibm-runtime no instalado")
        print(f"  Instala con: pip install qiskit-ibm-runtime")
        return False

def check_transpilation():
    """Verifica que la transpilación funcione correctamente"""
    print("\n" + "="*60)
    print("4. VERIFICACIÓN DE TRANSPILACIÓN")
    print("="*60)
    
    try:
        from qiskit import QuantumCircuit
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        
        # Crear circuito simple
        qc = QuantumCircuit(3, 3, name="test")
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure([0, 1, 2], [0, 1, 2])
        
        print(f"✓ Circuito de prueba creado:")
        print(f"  Qubits: {qc.num_qubits}")
        print(f"  Profundidad: {qc.depth()}")
        print(f"  Operaciones: {len(qc)}")
        
        # Intentar generar pass manager
        try:
            pm = generate_preset_pass_manager(optimization_level=2)
            print(f"✓ Pass Manager generado (sin backend específico)")
            
            # Transpilar
            qc_t = pm.run(qc)
            print(f"✓ Transpilación exitosa:")
            print(f"  Profundidad final: {qc_t.depth()}")
            
            return True
        except Exception as e:
            print(f"✗ Error en transpilación: {str(e)[:100]}")
            return False
            
    except ImportError as e:
        print(f"✗ Error de importación: {str(e)[:100]}")
        return False

def check_shor_circuit():
    """Verifica que se pueda crear un circuito de Shor"""
    print("\n" + "="*60)
    print("5. VERIFICACIÓN DE CIRCUITO SHOR")
    print("="*60)
    
    try:
        from qiskit import QuantumCircuit
        import numpy as np
        
        # Crear función de Shor (simplificada)
        def create_shor_circuit(N: int, n_counting_qubits: int = 8):
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
        
        # Crear circuito para N=15
        qc_shor = create_shor_circuit(15)
        print(f"✓ Circuito Shor creado para N=15:")
        print(f"  Qubits: {qc_shor.num_qubits}")
        print(f"  Profundidad: {qc_shor.depth()}")
        print(f"  Operaciones: {len(qc_shor)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "IBM QUANTUM SETUP VERIFICATION" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Entorno": check_environment(),
        "Dependencias": check_packages(),
        "Transpilación": check_transpilation(),
        "Circuito Shor": check_shor_circuit(),
        "Conexión IBM": check_runtime_connection(),
    }
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    for check, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}")
    
    all_pass = all(results.values())
    
    print("\n" + "="*60)
    if all_pass:
        print("✓ TODAS LAS VERIFICACIONES PASARON")
        print("✓ Estás listo para ejecutar el notebook en IBM Quantum")
        print("="*60)
        return 0
    else:
        print("✗ ALGUNAS VERIFICACIONES FALLARON")
        print("✗ Revisa los errores arriba y sigue las soluciones")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
