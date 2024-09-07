import pandas as pd
from gensim.models import Word2Vec

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
    print("\nStampa delle prime 10 righe del dataset, con true nelle posizioni in cui il dato è null:\n",
          df.drop(columns= columns_to_exclude).isnull().head(10))

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
    for genre in ['International Movies', 'Dramas']: 
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

    
    
