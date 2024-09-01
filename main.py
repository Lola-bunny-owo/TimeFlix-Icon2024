import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import eda 
from gensim.models import Word2Vec

# Import del dataset
df = pd.read_csv('dataset/netflix_titles.csv')

####### 1. ANALISI ESPLORATIVA DEI DATI (EDA) #######

# Informazioni generali e descrizione statistica
eda.dataset_info(df)
eda.describe_data(df)

# Grafico a barre per la differenza tra Film e Serie TV
df['type'].value_counts().plot(kind='bar', title="Movies and TV Shows Differences")
plt.show()

# Grafici a barre per la distribuzione del numero di film e serie TV per rating
eda.bar_plot(df, type_value='Movie')
eda.bar_plot(df, type_value='TV Show')

# Grafico dei generi di Film e Serie TV
eda.plot_combined_genres_by_type(df)

### Calcolo e management di skewness e kurtosis per la colonna duration_numeric_film
eda.prepare_duration_columns(df)

skewness_film, kurt_film = eda.calculate_skew_kurtosis(df, 'duration_numeric_film')
skewness_film, kurt_film= eda.manage_skew(df, skewness_film, kurt_film, 'duration_numeric_film')
eda.manage_kurt(kurt_film, 'duration_numeric_film')

# Istogrammi per le due colonne
eda.plot_histogram(df, 'duration_numeric_film')
eda.plot_histogram(df, 'duration_numeric_shows')


# Trova gli outliers per i film e le serie TV usando i percentili
print(f"Soglia impostata per gli outliers di 'duration_numeric_film' (99° percentile): ", df['duration_numeric_film'].quantile(0.99))
duration_film_outliers = eda.find_outliers(df, 'duration_numeric_film', percentile=0.99)
print(f"\nOutliers nella colonna duration_numeric_film:\n", duration_film_outliers)
print(f"Soglia impostata per gli outliers di 'duration_numeric_shows' (99° percentile): ", df['duration_numeric_shows'].quantile(0.99))
duration_shows_outliers = eda.find_outliers(df, 'duration_numeric_shows', percentile=0.99)
print(f"\nOutliers nella colonna duration_numeric_shows:\n", duration_shows_outliers)

# Identificazione e stampa del numero di valori mancanti per tutte le colonne eccetto quelle escluse
columns_to_exclude = ['duration_numeric_shows', 'duration_numeric_film', 'duration_numeric'] # Specifica le colonne da escludere
eda.print_null_values(df, columns_to_exclude)

####### 2. PREPROCESSING  #######  

# Imposta le soglie manuali per la rimozione degli outliers
manual_film_threshold = 210  # Soglia manuale per la durata dei film
manual_show_threshold = 10   # Soglia manuale per il numero di stagioni delle serie TV

# Gestione degli outliers utilizzando le soglie manuali
df = eda.manage_outliers(df, duration_film_outliers, 'duration_numeric_film', manual_threshold=manual_film_threshold)
df = eda.manage_outliers(df, duration_shows_outliers, 'duration_numeric_shows', manual_threshold=manual_show_threshold)

# Verifica degli outliers rimanenti dopo la gestione
updated_film_outliers = eda.find_outliers(df, 'duration_numeric_film', percentile=0.99)
#print(f"\nOutliers sui film aggiornati - rimossi i film di durata > {manual_film_threshold} minuti:\n", updated_film_outliers)
updated_show_outliers = eda.find_outliers(df, 'duration_numeric_shows', percentile=0.99)
#print(f"\nOutliers sulle serie TV aggiornati - rimosse le serie TV con #stagioni > {manual_show_threshold}:\n", updated_show_outliers)

# Gestione dei valori nulli e dei duplicati
df = eda.manage_null_values(df)
df.drop_duplicates(inplace=True)

# Verifica finale dei valori nulli e verifica del dataset per tutte le colonne eccetto quelle escluse
eda.print_null_values(df, columns_to_exclude)
print("\nPrime 10 righe del dataset dopo il preprocessing:\n",df.drop(columns= ['duration_numeric', 'duration_numeric_film','duration_numeric_shows']).head(10))


##  WORD2VEC

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

# Esempio
print("\nEmbedding per alcuni generi:")
for genre in ['International Movies', 'Dramas']: 
    print(f"{genre}: {genre_embeddings[genre]}\n")

# Creare embedding medio per ogni titolo
df['genre_embedding'] = df['listed_in_clean'].apply(lambda x: model.wv[x].mean(axis=0))

# Mostrare i primi embedding medi per i titoli
print("\nEmbedding medio per i primi 5 titoli:")
print(df[['title', 'genre_embedding']].head())

# One-Hot Encoding della colonna 'type'
df_encoded = pd.get_dummies(df, columns=['type'])

# Mostra le prime righe del DataFrame con la colonna 'type' one-hot encoded
print("\nPrime righe del DataFrame con la colonna 'type' one-hot encoded:")
print(df_encoded[['title', 'type_Movie', 'type_TV Show']].head())

print("\nColonne presenti nel DataFrame dopo il preprocessing:")
print(df.columns)
