import pandas as pd # per la manipolazione dei dati
import numpy as np  # per operazioni numeriche
import matplotlib.pyplot as plt  # per le visualizzazioni grafiche
import seaborn as sns  # per visualizzazioni avanzate
from scipy.stats import skew, kurtosis, zscore

#### Funzioni per la fase preliminare di analisi esplorativa dei dati (EDA)

# Funzione per avere avere delle informazioni generali sul dataset
def dataset_info(df):
    
    print("Verifica se il dataset è caricato correttamente stampandone le prime 3 righe: \n", df.head(3))
    
    print("\nColonne presenti nel dataset:", df.columns)
    print("\nNumero di righe e colonne:", df.shape)
    print("\nInformazioni generali sul dataset:\n")
    df.info()
   
    return df

# Funzione per avere una descrizione statistica del dataset
def describe_data(df):
    print("\nDescrizione statistica del dataset:\n")
    return df.describe()

# Funzione per calcolare la skewness (asimmetria) e la curtosi di una colonna del dataset
def calculate_skew_kurtosis(df, column):
    skewness = skew(df[column].dropna())
    kurt = kurtosis(df[column].dropna())
    print(f"\nSkewness di {column}: {skewness}, Kurtosis di {column}: {kurt}")
    return skewness, kurt

# Funzione per identificare gli outliers in una colonna utilizzando lo Z-score
def find_outliers(df, column):
    df = df.dropna(subset=[column])
    df['z_score'] = zscore(df[column])
    outliers = df[df['z_score'].abs() > 3]
    return outliers

# Funzione per la creazione di un box plot per una colonna specifica
def plot_boxplot(df, column):
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=df[column])
    plt.title(f'Box Plot della colonna {column}')
    plt.show()

# Funzione per la creazione di un istogramma per una colonna specifica
def plot_histogram(df, column):
    plt.figure(figsize=(8, 6))
    df[column].hist(bins=30)
    plt.xlabel('Valori')
    plt.ylabel('Frequenza')
    plt.title(f'Istogramma della colonna {column}')
    plt.show()

# Funzione per la creazione di bar plot 
def bar_plot(df, type_value):
    
    # Filtra il DataFrame in base al tipo specificato
    df_selection= df[df['type'] == type_value]
    
    # Crea il bar plot
    plt.figure(figsize=(12,10))
    ax = sns.countplot(x="rating", data=df_selection, palette="Set2", order=df_selection['rating'].value_counts().index[0:12])
    ax.set_title(f"{type_value} Rating")
    ax.set_ylabel(f"Number of {type_value}s")
    ax.set_xlabel("Rating Category")
    plt.show()
    
    
# Funzione per la verifica dei valori mancanti per una colonna specifica
def null_values(df, column):
    return df[column].isnull().sum()

## Funzione per contare e visualizzare i generi di film o serie TV
def plot_genres_by_type(df, content_type):
    genres = df['listed_in'].str.split(', ', expand=True).stack().value_counts()
    return genres

## Funzione per gestire skewness: se è troppo alta (> 1), applica una trasformazione logaritmica
def manage_skew(df, skew, kurt, column):

    if abs(skew) > 1:
        print(f"La skewness di {column} è elevata: {skew}. Applico una trasformazione logaritmica.")
        df[column] = np.log1p(df[column])  # Trasformazione logaritmica
        print("Valori dopo la trasformazione:")
        skew, kurt = calculate_skew_kurtosis(df, column)
        return skew, kurt
    else:
        print(f"La skewness di {column} non è elevata. Valori in regola.")
        return skew, kurt

## Funzione per gestire la kurtosis: se è elevata (> 3), potrebbe indicare la presenza di outliers significativi
def manage_kurt(kurt, column):
    if kurt > 3:
        print(f"La kurtosis di {column} è elevata: {kurt}. Potrebbero esserci outliers significativi!")
    else:
        print(f"La kurtosis di {column} non è elevata. Valori in regola.")

## Funzione per la creazione di 
        