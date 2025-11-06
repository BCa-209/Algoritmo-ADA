# busqueda_arbol.py
import pandas as pd
import networkx as nx
import os
from datetime import datetime

def cargar_arbol_enraizado(ruta_archivo):
    """
    Carga el árbol enraizado desde archivo GML
    """
    try:
        arbol = nx.read_gml(ruta_archivo)
        nombre_archivo = os.path.basename(ruta_archivo)
        nombre_grafo = nombre_archivo.replace('arbol_enraizado_', '').replace('.gml', '')
        
        print(f"Árbol enraizado cargado: {nombre_grafo}")
        print(f"  Nodos: {arbol.number_of_nodes()}")
        print(f"  Aristas: {arbol.number_of_edges()}")
        
        return arbol, nombre_grafo
    except Exception as e:
        print(f"Error cargando {ruta_archivo}: {e}")
        return None, None

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

def busqueda_anchura(arbol, nodo_inicio):
    """
    Realiza búsqueda en anchura (BFS) desde el nodo inicial
    """
    print(f"\n" + "="*50)
    print(f"BÚSQUEDA EN ANCHURA (BFS) - Desde: {nodo_inicio}")
    print("="*50)
    
    visitados = set()
    cola = [nodo_inicio]
    orden_bfs = []
    niveles = {}
    
    nivel_actual = 0
    nodos_por_nivel = {nivel_actual: [nodo_inicio]}
    
    while cola:
        nivel_actual += 1
        siguiente_nivel = []
        
        for nodo_actual in cola:
            if nodo_actual not in visitados:
                visitados.add(nodo_actual)
                orden_bfs.append(nodo_actual)
                
                # Obtener sucesores (hijos) del nodo actual
                sucesores = list(arbol.successors(nodo_actual))
                siguiente_nivel.extend(sucesores)
                
                if sucesores:
                    nodos_por_nivel[nivel_actual] = nodos_por_nivel.get(nivel_actual, []) + sucesores
        
        cola = siguiente_nivel
    
    # Mostrar resultados
    print(f"Orden de visita BFS: {' → '.join(orden_bfs)}")
    print(f"Total de nodos visitados: {len(orden_bfs)}")
    
    print(f"\nEstructura por niveles:")
    for nivel, nodos in nodos_por_nivel.items():
        if nodos:  # Solo mostrar niveles con nodos
            print(f"  Nivel {nivel}: {nodos}")
    
    return orden_bfs, nodos_por_nivel

def busqueda_profundidad(arbol, nodo_inicio):
    """
    Realiza búsqueda en profundidad (DFS) desde el nodo inicial
    """
    print(f"\n" + "="*50)
    print(f"BÚSQUEDA EN PROFUNDIDAD (DFS) - Desde: {nodo_inicio}")
    print("="*50)
    
    visitados = set()
    orden_dfs = []
    caminos_completos = []
    
    def dfs_recursivo(nodo_actual, camino_actual):
        if nodo_actual not in visitados:
            visitados.add(nodo_actual)
            camino_actual.append(nodo_actual)
            orden_dfs.append(nodo_actual)
            
            # Obtener sucesores (hijos)
            sucesores = list(arbol.successors(nodo_actual))
            
            if not sucesores:  # Es una hoja
                caminos_completos.append(camino_actual.copy())
                print(f"  Camino completo: {' → '.join(camino_actual)}")
            else:
                for sucesor in sucesores:
                    dfs_recursivo(sucesor, camino_actual.copy())
    
    dfs_recursivo(nodo_inicio, [])
    
    # Mostrar resultados
    print(f"\nOrden de visita DFS: {' → '.join(orden_dfs)}")
    print(f"Total de nodos visitados: {len(orden_dfs)}")
    print(f"Caminos completos encontrados: {len(caminos_completos)}")
    
    return orden_dfs, caminos_completos

def busqueda_anchura_iterativa(arbol, nodo_inicio, objetivo):
    """
    Búsqueda en anchura iterativa para encontrar camino a un nodo específico
    """
    print(f"\n" + "="*50)
    print(f"BÚSQUEDA DE CAMINO HACIA: {objetivo}")
    print("="*50)
    
    if objetivo not in arbol.nodes():
        print(f"❌ El nodo '{objetivo}' no existe en el árbol")
        return None
    
    if nodo_inicio == objetivo:
        print(f"✅ El nodo objetivo es el mismo que el inicio: {nodo_inicio}")
        return [nodo_inicio]
    
    # BFS para encontrar el camino más corto
    cola = [(nodo_inicio, [nodo_inicio])]  # (nodo_actual, camino)
    visitados = set([nodo_inicio])
    
    while cola:
        nodo_actual, camino = cola.pop(0)
        
        for sucesor in arbol.successors(nodo_actual):
            if sucesor == objetivo:
                camino_completo = camino + [sucesor]
                print(f"✅ Camino encontrado: {' → '.join(camino_completo)}")
                print(f"   Longitud del camino: {len(camino_completo) - 1} saltos")
                return camino_completo
            
            if sucesor not in visitados:
                visitados.add(sucesor)
                cola.append((sucesor, camino + [sucesor]))
    
    print(f"❌ No se encontró camino desde {nodo_inicio} a {objetivo}")
    return None

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

def exportar_resultados_busqueda(arbol, nombre_grafo, orden_bfs, orden_dfs, caminos_dfs, carpeta_salida="resultados_busqueda"):
    """
    Exporta los resultados de las búsquedas a archivos CSV
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Exportar resultados BFS
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
    ruta_bfs = os.path.join(carpeta_salida, f"bfs_{nombre_grafo}_{timestamp}.csv")
    df_bfs.to_csv(ruta_bfs, index=False)
    print(f"Resultados BFS guardados: {ruta_bfs}")
    
    # Exportar resultados DFS
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
    ruta_dfs = os.path.join(carpeta_salida, f"dfs_{nombre_grafo}_{timestamp}.csv")
    df_dfs.to_csv(ruta_dfs, index=False)
    print(f"Resultados DFS guardados: {ruta_dfs}")
    
    # Exportar caminos DFS completos
    datos_caminos = []
    for i, camino in enumerate(caminos_dfs, 1):
        datos_caminos.append({
            'camino_id': i,
            'camino': ' → '.join(camino),
            'longitud': len(camino) - 1,
            'nodo_inicio': camino[0],
            'nodo_fin': camino[-1],
            'es_camino_maximo': len(camino) == len(max(caminos_dfs, key=len))
        })
    
    df_caminos = pd.DataFrame(datos_caminos)
    ruta_caminos = os.path.join(carpeta_salida, f"caminos_dfs_{nombre_grafo}_{timestamp}.csv")
    df_caminos.to_csv(ruta_caminos, index=False)
    print(f"Caminos DFS guardados: {ruta_caminos}")
    
    return df_bfs, df_dfs, df_caminos

def mostrar_menu_nodos(arbol):
    """
    Muestra menú para seleccionar nodos de inicio y objetivo
    """
    nodos = list(arbol.nodes())
    
    print(f"\nNODOS DISPONIBLES:")
    print("-" * 40)
    for i, nodo in enumerate(nodos, 1):
        grado_entrada = arbol.in_degree(nodo)
        grado_salida = arbol.out_degree(nodo)
        tipo = "RAÍZ" if grado_entrada == 0 else "HOJA" if grado_salida == 0 else "INTERNO"
        print(f"{i:2d}. {nodo:10} ({tipo}) - Entrada: {grado_entrada}, Salida: {grado_salida}")
    
    return nodos

def seleccionar_nodo(nodos, mensaje):
    """
    Permite seleccionar un nodo de la lista
    """
    while True:
        try:
            print(f"\n{mensaje}")
            opcion = input("Ingresa el número del nodo o el nombre: ").strip()
            
            if opcion.isdigit():
                indice = int(opcion) - 1
                if 0 <= indice < len(nodos):
                    return nodos[indice]
                else:
                    print("❌ Número fuera de rango. Intenta nuevamente.")
            else:
                # Buscar por nombre
                opcion_lower = opcion.lower()
                coincidencias = [n for n in nodos if opcion_lower == n.lower()]
                if len(coincidencias) == 1:
                    return coincidencias[0]
                elif len(coincidencias) > 1:
                    print("❌ Múltiples coincidencias. Por favor usa el número:")
                    for i, n in enumerate(coincidencias, 1):
                        print(f"  {i}. {n}")
                else:
                    print("❌ Nodo no encontrado. Intenta nuevamente.")
                    
        except KeyboardInterrupt:
            print("\n👋 Ejecución interrumpida por el usuario.")
            exit()
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """
    Función principal
    """
    print("=" * 70)
    print("BÚSQUEDA EN ANCHURA Y PROFUNDIDAD - ÁRBOL ENRAIZADO")
    print("=" * 70)
    
    # CONFIGURACIÓN
    CARPETA_ARBOL = "mst_enraizado"
    ARCHIVO_ARBOL = "arbol_enraizado_B2C_mixto_x10.gml"  # Modifica según tu archivo
    
    ruta_arbol = os.path.join(CARPETA_ARBOL, ARCHIVO_ARBOL)
    
    if not os.path.exists(ruta_arbol):
        print(f"❌ Error: No se encuentra el archivo {ruta_arbol}")
        print("Archivos disponibles en mst_enraizado/:")
        if os.path.exists(CARPETA_ARBOL):
            archivos = [f for f in os.listdir(CARPETA_ARBOL) if f.endswith('.gml')]
            for archivo in archivos:
                print(f"  - {archivo}")
        return
    
    # Cargar árbol enraizado
    arbol, nombre_grafo = cargar_arbol_enraizado(ruta_arbol)
    
    if arbol is None:
        return
    
    # Encontrar nodo raíz automáticamente
    nodo_raiz = encontrar_nodo_raiz(arbol)
    print(f"🔍 Nodo raíz detectado: {nodo_raiz}")
    
    # Mostrar menú de nodos
    nodos = mostrar_menu_nodos(arbol)
    
    # Seleccionar nodo de inicio
    nodo_inicio = seleccionar_nodo(nodos, "Selecciona el nodo de INICIO para las búsquedas:")
    
    # Seleccionar nodo objetivo (opcional)
    nodo_objetivo = seleccionar_nodo(nodos, "Selecciona el nodo OBJETIVO para búsqueda específica (opcional):")
    
    # Realizar análisis completo
    profundidad_maxima, hojas, nodos_internos = analizar_estructura_arbol(arbol, nodo_raiz)
    
    # Realizar búsquedas
    orden_bfs, niveles_bfs = busqueda_anchura(arbol, nodo_inicio)
    orden_dfs, caminos_dfs = busqueda_profundidad(arbol, nodo_inicio)
    
    # Búsqueda de camino específico si se seleccionó un objetivo diferente al inicio
    if nodo_objetivo != nodo_inicio:
        camino_objetivo = busqueda_anchura_iterativa(arbol, nodo_inicio, nodo_objetivo)
    
    # Exportar resultados
    df_bfs, df_dfs, df_caminos = exportar_resultados_busqueda(
        arbol, nombre_grafo, orden_bfs, orden_dfs, caminos_dfs
    )
    
    # Resumen final
    print(f"\n" + "=" * 70)
    print("RESUMEN EJECUCIÓN COMPLETADA")
    print("=" * 70)
    print(f"📊 BFS: {len(orden_bfs)} nodos visitados")
    print(f"📊 DFS: {len(orden_dfs)} nodos visitados")
    print(f"🛣️  Caminos DFS encontrados: {len(caminos_dfs)}")
    print(f"📁 Resultados guardados en: resultados_busqueda/")
    print(f"🌳 Raíz del árbol: {nodo_raiz}")
    print(f"🎯 Nodo de inicio: {nodo_inicio}")
    if nodo_objetivo != nodo_inicio:
        print(f"🎯 Nodo objetivo: {nodo_objetivo}")

if __name__ == "__main__":
    main()