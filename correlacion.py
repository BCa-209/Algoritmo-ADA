import pandas as pd
import numpy as np
import os

def cargar_datasets_directo():
    """
    Carga los datasets directamente desde los archivos CSV
    """
    dataframes = {}
    data_dir = 'data'
    
    archivos = {
        'df_original': 'df_original.csv',
        'B2C': 'B2C.csv',
        'W2C': 'W2C.csv',
        'B4C': 'B4C.csv',
        'W4C': 'W4C.csv',
        'B8C': 'B8C.csv',
        'W8C': 'W8C.csv',
        'B16C': 'B16C.csv',
        'W16C': 'W16C.csv'
    }
    
    for nombre, archivo in archivos.items():
        ruta = os.path.join(data_dir, archivo)
        if os.path.exists(ruta):
            try:
                df = pd.read_csv(ruta)
                # Eliminar columnas no numéricas si existen
                df = df.select_dtypes(include=[np.number])
                dataframes[nombre] = df
                print(f"Cargado: {nombre} - {df.shape}")
            except Exception as e:
                print(f"Error cargando {nombre}: {e}")
        else:
            print(f"Archivo no encontrado: {ruta}")
    
    return dataframes

def crear_carpeta_resultados():
    """Crea la carpeta para guardar resultados si no existe"""
    carpeta = "resultado_correlacion"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
        print(f"Carpeta creada: {carpeta}")
    return carpeta

def matriz_correlacion_numerica(df):
    """
    Calcula matriz de correlación para datos puramente numéricos
    """
    # Asegurarse de que solo tenemos columnas numéricas
    df_numeric = df.select_dtypes(include=[np.number])
    
    # Calcular correlación de Pearson
    matriz_corr = df_numeric.corr(method='pearson')
    
    return matriz_corr

def matriz_distancia_numerica(df, metodo='absoluta'):
    """
    Calcula matriz de distancia para datos numéricos
    """
    matriz_corr = matriz_correlacion_numerica(df)
    
    if metodo == 'absoluta':
        # Distancia = 1 - |correlación|
        distancia = 1 - np.abs(matriz_corr)
    elif metodo == 'directa':
        # Distancia = 1 - correlación (preserva signo)
        distancia = 1 - matriz_corr
    else:
        raise ValueError("Método debe ser 'absoluta' o 'directa'")
    
    return distancia

def analizar_tipos_datos(df):
    """Analiza los tipos de datos en el dataset"""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    return num_cols, cat_cols

def guardar_matriz_npz(matriz, nombre_archivo, carpeta):
    """Guarda la matriz en formato .npz"""
    ruta_completa = os.path.join(carpeta, f"{nombre_archivo}.npz")
    
    np.savez_compressed(
        ruta_completa,
        matriz_valores=matriz.values.astype(np.float64),
        matriz_columnas=np.array(matriz.columns.values, dtype='<U50'),
        matriz_indices=np.array(matriz.index.values, dtype='<U50')
    )
    
    print(f"Matriz guardada: {ruta_completa}")
    return ruta_completa

def guardar_matriz_csv(matriz, nombre_archivo, carpeta):
    """Guarda la matriz en formato CSV para verificación"""
    ruta_completa = os.path.join(carpeta, f"{nombre_archivo}.csv")
    matriz.to_csv(ruta_completa)
    print(f"Matriz CSV guardada: {ruta_completa}")
    return ruta_completa

def analizar_dataset(nombre_dataset, df, metodo, carpeta_resultados):
    """Analiza un dataset específico y guarda resultados"""
    print("=" * 70)
    print(f"ANALIZANDO: {nombre_dataset}")
    print("=" * 70)
    
    print(f"Dimensión: {df.shape}")
    
    num_cols, cat_cols = analizar_tipos_datos(df)
    print(f"Columnas numéricas ({len(num_cols)}): {num_cols}")
    print(f"Columnas categóricas ({len(cat_cols)}): {cat_cols}")
    
    try:
        # Calcular matriz de distancia
        matriz_distancia = matriz_distancia_numerica(df, metodo=metodo)
        print(f"Matriz de distancia ({metodo}):")
        print(matriz_distancia.round(3))
        
        # Estadísticas
        valores = matriz_distancia.values
        valores_sin_diagonal = valores[~np.eye(valores.shape[0], dtype=bool)]
        print(f"Estadísticas de distancia:")
        print(f"   Rango: {valores_sin_diagonal.min():.3f} - {valores_sin_diagonal.max():.3f}")
        print(f"   Media: {valores_sin_diagonal.mean():.3f}")
        print(f"   Desviación estándar: {valores_sin_diagonal.std():.3f}")
        
        # Guardar resultados
        nombre_archivo = f"{nombre_dataset}_{metodo}"
        ruta_npz = guardar_matriz_npz(matriz_distancia, nombre_archivo, carpeta_resultados)
        #ruta_csv = guardar_matriz_csv(matriz_distancia, nombre_archivo, carpeta_resultados)
        
        return matriz_distancia, ruta_npz
        
    except Exception as e:
        print(f"Error analizando {nombre_dataset}: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("=" * 70)
    print("ANÁLISIS DE CORRELACIÓN PARA DATOS NUMÉRICOS")
    print("=" * 70)
    
    # CONFIGURACIÓN
    datasets_a_analizar = ['df_original','B2C', 'B4C', 'B8C', 'B16C', 'W2C', 'W4C', 'W8C', 'W16C']  # MODIFICA AQUÍ
    metodo = 'directa'  # 'absoluta' o 'directa'
    
    # Crear carpeta para resultados
    carpeta_resultados = crear_carpeta_resultados()
    
    print(f"Método seleccionado: {metodo}")
    print(f"Datasets a analizar: {datasets_a_analizar}")
    
    # Cargar datasets
    dataframes = cargar_datasets_directo()
    
    if not dataframes:
        print("ERROR: No se pudieron cargar los datasets.")
        exit()
    
    print(f"Datasets disponibles: {list(dataframes.keys())}")
    
    resultados = {}
    rutas_guardado = {}
    
    for nombre_dataset in datasets_a_analizar:
        if nombre_dataset in dataframes:
            df = dataframes[nombre_dataset]
            matriz, ruta = analizar_dataset(nombre_dataset, df, metodo, carpeta_resultados)
            resultados[nombre_dataset] = matriz
            rutas_guardado[nombre_dataset] = ruta
        else:
            print(f"Dataset '{nombre_dataset}' no encontrado en dataframes")
    
    # Resumen
    if rutas_guardado:
        print("\n" + "=" * 70)
        print("RESUMEN DE ARCHIVOS GUARDADOS")
        print("=" * 70)
        for dataset, ruta in rutas_guardado.items():
            if ruta:
                print(f"{dataset}: {ruta}")
    
    print("\n" + "=" * 70)
    print("ANÁLISIS COMPLETADO")
    print("=" * 70)