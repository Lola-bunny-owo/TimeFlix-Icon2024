
# Funzione che filtra i contenuti in base alle preferenze dell'utente
# Le variabili sono: is_movie, is_show, min_duration, max_duration, selected_genres
# I vincoli sono: il tipo di contenuto, la durata, i generi
def cs_filter(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    filtered_results = []

    # Vincolo sul tipo di contenuto
    if is_movie and not is_show:
        genre_mask = df['Genre_Film'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Film_Duration'].fillna(0) >= min_duration) & (df['Film_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_Movie'] == 1
    elif is_show and not is_movie:
        genre_mask = df['Genre_Show'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Show_Duration'].fillna(0) >= min_duration) & (df['Show_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_TVShow'] == 1
    else:
        return []

    # Applicazione dei vincoli e filtraggio dei dati
    filtered_df = df[genre_mask & duration_mask & type_mask] # Se qui si aggiunge un .head(5), ad esempio il filtro contiene solo 5 contenuti

    # Creazione della lista di risultati formattati
    for _, item in filtered_df.iterrows():
        if is_movie:
            filtered_results.append(f"Movie - {item['Title']} - Duration: {item.get('Film_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Film', []))}")
        elif is_show:
            filtered_results.append(f"TV Show - {item['Title']} - Seasons: {item.get('Show_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Show', []))}")

    return filtered_results

