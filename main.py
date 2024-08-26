import pandas as pd  # per la manipolazione dei dati
import numpy as np  # per operazioni numeriche
import matplotlib.pyplot as plt  # per le visualizzazioni grafiche
import seaborn as sns  # per visualizzazioni avanzate

# Import del dataset

df = pd.read_csv('dataset/netflix_titles.csv')
#### Fase preliminare di analisi esplorativa dei dati (EDA)

# Esplora le prime righe del dataset per assicurarti che sia stato caricato correttamente
print(df.head())

## Colonne
print("Colonne:", df.columns)

# Dimensione del dataset
print("Numero di righe e colonne:", df.shape)

# Tipi di dati nelle colonne
print("Tipi di dati per ogni colonna:\n", df.dtypes)

# Info generali
print("Informazioni generali sul dataset:\n", df.info())

# Verifica valori mancanti
print("Numero di valori mancanti per colonna:\n", df.isnull().sum())

# Statistiche descrittive
print("Statistiche descrittive:\n", df.describe())

# Istogrammi per tutte le variabili numeriche
df.hist(figsize=(10, 8), bins=30)
plt.show()

# Grafico a barre per le variabili categoriali
df['type'].value_counts().plot(kind='bar', title="Movies and TV Shows differences")
plt.show()

# Filtro di selezione dei film
df_film = df[df['type'] == 'Movie']  # Assumendo che la colonna che distingue i film dalle serie TV si chiami 'type'

# Crea il diagramma a barre per i rating solo dei film
df_film['rating'].value_counts().plot(kind='bar', title= "Movies rating")
plt.show()

## Feature listed_in da esaminare e lavorarci sopra! È quella del genere per il film / serie tv





