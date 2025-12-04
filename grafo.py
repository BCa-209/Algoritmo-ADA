import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
from typing import Dict, List, Tuple

def cargar_matrices_npz(carpeta: str = "resultado_correlacion") -> Dict[str, pd.DataFrame]:
    """
    Carga todas las matrices .npz de una carpeta
    """
    matrices = {}
    
    if not os.path.exists(carpeta):
        print(f"Error: La carpeta '{carpeta}' no existe")
        return matrices
    
    archivos_npz = [f for f in os.listdir(carpeta) if f.endswith('.npz')]
    
    if not archivos_npz:
        print(f"No se encontraron archivos .npz en '{carpeta}'")
        return matrices
    
    print(f"Cargando matrices de '{carpeta}':")
    
    for archivo in archivos_npz:
        try:
            ruta_completa = os.path.join(carpeta, archivo)
            
            # Cargar con allow_pickle=True para arrays de texto
            datos = np.load(ruta_completa, allow_pickle=True)
            
            # Reconstruir DataFrame
            matriz_valores = datos['matriz_valores']
            matriz_columnas = datos['matriz_columnas']
            matriz_indices = datos['matriz_indices']
            
            matriz_df = pd.DataFrame(
                matriz_valores,
                index=matriz_indices,
                columns=matriz_columnas
            )
            
            nombre_sin_ext = archivo.replace('.npz', '')
            matrices[nombre_sin_ext] = matriz_df
            print(f"  Cargado: {archivo} - {matriz_df.shape}")
    
        except Exception as e:
            print(f"  Error cargando {archivo}: {e}")
    
    return matrices

def matriz_a_grafo(matriz: pd.DataFrame, umbral: float = 0.7, 
                   grafo_dirigido: bool = False) -> nx.Graph:
    """
    Convierte una matriz de distancia en un grafo
    """
    if grafo_dirigido:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    
    # Añadir nodos (nombres de las columnas)
    nodos = matriz.columns.tolist()
    G.add_nodes_from(nodos)
    
    # Añadir aristas basadas en la matriz de distancia
    for i, nodo_i in enumerate(nodos):
        for j, nodo_j in enumerate(nodos):
            if i < j:  # Evitar duplicados en grafos no dirigidos
                distancia = matriz.iloc[i, j]
                # Convertir distancia a peso (inverso)
                peso = 1.0 - distancia
                
                # Solo crear arista si supera el umbral de correlación
                if peso >= umbral:
                    G.add_edge(nodo_i, nodo_j, weight=peso, distance=distancia)
    
    return G

def analizar_grafo(G: nx.Graph, nombre: str) -> Dict:
    """
    Analiza las propiedades del grafo
    """
    print(f"\n{'='*50}")
    print(f"ANALISIS DEL GRAFO: {nombre}")
    print(f"{'='*50}")
    
    metricas = {
        'nombre': nombre,
        'n_nodos': G.number_of_nodes(),
        'n_aristas': G.number_of_edges(),
        'densidad': nx.density(G)
    }
    
    print(f"Nodos: {metricas['n_nodos']}")
    print(f"Aristas: {metricas['n_aristas']}")
    print(f"Densidad: {metricas['densidad']:.4f}")
    
    if metricas['n_nodos'] > 0:
        # Grado de los nodos
        grados = dict(G.degree())
        metricas['grado_promedio'] = np.mean(list(grados.values()))
        metricas['grado_max'] = max(grados.values())
        metricas['grado_min'] = min(grados.values())
        
        print(f"Grado promedio: {metricas['grado_promedio']:.2f}")
        print(f"Grado maximo: {metricas['grado_max']}")
        print(f"Grado minimo: {metricas['grado_min']}")
        
        # Centralidad
        if G.number_of_edges() > 0:
            centralidad_grado = nx.degree_centrality(G)
            nodo_mas_central = max(centralidad_grado, key=centralidad_grado.get)
            metricas['nodo_mas_central'] = nodo_mas_central
            metricas['centralidad_max'] = centralidad_grado[nodo_mas_central]
            
            print(f"Nodo mas central: {nodo_mas_central} ({metricas['centralidad_max']:.3f})")
            
            # Componentes conexas
            if not G.is_directed():
                componentes = list(nx.connected_components(G))
                metricas['n_componentes'] = len(componentes)
                metricas['tamano_componente_max'] = max(len(c) for c in componentes)
                print(f"Componentes conexas: {metricas['n_componentes']}")
                print(f"Componente mas grande: {metricas['tamano_componente_max']} nodos")
    
    return metricas

def visualizar_grafo(G: nx.Graph, nombre: str, carpeta_salida: str = "grafos"):
    """
    Visualiza el grafo y guarda la imagen
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    plt.figure(figsize=(12, 8))
    
    # Diseño del grafo - ajustar parámetros para mejor visualización
    pos = nx.spring_layout(G, k=2, iterations=100)
    
    # Obtener pesos para el grosor de las aristas
    if G.number_of_edges() > 0:
        pesos = [G[u][v]['weight'] * 2 + 0.5 for u, v in G.edges()]
    else:
        pesos = [1] * G.number_of_edges()
    
    # Dibujar el grafo
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='lightblue', 
                          alpha=0.9, edgecolors='black', linewidths=1)
    
    if G.number_of_edges() > 0:
        nx.draw_networkx_edges(G, pos, width=pesos, alpha=0.7, edge_color='gray')
    
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Añadir etiquetas de peso en las aristas si no son demasiadas
    if G.number_of_edges() <= 30:
        etiquetas_aristas = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_aristas, font_size=8)
    
    plt.title(f"Grafo: {nombre}\n(Nodos: {G.number_of_nodes()}, Aristas: {G.number_of_edges()})")
    plt.axis('off')
    plt.tight_layout()
    
    # Guardar imagen
    ruta_imagen = os.path.join(carpeta_salida, f"grafo_{nombre}.png")
    plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Imagen guardada: {ruta_imagen}")

def exportar_grafos_gml(grafos: Dict[str, nx.Graph], carpeta: str = "grafos"):
    """
    Exporta grafos a formato GML para Gephi, Cytoscape u otras herramientas
    """
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    for nombre, G in grafos.items():
        ruta_gml = os.path.join(carpeta, f"grafo_{nombre}.gml")
        nx.write_gml(G, ruta_gml)
        print(f"Grafo exportado (GML): {ruta_gml}")

def exportar_metricas_gml(grafos: Dict[str, nx.Graph], todas_metricas: List[Dict], carpeta: str = "grafos"):
    """
    Exporta métricas de los grafos en archivos GML con atributos adicionales
    """
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    for nombre, G in grafos.items():
        # Encontrar las métricas correspondientes a este grafo
        metricas_grafo = next((m for m in todas_metricas if m['nombre'] == nombre), {})
        
        # Añadir métricas globales como atributos del grafo
        for key, value in metricas_grafo.items():
            if key != 'nombre':
                G.graph[key] = value
        
        # Guardar el grafo con métricas incluidas
        ruta_gml = os.path.join(carpeta, f"grafo_con_metricas_{nombre}.gml")
        nx.write_gml(G, ruta_gml)
        print(f"Grafo con métricas exportado (GML): {ruta_gml}")

def comparar_grafos(grafos: Dict[str, nx.Graph]):
    """
    Compara múltiples grafos y genera reporte
    """
    print(f"\n{'='*60}")
    print("COMPARACION DE GRAFOS")
    print(f"{'='*60}")
    
    comparacion = []
    
    for nombre, G in grafos.items():
        if G.number_of_nodes() > 0:
            grado_promedio = np.mean([d for n, d in G.degree()])
        else:
            grado_promedio = 0
            
        metricas = {
            'Grafo': nombre,
            'Nodos': G.number_of_nodes(),
            'Aristas': G.number_of_edges(),
            'Densidad': f"{nx.density(G):.4f}",
            'Grado Promedio': f"{grado_promedio:.2f}"
        }
        comparacion.append(metricas)
    
    df_comparacion = pd.DataFrame(comparacion)
    print(df_comparacion.to_string(index=False))

def main():
    """
    Función principal - ejecuta todo el pipeline
    """
    print("=" * 70)
    print("CONVERSION DE MATRICES A GRAFOS")
    print("=" * 70)
    
    # CONFIGURACION - MODIFICA AQUI
    UMBRAL_CORRELACION = 0.7 # Solo conexiones con correlación >= 0.7
    GRAFOS_A_CREAR = []  # Lista vacía = procesar todas las matrices
    
    # Cargar matrices
    matrices = cargar_matrices_npz()
    
    if not matrices:
        print("No hay matrices para procesar")
        print("Ejecuta primero: correlacion.py")
        return
    
    print(f"\nMatrices cargadas: {list(matrices.keys())}")
    
    # Crear grafos
    grafos = {} 
    todas_metricas = []
    
    for nombre_matriz, matriz in matrices.items():
        # Filtrar por GRAFOS_A_CREAR si se especificó
        if GRAFOS_A_CREAR and nombre_matriz not in GRAFOS_A_CREAR:
            continue
            
        print(f"\nCreando grafo para: {nombre_matriz}")
        
        # Crear grafo
        G = matriz_a_grafo(matriz, umbral=UMBRAL_CORRELACION, grafo_dirigido=False)
        
        # Analizar grafo
        metricas = analizar_grafo(G, nombre_matriz)
        grafos[nombre_matriz] = G
        todas_metricas.append(metricas)
        
        # Visualizar grafo
        visualizar_grafo(G, nombre_matriz)
    
    # Guardar grafos en formato GML
    if grafos:
        carpeta_grafos = "grafos"
        
        # Exportar grafos básicos
        exportar_grafos_gml(grafos, carpeta_grafos)
        
        # Exportar grafos con métricas incluidas
        exportar_metricas_gml(grafos, todas_metricas, carpeta_grafos)
        
        print(f"\nTodos los grafos han sido exportados en formato GML en la carpeta '{carpeta_grafos}'")
    
    # Comparar grafos si hay más de uno
    if len(grafos) > 1:
        comparar_grafos(grafos)
    
    print(f"\n{'='*70}")
    print("PROCESO COMPLETADO")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()