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
    
    # Registra il font TrueType
    pdf.add_font("DejaVuSans", "", "dejavufonts/ttf/DejaVuSerif.ttf", uni=True)
    pdf.set_font("DejaVuSans", size=12)  # Usa il font TrueType
    
    pdf.cell(200, 10, txt="Netflix Recommendations", ln=True, align='C')
    pdf.ln(10)
    
    for result in results:
        pdf.multi_cell(0, 10, result)
        pdf.ln(5)  # Spazio tra i risultati
    
    try:
        pdf.output("Netflix_Recommendations.pdf")
        messagebox.showinfo("PDF Generated", "The PDF has been successfully generated")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating the PDF: {e}")

# Funzione per aggiornare il frame della durata in base al tipo di contenuto selezionato
def update_duration_frame(content_type, duration_frame, min_duration_var, max_duration_var):
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
        tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
        tk.Label(duration_frame, text="Max Seasons").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)
        
     # Imposta i valori predefiniti per min e max duration / seasons
    if content_type.get() == "Movie":
        min_duration_var.set(0)
        max_duration_var.set(200)
    else:  # TV Show
        min_duration_var.set(1)
        max_duration_var.set(10)

# Funzione per aggiornare la lista dei generi basata sul tipo di contenuto
def update_genre_list(content_type, genre_var, df):
    genre_list = []
    
    if content_type == "Movie":
        genre_list = sorted(set(genre for sublist in df['Genre_Film'].dropna() for genre in sublist))
    elif content_type == "TV Show":
        genre_list = sorted(set(genre for sublist in df['Genre_Shows'].dropna() for genre in sublist))
    
    genre_var.delete(0, tk.END)
    for genre in genre_list:
        genre_var.insert(tk.END, genre)

# Funzione che filtra i contenuti in base alle preferenze dell'utente
def preferences_filter(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    filtered_results = []

    # Maschera booleana per i generi basata sul tipo di contenuto
    if is_movie:
        genre_mask = df['Genre_Film'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Films_Duration'].fillna(0) >= min_duration) & (df['Films_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_Movie'] == 1
    elif is_show:
        genre_mask = df['Genre_Shows'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Shows_Duration'].fillna(0) >= min_duration) & (df['Shows_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_TVShow'] == 1
    else:
        return []

    # Filtro finale
    filtered_df = df[genre_mask & duration_mask & type_mask]

    # Creazione della lista di risultati formattati
    for _, item in filtered_df.iterrows():
        if is_movie:
            filtered_results.append(f"Movie - {item['Title']} - Duration: {item.get('Films_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Film', []))}")
        elif is_show:
            filtered_results.append(f"TV Show - {item['Title']} - Seasons: {item.get('Shows_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Shows', []))}")

    return filtered_results

# Funzione per raccogliere le preferenze dell'utente
def submit_preferences(df, content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry, root):
    
    content_type = content_type_var.get()
    is_movie = content_type == "Movie"
    is_show = content_type == "TV Show"
    
    # Ottieni i valori delle variabili di durata
    min_duration = min_duration_var.get()
    max_duration = max_duration_var.get()

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
    # min_seasons_var = tk.IntVar(value=1)
    # max_seasons_var = tk.IntVar(value=10)
    
    tk.Label(duration_frame, text="Min Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
    tk.Label(duration_frame, text="Max Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)

    # Aggiorna il frame della durata quando cambia il tipo di contenuto
    content_type_var.trace_add('write', lambda *args: update_duration_frame(
        content_type_var, duration_frame, min_duration_var, max_duration_var))

    # Frame per i generi
    genre_frame = tk.LabelFrame(root, text="Genres")
    genre_frame.pack(fill="x", padx=5, pady=5)

    genre_var = tk.Listbox(genre_frame, selectmode="multiple", height=6)
    genre_var.pack(fill="x", padx=5, pady=5)
    
    # Aggiorna la lista dei generi basata sul tipo di contenuto iniziale
    update_genre_list(content_type_var.get(), genre_var, df)

    # Aggiorna la lista dei generi quando cambia il tipo di contenuto
    content_type_var.trace_add('write', lambda *args: update_genre_list(content_type_var.get(), genre_var, df))

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
