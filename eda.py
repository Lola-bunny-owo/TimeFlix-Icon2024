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
    print(df['release_year'].describe())
    print("\n\n", df.describe(include=[object]))

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
    
    # Filtra il df in base al tipo specificato
    df_selection= df[df['type'] == type_value]
    
    # Crea il bar plot
    plt.figure(figsize=(12,10))
    ax = sns.countplot(x="rating", data=df_selection, palette="Set2", order=df_selection['rating'].value_counts().index[0:12])
    ax.set_title(f"{type_value} Rating")
    ax.set_ylabel(f"Number of {type_value}s")
    ax.set_xlabel("Rating Category")
    plt.show()

# Funzione per contare e visualizzare i generi di film o serie TV
def plot_genres_by_type(df, content_type):
    genres = df['listed_in'].str.split(', ', expand=True).stack().value_counts()
    return genres

# Funzione per la creazione del grafico combinato per i generi 
def plot_combined_genres_by_type(df):
    
    # Conta i generi di film e serie TV
    films_genres = plot_genres_by_type(df[df['type'] == 'Movie'], 'Film')
    tv_series_genres = plot_genres_by_type(df[df['type'] == 'TV Show'], 'TV Show')

    # Combina i generi di film e serie TV in un unico df
    combined_genres = pd.concat([films_genres, tv_series_genres], axis=1)
    combined_genres.columns = ['Film Genres', 'TV Series Genres']

    # Gestisci i valori NaN nel caso un genere sia presente solo nei film o nelle serie TV
    combined_genres.fillna(0, inplace=True)

    # Melt il df combinato per unire le colonne dei generi in una colonna
    combined_genres = combined_genres.reset_index().melt(id_vars='index', var_name='Genre Type', value_name='Count')

    # Plot dei generi combinati
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Count', y='index', hue='Genre Type', data=combined_genres, palette='viridis')
    plt.title('Film and TV Series Genres Differences')
    plt.xlabel('Count')
    plt.ylabel('Genre')
    plt.show()
    
# Funzione che prepara le colonne 'duration_numeric_film' e 'duration_numeric_shows' per il calcolo di skewness e kurtosis
def prepare_duration_columns(df):
    # Crea colonne vuote per film e serie TV
    df['duration_numeric_film'] = pd.NA
    df['duration_numeric_shows'] = pd.NA
    df['duration_numeric'] = df['duration'].str.extract('(\\d+)').astype(float) # Estrazione della parte numerica dalla colonna 'duration'

    # Assegna i valori di 'duration_numeric' alla nuova colonna appropriata in base al tipo
    df.loc[df['type'] == 'Movie', 'duration_numeric_film'] = df['duration_numeric']
    df.loc[df['type'] == 'TV Show', 'duration_numeric_shows'] = df['duration_numeric']
    
    # Converti i valori nelle colonne a numerico, ignorando gli errori di conversione
    df['duration_numeric_film'] = pd.to_numeric(df['duration_numeric_film'], errors='coerce')
    df['duration_numeric_shows'] = pd.to_numeric(df['duration_numeric_shows'], errors='coerce')


# Funzione per calcolare la skewness (asimmetria) e la curtosi di una colonna del dataset
def calculate_skew_kurtosis(df, column):
    skewness = skew(df[column].dropna()) #Ignora i valori nulli o NaN con dropna()
    kurt = kurtosis(df[column].dropna())
    print(f"\nSkewness di {column}: {skewness}, Kurtosis di {column}: {kurt}")
    return skewness, kurt

# Funzione per gestire skewness: se è troppo alta (> 1), applica una trasformazione logaritmica
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

# Funzione per gestire la kurtosis: se è elevata (> 3), potrebbe indicare la presenza di outliers significativi
def manage_kurt(kurt, column):
    if kurt > 3:
        print(f"La kurtosis di {column} è elevata: {kurt}. Potrebbero esserci outliers significativi!")
    else:
        print(f"La kurtosis di {column} non è elevata. Valori in regola.")

# Funzione per identificare gli outliers in una colonna utilizzando lo Z-score
def find_outliers(df, column):
    
    # Elimina valori nulli nella colonna specificata
    df_clean = df.dropna(subset=[column]).copy()  # Usa una copia per evitare SettingWithCopyWarning
    df_clean['z_score'] = zscore(df_clean[column])  # Calcola lo Z-score

    # Filtra i dati per ottenere solo gli outlier
    outliers = df_clean[df_clean['z_score'].abs() > 3][[column, 'z_score', 'title']]
    return outliers   

# Funzione per la verifica dei valori mancanti per una colonna specifica
def null_values(df, column):
    return df[column].isnull().sum()

# Funzione che calcola i valori unici e non nulli per ciascuna colonna specificata, dove:
# - columns è una lista dei nomi delle colonne da analizzare
# - results è un dizionario contenente il numero di valori unici e non nulli per ciascuna colonna
def null_unique_values(df, columns):
    results = {}

    for column in columns:
        # Calcola i valori unici e non nulli per la colonna corrente
        unique_values = df[column].nunique(dropna=True)  # Valori unici ignorando i NaN
        non_null_count = df[column].notna().sum()        # Numero di valori non nulli
        null_count= df[column].isna().sum()

        # Stampa i risultati per la colonna corrente
        print(f"Colonna: {column}")
        print(f" - Valori unici: {unique_values}")
        print(f" - Valori nulli: {null_count}")
        print(f" - Valori non nulli: {non_null_count}")

        # Salva i risultati in un dizionario
        results[column] = {
            'unique_values': unique_values,
            'non_null_count': non_null_count,
            'null_count': null_count,
        }

    return results

# Funzione per la gestione degli outliers in  base alla colonna specificata.
# Se la colonna è 'duration_numeric_film', rimuove i film con durata superiore a 210 minuti.
# Se la colonna è 'duration_numeric_shows', rimuove le serie TV con più di 10 stagioni.
# NON CAPISCO PERCHè FILTRA MALEEEEEEEEEEEEEEE
def manage_outliers(dataframe, target_column, film_threshold=250, show_threshold=15):
    """Gestisce gli outliers in base alla colonna specificata."""
    if target_column not in dataframe.columns:
        print(f"Errore: la colonna '{target_column}' non esiste nel DataFrame.")
        return dataframe
    
    initial_row_count = dataframe.shape[0]

    if target_column == 'duration_numeric_film':
        filtered_dataframe = dataframe[dataframe[target_column] <= film_threshold].copy()
    elif target_column == 'duration_numeric_shows':
        filtered_dataframe = dataframe[dataframe[target_column] <= show_threshold].copy()
    else:
        print(f"Colonna '{target_column}' non supportata per la gestione degli outliers.")
        return dataframe
    
    final_row_count = filtered_dataframe.shape[0]
    rows_filtered = initial_row_count - final_row_count
    print(f"Filtrate {rows_filtered} righe dalla colonna '{target_column}'.")

    return filtered_dataframe







