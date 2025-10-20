import pandas as pd

# Definir dataframes como variable global al nivel del módulo
dataframes = {}

# Código de carga que se ejecuta cuando se importa el módulo
def cargar_datasets():
    global dataframes
    
    # Cargar los diferentes CSV
    try:
        df_copy = pd.read_csv('data/df_original.csv')
        B2C = pd.read_csv('data/B2C.csv')
        W2C = pd.read_csv('data/W2C.csv')
        B4C = pd.read_csv('data/B4C.csv')
        W4C = pd.read_csv('data/W4C.csv')
        B8C = pd.read_csv('data/B8C.csv')
        W8C = pd.read_csv('data/W8C.csv')
        B16C = pd.read_csv('data/B16C.csv')
        W16C = pd.read_csv('data/W16C.csv')
        
        # Asignar etiquetas a cada DataFrame
        df_copy['Label'] = 'df'
        B2C['Label'] = 'B2C'
        W2C['Label'] = 'W2C'
        B4C['Label'] = 'B4C'
        W4C['Label'] = 'W4C'
        B8C['Label'] = 'B8C'
        W8C['Label'] = 'W8C'
        B16C['Label'] = 'B16C'
        W16C['Label'] = 'W16C'
        
        # Diccionario para procesar cada DataFrame
        dataframes = {
            'df_original': df_copy,
            'B2C': B2C,
            'W2C': W2C,
            'B4C': B4C,
            'W4C': W4C,
            'B8C': B8C,
            'W8C': W8C,
            'B16C': B16C,
            'W16C': W16C
        }
        
        print("Datasets cargados exitosamente:")
        for nombre, df in dataframes.items():
            print(f"   {nombre}: {df.shape}")
            
    except FileNotFoundError as e:
        print(f"Error: No se encontraron los archivos CSV. Ejecuta primero main.py")
        print(f"Detalle: {e}")
    except Exception as e:
        print(f"Error cargando datasets: {e}")

# Cargar datasets automáticamente cuando se importe el módulo
cargar_datasets()

if __name__ == "__main__":
    # Código adicional si se ejecuta este archivo directamente
    print("Ejecutando analizar_datasets.py directamente")