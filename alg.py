import pandas as pd

def df_quartile(df, criterion, porc=0.25, quartile="first", ascending=True):
    """
    Extrae un cuartil/segmento de un DataFrame basado en una columna criterio.
    
    Parámetros:
    - df: DataFrame de pandas con los datos
    - criterion: Nombre de la columna por la cual ordenar y segmentar
    - porc: Porcentaje para determinar el tamaño del segmento (como decimal, ej: 0.25 para 25%)
    - quartile: Tipo de segmento ('first', 'second', 'third', 'fourth', 'center')
    - ascending: True para orden ascendente, False para descendente
    
    Retorna:
    - DataFrame con el segmento solicitado
    """
    
    # 1. Calcular el tamaño base del segmento
    total_filas = len(df)
    tamaño_q = int(total_filas * porc)
    
    # 2. Determinar los índices de inicio y fin (inclusivos) del segmento
    if quartile == "first" or quartile == "primero":
        indice_inicio = 0
        indice_fin_inclusivo = tamaño_q - 1
    elif quartile == "second" or quartile == "segundo":
        indice_inicio = tamaño_q
        indice_fin_inclusivo = 2 * tamaño_q - 1
    elif quartile == "third" or quartile == "tercero":
        indice_inicio = 2 * tamaño_q
        indice_fin_inclusivo = 3 * tamaño_q - 1
    elif quartile == "fourth" or quartile == "cuarto":
        indice_inicio = 3 * tamaño_q + 1
        indice_fin_inclusivo = 4 * tamaño_q
    elif quartile == "center" or quartile == "centro":
        indice_inicio = int(1.5 * tamaño_q)
        indice_fin_inclusivo = int(2.5 * tamaño_q) - 1
    else:
        raise ValueError("quartile debe ser: 'first', 'second', 'third', 'fourth', o 'center'")
    
    # 3. Ordenar la tabla de datos
    df_ordenado = df.sort_values(by=criterion, ascending=ascending).reset_index(drop=True)


    # Asegurar que los índices estén dentro del rango válido
    indice_fin_inclusivo = min(indice_fin_inclusivo, total_filas - 1)
    indice_inicio = max(0, indice_inicio)
    
    if indice_inicio <= indice_fin_inclusivo:
        df_resultado = df_ordenado.iloc[indice_inicio:indice_fin_inclusivo + 1].copy()
    else:
        # Retornar DataFrame vacío si los índices no son válidos
        df_resultado = pd.DataFrame(columns=df.columns)
    
    return df_resultado
