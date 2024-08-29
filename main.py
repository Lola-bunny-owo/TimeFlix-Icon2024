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


####### 2. PREPROCESSING  #######

# Gestione degli outliers - Non funziona! TO-FIX
# Praticamente, la funzione manage_outliers (nel eda.py) è una funzione che gestisce gli outliers come abbiamo già detto:
#  1) Filtra (dagli otuliers dei film e da quelli delle serie tv) film di durata > 3h30 (210) e serie tv di #stagioni > 10.
#  2) Elimina quei dati che superano quelle condizioni e riaggiorna gli outliers, rimanendo con gli outliers "corretti"
#  ..  che, di conseguenza, sono gli outliers che abbiamo deciso di non gestire e conservare nel dataset.
# Penso che qui il codice sia abbastanza chiaro poi, ma nel processo c'è qualcosa che non funziona..
# Quindi, se riesci alla fine dovremmo stampare queste due righe che vedi sugli outliers aggiornati

df = eda.manage_outliers(df, 'duration_numeric_film')
df = eda.manage_outliers(df, 'duration_numeric_shows')
duration_film_outliers = eda.find_outliers(df, 'duration_numeric_film')
print(f"\nOutliers sui film aggiornati - rimossi i film di durata > 3h30m :\n", duration_film_outliers)
duration_shows_outliers = eda.find_outliers(df, 'duration_numeric_shows')
print(f"\nOutliers sulle serie TV aggiornati - rimosse le serie TV con #stagioni > 10 :\n", duration_shows_outliers)

# Gestione dei valori nulli - È ancora da implementare, ma abbiamo già discusso su come fare
# Per le colonne director e country possiamo sostituire quei valori nulli con dati "Unknown", in quanto non ci servono molto al nostro fine.
# La colonna cast potrebbe servirci, quindi potremmo scegliere di eliminare le righe in cui il cast è vuoto o sconosciuto.
# .. oppure troviamo un altro modo per gestirli
# Anche la colonna date_added non c'interessa, quindi possiamo sostituirli con dati "Unknown". Per la colonna rating non so.

# Gestione dei duplicati - Penso sia abbastanza semplice; si eliminano i duplicati lol


