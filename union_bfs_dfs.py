# union_variables_bfs_dfs.py
import pandas as pd
import os
import glob
from pathlib import Path

def cargar_variables_bfs_bic():
    """
    Carga todas las variables de las búsquedas BFS para configuraciones BiC (B2C, B4C, B8C, B16C)
    """
    print("=" * 60)
    print("CARGANDO VARIABLES BFS DE CONFIGURACIONES BiC")
    print("=" * 60)
    
    variables_bfs_bic = {}
    
    # Configuraciones BiC a procesar
    configuraciones_bic = ['B2C', 'B4C', 'B8C', 'B16C']
    
    for config in configuraciones_bic:
        print(f"\n📂 Buscando archivos BFS para {config}...")
        
        # Patrón de búsqueda para archivos BFS de esta configuración
        patron_bfs = f"resultados_busqueda_limitada/{config}/{config}_bfs_limite_*.csv"
        archivos_bfs = glob.glob(patron_bfs)
        
        if not archivos_bfs:
            print(f"  ⚠️ No se encontraron archivos BFS para {config}")
            continue
        
        # Tomar el primer archivo BFS encontrado (normalmente solo hay uno por configuración)
        archivo_bfs = archivos_bfs[0]
        print(f"  ✓ Cargando: {archivo_bfs}")
        
        try:
            df_bfs = pd.read_csv(archivo_bfs)
            
            # Extraer la columna de nodos (variables)
            if 'nodo' in df_bfs.columns:
                variables = set(df_bfs['nodo'].tolist())
                variables_bfs_bic[config] = variables
                print(f"  📊 Variables encontradas: {len(variables)}")
                
                # Mostrar algunas variables
                if variables:
                    print(f"  🔍 Ejemplo (primeras 5): {list(variables)[:5]}")
            else:
                print(f"  ❌ No se encontró columna 'nodo' en {archivo_bfs}")
                print(f"    Columnas disponibles: {df_bfs.columns.tolist()}")
                
        except Exception as e:
            print(f"  ❌ Error al cargar {archivo_bfs}: {e}")
    
    print(f"\n✅ Total de configuraciones BiC cargadas: {len(variables_bfs_bic)}")
    return variables_bfs_bic

def cargar_variables_dfs_wic():
    """
    Carga todas las variables de las búsquedas DFS para configuraciones WiC (W2C, W4C, W8C, W16C)
    """
    print("\n" + "=" * 60)
    print("CARGANDO VARIABLES DFS DE CONFIGURACIONES WiC")
    print("=" * 60)
    
    variables_dfs_wic = {}
    
    # Configuraciones WiC a procesar
    configuraciones_wic = ['W2C', 'W4C', 'W8C', 'W16C']
    
    for config in configuraciones_wic:
        print(f"\n📂 Buscando archivos DFS para {config}...")
        
        # Patrón de búsqueda para archivos DFS de esta configuración
        patron_dfs = f"resultados_busqueda_limitada/{config}/{config}_dfs_limite_*.csv"
        archivos_dfs = glob.glob(patron_dfs)
        
        if not archivos_dfs:
            print(f"  ⚠️ No se encontraron archivos DFS para {config}")
            continue
        
        # Tomar el primer archivo DFS encontrado
        archivo_dfs = archivos_dfs[0]
        print(f"  ✓ Cargando: {archivo_dfs}")
        
        try:
            df_dfs = pd.read_csv(archivo_dfs)
            
            # Extraer la columna de nodos (variables)
            if 'nodo' in df_dfs.columns:
                variables = set(df_dfs['nodo'].tolist())
                variables_dfs_wic[config] = variables
                print(f"  📊 Variables encontradas: {len(variables)}")
                
                # Mostrar algunas variables
                if variables:
                    print(f"  🔍 Ejemplo (primeras 5): {list(variables)[:5]}")
            else:
                print(f"  ❌ No se encontró columna 'nodo' en {archivo_dfs}")
                print(f"    Columnas disponibles: {df_dfs.columns.tolist()}")
                
        except Exception as e:
            print(f"  ❌ Error al cargar {archivo_dfs}: {e}")
    
    print(f"\n✅ Total de configuraciones WiC cargadas: {len(variables_dfs_wic)}")
    return variables_dfs_wic

def calcular_uniones_por_configuracion(variables_bfs_bic, variables_dfs_wic):
    """
    Calcula uniones entre configuraciones correspondientes:
    B2C ∪ W2C, B4C ∪ W4C, B8C ∪ W8C, B16C ∪ W16C
    """
    print("\n" + "=" * 70)
    print("CALCULANDO UNIONES POR CONFIGURACIÓN")
    print("=" * 70)
    
    uniones_por_config = {}
    
    # Pares correspondientes (B2C-W2C, B4C-W4C, etc.)
    pares_config = [
        ('B2C', 'W2C'),
        ('B4C', 'W4C'),
        ('B8C', 'W8C'),
        ('B16C', 'W16C')
    ]
    
    for config_b, config_w in pares_config:
        print(f"\n🔗 Calculando {config_b} ∪ {config_w}...")
        
        if config_b in variables_bfs_bic and config_w in variables_dfs_wic:
            variables_b = variables_bfs_bic[config_b]
            variables_w = variables_dfs_wic[config_w]
            
            # Calcular unión
            union = variables_b.union(variables_w)
            
            uniones_por_config[f"{config_b}_∪_{config_w}"] = {
                'variables_b': variables_b,
                'variables_w': variables_w,
                'union': union,
                'count_b': len(variables_b),
                'count_w': len(variables_w),
                'count_union': len(union),
                'count_interseccion': len(variables_b.intersection(variables_w))
            }
            
            print(f"  📊 Variables en {config_b}: {len(variables_b)}")
            print(f"  📊 Variables en {config_w}: {len(variables_w)}")
            print(f"  ✅ Unión: {len(union)} variables")
            print(f"  🔍 Intersección: {len(variables_b.intersection(variables_w))} variables")
            
            if union:
                print(f"  📋 Total de variables únicas en la unión: {len(union)}")
        else:
            print(f"  ❌ No se pudieron cargar ambas configuraciones")
    
    return uniones_por_config

def calcular_union_todas_bic(variables_bfs_bic):
    """
    Calcula la unión de todas las configuraciones BiC
    """
    print("\n" + "=" * 60)
    print("CALCULANDO UNIÓN DE TODAS LAS CONFIGURACIONES BiC")
    print("=" * 60)
    
    if not variables_bfs_bic:
        print("❌ No hay datos de configuraciones BiC")
        return set()
    
    # Obtener lista de conjuntos de variables
    lista_conjuntos_bic = list(variables_bfs_bic.values())
    
    # Calcular unión de todos los conjuntos
    if lista_conjuntos_bic:
        union_bic = set()
        for conjunto in lista_conjuntos_bic:
            union_bic = union_bic.union(conjunto)
    else:
        union_bic = set()
    
    print(f"📊 Total de configuraciones BiC: {len(variables_bfs_bic)}")
    for config, variables in variables_bfs_bic.items():
        print(f"  {config}: {len(variables)} variables")
    
    print(f"\n✅ Unión de todas las BiC: {len(union_bic)} variables")
    if union_bic:
        print(f"📋 Variables en la unión BiC: {sorted(list(union_bic))}")
    
    return union_bic

def calcular_union_todas_wic(variables_dfs_wic):
    """
    Calcula la unión de todas las configuraciones WiC
    """
    print("\n" + "=" * 60)
    print("CALCULANDO UNIÓN DE TODAS LAS CONFIGURACIONES WiC")
    print("=" * 60)
    
    if not variables_dfs_wic:
        print("❌ No hay datos de configuraciones WiC")
        return set()
    
    # Obtener lista de conjuntos de variables
    lista_conjuntos_wic = list(variables_dfs_wic.values())
    
    # Calcular unión de todos los conjuntos
    if lista_conjuntos_wic:
        union_wic = set()
        for conjunto in lista_conjuntos_wic:
            union_wic = union_wic.union(conjunto)
    else:
        union_wic = set()
    
    print(f"📊 Total de configuraciones WiC: {len(variables_dfs_wic)}")
    for config, variables in variables_dfs_wic.items():
        print(f"  {config}: {len(variables)} variables")
    
    print(f"\n✅ Unión de todas las WiC: {len(union_wic)} variables")
    if union_wic:
        print(f"📋 Variables en la unión WiC: {sorted(list(union_wic))}")
    
    return union_wic

def calcular_union_final_b_w(union_bic, union_wic):
    """
    Calcula la unión final entre los resultados de B y W
    """
    print("\n" + "=" * 70)
    print("CALCULANDO UNIÓN FINAL (B ∪ W)")
    print("=" * 70)
    
    print(f"📊 Variables en unión BiC: {len(union_bic)}")
    print(f"📊 Variables en unión WiC: {len(union_wic)}")
    
    # Calcular unión final
    union_final = union_bic.union(union_wic)
    
    # Calcular intersección para estadísticas
    interseccion_final = union_bic.intersection(union_wic)
    
    print(f"\n🎯 UNIÓN FINAL (B ∪ W): {len(union_final)} variables")
    print(f"🔍 Intersección B ∩ W: {len(interseccion_final)} variables")
    
    if union_final:
        print(f"📋 Variables en la unión final: {sorted(list(union_final))}")
    
    return union_final, interseccion_final

def exportar_resultados(variables_bfs_bic, variables_dfs_wic, 
                       uniones_por_config, 
                       union_bic, union_wic, 
                       union_final, interseccion_final):
    """
    Exporta todos los resultados a archivos CSV
    """
    carpeta_salida = "resultados_uniones"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    print(f"\n" + "=" * 60)
    print("EXPORTANDO RESULTADOS A CSV")
    print("=" * 60)
    
    # 1. Exportar variables individuales de cada configuración
    print(f"\n📁 Exportando variables por configuración...")
    
    # Variables BiC (BFS)
    for config, variables in variables_bfs_bic.items():
        df_bic = pd.DataFrame(sorted(list(variables)), columns=['variables'])
        ruta_bic = os.path.join(carpeta_salida, f"variables_bfs_{config}.csv")
        df_bic.to_csv(ruta_bic, index=False)
        print(f"  ✓ {config} (BFS): {ruta_bic}")
    
    # Variables WiC (DFS)
    for config, variables in variables_dfs_wic.items():
        df_wic = pd.DataFrame(sorted(list(variables)), columns=['variables'])
        ruta_wic = os.path.join(carpeta_salida, f"variables_dfs_{config}.csv")
        df_wic.to_csv(ruta_wic, index=False)
        print(f"  ✓ {config} (DFS): {ruta_wic}")
    
    # 2. Exportar uniones por configuración
    print(f"\n📁 Exportando uniones por configuración...")
    
    datos_uniones = []
    for nombre_union, datos in uniones_por_config.items():
        variables_union = sorted(list(datos['union']))
        
        # Exportar lista de variables de la unión
        if variables_union:
            df_union = pd.DataFrame(variables_union, columns=['variables'])
            ruta_union = os.path.join(carpeta_salida, f"union_{nombre_union}.csv")
            df_union.to_csv(ruta_union, index=False)
            print(f"  ✓ {nombre_union}: {ruta_union}")
        
        # Guardar estadísticas para el resumen
        datos_uniones.append({
            'configuracion': nombre_union,
            'variables_b': datos['count_b'],
            'variables_w': datos['count_w'],
            'variables_union': datos['count_union'],
            'variables_interseccion': datos['count_interseccion']
        })
    
    # 3. Exportar unión de todas las BiC (B)
    print(f"\n📁 Exportando unión BiC (B)...")
    variables_bic_lista = sorted(list(union_bic))
    df_bic_final = pd.DataFrame(variables_bic_lista, columns=['variables'])
    ruta_bic_final = os.path.join(carpeta_salida, "union_B.csv")
    df_bic_final.to_csv(ruta_bic_final, index=False)
    print(f"  ✓ Unión B (BiC): {ruta_bic_final}")
    print(f"     Variables: {len(variables_bic_lista)}")
    
    # 4. Exportar unión de todas las WiC (W)
    print(f"\n📁 Exportando unión WiC (W)...")
    variables_wic_lista = sorted(list(union_wic))
    df_wic_final = pd.DataFrame(variables_wic_lista, columns=['variables'])
    ruta_wic_final = os.path.join(carpeta_salida, "union_W.csv")
    df_wic_final.to_csv(ruta_wic_final, index=False)
    print(f"  ✓ Unión W (WiC): {ruta_wic_final}")
    print(f"     Variables: {len(variables_wic_lista)}")
    
    # 5. Exportar unión final (B ∪ W)
    print(f"\n📁 Exportando unión final (B ∪ W)...")
    variables_final_lista = sorted(list(union_final))
    df_final = pd.DataFrame(variables_final_lista, columns=['variables'])
    ruta_final = os.path.join(carpeta_salida, "Lista_Completa.csv")
    df_final.to_csv(ruta_final, index=False)
    print(f"  🎯 Lista_Completa.csv: {ruta_final}")
    print(f"     Variables en unión final: {len(variables_final_lista)}")
    
    # 6. Exportar intersección B ∩ W (para referencia)
    print(f"\n📁 Exportando intersección B ∩ W (referencia)...")
    variables_interseccion_lista = sorted(list(interseccion_final))
    df_interseccion = pd.DataFrame(variables_interseccion_lista, columns=['variables'])
    ruta_interseccion = os.path.join(carpeta_salida, "interseccion_B_W.csv")
    df_interseccion.to_csv(ruta_interseccion, index=False)
    print(f"  🔍 Intersección B∩W: {ruta_interseccion}")
    print(f"     Variables comunes: {len(variables_interseccion_lista)}")
    
    # 7. Exportar resumen estadístico
    print(f"\n📁 Exportando resumen estadístico...")
    
    # Crear DataFrame de resumen
    df_resumen_uniones = pd.DataFrame(datos_uniones)
    ruta_resumen_uniones = os.path.join(carpeta_salida, "resumen_uniones.csv")
    df_resumen_uniones.to_csv(ruta_resumen_uniones, index=False)
    print(f"  ✓ Resumen uniones: {ruta_resumen_uniones}")
    
    # Resumen final consolidado
    datos_resumen_final = {
        'tipo': ['Unión B (BiC)', 'Unión W (WiC)', 'Unión Final (B ∪ W)', 'Intersección B∩W'],
        'numero_variables': [len(union_bic), len(union_wic), len(union_final), len(interseccion_final)],
        'variables': [', '.join(sorted(list(union_bic))), 
                     ', '.join(sorted(list(union_wic))), 
                     ', '.join(sorted(list(union_final))),
                     ', '.join(sorted(list(interseccion_final)))]
    }
    
    df_resumen_final = pd.DataFrame(datos_resumen_final)
    ruta_resumen_final = os.path.join(carpeta_salida, "resumen_final.csv")
    df_resumen_final.to_csv(ruta_resumen_final, index=False)
    print(f"  ✓ Resumen final: {ruta_resumen_final}")
    
    print(f"\n✅ Todos los resultados exportados a: {carpeta_salida}/")

def generar_reporte_estadisticas(variables_bfs_bic, variables_dfs_wic,
                               union_bic, union_wic,
                               union_final, interseccion_final):
    """
    Genera un reporte estadístico detallado
    """
    print("\n" + "=" * 80)
    print("REPORTE ESTADÍSTICO DETALLADO")
    print("=" * 80)
    
    # Estadísticas de configuraciones individuales
    print(f"\n📊 ESTADÍSTICAS POR CONFIGURACIÓN:")
    print(f"{'Configuración':<10} {'Tipo':<6} {'Variables':<12}")
    print("-" * 40)
    
    total_variables_b = 0
    total_variables_w = 0
    
    for config in ['B2C', 'B4C', 'B8C', 'B16C']:
        if config in variables_bfs_bic:
            count = len(variables_bfs_bic[config])
            total_variables_b += count
            print(f"{config:<10} {'BFS':<6} {count:<12}")
    
    print("-" * 40)
    
    for config in ['W2C', 'W4C', 'W8C', 'W16C']:
        if config in variables_dfs_wic:
            count = len(variables_dfs_wic[config])
            total_variables_w += count
            print(f"{config:<10} {'DFS':<6} {count:<12}")
    
    # Estadísticas de uniones e intersecciones
    print(f"\n🎯 ESTADÍSTICAS DE UNIONES E INTERSECCIONES:")
    print(f"{'Tipo':<25} {'Variables':<12}")
    print("-" * 40)
    print(f"{'Unión B (BiC)':<25} {len(union_bic):<12}")
    print(f"{'Unión W (WiC)':<25} {len(union_wic):<12}")
    print(f"{'Unión Final (B∪W)':<25} {len(union_final):<12}")
    print(f"{'Intersección (B∩W)':<25} {len(interseccion_final):<12}")
    
    # Porcentajes
    print(f"\n📈 PORCENTAJES:")
    if total_variables_b > 0:
        print(f"Unión B contiene {len(union_bic)} de {total_variables_b} variables únicas de BiC")
    
    if total_variables_w > 0:
        print(f"Unión W contiene {len(union_wic)} de {total_variables_w} variables únicas de WiC")
    
    if len(union_bic) > 0 and len(union_wic) > 0:
        porcentaje_interseccion = len(interseccion_final) / len(union_final) * 100
        print(f"La intersección representa el {porcentaje_interseccion:.1f}% de la unión final")
    
    # Variables en la unión final
    print(f"\n📋 VARIABLES EN LA UNIÓN FINAL (Lista_Completa):")
    if union_final:
        print(f"  Total: {len(union_final)} variables únicas")
        print(f"  Primeras 10 variables:")
        for i, variable in enumerate(sorted(list(union_final))[:10], 1):
            print(f"    {i:2}. {variable}")
        if len(union_final) > 10:
            print(f"    ... y {len(union_final) - 10} más")
    else:
        print("  No hay variables en la unión final")

def main():
    """
    Función principal
    """
    print("=" * 80)
    print("UNIÓN DE VARIABLES: BFS(BiC) ∪ DFS(WiC)")
    print("=" * 80)
    print("Objetivo: Combinar todas las variables encontradas en:")
    print("  • BFS en configuraciones BiC (B2C, B4C, B8C, B16C)")
    print("  • DFS en configuraciones WiC (W2C, W4C, W8C, W16C)")
    print("\nPasos:")
    print("  1. Cargar variables de BFS para cada BiC")
    print("  2. Cargar variables de DFS para cada WiC")
    print("  3. Calcular unión por configuración (B2C∪W2C, etc.)")
    print("  4. Calcular unión de todas las BiC → B")
    print("  5. Calcular unión de todas las WiC → W")
    print("  6. Calcular unión final B ∪ W → Lista_Completa")
    print("=" * 80)
    
    # 1. Cargar variables de BFS para configuraciones BiC
    variables_bfs_bic = cargar_variables_bfs_bic()
    
    # 2. Cargar variables de DFS para configuraciones WiC
    variables_dfs_wic = cargar_variables_dfs_wic()
    
    if not variables_bfs_bic or not variables_dfs_wic:
        print("\n❌ ERROR: No se pudieron cargar suficientes datos.")
        print("Asegúrate de que los archivos de resultados existan en:")
        print("  resultados_busqueda_limitada/{config}/{config}_bfs_limite_*.csv")
        print("  resultados_busqueda_limitada/{config}/{config}_dfs_limite_*.csv")
        return
    
    # 3. Calcular uniones por configuración correspondiente
    uniones_por_config = calcular_uniones_por_configuracion(
        variables_bfs_bic, variables_dfs_wic
    )
    
    # 4. Calcular unión de todas las BiC
    union_bic = calcular_union_todas_bic(variables_bfs_bic)
    
    # 5. Calcular unión de todas las WiC
    union_wic = calcular_union_todas_wic(variables_dfs_wic)
    
    # 6. Calcular unión final B ∪ W
    union_final, interseccion_final = calcular_union_final_b_w(union_bic, union_wic)
    
    # 7. Exportar resultados
    exportar_resultados(
        variables_bfs_bic, variables_dfs_wic,
        uniones_por_config,
        union_bic, union_wic,
        union_final, interseccion_final
    )
    
    # 8. Generar reporte estadístico
    generar_reporte_estadisticas(
        variables_bfs_bic, variables_dfs_wic,
        union_bic, union_wic,
        union_final, interseccion_final
    )
    
    print(f"\n{'=' * 80}")
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print(f"{'=' * 80}")
    print(f"🎯 Archivos generados en la carpeta: resultados_uniones/")
    print(f"📁 Archivos principales:")
    print(f"   • union_B.csv - Unión de todas las BiC")
    print(f"   • union_W.csv - Unión de todas las WiC")
    print(f"   • Lista_Completa.csv - Unión final B ∪ W (todas las variables únicas)")
    print(f"   • interseccion_B_W.csv - Variables comunes a B y W (referencia)")
    print(f"\n📊 Resumen de archivos generados:")
    print(f"   • variables_bfs_*.csv - Variables individuales por configuración BiC")
    print(f"   • variables_dfs_*.csv - Variables individuales por configuración WiC")
    print(f"   • union_*_∪_*.csv - Uniones por configuración")
    print(f"   • resumen_uniones.csv - Estadísticas de uniones")
    print(f"   • resumen_final.csv - Resumen consolidado")

if __name__ == "__main__":
    main()
