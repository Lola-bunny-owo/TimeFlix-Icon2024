import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Funzione per la conversione degli Embeddings da lista di stringhe ad array di float
def convert_embeddings(df, embedding):
    def safe_conversion(x):
        embedding_length= 100
        
        if isinstance(x, (list, np.ndarray)) and len(x) > 0:
            return np.array(x, dtype='float64')
        return np.zeros(embedding_length)  # Sostituisci embedding_length con la lunghezza desiderata
    
    # Setta le opzioni di stampa per visualizzare i numeri come 0.0 anziché in notazione scientifica
    np.set_printoptions(precision=1, suppress=True, floatmode='fixed')
    
    df[embedding] = df[embedding].apply(safe_conversion)
    return np.stack(df[embedding].values)  # Converte la colonna in una matrice NumPy
    
# Funzione per la standardizzazione dei dati [0 e 1]
def standardize_values(embedding_array):
    scaler = StandardScaler()
    embeddings_scaled= scaler.fit_transform(embedding_array)
    return embeddings_scaled

# Applicazione della tecnica PCA con numero di componenti preso in input
def pca(n_components, embeddings_scaled):
    pca = PCA(n_components= n_components)
    embeddings_pca= pca.fit_transform(embeddings_scaled)
    explained_variance = np.cumsum(pca.explained_variance_ratio_)
    
    return embeddings_pca, explained_variance

# Funzione per visualizzare la varianza spiegata cumulativa
def plot_explained_variance(explained_variance):
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, len(explained_variance) + 1), explained_variance, marker='o')
    plt.xlabel('Numero di Componenti Principali')
    plt.ylabel('Varianza Spiegata Cumulativa')
    plt.title('Varianza Spiegata Cumulativa vs Numero di Componenti Principali')
    plt.grid(True)
    plt.show()

# Funzione per aggiornare il df con i nuovi embeddings PCA
def update_embeddings_in_df(df, new_embeddings, column):
    # Verifica che il numero di righe degli embeddings coincida con quello del DataFrame
    if len(new_embeddings) == len(df):
        df[column] = list(new_embeddings)  # Converti l'array di embeddings in una lista di array
    else:
        print(f"Errore: Il numero di embeddings ({len(new_embeddings)}) non corrisponde al numero di righe del DataFrame ({len(df)}).")