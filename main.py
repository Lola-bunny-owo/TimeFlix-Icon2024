import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import eda  # La libreria eda che hai definito

# Import del dataset
df = pd.read_csv('dataset/netflix_titles.csv')

####### 1. Analisi esplorativa dei dati (EDA) #######

# Informazioni generali e descrizione statistica
eda.dataset_info(df)
print(eda.describe_data(df))

# Verifica valori mancanti
print("\nNumero di valori mancanti per colonna:\n", df.isnull().sum())

# Calcolo di skewness e kurtosis per release_year e duration_numeric
skewness, kurt = eda.calculate_skew_kurtosis(df, 'release_year')
df['duration_numeric'] = df['duration'].str.extract('(\\d+)').astype(float)
skewness, kurt = eda.calculate_skew_kurtosis(df, 'duration_numeric')

# Istogrammi per release_year e duration_numeric
eda.plot_histogram(df, 'release_year')
eda.plot_histogram(df, 'duration_numeric')

# Grafico a barre per la differenza tra Film e Serie TV
df['type'].value_counts().plot(kind='bar', title="Movies and TV Shows Differences")
plt.show()

# Grafici a barre per la distribuzione del numero di film e serie TV per rating
eda.bar_plot(df, type_value='Movie')
eda.bar_plot(df, type_value='TV Show')

# Identificazione e descrizione degli outliers per duration_numeric
duration_outliers = eda.find_outliers(df, 'duration_numeric')
print(f"\nOutliers nella colonna duration_numeric:\n", duration_outliers.describe())

### Grafico dei generi di Film e Serie TV

def plot_genres_by_type(df, content_type):
    """
    Funzione per contare e visualizzare i generi di film o serie TV
    """
    genres = df['listed_in'].str.split(', ', expand=True).stack().value_counts()
    return genres

# Conta i generi di film e serie TV
films_genres = plot_genres_by_type(df[df['type'] == 'Movie'], 'Film')
tv_series_genres = plot_genres_by_type(df[df['type'] == 'TV Show'], 'TV Show')

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
