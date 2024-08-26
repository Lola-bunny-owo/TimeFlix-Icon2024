import pandas as pd  # per la manipolazione dei dati
import numpy as np  # per operazioni numeriche
import matplotlib.pyplot as plt  # per le visualizzazioni grafiche
import seaborn as sns  # per visualizzazioni avanzate

# Import del dataset

df = pd.read_csv('dataset/netflix_titles.csv')

#### Fase preliminare di analisi esplorativa dei dati (EDA)

# Esplora le prime righe del dataset per assicurarti che sia stato caricato correttamente
print(df.head(10))

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
df_film = df[df['type'] == 'Movie'] 

plt.figure(figsize=(12,10))
ax = sns.countplot(x="rating", data=df_film, palette="Set2", order=df_film['rating'].value_counts().index[0:18])
ax.set_title("Movies Rating")
ax.set_ylabel("Number of Movies")
ax.set_xlabel("Rating Category")

# Filtro di selezione dei Tv Show
df_show = df[df['type'] == 'TV Show']

plt.figure(figsize=(12,10))
ax = sns.countplot(x="rating", data=df_show, palette="Set2", order=df_show['rating'].value_counts().index[0:18])
ax.set_title("Shows Rating")
ax.set_ylabel("Number of Shows")
ax.set_xlabel("Rating Category")




## Feature listed_in da esaminare e lavorarci sopra! È quella del genere per il film / serie tv





