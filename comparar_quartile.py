# compare_porciones_bic_wic_save_images.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime

def cargar_porciones(base_name="data"):
    """
    Carga todas las porciones BiC y WiC desde archivos CSV
    
    Retorna:
    - diccionario con DataFrames de todas las porciones
    """
    porciones = {}
    
    # Lista de configuraciones
    configuraciones = ['B2C', 'W2C', 'B4C', 'W4C', 'B8C', 'W8C', 'B16C', 'W16C']
    
    print("Cargando porciones desde archivos CSV...")
    for config in configuraciones:
        ruta_archivo = f"{base_name}/{config}.csv"
        
        if os.path.exists(ruta_archivo):
            try:
                df = pd.read_csv(ruta_archivo)
                porciones[config] = df
                print(f"  ✓ {config}: {df.shape[0]} filas, {df.shape[1]} columnas")
            except Exception as e:
                print(f"  ✗ Error cargando {config}: {e}")
        else:
            # Intentar ruta alternativa sin carpeta data
            ruta_alternativa = f"{config}.csv"
            if os.path.exists(ruta_alternativa):
                try:
                    df = pd.read_csv(ruta_alternativa)
                    porciones[config] = df
                    print(f"  ✓ {config}: {df.shape[0]} filas, {df.shape[1]} columnas")
                except Exception as e:
                    print(f"  ✗ Error cargando {config}: {e}")
            else:
                print(f"  ⚠️ {config}: Archivo no encontrado")
    
    return porciones

def crear_carpeta_imagenes():
    """
    Crea una carpeta para guardar las imágenes con timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta_imagenes = f"comparacion_imagenes_{timestamp}"
    
    if not os.path.exists(carpeta_imagenes):
        os.makedirs(carpeta_imagenes)
        print(f"✓ Carpeta creada: {carpeta_imagenes}/")
    
    return carpeta_imagenes

def guardar_figura(fig, nombre, carpeta_imagenes, dpi=300):
    """
    Guarda una figura en la carpeta especificada
    """
    ruta_completa = os.path.join(carpeta_imagenes, f"{nombre}.png")
    fig.savefig(ruta_completa, dpi=dpi, bbox_inches='tight')
    print(f"  ✓ Imagen guardada: {nombre}.png")
    plt.close(fig)  # Cerrar la figura para liberar memoria

def graficar_comparacion_pares(porciones, columna_objetivo='target_y', carpeta_imagenes="imagenes"):
    """
    Grafica comparaciones lado a lado para cada par BiC vs WiC y guarda las imágenes
    """
    pares = [
        ('B2C', 'W2C'),
        ('B4C', 'W4C'), 
        ('B8C', 'W8C'),
        ('B16C', 'W16C')
    ]
    
    print("\n📈 Generando gráficos de comparación por pares...")
    
    # Crear figura para cada par individualmente
    for idx, (bic, wic) in enumerate(pares):
        if bic in porciones and wic in porciones:
            # Crear figura individual para este par
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Crear DataFrame combinado para el gráfico
            df_bic = porciones[bic].copy()
            df_wic = porciones[wic].copy()
            
            df_bic['Grupo'] = bic
            df_wic['Grupo'] = wic
            
            df_combinado = pd.concat([df_bic, df_wic])
            
            # Gráfico de densidad
            sns.kdeplot(data=df_combinado, x=columna_objetivo, hue='Grupo', 
                       fill=True, alpha=0.5, ax=ax, palette=['#FF6B6B', '#4ECDC4'])
            
            # Añadir líneas verticales para medias
            media_bic = df_bic[columna_objetivo].mean()
            media_wic = df_wic[columna_objetivo].mean()
            
            ax.axvline(media_bic, color='#FF6B6B', linestyle='--', alpha=0.7, label=f'Media {bic}')
            ax.axvline(media_wic, color='#4ECDC4', linestyle='--', alpha=0.7, label=f'Media {wic}')
            
            ax.set_title(f'Comparación: {bic} vs {wic}\n({len(df_bic)} vs {len(df_wic)} filas)', fontsize=14, fontweight='bold')
            ax.set_xlabel(columna_objetivo, fontsize=12)
            ax.set_ylabel('Densidad', fontsize=12)
            ax.legend(fontsize=10)
            
            # Añadir estadísticas en texto
            texto_stats = f'{bic}:\n  Media: {media_bic:.2f}\n  N: {len(df_bic)}\n\n{wic}:\n  Media: {media_wic:.2f}\n  N: {len(df_wic)}\n\nDiferencia: {media_bic-media_wic:.2f}'
            ax.text(0.02, 0.98, texto_stats, transform=ax.transAxes, 
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Ajustar layout y guardar
            plt.tight_layout()
            guardar_figura(fig, f"comparacion_{bic}_vs_{wic}", carpeta_imagenes)
    
    # Crear también una figura con los 4 pares juntos
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (bic, wic) in enumerate(pares):
        if bic in porciones and wic in porciones:
            ax = axes[idx]
            
            df_bic = porciones[bic].copy()
            df_wic = porciones[wic].copy()
            
            df_bic['Grupo'] = bic
            df_wic['Grupo'] = wic
            
            df_combinado = pd.concat([df_bic, df_wic])
            
            sns.kdeplot(data=df_combinado, x=columna_objetivo, hue='Grupo', 
                       fill=True, alpha=0.5, ax=ax, palette=['#FF6B6B', '#4ECDC4'])
            
            media_bic = df_bic[columna_objetivo].mean()
            media_wic = df_wic[columna_objetivo].mean()
            
            ax.axvline(media_bic, color='#FF6B6B', linestyle='--', alpha=0.7, linewidth=1.5)
            ax.axvline(media_wic, color='#4ECDC4', linestyle='--', alpha=0.7, linewidth=1.5)
            
            ax.set_title(f'{bic} vs {wic}\n({len(df_bic)} vs {len(df_wic)} filas)', fontsize=12)
            ax.set_xlabel(columna_objetivo)
            ax.set_ylabel('Densidad')
            ax.legend(fontsize=9)
    
    plt.suptitle(f'Comparación de Distribuciones: BiC vs WiC\nColumna objetivo: {columna_objetivo}', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    guardar_figura(fig, "comparacion_todos_pares_combinados", carpeta_imagenes)

def graficar_boxplot_comparativo(porciones, columna_objetivo='target_y', carpeta_imagenes="imagenes"):
    """
    Gráfico de cajas comparativo y guarda las imágenes
    """
    print("📦 Generando gráficos de boxplot comparativo...")
    
    # Preparar datos para boxplot
    datos_boxplot = []
    
    configuraciones = ['B2C', 'W2C', 'B4C', 'W4C', 'B8C', 'W8C', 'B16C', 'W16C']
    
    for config in configuraciones:
        if config in porciones:
            df_temp = porciones[config].copy()
            df_temp['Configuración'] = config
            df_temp['Tipo'] = 'B' if config.startswith('B') else 'W'
            df_temp['Porcentaje'] = config[1:]  # Extraer 2C, 4C, etc.
            datos_boxplot.append(df_temp)
    
    if not datos_boxplot:
        print("No hay datos para graficar boxplot")
        return
    
    df_boxplot = pd.concat(datos_boxplot)
    
    # Gráfico 1: Boxplot por configuración
    fig1, ax1 = plt.subplots(figsize=(14, 8))
    sns.boxplot(data=df_boxplot, x='Configuración', y=columna_objetivo, 
                hue='Tipo', palette=['#FF6B6B', '#4ECDC4'], ax=ax1)
    ax1.set_title(f'Distribución de {columna_objetivo} por Configuración', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Configuración', fontsize=12)
    ax1.set_ylabel(columna_objetivo, fontsize=12)
    ax1.legend(title='Tipo', fontsize=10)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    guardar_figura(fig1, "boxplot_por_configuracion", carpeta_imagenes)
    
    # Gráfico 2: Boxplot agrupado por porcentaje
    fig2, ax2 = plt.subplots(figsize=(14, 8))
    sns.boxplot(data=df_boxplot, x='Porcentaje', y=columna_objetivo, 
                hue='Tipo', palette=['#FF6B6B', '#4ECDC4'], ax=ax2)
    ax2.set_title(f'Comparación B vs W por Porcentaje\n(2C=50%, 4C=25%, 8C=12.5%, 16C=6.25%)', 
                 fontsize=14, fontweight='bold')
    ax2.set_xlabel('Porcentaje', fontsize=12)
    ax2.set_ylabel(columna_objetivo, fontsize=12)
    ax2.legend(title='Tipo: B=Mayores, W=Menores', fontsize=10)
    plt.tight_layout()
    guardar_figura(fig2, "boxplot_por_porcentaje", carpeta_imagenes)

def graficar_evolucion_estadisticas(porciones, columna_objetivo='target_y', carpeta_imagenes="imagenes"):
    """
    Gráfico de evolución de estadísticas y guarda cada subplot como imagen separada
    """
    print("📊 Generando gráficos de evolución de estadísticas...")
    
    # Preparar datos
    datos_evolucion = []
    
    porcentajes = ['2C', '4C', '8C', '16C']
    
    for porc in porcentajes:
        bic = f'B{porc}'
        wic = f'W{porc}'
        
        if bic in porciones and wic in porciones:
            # Estadísticas para BiC
            datos_evolucion.append({
                'Porcentaje': porc,
                'Tipo': 'BiC (Mayores)',
                'Media': porciones[bic][columna_objetivo].mean(),
                'Mediana': porciones[bic][columna_objetivo].median(),
                'Mínimo': porciones[bic][columna_objetivo].min(),
                'Máximo': porciones[bic][columna_objetivo].max()
            })
            
            # Estadísticas para WiC
            datos_evolucion.append({
                'Porcentaje': porc,
                'Tipo': 'WiC (Menores)',
                'Media': porciones[wic][columna_objetivo].mean(),
                'Mediana': porciones[wic][columna_objetivo].median(),
                'Mínimo': porciones[wic][columna_objetivo].min(),
                'Máximo': porciones[wic][columna_objetivo].max()
            })
    
    df_evolucion = pd.DataFrame(datos_evolucion)
    
    if df_evolucion.empty:
        print("No hay datos para gráfico de evolución")
        return
    
    # Gráfico 1: Evolución de la media (imagen separada)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_evolucion, x='Porcentaje', y='Media', hue='Tipo', 
                marker='o', markersize=8, linewidth=2.5, ax=ax1, palette=['#FF6B6B', '#4ECDC4'])
    ax1.set_title('Evolución de la Media por Porcentaje', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Porcentaje (2C=50%, 4C=25%, 8C=12.5%, 16C=6.25%)', fontsize=12)
    ax1.set_ylabel(f'Media de {columna_objetivo}', fontsize=12)
    ax1.legend(title='Tipo', fontsize=10)
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    guardar_figura(fig1, "evolucion_media", carpeta_imagenes)
    
    # Gráfico 2: Evolución de la mediana (imagen separada)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_evolucion, x='Porcentaje', y='Mediana', hue='Tipo', 
                marker='o', markersize=8, linewidth=2.5, ax=ax2, palette=['#FF6B6B', '#4ECDC4'])
    ax2.set_title('Evolución de la Mediana por Porcentaje', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Porcentaje (2C=50%, 4C=25%, 8C=12.5%, 16C=6.25%)', fontsize=12)
    ax2.set_ylabel(f'Mediana de {columna_objetivo}', fontsize=12)
    ax2.legend(title='Tipo', fontsize=10)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    guardar_figura(fig2, "evolucion_mediana", carpeta_imagenes)
    
    # Gráfico 3: Rango de valores (imagen separada)
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    # Crear datos para el área de rango
    for tipo in ['BiC (Mayores)', 'WiC (Menores)']:
        df_tipo = df_evolucion[df_evolucion['Tipo'] == tipo]
        color = '#FF6B6B' if 'BiC' in tipo else '#4ECDC4'
        label = tipo
        
        # Rellenar área entre mínimo y máximo
        ax3.fill_between(df_tipo['Porcentaje'], df_tipo['Mínimo'], df_tipo['Máximo'], 
                        alpha=0.2, color=color, label=f'Rango {label}')
        
        # Línea para la media
        ax3.plot(df_tipo['Porcentaje'], df_tipo['Media'], marker='o', markersize=6, 
                linewidth=2, color=color, label=f'Media {label}')
    
    ax3.set_title('Rango de Valores y Media por Porcentaje', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Porcentaje (2C=50%, 4C=25%, 8C=12.5%, 16C=6.25%)', fontsize=12)
    ax3.set_ylabel(f'Valor de {columna_objetivo}', fontsize=12)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    plt.tight_layout()
    guardar_figura(fig3, "evolucion_rango_valores", carpeta_imagenes)
    
    # Gráfico 4: Diferencia entre BiC y WiC (imagen separada)
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    
    # Calcular diferencias
    df_diferencias = df_evolucion.pivot(index='Porcentaje', columns='Tipo', values='Media')
    df_diferencias['Diferencia'] = df_diferencias['BiC (Mayores)'] - df_diferencias['WiC (Menores)']
    
    # Gráfico de barras para diferencias
    bars = ax4.bar(df_diferencias.index, df_diferencias['Diferencia'], 
                  color=['#8A2BE2', '#9370DB', '#BA55D3', '#DA70D6'], 
                  edgecolor='black', linewidth=1.5)
    
    ax4.set_title('Diferencia Media entre BiC y WiC por Porcentaje', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Porcentaje (2C=50%, 4C=25%, 8C=12.5%, 16C=6.25%)', fontsize=12)
    ax4.set_ylabel('Diferencia de Medias (BiC - WiC)', fontsize=12)
    
    # Añadir valores en las barras
    for bar, v in zip(bars, df_diferencias['Diferencia']):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + (0.02 * max(df_diferencias['Diferencia'])),
                f'{v:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax4.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    guardar_figura(fig4, "diferencia_medias", carpeta_imagenes)

def graficar_densidad_individual(porciones, columna_objetivo='target_y', carpeta_imagenes="imagenes"):
    """
    Gráfico de densidad individual para cada configuración
    """
    print("🎨 Generando gráficos de densidad individuales...")
    
    configuraciones = ['B2C', 'W2C', 'B4C', 'W4C', 'B8C', 'W8C', 'B16C', 'W16C']
    
    for config in configuraciones:
        if config in porciones:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            df_config = porciones[config]
            
            # Determinar color según tipo
            color = '#FF6B6B' if config.startswith('B') else '#4ECDC4'
            tipo = "Mayores" if config.startswith('B') else "Menores"
            
            # Gráfico de densidad
            sns.kdeplot(data=df_config[columna_objetivo], fill=True, alpha=0.7, 
                       color=color, linewidth=2.5, ax=ax)
            
            # Líneas para estadísticas
            media = df_config[columna_objetivo].mean()
            mediana = df_config[columna_objetivo].median()
            
            ax.axvline(media, color='red', linestyle='--', linewidth=2, alpha=0.8, label=f'Media: {media:.2f}')
            ax.axvline(mediana, color='green', linestyle='--', linewidth=2, alpha=0.8, label=f'Mediana: {mediana:.2f}')
            
            # Título y etiquetas
            porcentaje = config[1:]
            if porcentaje == '2C':
                porc_text = '50%'
            elif porcentaje == '4C':
                porc_text = '25%'
            elif porcentaje == '8C':
                porc_text = '12.5%'
            else:
                porc_text = '6.25%'
            
            ax.set_title(f'Distribución de {config} ({porc_text} {tipo})\nN={len(df_config)}', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel(columna_objetivo, fontsize=12)
            ax.set_ylabel('Densidad', fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            guardar_figura(fig, f"densidad_individual_{config}", carpeta_imagenes)

def graficar_resumen_estadisticas(porciones, columna_objetivo='target_y', carpeta_imagenes="imagenes"):
    """
    Gráfico resumen con todas las estadísticas importantes
    """
    print("📋 Generando gráfico resumen de estadísticas...")
    
    # Preparar datos para el resumen
    datos_resumen = []
    
    configuraciones = ['B2C', 'W2C', 'B4C', 'W4C', 'B8C', 'W8C', 'B16C', 'W16C']
    
    for config in configuraciones:
        if config in porciones:
            df_config = porciones[config]
            
            datos_resumen.append({
                'Configuración': config,
                'Tipo': 'BiC' if config.startswith('B') else 'WiC',
                'Porcentaje': config[1:],
                'Media': df_config[columna_objetivo].mean(),
                'Mediana': df_config[columna_objetivo].median(),
                'Std': df_config[columna_objetivo].std(),
                'Mínimo': df_config[columna_objetivo].min(),
                'Máximo': df_config[columna_objetivo].max(),
                'N': len(df_config)
            })
    
    df_resumen = pd.DataFrame(datos_resumen)
    
    if df_resumen.empty:
        print("No hay datos para gráfico resumen")
        return
    
    # Crear figura de resumen
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Gráfico 1: Media y mediana por configuración
    ax1 = axes[0, 0]
    x = range(len(df_resumen))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], df_resumen['Media'], width, label='Media', color='#FF6B6B')
    ax1.bar([i + width/2 for i in x], df_resumen['Mediana'], width, label='Mediana', color='#4ECDC4')
    
    ax1.set_xlabel('Configuración')
    ax1.set_ylabel('Valor')
    ax1.set_title('Media y Mediana por Configuración', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_resumen['Configuración'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Gráfico 2: Desviación estándar
    ax2 = axes[0, 1]
    colors = ['#FF6B6B' if tipo == 'BiC' else '#4ECDC4' for tipo in df_resumen['Tipo']]
    ax2.bar(df_resumen['Configuración'], df_resumen['Std'], color=colors, edgecolor='black')
    ax2.set_xlabel('Configuración')
    ax2.set_ylabel('Desviación Estándar')
    ax2.set_title('Variabilidad (Desviación Estándar)', fontweight='bold')
    ax2.set_xticklabels(df_resumen['Configuración'], rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Gráfico 3: Rango (mínimo-máximo)
    ax3 = axes[1, 0]
    for i, row in df_resumen.iterrows():
        color = '#FF6B6B' if row['Tipo'] == 'BiC' else '#4ECDC4'
        ax3.plot([row['Configuración'], row['Configuración']], [row['Mínimo'], row['Máximo']], 
                color=color, linewidth=3, marker='o', markersize=8)
    
    ax3.set_xlabel('Configuración')
    ax3.set_ylabel(f'Valor de {columna_objetivo}')
    ax3.set_title('Rango de Valores (Mínimo-Máximo)', fontweight='bold')
    ax3.set_xticklabels(df_resumen['Configuración'], rotation=45, ha='right')
    ax3.grid(True, alpha=0.3)
    
    # Gráfico 4: Tamaño de muestra
    ax4 = axes[1, 1]
    colors = ['#FF6B6B' if tipo == 'BiC' else '#4ECDC4' for tipo in df_resumen['Tipo']]
    bars = ax4.bar(df_resumen['Configuración'], df_resumen['N'], color=colors, edgecolor='black')
    ax4.set_xlabel('Configuración')
    ax4.set_ylabel('Número de Observaciones')
    ax4.set_title('Tamaño de Muestra por Configuración', fontweight='bold')
    ax4.set_xticklabels(df_resumen['Configuración'], rotation=45, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Añadir valores en las barras
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    plt.suptitle(f'Resumen Estadístico - Columna objetivo: {columna_objetivo}', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    guardar_figura(fig, "resumen_estadistico_completo", carpeta_imagenes)

def exportar_estadisticas(porciones, columna_objetivo='target_y'):
    """
    Exporta las estadísticas a archivos CSV
    """
    if not os.path.exists('resultados_comparacion'):
        os.makedirs('resultados_comparacion')
    
    # Preparar datos para exportación
    datos_estadisticas = []
    
    configuraciones = ['B2C', 'W2C', 'B4C', 'W4C', 'B8C', 'W8C', 'B16C', 'W16C']
    
    for config in configuraciones:
        if config in porciones:
            df_config = porciones[config]
            
            datos_estadisticas.append({
                'Configuración': config,
                'Tipo': 'BiC' if config.startswith('B') else 'WiC',
                'Porcentaje': config[1:],
                'N': len(df_config),
                'Mínimo': df_config[columna_objetivo].min(),
                'Máximo': df_config[columna_objetivo].max(),
                'Media': df_config[columna_objetivo].mean(),
                'Mediana': df_config[columna_objetivo].median(),
                'Desviación Estándar': df_config[columna_objetivo].std(),
                'Percentil 25': df_config[columna_objetivo].quantile(0.25),
                'Percentil 75': df_config[columna_objetivo].quantile(0.75),
                'Rango': df_config[columna_objetivo].max() - df_config[columna_objetivo].min()
            })
    
    df_estadisticas = pd.DataFrame(datos_estadisticas)
    ruta_estadisticas = 'resultados_comparacion/estadisticas_detalladas.csv'
    df_estadisticas.to_csv(ruta_estadisticas, index=False)
    print(f"\n✓ Estadísticas exportadas: {ruta_estadisticas}")
    
    return df_estadisticas

def main():
    """
    Función principal
    """
    print("=" * 70)
    print("COMPARACIÓN DE PORCIONES BiC vs WiC - GUARDAR IMÁGENES")
    print("=" * 70)
    print("Análisis comparativo que guarda todas las imágenes en carpeta:")
    print("  • Gráficos individuales por par BiC-WiC")
    print("  • Boxplots comparativos")
    print("  • Evolución de estadísticas")
    print("  • Gráficos de densidad individuales")
    print("  • Resumen estadístico completo")
    print("=" * 70)
    
    # 1. Cargar todas las porciones
    porciones = cargar_porciones(base_name="data")
    
    if len(porciones) < 2:
        print("\n❌ Error: No se pudieron cargar suficientes porciones.")
        print("Asegúrate de que existan los archivos CSV en la carpeta 'data/'")
        print("Archivos esperados: B2C.csv, W2C.csv, B4C.csv, W4C.csv, etc.")
        return
    
    print(f"\n✅ Porciones cargadas: {len(porciones)}")
    
    # 2. Especificar columna objetivo
    columna_objetivo = 'target_y'  # Cambiar si es necesario
    
    # Verificar que la columna existe en todos los DataFrames
    for config, df in porciones.items():
        if columna_objetivo not in df.columns:
            print(f"\n⚠️ Advertencia: Columna '{columna_objetivo}' no encontrada en {config}")
            print(f"  Columnas disponibles: {df.columns.tolist()}")
            # Intentar con 'y' como alternativa
            if 'y' in df.columns:
                columna_objetivo = 'y'
                print(f"  Usando 'y' como columna objetivo")
                break
    
    print(f"\n📊 Columna objetivo para análisis: {columna_objetivo}")
    
    # 3. Crear carpeta para imágenes
    carpeta_imagenes = crear_carpeta_imagenes()
    
    # 4. Generar y guardar todas las imágenes
    print(f"\n🖼️ Generando y guardando imágenes en: {carpeta_imagenes}/")
    
    # 4.1 Gráficos de comparación por pares
    graficar_comparacion_pares(porciones, columna_objetivo, carpeta_imagenes)
    
    # 4.2 Boxplots comparativos
    graficar_boxplot_comparativo(porciones, columna_objetivo, carpeta_imagenes)
    
    # 4.3 Evolución de estadísticas
    graficar_evolucion_estadisticas(porciones, columna_objetivo, carpeta_imagenes)
    
    # 4.4 Gráficos de densidad individuales
    graficar_densidad_individual(porciones, columna_objetivo, carpeta_imagenes)
    
    # 4.5 Gráfico resumen
    graficar_resumen_estadisticas(porciones, columna_objetivo, carpeta_imagenes)
    
    # 5. Exportar estadísticas
    print("\n💾 Exportando estadísticas a CSV...")
    df_estadisticas = exportar_estadisticas(porciones, columna_objetivo)
    
    # 6. Mostrar resumen final
    print(f"\n" + "=" * 70)
    print("RESUMEN DEL ANÁLISIS")
    print("=" * 70)
    
    # Contar imágenes generadas
    imagenes_generadas = len([f for f in os.listdir(carpeta_imagenes) if f.endswith('.png')])
    
    print(f"📁 Carpeta de imágenes: {carpeta_imagenes}/")
    print(f"🖼️ Imágenes generadas: {imagenes_generadas}")
    print(f"📊 Estadísticas exportadas: resultados_comparacion/estadisticas_detalladas.csv")
    
    # Mostrar estadísticas resumidas
    print(f"\n📋 RESUMEN ESTADÍSTICO:")
    if 'df_estadisticas' in locals():
        print(df_estadisticas[['Configuración', 'N', 'Media', 'Mediana', 'Desviación Estándar']].to_string())
    
    print(f"\n✅ Análisis completado exitosamente")

if __name__ == "__main__":
    main()