# Factorización de números semiprimos con métodos clásicos y computación cuántica

Proyecto académico que compara aproximaciones clásicas y cuánticas para factorizar números semiprimos, incluyendo simulaciones locales, experimentos en hardware cuántico real (IBM Quantum) y análisis estadístico de resultados.

---

## Objetivo investigativo

Este proyecto busca responder empíricamente:

> *¿Existe una ventaja cuantificable del algoritmo de Shor sobre métodos clásicos (Pollard's Rho) para la factorización de números semiprimos pequeños, bajo condiciones de hardware cuántico real disponible hoy?*

Para ello se diseñaron experimentos reproducibles que miden tasa de éxito, tiempo de ejecución, uso de qubits y número de intentos, comparando ambos métodos en rangos de 4 a 17 bits.

**Alcance y limitaciones:**
- Los experimentos cubren semiprimos de **4 a 17 bits** — lejos de los tamaños usados en criptografía RSA real (2048+ bits).
- Este proyecto **no representa una amenaza a sistemas criptográficos actuales**. Su propósito es académico: estudiar el comportamiento del algoritmo de Shor en hardware cuántico disponible hoy.
- Los resultados con IBM Quantum son reales y verificables, pero están sujetos a las limitaciones de decoherencia del hardware actual (NISQ era).

---

## Estructura del repositorio

```
factorizacion_numeros_semiprimos/
│
├── ComputacionCuantica.ipynb          # Notebook principal del experimento
├── nuevas_funciones_shor_v2.py        # Implementación del algoritmo de Shor
├── visualizaciones_finales.py         # Scripts de generación de figuras
│
├── notebooks/
│   └── archive/                       # Versiones históricas del notebook
│       ├── 01_gcd_luck.ipynb          # Iteración 1: método GCD Luck
│       ├── 02_primer_exito_cuantico.ipynb  # Iteración 3: primer éxito cuántico
│       └── 03_algoritmo_optimizado.ipynb   # Iteración 4: rango 4-17 bits
│
├── datasets/                          # Todos los resultados experimentales
│   ├── README.md                      # Diccionario de datos completo
│   ├── 0.0_beta.algoritmo_simulado/   # Beta: validación inicial (simulado clásico)
│   ├── 0.1_ibm_algoritmo/             # ⭐ IBM Quantum hardware real (QPU)
│   ├── 1.gdc_luck_algoritmo_uno/      # Iteración 1: método GCD Luck
│   ├── 2.algorirmo_dos/               # Iteración 2: distinción clásico/cuántico
│   ├── 3.primer_exito_algoritmo_tres/ # Iteración 3: primer éxito cuántico
│   ├── 4.algoritmo_optimizado_4-17 bits/ # Iteración 4: rango optimizado
│   └── 5.aislar_cuantico_de_parte_clasica/ # ⭐ Dataset final (22,470 registros)
│
├── docs/
│   └── guia_ibm_quantum.md            # Guía paso a paso para ejecutar en IBM Quantum
│
├── INFORME ESTADÍSTICO CUANTICO.pdf   # Informe completo del proyecto
├── .env.example                       # Plantilla de variables de entorno
├── .gitignore                         # Exclusiones de Git
└── requirements.txt                   # Dependencias del proyecto
```

---

## Requisitos

- Python 3.11+
- Jupyter Notebook o JupyterLab
- Qiskit >= 1.0.0
- Qiskit Aer >= 0.14.0 (simulación local)
- Qiskit IBM Runtime >= 0.20.0 (ejecución en IBM Quantum)
- numpy, pandas, matplotlib, scipy
- python-dotenv

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Alejandr05ang/factorizacion_numeros_semiprimos.git
cd factorizacion_numeros_semiprimos

# 2. Crear y activar un entorno virtual
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Configuración — IBM Quantum

Para ejecutar en hardware cuántico real se requiere un token de IBM Quantum.

**Paso 1:** Obtener el token en [quantum.ibm.com](https://quantum.ibm.com) → Account → Copy token.

**Paso 2:** Crear un archivo `.env` en la raíz del proyecto basándose en la plantilla:

```bash
cp .env.example .env
```

Editar `.env` con tu token real:

```env
IBM_QUANTUM_TOKEN=tu_token_real_aqui
IBM_CHANNEL=ibm_quantum
```

> ⚠️ **El archivo `.env` está excluido de Git** por `.gitignore`. Nunca lo subas al repositorio.

**Paso 3:** El notebook carga el token automáticamente con `os.getenv("IBM_QUANTUM_TOKEN")`. No es necesario pegarlo manualmente en el código.

Para instrucciones detalladas de autenticación, selección de backend y troubleshooting, ver [`docs/guia_ibm_quantum.md`](docs/guia_ibm_quantum.md).

---

## Cómo ejecutar

### Experimento principal (simulación local)

```bash
# Activar entorno virtual
.\.venv\Scripts\activate

# Abrir el notebook
jupyter notebook ComputacionCuantica.ipynb
```

Ejecutar las celdas en orden. Los resultados se generan en la carpeta `datasets/`.

### Generar visualizaciones

```bash
python visualizaciones_finales.py
```

Las figuras se guardan en las subcarpetas de `datasets/` correspondientes.

### Experimento en IBM Quantum (hardware real)

Requiere configurar `IBM_QUANTUM_TOKEN` como se describe arriba.  
Ver guía completa en [`docs/guia_ibm_quantum.md`](docs/guia_ibm_quantum.md).

---

## Datasets

Todos los resultados experimentales están documentados en [`datasets/README.md`](datasets/README.md).

**Datasets principales:**

| Dataset | Tipo | Registros | Descripción |
|---------|------|-----------|-------------|
| `datasets/5.aislar_cuantico_de_parte_clasica/shor_experiment_v2.csv` | Simulación cuántica | 22,470 | Dataset definitivo del experimento final |
| `datasets/0.1_ibm_algoritmo/batch_*_quantum.csv` | **IBM Hardware Real** | ~240 | Ejecuciones reales en QPU con `job_id` verificables |

Total en el repositorio: **~77,360 registros** en 34 archivos CSV.

---

## Seguridad

- **Nunca subas tu token de IBM Quantum** al repositorio.
- El archivo `.env` está excluido por `.gitignore`.
- Usar `.env.example` como referencia — no contiene credenciales reales.
- Antes de cada commit, verificar con `git status` que `.env` no aparezca como tracked.

---

## Estado del proyecto

> Este es un proyecto **académico e investigativo**. No es una herramienta de producción criptográfica.

El hardware cuántico actual (era NISQ) no tiene la capacidad de factorizar números del tamaño utilizado en criptografía RSA. Los resultados de este proyecto son contribuciones al entendimiento empírico del comportamiento del algoritmo de Shor bajo condiciones reales de decoherencia y ruido cuántico.

---

## Referencias

- Shor, P. W. (1994). *Algorithms for quantum computation: discrete logarithms and factoring*. Proceedings 35th Annual Symposium on Foundations of Computer Science. IEEE. https://doi.org/10.1109/SFCS.1994.365700

- IBM Quantum. (2024). *Qiskit IBM Runtime documentation*. https://docs.quantum.ibm.com

- Qiskit Community. (2024). *Qiskit: An open-source SDK for working with quantum computers*. https://qiskit.org

- NIST. (2024). *Post-Quantum Cryptography Standardization*. https://csrc.nist.gov/projects/post-quantum-cryptography

---

## Licencia

Proyecto académico — Universidad. Uso educativo y de investigación.
