def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

def generate_semiprimes(n_bits, count):
    min_val, max_val = 2**(n_bits-1), 2**n_bits - 1
    
    # *** CHANGE: Start range from 3 to exclude 2 (even numbers) ***
    # This ensures all generated semiprimes are ODD
    primes = [n for n in range(3, max_val // 2 + 1) if is_prime(n)]
    
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
                semiprimes.append((N, p, q))
                
    np.random.shuffle(semiprimes)
    return semiprimes[:count]

# Regenerate test semiprimes
test_semiprimes = {n: generate_semiprimes(n, SEMIPRIMES_PER_SIZE) for n in BIT_RANGE}
for n, sp in test_semiprimes.items():
    if sp: print(f"{n} bits: {len(sp)} semiprimos, ej: N={sp[0][0]}={sp[0][1]}×{sp[0][2]}")
