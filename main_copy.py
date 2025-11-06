# 1 creando el dataframe
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from alg import df_quartile

# Set a seed for reproducibility
np.random.seed(42)
n_rows = 10000

# Generate heterogeneous data with specified relationships and correlations
data = {}
data['x1'] = np.random.rand(n_rows) * 100
data['x2'] = np.random.rand(n_rows) * 100
data['x5'] = np.random.rand(n_rows) * 100
data['x7'] = np.random.rand(n_rows) * 100

# Variables with specific relationships and noise
x6 = np.random.rand(n_rows) * 0.1 + 0.9 * np.sin(np.arange(n_rows) / 500)
x9 = np.random.rand(n_rows) * 0.1 + 0.9 * np.sin(np.arange(n_rows) / 500)
x4 = np.random.randint(0, 100, n_rows)
x8 = np.random.rand(n_rows) * 100

# Introduce correlations for x3, x6, x9
cov_matrix_x3_x6_x9 = [[1, 0.75, 0.75],
                    [0.75, 1, 0.75],
                    [0.75, 0.75, 1]]
correlated_x3_x6_x9 = np.random.multivariate_normal([0, 0, 0], cov_matrix_x3_x6_x9, n_rows)
data['x3'] = correlated_x3_x6_x9[:, 0] * np.std(x6) + np.mean(x6)
data['x6'] = correlated_x3_x6_x9[:, 1] * np.std(x6) + np.mean(x6)
data['x9'] = correlated_x3_x6_x9[:, 2] * np.std(x9) + np.mean(x9)

# Introduce correlations for x10, x4, x6, x8
cov_matrix_x10_x4_x6_x8 = [[1, 0.85, 0.85, 0.85],
                        [0.85, 1, 0.85, 0.85],
                        [0.85, 0.85, 1, 0.85],
                        [0.85, 0.85, 0.85, 1]]
correlated_x10_x4_x6_x8 = np.random.multivariate_normal([0, 0, 0, 0], cov_matrix_x10_x4_x6_x8, n_rows)
data['x10'] = correlated_x10_x4_x6_x8[:, 0]
data['x4'] = correlated_x10_x4_x6_x8[:, 1] * np.std(x4) + np.mean(x4)
data['x6'] = correlated_x10_x4_x6_x8[:, 2] * np.std(x6) + np.mean(x6)
data['x8'] = correlated_x10_x4_x6_x8[:, 3] * np.std(x8) + np.mean(x8)

# Create the DataFrame
df = pd.DataFrame(data)

# ==========================================
# Crear la variable y = x3 * x10 
# Con distribución gaussiana
# ==========================================

# Calcular el producto base
y_base = df['x3'] * df['x10']

# Normalizar a media 0 y desviación estándar 1
y_normalized = (y_base - y_base.mean()) / y_base.std()

# Añadir ruido gaussiano para mejorar la distribución normal
ruido_gaussiano = np.random.normal(0, 0.1, n_rows)  # Media 0, std pequeña
y = y_normalized + ruido_gaussiano



# Añadir la variable a la dataframe
df['y'] = y

# Display the first few rows and info to verify
print("DataFrame creado:")
print(df.head())
print("\nInformación del DataFrame:")
print(df.info())

# 2 FUNCIÓN df_quartile 
df_quartile(df, 'y', porc=0.25, quartile="first", ascending=False)

# 3 creando particiones
B2C = df_quartile(df, 'y', porc=0.50, quartile="first", ascending=False)
W2C = df_quartile(df, 'y', porc=0.50, quartile="first", ascending=True)
B4C = df_quartile(df, 'y', porc=0.25, quartile="first", ascending=False)
W4C = df_quartile(df, 'y', porc=0.25, quartile="first", ascending=True)
B8C = df_quartile(df, 'y', porc=0.125, quartile="first", ascending=False)
W8C = df_quartile(df, 'y', porc=0.125, quartile="first", ascending=True)
B16C = df_quartile(df, 'y', porc=0.0625, quartile="first", ascending=False)
W16C = df_quartile(df, 'y', porc=0.0625, quartile="first", ascending=True)

W1C = df_quartile(df, 'y', porc=0.0625, quartile="first", ascending=True)
W1C = df_quartile(df, 'y', porc=0.0625, quartile="first", ascending=True)


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
    sns.kdeplot(group_data['y'], label=label, fill=True, alpha=0.5, color=colors[label])

# Configurar título y etiquetas
plt.title('Densidade de y entre df y Subconjuntos')
plt.xlabel('y')
plt.ylabel('Densidade')
plt.legend()
plt.show()

# 6 Estadísticas descriptivas de los valores y
print("\n" + "="*50)
print("ESTADÍSTICAS DE VALORES 'y' POR PARTICIÓN:")
print("="*50)
partitions = {
    'Original': df['y'],
    'B2C': B2C['y'],
    'W2C': W2C['y'],
    'B4C': B4C['y'],
    'W4C': W4C['y'],
    'B8C': B8C['y'],
    'W8C': W8C['y'],
    'B16C': B16C['y'],
    'W16C': W16C['y']
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

B4C_discrete['y'] = 1  # Clase alta (valores mayores)
W4C_discrete['y'] = 0  # Clase baja (valores menores)

dfabc4c = pd.concat([B4C_discrete, W4C_discrete], ignore_index=True)

print("="*50)
print("DATASET DISCRETIZADO (B4C + W4C):")
print("="*50)
print(dfabc4c.head(3))
print(f"\nForma del dataset discretizado: {dfabc4c.shape}")
print(f"Distribucion de clases:")
print(dfabc4c['y'].value_counts().sort_index())

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
