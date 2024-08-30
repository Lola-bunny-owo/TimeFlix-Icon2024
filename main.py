import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import eda 

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

# Identificazione e descrizione degli outliers per duration_numeric_film e duration_numeric_shows
duration_film_outliers = eda.find_outliers(df, 'duration_numeric_film')
print(f"\nOutliers nella colonna duration_numeric_film:\n", duration_film_outliers)
duration_shows_outliers = eda.find_outliers(df, 'duration_numeric_shows')
print(f"\nOutliers nella colonna duration_numeric_shows:\n", duration_shows_outliers)

# Identificazione e stampa del numero di valori mancanti per tutte le colonne eccetto quelle escluse

columns_to_exclude = ['duration_numeric_shows', 'duration_numeric_film', 'duration_numeric'] # Specifica le colonne da escludere
print("\nNumero di valori mancanti per colonna:\n", df.drop(columns= columns_to_exclude).isnull().sum())
print("\nStampa delle prime 10 righe del dataset, con true nelle posizioni in cui il dato è null:\n",
      df.drop(columns= columns_to_exclude).isnull().head(10))


print("\nDescrizione statistica delle colonne 'duration_numeric_film' e 'duration_numeric_shows':\n")
print(df['duration_numeric_film'].describe())
print(df['duration_numeric_shows'].describe())



####### 2. PREPROCESSING  #######

# Calcolo delle soglie basate sui percentili
film_threshold = df['duration_numeric_film'].quantile(0.99)
show_threshold = df['duration_numeric_shows'].quantile(0.99)

print(f"Soglia per i film (99° percentile): {film_threshold}")
print(f"Soglia per le serie TV (99° percentile): {show_threshold}")

print("Film che verrebbero rimossi:\n", df[df['duration_numeric_film'] > film_threshold][['title', 'duration_numeric_film']])
print("Serie TV che verrebbero rimosse:\n", df[df['duration_numeric_shows'] > show_threshold][['title', 'duration_numeric_shows']])

# Gestione degli outliers usando le soglie calcolate dai percentili
# NON FUNZIONA - verificare manage_outliers
df = eda.manage_outliers(df, 'duration_numeric_film', film_threshold=film_threshold)
df = eda.manage_outliers(df, 'duration_numeric_shows', show_threshold=show_threshold)

# Verifica degli outliers rimanenti dopo la gestione
duration_film_outliers = eda.find_outliers(df, 'duration_numeric_film')
print(f"\nOutliers sui film aggiornati - rimossi i film di durata > {film_threshold} minuti:\n", duration_film_outliers)
duration_shows_outliers = eda.find_outliers(df, 'duration_numeric_shows')
print(f"\nOutliers sulle serie TV aggiornati - rimosse le serie TV con #stagioni > {show_threshold} :\n", duration_shows_outliers)


# Gestione dei valori nulli
# Sostituzione dei valori nulli nelle colonne specificate con "Unknown"
df['director'] = df['director'].fillna('Unknown')
df['country'] = df['country'].fillna('Unknown')
df['date_added'] = df['date_added'].fillna('Unknown')

# Gestione della colonna 'cast': al momento rimuoviamo le righe con valori nulli o sconosciuti
df['cast'] = df['cast'].fillna('Unknown')

# Per la colonna 'rating', possiamo sostituire i valori nulli con 'Not Rated' o 'Unknown'
df['rating'] = df['rating'].fillna('Not Rated')

# Gestione dei duplicati
df.drop_duplicates(inplace=True)

### PROVA DI GESTIONE DEI VALORI

# Verifica finale dei valori nulli
print("\nNumero di valori mancanti per colonna dopo il preprocessing:\n", df.isnull().sum())

# Stampa delle prime righe del dataset pulito
print("\nPrime 10 righe del dataset dopo il preprocessing:\n", df.head(10))
