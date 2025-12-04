import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from analizar_datasets import dataframes
from typing import List, Tuple

def configurar_estilos():
    """Configura los estilos de matplotlib y seaborn"""
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10

def crear_carpeta_resultados():
    """Crea la carpeta para guardar gráficas si no existe"""
    carpeta = "graficas_correlacion"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
        print(f"Carpeta creada: {carpeta}")
    return carpeta

def obtener_pares_variables(df, max_pares=20):
    """
    Selecciona pares de variables para graficar, priorizando numéricas
    """
    # Obtener columnas numéricas (excluyendo 'Label')
    columnas_numericas = [col for col in df.select_dtypes(include=[np.number]).columns 
                         if col != 'Label']
    
    # Obtener columnas categóricas
    columnas_categoricas = [col for col in df.select_dtypes(include=['object', 'category']).columns 
                           if col != 'Label']
    
    pares = []
    
    # Priorizar: numérica vs numérica
    for i, col1 in enumerate(columnas_numericas):
        for j, col2 in enumerate(columnas_numericas):
            if i < j and len(pares) < max_pares // 2:
                pares.append(('numerica', 'numerica', col1, col2))
    
    # Agregar: numérica vs categórica
    for num_col in columnas_numericas[:3]:  # Máximo 3 numéricas
        for cat_col in columnas_categoricas[:2]:  # Máximo 2 categóricas por numérica
            if len(pares) < max_pares:
                pares.append(('numerica', 'categorica', num_col, cat_col))
    
    return pares

def graficar_correlacion_numerica(df, col_x, col_y, ax, dataset_nombre):
    """
    Grafica correlación entre dos variables numéricas
    """
    # Calcular correlación
    correlacion = df[[col_x, col_y]].corr().iloc[0, 1]
    
    # Crear scatter plot
    scatter = ax.scatter(df[col_x], df[col_y], alpha=0.6, s=30, 
                        c=df[col_y] if col_y != 'y' else df[col_x], 
                        cmap='viridis')
    
    # Añadir línea de tendencia
    if not df[[col_x, col_y]].isna().any().any():
        z = np.polyfit(df[col_x], df[col_y], 1)
        p = np.poly1d(z)
        ax.plot(df[col_x], p(df[col_x]), "r--", alpha=0.8, linewidth=1)
    
    # Configurar el gráfico
    ax.set_xlabel(col_x)
    ax.set_ylabel(col_y)
    ax.set_title(f'{col_x} vs {col_y}\nCorrelación: {correlacion:.3f}')
    ax.grid(True, alpha=0.3)
    
    # Añadir colorbar si es útil
    if col_y != 'y':
        plt.colorbar(scatter, ax=ax, label=col_y)
    
    return correlacion

def graficar_correlacion_categorica(df, col_num, col_cat, ax, dataset_nombre):
    """
    Grafica relación entre variable numérica y categórica
    """
    # Crear boxplot
    df_boxplot = df[[col_num, col_cat]].copy()
    df_boxplot[col_cat] = df_boxplot[col_cat].astype(str)  # Asegurar que es string
    
    # Limitar categorías si hay muchas
    valores_unicos = df_boxplot[col_cat].unique()
    if len(valores_unicos) > 10:
        # Tomar las 10 categorías más frecuentes
        top_categorias = df_boxplot[col_cat].value_counts().head(10).index
        df_boxplot = df_boxplot[df_boxplot[col_cat].isin(top_categorias)]
    
    sns.boxplot(data=df_boxplot, x=col_cat, y=col_num, ax=ax)
    
    # Configurar el gráfico
    ax.set_xlabel(col_cat)
    ax.set_ylabel(col_num)
    ax.set_title(f'{col_num} por {col_cat}')
    ax.tick_params(axis='x', rotation=45)
    
    # Calcular correlation ratio (eta)
    correlation_ratio = calcular_correlation_ratio(df[col_num], df[col_cat])
    ax.text(0.05, 0.95, f'Correlation Ratio: {correlation_ratio:.3f}', 
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    return correlation_ratio

def calcular_correlation_ratio(numeric, categorical):
    """Calcula correlation ratio para numérica vs categórica"""
    try:
        categories = categorical.unique()
        mean_global = numeric.mean()
        
        ss_between = 0
        ss_total = 0
        
        for cat in categories:
            group = numeric[categorical == cat]
            if len(group) > 0:
                mean_group = group.mean()
                ss_between += len(group) * (mean_group - mean_global) ** 2
        
        ss_total = ((numeric - mean_global) ** 2).sum()
        
        return np.sqrt(ss_between / ss_total) if ss_total > 0 else 0
    except:
        return 0

def crear_matriz_correlacion(df, dataset_nombre, carpeta_resultados):
    """
    Crea y guarda matriz de correlación para variables numéricas
    """
    columnas_numericas = [col for col in df.select_dtypes(include=[np.number]).columns 
                         if col != 'Label']
    
    if len(columnas_numericas) < 2:
        print(f"  No hay suficientes variables numéricas en {dataset_nombre}")
        return
    
    # Calcular matriz de correlación
    corr_matrix = df[columnas_numericas].corr()
    
    # Crear heatmap
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', 
                center=0, square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
    
    plt.title(f'Matriz de Correlación - {dataset_nombre}\n', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Guardar
    ruta_guardado = os.path.join(carpeta_resultados, f'matriz_correlacion_{dataset_nombre}.png')
    plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"  Matriz de correlación guardada: {ruta_guardado}")

def analizar_dataset_completo(df, dataset_nombre, carpeta_resultados):
    """
    Analiza y grafica correlaciones para un dataset completo
    """
    print(f"\n{'='*60}")
    print(f"ANALIZANDO: {dataset_nombre}")
    print(f"{'='*60}")
    
    print(f"Dimensiones: {df.shape}")
    
    # Obtener información de columnas
    columnas_numericas = [col for col in df.select_dtypes(include=[np.number]).columns 
                         if col != 'Label']
    columnas_categoricas = [col for col in df.select_dtypes(include=['object', 'category']).columns 
                           if col != 'Label']
    
    print(f"Variables numéricas ({len(columnas_numericas)}): {columnas_numericas}")
    print(f"Variables categóricas ({len(columnas_categoricas)}): {columnas_categoricas}")
    
    # 1. Crear matriz de correlación
    crear_matriz_correlacion(df, dataset_nombre, carpeta_resultados)
    
    # 2. Crear gráficas individuales
    pares_variables = obtener_pares_variables(df, max_pares=12)
    
    if not pares_variables:
        print("  No se encontraron pares de variables para graficar")
        return
    
    # Crear subplots
    n_pares = len(pares_variables)
    n_cols = 3
    n_rows = (n_pares + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_pares == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    metricas_correlacion = []
    
    for idx, (tipo_x, tipo_y, col_x, col_y) in enumerate(pares_variables):
        if idx >= len(axes):
            break
            
        ax = axes[idx]
        
        try:
            if tipo_x == 'numerica' and tipo_y == 'numerica':
                correlacion = graficar_correlacion_numerica(df, col_x, col_y, ax, dataset_nombre)
                metricas_correlacion.append({
                    'dataset': dataset_nombre,
                    'variable_x': col_x,
                    'variable_y': col_y,
                    'tipo': 'numérica-numérica',
                    'correlacion': correlacion
                })
                
            elif tipo_x == 'numerica' and tipo_y == 'categorica':
                correlation_ratio = graficar_correlacion_categorica(df, col_x, col_y, ax, dataset_nombre)
                metricas_correlacion.append({
                    'dataset': dataset_nombre,
                    'variable_x': col_x,
                    'variable_y': col_y,
                    'tipo': 'numérica-categórica',
                    'correlacion': correlation_ratio
                })
                
        except Exception as e:
            ax.text(0.5, 0.5, f'Error:\n{str(e)}', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=10, color='red')
            ax.set_title(f'{col_x} vs {col_y}')
    
    # Ocultar ejes vacíos
    for idx in range(len(pares_variables), len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle(f'Análisis de Correlaciones - {dataset_nombre}', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Guardar gráficas individuales
    ruta_guardado = os.path.join(carpeta_resultados, f'correlaciones_{dataset_nombre}.png')
    plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"  Gráficas de correlación guardadas: {ruta_guardado}")
    
    # Mostrar resumen de correlaciones
    if metricas_correlacion:
        df_metricas = pd.DataFrame(metricas_correlacion)
        print(f"\n  RESUMEN DE CORRELACIONES PARA {dataset_nombre}:")
        print("  " + "-" * 50)
        
        # Ordenar por valor absoluto de correlación
        df_metricas['correlacion_abs'] = df_metricas['correlacion'].abs()
        df_metricas = df_metricas.sort_values('correlacion_abs', ascending=False)
        
        for _, row in df_metricas.iterrows():
            print(f"  {row['variable_x']} vs {row['variable_y']}: {row['correlacion']:.3f} ({row['tipo']})")
    
    return metricas_correlacion

def main():
    """
    Función principal
    """
    print("=" * 70)
    print("ANÁLISIS DE CORRELACIONES - GRÁFICAS DE DISPERSIÓN")
    print("=" * 70)
    
    # CONFIGURACIÓN
    DATASETS_A_ANALIZAR = ['df_original', 'B2C', 'B4C', 'B8C', 'B16C', 'W2C', 'W4C', 'W8C', 'W16C']  # Matriz .npz
    
    # Configurar estilos
    configurar_estilos()
    
    # Crear carpeta de resultados
    carpeta_resultados = crear_carpeta_resultados()
    
    print(f"Datasets a analizar: {DATASETS_A_ANALIZAR}")
    print(f"Carpeta de resultados: {carpeta_resultados}")
    
    todas_metricas = []
    
    for dataset_nombre in DATASETS_A_ANALIZAR:
        if dataset_nombre in dataframes:
            df = dataframes[dataset_nombre]
            metricas = analizar_dataset_completo(df, dataset_nombre, carpeta_resultados)
            if metricas:
                todas_metricas.extend(metricas)
        else:
            print(f"\nDataset '{dataset_nombre}' no encontrado")
            print(f"   Datasets disponibles: {list(dataframes.keys())}")
    
    # Guardar métricas completas
    if todas_metricas:
        df_todas_metricas = pd.DataFrame(todas_metricas)
        ruta_csv = os.path.join(carpeta_resultados, 'resumen_correlaciones.csv')
        df_todas_metricas.to_csv(ruta_csv, index=False)
        print(f"\nResumen de correlaciones guardado: {ruta_csv}")
    
    print(f"\n{'='*70}")
    print("ANÁLISIS COMPLETADO")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()