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

### Calcolo e management di skewness e kurtosis per film
eda.prepare_duration_columns(df)
skewness_film, kurt_film = eda.calculate_skew_kurtosis(df, 'duration_numeric_film')
skewness_film, kurt_film= eda.manage_skew(df, skewness_film, kurt_film, 'duration_numeric_film')
eda.manage_kurt(kurt_film, 'duration_numeric_film')


# Istogrammi per le due colonne
eda.plot_histogram(df, 'duration_numeric_film')
eda.plot_histogram(df, 'duration_numeric_shows')

# Colonne da analizzare
columns_to_analyze = ['duration_numeric_film', 'duration_numeric_shows']

# Calcola valori unici e non nulli per le colonne specificate
results = eda.null_unique_values(df, columns_to_analyze)

# Identificazione e descrizione degli outliers per duration_numeric_film e duration_numeric_shows - DA SISTEMARE!
duration_film_outliers = eda.find_outliers(df, 'duration_numeric_film')
print(f"\nOutliers nella colonna duration_numeric_film:\n", duration_film_outliers)
duration_shows_outliers = eda.find_outliers(df, 'duration_numeric_shows')
print(f"\nOutliers nella colonna duration_numeric_shows:\n", duration_shows_outliers)

# Verifica valori mancanti
print("\nNumero di valori mancanti per colonna:\n", df.isnull().sum())

