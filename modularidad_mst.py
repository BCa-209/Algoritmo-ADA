import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import defaultdict

def cargar_mst_desde_gml(ruta_archivo):
    """
    Carga el MST desde archivo GML
    """
    try:
        mst = nx.read_gml(ruta_archivo)
        nombre_grafo = os.path.basename(ruta_archivo).replace('mst_', '').replace('.gml', '')
        
        print(f"MST cargado: {nombre_grafo}")
        print(f"  Nodos: {mst.number_of_nodes()}")
        print(f"  Aristas: {mst.number_of_edges()}")
        
        return mst, nombre_grafo
    except Exception as e:
        print(f"Error cargando {ruta_archivo}: {e}")
        return None, None

def modularidad(G, comunidades):
    """
    Calcula la modularidad del grafo dado un agrupamiento en comunidades
    """
    m = G.number_of_edges()  # número total de aristas
    if m == 0:
        return 0.0
    
    Q = 0.0
    grados = dict(G.degree())
    
    for i in G.nodes():
        for j in G.nodes():
            if i == j:
                continue
                
            A_ij = 1 if G.has_edge(i, j) else 0
            k_i = grados[i]
            k_j = grados[j]
            misma_comunidad = 1 if comunidades[i] == comunidades[j] else 0
            Q += (A_ij - (k_i * k_j) / (2 * m)) * misma_comunidad
    
    return Q / (2 * m)

def modularidad_optimizada(G, comunidades):
    """
    Versión optimizada del cálculo de modularidad
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
        # Suma de grados en la comunidad
        suma_grados = sum(grados[nodo] for nodo in nodos)
        
        # Aristas dentro de la comunidad
        aristas_internas = 0
        for i in nodos:
            for j in nodos:
                if i < j and G.has_edge(i, j):  # Evitar contar dos veces
                    aristas_internas += 1
        
        Q += (aristas_internas / m) - (suma_grados / (2 * m)) ** 2
    
    return Q

def mejorar_comunidades(G, comunidades):
    """
    Mejora las comunidades moviendo nodos individualmente
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
            print(f"  Nodo {nodo} movido a comunidad {mejor_comunidad}")

    return comunidades, mejora

def detectar_comunidades_greedy(G):
    """
    Algoritmo greedy para detección de comunidades basado en modularidad
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

def analizar_comunidades(G, comunidades):
    """
    Analiza y muestra estadísticas de las comunidades detectadas
    """
    print("\n" + "="*60)
    print("ANÁLISIS DE COMUNIDADES DETECTADAS")
    print("="*60)
    
    # Agrupar nodos por comunidad
    comunidades_nodos = defaultdict(list)
    for nodo, comunidad in comunidades.items():
        comunidades_nodos[comunidad].append(nodo)
    
    print(f"Número de comunidades detectadas: {len(comunidades_nodos)}")
    print("\nDistribución de comunidades:")
    
    for comunidad, nodos in sorted(comunidades_nodos.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  Comunidad {comunidad}: {len(nodos)} nodos")
        print(f"    Nodos: {nodos}")
        
        # Calcular métricas internas de la comunidad
        subgrafo = G.subgraph(nodos)
        densidad = nx.density(subgrafo)
        print(f"    Densidad interna: {densidad:.4f}")
        print(f"    Aristas internas: {subgrafo.number_of_edges()}")
        print()

def visualizar_comunidades(G, comunidades, nombre_grafo, carpeta_salida="resultados_modularidad"):
    """
    Visualiza el grafo coloreado por comunidades
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    plt.figure(figsize=(14, 10))
    
    # Posición del grafo
    pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
    
    # Colores para comunidades
    comunidades_unicas = list(set(comunidades.values()))
    colores = plt.get_cmap('Set3')(range(len(comunidades_unicas)))
    
    # Dibujar nodos por comunidad
    for i, comunidad in enumerate(comunidades_unicas):
        nodos_comunidad = [nodo for nodo in G.nodes() if comunidades[nodo] == comunidad]
        nx.draw_networkx_nodes(G, pos, nodelist=nodos_comunidad,
                            node_color=[colores[i]], 
                            node_size=800, 
                            alpha=0.8,
                            label=f'Comunidad {comunidad} ({len(nodos_comunidad)} nodos)')
    
    # Dibujar aristas
    if G.number_of_edges() > 0:
        nx.draw_networkx_edges(G, pos, alpha=0.6, edge_color='gray', width=1.5)
    
    # Etiquetas de nodos
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Etiquetas de aristas (pesos)
    if G.number_of_edges() <= 40:  # Solo si no son demasiadas aristas
        etiquetas_aristas = {(u, v): f"{d.get('weight', 0):.3f}" 
                        for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_aristas, font_size=8)
    
    plt.title(f'Comunidades en MST - {nombre_grafo}\n'
            f'Modularidad: {modularidad_optimizada(G, comunidades):.4f} | '
            f'Comunidades: {len(comunidades_unicas)}', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.axis('off')
    plt.tight_layout()
    
    # Guardar imagen
    ruta_imagen = os.path.join(carpeta_salida, f"comunidades_{nombre_grafo}.png")
    plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Visualización guardada: {ruta_imagen}")

def guardar_resultados_comunidades(G, comunidades, nombre_grafo, carpeta_salida="resultados_modularidad"):
    """
    Guarda los resultados de las comunidades en archivos
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Guardar asignación de comunidades
    df_comunidades = pd.DataFrame([
        {'nodo': nodo, 'comunidad': comunidad, 'grado': G.degree(nodo)}
        for nodo, comunidad in comunidades.items()
    ])
    
    ruta_csv = os.path.join(carpeta_salida, f"comunidades_{nombre_grafo}.csv")
    df_comunidades.to_csv(ruta_csv, index=False)
    print(f"Asignación de comunidades guardada: {ruta_csv}")
    
    # Guardar en formato GML con atributos de comunidad
    for nodo in G.nodes():
        G.nodes[nodo]['comunidad'] = int(comunidades[nodo])
    
    ruta_gml = os.path.join(carpeta_salida, f"mst_con_comunidades_{nombre_grafo}.gml")
    nx.write_gml(G, ruta_gml)
    print(f"Grafo con comunidades guardado: {ruta_gml}")
    
    return df_comunidades

def main():
    """
    Función principal
    """
    print("=" * 70)
    print("ALGORITMO DE MODULARIDAD PARA MST")
    print("=" * 70)
    
    # CONFIGURACIÓN
    ARCHIVO_MST = "mst_resultados/mst_df_original_directa.gml"  # ← MODIFICA AQUÍ
    
    if not os.path.exists(ARCHIVO_MST):
        print(f"Error: No se encuentra el archivo {ARCHIVO_MST}")
        print("Archivos disponibles en mst_resultados/:")
        if os.path.exists("mst_resultados"):
            for archivo in os.listdir("mst_resultados"):
                if archivo.endswith('.gml'):
                    print(f"  - {archivo}")
        return
    
    # Cargar MST
    mst, nombre_grafo = cargar_mst_desde_gml(ARCHIVO_MST)
    
    if mst is None:
        return
    
    # Verificar que el grafo tenga aristas
    if mst.number_of_edges() == 0:
        print("El MST no tiene aristas. No se pueden detectar comunidades.")
        return
    
    # Detectar comunidades
    comunidades, historial_modularidad = detectar_comunidades_greedy(mst)
    
    # Analizar resultados
    analizar_comunidades(mst, comunidades)
    
    # Visualizar
    visualizar_comunidades(mst, comunidades, nombre_grafo)
    
    # Guardar resultados
    df_resultados = guardar_resultados_comunidades(mst, comunidades, nombre_grafo)
    
    # Gráfico de evolución de modularidad
    plt.figure(figsize=(10, 6))
    plt.plot(historial_modularidad, 'bo-', linewidth=2, markersize=6)
    plt.title(f'Evolución de la Modularidad - {nombre_grafo}')
    plt.xlabel('Iteración')
    plt.ylabel('Modularidad')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    ruta_evolucion = os.path.join("resultados_modularidad", f"evolucion_modularidad_{nombre_grafo}.png")
    plt.savefig(ruta_evolucion, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n" + "="*70)
    print("DETECCIÓN DE COMUNIDADES COMPLETADA")
    print("="*70)
    print(f"Archivo procesado: {ARCHIVO_MST}")
    print(f"Comunidades detectadas: {len(set(comunidades.values()))}")
    print(f"Modularidad final: {modularidad_optimizada(mst, comunidades):.6f}")

if __name__ == "__main__":
    main()