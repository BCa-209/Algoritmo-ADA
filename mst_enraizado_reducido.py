# mst_enraizado_reducido.py - VERSIÓN ACTUALIZADA PARA NUEVA BASE DE DATOS
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colormaps
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
import re
from collections import deque


def cargar_y_corregir_gml(ruta_archivo):
    """
    Carga y corrige el archivo GML, manejando IDs numéricos y etiquetas
    """
    try:
        print(f"\nCargando y corrigiendo: {os.path.basename(ruta_archivo)}")
        
        # Leer el archivo completo
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Analizar la estructura del GML
        lineas = contenido.split('\n')
        
        # 1. Encontrar todos los nodos y crear mapeo ID -> Label
        id_a_label = {}
        label_a_id = {}
        
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            
            if 'node [' in linea:
                # Encontrar el nodo
                id_nodo = None
                label_nodo = None
                
                i += 1
                while i < len(lineas) and ']' not in lineas[i]:
                    linea_actual = lineas[i].strip()
                    
                    # Buscar ID
                    if linea_actual.startswith('id'):
                        partes = linea_actual.split()
                        if len(partes) >= 2:
                            try:
                                id_nodo = int(partes[1])
                            except:
                                id_nodo = partes[1]
                    
                    # Buscar label
                    elif 'label' in linea_actual:
                        # Extraer el texto entre comillas
                        match = re.search(r'label\s+"([^"]+)"', linea_actual)
                        if match:
                            label_nodo = match.group(1)
                        else:
                            # Alternativa: extraer manualmente
                            partes = linea_actual.split('"')
                            if len(partes) >= 2:
                                label_nodo = partes[1]
                    
                    i += 1
                
                # Guardar el mapeo
                if id_nodo is not None and label_nodo is not None:
                    id_a_label[str(id_nodo)] = label_nodo
                    label_a_id[label_nodo] = str(id_nodo)
            
            i += 1
        
        print(f"  Encontrados {len(id_a_label)} nodos")
        if id_a_label:
            print(f"  Mapeo ID->Label (primeros 5): {dict(list(id_a_label.items())[:5])}")
        
        # 2. Cargar el grafo con NetworkX
        arbol = nx.read_gml(ruta_archivo)
        
        # 3. Corregir nombres de nodos
        arbol_corregido = nx.DiGraph()
        
        # Nodos corregidos
        for nodo_id_str in arbol.nodes():
            # Obtener la etiqueta real o usar el ID como fallback
            etiqueta_real = id_a_label.get(str(nodo_id_str), str(nodo_id_str))
            arbol_corregido.add_node(etiqueta_real)
            
            # Copiar atributos si existen
            if nodo_id_str in arbol.nodes():
                for attr, valor in arbol.nodes[nodo_id_str].items():
                    arbol_corregido.nodes[etiqueta_real][attr] = valor
        
        # Aristas corregidas
        for u, v, datos in arbol.edges(data=True):
            u_label = id_a_label.get(str(u), str(u))
            v_label = id_a_label.get(str(v), str(v))
            
            arbol_corregido.add_edge(u_label, v_label)
            
            # Copiar todos los atributos de la arista
            for attr, valor in datos.items():
                arbol_corregido[u_label][v_label][attr] = valor
        
        # 4. Verificar que target_y esté presente
        if 'target_y' not in arbol_corregido.nodes():
            print("  ADVERTENCIA: 'target_y' no encontrado en los nodos")
            print(f"  Nodos disponibles: {list(arbol_corregido.nodes())}")
            
            # Buscar si hay algún nodo con 'y' en el nombre
            nodos_y = [n for n in arbol_corregido.nodes() if 'y' in str(n).lower()]
            if nodos_y:
                print(f"  Nodos que contienen 'y': {nodos_y}")
        
        print(f"  Árbol corregido creado con {arbol_corregido.number_of_nodes()} nodos")
        print(f"  y {arbol_corregido.number_of_edges()} aristas")
        
        return arbol_corregido
    
    except Exception as e:
        print(f"ERROR al cargar GML: {e}")
        import traceback
        traceback.print_exc()
        return None

def encontrar_raiz(arbol):
    """
    Encuentra la raíz del árbol (nodo con grado de entrada 0)
    """
    # Primero buscar nodos con grado de entrada 0
    raices = [nodo for nodo in arbol.nodes() if arbol.in_degree(nodo) == 0]
    
    if raices:
        # Si hay múltiples raíces, preferir 'target_y'
        if len(raices) > 1 and 'target_y' in raices:
            return 'target_y'
        return raices[0]
    
    # Si no hay raíces claras, buscar el nodo con menor grado de entrada
    if arbol.number_of_nodes() > 0:
        # Buscar 'target_y' primero
        if 'target_y' in arbol.nodes():
            return 'target_y'
        
        # Si no, usar el primer nodo
        return list(arbol.nodes())[0]
    
    return None

def calcular_profundidades(arbol, nodo_raiz):
    """
    Calcula la profundidad de cada nodo desde la raíz usando BFS
    """
    if nodo_raiz not in arbol:
        print(f"  ERROR: Nodo raíz '{nodo_raiz}' no está en el grafo")
        print(f"  Nodos disponibles: {list(arbol.nodes())[:20]}...")
        return {}
    
    profundidades = {}
    cola = deque([(nodo_raiz, 0)])
    
    while cola:
        nodo_actual, prof_actual = cola.popleft()
        profundidades[nodo_actual] = prof_actual
        
        # Añadir sucesores
        for sucesor in arbol.successors(nodo_actual):
            if sucesor not in profundidades:
                cola.append((sucesor, prof_actual + 1))
    
    # Verificar si todos los nodos fueron alcanzados
    nodos_no_alcanzados = set(arbol.nodes()) - set(profundidades.keys())
    if nodos_no_alcanzados:
        print(f"  ADVERTENCIA: {len(nodos_no_alcanzados)} nodos no alcanzados desde la raíz")
        print(f"  Nodos no alcanzados: {list(nodos_no_alcanzados)[:10]}...")
    
    return profundidades

def reducir_arbol_por_profundidad(arbol, nodo_raiz, profundidad_maxima):
    """
    Reduce el árbol manteniendo solo nodos hasta la profundidad máxima
    """
    if arbol is None or arbol.number_of_nodes() == 0:
        print("  ERROR: Árbol vacío o inválido")
        return nx.DiGraph()
    
    if nodo_raiz not in arbol:
        print(f"  ERROR: Nodo raíz '{nodo_raiz}' no encontrado")
        return nx.DiGraph()
    
    print(f"\n  Reduciendo árbol con profundidad máxima: {profundidad_maxima}")
    
    # Calcular profundidades
    profundidades = calcular_profundidades(arbol, nodo_raiz)
    
    if not profundidades:
        print("  ERROR: No se pudieron calcular profundidades")
        return nx.DiGraph()
    
    # Filtrar nodos por profundidad
    nodos_a_mantener = [n for n, p in profundidades.items() if p <= profundidad_maxima]
    
    print(f"  Nodos a mantener (prof <= {profundidad_maxima}): {len(nodos_a_mantener)}/{len(arbol.nodes())}")
    
    # Crear subgrafo
    arbol_reducido = nx.DiGraph()
    
    # Añadir nodos
    for nodo in nodos_a_mantener:
        arbol_reducido.add_node(nodo)
        # Copiar atributos
        for attr, valor in arbol.nodes[nodo].items():
            arbol_reducido.nodes[nodo][attr] = valor
    
    # Añadir aristas entre nodos mantenidos
    for u, v, datos in arbol.edges(data=True):
        if u in nodos_a_mantener and v in nodos_a_mantener:
            arbol_reducido.add_edge(u, v)
            # Copiar atributos de aristas
            for attr, valor in datos.items():
                arbol_reducido[u][v][attr] = valor
    
    print(f"  Árbol reducido creado: {arbol_reducido.number_of_nodes()} nodos, {arbol_reducido.number_of_edges()} aristas")
    
    return arbol_reducido

def mostrar_estructura_arbol(arbol, nodo_raiz):
    """
    Muestra la estructura completa del árbol de forma jerárquica
    """
    print("\n" + "=" * 60)
    print("ESTRUCTURA JERÁRQUICA DEL ÁRBOL")
    print("=" * 60)
    
    profundidades = calcular_profundidades(arbol, nodo_raiz)
    
    # Agrupar nodos por nivel
    niveles = {}
    for nodo, prof in profundidades.items():
        if prof not in niveles:
            niveles[prof] = []
        niveles[prof].append(nodo)
    
    # Mostrar por niveles
    print(f"\nRaíz: {nodo_raiz}")
    for nivel in sorted(niveles.keys()):
        print(f"\nNivel {nivel}:")
        for nodo in sorted(niveles[nivel]):
            # Encontrar padre
            padres = list(arbol.predecessors(nodo))
            padre_str = f"← {padres[0]}" if padres else "(raíz)"
            
            # Encontrar hijos
            hijos = list(arbol.successors(nodo))
            hijos_str = f"→ {hijos}" if hijos else "(hoja)"
            
            print(f"  {nodo} {padre_str} {hijos_str}")
    
    # Mostrar resumen
    print(f"\nRESUMEN:")
    print(f"  Nodos totales: {arbol.number_of_nodes()}")
    print(f"  Aristas totales: {arbol.number_of_edges()}")
    print(f"  Profundidad máxima: {max(profundidades.values())}")
    
    # Distribución por niveles
    print(f"\nDISTRIBUCIÓN POR NIVELES:")
    for nivel in sorted(niveles.keys()):
        print(f"  Nivel {nivel}: {len(niveles[nivel])} nodos")

def visualizar_arbol(arbol, nodo_raiz, nombre_grafo, profundidad_maxima, carpeta_salida="mst_raiz_reducido"):
    """
    Visualiza el árbol de forma jerárquica
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    if arbol.number_of_nodes() == 0:
        print("  No hay nodos para visualizar")
        return
    
    plt.figure(figsize=(16, 10))
    
    # Calcular profundidades para colorear
    profundidades = calcular_profundidades(arbol, nodo_raiz)
    
    # Crear layout jerárquico
    pos = {}
    niveles = {}
    
    for nodo, prof in profundidades.items():
        if prof not in niveles:
            niveles[prof] = []
        niveles[prof].append(nodo)
    
    # Posicionar nodos por niveles
    max_nivel = max(niveles.keys()) if niveles else 0
    for nivel, nodos_nivel in niveles.items():
        y_pos = 1.0 - (nivel / (max_nivel + 1))
        num_nodos = len(nodos_nivel)
        
        for i, nodo in enumerate(sorted(nodos_nivel)):
            x_pos = (i + 1) / (num_nodos + 1)
            pos[nodo] = (x_pos, y_pos)
    
    # Colores por profundidad
    colores_nodos = [profundidades.get(nodo, 0) for nodo in arbol.nodes()]
    
    # Dibujar
    nx.draw_networkx_nodes(arbol, pos,
                          node_size=800,
                          node_color=colores_nodos,
                          cmap=plt.get_cmap('viridis'),
                          alpha=0.8,
                          edgecolors='black')
    
    nx.draw_networkx_edges(arbol, pos,
                          arrowstyle='->',
                          arrowsize=15,
                          edge_color='gray',
                          width=1.2,
                          alpha=0.7)
    
    # Etiquetas de nodos
    nx.draw_networkx_labels(arbol, pos, font_size=9, font_weight='bold')
    
    # Etiquetas de aristas (pesos)
    edge_labels = {}
    for u, v in arbol.edges():
        if 'weight' in arbol[u][v]:
            peso = arbol[u][v]['weight']
            edge_labels[(u, v)] = f"{peso:.3f}"
    
    if edge_labels:
        nx.draw_networkx_edge_labels(arbol, pos, edge_labels=edge_labels, font_size=7)
    
    # Resaltar raíz
    nx.draw_networkx_nodes(arbol, pos,
                          nodelist=[nodo_raiz],
                          node_size=1000,
                          node_color='red',
                          alpha=0.9)
    
    # Título
    plt.title(f'Árbol Reducido - {nombre_grafo}\n'
              f'Raíz: {nodo_raiz} | Prof. máxima: {profundidad_maxima} | '
              f'Nodos: {arbol.number_of_nodes()} | Aristas: {arbol.number_of_edges()}',
              fontsize=12, fontweight='bold')
    
    plt.axis('off')
    plt.tight_layout()
    
    # Guardar
    nombre_archivo = f"arbol_reducido_{nombre_grafo}_prof{profundidad_maxima}.png"
    ruta_completa = os.path.join(carpeta_salida, nombre_archivo)
    plt.savefig(ruta_completa, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"  Visualización guardada: {ruta_completa}")

def exportar_resultados(arbol, nodo_raiz, nombre_grafo, profundidad_maxima, carpeta_salida="mst_raiz_reducido"):
    """
    Exporta el árbol reducido a CSV y GML
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # 1. Exportar a GML
    ruta_gml = os.path.join(carpeta_salida, f"arbol_reducido_{nombre_grafo}_prof{profundidad_maxima}.gml")
    
    # Asegurar que todos los nodos tengan label
    for nodo in arbol.nodes():
        if 'label' not in arbol.nodes[nodo]:
            arbol.nodes[nodo]['label'] = str(nodo)
    
    nx.write_gml(arbol, ruta_gml)
    print(f"✓ GML guardado: {ruta_gml}")
    
    # 2. Exportar estructura a CSV
    datos_nodos = []
    profundidades = calcular_profundidades(arbol, nodo_raiz)
    
    for nodo in arbol.nodes():
        datos_nodos.append({
            'nodo': nodo,
            'profundidad': profundidades.get(nodo, -1),
            'es_raiz': nodo == nodo_raiz,
            'es_hoja': arbol.out_degree(nodo) == 0,
            'grado_entrada': arbol.in_degree(nodo),
            'grado_salida': arbol.out_degree(nodo),
            'padre': list(arbol.predecessors(nodo))[0] if list(arbol.predecessors(nodo)) else '',
            'hijos': ', '.join(list(arbol.successors(nodo))) if list(arbol.successors(nodo)) else ''
        })
    
    df_nodos = pd.DataFrame(datos_nodos)
    ruta_csv_nodos = os.path.join(carpeta_salida, f"nodos_reducido_{nombre_grafo}_prof{profundidad_maxima}.csv")
    df_nodos.to_csv(ruta_csv_nodos, index=False, encoding='utf-8')
    print(f"✓ CSV de nodos guardado: {ruta_csv_nodos}")
    
    # 3. Exportar aristas a CSV
    datos_aristas = []
    for u, v, datos in arbol.edges(data=True):
        datos_aristas.append({
            'desde': u,
            'hacia': v,
            'peso': datos.get('weight', ''),
            'distancia': datos.get('distance', ''),
            'direccion': datos.get('direccion', f"{u} → {v}")
        })
    
    if datos_aristas:
        df_aristas = pd.DataFrame(datos_aristas)
        ruta_csv_aristas = os.path.join(carpeta_salida, f"aristas_reducido_{nombre_grafo}_prof{profundidad_maxima}.csv")
        df_aristas.to_csv(ruta_csv_aristas, index=False, encoding='utf-8')
        print(f"✓ CSV de aristas guardado: {ruta_csv_aristas}")
    
    return df_nodos

def procesar_base_datos(nombre_bd, limite_profundidad=2):
    """
    Procesa una base de datos específica
    """
    print("\n" + "=" * 70)
    print(f"PROCESANDO: {nombre_bd}")
    print("=" * 70)
    
    # Rutas de archivos
    carpeta_arboles = "mst_enraizado"
    archivo_gml = f"arbol_enraizado_{nombre_bd}_directa_target_y.gml"
    archivo_csv = f"arbol_enraizado_{nombre_bd}_directa_target_y.csv"
    
    ruta_gml = os.path.join(carpeta_arboles, archivo_gml)
    ruta_csv = os.path.join(carpeta_arboles, archivo_csv)
    
    # Verificar que exista el archivo
    if not os.path.exists(ruta_gml):
        print(f"ERROR: No se encuentra {ruta_gml}")
        
        # Mostrar archivos disponibles
        if os.path.exists(carpeta_arboles):
            print(f"\nArchivos disponibles en {carpeta_arboles}/:")
            archivos_gml = [f for f in os.listdir(carpeta_arboles) if f.endswith('.gml')]
            for archivo in archivos_gml:
                print(f"  - {archivo}")
        
        return None
    
    # 1. Cargar y corregir el GML
    arbol = cargar_y_corregir_gml(ruta_gml)
    
    if arbol is None:
        print(f"ERROR: No se pudo cargar el árbol para {nombre_bd}")
        return None
    
    # 2. Encontrar la raíz
    nodo_raiz = encontrar_raiz(arbol)
    print(f"\n  Raíz identificada: {nodo_raiz}")
    
    # 3. Mostrar estructura original
    mostrar_estructura_arbol(arbol, nodo_raiz)
    
    # 4. Reducir el árbol
    arbol_reducido = reducir_arbol_por_profundidad(arbol, nodo_raiz, limite_profundidad)
    
    if arbol_reducido.number_of_nodes() == 0:
        print(f"  ERROR: Árbol reducido vacío para {nombre_bd}")
        return None
    
    # 5. Visualizar
    visualizar_arbol(arbol_reducido, nodo_raiz, nombre_bd, limite_profundidad)
    
    # 6. Exportar resultados
    df_resultados = exportar_resultados(arbol_reducido, nodo_raiz, nombre_bd, limite_profundidad)
    
    print(f"\n✓ Procesamiento completado para {nombre_bd}")
    
    return df_resultados

def main():
    """
    Función principal - Procesa múltiples bases de datos
    """
    print("=" * 80)
    print("REDUCCIÓN DE ÁRBOLES ENRAIZADOS POR PROFUNDIDAD")
    print("BASE DE DATOS: x_1 a x_39 con target_y")
    print("=" * 80)
    
    # CONFIGURACIÓN
    LIMITE_PROFUNDIDAD = 1  # Niveles a mantener desde la raíz
    
    # Lista de bases de datos a procesar
    bases_datos = [
        "B2C", "W2C",
        "B4C", "W4C", 
        "B8C", "W8C",
        "B16C", "W16C"
    ]
    
    # O procesar solo una
    # bases_datos = ["B2C"]
    
    resultados = {}
    
    for bd in bases_datos:
        print(f"\n{'='*40}")
        print(f"INICIANDO PROCESAMIENTO DE: {bd}")
        print(f"{'='*40}")
        
        resultado = procesar_base_datos(bd, LIMITE_PROFUNDIDAD)
        
        if resultado is not None:
            resultados[bd] = resultado
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 80)
    
    for bd, df in resultados.items():
        if df is not None:
            print(f"\n{bd}:")
            print(f"  Nodos: {len(df)}")
            print(f"  Niveles: {df['profundidad'].max() + 1}")
            print(f"  Hojas: {df['es_hoja'].sum()}")
    
    print(f"\nProcesamiento completado para {len(resultados)} bases de datos")

if __name__ == "__main__":
    main()