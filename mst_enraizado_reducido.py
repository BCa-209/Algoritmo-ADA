# mst_enraizado_reducido.py
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colormaps
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
from collections import deque

def cargar_arbol_enraizado_desde_gml(ruta_archivo):
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
        
        # Encontrar la raíz (nodo con grado de entrada 0)
        raices = [nodo for nodo in arbol.nodes() if arbol.in_degree(nodo) == 0]
        if raices:
            nodo_raiz = raices[0]
            print(f"  Raíz detectada: {nodo_raiz}")
        else:
            # Si no hay raíz clara, usar el primer nodo
            nodo_raiz = list(arbol.nodes())[0]
            print(f"  Advertencia: No se detectó raíz clara. Usando: {nodo_raiz}")
        
        return arbol, nodo_raiz, nombre_grafo
    except Exception as e:
        print(f"Error cargando {ruta_archivo}: {e}")
        return None, None, None

def cargar_arbol_desde_csv(ruta_csv, ruta_gml):
    """
    Carga el árbol desde CSV y GML para obtener estructura completa
    """
    try:
        # Cargar desde GML (para la estructura del grafo)
        arbol, nodo_raiz, nombre_grafo = cargar_arbol_enraizado_desde_gml(ruta_gml)
        
        # Cargar desde CSV (para información adicional)
        df_arbol = pd.read_csv(ruta_csv)
        
        return arbol, nodo_raiz, nombre_grafo, df_arbol
    except Exception as e:
        print(f"Error cargando árbol desde CSV/GML: {e}")
        return None, None, None, None

def calcular_profundidades(arbol, nodo_raiz):
    """
    Calcula la profundidad de cada nodo desde la raíz
    """
    profundidades = {nodo_raiz: 0}  # La raíz tiene profundidad 0
    
    def calcular_prof(nodo_actual, prof_actual):
        for sucesor in arbol.successors(nodo_actual):
            profundidades[sucesor] = prof_actual + 1
            calcular_prof(sucesor, prof_actual + 1)
    
    calcular_prof(nodo_raiz, 0)
    return profundidades

def reducir_arbol_por_profundidad(arbol, nodo_raiz, profundidad_maxima):
    """
    Reduce el árbol manteniendo solo nodos hasta la profundidad máxima especificada
    """
    # Crear un nuevo árbol dirigido
    arbol_reducido = nx.DiGraph()
    
    # Calcular profundidades
    profundidades = calcular_profundidades(arbol, nodo_raiz)
    
    # Añadir nodos que están dentro del límite de profundidad
    nodos_a_mantener = [nodo for nodo, prof in profundidades.items() 
                       if prof <= profundidad_maxima]
    
    arbol_reducido.add_nodes_from(nodos_a_mantener)
    
    # Añadir aristas que conectan nodos dentro del límite
    for u, v, datos in arbol.edges(data=True):
        if u in nodos_a_mantener and v in nodos_a_mantener:
            arbol_reducido.add_edge(u, v, **datos)
    
    # Copiar atributos de nodos
    for nodo in nodos_a_mantener:
        if nodo in arbol.nodes():
            for atributo, valor in arbol.nodes[nodo].items():
                arbol_reducido.nodes[nodo][atributo] = valor
    
    return arbol_reducido

def analizar_arbol_reducido(arbol_reducido, arbol_original, nodo_raiz, profundidad_maxima):
    """
    Analiza el árbol reducido y muestra estadísticas
    """
    print(f"\n" + "=" * 60)
    print(f"ANÁLISIS DEL ÁRBOL REDUCIDO (Profundidad máxima: {profundidad_maxima})")
    print("=" * 60)
    
    # Calcular profundidades en el árbol reducido
    profundidades_reducido = calcular_profundidades(arbol_reducido, nodo_raiz)
    
    # Estadísticas
    nodos_original = arbol_original.number_of_nodes()
    nodos_reducido = arbol_reducido.number_of_nodes()
    aristas_original = arbol_original.number_of_edges()
    aristas_reducido = arbol_reducido.number_of_edges()
    
    print(f"Nodos en árbol original: {nodos_original}")
    print(f"Nodos en árbol reducido: {nodos_reducido}")
    print(f"Reducción de nodos: {nodos_original - nodos_reducido} "
          f"({((nodos_original - nodos_reducido) / nodos_original * 100):.1f}%)")
    
    print(f"\nAristas en árbol original: {aristas_original}")
    print(f"Aristas en árbol reducido: {aristas_reducido}")
    print(f"Reducción de aristas: {aristas_original - aristas_reducido} "
          f"({((aristas_original - aristas_reducido) / aristas_original * 100):.1f}%)")
    
    # Mostrar estructura por niveles
    niveles = {}
    for nodo, prof in profundidades_reducido.items():
        if prof not in niveles:
            niveles[prof] = []
        niveles[prof].append(nodo)
    
    print(f"\nEstructura del árbol reducido:")
    for nivel in sorted(niveles.keys()):
        nodos_nivel = niveles[nivel]
        prefijo = "  " * nivel
        print(f"Nivel {nivel}: {prefijo}{nodos_nivel}")
    
    # Nodos eliminados
    nodos_eliminados = set(arbol_original.nodes()) - set(arbol_reducido.nodes())
    if nodos_eliminados:
        print(f"\nNodos eliminados (profundidad > {profundidad_maxima}): {list(nodos_eliminados)}")
    
    return profundidades_reducido, nodos_eliminados

def visualizar_arbol_reducido(arbol_reducido, nodo_raiz, nombre_grafo, profundidad_maxima, 
                            carpeta_salida="mst_raiz_reducido"):
    """
    Visualiza el árbol reducido de manera jerárquica
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    plt.figure(figsize=(12, 8))
    
    # Crear layout jerárquico
    pos = crear_layout_jerarquico(arbol_reducido, nodo_raiz)
    
    # Calcular profundidades para colorear
    profundidades = calcular_profundidades(arbol_reducido, nodo_raiz)
    colores = [profundidades[nodo] for nodo in arbol_reducido.nodes()]
    
    # Dibujar nodos
    scatter = nx.draw_networkx_nodes(arbol_reducido, pos, 
                        node_size=800, 
                        node_color=colores, 
                        cmap=plt.colormaps['viridis'],
                        alpha=0.8,
                        edgecolors='black')
    
    # Dibujar aristas con direcciones
    nx.draw_networkx_edges(arbol_reducido, pos, 
                        arrowstyle='->',
                        arrowsize=20,
                        edge_color='gray',
                        width=1.5,
                        alpha=0.7)
    
    # Etiquetas de nodos
    nx.draw_networkx_labels(arbol_reducido, pos, font_size=10, font_weight='bold')
    
    # Etiquetas de aristas (pesos)
    etiquetas_aristas = {(u, v): f"{arbol_reducido[u][v]['weight']:.3f}" 
                        for u, v in arbol_reducido.edges()}
    nx.draw_networkx_edge_labels(arbol_reducido, pos, 
                            edge_labels=etiquetas_aristas,
                            font_size=8)
    
    # Resaltar nodo raíz
    nx.draw_networkx_nodes(arbol_reducido, pos, 
                        nodelist=[nodo_raiz],
                        node_size=1000,
                        node_color='green',
                        alpha=0.9)
    
    plt.title(f'Árbol Reducido - {nombre_grafo}\n'
            f'Raíz: {nodo_raiz} | Profundidad máxima: {profundidad_maxima} | '
            f'Nodos: {arbol_reducido.number_of_nodes()} | '
            f'Aristas: {arbol_reducido.number_of_edges()}', 
            fontsize=14, fontweight='bold')
    plt.axis('off')
    
    # Añadir barra de colores para profundidades
    if len(set(colores)) > 1:  # Solo si hay múltiples profundidades
        ax = plt.gca()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        
        sm = plt.cm.ScalarMappable(cmap=plt.colormaps['viridis'], 
                                norm=plt.Normalize(vmin=min(colores), 
                                                vmax=max(colores)))
        sm.set_array([])
        cbar = plt.colorbar(sm, cax=cax)
        cbar.set_label('Profundidad desde la raíz', rotation=270, labelpad=15)
    
    plt.tight_layout()
    
    # Guardar imagen
    ruta_imagen = os.path.join(carpeta_salida, 
                             f"arbol_reducido_{nombre_grafo}_prof{profundidad_maxima}.png")
    plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Visualización guardada: {ruta_imagen}")

def crear_layout_jerarquico(arbol, nodo_raiz):
    """
    Crea un layout jerárquico manual para visualización
    """
    # Calcular profundidades
    profundidades = calcular_profundidades(arbol, nodo_raiz)
    niveles = {}
    
    for nodo, prof in profundidades.items():
        if prof not in niveles:
            niveles[prof] = []
        niveles[prof].append(nodo)
    
    # Crear posiciones
    pos = {}
    
    if niveles:
        nivel_height = 1.0 / (len(niveles) + 1)
        
        for nivel, nodos_nivel in niveles.items():
            nivel_y = 1.0 - (nivel * nivel_height)
            num_nodos = len(nodos_nivel)
            nivel_width = 1.0 / (num_nodos + 1)
            
            for i, nodo in enumerate(nodos_nivel):
                x = (i + 1) * nivel_width
                pos[nodo] = (x, nivel_y)
    
    return pos

def exportar_arbol_reducido(arbol_reducido, nodo_raiz, nombre_grafo, profundidad_maxima,
                          carpeta_salida="mst_raiz_reducido"):
    """
    Exporta el árbol reducido en formatos CSV y GML
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Exportar a GML
    ruta_gml = os.path.join(carpeta_salida, 
                          f"arbol_reducido_{nombre_grafo}_prof{profundidad_maxima}.gml")
    
    # Asegurarse de que todos los nodos tengan el atributo 'label'
    for nodo in arbol_reducido.nodes():
        if 'label' not in arbol_reducido.nodes[nodo]:
            arbol_reducido.nodes[nodo]['label'] = str(nodo)
    
    nx.write_gml(arbol_reducido, ruta_gml)
    print(f"✓ Árbol reducido guardado (GML): {ruta_gml}")
    
    # Exportar a CSV con estructura jerárquica
    datos = []
    profundidades = calcular_profundidades(arbol_reducido, nodo_raiz)
    
    for nodo in arbol_reducido.nodes():
        es_raiz = (nodo == nodo_raiz)
        es_hoja = (arbol_reducido.out_degree(nodo) == 0)
        
        # Encontrar padre (predecesor directo)
        predecesores = list(arbol_reducido.predecessors(nodo))
        padre = predecesores[0] if predecesores else ""
        
        # Encontrar hijos (sucesores directos)
        hijos = list(arbol_reducido.successors(nodo))
        
        datos.append({
            'nodo': nodo,
            'profundidad': profundidades[nodo],
            'es_raiz': es_raiz,
            'es_hoja': es_hoja,
            'padre': padre,
            'hijos': ', '.join(hijos) if hijos else '',
            'grado_salida': arbol_reducido.out_degree(nodo),
            'grado_entrada': arbol_reducido.in_degree(nodo)
        })
    
    df_arbol = pd.DataFrame(datos)
    ruta_csv = os.path.join(carpeta_salida, 
                          f"arbol_reducido_{nombre_grafo}_prof{profundidad_maxima}.csv")
    df_arbol.to_csv(ruta_csv, index=False, encoding='utf-8')
    print(f"✓ Estructura del árbol reducido guardada (CSV): {ruta_csv}")
    
    # Exportar aristas
    datos_aristas = []
    for u, v, datos_arista in arbol_reducido.edges(data=True):
        datos_aristas.append({
            'desde': u,
            'hacia': v,
            'peso': datos_arista.get('weight', 0),
            'distancia': datos_arista.get('distance', 0),
            'direccion': f"{u} → {v}"
        })
    
    if datos_aristas:  # Solo si hay aristas
        df_aristas = pd.DataFrame(datos_aristas)
        ruta_aristas = os.path.join(carpeta_salida, 
                                  f"aristas_reducido_{nombre_grafo}_prof{profundidad_maxima}.csv")
        df_aristas.to_csv(ruta_aristas, index=False, encoding='utf-8')
        print(f"✓ Aristas del árbol reducido guardadas (CSV): {ruta_aristas}")
    else:
        print("ℹ️ No hay aristas para exportar")
        df_aristas = None
    
    return df_arbol, df_aristas

def main():
    """
    Función principal
    """
    print("=" * 70)
    print("REDUCCIÓN DE ÁRBOL ENRAIZADO POR PROFUNDIDAD MÁXIMA")
    print("=" * 70)
    
    # CONFIGURACIÓN - MODIFICAR AQUÍ
    CARPETA_ARBOLES = "mst_enraizado"
    BD = "W16C"
    ARCHIVO_GML = f"arbol_enraizado_{BD}_mixto_x10.gml"
    ARCHIVO_CSV = f"arbol_enraizado_{BD}_mixto_x10.csv"
    LIMITE_PROFUNDIDAD = 2
    
    ruta_gml = os.path.join(CARPETA_ARBOLES, ARCHIVO_GML)
    ruta_csv = os.path.join(CARPETA_ARBOLES, ARCHIVO_CSV)
    
    print(f"Configuración:")
    print(f"  Base de datos: {BD}")
    print(f"  Archivo GML: {ARCHIVO_GML}")
    print(f"  Archivo CSV: {ARCHIVO_CSV}")
    print(f"  Límite de profundidad: {LIMITE_PROFUNDIDAD}")
    
    if not os.path.exists(ruta_gml):
        print(f"❌ Error: No se encuentra el archivo {ruta_gml}")
        print("Archivos disponibles en mst_enraizado/:")
        if os.path.exists(CARPETA_ARBOLES):
            for archivo in os.listdir(CARPETA_ARBOLES):
                if archivo.endswith('.gml'):
                    print(f"  - {archivo}")
        return
    
    if not os.path.exists(ruta_csv):
        print(f"⚠️  Advertencia: No se encuentra el archivo CSV {ruta_csv}")
        print("Continuando solo con archivo GML...")
    
    # Cargar árbol enraizado
    arbol, nodo_raiz, nombre_grafo, df_arbol = cargar_arbol_desde_csv(ruta_csv, ruta_gml)
    
    if arbol is None:
        return
    
    # Mostrar información del árbol original
    print(f"\n📊 INFORMACIÓN DEL ÁRBOL ORIGINAL:")
    print(f"   Raíz: {nodo_raiz}")
    profundidades_original = calcular_profundidades(arbol, nodo_raiz)
    print(f"   Profundidad máxima actual: {max(profundidades_original.values())}")
    
    # Mostrar estructura original
    niveles_original = {}
    for nodo, prof in profundidades_original.items():
        if prof not in niveles_original:
            niveles_original[prof] = []
        niveles_original[prof].append(nodo)
    
    print(f"\n🌳 Estructura del árbol original:")
    for nivel in sorted(niveles_original.keys()):
        nodos_nivel = niveles_original[nivel]
        prefijo = "  " * nivel
        print(f"   Nivel {nivel}: {prefijo}{nodos_nivel}")
    
    # Aplicar reducción automática con el límite configurado
    print(f"\n" + "=" * 50)
    print(f" APLICANDO REDUCCIÓN CON PROFUNDIDAD MÁXIMA: {LIMITE_PROFUNDIDAD}")
    print("=" * 50)
    
    # Reducir el árbol
    arbol_reducido = reducir_arbol_por_profundidad(arbol, nodo_raiz, LIMITE_PROFUNDIDAD)
    
    # Analizar el árbol reducido
    profundidades, nodos_eliminados = analizar_arbol_reducido(arbol_reducido, arbol, 
                                                             nodo_raiz, LIMITE_PROFUNDIDAD)
    
    # Visualizar el árbol reducidoF
    visualizar_arbol_reducido(arbol_reducido, nodo_raiz, nombre_grafo, LIMITE_PROFUNDIDAD)
    
    # Exportar resultados
    print(f"\n💾 EXPORTANDO ARCHIVOS:")
    df_arbol_reducido, df_aristas_reducido = exportar_arbol_reducido(
        arbol_reducido, nodo_raiz, nombre_grafo, LIMITE_PROFUNDIDAD)
    
    print(f"\n" + "=" * 70)
    print("✅ PROCESO DE REDUCCIÓN COMPLETADO")
    print("=" * 70)
    print(f"📁 Archivos guardados en carpeta: mst_raiz_reducido/")
    print(f"📏 Límite de profundidad aplicado: {LIMITE_PROFUNDIDAD}")
    print(f"📊 Nodos en árbol reducido: {arbol_reducido.number_of_nodes()}")
    print(f"🔗 Aristas en árbol reducido: {arbol_reducido.number_of_edges()}")

if __name__ == "__main__":
    main()