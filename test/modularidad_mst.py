import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram

def cargar_grafo_desde_gml(ruta_archivo):
    """
    Carga un grafo desde un archivo GML.
    """
    try:
        G = nx.read_gml(ruta_archivo)
        print(f"Grafo cargado desde GML: {ruta_archivo}")
        print(f"Nodos: {G.number_of_nodes()}")
        print(f"Aristas: {G.number_of_edges()}")
        return G
    except Exception as e:
        print(f"Error cargando el archivo GML: {e}")
        return None

def modularidad_optimizada(G, comunidades):
    """
    Versión optimizada del cálculo de modularidad.
    """
    m = G.number_of_edges()
    if m == 0:
        return 0.0
    
    Q = 0.0
    grados = dict(G.degree())
    
    # Agrupar por comunidades
    comunidades_nodos = defaultdict(list)
    for nodo, comunidad in comunidades.items():
        comunidades_nodos[comunidad].append(nodo)
    
    for comunidad, nodos in comunidades_nodos.items():
        suma_grados = sum(grados[nodo] for nodo in nodos)
        aristas_internas = 0
        for i in nodos:
            for j in nodos:
                if i < j and G.has_edge(i, j):  # Evitar contar dos veces
                    aristas_internas += 1
        Q += (aristas_internas / m) - (suma_grados / (2 * m)) ** 2
    
    return Q

def detectar_comunidades_greedy(G):
    """
    Algoritmo greedy para detección de comunidades basado en modularidad.
    """
    print("Iniciando detección de comunidades...")

    # Paso 1: Inicializar comunidades (cada nodo en su propia comunidad)
    comunidades = {nodo: i for i, nodo in enumerate(G.nodes())}
    
    # Calcular modularidad inicial
    mod_inicial = modularidad_optimizada(G, comunidades)
    print(f"Modularidad inicial: {mod_inicial:.6f}")
    
    # Paso 2: Iterar hasta que no haya mejora
    iteracion = 0
    mejora = True
    historial_modularidad = [mod_inicial]
    
    while mejora and iteracion < 50:  # Límite de iteraciones por seguridad
        iteracion += 1
        print(f"\n--- Iteración {iteracion} ---")
        
        # Mejorar comunidades
        comunidades, mejora = mejorar_comunidades(G, comunidades)
        mod_actual = modularidad_optimizada(G, comunidades)
        historial_modularidad.append(mod_actual)
        
        print(f"Modularidad actual: {mod_actual:.6f}")
        
        if not mejora:
            print("No hay más mejoras posibles.")
    
    # Paso 3: Consolidar comunidades (renumerar)
    comunidades_unicas = sorted(set(comunidades.values()))
    mapping = {com_old: i for i, com_old in enumerate(comunidades_unicas)}
    comunidades_final = {nodo: mapping[com] for nodo, com in comunidades.items()}
    
    mod_final = modularidad_optimizada(G, comunidades_final)
    print(f"\nModularidad final: {mod_final:.6f}")
    
    return comunidades_final, historial_modularidad

def mejorar_comunidades(G, comunidades):
    """
    Mejora las comunidades moviendo nodos individualmente.
    """
    mejora = False
    nodos = list(G.nodes())
    modularidad_actual = modularidad_optimizada(G, comunidades)

    for nodo in nodos:
        comunidad_actual = comunidades[nodo]
        mejor_comunidad = comunidad_actual
        mejor_modularidad = modularidad_actual

        # Explorar comunidades de vecinos y comunidades existentes
        comunidades_vecinas = set(comunidades[vecino] for vecino in G.neighbors(nodo))
        todas_comunidades = set(comunidades.values())

        for comunidad_candidata in todas_comunidades:
            if comunidad_candidata == comunidad_actual:
                continue

            # Probar mover el nodo a esta comunidad
            comunidades_temp = comunidades.copy()
            comunidades_temp[nodo] = comunidad_candidata
            
            mod_temp = modularidad_optimizada(G, comunidades_temp)

            if mod_temp > mejor_modularidad:
                mejor_modularidad = mod_temp
                mejor_comunidad = comunidad_candidata

        # Si hay mejora, actualizar comunidad
        if mejor_comunidad != comunidad_actual:
            comunidades[nodo] = mejor_comunidad
            modularidad_actual = mejor_modularidad
            mejora = True

    return comunidades, mejora

def visualizar_comunidades(G, comunidades):
    """
    Visualiza el grafo coloreado por comunidades.
    """
    plt.figure(figsize=(12, 12))

    # Posición del grafo
    pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
    
    # Colores para comunidades
    comunidades_unicas = list(set(comunidades.values()))
    colores = plt.get_cmap('tab20')(range(len(comunidades_unicas)))

    # Dibujar nodos por comunidad
    for i, comunidad in enumerate(comunidades_unicas):
        nodos_comunidad = [nodo for nodo in G.nodes() if comunidades[nodo] == comunidad]
        nx.draw_networkx_nodes(G, pos, nodelist=nodos_comunidad,
                               node_color=[colores[i]], 
                               node_size=500, 
                               alpha=0.8,
                               label=f'Comunidad {comunidad} ({len(nodos_comunidad)} nodos)')
    
    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray', width=1.0)
    
    # Etiquetas de nodos
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

    plt.title(f'Detección de Comunidades - Grafo Karate', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.axis('off')
    plt.tight_layout()

    plt.show()

def generar_dendrograma(G):
    """
    Genera un dendrograma a partir de las distancias entre nodos en el grafo.
    Utiliza la técnica de enlace jerárquico.
    """
    # Paso 1: Obtener las distancias entre los nodos
    nodos = list(G.nodes())
    distancias = []

    for i in range(len(nodos)):
        for j in range(i+1, len(nodos)):
            # Aquí usamos la distancia euclidiana (o cualquier otra métrica que prefieras)
            if G.has_edge(nodos[i], nodos[j]):
                # Usamos el peso de la arista como la distancia
                distancias.append([nodos[i], nodos[j], G[nodos[i]][nodos[j]]['weight']])

    # Paso 2: Realizar el enlace jerárquico
    Z = linkage(distancias, method='single')  # 'single' es el enlace simple

    # Paso 3: Dibujar el dendrograma
    plt.figure(figsize=(10, 7))
    dendrogram(Z, labels=nodos, leaf_rotation=90)
    plt.title('Dendrograma de la Comunidad')
    plt.xlabel('Nodos')
    plt.ylabel('Distancia')
    plt.tight_layout()

    plt.show()

def main():
    """
    Función principal
    """
    archivo_gml = 'grafo_karate.gml'  # Ruta al archivo GML
    
    # Cargar grafo desde archivo GML
    G = cargar_grafo_desde_gml(archivo_gml)
    
    if G is None:
        return

    # Detectar comunidades
    comunidades, historial_modularidad = detectar_comunidades_greedy(G)
    
    # Visualizar el grafo con comunidades
    visualizar_comunidades(G, comunidades)
    
    # Generar el dendrograma
    generar_dendrograma(G)

if __name__ == "__main__":
    main()
