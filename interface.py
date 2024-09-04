import tkinter as tk
import pandas as pd
from tkinter import ttk, messagebox
import calendar
from datetime import datetime
from fpdf import FPDF
import json  # Importa il modulo JSON per salvare le preferenze

# Funzione per salvare le preferenze in un file JSON
def save_preferences(preferences):
    with open("user_preferences.json", "w") as file:
        json.dump(preferences, file)
    messagebox.showinfo("Preferences Saved", "Your preferences have been saved successfully")

# Funzione per visualizzare i risultati su un calendario
def generate_calendar(results, root):
    now = datetime.now()
    cal = calendar.TextCalendar(calendar.SUNDAY)
    cal_str = cal.formatmonth(now.year, now.month)

    top = tk.Toplevel(root)
    top.title("Calendar")
    
    cal_label = tk.Label(top, text=cal_str, font=("Courier", 10))
    cal_label.pack(pady=10)

    result_label = tk.Label(top, text="\n".join(results), justify='left')
    result_label.pack(pady=10)

# Funzione per generare un pdf con i suggerimenti e la pianificazione.
def generate_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Netflix Recommendations", ln=True, align='C')
    pdf.ln(10)
    
    for result in results:
        pdf.multi_cell(0, 10, result)
        pdf.ln(5)
    
    pdf.output("Netflix_Recommendations.pdf")
    messagebox.showinfo("PDF Generated", "The PDF has been successfully generated")

# Funzione per aggiornare il frame della durata in base al tipo di contenuto selezionato
def update_duration_frame(content_type, duration_frame, min_duration_var, max_duration_var, min_seasons_var, max_seasons_var):
    # Rimuove tutti i widget esistenti nel frame della durata
    for widget in duration_frame.winfo_children():
        widget.destroy()

    # Aggiunge i widget in base al tipo di contenuto selezionato
    if content_type.get() == "Movie":
        duration_frame.config(text="Duration (Minutes)")
        tk.Label(duration_frame, text="Min Duration").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
        tk.Label(duration_frame, text="Max Duration").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)
    else:  # TV Show
        duration_frame.config(text="Duration (Seasons)")
        tk.Label(duration_frame, text="Min Seasons").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=min_seasons_var, width=5).pack(side="left", padx=5)
        tk.Label(duration_frame, text="Max Seasons").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=max_seasons_var, width=5).pack(side="left", padx=5)

'''# Funzione che filtra i contenuti in base alle preferenze dell'utente -- TO FIX!! NON FUNZIONAAA NON CAPISCO PERCHÉ
def preferences_filter(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    filtered_results = []

    for _, item in df.iterrows():
        # Recupera la colonna "Genre" e assicura che sia una lista
        genres = item.get("Genre", [])
        if isinstance(genres, str):  # Se è una stringa, convertila in lista
            genres = genres.strip("[]").replace('"', '').split(", ")

        print(f"Controllo item: {item.get('Title', 'N/A')}")
        print(f"Genres: {genres}")

        if is_movie:
            print(f"Checking if item is a movie...")
            if item.get("Is_Movie", False) and min_duration <= item.get("Films_Duration", 0) <= max_duration:
                print(f"Item matches duration criteria for movies")
                if any(genre in selected_genres for genre in genres):
                    print(f"Item matches genre criteria for movies")
                    filtered_results.append(f"Movie - {item.get('Title', 'N/A')} - Duration: {item.get('Films_Duration', 'N/A')} - Genres: {', '.join(genres)}")

        elif is_show:
            print(f"Checking if item is a TV show...")
            if item.get("Is_TVShow", False) and min_duration <= item.get("Shows_Duration", 0) <= max_duration:
                print(f"Item matches duration criteria for TV shows")
                if any(genre in selected_genres for genre in genres):
                    print(f"Item matches genre criteria for TV shows")
                    filtered_results.append(f"TV Show - {item.get('Title', 'N/A')} - Seasons: {item.get('Shows_Duration', 'N/A')} - Genres: {', '.join(genres)}")

    return filtered_results'''
    
# Funzione che filtra i contenuti in base alle preferenze dell'utente
def preferences_filter(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    filtered_results = []

    for _, item in df.iterrows():
        # Recupera la colonna "Genre" e assicura che sia una lista
        genres = item.get("Genre", [])
        if isinstance(genres, str):  # Se è una stringa, convertila in lista
            genres = genres.strip("[]").replace("'", '').split(", ")
            genres = [genre.strip() for genre in genres]  # Rimuove spazi superflui

        # Debugging per vedere cosa stiamo processando
        print(f"Controllo item: {item.get('Title', 'N/A')}")
        print(f"Genres: {genres}")

        # Filtraggio per Film
        if is_movie:
            print(f"Checking if item is a movie...")
            # Verifica che sia un film e che la durata sia all'interno dell'intervallo
            films_duration = item.get("Films_Duration", 0)
            if pd.notnull(films_duration) and min_duration <= films_duration <= max_duration:
                print(f"Item matches duration criteria for movies")
                # Verifica che almeno uno dei generi sia presente nei generi selezionati
                if any(genre in selected_genres for genre in genres):
                    print(f"Item matches genre criteria for movies")
                    filtered_results.append(f"Movie - {item.get('Title', 'N/A')} - Duration: {films_duration} - Genres: {', '.join(genres)}")

        # Filtraggio per Serie TV
        if is_show:
            print(f"Checking if item is a TV show...")
            # Verifica che sia una serie TV e che la durata sia all'interno dell'intervallo
            shows_duration = item.get("Shows_Duration", 0)
            if pd.notnull(shows_duration) and min_duration <= shows_duration <= max_duration:
                print(f"Item matches duration criteria for TV shows")
                # Verifica che almeno uno dei generi sia presente nei generi selezionati
                if any(genre in selected_genres for genre in genres):
                    print(f"Item matches genre criteria for TV shows")
                    filtered_results.append(f"TV Show - {item.get('Title', 'N/A')} - Seasons: {shows_duration} - Genres: {', '.join(genres)}")

    return filtered_results
    

# Funzione per raccogliere le preferenze dell'utente
def submit_preferences(df, content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry, root):
    
    content_type = content_type_var.get()
    is_movie = content_type == "Movie"
    is_show = content_type == "TV Show"
    
    # Ottieni i valori delle variabili di durata o stagioni
    min_duration = min_duration_var.get() if is_movie else 0
    max_duration = max_duration_var.get() if is_movie else 0
    
    # genres = [genre_var.get(i) for i in genre_var.curselection()]
    # Ottieni i generi selezionati
    selected_genres = [genre_var.get(i) for i in genre_var.curselection()]
    cast = cast_entry.get()

    preferences = {
        "content_type": content_type,
        "min_duration": min_duration,
        "max_duration": max_duration,
        "genres": selected_genres,
        "cast": cast
    }

    save_preferences(preferences)  # Salva le preferenze in un file
    
    # Passa i parametri al filtro
    results = preferences_filter(df, is_movie, is_show, min_duration, max_duration, selected_genres)

    '''
    # Qui andrebbe implementata la logica per filtrare il dataset in base alle preferenze.
    # Per ora, inseriamo dei dati di esempio.
    results = [
        f"{content_type} - Title 1 - 100 min - {', '.join(genres)} - Cast: {cast}",
        f"{content_type} - Title 2 - 120 min - {', '.join(genres)} - Cast: {cast}"
    ]
    '''
    
    if len(results) > 0:
        generate_pdf(results)
        generate_calendar(results, root)
    else:
        messagebox.showinfo("No Results", "No results match your preferences.")

# Funzione per resettare i campi
def reset_fields(content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry):
    content_type_var.set("Movie")
    min_duration_var.set(0)
    max_duration_var.set(200)
    genre_var.selection_clear(0, tk.END)
    cast_entry.delete(0, tk.END)

# Funzione per creare e avviare l'interfaccia grafica
def create_interface(df):
    root = tk.Tk()
    root.title("Netflix Recommendation System")

    # Frame per il tipo di contenuto
    type_frame = tk.LabelFrame(root, text="Content Type")
    type_frame.pack(fill="x", padx=5, pady=5)

    content_type_var = tk.StringVar(value="Movie")
    ttk.Radiobutton(type_frame, text="Movie", variable=content_type_var, value="Movie").pack(side="left", padx=5)
    ttk.Radiobutton(type_frame, text="TV Show", variable=content_type_var, value="TV Show").pack(side="left", padx=5)

    # Frame per la durata
    duration_frame = tk.LabelFrame(root, text="Duration (Minutes)")
    duration_frame.pack(fill="x", padx=5, pady=5)
    
    # Variabili per la durata
    min_duration_var = tk.IntVar(value=0)
    max_duration_var = tk.IntVar(value=200)
    min_seasons_var = tk.IntVar(value=1)
    max_seasons_var = tk.IntVar(value=10)
    
    tk.Label(duration_frame, text="Min Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
    tk.Label(duration_frame, text="Max Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)

    # Aggiorna il frame della durata quando cambia il tipo di contenuto
    content_type_var.trace_add('write', lambda *args: update_duration_frame(
        content_type_var, duration_frame, min_duration_var, max_duration_var, min_seasons_var, max_seasons_var))

    # Frame per i generi
    genre_frame = tk.LabelFrame(root, text="Genres")
    genre_frame.pack(fill="x", padx=5, pady=5)

    # Nota bene: dovremmo avere come lista dei generi una lista esaustiva che raggruppi i generi per film e generi per serie tv.
    # non va bene avere l'elenco scritto da noi -> c'è bisogno di un modo per mappare la scelta all'operazione che avviene nel dataset (filtraggio secondo le preferenze)
    genres_list = ["Action", "Comedy", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller"]
    genre_var = tk.Listbox(genre_frame, selectmode="multiple", height=6)
    for genre in genres_list:
        genre_var.insert(tk.END, genre)
    genre_var.pack(fill="x", padx=5, pady=5)

    # Frame per il cast
    cast_frame = tk.LabelFrame(root, text="Cast (Optional)")
    cast_frame.pack(fill="x", padx=5, pady=5)

    cast_entry = tk.Entry(cast_frame)
    cast_entry.pack(fill="x", padx=5, pady=5)

    # Frame per i pulsanti
    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=5, pady=5)

    ttk.Button(button_frame, text="Submit", command=lambda: submit_preferences(
        df, content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry, root)).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Reset", command=lambda: reset_fields(
        content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry)).pack(side="left", padx=5)

    # Avvio dell'interfaccia grafica
    root.mainloop()
