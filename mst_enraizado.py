# mst_enraizado.py
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colormaps
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
from collections import deque

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

def mostrar_nodos_disponibles(mst):
    """
    Muestra los nodos disponibles para elegir como raíz
    """
    nodos = list(mst.nodes())
    print(f"\nNODOS DISPONIBLES EN EL GRAFO:")
    print("=" * 40)
    
    # Mostrar nodos en columnas para mejor visualización
    for i, nodo in enumerate(nodos, 1):
        grado = mst.degree(nodo)
        print(f"{i:2d}. {nodo:10} (grado: {grado})")
    
    return nodos

def elegir_nodo_raiz(nodos):
    """
    Permite al usuario elegir el nodo raíz
    """
    while True:
        try:
            print(f"\n" + "=" * 50)
            opcion = input("Elige el número del nodo que quieres como raíz (variable objetivo): ").strip()
            
            if opcion.isdigit():
                indice = int(opcion) - 1
                if 0 <= indice < len(nodos):
                    nodo_raiz = nodos[indice]
                    print(f"Nodo seleccionado como raíz: {nodo_raiz}")
                    return nodo_raiz
                else:
                    print("Número fuera de rango. Intenta nuevamente.")
            else:
                # Buscar por nombre
                opcion_lower = opcion.lower()
                coincidencias = [n for n in nodos if opcion_lower in n.lower()]
                if len(coincidencias) == 1:
                    print(f"Nodo seleccionado como raíz: {coincidencias[0]}")
                    return coincidencias[0]
                elif len(coincidencias) > 1:
                    print("Múltiples coincidencias. Por favor especifica:")
                    for i, n in enumerate(coincidencias, 1):
                        print(f"  {i}. {n}")
                else:
                    print("Nodo no encontrado. Intenta nuevamente.")
                    
        except KeyboardInterrupt:
            print("\nEjecución interrumpida por el usuario.")
            exit()
        except Exception as e:
            print(f"Error: {e}")

def enraizar_mst(mst, nodo_raiz):
    """
    Convierte el MST en un árbol enraizado con el nodo especificado como raíz
    Incluye nodos aislados
    """
    # Crear un árbol dirigido desde el MST
    arbol_enraizado = nx.DiGraph()
    
    # Copiar todos los nodos (incluyendo aislados)
    arbol_enraizado.add_nodes_from(mst.nodes())
    
    # Para nodos aislados, los mantenemos pero sin conexiones
    nodos_aislados = [nodo for nodo in mst.nodes() if mst.degree(nodo) == 0]
    
    # Verificar si el nodo raíz está aislado
    if mst.degree(nodo_raiz) == 0:
        print(f"ADVERTENCIA: El nodo raíz '{nodo_raiz}' está aislado (sin conexiones)")
        # Marcar todos los nodos como aislados en este caso
        for nodo in arbol_enraizado.nodes():
            arbol_enraizado.nodes[nodo]['aislado'] = True
            arbol_enraizado.nodes[nodo]['profundidad'] = -1
        return arbol_enraizado
    
    # Realizar BFS desde el nodo raíz para establecer direcciones
    visitados = set([nodo_raiz])
    cola = deque([nodo_raiz])
    
    while cola:
        nodo_actual = cola.popleft()
        
        for vecino in mst.neighbors(nodo_actual):
            if vecino not in visitados:
                # Añadir arista desde el nodo actual hacia el vecino
                peso = mst[nodo_actual][vecino]['weight']
                distancia = mst[nodo_actual][vecino].get('distance', 0)
                
                arbol_enraizado.add_edge(nodo_actual, vecino, 
                                    weight=peso, 
                                    distance=distancia,
                                    direccion=f"{nodo_actual} → {vecino}")
            
                visitados.add(vecino)
                cola.append(vecino)
    
    # Añadir información sobre nodos aislados
    for nodo_aislado in nodos_aislados:
        arbol_enraizado.nodes[nodo_aislado]['aislado'] = True
        arbol_enraizado.nodes[nodo_aislado]['profundidad'] = -1  # Profundidad especial para aislados
    
    return arbol_enraizado

def analizar_arbol_enraizado(arbol, nodo_raiz):
    """
    Analiza la estructura del árbol enraizado
    """
    print(f"\n" + "=" * 60)
    print(f"ANÁLISIS DEL ÁRBOL ENRAIZADO (Raíz: {nodo_raiz})")
    print("=" * 60)
    
    # Calcular profundidades y niveles (excluyendo nodos aislados)
    profundidades = {}
    niveles = {}
    nodos_aislados = []
    
    def calcular_profundidad(nodo_actual, profundidad_actual):
        if arbol.nodes[nodo_actual].get('aislado', False):
            nodos_aislados.append(nodo_actual)
            return
            
        profundidades[nodo_actual] = profundidad_actual
        if profundidad_actual not in niveles:
            niveles[profundidad_actual] = []
        niveles[profundidad_actual].append(nodo_actual)
        
        for sucesor in arbol.successors(nodo_actual):
            calcular_profundidad(sucesor, profundidad_actual + 1)
    
    calcular_profundidad(nodo_raiz, 0)
    
    print(f"Estructura jerárquica:")
    for nivel in sorted(niveles.keys()):
        nodos_nivel = niveles[nivel]
        prefijo = "  " * nivel
        print(f"Nivel {nivel}: {prefijo}{nodos_nivel}")
    
    # Mostrar nodos aislados
    if nodos_aislados:
        print(f"\nNodos aislados (sin conexiones): {nodos_aislados}")
    
    # Encontrar hojas (nodos sin sucesores, excluyendo aislados)
    hojas = [nodo for nodo in arbol.nodes() 
            if arbol.out_degree(nodo) == 0 and not arbol.nodes[nodo].get('aislado', False)]
    
    print(f"\nHojas del árbol ({len(hojas)}): {hojas}")
    
    # Encontrar rama más larga
    if profundidades:
        rama_mas_larga = max(profundidades.values())
        print(f"Profundidad máxima: {rama_mas_larga}")
    else:
        rama_mas_larga = 0
        print(f"Profundidad máxima: 0 (solo nodo raíz)")
    
    return profundidades, niveles, hojas, nodos_aislados

def crear_layout_jerarquico(arbol, nodo_raiz):
    """
    Crea un layout jerárquico manual sin depender de pygraphviz
    Maneja nodos aislados
    """
    # Calcular profundidades (excluyendo nodos aislados)
    profundidades = {}
    niveles = {}
    nodos_aislados = []
    
    def calcular_profundidad(nodo_actual, profundidad_actual):
        if arbol.nodes[nodo_actual].get('aislado', False):
            nodos_aislados.append(nodo_actual)
            return
            
        profundidades[nodo_actual] = profundidad_actual
        if profundidad_actual not in niveles:
            niveles[profundidad_actual] = []
        niveles[profundidad_actual].append(nodo_actual)
        
        for sucesor in arbol.successors(nodo_actual):
            calcular_profundidad(sucesor, profundidad_actual + 1)
    
    calcular_profundidad(nodo_raiz, 0)
    
    # Crear posiciones
    pos = {}
    
    # Posicionar nodos conectados
    if niveles:
        nivel_height = 1.0 / (len(niveles) + 1)
        
        for nivel, nodos_nivel in niveles.items():
            nivel_y = 1.0 - (nivel * nivel_height)
            num_nodos = len(nodos_nivel)
            nivel_width = 1.0 / (num_nodos + 1)
            
            for i, nodo in enumerate(nodos_nivel):
                x = (i + 1) * nivel_width
                pos[nodo] = (x, nivel_y)
    else:
        # Si no hay niveles (solo nodo raíz aislado o estructura vacía)
        # Asegurarnos de que el nodo raíz tenga posición
        if nodo_raiz in arbol.nodes():
            pos[nodo_raiz] = (0.5, 0.5)
    
    # Posicionar nodos aislados en una fila separada
    if nodos_aislados:
        aislados_y = 0.1  # Posición en la parte inferior
        num_aislados = len(nodos_aislados)
        aislados_width = 1.0 / (num_aislados + 1) if num_aislados > 0 else 1.0
        
        for i, nodo in enumerate(nodos_aislados):
            x = (i + 1) * aislados_width
            pos[nodo] = (x, aislados_y)
    
    # Asegurar que TODOS los nodos tengan posición
    for nodo in arbol.nodes():
        if nodo not in pos:
            # Asignar posición por defecto a cualquier nodo faltante
            pos[nodo] = (0.1, 0.1)
    
    return pos

def visualizar_arbol_enraizado(arbol, nodo_raiz, nombre_grafo, carpeta_salida="mst_enraizado"):
    """
    Visualiza el árbol enraizado de manera jerárquica (sin pygraphviz)
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    plt.figure(figsize=(14, 10))
    
    # Usar layout jerárquico manual
    pos = crear_layout_jerarquico(arbol, nodo_raiz)
    
    # Calcular profundidades para colorear (manejar nodos aislados)
    colores = []
    for nodo in arbol.nodes():
        if arbol.nodes[nodo].get('aislado', False):
            colores.append(-1)  # Color especial para aislados
        else:
            try:
                # Calcular profundidad para nodos conectados
                profundidad = nx.shortest_path_length(arbol, nodo_raiz, nodo)
                colores.append(profundidad)
            except nx.NetworkXNoPath:
                colores.append(-1)  # En caso de error, tratar como aislado
    
    # Dibujar nodos conectados
    nodos_conectados = [nodo for nodo in arbol.nodes() if colores[list(arbol.nodes()).index(nodo)] >= 0]
    nodos_aislados = [nodo for nodo in arbol.nodes() if colores[list(arbol.nodes()).index(nodo)] == -1]
    
    if nodos_conectados:
        pos_conectados = {nodo: pos[nodo] for nodo in nodos_conectados}
        colores_conectados = [c for c in colores if c >= 0]
        
        # Crear un mapeo de nodos a sus posiciones para dibujar
        scatter = nx.draw_networkx_nodes(arbol, pos_conectados, 
                            nodelist=nodos_conectados,
                            node_size=800, 
                            node_color=colores_conectados, 
                            cmap=plt.colormaps['Blues'],
                            alpha=0.8,
                            edgecolors='black')
        
        # Dibujar aristas con direcciones (solo para nodos conectados)
        aristas_conectadas = [(u, v) for u, v in arbol.edges() 
                            if u in nodos_conectados and v in nodos_conectados]
        
        if aristas_conectadas:
            nx.draw_networkx_edges(arbol, pos, 
                                edgelist=aristas_conectadas,
                                arrowstyle='->',
                                arrowsize=20,
                                edge_color='gray',
                                width=1.5,
                                alpha=0.7)
    
    # Dibujar nodos aislados
    if nodos_aislados:
        pos_aislados = {nodo: pos[nodo] for nodo in nodos_aislados}
        nx.draw_networkx_nodes(arbol, pos_aislados, 
                            nodelist=nodos_aislados,
                            node_size=600, 
                            node_color='red',
                            alpha=0.6,
                            edgecolors='black',
                            linewidths=2)
    
    # Etiquetas de nodos
    nx.draw_networkx_labels(arbol, pos, font_size=10, font_weight='bold')
    
    # Etiquetas de aristas (pesos) - solo para aristas conectadas
    if 'aristas_conectadas' in locals() and aristas_conectadas:
        etiquetas_aristas = {(u, v): f"{arbol[u][v]['weight']:.3f}" 
                            for u, v in aristas_conectadas}
        nx.draw_networkx_edge_labels(arbol, pos, 
                                edge_labels=etiquetas_aristas,
                                font_size=8)
    
    # Resaltar nodo raíz
    if nodo_raiz in pos:
        color_raiz = 'green' if nodo_raiz in nodos_conectados else 'orange'
        nx.draw_networkx_nodes(arbol, pos, 
                            nodelist=[nodo_raiz],
                            node_size=1000,
                            node_color=color_raiz,
                            alpha=0.9)
    
    plt.title(f'Árbol Enraizado - {nombre_grafo}\n'
            f'Raíz: {nodo_raiz} | Nodos: {arbol.number_of_nodes()} | '
            f'Aristas: {arbol.number_of_edges()} | '
            f'Conectados: {len(nodos_conectados)} | '
            f'Aislados: {len(nodos_aislados)}', 
            fontsize=14, fontweight='bold')
    plt.axis('off')
    
    # Añadir leyenda SOLO si hay nodos conectados con diferentes profundidades
    # Y si el scatter plot fue creado exitosamente
    if nodos_conectados and len(set(colores_conectados)) > 1 and 'scatter' in locals():
        # Crear un eje para la barra de colores
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        ax = plt.gca()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        
        sm = plt.cm.ScalarMappable(cmap=plt.colormaps['Blues'], 
                                norm=plt.Normalize(vmin=min(colores_conectados), 
                                                vmax=max(colores_conectados)))
        sm.set_array([])
        cbar = plt.colorbar(sm, cax=cax)
        cbar.set_label('Profundidad desde la raíz', rotation=270, labelpad=15)
    elif nodos_conectados:
        # Si solo hay un nivel de profundidad, mostrar leyenda simple
        plt.text(1.05, 0.5, f'Todos los nodos conectados\nestán en profundidad {colores_conectados[0]}', 
                transform=plt.gca().transAxes, fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    
    # Guardar imagen
    ruta_imagen = os.path.join(carpeta_salida, f"arbol_enraizado_{nombre_grafo}_{nodo_raiz}.png")
    plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Visualización guardada: {ruta_imagen}")

def exportar_arbol_enraizado(arbol, nodo_raiz, nombre_grafo, carpeta_salida="mst_enraizado"):
    """
    Exporta el árbol enraizado en formatos CSV y GML
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Exportar a GML
    ruta_gml = os.path.join(carpeta_salida, f"arbol_enraizado_{nombre_grafo}_{nodo_raiz}.gml")
    nx.write_gml(arbol, ruta_gml)
    print(f"Árbol guardado (GML): {ruta_gml}")
    
    # Exportar a CSV con estructura jerárquica
    datos = []
    
    for nodo in arbol.nodes():
        es_aislado = arbol.nodes[nodo].get('aislado', False)
        
        if es_aislado:
            profundidad = -1
            es_raiz = False
            es_hoja = True
            padre = ""
            hijos = []
        else:
            try:
                profundidad = nx.shortest_path_length(arbol, nodo_raiz, nodo)
                es_raiz = (nodo == nodo_raiz)
                es_hoja = (arbol.out_degree(nodo) == 0)
                
                # Encontrar padre (predecesor directo)
                predecesores = list(arbol.predecessors(nodo))
                padre = predecesores[0] if predecesores else ""
                
                # Encontrar hijos (sucesores directos)
                hijos = list(arbol.successors(nodo))
            except nx.NetworkXNoPath:
                profundidad = -1
                es_raiz = False
                es_hoja = True
                padre = ""
                hijos = []
        
        datos.append({
            'nodo': nodo,
            'profundidad': profundidad,
            'es_raiz': es_raiz,
            'es_hoja': es_hoja,
            'es_aislado': es_aislado,
            'padre': padre,
            'hijos': ', '.join(hijos) if hijos else '',
            'grado_salida': arbol.out_degree(nodo),
            'grado_entrada': arbol.in_degree(nodo)
        })
    
    df_arbol = pd.DataFrame(datos)
    ruta_csv = os.path.join(carpeta_salida, f"arbol_enraizado_{nombre_grafo}_{nodo_raiz}.csv")
    df_arbol.to_csv(ruta_csv, index=False)
    print(f"Estructura del árbol guardada (CSV): {ruta_csv}")
    
    # Exportar aristas con información de dirección
    datos_aristas = []
    for u, v, datos_arista in arbol.edges(data=True):
        datos_aristas.append({
            'desde': u,
            'hacia': v,
            'peso': datos_arista['weight'],
            'distancia': datos_arista.get('distance', 0),
            'direccion': f"{u} → {v}"
        })
    
    df_aristas = pd.DataFrame(datos_aristas)
    ruta_aristas = os.path.join(carpeta_salida, f"aristas_arbol_{nombre_grafo}_{nodo_raiz}.csv")
    df_aristas.to_csv(ruta_aristas, index=False)
    print(f"Aristas del árbol guardadas (CSV): {ruta_aristas}")
    
    return df_arbol, df_aristas

def generar_reporte_influencia(arbol, nodo_raiz):
    """
    Genera un reporte de influencia desde la raíz hacia las hojas
    """
    print(f"\n" + "=" * 60)
    print(f"REPORTE DE INFLUENCIA DESDE {nodo_raiz}")
    print("=" * 60)
    
    # Calcular caminos desde la raíz a cada hoja (excluyendo aislados)
    hojas = [nodo for nodo in arbol.nodes() 
            if arbol.out_degree(nodo) == 0 and not arbol.nodes[nodo].get('aislado', False)]
    
    for hoja in hojas:
        # Encontrar camino desde raíz a hoja
        try:
            camino = nx.shortest_path(arbol, nodo_raiz, hoja)
            print(f"\nCamino hacia {hoja}:")
            print("  " + " → ".join(camino))
            
            # Calcular peso acumulado del camino
            peso_acumulado = 1.0
            for i in range(len(camino) - 1):
                u, v = camino[i], camino[i + 1]
                peso = arbol[u][v]['weight']
                peso_acumulado *= peso
                print(f"    {u} → {v}: {peso:.4f}")
            
            print(f"  Peso acumulado del camino: {peso_acumulado:.6f}")
            print(f"  Influencia relativa: {peso_acumulado * 100:.2f}%")
            
        except nx.NetworkXNoPath:
            print(f"  No hay camino desde {nodo_raiz} a {hoja}")

def main():
    """
    Función principal
    """
    print("=" * 70)
    print("ENRAIZADO DE ÁRBOL DE EXPANSIÓN MÍNIMA")
    print("=" * 70)
    
    # CONFIGURACIÓN - MODIFICAR AQUÍ
    CARPETA_MST = "mst_resultados"
    ARCHIVO_MST = "mst_W16C_mixto.gml"  # ← CAMBIADO de W4C_mixto a B4C_mixto
    
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
    mst, nombre_grafo = cargar_mst_desde_gml(ruta_mst)
    
    if mst is None:
        return
    
    # Mostrar nodos disponibles
    nodos = mostrar_nodos_disponibles(mst)
    
    # Elegir nodo raíz
    nodo_raiz = elegir_nodo_raiz(nodos)
    
    # Enraizar el MST
    arbol_enraizado = enraizar_mst(mst, nodo_raiz)
    
    # Analizar estructura
    profundidades, niveles, hojas, nodos_aislados = analizar_arbol_enraizado(arbol_enraizado, nodo_raiz)
    
    # Visualizar
    visualizar_arbol_enraizado(arbol_enraizado, nodo_raiz, nombre_grafo)
    
    # Exportar resultados
    df_arbol, df_aristas = exportar_arbol_enraizado(arbol_enraizado, nodo_raiz, nombre_grafo)
    
    # Generar reporte de influencia
    generar_reporte_influencia(arbol_enraizado, nodo_raiz)
    
    print(f"\n" + "=" * 70)
    print("PROCESO DE ENRAIZADO COMPLETADO")
    print("=" * 70)
    print(f"Archivos guardados en carpeta: mst_enraizado/")

if __name__ == "__main__":
    main()