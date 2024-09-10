import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

#### Funzioni per l'Apprendimento Non Supervisionato ####

# Funzione per la conversione degli Embeddings da lista di stringhe ad array di float
def convert_embeddings(df, embedding):
    embedding_length= 100

    def safe_conversion(x):  
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

# Funzione che applica agli embeddings le due operazioni di conversione e standardizzazione
def preprocess_embeddings(df, embedding_column):
     # Conversione degli embeddings in array di float
    embeddings_array = convert_embeddings(df, embedding_column)
    print(f"\nEmbeddings convertiti per {embedding_column}: ", embeddings_array[:1])

    # Standardizzazione degli embeddings
    embeddings_array = standardize_values(embeddings_array)
    print(f"\nEmbeddings standardizzati per {embedding_column}: ", embeddings_array[:1])

    return embeddings_array
    
# Tecnica PCA con numero di componenti preso in input
def pca(n_components, embeddings_scaled):
    pca = PCA(n_components= n_components)
    embeddings_pca= pca.fit_transform(embeddings_scaled)
    explained_variance = np.cumsum(pca.explained_variance_ratio_)
    
    return embeddings_pca, explained_variance

# Funzione per visualizzare la varianza spiegata cumulativa
def plot_explained_variance(explained_variance, title):
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, len(explained_variance) + 1), explained_variance, marker='o')
    plt.xlabel('Numero di Componenti Principali')
    plt.ylabel('Varianza Spiegata Cumulativa')
    plt.title(f'Varianza Spiegata Cumulativa vs Numero di Componenti Principali per {title}')
    plt.grid(True)
    plt.show()

# Applicazione della PCA e stampa dei plot
def apply_pca_and_plot(n_components, embeddings, title):
    
    # Applicazione della PCA
    embeddings_pca, explained_variance = pca(n_components, embeddings)
    print(f"\nGrafico della varianza spiegata cumulativa per {title} con {n_components} componenti: ")
    ## plot_explained_variance(explained_variance, title)
    return embeddings_pca, explained_variance

# Funzione per calcolare il numero di componenti principali necessarie per mantenere una certa varianza
def calculate_components_needed(explained_variance, threshold_comp, title):
    components_needed = np.argmax(explained_variance >= threshold_comp) + 1
    print(f"\nNumero di componenti principali necessarie per mantenere il {threshold_comp * 100}% della varianza per {title}: {components_needed}")
    return components_needed

# Funzione per aggiornare il df con i nuovi embeddings PCA
def update_embeddings_in_df(df, new_embeddings, column):
    # Verifica che il numero di righe degli embeddings coincida con quello del DataFrame
    if len(new_embeddings) == len(df):
        df[column] = list(new_embeddings)  # Converti l'array di embeddings in una lista di array
    else:
        print(f"Errore: il numero di embeddings ({len(new_embeddings)}) non corrisponde al numero di righe del DataFrame ({len(df)}).")

# Funzione che suggerisce contenuto basandosi sugli embeddings del genere
def recommend_based_on_embeddings(df, content_title, num_recommendations=3, content_type="Movie"):
    # Verifica che il titolo del contenuto sia presente nel DataFrame
    if content_title not in df['Title'].values:
        raise ValueError(f"Content title '{content_title}' not found in the dataset.")
    
    # Seleziona l'embedding del genere per il contenuto specificato
    selected_embedding = df[df['Title'] == content_title]['Genre_Embedding_Film'].values[0]

    #  Seleziona l'embedding del genere per il contenuto specificato
    selected_embedding = np.array(selected_embedding).reshape(1, -1)

    # Calcola la similarità coseno tra l'embedding selezionato e tutti gli altri embeddings
    df['similarity'] = df['Genre_Embedding_Film'].apply(
        lambda x: cosine_similarity(
            selected_embedding, np.array(x).reshape(1, -1) if isinstance(x, (list, np.ndarray)) else np.zeros(selected_embedding.shape[1])
        )[0][0]
    )

    # Seleziona i film o le serie TV in base al tipo di contenuto specificato
    if content_type == "TV Show":
        recommendations = df[df['Is_TVshow'] == 1].sort_values(by='similarity', ascending=False).head(num_recommendations).to_dict(orient='records')
    else:
        recommendations = df[df['Is_movie'] == 1].sort_values(by='similarity', ascending=False).head(num_recommendations).to_dict(orient='records')

    return recommendations

