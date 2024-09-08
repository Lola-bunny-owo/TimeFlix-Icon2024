
#### Funzioni per il CSP Applicato al sistema di raccomandazione e pianificazione ####

# Funzione che che verifica se il contenuto soddisfa i vincoli specificati
def is_consistent(content, selected_genres, min_duration, max_duration, is_movie, is_show):
    # Controlla se il contenuto corrisponde al tipo (film o show)
    if is_movie and not content['Is_movie']:
        return False
    if is_show and not content['Is_TVshow']:
        return False

     # Verifica e sanifica i generi in base al tipo di contenuto (Film o Show)
    genres = content['Genre_Film'] if is_movie else content['Genre_Show']
    
    # Controllo sul genere per assicurarsi che sia una lista o una stringa
    if isinstance(genres, list):
        genres_list = genres
    elif isinstance(genres, str):
        genres_list = [genre.strip() for genre in genres.split(',')]
    else:
        print(f"Warning: Invalid genre type found: {genres}. Skipping content.")
        return False

    # Controllo su selected_genres per assicurarsi sia un iterabile valido e contenga stringhe
    if not isinstance(selected_genres, (list, set, tuple)):
        print(f"Warning: Invalid selected_genres type found: {selected_genres}. Expected list, set, or tuple.")
        return False

    # Controlla che genres_list e selected_genres contengano stringhe valide
    if not any(isinstance(genre, str) and genre in selected_genres for genre in genres_list):
        return False

    # Controlla la durata del contenuto
    duration = content['Film_Duration'] if is_movie else content['Show_Duration']
    if not isinstance(duration, (int, float)):
        print(f"Warning: Invalid duration found: {duration}. Skipping content.")
        return False
    if not (min_duration <= duration <= max_duration):
        return False

    return True

# Funzione che implementa il forward checking per ridurre il numero di opzioni da esplorare.
# Itera attraverso il dataframe e utilizza is_consistent() per filtrare i contenuti.
# Si ferma quando raggiunge il numero massimo di soluzioni specificato o esamina tutti i contenuti.
def forward_checking(df, selected_genres, min_duration, max_duration, is_movie, is_show, max_solutions=50):
    filtered_content = []
    
    for _, content in df.iterrows():
        if is_consistent(content, selected_genres, min_duration, max_duration, is_movie, is_show):
            filtered_content.append(content.to_dict())
        if len(filtered_content) >= max_solutions:
            break

    return filtered_content

# Funzione che applica il backtracking con forward checking per trovare soluzioni coerenti con i vincoli
def apply_backtracking(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    return forward_checking(df, selected_genres, min_duration, max_duration, is_movie, is_show)


