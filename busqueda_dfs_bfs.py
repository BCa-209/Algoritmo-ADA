# busqueda_dfs_bfs.py
import pandas as pd
import networkx as nx
import os
import re
from datetime import datetime

def cargar_arbol_enraizado(ruta_archivo):
    """
    Carga el árbol enraizado desde archivo GML
    """
    try:
        arbol = nx.read_gml(ruta_archivo)
        nombre_archivo = os.path.basename(ruta_archivo)
        nombre_grafo = nombre_archivo.replace('.gml', '')
        
        print(f"Árbol enraizado cargado: {nombre_grafo}")
        print(f"  Nodos: {arbol.number_of_nodes()}")
        print(f"  Aristas: {arbol.number_of_edges()}")
        
        return arbol, nombre_grafo
    except Exception as e:
        print(f"Error cargando {ruta_archivo}: {e}")
        return None, None

def extraer_configuracion_archivo(nombre_archivo):
    """
    Extrae la configuración (B4C, W2C, etc.) del nombre del archivo
    """
    # Patrones para detectar la configuración
    patrones = [
        r'(B|W)(\d+)C',  # B4C, W2C, etc.
        r'reducido_(B|W)(\d+)C',  # arbol_reducido_B4C...
        r'enraizado_(B|W)(\d+)C'  # arbol_enraizado_B4C...
    ]
    
    for patron in patrones:
        match = re.search(patron, nombre_archivo)
        if match:
            tipo = match.group(1)  # B o W
            qrtl = match.group(2)  # 2, 4, 8, 16
            return f"{tipo}{qrtl}C"
    
    # Si no encuentra patrón, usar el nombre del archivo sin extensión
    return nombre_archivo.replace('.gml', '')

def encontrar_nodo_raiz(arbol):
    """
    Encuentra el nodo raíz del árbol (nodo con grado de entrada 0)
    """
    raices = [nodo for nodo in arbol.nodes() if arbol.in_degree(nodo) == 0]
    if raices:
        return raices[0]
    else:
        # Si no hay nodo con grado de entrada 0, buscar el que tiene más conexiones
        return max(arbol.nodes(), key=lambda x: arbol.out_degree(x))

def busqueda_anchura_limitada(arbol, nodo_inicio, limite_nivel=3):
    """
    Realiza búsqueda en anchura (BFS) desde el nodo inicial con límite de niveles
    """
    print(f"\n" + "="*50)
    print(f"BÚSQUEDA EN ANCHURA (BFS) - Desde: {nodo_inicio} - Límite: {limite_nivel} niveles")
    print("="*50)
    
    visitados = set()
    cola = [nodo_inicio]
    orden_bfs = []
    niveles = {}
    nivel_actual = 0
    nodos_por_nivel = {nivel_actual: [nodo_inicio]}
    
    while cola and nivel_actual < limite_nivel:
        siguiente_nivel = []
        
        for nodo_actual in cola:
            if nodo_actual not in visitados:
                visitados.add(nodo_actual)
                orden_bfs.append(nodo_actual)
                
                # Obtener sucesores (hijos) del nodo actual
                sucesores = list(arbol.successors(nodo_actual))
                siguiente_nivel.extend(sucesores)
                
                if sucesores:
                    nodos_por_nivel[nivel_actual + 1] = nodos_por_nivel.get(nivel_actual + 1, []) + sucesores
        
        cola = siguiente_nivel
        nivel_actual += 1
    
    # Mostrar resultados
    print(f"Orden de visita BFS (limitado a {limite_nivel} niveles):")
    print(f"{' → '.join(orden_bfs)}")
    print(f"Total de nodos visitados: {len(orden_bfs)}")
    
    print(f"\nEstructura por niveles (hasta nivel {limite_nivel}):")
    for nivel in range(min(limite_nivel + 1, len(nodos_por_nivel))):
        if nivel in nodos_por_nivel and nodos_por_nivel[nivel]:
            print(f"  Nivel {nivel}: {nodos_por_nivel[nivel]}")
    
    return orden_bfs, nodos_por_nivel

def busqueda_profundidad_limitada(arbol, nodo_inicio, limite_profundidad=3):
    """
    Realiza búsqueda en profundidad (DFS) desde el nodo inicial con límite de profundidad
    """
    print(f"\n" + "="*50)
    print(f"BÚSQUEDA EN PROFUNDIDAD (DFS) - Desde: {nodo_inicio} - Límite: {limite_profundidad} niveles")
    print("="*50)
    
    visitados = set()
    orden_dfs = []
    caminos_completos = []
    
    def dfs_recursivo(nodo_actual, camino_actual, profundidad_actual):
        # Si superamos el límite de profundidad, detener la recursión
        if profundidad_actual > limite_profundidad:
            return
        
        if nodo_actual not in visitados:
            visitados.add(nodo_actual)
            camino_actual.append(nodo_actual)
            orden_dfs.append(nodo_actual)
            
            # Obtener sucesores (hijos)
            sucesores = list(arbol.successors(nodo_actual))
            
            if not sucesores or profundidad_actual == limite_profundidad:  # Es una hoja o límite alcanzado
                caminos_completos.append(camino_actual.copy())
                print(f"  Camino (profundidad {profundidad_actual}): {' → '.join(camino_actual)}")
            else:
                for sucesor in sucesores:
                    dfs_recursivo(sucesor, camino_actual.copy(), profundidad_actual + 1)
    
    dfs_recursivo(nodo_inicio, [], 0)
    
    # Mostrar resultados
    print(f"\nOrden de visita DFS (limitado a {limite_profundidad} niveles):")
    print(f"{' → '.join(orden_dfs)}")
    print(f"Total de nodos visitados: {len(orden_dfs)}")
    print(f"Caminos completos encontrados: {len(caminos_completos)}")
    
    return orden_dfs, caminos_completos

def analizar_estructura_arbol(arbol, nodo_raiz):
    """
    Analiza la estructura completa del árbol
    """
    print(f"\n" + "="*60)
    print(f"ANÁLISIS COMPLETO DEL ÁRBOL - Raíz: {nodo_raiz}")
    print("="*60)
    
    # Información básica
    print(f"Información del árbol:")
    print(f"  - Total de nodos: {arbol.number_of_nodes()}")
    print(f"  - Total de aristas: {arbol.number_of_edges()}")
    print(f"  - Nodo raíz: {nodo_raiz}")
    
    # Calcular profundidad máxima
    try:
        profundidades = [nx.shortest_path_length(arbol, nodo_raiz, nodo) 
                        for nodo in arbol.nodes() if nodo != nodo_raiz]
        profundidad_maxima = max(profundidades) if profundidades else 0
        print(f"  - Profundidad máxima: {profundidad_maxima}")
    except:
        profundidad_maxima = 0
        print(f"  - Profundidad máxima: 0")
    
    # Encontrar hojas
    hojas = [nodo for nodo in arbol.nodes() if arbol.out_degree(nodo) == 0]
    print(f"  - Hojas del árbol ({len(hojas)}): {hojas}")
    
    # Encontrar nodos internos (no raíz y no hoja)
    nodos_internos = [nodo for nodo in arbol.nodes() 
                     if nodo != nodo_raiz and arbol.out_degree(nodo) > 0]
    print(f"  - Nodos internos ({len(nodos_internos)}): {nodos_internos}")
    
    return profundidad_maxima, hojas, nodos_internos

def exportar_resultados_busqueda_limitada(arbol, configuracion, orden_bfs, orden_dfs, caminos_dfs, limite_bfs, limite_dfs):
    """
    Exporta los resultados de las búsquedas limitadas a archivos CSV
    """
    carpeta_salida = "resultados_busqueda_limitada"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Crear subcarpeta para la configuración actual
    carpeta_config = os.path.join(carpeta_salida, configuracion)
    if not os.path.exists(carpeta_config):
        os.makedirs(carpeta_config)
    
    # Exportar resultados BFS limitada
    datos_bfs = []
    for i, nodo in enumerate(orden_bfs, 1):
        datos_bfs.append({
            'orden': i,
            'nodo': nodo,
            'grado_salida': arbol.out_degree(nodo),
            'grado_entrada': arbol.in_degree(nodo),
            'es_hoja': arbol.out_degree(nodo) == 0,
            'es_raiz': arbol.in_degree(nodo) == 0
        })
    
    df_bfs = pd.DataFrame(datos_bfs)
    ruta_bfs = os.path.join(carpeta_config, f"{configuracion}_bfs_limite_{limite_bfs}.csv")
    df_bfs.to_csv(ruta_bfs, index=False)
    print(f"✓ Resultados BFS (limite {limite_bfs}) guardados: {ruta_bfs}")
    
    # Exportar resultados DFS limitada
    datos_dfs = []
    for i, nodo in enumerate(orden_dfs, 1):
        datos_dfs.append({
            'orden': i,
            'nodo': nodo,
            'grado_salida': arbol.out_degree(nodo),
            'grado_entrada': arbol.in_degree(nodo),
            'es_hoja': arbol.out_degree(nodo) == 0,
            'es_raiz': arbol.in_degree(nodo) == 0
        })
    
    df_dfs = pd.DataFrame(datos_dfs)
    ruta_dfs = os.path.join(carpeta_config, f"{configuracion}_dfs_limite_{limite_dfs}.csv")
    df_dfs.to_csv(ruta_dfs, index=False)
    print(f"✓ Resultados DFS (limite {limite_dfs}) guardados: {ruta_dfs}")
    
    # Exportar caminos DFS completos (limitados)
    datos_caminos = []
    for i, camino in enumerate(caminos_dfs, 1):
        datos_caminos.append({
            'camino_id': i,
            'camino': ' → '.join(camino),
            'longitud': len(camino) - 1,
            'nodo_inicio': camino[0],
            'nodo_fin': camino[-1],
            'niveles_recorridos': len(camino) - 1,
            'limite_aplicado': limite_dfs
        })
    
    df_caminos = pd.DataFrame(datos_caminos)
    ruta_caminos = os.path.join(carpeta_config, f"{configuracion}_caminos_dfs_limite_{limite_dfs}.csv")
    df_caminos.to_csv(ruta_caminos, index=False)
    print(f"✓ Caminos DFS (limite {limite_dfs}) guardados: {ruta_caminos}")
    
    # Exportar resumen consolidado
    datos_resumen = {
        'configuracion': [configuracion],
        'limite_bfs': [limite_bfs],
        'limite_dfs': [limite_dfs],
        'nodos_visitados_bfs': [len(orden_bfs)],
        'nodos_visitados_dfs': [len(orden_dfs)],
        'caminos_dfs_encontrados': [len(caminos_dfs)],
        'nodos_total_arbol': [arbol.number_of_nodes()],
        'aristas_total_arbol': [arbol.number_of_edges()]
    }
    
    df_resumen = pd.DataFrame(datos_resumen)
    ruta_resumen = os.path.join(carpeta_config, f"{configuracion}_resumen_limites.csv")
    df_resumen.to_csv(ruta_resumen, index=False)
    print(f"✓ Resumen consolidado guardado: {ruta_resumen}")
    
    return df_bfs, df_dfs, df_caminos, df_resumen

def exportar_variables_comunes(configuracion, variables_bfs, variables_dfs):
    """
    Exporta las variables comunes entre BFS y DFS, y sus diferencias
    """
    carpeta_salida = "resultados_busqueda_limitada"
    carpeta_config = os.path.join(carpeta_salida, configuracion)
    
    if not os.path.exists(carpeta_config):
        os.makedirs(carpeta_config)
    
    # Convertir a conjuntos para operaciones de conjunto
    set_bfs = set(variables_bfs)
    set_dfs = set(variables_dfs)
    
    # Encontrar variables comunes
    comunes = sorted(list(set_bfs.intersection(set_dfs)))
    
    # Encontrar variables únicas en cada búsqueda
    unicas_bfs = sorted(list(set_bfs - set_dfs))
    unicas_dfs = sorted(list(set_dfs - set_bfs))
    
    # Crear DataFrames para cada conjunto
    df_comunes = pd.DataFrame(comunes, columns=['variables_comunes'])
    df_unicas_bfs = pd.DataFrame(unicas_bfs, columns=['variables_unicas_bfs'])
    df_unicas_dfs = pd.DataFrame(unicas_dfs, columns=['variables_unicas_dfs'])
    
    # Guardar archivos
    ruta_comunes = os.path.join(carpeta_config, f"{configuracion}_variables_comunes.csv")
    df_comunes.to_csv(ruta_comunes, index=False)
    print(f"✓ Variables comunes guardadas: {ruta_comunes}")
    
    if unicas_bfs:
        ruta_unicas_bfs = os.path.join(carpeta_config, f"{configuracion}_variables_unicas_bfs.csv")
        df_unicas_bfs.to_csv(ruta_unicas_bfs, index=False)
        print(f"✓ Variables únicas BFS guardadas: {ruta_unicas_bfs}")
    
    if unicas_dfs:
        ruta_unicas_dfs = os.path.join(carpeta_config, f"{configuracion}_variables_unicas_dfs.csv")
        df_unicas_dfs.to_csv(ruta_unicas_dfs, index=False)
        print(f"✓ Variables únicas DFS guardadas: {ruta_unicas_dfs}")
    
    # Crear resumen de comparación
    datos_comparacion = {
        'tipo_comparacion': ['Comunes', 'Únicas BFS', 'Únicas DFS', 'Total BFS', 'Total DFS'],
        'cantidad': [len(comunes), len(unicas_bfs), len(unicas_dfs), len(variables_bfs), len(variables_dfs)]
    }
    
    df_comparacion = pd.DataFrame(datos_comparacion)
    ruta_comparacion = os.path.join(carpeta_config, f"{configuracion}_comparacion_variables.csv")
    df_comparacion.to_csv(ruta_comparacion, index=False)
    print(f"✓ Comparación de variables guardada: {ruta_comparacion}")
    
    return df_comunes, df_unicas_bfs, df_unicas_dfs

def procesar_archivo_gml(ruta_archivo, limite_bfs=3, limite_dfs=3):
    """
    Procesa un archivo GML específico con límites en las búsquedas
    """
    if not os.path.exists(ruta_archivo):
        print(f"❌ Error: No se encuentra el archivo {ruta_archivo}")
        return False
    
    # Cargar árbol enraizado
    arbol, nombre_grafo = cargar_arbol_enraizado(ruta_archivo)
    
    if arbol is None:
        return False
    
    # Extraer configuración del nombre del archivo
    configuracion = extraer_configuracion_archivo(ruta_archivo)
    print(f"🔧 Configuración detectada: {configuracion}")
    print(f"📏 Límites aplicados: BFS={limite_bfs} niveles, DFS={limite_dfs} niveles")
    
    # Encontrar nodo raíz automáticamente
    nodo_raiz = encontrar_nodo_raiz(arbol)
    print(f"🔍 Nodo raíz detectado: {nodo_raiz}")
    
    # Mostrar todos los nodos disponibles
    nodos = list(arbol.nodes())
    print(f"\nNODOS DISPONIBLES: {nodos}")
    
    # Realizar análisis completo
    profundidad_maxima, hojas, nodos_internos = analizar_estructura_arbol(arbol, nodo_raiz)
    
    # Realizar búsquedas limitadas desde la raíz
    print(f"\n🎯 Realizando búsquedas limitadas desde la raíz: {nodo_raiz}")
    orden_bfs, niveles_bfs = busqueda_anchura_limitada(arbol, nodo_raiz, limite_bfs)
    orden_dfs, caminos_dfs = busqueda_profundidad_limitada(arbol, nodo_raiz, limite_dfs)
    
    # Exportar todos los resultados
    print(f"\n💾 Exportando resultados limitados a CSV...")
    
    # Exportar resultados de búsquedas limitadas
    df_bfs, df_dfs, df_caminos, df_resumen = exportar_resultados_busqueda_limitada(
        arbol, configuracion, orden_bfs, orden_dfs, caminos_dfs, limite_bfs, limite_dfs
    )
    
    # Exportar comparación de variables entre BFS y DFS
    df_comunes, df_unicas_bfs, df_unicas_dfs = exportar_variables_comunes(
        configuracion, orden_bfs, orden_dfs
    )
    
    # Resumen final
    print(f"\n" + "=" * 80)
    print(f"RESUMEN EJECUCIÓN LIMITADA COMPLETADA - {configuracion}")
    print("=" * 80)
    print(f"📊 BFS (límite {limite_bfs}): {len(orden_bfs)} nodos visitados")
    print(f"📊 DFS (límite {limite_dfs}): {len(orden_dfs)} nodos visitados")
    print(f"🛣️  Caminos DFS encontrados: {len(caminos_dfs)}")
    print(f"🤝 Variables comunes BFS/DFS: {len(set(orden_bfs).intersection(set(orden_dfs)))}")
    print(f"📁 Archivos CSV generados en: resultados_busqueda_limitada/{configuracion}/")
    print(f"🌳 Raíz del árbol: {nodo_raiz}")
    
    return True

def procesar_todas_configuraciones(profundidad="prof1", limite_bfs=3, limite_dfs=3):
    """
    Procesa todas las configuraciones (B2C, B4C, etc.) con límites específicos
    """
    print("=" * 80)
    print(f"PROCESAMIENTO MASIVO CON LÍMITES")
    print(f"Límite BFS: {limite_bfs} niveles | Límite DFS: {limite_dfs} niveles")
    print("=" * 80)
    
    # Lista de todas las configuraciones a procesar
    configuraciones = ['B2C', 'B4C', 'B8C', 'B16C', 'W2C', 'W4C', 'W8C', 'W16C']
    
    resultados_totales = []
    archivos_procesados = []
    archivos_fallados = []
    
    for config in configuraciones:
        print(f"\n{'#' * 80}")
        print(f"PROCESANDO CONFIGURACIÓN: {config}")
        print(f"{'#' * 80}")
        
        # Construir la ruta del archivo
        ruta_archivo = f"mst_raiz_reducido/arbol_reducido_{config}_{profundidad}.gml"
        
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            print(f"⚠️  Advertencia: No se encuentra {ruta_archivo}")
            print(f"   Intentando formato alternativo...")
            # Intentar formato alternativo
            ruta_alternativa = f"mst_raiz_reducido/arbol_reducido_{config}_directa_target_y_prof{limite_bfs}.gml"
            if os.path.exists(ruta_alternativa):
                ruta_archivo = ruta_alternativa
                print(f"   ✓ Usando archivo alternativo: {ruta_alternativa}")
            else:
                print(f"❌ No se encontró archivo para {config}")
                archivos_fallados.append(config)
                continue
        
        # Procesar el archivo
        exito = procesar_archivo_gml(ruta_archivo, limite_bfs, limite_dfs)
        
        if exito:
            archivos_procesados.append(config)
            resultados_totales.append({
                'configuracion': config,
                'estado': 'ÉXITO',
                'limite_bfs': limite_bfs,
                'limite_dfs': limite_dfs,
                'archivo': ruta_archivo
            })
        else:
            archivos_fallados.append(config)
            resultados_totales.append({
                'configuracion': config,
                'estado': 'FALLÓ',
                'limite_bfs': limite_bfs,
                'limite_dfs': limite_dfs,
                'archivo': ruta_archivo
            })
    
    # Generar resumen global
    generar_resumen_global(resultados_totales, limite_bfs, limite_dfs)
    
    return resultados_totales

def generar_resumen_global(resultados, limite_bfs, limite_dfs):
    """
    Genera un resumen global de todas las configuraciones procesadas
    """
    carpeta_salida = "resultados_busqueda_limitada"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Crear DataFrame con todos los resultados
    df_resumen_global = pd.DataFrame(resultados)
    
    # Agregar estadísticas adicionales
    total_procesados = len([r for r in resultados if r['estado'] == 'ÉXITO'])
    total_fallados = len([r for r in resultados if r['estado'] == 'FALLÓ'])
    
    # Guardar resumen global
    ruta_resumen_global = os.path.join(carpeta_salida, f"resumen_global_limites_bfs{limite_bfs}_dfs{limite_dfs}.csv")
    df_resumen_global.to_csv(ruta_resumen_global, index=False)
    
    print(f"\n{'=' * 80}")
    print("RESUMEN GLOBAL DEL PROCESAMIENTO")
    print(f"{'=' * 80}")
    print(f"✅ Configuraciones procesadas exitosamente: {total_procesados}")
    print(f"❌ Configuraciones falladas: {total_fallados}")
    print(f"📊 Límites aplicados: BFS={limite_bfs}, DFS={limite_dfs}")
    print(f"📁 Resumen global guardado: {ruta_resumen_global}")
    
    # Mostrar lista de configuraciones procesadas
    if total_procesados > 0:
        print(f"\n📋 Configuraciones exitosas:")
        for resultado in resultados:
            if resultado['estado'] == 'ÉXITO':
                print(f"   ✓ {resultado['configuracion']}")
    
    if total_fallados > 0:
        print(f"\n⚠️  Configuraciones falladas:")
        for resultado in resultados:
            if resultado['estado'] == 'FALLÓ':
                print(f"   ✗ {resultado['configuracion']}")

def main():
    """
    Función principal para procesar todas las configuraciones con límites
    """
    print("=" * 80)
    print("BÚSQUEDA EN ANCHURA Y PROFUNDIDAD - CON LÍMITES")
    print("=" * 80)
    
    # CONFIGURACIÓN DE LÍMITES (puedes modificar estos valores)
    LIMITE_BFS = 3  # Niveles máximos para BFS
    LIMITE_DFS = 3  # Niveles máximos para DFS
    PROFUNDIDAD_ARCHIVOS = "prof1"  # Puede ser "prof1", "prof2", "prof3", etc.
    
    print(f"⚙️  Configuración de límites:")
    print(f"   - Límite BFS: {LIMITE_BFS} niveles")
    print(f"   - Límite DFS: {LIMITE_DFS} niveles")
    print(f"   - Profundidad de archivos: {PROFUNDIDAD_ARCHIVOS}")
    
    # Procesar todas las configuraciones
    resultados = procesar_todas_configuraciones(PROFUNDIDAD_ARCHIVOS, LIMITE_BFS, LIMITE_DFS)
    
    print(f"\n{'=' * 80}")
    print("PROCESAMIENTO COMPLETADO")
    print(f"{'=' * 80}")
    print("🎯 Los resultados se han guardado en la carpeta: resultados_busqueda_limitada/")
    print("📁 Cada configuración tiene su propia subcarpeta con:")
    print("   - Resultados BFS limitados")
    print("   - Resultados DFS limitados")
    print("   - Caminos DFS limitados")
    print("   - Variables comunes y únicas")
    print("   - Resumen de la ejecución")

if __name__ == "__main__":
    # Ejecutar procesamiento principal
    main()