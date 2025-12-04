# unificar_simple_separado.py
import pandas as pd
import os
import glob

def unificar_y_intersectar_simple():
    """
    Versión simple que hace exactamente lo que necesitas
    """
    print("🔄 UNIFICANDO VARIABLES EN LISTAS SEPARADAS")
    
    # 1. Unificar variables CON raíz
    print("\n1. Unificando variables CON raíz...")
    variables_con_raiz = set()
    archivos_con_raiz = glob.glob("resultados_intersecciones/*Lista_Con_Raiz.csv")
    
    for archivo in archivos_con_raiz:
        df = pd.read_csv(archivo)
        if 'variables' in df.columns:
            variables_con_raiz.update(df['variables'].dropna().unique())
    
    # 2. Unificar variables SIN raíz
    print("2. Unificando variables SIN raíz...")
    variables_sin_raiz = set()
    
    for carpeta in os.listdir("resultados_comparacion"):
        if carpeta.startswith('analisis_'):
            archivo = f"resultados_comparacion/{carpeta}/nodos_con_diferencias.csv"
            if os.path.exists(archivo):
                df = pd.read_csv(archivo)
                if 'nodo_con_diferencias' in df.columns:
                    variables_sin_raiz.update(df['nodo_con_diferencias'].dropna().unique())
    
    # 3. Calcular intersección
    print("3. Calculando intersección...")
    interseccion = variables_con_raiz.intersection(variables_sin_raiz)
    
    # 4. Guardar las tres listas
    os.makedirs("resultados_unificados", exist_ok=True)
    
    # Lista 1: Variables CON raíz
    pd.DataFrame(sorted(variables_con_raiz), columns=['variables']).to_csv(
        "resultados_unificados/variables_con_raiz.csv", index=False)
    
    # Lista 2: Variables SIN raíz
    pd.DataFrame(sorted(variables_sin_raiz), columns=['variables']).to_csv(
        "resultados_unificados/variables_sin_raiz.csv", index=False)
    
    # Lista 3: Intersección
    pd.DataFrame(sorted(interseccion), columns=['variables']).to_csv(
        "resultados_unificados/interseccion_variables.csv", index=False)
    
    # 5. Mostrar resultados
    print(f"\n{'='*50}")
    print("📊 RESULTADOS FINALES")
    print(f"{'='*50}")
    print(f"🔸 Variables CON raíz: {len(variables_con_raiz)}")
    print(f"🔸 Variables SIN raíz: {len(variables_sin_raiz)}")
    print(f"🔸 Intersección: {len(interseccion)}")
    
    if interseccion:
        print(f"🔸 Variables comunes: {sorted(interseccion)}")
    
    print(f"\n💾 Archivos guardados:")
    print(f"   - variables_con_raiz.csv")
    print(f"   - variables_sin_raiz.csv")
    print(f"   - interseccion_variables.csv")

if __name__ == "__main__":
    unificar_y_intersectar_simple()