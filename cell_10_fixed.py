def shor_factor_detailed(N, shots, max_attempts=10):
    """
    Ejecuta Shor con clasificación detallada:
    - gcd_luck: éxito por MCD (clásico)
    - quantum_success: éxito cuántico real
    - fail_r_odd: r impar
    - fail_trivial: a^(r/2) ≡ ±1 mod N
    - fail_no_period: no se encontró período
    """
    t0 = time.time()
    qubits_used = 0
    
    if N % 2 == 0:
        return {'success': True, 'factors': [2, N//2], 'attempts': 0,
                'time': 0, 'qubits': 0, 'method': 'trivial_even',
                'is_quantum': False, 'fail_reason': None}
    
    for attempt in range(1, max_attempts + 1):
        a = np.random.randint(2, N - 1)
        
        # Verificar MCD (éxito clásico)
        g = gcd(a, N)
        if g > 1:
            return {'success': True, 'factors': sorted([g, N//g]), 'attempts': attempt,
                    'time': time.time()-t0, 'qubits': 0, 'method': 'gcd_luck',
                    'is_quantum': False, 'fail_reason': None, 'a': a}
        
        # Ejecutar QPE cuántico
        n_count = min(12, max(4, 2 * N.bit_length()))
        qc = create_shor_circuit(N, a, n_count)
        qubits_used = qc.num_qubits
        
        # *** FIX: Decompose circuit for AerSimulator ***
        qc_decomposed = qc.decompose()
        
        sim = AerSimulator()
        # Use decomposed circuit
        counts = sim.run(qc_decomposed, shots=shots).result().get_counts()
        
        # Buscar período
        r_found = None
        for output, cnt in sorted(counts.items(), key=lambda x: -x[1]):
            decimal = int(output, 2)
            if decimal == 0: continue
            phase = decimal / (2**n_count)
            frac = Fraction(phase).limit_denominator(N)
            r = frac.denominator
            if r > 1 and mod_exp(a, r, N) == 1:
                r_found = r
                break
        
        if r_found is None:
            continue  # fail_no_period, seguir intentando
        
        # Verificar condiciones
        if r_found % 2 != 0:
            continue  # fail_r_odd
        
        x = mod_exp(a, r_found // 2, N)
        if x == 1 or x == N - 1:
            continue  # fail_trivial: a^(r/2) ≡ ±1
        
        # Intentar factorizar
        f1, f2 = gcd(x-1, N), gcd(x+1, N)
        if 1 < f1 < N:
            return {'success': True, 'factors': sorted([f1, N//f1]), 'attempts': attempt,
                    'time': time.time()-t0, 'qubits': qubits_used, 'method': 'quantum_success',
                    'is_quantum': True, 'fail_reason': None, 'a': a, 'r': r_found}
        if 1 < f2 < N:
            return {'success': True, 'factors': sorted([f2, N//f2]), 'attempts': attempt,
                    'time': time.time()-t0, 'qubits': qubits_used, 'method': 'quantum_success',
                    'is_quantum': True, 'fail_reason': None, 'a': a, 'r': r_found}
    
    return {'success': False, 'factors': [], 'attempts': max_attempts,
            'time': time.time()-t0, 'qubits': qubits_used, 'method': 'failed',
            'is_quantum': False, 'fail_reason': 'max_attempts'}

# Test
test = shor_factor_detailed(15, 1024)
print(f"Test N=15: {test['method']}, success={test['success']}")
