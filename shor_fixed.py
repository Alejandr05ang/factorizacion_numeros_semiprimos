# Fixed Shor Algorithm Implementation
# The key fix: decompose() the circuit before running it on AerSimulator

import time
import math
import numpy as np
from fractions import Fraction
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def qft_dagger(circuit: QuantumCircuit, n: int):
    """QFT inversa para n qubits."""
    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            circuit.cp(-np.pi / float(2 ** (j - m)), m, j)
        circuit.h(j)


def c_amod15(a: int, power: int) -> QuantumCircuit:
    """Multiplicación modular controlada para N=15."""
    U = QuantumCircuit(4)
    for _ in range(power):
        if a in [2, 13]:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)
        if a in [7, 8]:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        if a in [4, 11]:
            U.swap(1, 3)
            U.swap(0, 2)
        if a in [7, 11, 13]:
            for q in range(4):
                U.x(q)
    U = U.to_gate()
    U.name = f"{a}^{power} mod 15"
    c_U = U.control()
    return c_U


def shor_circuit_15(a: int, n_count: int = 8) -> QuantumCircuit:
    """Circuito de Shor para N=15."""
    qc = QuantumCircuit(n_count + 4, n_count)
    
    for q in range(n_count):
        qc.h(q)
    
    qc.x(n_count)
    
    for q in range(n_count):
        qc.append(c_amod15(a, 2**q), [q] + list(range(n_count, n_count + 4)))
    
    qft_dagger(qc, n_count)
    qc.measure(range(n_count), range(n_count))
    
    return qc


def gcd(a: int, b: int) -> int:
    """Máximo común divisor."""
    while b:
        a, b = b, a % b
    return a


def mod_exp(base: int, exp: int, mod: int) -> int:
    """Exponenciación modular eficiente."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result


def find_period_quantum(N: int, a: int, shots: int) -> tuple:
    """Encuentra el período usando QPE - FIXED VERSION."""
    t0 = time.time()
    
    n_count = max(4, 2 * N.bit_length())
    n_count = min(n_count, 12)  # Límite para simulación
    
    # Create the circuit
    if N == 15:
        qc = shor_circuit_15(a, n_count)
    else:
        # For other numbers, use a simplified approach
        raise NotImplementedError("Only N=15 is implemented in this version")
    
    # *** CRITICAL FIX: Decompose the circuit into basic gates ***
    # This converts custom controlled gates into gates that AerSimulator understands
    qc_decomposed = qc.decompose()
    
    simulator = AerSimulator()
    job = simulator.run(qc_decomposed, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    elapsed = time.time() - t0
    qubits_used = qc.num_qubits
    
    # Procesar resultados
    for output, count in sorted(counts.items(), key=lambda x: -x[1]):
        decimal = int(output, 2)
        if decimal == 0:
            continue
        phase = decimal / (2 ** n_count)
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        
        if r > 1 and mod_exp(a, r, N) == 1:
            return r, True, elapsed, qubits_used
    
    return None, False, elapsed, qubits_used


def shor_factor(N: int, shots: int, max_attempts: int = 10) -> dict:
    """Ejecuta Shor para factorizar N."""
    t_start = time.time()
    qubits_used = 0
    
    # Caso trivial
    if N % 2 == 0:
        return {'success': True, 'factors': [2, N // 2], 'attempts': 0,
                'time': 0, 'qubits_used': 0, 'method': 'trivial_even'}
    
    for attempt in range(1, max_attempts + 1):
        a = np.random.randint(2, N - 1)
        
        g = gcd(a, N)
        if g > 1:
            return {'success': True, 'factors': sorted([g, N // g]), 'attempts': attempt,
                    'time': time.time() - t_start, 'qubits_used': 0, 'method': 'gcd_luck'}
        
        r, found, q_time, qubits = find_period_quantum(N, a, shots)
        qubits_used = qubits
        
        if found and r is not None and r % 2 == 0:
            x = mod_exp(a, r // 2, N)
            f1 = gcd(x - 1, N)
            f2 = gcd(x + 1, N)
            
            if 1 < f1 < N:
                return {'success': True, 'factors': sorted([f1, N // f1]),
                        'attempts': attempt, 'time': time.time() - t_start,
                        'qubits_used': qubits, 'method': 'quantum'}
            if 1 < f2 < N:
                return {'success': True, 'factors': sorted([f2, N // f2]),
                        'attempts': attempt, 'time': time.time() - t_start,
                        'qubits_used': qubits, 'method': 'quantum'}
    
    return {'success': False, 'factors': [], 'attempts': max_attempts,
            'time': time.time() - t_start, 'qubits_used': qubits_used, 'method': 'failed'}


# Test the fixed implementation
if __name__ == "__main__":
    print("Testing fixed Shor implementation...")
    test_result = shor_factor(15, shots=1024)
    print(f"Prueba N=15: {test_result}")
