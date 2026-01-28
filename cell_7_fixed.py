def find_period_quantum(N: int, a: int, shots: int) -> tuple:
    """Encuentra el período usando QPE."""
    t0 = time.time()
    
    n_count = max(4, 2 * N.bit_length())
    n_count = min(n_count, 12)  # Límite para simulación
    
    if N == 15:
        qc = shor_circuit_15(a, n_count)
    else:
        qc = create_general_qpe_circuit(N, a, n_count)
    
    # *** FIX: Decompose the circuit into basic gates ***
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

# Prueba rápida
test_result = shor_factor(15, shots=1024)
print(f"Prueba N=15: {test_result}")
