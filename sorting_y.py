# sorting_y.py
import pandas as pd
import numpy as np
import time
import os
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt

# =============================================================================
# ALGORITMOS DE ORDENAMIENTO (VERSIÓN SIMPLIFICADA)
# =============================================================================

def bubble_sort(arr):
    """Implementación del algoritmo Bubble Sort (sin pasos)"""
    n = len(arr)
    arr = arr.copy()
    
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

def selection_sort(arr):
    """Implementación del algoritmo Selection Sort (sin pasos)"""
    arr = arr.copy()
    n = len(arr)
    
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def insertion_sort(arr):
    """Implementación del algoritmo Insertion Sort (sin pasos)"""
    arr = arr.copy()
    
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        while j >= 0 and current < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr

def quick_sort(arr):
    """Implementación del algoritmo Quick Sort (sin pasos)"""
    arr = arr.copy()
    
    def _quick_sort(sub_arr):
        if len(sub_arr) <= 1:
            return sub_arr
        else:
            pivot = sub_arr[len(sub_arr) // 2]
            left = [x for x in sub_arr if x < pivot]
            middle = [x for x in sub_arr if x == pivot]
            right = [x for x in sub_arr if x > pivot]
            return _quick_sort(left) + middle + _quick_sort(right)
    
    return _quick_sort(arr)

def merge_sort(arr):
    """Implementación del algoritmo Merge Sort (sin pasos)"""
    arr = arr.copy()
    
    def _merge_sort(sub_arr):
        if len(sub_arr) <= 1:
            return sub_arr
            
        mid = len(sub_arr) // 2
        left = _merge_sort(sub_arr[:mid])
        right = _merge_sort(sub_arr[mid:])
        
        return _merge(left, right)
    
    def _merge(left, right):
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    return _merge_sort(arr)

def heap_sort(arr):
    """Implementación del algoritmo Heap Sort (sin pasos)"""
    arr = arr.copy()
    
    def _heapify(sub_arr, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and sub_arr[left] > sub_arr[largest]:
            largest = left
        
        if right < n and sub_arr[right] > sub_arr[largest]:
            largest = right
        
        if largest != i:
            sub_arr[i], sub_arr[largest] = sub_arr[largest], sub_arr[i]
            _heapify(sub_arr, n, largest)
    
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i)
    
    # Extract elements
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        _heapify(arr, i, 0)
    
    return arr

def shell_sort(arr):
    """Implementación del algoritmo Shell Sort (sin pasos)"""
    arr = arr.copy()
    n = len(arr)
    gap = n // 2
    
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    
    return arr

def gnome_sort(arr):
    """Implementación del algoritmo Gnome Sort (sin pasos)"""
    arr = arr.copy()
    n = len(arr)
    i = 0
    
    while i < n:
        if i == 0:
            i += 1
        elif arr[i] >= arr[i - 1]:
            i += 1
        else:
            arr[i], arr[i - 1] = arr[i - 1], arr[i]
            i -= 1
    return arr

def shaker_sort(arr):
    """Implementación del algoritmo Shaker Sort (sin pasos)"""
    arr = arr.copy()
    n = len(arr)
    left = 0
    right = n - 1
    swapped = True
    
    while left < right and swapped:
        swapped = False
        
        # Ida: izquierda a derecha
        for i in range(left, right):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        if not swapped:
            break
            
        right -= 1
        swapped = False
        
        # Vuelta: derecha a izquierda
        for i in range(right, left, -1):
            if arr[i] < arr[i - 1]:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                swapped = True
                
        left += 1
    return arr

# Diccionario de algoritmos disponibles
ALGORITMOS = {
    "bubble_sort": bubble_sort,
    "selection_sort": selection_sort,
    "insertion_sort": insertion_sort,
    "quick_sort": quick_sort,
    "merge_sort": merge_sort,
    "heap_sort": heap_sort,
    "shell_sort": shell_sort,
    "gnome_sort": gnome_sort,
    "shaker_sort": shaker_sort
}

# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

def crear_carpeta_resultados():
    """Crea la carpeta para guardar resultados si no existe"""
    carpeta = "resultados_ordenamiento"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
        print(f"Carpeta creada: {carpeta}")
    return carpeta

def ordenar_columna_y(df, algoritmo="bubble_sort"):
    """
    Ordena la columna 'y' usando el algoritmo especificado y mide el tiempo
    
    Parámetros:
    - df: DataFrame con columna 'y'
    - algoritmo: nombre del algoritmo a usar
    
    Retorna:
    - DataFrame ordenado
    - tiempo de ejecución en segundos
    """
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo no disponible. Opciones: {list(ALGORITMOS.keys())}")
    
    # Extraer columna y
    y_values = df['y'].tolist()
    
    # Medir tiempo de ordenamiento
    inicio = time.time()
    y_ordenado = ALGORITMOS[algoritmo](y_values)
    tiempo_ejecucion = time.time() - inicio
    
    # Crear nuevo DataFrame con columna ordenada
    df_ordenado = df.copy()
    df_ordenado['y'] = y_ordenado
    
    return df_ordenado, tiempo_ejecucion

def verificar_ordenamiento(df_ordenado):
    """Verifica si la columna 'y' está correctamente ordenada"""
    y_values = df_ordenado['y'].values
    return all(y_values[i] <= y_values[i + 1] for i in range(len(y_values) - 1))

def ejecutar_todos_algoritmos(df):
    """
    Ejecuta todos los algoritmos de ordenamiento y guarda los resultados
    
    Parámetros:
    - df: DataFrame original con columna 'y'
    
    Retorna:
    - DataFrame con resultados de tiempos
    """
    print("=" * 70)
    print("EJECUTANDO TODOS LOS ALGORITMOS DE ORDENAMIENTO")
    print("=" * 70)
    
    resultados = []
    carpeta_resultados = crear_carpeta_resultados()
    
    for nombre_algoritmo in ALGORITMOS.keys():
        print(f"\nEjecutando {nombre_algoritmo}...")
        
        try:
            # Ordenar y medir tiempo
            df_ordenado, tiempo = ordenar_columna_y(df, nombre_algoritmo)
            
            # Verificar ordenamiento
            correcto = verificar_ordenamiento(df_ordenado)
            
            # Guardar resultado en CSV
            nombre_archivo = f"{nombre_algoritmo}.csv"
            ruta_completa = os.path.join(carpeta_resultados, nombre_archivo)
            df_ordenado.to_csv(ruta_completa, index=False)
            
            # Agregar a resultados
            resultados.append({
                'algoritmo': nombre_algoritmo,
                'tiempo_segundos': tiempo,
                'tiempo_milisegundos': tiempo * 1000,
                'correcto': correcto,
                'archivo': nombre_archivo
            })
            
            print(f"  ✓ Tiempo: {tiempo * 1000:.2f} ms")
            print(f"  ✓ Ordenamiento correcto: {correcto}")
            print(f"  ✓ Archivo guardado: {ruta_completa}")
            
        except Exception as e:
            print(f"  ✗ Error en {nombre_algoritmo}: {e}")
            resultados.append({
                'algoritmo': nombre_algoritmo,
                'tiempo_segundos': float('inf'),
                'tiempo_milisegundos': float('inf'),
                'correcto': False,
                'archivo': None,
                'error': str(e)
            })
    
    return pd.DataFrame(resultados)

def generar_reporte_comparativo(df_resultados):
    """
    Genera un reporte comparativo y gráficos de los resultados
    """
    print("\n" + "=" * 70)
    print("REPORTE COMPARATIVO")
    print("=" * 70)
    
    # Filtrar resultados exitosos
    df_exitosos = df_resultados[df_resultados['correcto'] == True].copy()
    
    if len(df_exitosos) == 0:
        print("No hay algoritmos exitosos para comparar")
        return
    
    # Ordenar por tiempo (más rápido primero)
    df_exitosos = df_exitosos.sort_values('tiempo_milisegundos')
    
    print("\nRANKING DE ALGORITMOS (más rápido primero):")
    print("-" * 50)
    for i, (_, fila) in enumerate(df_exitosos.iterrows(), 1):
        print(f"{i:2d}. {fila['algoritmo']:20} - {fila['tiempo_milisegundos']:8.2f} ms")
    
    print(f"\nRESUMEN ESTADÍSTICO:")
    print(f"  • Total de algoritmos: {len(df_resultados)}")
    print(f"  • Algoritmos exitosos: {len(df_exitosos)}")
    print(f"  • Más rápido: {df_exitosos.iloc[0]['algoritmo']} "
          f"({df_exitosos.iloc[0]['tiempo_milisegundos']:.2f} ms)")
    print(f"  • Más lento: {df_exitosos.iloc[-1]['algoritmo']} "
          f"({df_exitosos.iloc[-1]['tiempo_milisegundos']:.2f} ms)")
    
    if len(df_exitosos) > 1:
        ratio = df_exitosos.iloc[-1]['tiempo_milisegundos'] / df_exitosos.iloc[0]['tiempo_milisegundos']
        print(f"  • Ratio rápido/lento: {ratio:.1f}x")
    
    return df_exitosos

def visualizar_resultados(df_resultados):
    """
    Crea visualizaciones de los resultados de ordenamiento
    """
    # Filtrar resultados exitosos
    df_exitosos = df_resultados[df_resultados['correcto'] == True]
    
    if len(df_exitosos) == 0:
        print("No hay resultados exitosos para visualizar")
        return
    
    # Crear gráficos
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Gráfico 1: Tiempos de ejecución (barras)
    algoritmos = df_exitosos['algoritmo'].values
    tiempos = df_exitosos['tiempo_milisegundos'].values
    
    bars = ax1.bar(algoritmos, tiempos, color='skyblue', alpha=0.7)
    ax1.set_title('Tiempo de Ejecución por Algoritmo', fontweight='bold')
    ax1.set_ylabel('Tiempo (milisegundos)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Añadir valores en las barras
    for bar, tiempo in zip(bars, tiempos):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{tiempo:.1f} ms', ha='center', va='bottom', fontsize=9)
    
    # Gráfico 2: Comparación de eficiencia (colores)
    colors = ['green' if t == min(tiempos) else 
              'red' if t == max(tiempos) else 
              'skyblue' for t in tiempos]
    
    ax2.bar(algoritmos, tiempos, color=colors, alpha=0.7)
    ax2.set_title('Comparación de Eficiencia\n(Verde = más rápido, Rojo = más lento)', 
                 fontweight='bold')
    ax2.set_ylabel('Tiempo (ms)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Gráfico 3: Distribución de tiempos (pie chart)
    ax3.pie(tiempos, labels=algoritmos, autopct='%1.1f%%', startangle=90)
    ax3.set_title('Distribución de Tiempos de Ejecución', fontweight='bold')
    
    # Gráfico 4: Ranking visual
    y_pos = range(len(algoritmos))
    ax4.barh(y_pos, sorted(tiempos), color='lightgreen', alpha=0.7)
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels([algoritmos[i] for i in np.argsort(tiempos)])
    ax4.set_xlabel('Tiempo (milisegundos)')
    ax4.set_title('Ranking de Velocidad', fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    # Guardar gráfico
    carpeta_resultados = "resultados_ordenamiento"
    ruta_grafico = os.path.join(carpeta_resultados, "comparacion_algoritmos.png")
    plt.savefig(ruta_grafico, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Gráfico comparativo guardado: {ruta_grafico}")

def main():
    """
    Función principal
    """
    print("=" * 70)
    print("ORDENAMIENTO DE COLUMNA 'y' - COMPARACIÓN DE ALGORITMOS")
    print("=" * 70)
    
    try:
        # Cargar dataset
        df = pd.read_csv('data/df_original.csv')
        
        if 'y' not in df.columns:
            print("Error: La columna 'y' no existe en el dataset")
            return
        
        print(f"Dataset cargado: {df.shape}")
        print(f"Estadísticas de 'y':")
        print(f"  Mínimo: {df['y'].min():.2f}")
        print(f"  Máximo: {df['y'].max():.2f}")
        print(f"  Media: {df['y'].mean():.2f}")
        print(f"  Desviación: {df['y'].std():.2f}")
        print(f"  Elementos: {len(df)}")
        
        # Ejecutar todos los algoritmos
        df_resultados = ejecutar_todos_algoritmos(df)
        
        # Generar reporte
        df_exitosos = generar_reporte_comparativo(df_resultados)
        
        # Guardar resumen de resultados
        if not df_resultados.empty:
            carpeta_resultados = "resultados_ordenamiento"
            ruta_resumen = os.path.join(carpeta_resultados, "resumen_resultados.csv")
            df_resultados.to_csv(ruta_resumen, index=False)
            print(f"\nResumen de resultados guardado: {ruta_resumen}")
        
        # Generar visualizaciones
        visualizar_resultados(df_resultados)
        
        print(f"\n" + "=" * 70)
        print("PROCESO COMPLETADO")
        print("=" * 70)
        print(f"Archivos guardados en carpeta: resultados_ordenamiento/")
        
    except FileNotFoundError:
        print("Error: No se encuentra data/df_original.csv")
        print("Ejecuta primero: python main.py")
    except Exception as e:
        print(f"Error inesperado: {e}")

# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================

if __name__ == "__main__":
    main()