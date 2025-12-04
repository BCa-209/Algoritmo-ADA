# 1 creando el dataframe
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from alg import df_quartile

np.random.seed(42)

# --- Configuración ---
n_samples = 1000
dim_x = 39
x_cols = [f'x_{i+1}' for i in range(dim_x)]

# --- Generar TODAS las variables como "Raíz" (independientes) ---
X_data = np.random.normal(loc=0.0, scale=1.0, size=(n_samples, dim_x))
df = pd.DataFrame(X_data, columns=x_cols)
L = np.random.normal(loc=0.0, scale=1.0, size=n_samples)

grandparent_vars = ['x_3', 'x_5', 'x_6', 'x_7', 
                    'x_10', 'x_12', 
                    'x_15', 'x_16', 'x_17', 
                    'x_20', 'x_22', 
                    'x_27', 'x_30', 
                    'x_31', 'x_32', 'x_34', 
                    'x_35', 'x_36', 'x_37', 'x_38']

for col in grandparent_vars:
    df[col] = 0.8 * L + 0.6 * np.random.normal(0, 1, n_samples)

# --- Sobrescribir variables (Crear Dependencias) ---
noise_scale = 0.1

# (x9 = x7, x6, x5, x3)
noise_9 = np.random.normal(0, noise_scale, n_samples)
df['x_9'] = 0.5 * df['x_7'] + 0.4 * df['x_6'] - 0.5 * df['x_5'] + 0.6 * df['x_3'] + noise_9

# (x11 = x12, x10)
noise_11 = np.random.normal(0, noise_scale, n_samples)
df['x_11'] = 0.5 * df['x_12'] + 0.6 * df['x_10'] + noise_11

# (x18 = x15, x16, x17)
noise_18 = np.random.normal(0, noise_scale, n_samples)
df['x_18'] = 0.5 * df['x_15'] - 0.4 * df['x_16'] + 0.5 * df['x_17'] + noise_18

# (x21 = x22, x20)
noise_21 = np.random.normal(0, noise_scale, n_samples)
df['x_21'] = 0.7 * df['x_22'] + 0.6 * df['x_20'] + noise_21

# (x24 = x27, x30)
noise_24 = np.random.normal(0, noise_scale, n_samples)
df['x_24'] = 0.5 * df['x_27'] + 0.5 * df['x_30'] + noise_24

# (x33 = x32, x31, x34)
noise_33 = np.random.normal(0, noise_scale, n_samples)
df['x_33'] = 0.6 * df['x_32'] - 0.5 * df['x_31'] + 0.4 * df['x_34'] + noise_33

# (x39 = x35, x36, x37, x38)
noise_39 = np.random.normal(0, noise_scale, n_samples)
df['x_39'] = 0.4 * df['x_35'] + 0.4 * df['x_36'] + 0.5 * df['x_37'] + 0.6 * df['x_38'] + noise_39

# --- Generar el Target Y ---
y_noise = np.random.normal(0, 0.1, n_samples) 

df['target_y'] = (
    3.0 * df['x_39'] +
    2.5 * df['x_33'] -
    2.0 * df['x_24'] + 
    2.0 * df['x_21'] +
    2.5 * df['x_18'] +
    3.0 * df['x_11'] +
    2.0 * df['x_9'] +
    y_noise
)

# --- Transformar todas las columnas a valores positivos ---
print("--- Transformando datos para que sean positivos ---")
for col in df.columns:
    min_val = df[col].min()
    if min_val < 0:
        df[col] = df[col] - min_val 

print(f"El nuevo valor mínimo en todo el DataFrame es: {df.min().min()}")
print("\n")

# --- Mostrar resultados ---
print(f"Forma del DataFrame (filas, columnas): {df.shape}")
print("\nPrimeras 5 filas del conjunto de datos (solo positivos):")
print(df.head())

# --- Verificar correlaciones ---
print("\n--- Correlación de Y con sus 7 'padres' directos ---")
target_corr_7 = df[
    ['x_39', 'x_33', 'x_24', 'x_21', 'x_18', 'x_11', 'x_9', 'target_y']
].corr()
print(target_corr_7['target_y'].sort_values(ascending=False))

# Imprimimos también la correlación completa
print("\n--- Correlación con TODAS las variables (target_y) ---")
target_corr_all = df.corr()
# Ordenamos por valor absoluto para ver las más fuertes (positivas o negativas)
print(target_corr_all['target_y'].abs().sort_values(ascending=False))

# 2 FUNCIÓN df_quartile 
df_quartile(df, 'target_y', porc=0.25, quartile="first", ascending=False)

# 3 creando particiones
B2C = df_quartile(df, 'target_y', porc=0.50, quartile="first", ascending=False)
W2C = df_quartile(df, 'target_y', porc=0.50, quartile="first", ascending=True)
B4C = df_quartile(df, 'target_y', porc=0.25, quartile="first", ascending=False)
W4C = df_quartile(df, 'target_y', porc=0.25, quartile="first", ascending=True)
B8C = df_quartile(df, 'target_y', porc=0.125, quartile="first", ascending=False)
W8C = df_quartile(df, 'target_y', porc=0.125, quartile="first", ascending=True)
B16C = df_quartile(df, 'target_y', porc=0.0625, quartile="first", ascending=False)
W16C = df_quartile(df, 'target_y', porc=0.0625, quartile="first", ascending=True)

W1C = df_quartile(df, 'target_y', porc=0.0625, quartile="first", ascending=True)
W1C = df_quartile(df, 'target_y', porc=0.0625, quartile="first", ascending=True)

# 4 observando las particiones de los subconjuntos 
print("\n" + "="*50)
print("TAMAÑOS DE LAS PARTICIONES:")
print("="*50)
print(f"df original: {df.shape}")
print(f"B2C (50% mayores): {B2C.shape}")
print(f"W2C (50% menores): {W2C.shape}")
print(f"B4C (25% mayores): {B4C.shape}")
print(f"W4C (25% menores): {W4C.shape}")
print(f"B8C (12.5% mayores): {B8C.shape}")
print(f"W8C (12.5% menores): {W8C.shape}")
print(f"B16C (6.25% mayores): {B16C.shape}")
print(f"W16C (6.25% menores): {W16C.shape}")

# 5 Visualización
# Asegurar que cada DataFrame tenga una columna que identifique el grupo al cual pertenece
df_copy = df.copy()
df_copy['Label'] = 'df'
B2C['Label'] = 'B2C'
W2C['Label'] = 'W2C'
B4C['Label'] = 'B4C'
W4C['Label'] = 'W4C'
B8C['Label'] = 'B8C'
W8C['Label'] = 'W8C'
B16C['Label'] = 'B16C'
W16C['Label'] = 'W16C'

# Concatenar todos los DataFrames en un único DataFrame
dataframes = [df_copy, B2C, W2C, B4C, W4C, B8C, W8C, B16C, W16C]
all_data = pd.concat(dataframes)

# Definir un diccionario de colores
colors = {
    'df': '#6C3483',  # purple
    'B2C': '#FF5733', 'W2C': '#FF5733',   # red
    'B4C': '#FFC300', 'W4C': '#FFC300',  # orange
    'B8C': '#52BE80', 'W8C': '#52BE80',  # green
    'B16C': '#3498DB', 'W16C': '#3498DB'  # blue
}

# Configurar el tamaño de la figura
plt.figure(figsize=(18, 6))

# Adicionar cada conjunto de datos al gráfico de densidad
for label, group_data in all_data.groupby('Label'):
    sns.kdeplot(group_data['target_y'], label=label, fill=True, alpha=0.5, color=colors[label])

# Configurar título y etiquetas
plt.title('Densidade de target_y entre df y Subconjuntos')
plt.xlabel('target_y')
plt.ylabel('Densidade')
plt.legend()
plt.show()

# 6 Estadísticas descriptivas de los valores target_y
print("\n" + "="*50)
print("ESTADÍSTICAS DE VALORES 'target_y' POR PARTICIÓN:")
print("="*50)
partitions = {
    'Original': df['target_y'],
    'B2C': B2C['target_y'],
    'W2C': W2C['target_y'],
    'B4C': B4C['target_y'],
    'W4C': W4C['target_y'],
    'B8C': B8C['target_y'],
    'W8C': W8C['target_y'],
    'B16C': B16C['target_y'],
    'W16C': W16C['target_y']
}

for name, partition in partitions.items():
    print(f"{name}:")
    print(f"  Min: {partition.min():.2f}")
    print(f"  Max: {partition.max():.2f}")
    print(f"  Media: {partition.mean():.2f}")
    print(f"  Mediana: {partition.median():.2f}")
    print()

# 7 Discretización del objetivo
# Al discretizar generamos 2 grupos (Clasificación)
B4C_discrete = B4C.copy()
W4C_discrete = W4C.copy()

B4C_discrete['target_y'] = 1  # Clase alta (valores mayores)
W4C_discrete['target_y'] = 0  # Clase baja (valores menores)

dfabc4c = pd.concat([B4C_discrete, W4C_discrete], ignore_index=True)

print("="*50)
print("DATASET DISCRETIZADO (B4C + W4C):")
print("="*50)
print(dfabc4c.head(3))
print(f"\nForma del dataset discretizado: {dfabc4c.shape}")
print(f"Distribucion de clases:")
print(dfabc4c['target_y'].value_counts().sort_index())

# Guardar los DataFrames originales y particionados en CSV
df.to_csv('data/df_original.csv', index=False)
B2C.to_csv('data/B2C.csv', index=False)
W2C.to_csv('data/W2C.csv', index=False)
B4C.to_csv('data/B4C.csv', index=False)
W4C.to_csv('data/W4C.csv', index=False)
B8C.to_csv('data/B8C.csv', index=False)
W8C.to_csv('data/W8C.csv', index=False)
B16C.to_csv('data/B16C.csv', index=False)
W16C.to_csv('data/W16C.csv', index=False)

# Guardar dataset discretizado
dfabc4c.to_csv('data/df_discretizado.csv', index=False)

print("Archivos CSV guardados correctamente.")