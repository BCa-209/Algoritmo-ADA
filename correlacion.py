import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from sklearn.preprocessing import LabelEncoder
import os

def cargar_datasets_directo():
    """
    Carga los datasets directamente desde los archivos CSV
    como fallback si analizar_datasets no funciona
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
                if 'Label' not in df.columns:
                    df['Label'] = nombre
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

def correlacion_heterogenea(df):
    """
    Calcula correlaciones entre variables numericas y categoricas.
    """
    columnas = [col for col in df.columns if col not in ['Label']]
    
    n = len(columnas)
    matriz_corr = pd.DataFrame(np.eye(n), index=columnas, columns=columnas)
    
    for i, col1 in enumerate(columnas):
        for j, col2 in enumerate(columnas):
            if i >= j:
                continue
            
            es_num1 = pd.api.types.is_numeric_dtype(df[col1])
            es_num2 = pd.api.types.is_numeric_dtype(df[col2])
            
            try:
                if es_num1 and es_num2:
                    corr = df[[col1, col2]].corr().iloc[0, 1]
                elif not es_num1 and not es_num2:
                    corr = cramer_v(df[col1], df[col2])
                else:
                    if es_num1:
                        corr = correlation_ratio(df[col1], df[col2])
                    else:
                        corr = correlation_ratio(df[col2], df[col1])
                
                matriz_corr.iloc[i, j] = corr
                matriz_corr.iloc[j, i] = corr
            except Exception as e:
                print(f"Error calculando correlacion entre {col1} y {col2}: {e}")
                matriz_corr.iloc[i, j] = 0
                matriz_corr.iloc[j, i] = 0
    
    return matriz_corr

def cramer_v(x, y):
    """V de Cramer para variables categoricas"""
    try:
        confusion_matrix = pd.crosstab(x, y)
        chi2 = chi2_contingency(confusion_matrix)[0]
        n = confusion_matrix.sum().sum()
        min_dim = min(confusion_matrix.shape) - 1
        return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    except:
        return 0

def correlation_ratio(numeric, categorical):
    """Correlation Ratio (Eta) para numerica vs categorica"""
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

def codificar_categoricas(df):
    """Codificar variables categoricas a numericas"""
    df_encoded = df.copy()
    le = LabelEncoder()
    
    for col in df_encoded.columns:
        if not pd.api.types.is_numeric_dtype(df_encoded[col]) and col != 'Label':
            try:
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            except:
                df_encoded[col] = np.random.randint(0, 10, len(df_encoded))
    
    return df_encoded

def matriz_distancia_heterogenea(df, metodo='mixto'):
    """Calcula matriz de distancia para datos heterogeneos."""
    if metodo == 'mixto':
        corr = correlacion_heterogenea(df)
    elif metodo == 'codificado':
        df_encoded = codificar_categoricas(df)
        corr = df_encoded.corr(method='pearson')
    else:
        raise ValueError("Metodo debe ser 'mixto' o 'codificado'")
    
    distancia = 1 - corr.abs()
    return distancia

def analizar_tipos_datos(df):
    """Analiza los tipos de datos en el dataset"""
    columnas_analisis = [col for col in df.columns if col != 'Label']
    df_analisis = df[columnas_analisis]
    
    num_cols = df_analisis.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df_analisis.select_dtypes(include=['object', 'category']).columns.tolist()
    
    return num_cols, cat_cols

def guardar_matriz_npz(matriz, nombre_archivo, carpeta):
    """Guarda la matriz en formato .npz"""
    ruta_completa = os.path.join(carpeta, f"{nombre_archivo}.npz")
    
    np.savez_compressed(
        ruta_completa,
        matriz_valores=matriz.values.astype(np.float64),
        matriz_columnas=np.array(matriz.columns.values, dtype='<U50'),  # Unicode string
        matriz_indices=np.array(matriz.index.values, dtype='<U50')     # Unicode string
    )
    
    print(f"Matriz guardada: {ruta_completa}")
    return ruta_completa

def analizar_dataset(nombre_dataset, df, metodo, carpeta_resultados):
    """Analiza un dataset especifico y guarda resultados"""
    print("=" * 70)
    print(f"ANALIZANDO: {nombre_dataset}")
    print("=" * 70)
    
    print(f"Dimension: {df.shape}")
    
    num_cols, cat_cols = analizar_tipos_datos(df)
    print(f"Columnas numericas ({len(num_cols)}): {num_cols}")
    print(f"Columnas categoricas ({len(cat_cols)}): {cat_cols}")
    
    try:
        matriz_distancia = matriz_distancia_heterogenea(df, metodo=metodo)
        print(f"Matriz de distancia ({metodo}):")
        print(matriz_distancia.round(3))
        
        valores = matriz_distancia.values
        valores_sin_diagonal = valores[~np.eye(valores.shape[0], dtype=bool)]
        print(f"Estadisticas:")
        print(f"   Rango: {valores_sin_diagonal.min():.3f} - {valores_sin_diagonal.max():.3f}")
        print(f"   Media: {valores_sin_diagonal.mean():.3f}")
        
        nombre_archivo = f"{nombre_dataset}_{metodo}"
        ruta_guardado = guardar_matriz_npz(matriz_distancia, nombre_archivo, carpeta_resultados)
        
        return matriz_distancia, ruta_guardado
        
    except Exception as e:
        print(f"Error analizando {nombre_dataset}: {e}")
        return None, None

if __name__ == "__main__":
    print("=" * 70)
    print("ANALISIS DE CORRELACION HETEROGENEA - GUARDADO EN NPZ")
    print("=" * 70)
    
    # CONFIGURACION
    datasets_a_analizar = ['df_original']  # MODIFICA AQUI
    metodo = 'mixto'  # MODIFICA AQUI
    #
        #
    #
    
    # Crear carpeta para resultados
    carpeta_resultados = crear_carpeta_resultados()
    
    print(f"Metodo seleccionado: {metodo}")
    print(f"Datasets a analizar: {datasets_a_analizar}")
    
    # Intentar cargar datasets de analizar_datasets primero
    try:
        from analizar_datasets import dataframes
        print("Usando datasets de analizar_datasets.py")
    except ImportError:
        print("analizar_datasets no disponible, cargando datasets directamente...")
        dataframes = cargar_datasets_directo()
    except Exception as e:
        print(f"Error importando analizar_datasets: {e}")
        print("Cargando datasets directamente...")
        dataframes = cargar_datasets_directo()
    
    if not dataframes:
        print("ERROR: No se pudieron cargar los datasets.")
        print("Ejecuta primero: python main.py")
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
    print("ANALISIS COMPLETADO")
    print("=" * 70)