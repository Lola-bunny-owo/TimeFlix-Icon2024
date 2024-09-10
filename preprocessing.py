import pandas as pd
from gensim.models import Word2Vec
import numpy as np
from sklearn.utils import resample
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from datetime import datetime


#### Funzioni per la fase di preprocessing

# Funzione per la gestione degli outliers attraverso le soglie manuali
def manage_outliers(df, outliers_df, column, manual_threshold):
    # Filtra gli outliers che superano la soglia manuale
    outliers_to_remove = outliers_df[outliers_df[column] > manual_threshold]
    
    # Rimuove gli outliers dal DataFrame originale
    df_filtered = df[~df.index.isin(outliers_to_remove.index)].copy()
    
    return df_filtered

# Funzione per la gestione dei valori nulli
def manage_null_values(df):
    # Sostituzione dei valori nulli nelle colonne specificate con "Unknown"
    df['director'] = df['director'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['date_added'] = df['date_added'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    
    # Per la colonna 'rating', possiamo sostituire i valori nulli con 'Not Rated' o 'Unknown'
    df['rating'] = df['rating'].fillna('Not Rated')
    
    # Per la colonna 'duration', eliminiamo le righe in cui ci sono i valori nulli (quantità irrisoria)
    df = df.dropna(subset=['duration'])

    return df

# Funzione per la verifica dei valori mancanti per una colonna specifica
def null_values(df, column):
    return df[column].isnull().sum()

# Funzione per la stampa dei valori nulli
def print_null_values(df, columns_to_exclude):
    print("\nNumero di valori mancanti per colonna:\n", df.drop(columns= columns_to_exclude).isnull().sum())
    print("\nStampa delle prime 5 righe del dataset, con true nelle posizioni in cui il dato e' null:\n",
          df.drop(columns= columns_to_exclude).isnull().head(5))

# Funzione per il One-Hot Encoding sulla colonna 'type'
def one_hot_enc(df):
    
    # One-Hot Encoding della colonna 'type' e aggiornamento del DataFrame df
    df = pd.get_dummies(df, columns=['type'])
    # Mostra le prime righe del DataFrame aggiornato con la colonna 'type' one-hot encoded
    print("\nPrime righe del DataFrame con la colonna 'type' one-hot encoded:")
    print(df[['title', 'type_Movie', 'type_TV Show']].head())
    return df

# Funzione per l'applicazione del W2V alla colonna 'listed_in' con due embedding e due liste separate Film/Serie Tv
def w2v(df):
    
    # Preprocessing della colonna 'listed_in' per creare una lista di generi
    # Creazione delle liste di generi per i film e per le serie TV
    df['Genre_Film'] = df.apply(lambda x: x['listed_in'].split(', ') if x['type_Movie'] else [], axis=1)
    df['Genre_Show'] = df.apply(lambda x: x['listed_in'].split(', ') if x['type_TV Show'] else [], axis=1)
    
    # Addestramento del modello Word2Vec sui generi dei film e delle serie TV combinati
    all_genres = df['Genre_Film'] + df['Genre_Show']
    model = Word2Vec(sentences=all_genres, vector_size=100, window=5, min_count=1, workers=4, sg=0)

    # Ottenere gli embeddings per tutti i generi estraendo l'elenco di generi unici
    genres_vocab = list(model.wv.key_to_index.keys())
    print(f"\nGeneri nel vocabolario del modello Word2Vec:\n{genres_vocab}")

    # Recuperiamo l'embedding per ogni genere nel vocabolario
    genre_embeddings = {genre: model.wv[genre] for genre in genres_vocab}

    print("\nEmbedding per alcuni generi:")    # Esempio
        print(f"{genre}: {genre_embeddings[genre]}\n")

    # Creazione degli embedding medi per film e serie TV
    df['Genre_Embedding_Film'] = df['Genre_Film'].apply(lambda x: model.wv[x].mean(axis=0) if x else None)
    df['Genre_Embedding_Show'] = df['Genre_Show'].apply(lambda x: model.wv[x].mean(axis=0) if x else None)

    print("\nEmbedding medio per i primi 5 titoli (film e serie TV):")
    print(df[['title', 'Genre_Embedding_Film', 'Genre_Embedding_Show']].head())

# Funzione per la eliminazione delle colonne
def delete_feature(df, columns):
    df.drop(columns, axis=1, inplace=True)
    print(f"\nColonne rimosse: {columns}")
    return df

# Funzione per il mapping dei ratings in una categoria corrispondente. 
# Considerate 7 categorie differenti: Kids, Children, Family, Teens, Mature Teens, Adults, Unrated
def map_rating(rating):
    
    # Dizionario che mappa i ratings alle categorie
    categories = {
        'kids': ['G', 'TV-G', 'TV-Y'],  # Bambini piccoli
        'children': ['TV-Y7', 'TV-Y7-FV'],  # Bambini sopra i 7 anni
        'family': ['PG', 'TV-PG'],  # Contenuti adatti a tutta la famiglia
        'teens': ['PG-13', 'TV-14'],  # Adolescenti
        'mature teens': ['R'],  # Adolescenti Maggiorenni
        'adults': ['NC-17', 'TV-MA'],  # Contenuti per adulti
        'unrated': ['NR', 'Not Rated', 'UR']  # Non classificati
    }
    
    # Ricerca del rating nella categoria
    for category, ratings in categories.items():
        if rating in ratings:
            return category.capitalize()

# Funzione per il renaming delle colonne
def rename_feature(df):
    new_features_names = {
        'show_id': 'ID',
        'type': 'Type',
        'title': 'Title',
        'director': 'Director',
        'description': 'Description',
        'cast': 'Cast',
        'rating': 'Classification',
        'duration_numeric_film': 'Film_Duration',
        'duration_numeric_shows': 'Show_Duration',
        'type_Movie': 'Is_movie',
        'type_TV Show': 'Is_TVshow',
        'duration_numeric': 'Duration_numeric',
    }
    
    print("\nRenaming delle colonne..")
    df.rename(columns= new_features_names, inplace= True)
    return df


# Funzioni per la preparazione dei dati per il Decision Tree
def prepare_data_for_decision_tree(df):
    # Aggiungi le preferenze dell'utente al DataFrame
    df['Genre_Embedding_Film'] = df['Genre_Embedding_Film'].apply(lambda x: np.array(x) if isinstance(x, (list, np.ndarray)) else np.zeros(100))
    
    genre_embedding_matrix = np.stack(df['Genre_Embedding_Film'])
    
    # Calcola il numero di componenti principali da utilizzare
    n_samples, n_features = genre_embedding_matrix.shape
    n_components = min(n_samples, n_features)
    
    pca = PCA(n_components=n_components)  # PCA con numero di componenti massimo
    genre_embedding_pca = pca.fit_transform(genre_embedding_matrix)
    explained_variance_ratio = pca.explained_variance_ratio_
    print(f"\nExplained variance ratio: {explained_variance_ratio}\n")


    # Aggiungi le feature di genere ridotte e le feature esistenti al DataFrame
    X = np.column_stack([genre_embedding_pca, df[['Film_Duration', 'Is_movie', 'Is_TVshow']].values])
    y = df['user_preference']

    return X, y

def add_user_preferences(df):
    # Definisci i generi che preferisci
    preferred_genres = ['International Movies']

    # Aggiungi una colonna di preferenze simulata basata su criteri: genere, durata e classificazione
    df['user_preference'] = df.apply(lambda row: 1 if any(genre in row['Genre_Film'] for genre in preferred_genres) 
                                     and row['Film_Duration'] < 200 and row['Classification'] in ['Family'] else 0, axis=1)
    return df

def balance_data(df):
    # Separa il DataFrame in classi di maggioranza e minoranza
    df_majority = df[df.user_preference == 0]
    df_minority = df[df.user_preference == 1]

    # Upsample della classe di minoranza
    df_minority_upsampled = resample(df_minority, replace=True, n_samples=len(df_majority), random_state=42)

    # Combina le classi di maggioranza e minoranza
    df_balanced = pd.concat([df_majority, df_minority_upsampled])

    return df_balanced
    
# Funzione per generare dati sintetici bilanciati in un dataset fittizio con preferenze di visione
def generate_synthetic_time_pref(n_samples):
    # Imposta un seme fisso per il generatore di numeri casuali per ottenere risultati riproducibili
    np.random.seed(42)

    # Definisce la lista dei giorni della settimana e una lista di orari a intervalli di un'ora
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    times = pd.date_range('00:00', '23:59', freq='1h').strftime('%H:%M')

    data = []

    # Calcola il numero di campioni per ogni classe (1 e 0)
    n_preferred = n_samples // 2
    n_not_preferred = n_samples - n_preferred

    # Funzione per generare un singolo campione
    def generate_sample(is_preferred):
        while True:
            day = np.random.choice(days)
            start_time = np.random.choice(times)
            start_minutes = int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1])
            end_minutes = start_minutes + np.random.randint(60, 180)
            end_time = f"{end_minutes // 60 % 24:02d}:{end_minutes % 60:02d}"
            
            # Criteri di preferenza come indicato
            if is_preferred:
                if (day in ['Saturday', 'Sunday'] and 10 <= start_minutes // 60 < 23) or \
                   (day not in ['Saturday', 'Sunday'] and 18 <= start_minutes // 60 <= 22):
                    return [day, start_time, end_time, 1]
            else:
                if not ((day in ['Saturday', 'Sunday'] and 10 <= start_minutes // 60 < 23) or \
                        (day not in ['Saturday', 'Sunday'] and 18 <= start_minutes // 60 <= 22)):
                    return [day, start_time, end_time, 0]

    # Genera campioni preferiti (Is_Preferred = 1)
    for _ in range(n_preferred):
        data.append(generate_sample(is_preferred=1))

    # Genera campioni non preferiti (Is_Preferred = 0)
    for _ in range(n_not_preferred):
        data.append(generate_sample(is_preferred=0))

    # Crea un DataFrame dai dati generati
    return pd.DataFrame(data, columns=['Day', 'Start_Time', 'End_Time', 'Is_Preferred'])

# Funzione per il preprocessamento dei dati del dataset delle preferenze
def preprocess_data(df):
    
    # Codifica del giorno e conversione degli orari in formato numerico
    le_day = LabelEncoder()
    df['Day_Encoded'] = le_day.fit_transform(df['Day'])

    # Conversione degli orari in minuti per facilitare i calcoli
    df['Start_Time'] = df['Start_Time'].apply(lambda x: convert_time_to_minutes(x))
    df['End_Time'] = df['End_Time'].apply(lambda x: convert_time_to_minutes(x))
    
    # Stampa le prime righe del dataset preprocessato per vedere come appare
    print("\nDataset Preprocessato:")
    print(df.head())
    
    # Selezione delle feature e della target
    X = df[['Day_Encoded', 'Start_Time', 'End_Time']]
    y = df['Is_Preferred']
    
    # Stampa le feature e le etichette
    print("\n--- Feature (X) ---")
    print(X.head())
    print("\n--- Target (y) ---")
    print(y.head())

    return X, y, le_day

# Funzione per convertire l'orario in minuti
def convert_time_to_minutes(time_str):
    
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

# Funzione per convertire i minuti in formato orario HH:MM
def convert_minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f'{hours:02d}:{mins:02d}'



    
    
