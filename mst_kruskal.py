import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
import sys

# Configurar encoding para evitar problemas con caracteres Unicode
sys.stdout.reconfigure(encoding='utf-8')

def cargar_grafo_desde_gml(ruta_archivo):
    """
    Carga un grafo desde archivo GML
    """
    try:
        G = nx.read_gml(ruta_archivo)
        nombre_grafo = os.path.basename(ruta_archivo).replace('grafo_', '').replace('.gml', '')
        
        print(f"Grafo cargado: {nombre_grafo}")
        print(f"  Nodos: {G.number_of_nodes()}")
        print(f"  Aristas: {G.number_of_edges()}")
        
        return G, nombre_grafo
    except Exception as e:
        print(f"Error cargando {ruta_archivo}: {e}")
        return None, None

def cargar_grafo_desde_csv(ruta_archivo):
    """
    Carga un grafo desde el archivo CSV (mantenido por compatibilidad)
    """
    df = pd.read_csv(ruta_archivo)
    
    # Crear grafo
    G = nx.Graph()
    
    # Extraer nombre del grafo desde la primera fila
    nombre_grafo = df.iloc[0]['grafo'] if 'grafo' in df.columns else 'grafo_desconocido'
    
    # Añadir nodos (filas con tipo 'nodo')
    nodos_df = df[df['tipo'] == 'nodo']
    for _, nodo in nodos_df.iterrows():
        G.add_node(nodo['nodo'])
    
    # Añadir aristas (filas con tipo 'arista')
    aristas_df = df[df['tipo'] == 'arista']
    for _, arista in aristas_df.iterrows():
        # Verificar que los campos no estén vacíos
        if pd.notna(arista['origen']) and pd.notna(arista['destino']):
            G.add_edge(arista['origen'], arista['destino'], 
                      weight=arista['peso'], 
                      distance=arista['distancia'])
    
    print(f"Grafo cargado: {nombre_grafo}")
    print(f"  Nodos: {G.number_of_nodes()}")
    print(f"  Aristas: {G.number_of_edges()}")
    
    return G, nombre_grafo

def kruskal_networkx(grafo):
    """
    Usa la implementación de Kruskal de NetworkX
    """
    return nx.minimum_spanning_tree(grafo, weight='weight')
    #return nx.minimum_spanning_tree(grafo, weight='weight', algorithm='kruskal')

def analizar_mst(grafo_original, mst, nombre_grafo):
    """
    Analiza y compara el grafo original con el MST
    """
    print(f"\n" + "="*60)
    print(f"ARBOL DE EXPANSION MINIMA - {nombre_grafo}")
    print("="*60)
    
    peso_total_original = sum(d['weight'] for u, v, d in grafo_original.edges(data=True))
    peso_total_mst = sum(d['weight'] for u, v, d in mst.edges(data=True))
    
    # Contar nodos aislados
    nodos_aislados = [nodo for nodo in mst.nodes() if mst.degree(nodo) == 0]
    
    print(f"Grafo original:")
    print(f"  Nodos: {grafo_original.number_of_nodes()}")
    print(f"  Aristas: {grafo_original.number_of_edges()}")
    print(f"  Peso total: {peso_total_original:.6f}")
    
    print(f"\nArbol de expansion minima:")
    print(f"  Nodos totales: {mst.number_of_nodes()}")
    print(f"  Nodos conectados: {mst.number_of_nodes() - len(nodos_aislados)}")
    print(f"  Nodos aislados: {len(nodos_aislados)}")
    print(f"  Aristas: {mst.number_of_edges()}")
    print(f"  Peso total: {peso_total_mst:.6f}")
    print(f"  Reduccion de aristas: {grafo_original.number_of_edges() - mst.number_of_edges()}")
    
    if nodos_aislados:
        print(f"  Nodos aislados: {nodos_aislados}")
    
    # Aristas en el MST (ordenadas por peso)
    print(f"\nAristas del MST (ordenadas por correlacion):")
    aristas_mst = sorted(mst.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
    for u, v, datos in aristas_mst:
        correlacion = datos['weight']
        distancia = datos.get('distance', 0)
        print(f"  {u} <-> {v}: peso={correlacion:.6f}, dist={distancia:.6f}")

def visualizar_mst_comparacion(grafo_original, mst, nombre_grafo, carpeta_salida="mst_resultados"):
    """
    Visualiza el grafo original y el MST lado a lado, marcando nodos aislados
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Posición consistente para ambos grafos
    pos = nx.spring_layout(grafo_original, k=1, iterations=50, seed=42)
    
    # Grafo original
    nx.draw_networkx_nodes(grafo_original, pos, ax=ax1, node_size=500, 
                          node_color='lightblue', alpha=0.9, edgecolors='black')
    if grafo_original.number_of_edges() > 0:
        nx.draw_networkx_edges(grafo_original, pos, ax=ax1, alpha=0.3, 
                              edge_color='gray', width=1)
    nx.draw_networkx_labels(grafo_original, pos, ax=ax1, font_size=8)
    ax1.set_title(f'Grafo Original\n{nombre_grafo}\n'
                 f'Nodos: {grafo_original.number_of_nodes()}, '
                 f'Aristas: {grafo_original.number_of_edges()}', fontsize=12)
    
    # MST - identificar nodos aislados
    nodos_conectados = [nodo for nodo in mst.nodes() if mst.degree(nodo) > 0]
    nodos_aislados = [nodo for nodo in mst.nodes() if mst.degree(nodo) == 0]
    
    # Dibujar nodos conectados
    nx.draw_networkx_nodes(mst, pos, nodelist=nodos_conectados, ax=ax2, 
                          node_size=500, node_color='lightgreen', 
                          alpha=0.9, edgecolors='black')
    
    # Dibujar nodos aislados en rojo para destacarlos
    if nodos_aislados:
        nx.draw_networkx_nodes(mst, pos, nodelist=nodos_aislados, ax=ax2,
                              node_size=300, node_color='red',
                              alpha=0.7, edgecolors='darkred')
    
    if mst.number_of_edges() > 0:
        # Usar grosor proporcional al peso (correlación)
        pesos = [d['weight'] for u, v, d in mst.edges(data=True)]
        grosores = [p * 10 + 1 for p in pesos]  # Escalar grosor
        
        nx.draw_networkx_edges(mst, pos, ax=ax2, width=grosores, 
                              alpha=0.8, edge_color='darkgreen')
        
        # Etiquetas de peso
        etiquetas = {(u, v): f"{d['weight']:.3f}" 
                     for u, v, d in mst.edges(data=True)}
        nx.draw_networkx_edge_labels(mst, pos, ax=ax2, edge_labels=etiquetas, 
                                   font_size=7)
    
    nx.draw_networkx_labels(mst, pos, ax=ax2, font_size=8)
    
    # Añadir leyenda para nodos aislados
    if nodos_aislados:
        ax2.text(0.02, 0.02, f'Nodos aislados: {len(nodos_aislados)}', 
                transform=ax2.transAxes, fontsize=10, color='red',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    ax2.set_title(f'Arbol de Expansion Minima (Kruskal)\n{nombre_grafo}\n'
                 f'Nodos conectados: {len(nodos_conectados)}, '
                 f'Aristas: {mst.number_of_edges()}', fontsize=12)
    
    for ax in [ax1, ax2]:
        ax.axis('off')
    
    plt.tight_layout()
    
    # Guardar imagen
    ruta_imagen = os.path.join(carpeta_salida, f"mst_{nombre_grafo}.png")
    plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Imagen guardada: {ruta_imagen}")
    if nodos_aislados:
        print(f"Nodos aislados en el MST: {nodos_aislados}")

def guardar_mst_gml(mst, nombre_grafo, carpeta_salida="mst_resultados"):
    """
    Guarda el MST en formato GML, excluyendo nodos aislados
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Crear un nuevo grafo sin nodos aislados
    mst_filtrado = mst.copy()
    nodos_aislados = [nodo for nodo in mst_filtrado.nodes() if mst_filtrado.degree(nodo) == 0]
    mst_filtrado.remove_nodes_from(nodos_aislados)
    
    ruta_gml = os.path.join(carpeta_salida, f"mst_{nombre_grafo}.gml")
    nx.write_gml(mst_filtrado, ruta_gml)
    
    print(f"MST guardado (GML): {ruta_gml}")
    print(f"  Nodos eliminados (aislados): {len(nodos_aislados)}")
    return ruta_gml

def guardar_mst_csv(mst, nombre_grafo, carpeta_salida="mst_resultados"):
    """
    Guarda el MST en formato CSV, excluyendo nodos aislados
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    datos = []
    
    # Solo incluir nodos que tienen conexiones (grado > 0)
    for nodo in mst.nodes():
        grado = mst.degree(nodo)
        if grado > 0:  # Solo incluir nodos conectados
            datos.append({
                'grafo': f"{nombre_grafo}_MST",
                'nodo': nodo,
                'grado': grado,
                'tipo': 'nodo',
                'origen': '',
                'destino': '',
                'peso': '',
                'distancia': ''
            })
    
    # Aristas del MST
    for u, v, datos_arista in mst.edges(data=True):
        datos.append({
            'grafo': f"{nombre_grafo}_MST",
            'nodo': '',
            'grado': '',
            'tipo': 'arista',
            'origen': u,
            'destino': v,
            'peso': datos_arista.get('weight', 0),
            'distancia': datos_arista.get('distance', 0)
        })
    
    df_mst = pd.DataFrame(datos)
    ruta_csv = os.path.join(carpeta_salida, f"mst_{nombre_grafo}.csv")
    df_mst.to_csv(ruta_csv, index=False)
    
    nodos_aislados = [nodo for nodo in mst.nodes() if mst.degree(nodo) == 0]
    print(f"Datos del MST guardados (CSV): {ruta_csv}")
    print(f"  Nodos eliminados (aislados): {len(nodos_aislados)}")
    return df_mst

def exportar_aristas_importantes(mst, nombre_grafo, carpeta_salida="mst_resultados", top_n=5):
    """
    Exporta las aristas más importantes del MST (mayor correlación)
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    aristas_ordenadas = sorted(mst.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
    
    print(f"\nTOP {top_n} ARISTAS MAS IMPORTANTES DEL MST:")
    print("-" * 50)
    
    datos_importantes = []
    for i, (u, v, datos) in enumerate(aristas_ordenadas[:top_n], 1):
        peso = datos['weight']
        distancia = datos.get('distance', 0)
        print(f"{i}. {u} <-> {v}:")
        print(f"   Correlacion: {peso:.6f}")
        print(f"   Distancia: {distancia:.6f}")
        print(f"   Fuerza de relacion: {peso * 100:.2f}%")
        print()
        
        datos_importantes.append({
            'ranking': i,
            'arista': f"{u} <-> {v}",
            'correlacion': peso,
            'distancia': distancia,
            'fuerza_relacion': peso * 100
        })
    
    # Guardar en CSV
    df_importantes = pd.DataFrame(datos_importantes)
    ruta_importantes = os.path.join(carpeta_salida, f"aristas_importantes_{nombre_grafo}.csv")
    df_importantes.to_csv(ruta_importantes, index=False)
    print(f"Aristas importantes guardadas: {ruta_importantes}")

def main():
    print("=" * 70)
    print("ALGORITMO DE KRUSKAL - ARBOL DE EXPANSION MINIMA")
    print("=" * 70)
    
    carpeta_grafos = "grafos"
    
    # CONFIGURACIÓN: Elige qué grafos procesar
    GRAFOS_A_PROCESAR = []  # ← MODIFICA AQUÍ
    #GRAFOS_A_PROCESAR = ['B4C']  # ← MODIFICA AQUÍ
    # Opciones:
    # ['B4C_mixto']           - Solo B4C
    # ['W4C_mixto']           - Solo W4C  
    # ['B4C_mixto', 'W4C_mixto'] - Ambos
    # []                      - Todos los disponibles
    
    if not os.path.exists(carpeta_grafos):
        print(f"Error: La carpeta '{carpeta_grafos}' no existe")
        print("Ejecuta primero: python grafo.py")
        return
    
    # Buscar archivos GML (nuevo formato)
    archivos_gml = [f for f in os.listdir(carpeta_grafos) 
                   if f.startswith('grafo_') and f.endswith('.gml') and not f.startswith('grafo_con_metricas_')]
    
    # Buscar archivos CSV (formato antiguo - por compatibilidad)
    archivos_csv = [f for f in os.listdir(carpeta_grafos) 
                   if f.startswith('datos_grafo_') and f.endswith('.csv')]
    
    # Filtrar por GRAFOS_A_PROCESAR si se especificó
    if GRAFOS_A_PROCESAR:
        archivos_gml = [f for f in archivos_gml 
                       if any(grafo in f for grafo in GRAFOS_A_PROCESAR)]
        archivos_csv = [f for f in archivos_csv 
                       if any(grafo in f for grafo in GRAFOS_A_PROCESAR)]
    
    archivos_grafo = archivos_gml + archivos_csv
    
    if not archivos_grafo:
        print("No se encontraron archivos de grafos que coincidan con la configuración")
        print("Archivos disponibles en la carpeta 'grafos':")
        for archivo in os.listdir(carpeta_grafos):
            if archivo.startswith('grafo_') and archivo.endswith('.gml'):
                print(f"  - {archivo} (GML)")
            elif archivo.startswith('datos_grafo_'):
                print(f"  - {archivo} (CSV)")
        return
    
    print(f"Archivos de grafos encontrados:")
    for archivo in archivos_gml:
        print(f"  - {archivo} (GML)")
    for archivo in archivos_csv:
        print(f"  - {archivo} (CSV)")
    
    for archivo in archivos_grafo:
        try:
            # Determinar tipo de archivo y cargar
            ruta_completa = os.path.join(carpeta_grafos, archivo)
            
            if archivo.endswith('.gml'):
                grafo_original, nombre_grafo = cargar_grafo_desde_gml(ruta_completa)
            else:
                grafo_original, nombre_grafo = cargar_grafo_desde_csv(ruta_completa)
            
            if grafo_original is None:
                continue
                
            if grafo_original.number_of_edges() == 0:
                print("  El grafo no tiene aristas, no se puede aplicar Kruskal")
                continue
            
            # Aplicar Kruskal
            mst = kruskal_networkx(grafo_original)
            
            # Analizar resultados
            analizar_mst(grafo_original, mst, nombre_grafo)
            
            # Exportar aristas importantes
            exportar_aristas_importantes(mst, nombre_grafo)
            
            # Visualizar
            visualizar_mst_comparacion(grafo_original, mst, nombre_grafo)
            
            # Guardar resultados en GML (nuevo formato)
            guardar_mst_gml(mst, nombre_grafo)
            
            # También guardar en CSV (opcional - por compatibilidad)
            guardar_mst_csv(mst, nombre_grafo)
            
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n" + "="*70)
    print("PROCESO DE KRUSKAL COMPLETADO")
    print("="*70)

if __name__ == "__main__":
    main()