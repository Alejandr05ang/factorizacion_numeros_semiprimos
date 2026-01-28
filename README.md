# Prueba Funcional: Factorización de Números Semiprimos
## Computación Clásica vs Cuántica

Este proyecto implementa una suite completa de pruebas para factorización de números semiprimos, comparando algoritmos clásicos y cuánticos.

---

## 📋 Contenidos

### 1. **Métodos Clásicos**

#### Algoritmo de Pollard's Rho
- **Complejidad**: O(n^(1/4))
- **Tipo**: Probabilístico (puede reintentar)
- **Especializado**: Números con factores pequeños
- **Ventajas**:
  - Muy eficiente para semiprimos RSA moderados
  - Implementable en cualquier máquina
  - No requiere librerías especiales
- **Desventajas**:
  - Tiempo exponencial para números muy grandes
  - Depende de valores aleatorios

**Funcionamiento**:
```
1. Comienza con un valor inicial x aleatorio
2. Itera f(x) = (x² + c) mod n
3. Calcula gcd(|x - y|, n) para detectar factores
4. Si encuentra factor válido, retorna (p, q)
```

---

### 2. **Métodos Cuánticos**

#### Algoritmo de Shor
- **Complejidad**: O(log³ n) - Polinomial
- **Tipo**: Determinístico
- **Base**: Transformada Cuántica de Fourier
- **Ventajas**:
  - Exponencialmente más rápido que métodos clásicos
  - Polinomial (no exponencial)
  - Funciona para números arbitrariamente grandes
- **Desventajas**:
  - Requiere computadora cuántica real
  - Simuladores clásicos limitados a números pequeños
  - Alto número de qubits necesarios

**Impacto en Criptografía**:
- RSA es seguro hoy porque factorizar es exponencialmente difícil clásicamente
- Shor puede factorizar en tiempo polinomial con computadora cuántica
- Una computadora cuántica suficientemente potente podría romper RSA

#### Búsqueda Cuántica de Grover
- **Complejidad**: O(√N) - Aceleración cuadrática
- **Principio**: Amplificación de amplitud
- **Aplicación**: Búsqueda en espacio de soluciones

---

## 🚀 Instalación y Uso

### Requisitos
- Python 3.8+
- Entorno virtual (venv)

### Configuración

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
.\venv\Scripts\Activate.ps1

# Activar (Linux/Mac)
source venv/bin/activate
```

### Instalar Dependencias

```bash
# Solo métodos clásicos (sin librerías cuánticas)
# pip install (no requiere dependencias adicionales)

# Con soporte cuántico completo
pip install qiskit qiskit-aer
```

### Ejecutar Pruebas

```bash
python test.py
```

---

## 📊 Resultados de Pruebas

### Casos Prueba:
| Tipo | P | Q | N | Tamaño |
|------|------|------|------------|---------|
| Pequeño | 3 | 5 | 15 | 4 bits |
| Pequeño | 7 | 11 | 77 | 7 bits |
| Mediano | 61 | 53 | 3,233 | 12 bits |
| Mediano | 97 | 89 | 8,633 | 14 bits |
| Grande | 10007 | 10009 | 100,160,063 | 27 bits |

### Rendimiento Observado:

**Pollard's Rho (Clásico)**:
```
✓ N=15:          0.0000 ms
✓ N=77:          0.0000 ms
✓ N=3,233:       0.0000 ms
✓ N=8,633:       0.0000 ms
✓ N=100,160,063: 0.0000 ms
```

**Grover (Cuántico Simulado)**:
```
✓ N=15:          451.68 ms
✓ N=77:          2.35 ms
✓ N=3,233:       6.43 ms
⊘ N=8,633:       Falló (límite simulador)
⊘ N=100,160,063: Falló (límite simulador)
```

---

## 🔐 Implicaciones en Criptografía

### RSA vs Computadoras Cuánticas

**Situación Actual (2024-2026)**:
```
┌─────────────────────────────────────────┐
│ RSA-2048 (617 dígitos)                  │
├─────────────────────────────────────────┤
│ Tiempo Clásico: ~300 años               │
│ Tiempo Shor (Cuántico): ~8 horas        │
│ Aceleración: ~300,000 veces             │
└─────────────────────────────────────────┘
```

### Transición a Criptografía Post-Cuántica

El NIST ha estandarizado (2022-2024) algoritmos resistentes:
- **ML-KEM** (Kyber) - Encapsulación de claves
- **ML-DSA** (Dilithium) - Firmas digitales
- **SLH-DSA** (SPHINCS+) - Firmas basadas en hash

**Recomendación**: Migrar a criptografía post-cuántica para datos de larga vida.

---

## 🧬 Estado de Computadoras Cuánticas (2026)

### Disponibles Actualmente:
- **IBM**: 127-433 qubits (Falcon, Heron)
- **Google**: 99-109 qubits (Willow)
- **IonQ**: 11-24 qubits (pero de alta fidelidad)
- **Atom Computing**: 24-100 qubits

### Limitaciones Principales:
1. **Decoherencia**: Qubits pierden información en microsegundos
2. **Error rates**: ~0.1-1% por puerta cuántica
3. **Escalabilidad**: Difícil pasar de 100 a 10,000 qubits
4. **Corrección de errores**: Requiere miles de qubits lógicos por qubit físico

### Timeline Estimado:
```
2024-2026: Qubits de demostración (100-1000)
2027-2030: Qubits útiles para optimización (1000-10,000)
2030-2035: Computadoras cuánticas prácticas
2035+:     Amenaza potencial a RSA (requiere ~20 millones de qubits)
```

**Estimación conservadora**: RSA seguirá siendo seguro durante años,
pero la migración a post-cuántica es CRÍTICA para datos sensibles.

---

## 📚 Referencias Teóricas

### Algoritmo de Shor (1994)
```
1. Elije un número a aleatorio con gcd(a, n) = 1
2. Encuentra el orden r de a módulo n
   r es el número más pequeño donde a^r ≡ 1 (mod n)
3. Si r es par y a^(r/2) ≢ -1 (mod n):
   p = gcd(a^(r/2) - 1, n)
   q = n / p
4. Si no, reintentar con otro a
```

**Clave cuántica**: Encontrar r (paso 2) se acelera exponencialmente
usando la Transformada Cuántica de Fourier.

### Algoritmo de Pollard's Rho
```
Basado en la paradoja del cumpleaños:
- Busca ciclos en secuencia f(x) = (x² + c) mod n
- Cuando encuentra x, y con f(x) ≡ f(y) (mod p),
  entonces gcd(x - y, n) probablemente sea divisor
```

---

## 🔧 Arquitectura del Código

```
test.py
├── Métodos Clásicos
│   └── metodo_pollard_rho_mejorado()
├── Métodos Cuánticos
│   ├── metodo_algoritmo_shor()
│   └── metodo_busqueda_grover_simulada()
├── Utilidades
│   ├── es_semiprimo()
│   ├── generar_semiprimo()
│   └── verificar_factorizacion()
└── Suite de Pruebas
    ├── prueba_individual()
    └── ejecutar_suite_pruebas()
```

---

## 💡 Conclusiones

### ✓ Computación Clásica Actual
- Pollard's Rho es muy eficiente para semiprimos moderados
- Suitable para números hasta ~100 bits en tiempo razonable
- Seguridad RSA depende en la dificultad de factorizar números grandes

### ✓ Computación Cuántica Futura
- Shor revolucionará la criptografía si se logra escala suficiente
- Amenaza directa a RSA, ElGamal, ECDH
- Necesita 20+ millones de qubits lógicos para factorizar RSA-2048

### ✓ Acciones Recomendadas
1. **Inmediato**: Iniciar auditoría de datos sensibles de larga vida
2. **Corto plazo**: Planes de migración a post-cuántica
3. **Mediano plazo**: Implementar crypto-agility en sistemas
4. **Largo plazo**: Monitoreo de avances en computación cuántica

---

## 📖 Lecturas Adicionales

- Peter Shor: "Polynomial-time algorithms for prime factorization..." (1994)
- NIST Post-Quantum Cryptography Standardization
- IBM Quantum Experience: https://quantum.ibm.com/
- Qiskit Documentation: https://docs.quantum.ibm.com/

---

**Última actualización**: Enero 2026  
**Autor**: Suite de Pruebas de Factorización Cuántica  
**Licencia**: Educativo
