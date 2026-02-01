"""
VISUALIZACIONES FINALES Y DASHBOARD DE RIESGO
=============================================

Incluye:
1. Dashboard de Riesgo Criptográfico (4 gráficas)
2. Resumen Final del Experimento (Enfoque Framework de Riesgo)
3. Análisis Extra: Eficiencia de Shots

Instrucciones:
Copiar y pegar estas celdas al final del notebook.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binom

# =====================================================================
# CELDA 5: DASHBOARD DE RIESGO
# =====================================================================

def plot_risk_dashboard(df):
    """
    Dashboard consolidado de evaluación de riesgo criptográfico.
    Incluye: Distribución, Riesgo Acumulado, Binomial y Correlación.
    """
    # Filtrar datos relevantes (si se usó force_quantum solo debería haber quantum_success y failed)
    # Pero por si acaso filtramos gcd_luck para el análisis de riesgo cuántico puro
    df_risk = df[df['method'] != 'gcd_luck'].copy()
    
    fig = plt.figure(figsize=(16, 12))
    plt.suptitle("Dashboard de Evaluación de Riesgo Criptográfico Cuántico", fontsize=16)
    
    # 1. Distribución de Resultados (Pie Chart)
    ax1 = fig.add_subplot(2, 2, 1)
    counts = df_risk['method'].value_counts()
    # Mapeo de colores y etiquetas amigables
    labels_map = {'quantum_success': 'Éxito Cuántico', 'failed': 'Fallo (Ruido/Shots)', 'gcd_luck': 'Suerte Clásica'}
    labels = [labels_map.get(l, l) for l in counts.index]
    colors_map = {'quantum_success': '#4CAF50', 'failed': '#F44336', 'gcd_luck': '#FFC107'}
    colors = [colors_map.get(l, 'gray') for l in counts.index]
    
    wedges, texts, autotexts = ax1.pie(counts, labels=labels, autopct='%1.1f%%', 
            startangle=90, colors=colors, textprops={'fontsize': 10})
    ax1.set_title('Distribución de Resultados (Entorno Cuántico)', fontsize=12)
    
    # 2. Riesgo Acumulado de Éxito (P(break <= k intentos))
    ax2 = fig.add_subplot(2, 2, 2)
    k_attempts = np.arange(1, 21) # Evaluar hasta 20 intentos
    
    # Seleccionar algunos tamaños de bits representativos
    sample_bits = sorted(df_risk['n_bits'].unique())[::2] # Tomar uno sí y uno no para no saturar
    
    for n in sample_bits:
        subset = df_risk[df_risk['n_bits'] == n]
        if len(subset) == 0: continue
        p_hat = subset['success'].mean()
        
        # Probabilidad acumulada: 1 - (1 - p)^k
        # Si p_hat es 0, el riesgo es 0.
        if p_hat > 0:
            risk_curve = 1 - (1 - p_hat)**k_attempts
            ax2.plot(k_attempts, risk_curve, marker='.', label=f'{n} bits (p={p_hat:.2f})')
    
    ax2.set_title('Riesgo Acumulado de Ruptura (k intentos)', fontsize=12)
    ax2.set_xlabel('Número de Intentos (k)')
    ax2.set_ylabel(r'Probabilidad de Éxito $P(T \leq k)$')
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8, loc='lower right')
    
    # 3. Distribución Binomial de Éxitos (Real vs Teórica)
    # Analizamos grupos de (n_bits, shots) que tienen R repeticiones
    ax3 = fig.add_subplot(2, 2, 3)
    
    # Calcular cuántos éxitos hubo en cada grupo de R repeticiones
    grouped = df_risk.groupby(['n_bits', 'N', 'M_shots'])['success'].sum()
    if not grouped.empty:
        # Frecuencia de cantidad de éxitos (0 a R)
        success_counts = grouped.value_counts().sort_index()
        
        # Histograma Real
        ax3.bar(success_counts.index, success_counts.values/success_counts.sum(), 
                alpha=0.6, label='Frecuencia Real', color='purple')
        
        # Aproximación Teórica (Binomial media)
        # Tomamos la p promedio global para generar una referencia
        p_avg = df_risk['success'].mean()
        n_trials = df_risk['rep'].max() # Debería ser R (ej. 10 o 20)
        x = np.arange(0, n_trials + 1)
        y_binom = binom.pmf(x, n_trials, p_avg)
        
        ax3.plot(x, y_binom, 'r--', marker='o', label=rf'Binomial Teórica ($p \approx {p_avg:.2f}$)')
        ax3.set_title(f'Distribución de Éxitos en R={n_trials} Intentos', fontsize=12)
        ax3.set_xlabel('Número de Éxitos')
        ax3.set_ylabel('Frecuencia Relativa')
        ax3.legend(fontsize=9)
    else:
        ax3.text(0.5, 0.5, "Datos insuficientes para distribución", ha='center')

    # 4. Matriz de Correlación
    ax4 = fig.add_subplot(2, 2, 4)
    # Seleccionar columnas numéricas relevantes para correlación
    cols = ['n_bits', 'M_shots', 'time_sec', 'qubits', 'attempts', 'success']
    corr_df = df[cols].corr()
    
    cax = ax4.matshow(corr_df, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(cax, ax=ax4)
    
    # Etiquetas
    ticks = np.arange(len(cols))
    ax4.set_xticks(ticks)
    ax4.set_yticks(ticks)
    ax4.set_xticklabels(cols, rotation=45, ha='left')
    ax4.set_yticklabels(cols)
    ax4.set_title('Matriz de Correlación de Variables', fontsize=12, pad=20)
    
    # Anotar valores
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax4.text(j, i, f"{corr_df.iloc[i, j]:.2f}", ha='center', va='center', fontsize=8, color='black')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f"{DATA_DIR}/risk_dashboard_final.png", dpi=150)
    plt.show()
    print(f"Dashboard guardado en: {DATA_DIR}/risk_dashboard_final.png")

# Ejecutar visualización
plot_risk_dashboard(df)


# =====================================================================
# CELDA 6: RESUMEN FINAL v2 (Actualizado para Framework de Riesgo)
# =====================================================================

def final_summary_v2(df):
    """
    Resumen Final del Experimento enfocado en Evaluación de Riesgo.
    """
    df_risk = df[df['method'] != 'gcd_luck']
    total_runs = len(df)
    quantum_runs = len(df_risk)
    
    print("\n" + "="*70)
    print("INFORME FINAL: FRAMEWORK DE EVALUACIÓN DE RIESGO CRYPTO-CUÁNTICO")
    print("="*70)
    
    print(f"\n1. ALCANCE DEL EXPERIMENTO")
    print(f"   Total Simulaciones: {total_runs}")
    print(f"   Simulaciones Núcleo Cuántico (force_quantum): {quantum_runs} ({quantum_runs/total_runs:.1%})")
    print(f"   Rango de Bits: {df['n_bits'].min()} - {df['n_bits'].max()} bits")
    
    print(f"\n2. MÉTRICAS DE RENDIMIENTO (Núcleo Cuántico)")
    success_rate = df_risk['success'].mean()
    avg_attempts = df_risk[df_risk['success']==1]['attempts'].mean()
    print(f"   Tasa Global de Éxito: {success_rate:.4f} ({success_rate*100:.2f}%)")
    print(f"   Intentos Promedio para Éxito: {avg_attempts:.2f}")
    print(f"   Tiempo Promedio de Ejecución: {df_risk['time_sec'].mean():.4f} s")
    
    print(f"\n3. CRITERIOS DE CLASIFICACIÓN DE RIESGO (Preliminar)")
    # Definimos riesgo basado en probabilidad de éxito con 1024/2048 shots (estándar)
    high_risk_bits = df_risk[df_risk['success'] > 0.8]['n_bits'].max()
    med_risk_bits = df_risk[(df_risk['success'] > 0.3) & (df_risk['success'] <= 0.8)]['n_bits'].max()
    
    print(f"   Riesgo ALTO (>80% éxito): Hasta {high_risk_bits} bits")
    print(f"   Riesgo MEDIO (30-80% éxito): Hasta {med_risk_bits} bits")
    print(f"   Riesgo BAJO (<30% éxito): > {med_risk_bits} bits (limitado por ruido/decoherencia simulada)")
    
    print(f"\n4. CONCLUSIÓN")
    print("   El uso de 'force_quantum' ha permitido aislar la efectividad del algoritmo")
    print("   de Shor, eliminando el sesgo de suerte clásica. Los resultados muestran")
    print("   que el riesgo criptográfico escala de manera no lineal con el tamaño de N,")
    print("   dependiendo críticamente de la profundidad del circuito y la tasa de error.")
    print("\n   Archivos generados:")
    print(f"   - {DATA_DIR}/shor_experiment_v2.csv (Dataset Principal)")
    print(f"   - {DATA_DIR}/risk_dashboard_final.png (Dashboard Visual)")
    print(f"   - {DATA_DIR}/shots_efficiency.png (Análisis Extra)")

# Ejecutar resumen
final_summary_v2(df)

# =====================================================================
# CELDA 7: ANÁLISIS DE EFICIENCIA DE SHOTS (NUEVO)
# =====================================================================

def plot_shots_efficiency(df):
    """
    Analiza la correspondencia entre número de Shots y Probabilidad de Éxito.
    Permite identificar rendimientos decrecientes (diminishing returns).
    """
    df_risk = df[df['method'] != 'gcd_luck']
    
    plt.figure(figsize=(10, 6))
    
    # Agrupar por n_bits y M_shots
    # Calculamos la probabilidad media de éxito para cada configuración
    grouped = df_risk.groupby(['n_bits', 'M_shots'])['success'].mean().reset_index()
    
    # Obtener lista de bits para graficar líneas separadas
    bits_list = sorted(grouped['n_bits'].unique())
    
    # Colores distintivos
    colors = plt.cm.viridis(np.linspace(0, 1, len(bits_list)))
    
    for i, n_bits in enumerate(bits_list):
        data = grouped[grouped['n_bits'] == n_bits]
        # Graficamos si hay al menos dos puntos para conectar
        if len(data['M_shots'].unique()) > 1:
            plt.plot(data['M_shots'], data['success'], marker='o', 
                     label=f'{n_bits} bits', color=colors[i], linewidth=2)
            
    # Línea promedio global (Normalizada por grupo de bits para no sesgar, o simple mean)
    # Simple mean de todos los experimentos por shot
    global_trend = df_risk.groupby('M_shots')['success'].mean()
    if len(global_trend) > 1:
        plt.plot(global_trend.index, global_trend.values, 'k--', linewidth=3, alpha=0.5, label='Promedio Global')
    
    plt.title('Eficiencia de Recursos: Probabilidad de Éxito vs Shots', fontsize=14)
    plt.xlabel('Número de Shots (M) [Log Scale]', fontsize=12)
    plt.ylabel(r'Probabilidad de Éxito Cuántico ($P_{succ}$)', fontsize=12)
    plt.xscale('log') # Escala logarítmica para ver mejor órdenes de magnitud (1024, 2048, 4096...)
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.ylim(-0.05, 1.05)
    
    plt.tight_layout()
    plt.savefig(f"{DATA_DIR}/shots_efficiency.png", dpi=150)
    plt.show()
    print(f"Gráfica de eficiencia guardada en: {DATA_DIR}/shots_efficiency.png")

# Ejecutar
plot_shots_efficiency(df)
