# interseccion_variables_bfs_dfs.py
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

def calcular_intersecciones_por_configuracion(variables_bfs_bic, variables_dfs_wic):
    """
    Calcula intersecciones entre configuraciones correspondientes:
    B2C ∩ W2C, B4C ∩ W4C, B8C ∩ W8C, B16C ∩ W16C
    """
    print("\n" + "=" * 70)
    print("CALCULANDO INTERSECCIONES POR CONFIGURACIÓN")
    print("=" * 70)
    
    intersecciones_por_config = {}
    
    # Pares correspondientes (B2C-W2C, B4C-W4C, etc.)
    pares_config = [
        ('B2C', 'W2C'),
        ('B4C', 'W4C'),
        ('B8C', 'W8C'),
        ('B16C', 'W16C')
    ]
    
    for config_b, config_w in pares_config:
        print(f"\n🔗 Calculando {config_b} ∩ {config_w}...")
        
        if config_b in variables_bfs_bic and config_w in variables_dfs_wic:
            variables_b = variables_bfs_bic[config_b]
            variables_w = variables_dfs_wic[config_w]
            
            # Calcular intersección
            interseccion = variables_b.intersection(variables_w)
            
            intersecciones_por_config[f"{config_b}_∩_{config_w}"] = {
                'variables_b': variables_b,
                'variables_w': variables_w,
                'interseccion': interseccion,
                'count_b': len(variables_b),
                'count_w': len(variables_w),
                'count_interseccion': len(interseccion)
            }
            
            print(f"  📊 Variables en {config_b}: {len(variables_b)}")
            print(f"  📊 Variables en {config_w}: {len(variables_w)}")
            print(f"  ✅ Intersección: {len(interseccion)} variables")
            
            if interseccion:
                print(f"  🔍 Variables comunes: {sorted(list(interseccion))}")
            else:
                print(f"  ⚠️ No hay variables comunes")
        else:
            print(f"  ❌ No se pudieron cargar ambas configuraciones")
    
    return intersecciones_por_config

def calcular_interseccion_todas_bic(variables_bfs_bic):
    """
    Calcula la intersección de todas las configuraciones BiC
    """
    print("\n" + "=" * 60)
    print("CALCULANDO INTERSECCIÓN DE TODAS LAS CONFIGURACIONES BiC")
    print("=" * 60)
    
    if not variables_bfs_bic:
        print("❌ No hay datos de configuraciones BiC")
        return set()
    
    # Obtener lista de conjuntos de variables
    lista_conjuntos_bic = list(variables_bfs_bic.values())
    
    # Calcular intersección de todos los conjuntos
    if lista_conjuntos_bic:
        interseccion_bic = set.intersection(*lista_conjuntos_bic)
    else:
        interseccion_bic = set()
    
    print(f"📊 Total de configuraciones BiC: {len(variables_bfs_bic)}")
    for config, variables in variables_bfs_bic.items():
        print(f"  {config}: {len(variables)} variables")
    
    print(f"\n✅ Intersección de todas las BiC: {len(interseccion_bic)} variables")
    if interseccion_bic:
        print(f"🔍 Variables comunes a todas las BiC: {sorted(list(interseccion_bic))}")
    else:
        print("⚠️ No hay variables comunes a todas las configuraciones BiC")
    
    return interseccion_bic

def calcular_interseccion_todas_wic(variables_dfs_wic):
    """
    Calcula la intersección de todas las configuraciones WiC
    """
    print("\n" + "=" * 60)
    print("CALCULANDO INTERSECCIÓN DE TODAS LAS CONFIGURACIONES WiC")
    print("=" * 60)
    
    if not variables_dfs_wic:
        print("❌ No hay datos de configuraciones WiC")
        return set()
    
    # Obtener lista de conjuntos de variables
    lista_conjuntos_wic = list(variables_dfs_wic.values())
    
    # Calcular intersección de todos los conjuntos
    if lista_conjuntos_wic:
        interseccion_wic = set.intersection(*lista_conjuntos_wic)
    else:
        interseccion_wic = set()
    
    print(f"📊 Total de configuraciones WiC: {len(variables_dfs_wic)}")
    for config, variables in variables_dfs_wic.items():
        print(f"  {config}: {len(variables)} variables")
    
    print(f"\n✅ Intersección de todas las WiC: {len(interseccion_wic)} variables")
    if interseccion_wic:
        print(f"🔍 Variables comunes a todas las WiC: {sorted(list(interseccion_wic))}")
    else:
        print("⚠️ No hay variables comunes a todas las configuraciones WiC")
    
    return interseccion_wic

def calcular_interseccion_final_b_w(interseccion_bic, interseccion_wic):
    """
    Calcula la intersección final entre los resultados de B y W
    """
    print("\n" + "=" * 70)
    print("CALCULANDO INTERSECCIÓN FINAL (B ∩ W)")
    print("=" * 70)
    
    print(f"📊 Variables en intersección BiC: {len(interseccion_bic)}")
    print(f"📊 Variables en intersección WiC: {len(interseccion_wic)}")
    
    # Calcular intersección final
    interseccion_final = interseccion_bic.intersection(interseccion_wic)
    
    print(f"\n🎯 INTERSECCIÓN FINAL (B ∩ W): {len(interseccion_final)} variables")
    
    if interseccion_final:
        print(f"🔍 Variables en la intersección final: {sorted(list(interseccion_final))}")
    else:
        print("⚠️ No hay variables en la intersección final")
    
    return interseccion_final

def exportar_resultados(variables_bfs_bic, variables_dfs_wic, 
                       intersecciones_por_config, 
                       interseccion_bic, interseccion_wic, 
                       interseccion_final):
    """
    Exporta todos los resultados a archivos CSV
    """
    carpeta_salida = "resultados_intersecciones"
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
    
    # 2. Exportar intersecciones por configuración
    print(f"\n📁 Exportando intersecciones por configuración...")
    
    datos_intersecciones = []
    for nombre_interseccion, datos in intersecciones_por_config.items():
        variables_interseccion = sorted(list(datos['interseccion']))
        
        # Exportar lista de variables de la intersección
        if variables_interseccion:
            df_interseccion = pd.DataFrame(variables_interseccion, columns=['variables'])
            ruta_interseccion = os.path.join(carpeta_salida, f"interseccion_{nombre_interseccion}.csv")
            df_interseccion.to_csv(ruta_interseccion, index=False)
            print(f"  ✓ {nombre_interseccion}: {ruta_interseccion}")
        
        # Guardar estadísticas para el resumen
        datos_intersecciones.append({
            'configuracion': nombre_interseccion,
            'variables_b': datos['count_b'],
            'variables_w': datos['count_w'],
            'variables_interseccion': datos['count_interseccion']
        })
    
    # 3. Exportar intersección de todas las BiC (B)
    print(f"\n📁 Exportando intersección BiC (B)...")
    variables_bic_lista = sorted(list(interseccion_bic))
    df_bic_final = pd.DataFrame(variables_bic_lista, columns=['variables'])
    ruta_bic_final = os.path.join(carpeta_salida, "interseccion_B.csv")
    df_bic_final.to_csv(ruta_bic_final, index=False)
    print(f"  ✓ Intersección B (BiC): {ruta_bic_final}")
    print(f"     Variables: {len(variables_bic_lista)}")
    
    # 4. Exportar intersección de todas las WiC (W)
    print(f"\n📁 Exportando intersección WiC (W)...")
    variables_wic_lista = sorted(list(interseccion_wic))
    df_wic_final = pd.DataFrame(variables_wic_lista, columns=['variables'])
    ruta_wic_final = os.path.join(carpeta_salida, "interseccion_W.csv")
    df_wic_final.to_csv(ruta_wic_final, index=False)
    print(f"  ✓ Intersección W (WiC): {ruta_wic_final}")
    print(f"     Variables: {len(variables_wic_lista)}")
    
    # 5. Exportar intersección final (B ∩ W)
    print(f"\n📁 Exportando intersección final (B ∩ W)...")
    variables_final_lista = sorted(list(interseccion_final))
    df_final = pd.DataFrame(variables_final_lista, columns=['variables'])
    ruta_final = os.path.join(carpeta_salida, "Lista_Con_Raiz.csv")
    df_final.to_csv(ruta_final, index=False)
    print(f"  🎯 Lista_Con_Raiz.csv: {ruta_final}")
    print(f"     Variables finales: {len(variables_final_lista)}")
    
    # 6. Exportar resumen estadístico
    print(f"\n📁 Exportando resumen estadístico...")
    
    # Crear DataFrame de resumen
    df_resumen_intersecciones = pd.DataFrame(datos_intersecciones)
    ruta_resumen_intersecciones = os.path.join(carpeta_salida, "resumen_intersecciones.csv")
    df_resumen_intersecciones.to_csv(ruta_resumen_intersecciones, index=False)
    print(f"  ✓ Resumen intersecciones: {ruta_resumen_intersecciones}")
    
    # Resumen final consolidado
    datos_resumen_final = {
        'tipo': ['Intersección B (BiC)', 'Intersección W (WiC)', 'Intersección Final (B ∩ W)'],
        'numero_variables': [len(interseccion_bic), len(interseccion_wic), len(interseccion_final)],
        'variables': [', '.join(sorted(list(interseccion_bic))), 
                     ', '.join(sorted(list(interseccion_wic))), 
                     ', '.join(sorted(list(interseccion_final)))]
    }
    
    df_resumen_final = pd.DataFrame(datos_resumen_final)
    ruta_resumen_final = os.path.join(carpeta_salida, "resumen_final.csv")
    df_resumen_final.to_csv(ruta_resumen_final, index=False)
    print(f"  ✓ Resumen final: {ruta_resumen_final}")
    
    print(f"\n✅ Todos los resultados exportados a: {carpeta_salida}/")

def generar_reporte_estadisticas(variables_bfs_bic, variables_dfs_wic,
                               interseccion_bic, interseccion_wic,
                               interseccion_final):
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
    
    # Estadísticas de intersecciones
    print(f"\n🎯 ESTADÍSTICAS DE INTERSECCIONES:")
    print(f"{'Tipo de intersección':<25} {'Variables':<12}")
    print("-" * 40)
    print(f"{'Intersección B (BiC)':<25} {len(interseccion_bic):<12}")
    print(f"{'Intersección W (WiC)':<25} {len(interseccion_wic):<12}")
    print(f"{'Intersección Final (B∩W)':<25} {len(interseccion_final):<12}")
    
    # Porcentajes
    if total_variables_b > 0 and total_variables_w > 0:
        print(f"\n📈 PORCENTAJES:")
        avg_b = len(interseccion_bic) / total_variables_b * 100 if total_variables_b > 0 else 0
        avg_w = len(interseccion_wic) / total_variables_w * 100 if total_variables_w > 0 else 0
        
        print(f"Intersección B representa el {avg_b:.1f}% de las variables BiC totales")
        print(f"Intersección W representa el {avg_w:.1f}% de las variables WiC totales")
    
    # Variables en la intersección final
    print(f"\n🔍 VARIABLES EN LA INTERSECCIÓN FINAL (Lista_Con_Raiz):")
    if interseccion_final:
        for i, variable in enumerate(sorted(list(interseccion_final)), 1):
            print(f"  {i:2}. {variable}")
    else:
        print("  No hay variables en la intersección final")

def main():
    """
    Función principal
    """
    print("=" * 80)
    print("INTERSECCIÓN DE VARIABLES: BFS(BiC) ∩ DFS(WiC)")
    print("=" * 80)
    print("Objetivo: Encontrar variables comunes entre:")
    print("  • BFS en configuraciones BiC (B2C, B4C, B8C, B16C)")
    print("  • DFS en configuraciones WiC (W2C, W4C, W8C, W16C)")
    print("\nPasos:")
    print("  1. Cargar variables de BFS para cada BiC")
    print("  2. Cargar variables de DFS para cada WiC")
    print("  3. Calcular intersección por configuración (B2C∩W2C, etc.)")
    print("  4. Calcular intersección de todas las BiC → B")
    print("  5. Calcular intersección de todas las WiC → W")
    print("  6. Calcular intersección final B ∩ W → Lista_Con_Raiz")
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
    
    # 3. Calcular intersecciones por configuración correspondiente
    intersecciones_por_config = calcular_intersecciones_por_configuracion(
        variables_bfs_bic, variables_dfs_wic
    )
    
    # 4. Calcular intersección de todas las BiC
    interseccion_bic = calcular_interseccion_todas_bic(variables_bfs_bic)
    
    # 5. Calcular intersección de todas las WiC
    interseccion_wic = calcular_interseccion_todas_wic(variables_dfs_wic)
    
    # 6. Calcular intersección final B ∩ W
    interseccion_final = calcular_interseccion_final_b_w(interseccion_bic, interseccion_wic)
    
    # 7. Exportar resultados
    exportar_resultados(
        variables_bfs_bic, variables_dfs_wic,
        intersecciones_por_config,
        interseccion_bic, interseccion_wic,
        interseccion_final
    )
    
    # 8. Generar reporte estadístico
    generar_reporte_estadisticas(
        variables_bfs_bic, variables_dfs_wic,
        interseccion_bic, interseccion_wic,
        interseccion_final
    )
    
    print(f"\n{'=' * 80}")
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print(f"{'=' * 80}")
    print(f"🎯 Archivos generados en la carpeta: resultados_intersecciones/")
    print(f"📁 Archivos principales:")
    print(f"   • interseccion_B.csv - Variables comunes a todas las BiC")
    print(f"   • interseccion_W.csv - Variables comunes a todas las WiC")
    print(f"   • Lista_Con_Raiz.csv - Intersección final B ∩ W")
    print(f"\n📊 Resumen de archivos generados:")
    print(f"   • variables_bfs_*.csv - Variables individuales por configuración BiC")
    print(f"   • variables_dfs_*.csv - Variables individuales por configuración WiC")
    print(f"   • interseccion_*_∩_*.csv - Intersecciones por configuración")
    print(f"   • resumen_intersecciones.csv - Estadísticas de intersecciones")
    print(f"   • resumen_final.csv - Resumen consolidado")

if __name__ == "__main__":
    main()

    
"""
resultados_intersecciones/
├── interseccion_B.csv          # Variables comunes a todas las BiC
├── interseccion_W.csv          # Variables comunes a todas las WiC
├── Lista_Con_Raiz.csv          # Intersección final B ∩ W
├── variables_bfs_B2C.csv       # Variables BFS de B2C
├── variables_bfs_B4C.csv       # Variables BFS de B4C
├── ...
├── variables_dfs_W2C.csv       # Variables DFS de W2C
├── ...
├── interseccion_B2C_∩_W2C.csv  # Intersección B2C ∩ W2C
├── interseccion_B4C_∩_W4C.csv  # Intersección B4C ∩ W4C
├── ...
├── resumen_intersecciones.csv  # Estadísticas de intersecciones
└── resumen_final.csv           # Resumen consolidado
"""