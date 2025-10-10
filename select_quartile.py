# select_quartile.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from alg import df_quartile

def seleccionar_cuartil(df, columna_objetivo, porc=0.25, quartile="first", ascending=True):
    """
    Selecciona y retorna un cuartil/segmento del DataFrame usando df_quartile.

    Parámetros:
    - df: DataFrame completo
    - columna_objetivo: columna para ordenar y segmentar (ej. 'y')
    - porc: porcentaje del segmento (por defecto 0.25 = 25%)
    - quartile: cuartil a seleccionar ('first', 'second', 'third', 'fourth', 'center')
    - ascending: ordenar ascendente o descendente (True/False)

    Retorna:
    - DataFrame con el segmento seleccionado
    """
    return df_quartile(df, criterion=columna_objetivo, porc=porc, quartile=quartile, ascending=ascending)


def graficar_cuartiles(df_original, df_cuartil, columna_objetivo='y', label_cuartil='Cuartil seleccionado'):
    """
    Grafica la densidad KDE de la columna objetivo para el dataset original y el cuartil seleccionado.

    Parámetros:
    - df_original: DataFrame completo
    - df_cuartil: DataFrame con el cuartil seleccionado
    - columna_objetivo: columna sobre la que se hace la gráfica
    - label_cuartil: etiqueta para el cuartil en la leyenda
    """
    plt.figure(figsize=(12, 6))

    sns.kdeplot(df_original[columna_objetivo], label='Original', fill=True, alpha=0.5, color="#A03B79")
    sns.kdeplot(df_cuartil[columna_objetivo], label=label_cuartil, fill=True, alpha=0.7, color="#5344DA")

    plt.title(f'Densidad de {columna_objetivo} en Dataset Original vs {label_cuartil}')
    plt.xlabel(columna_objetivo)
    plt.ylabel('Densidad')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # Ejemplo básico para probar
    df = pd.read_csv('data/df_original.csv')

    # Seleccionar el cuartil 
    cuartil = seleccionar_cuartil(df, 'y', porc=0.0625, quartile='first', ascending=True)

    print("Cuartil seleccionado:")
    print(cuartil)

    # Graficar la comparación
    graficar_cuartiles(df, cuartil, columna_objetivo='y', label_cuartil='Tercer cuartil (desc)')
