"""
NUEVAS FUNCIONES Y CELDAS PARA ComputacionCuantica.ipynb (VERSIÓN 2)
=====================================================================

Incluye la mejora de 'Shor con Ejecución Cuántica Forzada' (force_quantum).

Instrucciones:
Copiar y reemplazar las celdas correspondientes en el notebook.
"""

import time
import numpy as np
import math
from fractions import Fraction
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# =====================================================================
# CELDA 1: REEMPLAZAR generate_semiprimes
# =====================================================================

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

def generate_semiprimes(n_bits, count):
    min_val, max_val = 2**(n_bits-1), 2**n_bits - 1
    
    # Umbral dinámico: bits pequeños necesitan primos pequeños
    if n_bits <= 6:
        MIN_PRIME = 3
    elif n_bits <= 8:
        MIN_PRIME = 7
    else:
        MIN_PRIME = 11  # Evitar primos muy pequeños para reducir gcd_luck trivial
    
    primes = [n for n in range(MIN_PRIME, max_val // 2 + 1) if is_prime(n)]
    
    semiprimes = []
    sqrt_limit = int(math.isqrt(max_val))
    
    for i, p in enumerate(primes):
        if p > sqrt_limit:
            break
        for q in primes[i:]: 
            N = p * q
            if N > max_val:
                break
            if min_val <= N <= max_val and p != q:
                # Filtrar factores muy desbalanceados
                ratio = max(p, q) / min(p, q)
                if ratio < 10:
                    semiprimes.append((N, p, q))
                
    np.random.shuffle(semiprimes)
    return semiprimes[:count]

# =====================================================================
# CELDA 2: REEMPLAZAR shor_factor_detailed (Implementa force_quantum)
# =====================================================================

def shor_factor_detailed(N, shots, max_attempts=10, force_quantum=True):
    """
    Ejecuta Shor con clasificación detallada.
    
    Args:
        force_quantum (bool): Si True, descarta los casos donde gcd(a, N) > 1 (suerte clásica)
                              y reintenta con otro 'a' para forzar el uso del circuito cuántico.
                              Esto aísla el rendimiento del núcleo cuántico.
    """
    t0 = time.time()
    qubits_used = 0
    
    if N % 2 == 0:
        return {'success': True, 'factors': [2, N//2], 'attempts': 0,
                'time': 0, 'qubits': 0, 'method': 'trivial_even',
                'is_quantum': False, 'fail_reason': None}
    
    for attempt in range(1, max_attempts + 1):
        # Elegir 'a' aleatorio
        a = np.random.randint(2, N - 1)
        
        # Verificar MCD (éxito clásico trivial)
        g = gcd(a, N)
        if g > 1:
            if force_quantum:
                # Si forzamos cuántico, ignoramos este éxito "fácil" y buscamos otro 'a'
                continue 
            else:
                return {'success': True, 'factors': sorted([g, N//g]), 'attempts': attempt,
                        'time': time.time()-t0, 'qubits': 0, 'method': 'gcd_luck',
                        'is_quantum': False, 'fail_reason': None, 'a': a}
        
        # --- AQUÍ COMIENZA EL NÚCLEO CUÁNTICO ---
        n_count = min(12, max(4, 2 * N.bit_length()))
        qc = create_shor_circuit(N, a, n_count)
        qubits_used = qc.num_qubits

        qc_decomposed = qc.decompose()
        
        sim = AerSimulator()
        counts = sim.run(qc_decomposed, shots=shots).result().get_counts()
        
        # Post-procesamiento clásico de la salida cuántica
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
            continue  # fail_no_period
        
        if r_found % 2 != 0:
            continue  # fail_r_odd
        
        x = mod_exp(a, r_found // 2, N)
        if x == 1 or x == N - 1:
            continue  # fail_trivial_root
        
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


# =====================================================================
# CELDA 3: REEMPLAZAR run_experiment (pasa el parámetro force_quantum)
# =====================================================================

def run_experiment():
    rows = []
    # Nota: Asegúrate de que FORCE_QUANTUM esté definido o pásalo directo
    FORCE_QUANTUM_MODE = True 
    print(f"Iniciando experimento con FORCE_QUANTUM = {FORCE_QUANTUM_MODE}")
    print("(Se descartarán éxitos triviales por MCD para probar el circuito cuántico)")
    
    total = sum(len(test_semiprimes.get(n,[])) for n in BIT_RANGE) * len(M_SHOTS_LIST) * R
    
    with tqdm(total=total, desc="Experimento") as pbar:
        for n_bits in BIT_RANGE:
            for N, p, q in test_semiprimes.get(n_bits, []):
                for M in M_SHOTS_LIST:
                    for rep in range(1, R + 1):
                        # Llamada con force_quantum
                        res = shor_factor_detailed(N, shots=M, force_quantum=FORCE_QUANTUM_MODE)
                        
                        rows.append({
                            'n_bits': n_bits, 'N': N, 'p_true': p, 'q_true': q,
                            'M_shots': M, 'rep': rep,
                            'success': int(res['success']),
                            'is_quantum': int(res['is_quantum']),
                            'method': res['method'],
                            'attempts': res['attempts'],
                            'time_sec': res['time'],
                            'qubits': res['qubits']
                        })
                        pbar.update(1)
    return pd.DataFrame(rows)


# =====================================================================
# CELDA 4: NUEVA GRÁFICA (Comparativa ajustada)
# =====================================================================

def plot_quantum_analysis_v2(df):
    """Gráficas de análisis cuántico (Versión Force Quantum)"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Filtramos casos que NO sean gcd_luck (si force_quantum=True, no debería haberlos,
    # pero filtramos por seguridad o para comparar con datos viejos)
    df_pure = df[df['method'] != 'gcd_luck']
    
    # 1. Tasa de Éxito Cuántico Puro por Bits
    ax1 = axes[0]
    bits = sorted(df_pure['n_bits'].unique())
    rates = []
    for n in bits:
        sub = df_pure[df_pure['n_bits'] == n]
        if len(sub) > 0:
            rate = sub['success'].mean() * 100
            rates.append(rate)
        else:
            rates.append(0)
            
    ax1.plot(bits, rates, 'o-', color='purple', linewidth=2)
    ax1.fill_between(bits, rates, alpha=0.3, color='purple')
    ax1.set_title('Tasa de Éxito del NÚCLEO CUÁNTICO (Sin ayuda clásica)', fontsize=12)
    ax1.set_xlabel('Tamaño del Semiprimo (bits)')
    ax1.set_ylabel('Éxito (%)')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 105)
    
    # 2. Barras Apiladas: Cuántico vs Fallos
    ax2 = axes[1]
    q_counts = []
    f_counts = []
    
    for n in bits:
        sub = df_pure[df_pure['n_bits'] == n]
        q = len(sub[sub['method'] == 'quantum_success'])
        f = len(sub[sub['success'] == 0]) # Fallos
        total = q + f
        if total > 0:
            q_counts.append(q / total * 100)
            f_counts.append(f / total * 100)
        else:
            q_counts.append(0)
            f_counts.append(0)
            
    x = np.arange(len(bits))
    ax2.bar(x, q_counts, label='Éxito Cuántico', color='green', alpha=0.7)
    ax2.bar(x, f_counts, bottom=q_counts, label='Fracaso (Timeout/Ruido)', color='red', alpha=0.7)
    
    ax2.set_title('Proporción: Éxito Cuántico vs Fracasos', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(bits)
    ax2.set_xlabel('Tamaño (bits)')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f"{DATA_DIR}/force_quantum_analysis.png", dpi=150)
    plt.show()

# Ejecutar análisis visual
plot_quantum_analysis_v2(df)

