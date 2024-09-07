
#### Funzioni per il CSP Applicato al sistema di raccomandazione e pianificazione ####

# Funzione che che verifica se il contenuto soddisfa i vincoli specificati
def is_consistent(content, selected_genres, min_duration, max_duration, is_movie, is_show):
    # Check if the content matches the type (movie or show)
    if is_movie and not content['Is_movie']:
        return False
    if is_show and not content['Is_TVshow']:
        return False

    # Check and sanitize genres based on content type (Film or Show)
    genres = content['Genre_Film'] if is_movie else content['Genre_Show']
    
    # Ensure that genres is a list or string
    if isinstance(genres, list):
        genres_list = genres
    elif isinstance(genres, str):
        genres_list = [genre.strip() for genre in genres.split(',')]  # Split string into a list
    else:
        print(f"Warning: Invalid genre type found: {genres}. Skipping content.")
        return False

    # Ensure that selected_genres is a valid iterable and contains strings
    if not isinstance(selected_genres, (list, set, tuple)):
        print(f"Warning: Invalid selected_genres type found: {selected_genres}. Expected list, set, or tuple.")
        return False

    # Ensure that genres_list and selected_genres contain valid strings
    if not any(isinstance(genre, str) and genre in selected_genres for genre in genres_list):
        return False

    # Check the duration of the content
    duration = content['Film_Duration'] if is_movie else content['Show_Duration']
    if not isinstance(duration, (int, float)):
        print(f"Warning: Invalid duration found: {duration}. Skipping content.")
        return False
    if not (min_duration <= duration <= max_duration):
        return False

    return True




# Funzione che implementa il forward checking per ridurre il numero di opzioni da esplorare.
# Termina se ha trovato un numero sufficiente di soluzioni.
def forward_checking(df, selected_genres, min_duration, max_duration, is_movie, is_show, max_solutions=50):
    partial_solution = []
    index = 0
    
    # Iterate through the DataFrame rows
    while index < len(df) and len(partial_solution) < max_solutions:
        content = df.iloc[index]
        
        if is_consistent(content, selected_genres, min_duration, max_duration, is_movie, is_show):
            partial_solution.append(content.to_dict())
        
        index += 1
    
    return partial_solution

# Funzione che applica il backtracking con forward checking per trovare soluzioni coerenti con i vincoli
def apply_backtracking(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    return forward_checking(df, 0, selected_genres, min_duration, max_duration, is_movie, is_show)


