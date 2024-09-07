
#### Funzioni per il CSP Applicato al sistema di raccomandazione e pianificazione ####

# Funzionche che verifica se il contenuto soddisfa i vincoli specificati
def is_consistent(content, selected_genres, min_duration, max_duration, is_movie, is_show):
    if is_movie and not content['Is_movie']:
        return False
    if is_show and not content['Is_TVshow']:
        return False

    # Controllo dei generi
    genres = content['Genre_Film'] if is_movie else content['Genre_Show']
    if not any(genre in selected_genres for genre in genres):
        return False

    # Controllo della durata
    duration = content['Film_Duration'] if is_movie else content['Show_Duration']
    if not (min_duration <= duration <= max_duration):
        return False

    return True

# Funzione che implementa il forward checking per ridurre il numero di opzioni da esplorare.
# Termina se ha trovato un numero sufficiente di soluzioni.
def forward_checking(df, index, selected_genres, min_duration, max_duration, is_movie, is_show, partial_solution, max_solutions=50):
    # Condizione di terminazione: Se l'indice supera la lunghezza del DataFrame o se abbiamo abbastanza soluzioni.
    if index >= len(df) or len(partial_solution) >= max_solutions:
        return partial_solution

    content = df.iloc[index]  # Si ottiene il contenuto corrente dal df

    # Verifica se il contenuto soddisfa i vincoli. Se il contenuto è valido, lo aggiunge alla soluzione parziale
    if is_consistent(content, selected_genres, min_duration, max_duration, is_movie, is_show):
        partial_solution.append(content.to_dict())

    # Si prosegue con l'elemento successivo
    return forward_checking(df, index + 1, selected_genres, min_duration, max_duration, is_movie, is_show, partial_solution, max_solutions)

# Funzione che applica il backtracking con forward checking per trovare soluzioni coerenti con i vincoli
def apply_backtracking(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    return forward_checking(df, 0, selected_genres, min_duration, max_duration, is_movie, is_show, [])

