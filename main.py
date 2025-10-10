# 1 creando el dataframe
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from alg import df_quartile

# Set a seed for reproducibility
np.random.seed(42)
# Generate 10000 rows
n_rows = 10000

# Generate heterogeneous data for x1 to x10
data = {}
for i in range(1, 11):
    col_name = f'x{i}'
    # Vary data types
    if i % 3 == 0:
        data[col_name] = np.random.rand(n_rows)  # float
    elif i % 3 == 1:
        data[col_name] = np.random.randint(0, 100, n_rows) # int
    else:
        data[col_name] = np.random.choice(['A', 'B', 'C', 'D', 'E'], n_rows) # string/categorical

# Generate a numeric 'y' column with a normal distribution, scaled and shifted
# Mean will be the center of the range, std dev will be roughly 1/6 of the range
mean_y = (1500 + 75000) / 2
std_y = (75000 - 1500) / 6  # Using the 68-95-99.7 rule for approximation
data['y'] = np.random.randn(n_rows) * std_y + mean_y

# Create the DataFrame
df = pd.DataFrame(data)

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
df.to_csv('df_original.csv', index=False)
B2C.to_csv('B2C.csv', index=False)
W2C.to_csv('W2C.csv', index=False)
B4C.to_csv('B4C.csv', index=False)
W4C.to_csv('W4C.csv', index=False)
B8C.to_csv('B8C.csv', index=False)
W8C.to_csv('W8C.csv', index=False)
B16C.to_csv('B16C.csv', index=False)
W16C.to_csv('W16C.csv', index=False)

# Guardar dataset discretizado
dfabc4c.to_csv('df_discretizado.csv', index=False)

print("Archivos CSV guardados correctamente.")
