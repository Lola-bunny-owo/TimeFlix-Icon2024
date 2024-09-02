import pandas as pd
from gensim.models import Word2Vec

#### Funzioni per la fase di preprocessing

# Funzione per la gestione degli outliers attraverso le soglie manuali
def manage_outliers(df, outliers_df, column, manual_threshold):
    # Filtra gli outliers che superano la soglia manuale
    outliers_to_remove = outliers_df[outliers_df[column] > manual_threshold]
    
    # Rimuove gli outliers dal DataFrame originale
    df_filtered = df[~df.index.isin(outliers_to_remove.index)].copy()
    
    # Informazioni sugli outliers rimossi
    print(f"\nRimossi {len(outliers_to_remove)} outliers dalla colonna '{column}' con soglia manuale > {manual_threshold}.")
    
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

# Funzione per l'applicazione del W2V alla colonna 'listed_in'
def w2v(df):
    
    # Preprocessing della colonna 'listed_in' per creare una lista di generi
    # Dividi i generi in liste di parole (liste di generi per titolo)
    df['listed_in_clean'] = df['listed_in'].apply(lambda x: x.split(', '))
    
    # Addestramento del modello Word2Vec sulle liste di generi
    model = Word2Vec(sentences=df['listed_in_clean'], vector_size=100, window=5, min_count=1, workers=4, sg=0)

    # Ottenere gli embeddings per tutti i generi estraendo l'elenco di generi unici
    genres_vocab = list(model.wv.key_to_index.keys())
    print(f"Generi nel vocabolario del modello Word2Vec: {genres_vocab}")

    # Recuperiamo l'embedding per ogni genere nel vocabolario
    genre_embeddings = {genre: model.wv[genre] for genre in genres_vocab}

    print("\nEmbedding per alcuni generi:")    # Esempio
    for genre in ['International Movies', 'Dramas']: 
        print(f"{genre}: {genre_embeddings[genre]}\n")

    # Creare embedding medio per ogni titolo
    df['genre_embedding'] = df['listed_in_clean'].apply(lambda x: model.wv[x].mean(axis=0))

    # Mostrare i primi embedding medi per i titoli
    print("\nEmbedding medio per i primi 5 titoli:")
    print(df[['title', 'genre_embedding']].head())

# Funzione per il One-Hot Encoding sulla colonna 'type'
def one_hot_enc(df):
    
    # One-Hot Encoding della colonna 'type' e aggiornamento del DataFrame df
    df = pd.get_dummies(df, columns=['type'])
    # Mostra le prime righe del DataFrame aggiornato con la colonna 'type' one-hot encoded
    print("\nPrime righe del DataFrame con la colonna 'type' one-hot encoded:")
    print(df[['title', 'type_Movie', 'type_TV Show']].head())
    return df

# Funzione per la eliminazione delle colonne
def delete_feature(df, columns):
    df.drop(columns, axis=1, inplace=True)
    print(f"\nColonne rimosse: {columns}")
    return df