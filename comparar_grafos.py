import networkx as nx
import pandas as pd
import os
from datetime import datetime
import csv

# Función para crear carpeta de resultados con nombre personalizado
def crear_carpeta_resultados(QRTL, tipo_grafo1, tipo_grafo2):
    carpeta_base = "resultados_comparacion"
    nombre_carpeta = f"analisis_B{QRTL}C_W{QRTL}C"
    carpeta_resultados = os.path.join(carpeta_base, nombre_carpeta)
    os.makedirs(carpeta_resultados, exist_ok=True)
    return carpeta_resultados

# Función para cargar el grafo desde un archivo .gml
def cargar_grafo(file_path):
    return nx.read_gml(file_path)

# Función para comparar las estructuras de nodos entre dos grafos, considerando distancias topológicas
def comparar_estructuras_con_distancia(grafo1, grafo2):
    # Obtener nodos y sus vecinos de ambos grafos
    nodos_grafo1 = set(grafo1.nodes())
    nodos_grafo2 = set(grafo2.nodes())
    
    diferencias = set()
    detalles_diferencias = []

    # 1. Comparar nodos que están en ambos grafos
    nodos_comunes = nodos_grafo1.intersection(nodos_grafo2)
    for nodo in nodos_comunes:
        try:
            # Calcular las distancias más cortas a todos los vecinos en cada grafo
            distancias_grafo1 = nx.single_source_shortest_path_length(grafo1, nodo)
            distancias_grafo2 = nx.single_source_shortest_path_length(grafo2, nodo)

            # Comprobar si las distancias a los vecinos no son las mismas
            for vecino in set(distancias_grafo1.keys()).union(set(distancias_grafo2.keys())):
                distancia_grafo1 = distancias_grafo1.get(vecino, float('inf'))
                distancia_grafo2 = distancias_grafo2.get(vecino, float('inf'))

                # Si las distancias no coinciden, agregamos el nodo a las diferencias
                if distancia_grafo1 != distancia_grafo2:
                    diferencias.add(nodo)
                    detalles_diferencias.append({
                        'nodo': nodo,
                        'vecino': vecino,
                        'distancia_grafo1': distancia_grafo1,
                        'distancia_grafo2': distancia_grafo2,
                        'tipo_diferencia': 'distancia_topologica',
                        'descripcion': f'Distancia de {nodo} a {vecino}: {distancia_grafo1} vs {distancia_grafo2}'
                    })
        except Exception as e:
            print(f"Error calculando distancias para nodo {nodo}: {e}")

    # 2. Comparar nodos que están solo en grafo1
    nodos_solo_grafo1 = nodos_grafo1 - nodos_grafo2
    for nodo in nodos_solo_grafo1:
        diferencias.add(nodo)
        detalles_diferencias.append({
            'nodo': nodo,
            'vecino': 'N/A',
            'distancia_grafo1': 'Presente',
            'distancia_grafo2': 'Ausente',
            'tipo_diferencia': 'nodo_faltante',
            'descripcion': f'Nodo {nodo} solo existe en Grafo 1'
        })

    # 3. Comparar nodos que están solo en grafo2
    nodos_solo_grafo2 = nodos_grafo2 - nodos_grafo1
    for nodo in nodos_solo_grafo2:
        diferencias.add(nodo)
        detalles_diferencias.append({
            'nodo': nodo,
            'vecino': 'N/A',
            'distancia_grafo1': 'Ausente',
            'distancia_grafo2': 'Presente',
            'tipo_diferencia': 'nodo_extra',
            'descripcion': f'Nodo {nodo} solo existe en Grafo 2'
        })

    return diferencias, detalles_diferencias

# Función para guardar resultados en CSV
def guardar_resultados_csv(diferencias, detalles_diferencias, grafo1, grafo2, archivo1, archivo2, carpeta_resultados, QRTL):
    """Guarda todos los resultados en archivos CSV organizados"""
    
    # 1. Guardar resumen general
    resumen_general = {
        'archivo_grafo1': archivo1,
        'archivo_grafo2': archivo2,
        'QRTL': QRTL,
        'total_nodos_grafo1': grafo1.number_of_nodes(),
        'total_nodos_grafo2': grafo2.number_of_nodes(),
        'total_aristas_grafo1': grafo1.number_of_edges(),
        'total_aristas_grafo2': grafo2.number_of_edges(),
        'nodos_con_diferencias': len(diferencias),
        'total_diferencias_detectadas': len(detalles_diferencias),
        'fecha_analisis': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    df_resumen = pd.DataFrame([resumen_general])
    archivo_resumen = os.path.join(carpeta_resultados, "resumen_general.csv")
    df_resumen.to_csv(archivo_resumen, index=False)
    
    # 2. Guardar lista de nodos con diferencias
    if diferencias:
        df_nodos_diferencias = pd.DataFrame(list(diferencias), columns=['nodo_con_diferencias'])
        archivo_nodos = os.path.join(carpeta_resultados, "nodos_con_diferencias.csv")
        df_nodos_diferencias.to_csv(archivo_nodos, index=False)
    
    # 3. Guardar detalles de las diferencias
    if detalles_diferencias:
        df_detalles = pd.DataFrame(detalles_diferencias)
        archivo_detalles = os.path.join(carpeta_resultados, "detalles_diferencias.csv")
        df_detalles.to_csv(archivo_detalles, index=False)
    
    # 4. Guardar estadísticas por tipo de diferencia
    if detalles_diferencias:
        stats_tipo = pd.DataFrame(detalles_diferencias)['tipo_diferencia'].value_counts().reset_index()
        stats_tipo.columns = ['tipo_diferencia', 'cantidad']
        archivo_stats = os.path.join(carpeta_resultados, "estadisticas_tipos_diferencias.csv")
        stats_tipo.to_csv(archivo_stats, index=False)
    
    return len(detalles_diferencias)

# Función para generar reporte de comparación
def generar_reporte_comparacion(grafo1, grafo2, archivo1, archivo2, QRTL):
    """Genera un reporte comparativo básico entre los dos grafos"""
    
    reporte = {
        'Metrica': [
            'QRTL',
            'Total de nodos',
            'Total de aristas', 
            'Densidad',
            'Grado promedio',
            'Diámetro (si es conexo)',
            'Componentes conexas'
        ],
        'Grafo_1': [
            QRTL,
            grafo1.number_of_nodes(),
            grafo1.number_of_edges(),
            nx.density(grafo1),
            sum(dict(grafo1.degree()).values()) / grafo1.number_of_nodes() if grafo1.number_of_nodes() > 0 else 0,
            nx.diameter(grafo1) if nx.is_connected(grafo1) else 'No conexo',
            nx.number_connected_components(grafo1) if not grafo1.is_directed() else 'N/A'
        ],
        'Grafo_2': [
            QRTL,
            grafo2.number_of_nodes(),
            grafo2.number_of_edges(),
            nx.density(grafo2),
            sum(dict(grafo2.degree()).values()) / grafo2.number_of_nodes() if grafo2.number_of_nodes() > 0 else 0,
            nx.diameter(grafo2) if nx.is_connected(grafo2) else 'No conexo',
            nx.number_connected_components(grafo2) if not grafo2.is_directed() else 'N/A'
        ]
    }
    
    return pd.DataFrame(reporte)

# Función principal para un QRTL específico
def analizar_par_grafos(QRTL, tipo_grafo1, tipo_grafo2):
    """Analiza un par específico de grafos para un QRTL dado"""
    
    # Construir rutas de archivos
    archivo_grafo1 = f'arbol_objetivo_resultados/arbol_objetivo_{tipo_grafo1}{QRTL}C_directa.gml'
    archivo_grafo2 = f'arbol_objetivo_resultados/arbol_objetivo_{tipo_grafo2}{QRTL}C_directa.gml'

    # Crear carpeta de resultados con nombre personalizado
    carpeta_resultados = crear_carpeta_resultados(QRTL, tipo_grafo1, tipo_grafo2)
    
    try:
        # Cargar los grafos desde los archivos
        print(f"\n=== ANALIZANDO QRTL {QRTL} ===")
        print("Cargando grafos...")
        grafo1 = cargar_grafo(archivo_grafo1)
        grafo2 = cargar_grafo(archivo_grafo2)
        
        print(f"Grafo 1 cargado: {archivo_grafo1}")
        print(f"Grafo 2 cargado: {archivo_grafo2}")
        
        # Comparar las estructuras de los grafos, considerando distancias topológicas
        print("Comparando estructuras...")
        diferencias, detalles_diferencias = comparar_estructuras_con_distancia(grafo1, grafo2)
        
        # Guardar resultados en CSV
        print("Guardando resultados...")
        total_diferencias = guardar_resultados_csv(
            diferencias, detalles_diferencias, grafo1, grafo2,
            os.path.basename(archivo_grafo1), os.path.basename(archivo_grafo2),
            carpeta_resultados, QRTL
        )
        
        # Generar y guardar reporte comparativo
        reporte_comparativo = generar_reporte_comparacion(grafo1, grafo2, archivo_grafo1, archivo_grafo2, QRTL)
        archivo_reporte = os.path.join(carpeta_resultados, "reporte_comparativo.csv")
        reporte_comparativo.to_csv(archivo_reporte, index=False)
        
        # Mostrar resumen en consola
        print(f"\n=== RESULTADOS PARA QRTL {QRTL} ===")
        print(f"Archivos analizados:")
        print(f"  - Grafo 1: {os.path.basename(archivo_grafo1)}")
        print(f"  - Grafo 2: {os.path.basename(archivo_grafo2)}")
        print(f"Nodos con diferencias estructurales: {len(diferencias)}")
        print(f"Total de diferencias detectadas: {total_diferencias}")
        print(f"Resultados guardados en: {carpeta_resultados}")
        
        if diferencias:
            print(f"Primeros 10 nodos con diferencias: {list(diferencias)[:10]}")
        else:
            print("¡No se encontraron diferencias estructurales entre los grafos!")
            
        return {
            'QRTL': QRTL,
            'tipo_grafo1': tipo_grafo1,
            'tipo_grafo2': tipo_grafo2,
            'nodos_con_diferencias': len(diferencias),
            'total_diferencias': total_diferencias,
            'carpeta_resultados': carpeta_resultados
        }
            
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar el archivo {e.filename}")
        print("Verifica que las rutas de los archivos .gml sean correctas")
        return None
    except Exception as e:
        print(f"Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return None

# Función para analizar múltiples QRTL
def analizar_multiples_QRTL(QRTLs, tipo_grafo1, tipo_grafo2):
    """Analiza múltiples valores de QRTL para los mismos tipos de grafos"""
    
    resultados_totales = []
    
    for qrtl in QRTLs:
        resultado = analizar_par_grafos(qrtl, tipo_grafo1, tipo_grafo2)
        if resultado:
            resultados_totales.append(resultado)
    
    # Guardar resumen de todos los análisis
    if resultados_totales:
        df_resumen_total = pd.DataFrame(resultados_totales)
        carpeta_base = "resultados_comparacion"
        archivo_resumen_total = os.path.join(carpeta_base, f"resumen_completo_{tipo_grafo1}_{tipo_grafo2}.csv")
        df_resumen_total.to_csv(archivo_resumen_total, index=False)
        print(f"\n=== RESUMEN COMPLETO GUARDADO EN: {archivo_resumen_total} ===")
        print(df_resumen_total.to_string(index=False))

def main():
    """Función principal - Ejemplo de uso"""
    
    # CONFIGURACIÓN - Modifica estos valores según necesites
    
    # Opción 1: Analizar un solo par de grafos
    QRTL = 2  # 2, 4, 8, 16
    tipo_grafo1 = "B"  # B, W, etc.
    tipo_grafo2 = "W"  # B, W, etc.
    
    
    # Opción 2: Analizar múltiples QRTL (descomenta para usar)
    QRTLs = [2, 4, 8, 16]
    analizar_multiples_QRTL(QRTLs, tipo_grafo1, tipo_grafo2)    # multiple
    #analizar_par_grafos(QRTL, tipo_grafo1, tipo_grafo2)        # un par

if __name__ == "__main__":
    main()