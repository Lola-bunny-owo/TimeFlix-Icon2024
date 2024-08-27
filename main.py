import pandas as pd # per la manipolazione dei dati
import matplotlib.pyplot as plt  # per le visualizzazioni grafiche
import seaborn as sns  # per visualizzazioni avanzate
from scipy.stats import skew, kurtosis, zscore
import eda

# Import del dataset
df = pd.read_csv('dataset/netflix_titles.csv')

####### 1. Analisi esplorativa dei dati (EDA) ####### 

eda.dataset_info(df)     # Info generali
print(eda.describe_data(df))     # Descrizione statistica

# Verifica valori mancanti
print("\nNumero di valori mancanti per colonna:\n", df.isnull().sum())

# Calcola skewness e kurtosis per le colonne release_year e duration, con rispettivi istogrammi
skewness, kurt = eda.calculate_skew_kurtosis(df, 'release_year')
df['duration_numeric'] = df['duration'].str.extract('(\\d+)').astype(float) # Estrazione della parte numerica dalla colonna duration  
skewness, kurt = eda.calculate_skew_kurtosis(df, 'duration_numeric')

eda.plot_histogram(df, 'release_year')
eda.plot_histogram(df, 'duration_numeric')

# Grafico a barre per le variabili categoriali
df['type'].value_counts().plot(kind='bar', title="Movies and TV Shows differences")
plt.show()

# Grafici a barre per la distribuzione del numero di film e serie tv per ciascuna categoria di rating
eda.bar_plot(df, type_value= 'Movie')
eda.bar_plot(df, type_value= 'TV Show')

# Outliers trovati nella colonna duration_numeric
duration_outliers= eda.find_outliers(df, 'duration_numeric')
print(f"\n Outliers nella colonna duration:\n", duration_outliers)
print("\n", duration_outliers.describe())

# Verifica se ci sono duplicati nel dataset
duplicati = df.duplicated()

# Conta il numero di righe duplicate
numero_duplicati = duplicati.sum()
print(f"Numero di righe duplicate: {numero_duplicati}")

# Elimina i duplicati nel caso ci siano
df_cleaned = df.drop_duplicates()

# Controlla la forma del dataset per vedere se ci sono stati cambiamenti
print(f"Numero di righe nel dataset dopo la rimozione dei duplicati: {df_cleaned.shape[0]}")

## Feature listed_in da esaminare e lavorarci sopra! È quella del genere per il film / serie tv
'''Commenti per elisa, da eliminare: 
- Se vuoi fai qualche ricerca su Skewness, Kurtosis e Outliers, cercando (per quest'ultimi) come gestirli (eliminandoli oppure ecc..)
- Se pensi dobbiamo aggiungere altri grafici su altre cose, fai pure tranquillamente!
- Per l'esecuzione, ti consiglio di eseguire sia con la finestra interattiva (per vedere i plot) e sia normalmente nel terminale,
che così facendo escono tutti i valori correttamente (ma nel terminale non escono i plot)
'''
 

