# mst_camino_largo_objetivo.py
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import deque

# CONFIGURACIÓN DE VARIABLE OBJETIVO
VARIABLE_OBJETIVO = "target_y"  # ← MODIFICA AQUÍ la variable objetivo

def cargar_mst_desde_gml(ruta_archivo):
    """
    Carga el MST desde archivo GML
    """
    try:
        grafo = nx.read_gml(ruta_archivo)
        nombre_grafo = os.path.basename(ruta_archivo).replace('mst_', '').replace('.gml', '')
        
        print(f"Grafo cargado: {nombre_grafo}")
        print(f"  Nodos: {grafo.number_of_nodes()}")
        print(f"  Aristas: {grafo.number_of_edges()}")
        
        return grafo, nombre_grafo
    except Exception as e:
        print(f"Error cargando {ruta_archivo}: {e}")
        return None, None

def encontrar_camino_mas_largo_topologico(grafo):
    """
    Encuentra el camino más largo considerando distancia topológica (cada arista = 1)
    """
    print(f"\n" + "="*60)
    print(f"BUSCANDO CAMINO TOPOLÓGICO MÁS LARGO")
    print("="*60)
    
    # Crear grafo no dirigido para cálculo de distancias
    grafo_no_dirigido = grafo.to_undirected()
    
    # Encontrar todos los pares de hojas
    hojas = [nodo for nodo in grafo_no_dirigido.nodes() if grafo_no_dirigido.degree(nodo) == 1]
    
    if len(hojas) < 2:
        print("No hay suficientes hojas para encontrar un camino largo")
        return None, 0, None
    
    camino_mas_largo = []
    longitud_maxima = -1
    mejor_par = (None, None)
    
    # Probar todos los pares de hojas usando BFS para distancia topológica
    for i in range(len(hojas)):
        for j in range(i + 1, len(hojas)):
            hoja1, hoja2 = hojas[i], hojas[j]
            try:
                # Usar BFS para encontrar el camino más corto (distancia topológica)
                camino = nx.shortest_path(grafo_no_dirigido, hoja1, hoja2)
                longitud = len(camino) - 1  # Número de aristas (distancia topológica)
                
                if longitud > longitud_maxima:
                    longitud_maxima = longitud
                    camino_mas_largo = camino
                    mejor_par = (hoja1, hoja2)
                    
            except nx.NetworkXNoPath:
                continue
    
    if not camino_mas_largo:
        print("No se encontró ningún camino entre hojas")
        return None, 0, None
    
    print(f" Camino topológico más largo encontrado:")
    print(f"   Desde: {mejor_par[0]} → Hasta: {mejor_par[1]}")
    print(f"   Camino: {' → '.join(camino_mas_largo)}")
    print(f"   Longitud topológica: {longitud_maxima} aristas")
    print(f"   Nodos: {len(camino_mas_largo)} nodos")
    
    return camino_mas_largo, longitud_maxima, mejor_par

def obtener_aristas_del_camino(grafo, camino):
    """
    Obtiene las aristas del camino con sus pesos
    """
    aristas = []
    for i in range(len(camino) - 1):
        u, v = camino[i], camino[i+1]
        peso = grafo[u][v]['weight']
        distancia = grafo[u][v].get('distance', 0)
        aristas.append({
            'desde': u,
            'hacia': v,
            'peso': peso,
            'distancia': distancia,
            'indice': i
        })
    
    return aristas

def dividir_grafo_eliminando_arista_media(grafo, camino_mas_largo, num_aristas):
    """
    Divide el grafo eliminando la arista del medio
    CORRECCIÓN: Si es PAR, se suma 1 y se elimina la del medio
    """
    print(f"\n" + "="*60)
    print(f"DIVIDIENDO GRAFO - {num_aristas} ARISTAS TOPOLÓGICAS")
    print("="*60)
    
    aristas_camino = obtener_aristas_del_camino(grafo, camino_mas_largo)
    
    # CORRECCIÓN APLICADA: Si es PAR, se suma 1 para encontrar la posición media
    if num_aristas % 2 == 0:  # PAR - sumar 1 y tomar la del medio
        posicion_media = (num_aristas + 1) // 2
        print(f" Número PAR de aristas topológicas ({num_aristas})")
        print(f"    Se suma 1: {num_aristas} + 1 = {num_aristas + 1}")
        print(f"    Posición media calculada: {posicion_media}")
        
    else:  # IMPAR - tomar directamente la del medio
        posicion_media = num_aristas // 2
        print(f" Número IMPAR de aristas topológicas ({num_aristas})")
        print(f"    Posición media: {posicion_media}")
    
    aristas_a_eliminar = [posicion_media]
    
    # Mostrar información de la arista a eliminar
    print(f"\n  ARISTA A ELIMINAR (posición {posicion_media}):")
    arista = aristas_camino[posicion_media]
    print(f"   {arista['desde']} ↔ {arista['hacia']}")
    print(f"   Peso: {arista['peso']:.4f}")
    print(f"   Distancia: {arista['distancia']:.4f}")
    
    # Crear copia del grafo original
    grafo_dividido = grafo.copy()
    
    # Eliminar arista del grafo
    u, v = arista['desde'], arista['hacia']
    
    if grafo_dividido.has_edge(u, v):
        grafo_dividido.remove_edge(u, v)
    
    # Obtener componentes conexas después de eliminar la arista
    componentes = list(nx.connected_components(grafo_dividido))
    
    return componentes, aristas_a_eliminar, u, v, grafo_dividido

def seleccionar_arbol_con_variable_objetivo(componentes, variable_objetivo, grafo_original):
    """
    Selecciona el árbol que contiene la variable objetivo
    """
    print(f"\n" + "="*60)
    print(f"SELECCIONANDO ÁRBOL CON VARIABLE OBJETIVO: {variable_objetivo}")
    print("="*60)
    
    arbol_objetivo = None
    otros_arboles = []
    
    for i, componente in enumerate(componentes, 1):
        subgrafo = nx.subgraph(grafo_original, componente)
        
        print(f" Componente {i}: {len(componente)} nodos")
        print(f"   Nodos: {list(componente)}")
        
        if variable_objetivo in componente:
            print(f"    CONTIENE la variable objetivo '{variable_objetivo}'")
            arbol_objetivo = componente
        else:
            print(f"    NO contiene la variable objetivo")
            otros_arboles.append(componente)
    
    if arbol_objetivo is None:
        print(f" ERROR: La variable objetivo '{variable_objetivo}' no se encuentra en ninguna componente")
        return None, otros_arboles
    
    print(f"\n ÁRBOL SELECCIONADO:")
    print(f"   Nodos: {len(arbol_objetivo)} → {list(arbol_objetivo)}")
    
    return arbol_objetivo, otros_arboles

def analizar_componentes_conexas(componentes, variable_objetivo):
    """
    Analiza las componentes conexas después de la división
    """
    print(f"\n🔍 ANÁLISIS DE COMPONENTES CONEXAS:")
    print(f"   Total de componentes: {len(componentes)}")
    
    for i, componente in enumerate(componentes, 1):
        tamaño = len(componente)
        contiene_objetivo = variable_objetivo in componente
        estado = " OBJETIVO" if contiene_objetivo else "➖ OTRO"
        
        print(f"   Componente {i} ({estado}): {tamaño} nodos")
        print(f"     Nodos: {list(componente)}")
    
    return componentes

def visualizar_division_y_seleccion(grafo_original, camino_mas_largo, componentes, 
                                  arbol_objetivo, aristas_eliminadas, nombre_grafo, grafo_dividido):
    """
    Visualiza el proceso de división y selección
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # Layout consistente
    pos = nx.spring_layout(grafo_original, k=1, iterations=50, seed=42)
    
    # 1. Grafo original con camino más largo resaltado
    nx.draw_networkx_nodes(grafo_original, pos, ax=ax1, node_size=500, 
                          node_color='lightblue', alpha=0.7)
    nx.draw_networkx_edges(grafo_original, pos, ax=ax1, alpha=0.3, 
                          edge_color='gray', width=1)
    
    # Resaltar camino más largo
    if len(camino_mas_largo) > 1:
        edges_camino = [(camino_mas_largo[i], camino_mas_largo[i+1]) 
                       for i in range(len(camino_mas_largo)-1)]
        nx.draw_networkx_edges(grafo_original, pos, edgelist=edges_camino, 
                              ax=ax1, edge_color='red', width=3, alpha=0.8)
    
    # Marcar arista eliminada
    aristas_camino = obtener_aristas_del_camino(grafo_original, camino_mas_largo)
    if aristas_eliminadas:
        arista_eliminada = aristas_camino[aristas_eliminadas[0]]
        u, v = arista_eliminada['desde'], arista_eliminada['hacia']
        nx.draw_networkx_edges(grafo_original, pos, edgelist=[(u, v)], 
                              ax=ax1, edge_color='black', width=4, alpha=0.8, 
                              style='dashed')
    
    nx.draw_networkx_labels(grafo_original, pos, ax=ax1, font_size=8)
    ax1.set_title(f'Grafo Original - Camino Topológico Más Largo\n'
                 f'Longitud: {len(camino_mas_largo)-1} aristas | '
                 f'Arista eliminada: {u}↔{v}', fontsize=12)
    
    # 2. Componentes después de división
    colores = plt.get_cmap('Set1')(np.linspace(0, 1, len(componentes)))
    
    for i, componente in enumerate(componentes):
        color = colores[i]
        es_objetivo = componente == arbol_objetivo
        node_color = [color] if not es_objetivo else ['gold']
        node_size = 500 if not es_objetivo else 700
        
        nx.draw_networkx_nodes(grafo_original, pos, nodelist=list(componente), 
                              ax=ax2, node_size=node_size, node_color=node_color, 
                              alpha=0.8, edgecolors='black' if es_objetivo else None)
    
    # Dibujar todas las aristas que permanecen
    nx.draw_networkx_edges(grafo_dividido, pos, ax=ax2, alpha=0.6, width=1.5)
    nx.draw_networkx_labels(grafo_original, pos, ax=ax2, font_size=8)
    ax2.set_title(f'Componentes después de División\n'
                 f'Total: {len(componentes)} componentes', fontsize=12)
    
    # 3. Árbol objetivo resaltado
    if arbol_objetivo:
        # Nodos del árbol objetivo en dorado
        nx.draw_networkx_nodes(grafo_original, pos, nodelist=list(arbol_objetivo), 
                              ax=ax3, node_size=600, node_color='gold', 
                              alpha=0.9, edgecolors='darkorange', linewidths=2)
        
        # Resaltar variable objetivo
        if VARIABLE_OBJETIVO in arbol_objetivo:
            nx.draw_networkx_nodes(grafo_original, pos, nodelist=[VARIABLE_OBJETIVO], 
                                  ax=ax3, node_size=800, node_color='red', 
                                  alpha=1.0, edgecolors='darkred', linewidths=3)
        
        # Aristas del árbol objetivo
        subgrafo_objetivo = grafo_dividido.subgraph(arbol_objetivo)
        nx.draw_networkx_edges(subgrafo_objetivo, pos, ax=ax3, 
                              edge_color='orange', width=2.5, alpha=0.8)
        
        nx.draw_networkx_labels(grafo_original, pos, ax=ax3, font_size=8)
        ax3.set_title(f'Árbol Seleccionado (contiene {VARIABLE_OBJETIVO})\n'
                     f'{len(arbol_objetivo)} nodos', fontsize=12)
    
    # 4. Información de la selección
    ax4.axis('off')
    info_text = f"INFORMACIÓN DE SELECCIÓN:\n\n"
    info_text += f"Variable objetivo: {VARIABLE_OBJETIVO}\n\n"
    info_text += f"Camino topológico más largo:\n"
    info_text += f"{' → '.join(camino_mas_largo)}\n\n"
    info_text += f"Longitud: {len(camino_mas_largo)-1} aristas\n"
    
    # Mostrar lógica de división
    num_aristas = len(camino_mas_largo) - 1
    if num_aristas % 2 == 0:
        info_text += f"Lógica: PAR → {num_aristas} + 1\n"
    else:
        info_text += f"Lógica: IMPAR\n"
    
    info_text += f"Arista eliminada: {u}↔{v}\n\n"
    info_text += f"RESULTADO:\n"
    info_text += f"Componentes totales: {len(componentes)}\n"
    if arbol_objetivo:
        info_text += f"Árbol seleccionado: {len(arbol_objetivo)} nodos\n"
        info_text += f"Nodos: {', '.join(list(arbol_objetivo))}"
    
    ax4.text(0.1, 0.9, info_text, transform=ax4.transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                                             facecolor="lightyellow", alpha=0.8))
    
    for ax in [ax1, ax2, ax3]:
        ax.axis('off')
    
    plt.tight_layout()
    
    # Guardar imagen
    carpeta_salida = "arbol_objetivo_resultados"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    ruta_imagen = os.path.join(carpeta_salida, f"arbol_objetivo_{nombre_grafo}.png")
    plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Visualización guardada: {ruta_imagen}")

def exportar_arbol_objetivo(arbol_objetivo, grafo_original, nombre_grafo, aristas_eliminadas):
    """
    Exporta el árbol objetivo en formato GML y CSV
    """
    carpeta_salida = "arbol_objetivo_resultados"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Crear subgrafo del árbol objetivo
    arbol_objetivo_grafo = grafo_original.subgraph(arbol_objetivo)
    
    # Exportar GML
    ruta_gml = os.path.join(carpeta_salida, f"arbol_objetivo_{nombre_grafo}.gml")
    nx.write_gml(arbol_objetivo_grafo, ruta_gml)
    
    print(f"Árbol objetivo guardado: {ruta_gml}")
    
    # Exportar CSV con información
    info_arbol = {
        'nombre_grafo': [nombre_grafo],
        'variable_objetivo': [VARIABLE_OBJETIVO],
        'aristas_eliminadas': [str(aristas_eliminadas)],
        'arbol_nodos': [arbol_objetivo_grafo.number_of_nodes()],
        'arbol_aristas': [arbol_objetivo_grafo.number_of_edges()],
        'nodos_arbol': [', '.join(arbol_objetivo)],
        'metodo': ['distancia_topologica']
    }
    
    df_info = pd.DataFrame(info_arbol)
    ruta_csv = os.path.join(carpeta_salida, f"info_arbol_objetivo_{nombre_grafo}.csv")
    df_info.to_csv(ruta_csv, index=False)
    
    print(f"Información del árbol guardada: {ruta_csv}")
    
    return ruta_gml, ruta_csv

def main():
    """
    Función principal - Versión con variable objetivo
    """
    print("=" * 70)
    print("SELECCIÓN DE ÁRBOL POR VARIABLE OBJETIVO")
    print("=" * 70)
    print(f"VARIABLE OBJETIVO: {VARIABLE_OBJETIVO}")
    print("Método: Distancia topológica más larga")
    print("=" * 70)
    
    # CONFIGURACIÓN
    CARPETA_MST = "mst_resultados"
    MST = "W16C"
    ARCHIVO_MST = f"mst_{MST}_directa.gml"  # Modifica según necesites
    
    ruta_mst = os.path.join(CARPETA_MST, ARCHIVO_MST)
    
    if not os.path.exists(ruta_mst):
        print(f"Error: No se encuentra el archivo {ruta_mst}")
        print("Archivos disponibles en mst_resultados/:")
        if os.path.exists(CARPETA_MST):
            for archivo in os.listdir(CARPETA_MST):
                if archivo.endswith('.gml'):
                    print(f"  - {archivo}")
        return
    
    # Cargar MST
    grafo, nombre_grafo = cargar_mst_desde_gml(ruta_mst)
    
    if grafo is None:
        return
    
    # Verificar que la variable objetivo existe en el grafo
    if VARIABLE_OBJETIVO not in grafo.nodes():
        print(f" ERROR: La variable objetivo '{VARIABLE_OBJETIVO}' no existe en el grafo")
        print(f"Nodos disponibles: {list(grafo.nodes())}")
        return
    
    # Encontrar camino topológico más largo
    print(f"\n BUSCANDO CAMINO TOPOLÓGICO MÁS LARGO...")
    camino_mas_largo, num_aristas, mejor_par = encontrar_camino_mas_largo_topologico(grafo)
    
    if camino_mas_largo is None:
        print("No se pudo encontrar un camino válido para dividir el grafo")
        return
    
    # Dividir grafo según la corrección
    componentes, aristas_eliminadas, u, v, grafo_dividido = dividir_grafo_eliminando_arista_media(
        grafo, camino_mas_largo, num_aristas
    )
    
    # Seleccionar árbol que contiene la variable objetivo
    arbol_objetivo, otros_arboles = seleccionar_arbol_con_variable_objetivo(componentes, VARIABLE_OBJETIVO, grafo)
    
    if arbol_objetivo is None:
        return
    
    # Analizar componentes resultantes
    analizar_componentes_conexas(componentes, VARIABLE_OBJETIVO)
    
    # Visualizar resultados
    visualizar_division_y_seleccion(grafo, camino_mas_largo, componentes, 
                                  arbol_objetivo, aristas_eliminadas, nombre_grafo, grafo_dividido)
    
    # Exportar árbol objetivo
    exportar_arbol_objetivo(arbol_objetivo, grafo, nombre_grafo, aristas_eliminadas)
    
    print(f"\n" + "=" * 70)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print(f" Camino topológico más largo encontrado")
    print(f" Grafo dividido en {len(componentes)} componentes")
    print(f" Árbol seleccionado que contiene '{VARIABLE_OBJETIVO}'")
    print(f" Árbol con {len(arbol_objetivo)} nodos")
    print(f" Archivos guardados en: arbol_objetivo_resultados/")

if __name__ == "__main__":
    main()