import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import eda 
import preprocessing
import apprNonSup
import interface


# Import del dataset
df = pd.read_csv('dataset/netflix_titles.csv')

####### 1. ANALISI ESPLORATIVA DEI DATI (EDA) #######

# Informazioni generali e descrizione statistica
eda.dataset_info(df)
eda.describe_data(df)

# Grafico a barre per la differenza tra Film e Serie TV
## df['type'].value_counts().plot(kind='bar', title="Movies and TV Shows Differences", figsize=(8, 6))
## plt.show()

# Grafici a barre per la distribuzione del numero di film e serie TV per rating
## eda.bar_plot(df, type_value='Movie')
## eda.bar_plot(df, type_value='TV Show')

# Grafico dei generi di Film e Serie TV
## eda.plot_combined_genres_by_type(df)

### Calcolo e management di skewness e kurtosis per la colonna duration_numeric_film
eda.prepare_duration_columns(df)

skewness_film, kurt_film = eda.calculate_skew_kurtosis(df, 'duration_numeric_film')
skewness_film, kurt_film= eda.manage_skew(df, skewness_film, kurt_film, 'duration_numeric_film')
eda.manage_kurt(kurt_film, 'duration_numeric_film')

# Istogrammi per le due colonne
## eda.plot_histogram(df, 'duration_numeric_film')
## eda.plot_histogram(df, 'duration_numeric_shows')


# Trova gli outliers per i film e le serie TV usando i percentili
print(f"Soglia impostata per gli outliers di 'duration_numeric_film' (99° percentile): ", df['duration_numeric_film'].quantile(0.99))
duration_film_outliers = eda.find_outliers(df, 'duration_numeric_film', percentile=0.99)
print(f"\nOutliers nella colonna duration_numeric_film:\n", duration_film_outliers)
print(f"Soglia impostata per gli outliers di 'duration_numeric_shows' (99° percentile): ", df['duration_numeric_shows'].quantile(0.99))
duration_shows_outliers = eda.find_outliers(df, 'duration_numeric_shows', percentile=0.99)
print(f"\nOutliers nella colonna duration_numeric_shows:\n", duration_shows_outliers)

# Identificazione e stampa del numero di valori mancanti per tutte le colonne eccetto quelle escluse
columns_to_exclude = ['duration_numeric_shows', 'duration_numeric_film', 'duration_numeric'] # Specifica le colonne da escludere
preprocessing.print_null_values(df, columns_to_exclude)

####### 2. PREPROCESSING  #######  

# Imposta le soglie manuali per la rimozione degli outliers
manual_film_threshold = 210  # Soglia manuale per la durata dei film
manual_show_threshold = 10   # Soglia manuale per il numero di stagioni delle serie TV

# Gestione degli outliers utilizzando le soglie manuali
df = preprocessing.manage_outliers(df, duration_film_outliers, 'duration_numeric_film', manual_threshold=manual_film_threshold)
df = preprocessing.manage_outliers(df, duration_shows_outliers, 'duration_numeric_shows', manual_threshold=manual_show_threshold)

# Verifica degli outliers rimanenti dopo la gestione
# Trova gli outliers per i film e le serie TV usando i percentili
updated_film_outliers = eda.find_outliers(df, 'duration_numeric_film', percentile=0.99)
print(f"\nOutliers sui film aggiornati - rimossi i film di durata superiore a {manual_film_threshold} minuti:\n")
print(updated_film_outliers[['title', 'duration_numeric_film']]) 

updated_show_outliers = eda.find_outliers(df, 'duration_numeric_shows', percentile=0.99)
print(f"\nOutliers sulle serie TV aggiornati - rimosse le serie TV con più di {manual_show_threshold} stagioni:\n")
print(updated_show_outliers[['title', 'duration_numeric_shows']])

# Gestione dei valori nulli e dei duplicati
df = preprocessing.manage_null_values(df)
df.drop_duplicates(inplace=True)

# Verifica finale dei valori nulli e verifica del dataset per tutte le colonne eccetto quelle escluse
preprocessing.print_null_values(df, columns_to_exclude)
print("\nPrime 10 righe del dataset dopo il preprocessing:\n",df.drop(columns= ['duration_numeric', 'duration_numeric_film','duration_numeric_shows']).head(10))

# One-Hot Encoding per la colonna 'type', Embedding WORD2VEC per la colonna 'listed_in'
df= preprocessing.one_hot_enc(df) 
preprocessing.w2v(df)

### PCA - Apprendimento Non Supervisionato ###

# Conversione degli embeddings in array di float e standardizzazione degli array
embeddings_array_film= apprNonSup.convert_embeddings(df, 'Genre_Embedding_Film')
embeddings_array_show= apprNonSup.convert_embeddings(df, 'Genre_Embedding_Show')
embeddings_array_film= apprNonSup.standardize_values(embeddings_array_film)
embeddings_array_show= apprNonSup.standardize_values(embeddings_array_show)

max_components= 50 # Numero di componenti iniziali

# Applicazione della tecnica pca su 50 componenti
embeddings_film_pca, explained_variance_film = apprNonSup.pca(max_components, embeddings_array_film)
embeddings_show_pca, explained_variance_show = apprNonSup.pca(max_components, embeddings_array_show)

# Visualizzazione della varianza spiegata cumulativa per i film e serie tv con 50 componenti
print("\nVarianza spiegata cumulativa per i film:")
apprNonSup.plot_explained_variance(explained_variance_film)
print("\nVarianza spiegata cumulativa per le serie tv:")
apprNonSup.plot_explained_variance(explained_variance_show)

# Calcola il numero di componenti necessarie per raggiungere la soglia del 95% di varianza
threshold_comp = 0.95 
components_needed_film = np.argmax(explained_variance_film >= threshold_comp) + 1
print(f"\nNumero di componenti principali necessarie per mantenere il {threshold_comp * 100}% della varianza per i film: {components_needed_film}")
components_needed_show = np.argmax(explained_variance_show >= threshold_comp) + 1
print(f"\nNumero di componenti principali necessarie per mantenere il {threshold_comp * 100}% della varianza per le serie tv: {components_needed_show}")

# Ricalcola il pca sul numero di componenti per film e per serie tv
embeddings_film_pca, explained_variance_film = apprNonSup.pca(components_needed_film, embeddings_array_film)
embeddings_show_pca, explained_variance_show = apprNonSup.pca(components_needed_show, embeddings_array_show)

# Visualizzazione della varianza spiegata cumulativa per i film e serie tv con le nuove componenti
print("\nVarianza spiegata cumulativa per i film:")
apprNonSup.plot_explained_variance(explained_variance_film)
print("\nVarianza spiegata cumulativa per le serie tv:")
apprNonSup.plot_explained_variance(explained_variance_show)

# Aggiorna il DataFrame con gli embeddings PCA trasformati
apprNonSup.update_embeddings_in_df(df, embeddings_film_pca, 'Genre_Embedding_Film')
apprNonSup.update_embeddings_in_df(df, embeddings_show_pca, 'Genre_Embedding_Show')

# Stampa di controllo per verificare che gli embeddings siano stati aggiornati
print(df[['Genre_Embedding_Film', 'Genre_Embedding_Show']].head(5))


# Eliminazione delle colonne seguenti: 'release_year', 'country', 'date_added', 'duration'. Renaming delle colonne
columns_to_remove= ["release_year", "country", "date_added", "listed_in", "duration"]
df = preprocessing.delete_feature(df, columns_to_remove)

# Mapping dei ratings
all_ratings = df['rating'].value_counts().index.to_list()       
print("\nRatings presenti nel dataset:", sorted(all_ratings))    # Innanzitutto stampa a schermo i ratings presenti nel dataset
df['rating'] = df['rating'].apply(preprocessing.map_rating) 
print("\nPrime 10 righe del dataset con i ratings mappati:")
print(df[['show_id','title', 'description', 'rating' ]].head(10))

# Renaming delle feature
df = preprocessing.rename_feature(df)

# Mostra tutte le colonne presenti nel DataFrame dopo l'operazione di preprocessing
print("\nColonne presenti nel DataFrame dopo il preprocessing:")
print(df.columns)

####### 3. CREAZIONE DELL'INTERFACCIA GRAFICA E ACQUISIZIONE PREFERENZE  #######  

# Inizializzazione dell'interfaccia grafica
interface.create_interface(df)
