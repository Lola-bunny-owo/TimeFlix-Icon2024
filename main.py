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
print(eda.describe_data(df))

# Grafico a barre per la differenza tra Film e Serie TV
df['type'].value_counts().plot(kind='bar', title="Movies and TV Shows Differences")
plt.show()

# Grafici a barre per la distribuzione del numero di film e serie TV per rating
eda.bar_plot(df, type_value='Movie')
eda.bar_plot(df, type_value='TV Show')

# Grafico dei generi di Film e Serie TV

# Conta i generi di film e serie TV
films_genres = eda.plot_genres_by_type(df[df['type'] == 'Movie'], 'Film')
tv_series_genres = eda.plot_genres_by_type(df[df['type'] == 'TV Show'], 'TV Show')

# Combina i generi di film e serie TV in un unico DataFrame
combined_genres = pd.concat([films_genres, tv_series_genres], axis=1)
combined_genres.columns = ['Film Genres', 'TV Series Genres']

# Gestisci i valori NaN nel caso un genere sia presente solo nei film o nelle serie TV
combined_genres.fillna(0, inplace=True)

# Melt il DataFrame combinato per unire le colonne dei generi in una colonna
combined_genres = combined_genres.reset_index().melt(id_vars='index', var_name='Genre Type', value_name='Count')

# Plot dei generi combinati
plt.figure(figsize=(12, 6))
sns.barplot(x='Count', y='index', hue='Genre Type', data=combined_genres, palette='viridis')
plt.title('Film and TV Series Genres Differences')
plt.xlabel('Count')
plt.ylabel('Genre')
plt.show()

### Calcolo di skewness e kurtosis per duration_numeric. Suddivisione in duration_numeric_film e duration_numeric_shows ###

df['duration_numeric_film'] = pd.NA   # Crea colonne vuote per film e serie TV
df['duration_numeric_shows'] = pd.NA
df['duration_numeric'] = df['duration'].str.extract('(\\d+)').astype(float)

# Assegna i valori di 'duration_numeric' alla nuova colonna appropriata in base al tipo
df.loc[df['type'] == 'Movie', 'duration_numeric_film'] = df['duration_numeric']
df.loc[df['type'] == 'TV Show', 'duration_numeric_shows'] = df['duration_numeric']

# Converti i valori nelle colonne a numerico, ignorando gli errori di conversione
df['duration_numeric_film'] = pd.to_numeric(df['duration_numeric_film'], errors='coerce')
df['duration_numeric_shows'] = pd.to_numeric(df['duration_numeric_shows'], errors='coerce')

# Verifica il risultato
print("\nEcco la suddivisione corretta: \n", df[['type', 'duration', 'duration_numeric_film', 'duration_numeric_shows']].head(3))

# Verifica la quantità di valori non nulli in entrambe le colonne
print("\nValori non nulli in duration_numeric_film:", df['duration_numeric_film'].dropna().count())
print("Valori non nulli in duration_numeric_shows:", df['duration_numeric_shows'].dropna().count())

# Verifica se ci sono valori non numerici
print("\nValori unici in duration_numeric_film:", df['duration_numeric_film'].unique())
print("Valori unici in duration_numeric_shows:", df['duration_numeric_shows'].unique())

### Calcolo e management di skewness e kurtosis per film e per serie tv
skewness_film, kurt_film = eda.calculate_skew_kurtosis(df, 'duration_numeric_film')
skewness_film, kurt_film= eda.manage_skew(df, skewness_film, kurt_film, 'duration_numeric_film')
eda.manage_kurt(kurt_film, 'duration_numeric_film')

skewness_shows, kurt_shows = eda.calculate_skew_kurtosis(df, 'duration_numeric_shows')
skewness_shows, kurt_shows=eda.manage_skew(df, skewness_shows, kurt_shows, 'duration_numeric_shows')
eda.manage_kurt(kurt_shows, 'duration_numeric_shows')

# Istogrammi per le due colonne
eda.plot_histogram(df, 'duration_numeric_film')
eda.plot_histogram(df, 'duration_numeric_shows')

# Identificazione e descrizione degli outliers per duration_numeric_film e duration_numeric_shows
duration_film_outliers = eda.find_outliers(df, 'duration_numeric_film')
print(f"\nOutliers nella colonna duration_numeric_film:\n", duration_film_outliers.describe())
duration_shows_outliers = eda.find_outliers(df, 'duration_numeric_film')
print(f"\nOutliers nella colonna duration_numeric_shows:\n", duration_film_outliers.describe())

# Verifica valori mancanti
print("\nNumero di valori mancanti per colonna:\n", df.isnull().sum())



